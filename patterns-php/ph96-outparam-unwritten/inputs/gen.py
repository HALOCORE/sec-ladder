#!/usr/bin/env python3
"""Generate ph96's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph96-outparam-unwritten/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel runs one window
    byte 8..   u8[] blob       windows; n_blob = payload_len - 8

A *window* is a run of `$obj[...]` operations, one per 16-byte record:

    byte 0   u8  shape_raw  -> shape  = shape_raw % 4     which of the four
                                                          ArrayAccess handlers
    byte 1   u8  stat_raw   -> failed = stat_raw % 5 == 0 zend_call_function
                                                          returns FAILURE
    byte 2   u8  wrote_raw  -> wrote  = wrote_raw % 3 != 0 the user method
                                                          returned a zval
    byte 3   u8  ty_raw     -> Z_TYPE_P = TYTAB[ty_raw % 4]
    byte 4   u8  lval       -> Z_LVAL_P
    byte 5   u8  len_raw    -> Z_STRLEN_P = len_raw % 11
    byte 6.. u8[10]         -> Z_STRVAL_P

⚠⚠⚠ **`stat_raw` AND `wrote_raw` ARE SEPARATE BYTES AND THAT IS THE ROW.**
*Did the call fail?* and *did it leave an output?* are two propositions;
`zend_call_method` answers the first (`zend_interfaces.c:81`, E_CORE_ERROR) and
`zend_object_handlers.c:513` needs the second. A generator that derived one from
the other -- `wrote` meaningful only when the call succeeded, say -- would have
deleted the mechanism before a single rung was written, and the row would be
`ph60` rebuilt. That is the catalogue's own `⚠ risk` note on this row, verbatim.
They are independent here, `_check_span()` asserts that the corpus reaches every
COMBINATION the benign domain admits, and `../spec.md idiom.required[0]` pins it.
`shape_raw` is a THIRD independent byte.

⚠ **THE 10 PAYLOAD BYTES PAST `Z_STRLEN` ARE NON-ZERO JUNK**, on purpose: a zval
string is `(val, len)` and every rung folds exactly `len` bytes, so a rung that
walked to a NUL instead would fold the junk. `_check_span()` refuses a corpus
whose padding contains a zero byte.

⚠⚠ **THE ARMS THIS CORPUS MUST REACH, AND `_check_span()` REFUSES TO WRITE A
CORPUS THAT DOES NOT** (`PROTOCOL_PHP.md` §A2a rule 1):

  * **all four consumer shapes** -- `read` (output, GUARDED at `:385`), `write`
    (NO-OUTPUT, `:413` passes NULL), `exists` (output, UNGUARDED at `:427`) and
    `unset` (output, UNGUARDED at `:512`), which is the 2x2 the row is about;
  * **both call statuses** -- FAILURE, which `zend_interfaces.c:81` DOES test
    and turns into `E_CORE_ERROR`, and SUCCESS. A corpus in which the status
    never fails would have no status guard at all, and the row's claim is that
    the guard that IS there answers a different question;
  * **both out-parameter outcomes WITH the status failing** -- so `wrote` varies
    freely on the arm where it does not decide anything, which is what makes it
    an independent bit rather than a relabelling of the status;
  * **all four `Z_TYPE_P` tags** -- `IS_NULL`, `IS_LONG`, `IS_BOOL`, `IS_STRING`,
    which are the four arms of `i_zend_is_true`'s switch this row carries;
  * **both `i_zend_is_true` answers on the scalar arm** -- `lval == 0` and
    `lval != 0` (`zend_execute.h:79`);
  * **all three `i_zend_is_true` string arms** -- `len == 0`, `len == 1 &&
    val[0] == '0'`, and everything else (`zend_execute.h:85-90`), because a rung
    that wrote `len == 0` alone agrees with upstream on every other string;
  * **both ends of the `Z_STRLEN` domain**, 0 and 10;
  * ⚠ and, NEGATIVELY, **NO record with `failed == False and wrote == False`.**
    That is the `zend_execute_API.c:592-595` sentinel -- the ADVERSARIAL case --
    and keeping it out of the measured corpus is what "benign" means here: R1
    and R1h then agree on every measured call, which is what `check.py` stage 7h
    requires and what makes the R1-vs-R1h comparison a comparison between two
    runs of one program.

⚠ **THIS IS A SUPERSET CONDITION AND `model.py` CARRIES THE SHARPER ONE.**
`_check_span` asserts over EVERY window in the file; the driver picks windows
from a checksum-derived index and need not visit them all, so
`model.py::selfcheck` re-asserts the same arm table over **the calls the driver
actually makes**.

Four things about the sizes are deliberate.

  * **`small` and `large` have different strides** -- 118 and 1004 -- and they
    are in different residue classes mod 4, 8 and 16. `work_per_call` *is* the
    stride, so `harness/check.py`'s `d(Ir)/d(work)` assertion needs two probe
    shapes with different `work_per_call` or it cannot run at all.
    ⚠ `ph64` shipped `small.bin` and `large.bin` at **nine bytes each**, which
    is one alignment draw sampled twice, and it silently weakened every
    two-input argument that row made (F119/M4). These differ by 8.5x.
  * **the strides are not powers of two** (118 = 2*59, 1004 = 2^2*251).
  * **neither stride is a multiple of 16**, so both carry a trailing PARTIAL
    record that `nrec = len / 16` truncates away. That is the cheapest way to
    check that no rung reads past `nrec` records, and every rung derives `nrec`
    the same way.
  * **every residue field is written with a random multiple of its modulus
    added**, so the `%` in each rung is exercised rather than being the identity
    on every record.

⚠⚠ **THE FIVE ADVERSARIAL FILES, AND THE ONE THAT IS NOT HERE.**
`adversarial-unset.bin` is the row: one window, one record, `shape == unset`,
`failed == False`, `wrote == False`, and the C R1 rung writes through address
0x10 there. `adversarial-read.bin` and `adversarial-write.bin` are the 2x2's two
GUARDED cells on the same input state -- the `:385` test firing and the
`:413`/`:89` no-output disposal -- and both are `clean` in every rung.
`adversarial-corefail.bin` is the status guard firing, and `adversarial-nowin`
makes no kernel call at all.

⛔⛔ **THERE IS NO `adversarial-exists.bin`, AND THE REASON IS A MEASUREMENT
RATHER THAN AN OVERSIGHT.** `zend_std_has_dimension` at `:427-429` has the same
defect and `cf020f133487` does not touch it, so an input carrying that state
faults in **R1h as well as R1** -- and `check.py` stage 7h fails a row whose R1h
fires a sanitizer on ANY input, adversarial included. The limb is therefore
measured by `controls/second_limb.py`, which builds both C rungs and all four
Rust rungs and drives exactly that state through them. ../NOTES.md section 5 has
the scope of the claim and section 12 has the ruling question this raises.
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "common-php"))
import slb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 0x5EC1ADDE  # "sec-ladder", fixed forever: the .bin files are gitignored
                   # and must be regenerable byte-for-byte from this file alone.

REC = 16
STRMAX = 10

SHAPE_READ, SHAPE_WRITE, SHAPE_EXISTS, SHAPE_UNSET = 0, 1, 2, 3
SHAPE_NAME = ("read", "write", "exists", "unset")

# Z_TYPE_P, upstream's own numbering (Zend/zend.h:302-309), indexed by
# `ty_raw % 4`. `model.py` and every rung carry the same four.
TYTAB = (0, 1, 3, 6)  # IS_NULL, IS_LONG, IS_BOOL, IS_STRING
TY_NULL, TY_LONG, TY_BOOL, TY_STRING = 0, 1, 2, 3

SMALL_STRIDE, SMALL_WINS = 118, 24
LARGE_STRIDE, LARGE_WINS = 1004, 60


def rec(rng, shape, failed, wrote, ty=TY_NULL, lval=0, s=b""):
    """One 16-byte call record.

    Every residue field is written with a random multiple of its modulus added,
    so every rung's `%` is exercised rather than being the identity. The 10
    payload bytes past `len(s)` are non-zero junk."""
    assert 0 <= shape <= 3 and 0 <= ty <= 3 and len(s) <= STRMAX
    b0 = shape + 4 * rng.randrange(0, 63)
    b1 = (0 if failed else rng.randrange(1, 5)) + 5 * rng.randrange(0, 51)
    b2 = (0 if not wrote else rng.randrange(1, 3)) + 3 * rng.randrange(0, 84)
    b3 = ty + 4 * rng.randrange(0, 63)
    b5 = len(s) + 11 * rng.randrange(0, 23)
    assert max(b0, b1, b2, b3, b5) <= 255
    assert b0 % 4 == shape and b3 % 4 == ty and b5 % 11 == len(s)
    assert (b1 % 5 == 0) == failed and (b2 % 3 != 0) == wrote
    pad = bytes(rng.randrange(1, 256) for _ in range(STRMAX - len(s)))
    return bytes((b0, b1, b2, b3, lval & 0xFF, b5)) + s + pad


def decode(b):
    """(shape, failed, wrote, ty, lval, slen, payload) -- the inverse of `rec`."""
    return (b[0] % 4, b[1] % 5 == 0, b[2] % 3 != 0, b[3] % 4, b[4],
            b[5] % 11, b[6:6 + STRMAX])


# The record menu the tiling draws from. Every entry names the arm it exists
# for, and `_check_span` checks the arms rather than the menu.
def menu(rng):
    m = []
    # the benign call, all four shapes, a string value
    for sh in range(4):
        m.append((f"ok-{SHAPE_NAME[sh]}",
                  rec(rng, sh, False, True, TY_STRING, 0, b"offset")))
    # the four Z_TYPE arms of i_zend_is_true, on the shape that reads the type
    m.append(("ty-null", rec(rng, SHAPE_EXISTS, False, True, TY_NULL, 7)))
    m.append(("ty-long-0", rec(rng, SHAPE_EXISTS, False, True, TY_LONG, 0)))
    m.append(("ty-long-1", rec(rng, SHAPE_EXISTS, False, True, TY_LONG, 9)))
    m.append(("ty-bool-0", rec(rng, SHAPE_EXISTS, False, True, TY_BOOL, 0)))
    m.append(("ty-bool-1", rec(rng, SHAPE_EXISTS, False, True, TY_BOOL, 1)))
    # zend_execute.h:85-90 -- the three string arms
    m.append(("str-empty", rec(rng, SHAPE_EXISTS, False, True, TY_STRING, 0, b"")))
    m.append(("str-zero", rec(rng, SHAPE_EXISTS, False, True, TY_STRING, 0, b"0")))
    m.append(("str-one", rec(rng, SHAPE_EXISTS, False, True, TY_STRING, 0, b"1")))
    m.append(("str-long", rec(rng, SHAPE_READ, False, True, TY_STRING, 0,
                              b"abcdefghij")))
    # the STATUS guard firing -- zend_interfaces.c:81, E_CORE_ERROR. `wrote`
    # varies freely on this arm, which is what makes it an independent bit.
    m.append(("core-w1", rec(rng, SHAPE_UNSET, True, True, TY_STRING, 0, b"x")))
    m.append(("core-w0", rec(rng, SHAPE_UNSET, True, False, TY_NULL, 0)))
    m.append(("core-read-w0", rec(rng, SHAPE_READ, True, False, TY_LONG, 3)))
    m.append(("core-exists-w1", rec(rng, SHAPE_EXISTS, True, True, TY_BOOL, 1)))
    m.append(("core-write-w0", rec(rng, SHAPE_WRITE, True, False, TY_NULL, 0)))
    # a released value on the no-output contract -- zend_interfaces.c:89-90
    m.append(("noout-rel", rec(rng, SHAPE_WRITE, False, True, TY_LONG, 5)))
    return m


def tiled(rng, nwin, stride):
    """The measured corpus: `nwin` windows of `stride // 16` records each."""
    nrec = stride // REC
    tail = stride - nrec * REC
    assert nrec >= 1 and tail > 0
    pool = menu(rng)
    out = []
    k = 0
    for _ in range(nwin):
        w = b""
        for _ in range(nrec):
            w += pool[k % len(pool)][1]
            k += 1
        # the trailing partial record: junk no rung may read
        w += bytes(rng.randrange(1, 256) for _ in range(tail))
        out.append(w)
    return b"".join(out)


def one_window(rng, stride, r):
    """A single-record adversarial payload padded out to `stride`."""
    nrec = stride // REC
    tail = stride - nrec * REC
    w = r + b"".join(rec(rng, i % 4, False, True, TY_STRING, 0, b"ok")
                     for i in range(nrec - 1))
    return w + bytes(rng.randrange(1, 256) for _ in range(tail))


# --------------------------------------------------------------------------
# the assertion half of A2a rule 1 -- an intention in a comment is what ph03
# had, and it was wrong for a task
# --------------------------------------------------------------------------

def _arm_of(shape, failed, wrote, ty, lval, slen, payload):
    """Which arm this record reaches, and how.

    Deliberately a SECOND derivation of the kernel's control flow, written from
    the tarball citations rather than from model.py."""
    if failed:                                    # zend_interfaces.c:81-86
        return "core", "E_CORE_ERROR"
    if not wrote:                                 # zend_execute_API.c:595
        if shape == SHAPE_READ:
            return "sentinel", "GUARDED :385"
        if shape == SHAPE_WRITE:
            return "sentinel", "NO-OUTPUT :413"
        return "sentinel", "NULL-DEREF"           # :427-429 / :512-513
    return "value", SHAPE_NAME[shape]


def _check_span(name, blob, stride):
    """Refuse to write a corpus that misses an arm. Returns a list of problems."""
    bad = []
    nwin = len(blob) // stride
    nrec = stride // REC
    if nwin == 0 or nrec == 0:
        return [f"{name}: no complete window/record at stride {stride}"]
    shapes, tys, routes, arms = set(), set(), set(), set()
    statwrote, lens, scalars, strarms = set(), set(), set(), set()
    sentinel = 0
    padzero = 0
    for k in range(nwin):
        win = blob[k * stride:(k + 1) * stride]
        for r in range(nrec):
            b = win[r * REC:(r + 1) * REC]
            sh, fl, wr, ty, lv, ln, pay = decode(b)
            shapes.add(sh)
            statwrote.add((fl, wr))
            if not fl and not wr:
                sentinel += 1
            if not fl and wr:
                tys.add(ty)
                lens.add(ln)
                if ty in (TY_LONG, TY_BOOL):
                    scalars.add(1 if lv else 0)
                if ty == TY_STRING:
                    s = pay[:ln]
                    if ln == 0:
                        strarms.add("empty")
                    elif ln == 1 and s[0:1] == b"0":
                        strarms.add("zero")
                    else:
                        strarms.add("other")
            if 0 in pay[ln:]:
                padzero += 1
            route, arm = _arm_of(sh, fl, wr, ty, lv, ln, pay)
            routes.add(route)
            arms.add(arm)
    if shapes != {0, 1, 2, 3}:
        bad.append(f"{name}: the corpus reaches shapes {sorted(shapes)}, want "
                   f"all four -- read/write/exists/unset are the 2x2 the row is "
                   f"about and three of them are not the defect site")
    if statwrote != {(True, False), (True, True), (False, True)}:
        bad.append(f"{name}: `(failed, wrote)` reaches {sorted(statwrote)}, "
                   f"want exactly {{(True, False), (True, True), (False, True)}} "
                   f"-- both bits must vary independently, and (False, False) is "
                   f"the zend_execute_API.c:595 SENTINEL, which is ADVERSARIAL")
    if sentinel:
        bad.append(f"{name}: {sentinel} record(s) carry `failed == False and "
                   f"wrote == False`. That is the defect's own input: R1 writes "
                   f"through address 0x10 on it, so a measured corpus "
                   f"containing one is not benign and check.py stage 7h's "
                   f"R1h == R1 requirement cannot hold")
    if routes != {"core", "value"}:
        bad.append(f"{name}: only {sorted(routes)} of the two benign routes are "
                   f"reached -- the STATUS guard at zend_interfaces.c:81 must "
                   f"be able to FIRE or the kernel has no status guard at all")
    if tys != {TY_NULL, TY_LONG, TY_BOOL, TY_STRING}:
        bad.append(f"{name}: `Z_TYPE_P` on a written output reaches "
                   f"{sorted(tys)}, want all four -- they are the four arms of "
                   f"i_zend_is_true's switch (zend_execute.h:72-109)")
    if scalars != {0, 1}:
        bad.append(f"{name}: the IS_LONG/IS_BOOL arm reaches truth values "
                   f"{sorted(scalars)}, want both -- zend_execute.h:79 is "
                   f"`op->value.lval ? 1 : 0`")
    if strarms != {"empty", "zero", "other"}:
        bad.append(f"{name}: the IS_STRING arm reaches {sorted(strarms)}, want "
                   f"all three -- zend_execute.h:85-90 is false for a zero "
                   f"length AND for the one-byte string \"0\", and a rung that "
                   f"tested only the length would agree everywhere else")
    if 0 not in lens or STRMAX not in lens:
        bad.append(f"{name}: `Z_STRLEN` reaches {sorted(lens)}; both ends of "
                   f"the length domain (0 and {STRMAX}) must be present")
    if padzero:
        bad.append(f"{name}: {padzero} record(s) have a zero byte in the "
                   f"payload past Z_STRLEN. The padding must be non-zero so "
                   f"that a rung which folded to a terminator rather than to "
                   f"Z_STRLEN compares against junk rather than agreeing")
    return bad


def write(name, n_iters, stride, body, declared_len=None):
    path = os.path.join(HERE, name)
    payload = slb.pack_head1_bytes(stride, body)
    slb.write(path, n_iters, payload, declared_len)
    nw = len(body) // stride if stride else 0
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<6d} "
          f"blob={len(body):<8d} windows={nw:<5d} recs/win={stride // REC:<4d} "
          f"file={os.path.getsize(path)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()

    for mod in (4, 8, 16):
        if SMALL_STRIDE % mod == LARGE_STRIDE % mod:
            print(f"REFUSING TO WRITE: strides {SMALL_STRIDE}/{LARGE_STRIDE} "
                  f"are both == {SMALL_STRIDE % mod} mod {mod}")
            return 1
    if SMALL_STRIDE % REC == 0 or LARGE_STRIDE % REC == 0:
        print(f"REFUSING TO WRITE: a stride that is a multiple of {REC} carries "
              f"no trailing partial record, so nothing checks that a rung stops "
              f"at `nrec`")
        return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod 4, "
          f"8 and 16, and neither is a multiple of {REC}")

    small = tiled(random.Random(SEED + 1), SMALL_WINS, SMALL_STRIDE)
    large = tiled(random.Random(SEED + 2), LARGE_WINS, LARGE_STRIDE)
    problems = (_check_span("small.bin", small, SMALL_STRIDE)
                + _check_span("large.bin", large, LARGE_STRIDE))
    if problems:
        print("REFUSING TO WRITE -- the corpus misses an arm "
              "(PROTOCOL_PHP.md A2a rule 1):")
        for p in problems:
            print(f"    {p}")
        return 1
    print("  arm coverage ok on both measured inputs")

    write("small.bin", 20_000, SMALL_STRIDE, small)
    write("large.bin", 2_500, LARGE_STRIDE, large)

    # ---- the adversarial five -------------------------------------------
    rng = random.Random(SEED + 3)
    st = SMALL_STRIDE
    # ⛔ THE ROW. zend_call_function returns SUCCESS (:873) having written the
    # :595 sentinel, and zend_object_handlers.c:513 releases it untested.
    write("adversarial-unset.bin", 64, st,
          one_window(rng, st, rec(rng, SHAPE_UNSET, False, False, TY_NULL)))
    # ⭐ the SAME input state at the GUARDED site -- :385's `if (!retval)`. It
    # answers rather than faulting, in every rung, which is what makes the row's
    # claim behavioural rather than a reading of the source.
    write("adversarial-read.bin", 64, st,
          one_window(rng, st, rec(rng, SHAPE_READ, False, False, TY_NULL)))
    # ⭐ and at the NO-OUTPUT site -- :413 passes NULL, so zend_interfaces.c:89's
    # own `if (retval)` disposes of nothing. The contract that cannot be misused.
    write("adversarial-write.bin", 64, st,
          one_window(rng, st, rec(rng, SHAPE_WRITE, False, False, TY_NULL)))
    # the STATUS guard firing at the defect site: zend_interfaces.c:81 tests it,
    # so this is the half of I12/O1 that IS discharged.
    write("adversarial-corefail.bin", 64, st,
          one_window(rng, st, rec(rng, SHAPE_UNSET, True, False, TY_NULL)))
    # the control: a stride larger than the blob, so the kernel is never called.
    write("adversarial-nowin.bin", 64, 4096,
          one_window(rng, st, rec(rng, SHAPE_UNSET, False, False, TY_NULL)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
