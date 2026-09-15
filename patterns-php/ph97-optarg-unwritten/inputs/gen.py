#!/usr/bin/env python3
"""Generate ph97's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph97-optarg-unwritten/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel runs one window
    byte 8..   u8[] blob       windows; n_blob = payload_len - 8

A *window* is a run of `mb_get_info(...)` calls, one per 24-byte record:

    byte 0   u8  argc_raw   -> num_args = argc_raw % 3      ZEND_NUM_ARGS()
    byte 1   u8  type_raw   -> type_tag = type_raw % 4      Z_TYPE_PP(arg)
    byte 2   u8  len_raw    -> arg_len  = len_raw  % 21     Z_STRLEN_PP(arg)
    byte 3   u8  lval                                       Z_LVAL_PP(arg)
    byte 4.. u8[20]         -> Z_STRVAL_PP(arg)

⚠⚠⚠ **`argc_raw` AND `type_raw` ARE SEPARATE BYTES AND THAT IS THE ROW.**
*Was an argument supplied?* and *was it well-typed?* are two propositions;
`zend_parse_parameters` answers the second and `mbstring.c:3219` needs the
first. A generator that derived one from the other -- `type_tag` meaningful only
when `num_args > 0`, say -- would have deleted the mechanism before a single
rung was written. They are independent here, `_check_span()` asserts that the
corpus reaches every COMBINATION, and `../spec.md idiom.required[0]` pins it.
(`ph96`'s `⚠ risk` note is this trap one row over, and it is the same trap.)

⚠ **THE 20 PAYLOAD BYTES ARE NOT NUL-PADDED.** Everything past `arg_len` is
non-zero junk, on purpose: `convert_to_string_ex` materialises a NUL-terminated
`Z_STRVAL`, every rung copies `arg_len` bytes into a 21-byte frame and
terminates it, and a rung that forgot the terminator would compare against the
junk. `_check_span()` refuses a corpus whose padding contains a zero byte.

⚠⚠ **THE ARMS THIS CORPUS MUST REACH, AND `_check_span()` REFUSES TO WRITE A
CORPUS THAT DOES NOT** (`PROTOCOL_PHP.md` §A2a rule 1). The defect lives on the
selector chain at `mbstring.c:3219-3251` and on the two FAILURE routes out of
`zend_parse_va_args`, so the arms are:

  * **both benign argument counts** -- `num_args == 1` (the parser writes) and
    `num_args == 2` (the count test at `zend_API.c:511` REFUSES, so
    `mbstring.c:3216 RETURN_FALSE` is reached);
  * **all four type tags** -- `IS_NULL`, `IS_BOOL`, `IS_STRING` (all three of
    which `zend_parse_arg`'s 's' arm CONVERTS) and `IS_ARRAY` (which it
    REFUSES, `zend_API.c:330`);
  * **all six arms of the selector chain** -- `all`, `internal_encoding`,
    `http_input`, `http_output`, `func_overload`, and the unmatched `else` at
    `:3249`;
  * **at least one selector in a DIFFERENT CASE**, because `strcasecmp` is
    case-insensitive and a rung that wrote `strcmp` would agree on every
    lower-case corpus. Measured on the 5.0.0 CLI: `mb_get_info("ALL")` returns
    the four-element array;
  * **both ends of the length domain**, `arg_len == 0` and `arg_len == 20`;
  * **a string that is a strict PREFIX of a selector and one that strictly
    EXTENDS one** (`al`, `allx`), so the compare's terminator handling is
    exercised in both directions;
  * **an embedded NUL inside `arg_len`**, so the compare stops where PHP's
    `strcasecmp` stops rather than at `Z_STRLEN`;
  * **both `IS_BOOL` values**, `lval & 1` set and clear, i.e. `"1"` and `""`;
  * ⚠ and, NEGATIVELY, **NO record with `num_args == 0`.** That is the
    ADVERSARIAL case and keeping it out of the measured corpus is what "benign"
    means here: R1 and R1h then agree on every measured call, which is what
    `check.py` stage 7h requires and what makes the R1-vs-R1h comparison a
    comparison between two runs of one program.

⚠ **THIS IS A SUPERSET CONDITION AND `model.py` CARRIES THE SHARPER ONE.**
`_check_span` asserts over EVERY window in the file; the driver picks windows
from a checksum-derived index and need not visit them all, so
`model.py::selfcheck` re-asserts the same arm table over **the calls the driver
actually makes**.

Four things about the sizes are deliberate.

  * **`small` and `large` have different strides** -- 122 and 1036 -- and they
    are in different residue classes mod 4, 8 and 16. `work_per_call` *is* the
    stride, so `harness/check.py`'s `d(Ir)/d(work)` assertion needs two probe
    shapes with different `work_per_call` or it cannot run at all.
    ⚠ `ph64` shipped `small.bin` and `large.bin` at **nine bytes each**, which
    is one alignment draw sampled twice, and it silently weakened every
    two-input argument that row made (F119/M4). These differ by 8.5x.
  * **the strides are not powers of two** (122 = 2*61, 1036 = 2^2*7*37).
  * **neither stride is a multiple of 24**, so both carry a trailing PARTIAL
    record that `nrec = len / 24` truncates away. That is deliberate: it is the
    cheapest way to check that no rung reads past `nrec` records, and every
    rung derives `nrec` the same way.
  * **`argc_raw`, `type_raw` and `len_raw` are written with a random multiple
    of their modulus added**, so the `%` in each rung is exercised rather than
    being the identity on every record.

⚠⚠ **THE FIVE ADVERSARIAL FILES.** `adversarial-absent.bin` is the row: one
window, one record, `num_args == 0`, and the C R1 rung reads address 0 there.
The other four are its controls and all four are `clean` -- `typefail` and
`toomany` are the two routes by which the `:3215` guard FIRES, `nullvalue` is
the argument that IS null but was SUPPLIED (which does not fault, and that
separation is the row's claim at run time), and `nowin` makes no kernel call at
all.
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

REC = 24
STRMAX = 20

IS_NULL, IS_BOOL, IS_STRING, IS_ARRAY = 0, 1, 2, 3

SELECTORS = (b"all", b"internal_encoding", b"http_input", b"http_output",
             b"func_overload")

SMALL_STRIDE, SMALL_WINS = 122, 24
LARGE_STRIDE, LARGE_WINS = 1036, 60


def rec(rng, num_args, type_tag, s=b"", lval=0):
    """One 24-byte call record.

    The three residue fields are written with a random multiple of their
    modulus added, so every rung's `%` is exercised rather than being the
    identity. The 20 payload bytes past `len(s)` are non-zero junk."""
    assert 0 <= num_args <= 2 and 0 <= type_tag <= 3 and len(s) <= STRMAX
    b0 = num_args + 3 * rng.randrange(0, 85)
    b1 = type_tag + 4 * rng.randrange(0, 63)
    b2 = len(s) + 21 * rng.randrange(0, 12)
    assert b0 <= 255 and b1 <= 255 and b2 <= 255
    assert b0 % 3 == num_args and b1 % 4 == type_tag and b2 % 21 == len(s)
    pad = bytes(rng.randrange(1, 256) for _ in range(STRMAX - len(s)))
    return bytes((b0, b1, b2, lval & 0xFF)) + s + pad


def decode(b):
    """(num_args, type_tag, arg_len, lval, bytes) -- the inverse of `rec`."""
    return (b[0] % 3, b[1] % 4, b[2] % 21, b[3], b[4:4 + STRMAX])


# The record menu the tiling draws from. Every entry names the arm it exists
# for, and `_check_span` checks the arms rather than the menu.
def menu(rng):
    m = []
    for sel in SELECTORS:
        m.append(("sel-" + sel.decode(), rec(rng, 1, IS_STRING, sel)))
    m.append(("sel-ALL-upper", rec(rng, 1, IS_STRING, b"ALL")))
    m.append(("sel-HtTp_InPuT", rec(rng, 1, IS_STRING, b"HtTp_InPuT")))
    m.append(("unmatched", rec(rng, 1, IS_STRING, b"nonesuch")))
    m.append(("prefix-al", rec(rng, 1, IS_STRING, b"al")))
    m.append(("extend-allx", rec(rng, 1, IS_STRING, b"allx")))
    m.append(("len-0", rec(rng, 1, IS_STRING, b"")))
    m.append(("len-20", rec(rng, 1, IS_STRING, b"internal_encodingXYZ")))
    m.append(("embedded-nul", rec(rng, 1, IS_STRING, b"all\x00rubbish")))
    m.append(("type-null", rec(rng, 1, IS_NULL, b"", 0)))
    m.append(("type-bool-0", rec(rng, 1, IS_BOOL, b"", 0)))
    m.append(("type-bool-1", rec(rng, 1, IS_BOOL, b"", 1)))
    m.append(("type-array", rec(rng, 1, IS_ARRAY, b"all")))
    m.append(("argc-2", rec(rng, 2, IS_STRING, b"all")))
    return m


def tiled(rng, nwin, stride):
    """The measured corpus: `nwin` windows of `stride // 24` records each."""
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
    w = r + b"".join(rec(rng, 1, IS_STRING, SELECTORS[i % len(SELECTORS)])
                     for i in range(nrec - 1))
    return w + bytes(rng.randrange(1, 256) for _ in range(tail))


# --------------------------------------------------------------------------
# the assertion half of A2a rule 1 -- an intention in a comment is what ph03
# had, and it was wrong for a task
# --------------------------------------------------------------------------

def _arm_of(num_args, type_tag, arg_len, lval, payload):
    """Which arm of mb_get_info's chain this record reaches, and how.

    Returns (route, arm). `route` is one of `count`, `type`, `chain`.
    Deliberately a SECOND derivation of the kernel's control flow, written from
    the tarball citations rather than from model.py."""
    if num_args < 0 or num_args > 1:                 # zend_API.c:511
        return "count", "RETURN_FALSE"
    if num_args == 1 and type_tag == IS_ARRAY:       # zend_API.c:327-330
        return "type", "RETURN_FALSE"
    if num_args == 0:
        return "chain", "NULL-DEREF"                 # mbstring.c:3219, THE BUG
    if type_tag == IS_STRING:
        s = payload[:arg_len]
    elif type_tag == IS_BOOL:
        s = b"1" if (lval & 1) else b""
    else:                                            # IS_NULL -> ""
        s = b""
    s = s.split(b"\x00", 1)[0]                       # strcasecmp stops at NUL
    low = s.lower()
    for sel in SELECTORS:
        if low == sel:
            return "chain", sel.decode()
    return "chain", "else"                           # mbstring.c:3249


def _check_span(name, blob, stride):
    """Refuse to write a corpus that misses an arm. Returns a list of problems."""
    bad = []
    nwin = len(blob) // stride
    nrec = stride // REC
    if nwin == 0 or nrec == 0:
        return [f"{name}: no complete window/record at stride {stride}"]
    counts, types, arms, routes = set(), set(), set(), set()
    lens, bools = set(), set()
    upper = False
    prefix = False
    extend = False
    embnul = False
    absent = 0
    padzero = 0
    for k in range(nwin):
        win = blob[k * stride:(k + 1) * stride]
        for r in range(nrec):
            b = win[r * REC:(r + 1) * REC]
            na, ty, ln, lv, pay = decode(b)
            counts.add(na)
            types.add(ty)
            lens.add(ln)
            if na == 0:
                absent += 1
            if ty == IS_BOOL:
                bools.add(lv & 1)
            if ty == IS_STRING:
                s = pay[:ln]
                if s != s.lower():
                    upper = True
                if b"\x00" in s:
                    embnul = True
                for sel in SELECTORS:
                    if sel.lower().startswith(s.lower()) and s.lower() != sel:
                        prefix = True
                    if s.lower().startswith(sel) and s.lower() != sel:
                        extend = True
            if 0 in pay[ln:]:
                padzero += 1
            route, arm = _arm_of(na, ty, ln, lv, pay)
            routes.add(route)
            arms.add(arm)
    if counts != {1, 2}:
        bad.append(f"{name}: `num_args` reaches {sorted(counts)}, want exactly "
                   f"{{1, 2}} -- 1 is the writing call, 2 is the one the count "
                   f"test at zend_API.c:511 refuses, and 0 is ADVERSARIAL")
    if absent:
        bad.append(f"{name}: {absent} record(s) carry `num_args == 0`. That is "
                   f"the defect's own input: R1 dereferences NULL on it, so a "
                   f"measured corpus containing one is not benign and "
                   f"check.py stage 7h's R1h == R1 requirement cannot hold")
    if types != {IS_NULL, IS_BOOL, IS_STRING, IS_ARRAY}:
        bad.append(f"{name}: `Z_TYPE_PP(arg)` reaches {sorted(types)}, want all "
                   f"four -- IS_NULL/IS_BOOL/IS_STRING are the three the 's' "
                   f"arm CONVERTS (zend_API.c:310-317) and IS_ARRAY is the one "
                   f"it REFUSES (:330)")
    if routes != {"count", "type", "chain"}:
        bad.append(f"{name}: only {sorted(routes)} of the three routes are "
                   f"reached -- the `:3215` guard must be able to FAIL by BOTH "
                   f"its routes or the kernel has no guard at all")
    want_arms = {s.decode() for s in SELECTORS} | {"else", "RETURN_FALSE"}
    if arms != want_arms:
        bad.append(f"{name}: selector-chain arms reached {sorted(arms)}, want "
                   f"{sorted(want_arms)}")
    if 0 not in lens or STRMAX not in lens:
        bad.append(f"{name}: `Z_STRLEN` reaches {sorted(lens)}; both ends of "
                   f"the length domain (0 and {STRMAX}) must be present")
    if bools != {0, 1}:
        bad.append(f"{name}: IS_BOOL reaches lval bits {sorted(bools)}, want "
                   f"both -- `convert_to_boolean_ex` gives \"\" and \"1\"")
    if not upper:
        bad.append(f"{name}: no selector is spelled in a different case, so a "
                   f"rung that wrote `strcmp` for `strcasecmp` would agree on "
                   f"every record. The 5.0.0 CLI answers mb_get_info(\"ALL\") "
                   f"with the four-element array")
    if not prefix:
        bad.append(f"{name}: no argument is a strict PREFIX of a selector")
    if not extend:
        bad.append(f"{name}: no argument strictly EXTENDS a selector")
    if not embnul:
        bad.append(f"{name}: no argument carries an embedded NUL inside its "
                   f"Z_STRLEN, so nothing distinguishes a compare that stops "
                   f"at the terminator from one that runs to the length")
    if padzero:
        bad.append(f"{name}: {padzero} record(s) have a zero byte in the "
                   f"padding past Z_STRLEN. The padding must be non-zero so "
                   f"that a rung which forgot to NUL-terminate its frame copy "
                   f"compares against junk rather than accidentally agreeing")
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
    write("large.bin", 3_000, LARGE_STRIDE, large)

    # ---- the adversarial five -------------------------------------------
    rng = random.Random(SEED + 3)
    st = SMALL_STRIDE
    # ⛔ THE ROW. num_args == 0: zend_parse_parameters returns SUCCESS having
    # written nothing, and mbstring.c:3219 hands the caller's own NULL to the
    # compare.
    write("adversarial-absent.bin", 64, st,
          one_window(rng, st, rec(rng, 0, IS_STRING, b"all")))
    # the `:3215` guard FIRING, route 1: the argument is there and is an array.
    write("adversarial-typefail.bin", 64, st,
          one_window(rng, st, rec(rng, 1, IS_ARRAY, b"all")))
    # route 2: too many arguments for "|s".
    write("adversarial-toomany.bin", 64, st,
          one_window(rng, st, rec(rng, 2, IS_STRING, b"all")))
    # ⭐ the argument that IS null and WAS supplied. "|s" carries no `!`, so
    # zend_API.c:302-308 falls through to convert_to_string_ex and `typ` is the
    # EMPTY STRING, not NULL. The measured CLI answers bool(false).
    write("adversarial-nullvalue.bin", 64, st,
          one_window(rng, st, rec(rng, 1, IS_NULL, b"")))
    # the control: a stride larger than the blob, so the kernel is never called.
    write("adversarial-nowin.bin", 64, 4096,
          one_window(rng, st, rec(rng, 0, IS_STRING, b"all")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
