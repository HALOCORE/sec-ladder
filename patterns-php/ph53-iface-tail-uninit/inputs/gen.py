#!/usr/bin/env python3
"""Generate ph53's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph53-iface-tail-uninit/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel runs one window
    byte 8..   u8[] blob       windows; n_blob = payload_len - 8

A *window* is one class declaration followed by an opcode stream:

    byte  0..3   u32 LE  n_decl_w   n_decl = n_decl_w % (MAXD + 1)   0..16
    byte  4..7   u32 LE  n_pool_w   n_pool = 1 + n_pool_w % MAXP     1..8
    byte  8..11  u32 LE  n_ops_w    n_ops  = n_ops_w % (cap + 1)
    byte 12..75          u64[8]     the interface pool's `id`s
    byte 76..            9 B each   { u8 op; u32 LE a; u32 LE b }
                                    cap = (stride - 76) // 9

and one op is

    op % 3 == 0  FILL         ce->interfaces[idx[a % n_decl]] = &pool[b % n_pool]
                              -- ZEND_ADD_INTERFACE's runtime half
    op % 3 == 1  QUERY_DEREF  zend_operators.c:1534-1535, the FAULTING consumer
    op % 3 == 2  QUERY_CMP    zend_compile.c:1951, the COMPARE-ONLY consumer

⚠⚠⚠ **THE BLOB IS THE OPCODE STREAM AND THAT IS DELIBERATE.** `ph49`'s warning
applies verbatim: *an extraction that reaches for the executor has built a
different row.* `n_decl` is what `zend_do_implements_interface` counted at
COMPILE time (`zend_compile.c:2591`) and the `FILL` ops are the
`ZEND_ADD_INTERFACE` opcodes that were supposed to write the slots. The defect
is the gap between the two, so the corpus's job is to control that gap.

⚠⚠ **WHAT "BENIGN" MEANS HERE, AND IT IS A STRUCTURAL CONDITION ON THE OP
STREAM, NOT A RANGE ON A NUMBER.** A window is benign iff

  * every `FILL` precedes every `QUERY`, and
  * the `FILL`s write decl indices `0, 1, ..., n_decl - 1`, each exactly once,
    **in increasing order**.

The second clause is stronger than "cover them all" and the reason is R3: the
safe-tuned rung is PHP 5.2.0's repair -- `ce->interfaces[ce->num_interfaces++]
= iface`, i.e. append-and-count -- so its slot order is the ARRIVAL order of
the `FILL`s. Increasing order is what makes arrival order equal index order and
therefore what makes all six rungs agree. ⚠ It is also what real PHP does: the
`ZEND_ADD_INTERFACE` opcodes run in source order, and `extended_value` was
assigned in that same order one pass earlier.

⚠⚠ **THE ARMS THIS CORPUS MUST REACH, AND `_check_arms()` REFUSES TO WRITE A
CORPUS THAT DOES NOT** (`PROTOCOL_PHP.md` §A2a rule 1). The defect's own branch
is `if (ce->num_interfaces > 0)` at `zend_compile.c:2570` -- **two arms** -- and
_040 §5.5 enumerates the rest:

  * **both arms of `:2570`**: windows with `n_decl == 0` (no allocation at all,
    `php_shim_tally() == 0`) and with `n_decl > 0`;
  * **all four arms of the query loops**: zero iterations (`n_decl == 0`), a
    match on the FIRST slot, a match on the LAST slot, and no match at all
    (the full scan);
  * **both consumers**, `QUERY_DEREF` and `QUERY_CMP`;
  * **all three op codes** reached, and `op` taken past one wrap of its `% 3`
    so a rung that read the raw byte would differ;
  * the three head words' `%` exercised rather than left the identity;
  * and, NEGATIVELY, **NO measured window may leave a slot unwritten when a
    QUERY runs.** That is the ADVERSARIAL case, and keeping it out of the
    measured corpus is what makes the R1-vs-R1h comparison a comparison
    between two runs of one program (`check.py` stage 7h).

⚠ **THIS IS A SUPERSET CONDITION AND `model.py` CARRIES THE SHARPER ONE.**
`_check_arms` asserts over EVERY window in the file; the driver picks windows
from a checksum-derived index and need not visit them all, so
`model.py::selfcheck` check 2 re-asserts the same arm table over **the calls
the driver actually makes**.

⚠ **`_check_arms` RE-DERIVES THE COVERAGE FROM THE BYTES IT JUST WROTE** rather
than trusting the builder's intention -- *"an intention in a comment is what
ph03 had, and it was wrong for a task"* (§A2a rule 1).

Four things about the sizes are deliberate.

  * **`small` and `large` have different strides** -- 221 and 439 -- so
    `harness/check.py`'s `d(Ir)/d(work)` assertion has two probe shapes with
    different `work_per_call`.
  * **they are in different residue classes mod 4, 8 and 16** (221 = 13*17 is
    1/5/13, 439 is prime and is 3/7/7), so consecutive windows do not share a
    cache-set alignment and neither stride is a power of two.
  * **the op count scales with the stride**: `cap = (stride - 76) // 9`, 16 and
    40, so per-call work really does scale with `work_per_call`. The 12-byte
    header, the 8-entry pool read and the `memset` are a FIXED per-call term
    that does not, and ../NOTES.md §8 decomposes the marginal rather than
    presenting it as a pure op rate.
  * **`n_decl` is 6 on 15 of every 16 windows and 0 on the sixteenth.** Both
    arms of `:2570` have to be in the MEASURED corpus (rule 1), and the two
    arms cannot have the same per-window work, so the row declares the spread
    instead of pretending to uniformity. `n_pool` is 8 on every measured
    window so the pool read is a constant.

⚠⚠ **FIVE ADVERSARIAL FILES, AND THE ONE A READER EXPECTS IS NOT AMONG THEM.**
There is no `adversarial-deref.bin`, and the reason is the row's own result:
`d09cdd9f71f3` zeroes the array and adds NO consumer guard, so **every blob on
which R1's `QUERY_DEREF` faults is a blob on which R1h NULL-dereferences too**,
and `check.py` stage 7h requires R1h clean on every input in this directory and
says so in terms ("a per-input declaration here would let a pattern declare its
way out of the only thing this stage asks"). That is `.memory-php/02-ladder.md`
F31's standing limitation binding for the first time on a real row. The
dereference evidence therefore lives in `controls/r1h_consumers.py`, which
builds both C arms itself and generates its own blobs -- see ../NOTES.md §5.

What IS here is the half that is safe under every detector:

  * `adversarial-cmp`       an unwritten slot READ by the compare-only
                            consumer. No dereference, so no rung faults --
                            and **R3 diverges from the other five**, because
                            its array is only as long as the `FILL`s it saw.
  * `adversarial-shadowed`  an unwritten slot EXISTS and a `QUERY_DEREF` runs,
                            but an earlier slot matches and the loop breaks
                            first. Must-NOT-fire: the fault needs the slot to
                            be REACHED, not merely to exist.
  * `adversarial-covered`   `adversarial-cmp`'s op stream with the coverage
                            completed. Must-NOT-fire: without it the divergence
                            above could be the op SHAPE rather than the
                            coverage, and nothing in the number would say which.
  * `adversarial-nowin`     stride larger than the blob, so the driver makes NO
                            kernel call. The control for all of them.
  * `adversarial-trunc`     a declared payload length past the bytes present;
                            the driver must exit 5 rather than read past the
                            end. Nothing about ph53 is involved, and that is
                            the point.
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

MAXD = 16          # c/kernel.h PH53_MAXD -- the largest ce->num_interfaces
MAXP = 8           # c/kernel.h PH53_MAXP -- interfaces in scope
HDR = 12
POOL_OFF = HDR
OPS_OFF = POOL_OFF + 8 * MAXP      # 76
OP_BYTES = 9

OP_FILL, OP_QD, OP_QC = 0, 1, 2

SMALL_STRIDE, SMALL_WINS = 221, 64
LARGE_STRIDE, LARGE_WINS = 439, 4096

N_DECL = 6         # the measured corpus's `implements` count on 15/16 windows
N_POOL = 8         # ... and its pool size on every measured window

# The pool ids. Distinct, and none of them 0, so a slot that reads back as NULL
# (R1h) or as a fill byte (R1 under ASan) can never be mistaken for a match.
POOL_IDS = (0x0C1A55_000000_01, 0x0C1A55_000000_02, 0x0C1A55_000000_03,
            0x0C1A55_000000_04, 0x0C1A55_000000_05, 0x0C1A55_000000_06,
            0x0C1A55_000000_07, 0x0C1A55_000000_08)


def u32(v):
    assert 0 <= v <= 0xFFFFFFFF, v
    return bytes(((v) & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF))


def u64(v):
    return u32(v & 0xFFFFFFFF) + u32((v >> 32) & 0xFFFFFFFF)


def cap_of(stride):
    return (stride - OPS_OFF) // OP_BYTES


# ---------------------------------------------------------------------------
# window construction
# ---------------------------------------------------------------------------

def op(rng, kind, a, b):
    """One op record. `kind` is 0/1/2 and the byte written is taken past one
    wrap of the kernel's `% 3`, so a rung reading the raw byte differs."""
    ob = kind + 3 * rng.randrange(0, 80)          # <= 2 + 237 = 239
    return bytes((ob,)) + u32(a) + u32(b)


def window(rng, stride, n_decl, ops, n_pool=N_POOL, pool_ids=POOL_IDS):
    """Assemble one window. `ops` is a list of (kind, a, b) already reduced;
    the raw head words carry a random multiple of the modulus so the kernel's
    `%` is exercised rather than being the identity."""
    cap = cap_of(stride)
    assert len(ops) <= cap, (len(ops), cap)
    nd_w = n_decl + (MAXD + 1) * rng.randrange(0, 3)
    np_w = (n_pool - 1) + MAXP * rng.randrange(0, 3)
    no_w = len(ops) + (cap + 1) * rng.randrange(0, 3)
    out = [u32(nd_w), u32(np_w), u32(no_w)]
    for j in range(MAXP):
        out.append(u64(pool_ids[j] if j < len(pool_ids) else 0))
    for (kind, a, b) in ops:
        out.append(op(rng, kind, a, b))
    body = b"".join(out)
    assert len(body) == OPS_OFF + OP_BYTES * len(ops)
    return body + bytes(stride - len(body))       # tail padding, never read


def benign_ops(rng, n_decl, n_ops, n_pool=N_POOL):
    """`n_decl` FILLs covering 0..n_decl-1 in order, then QUERYs.

    The QUERY targets walk the four arms of the scan loop: the pool index the
    FIRST fill used, the one the LAST fill used, two in the middle, and the
    pool indices NO fill used (the no-match / full-scan arm). That last arm is
    why `n_pool` must exceed `n_decl`."""
    assert n_ops >= n_decl
    ops = []
    for d in range(n_decl):
        # d = a % n_decl; pool index d = b % n_pool
        a = d + n_decl * rng.randrange(0, 4)
        b = d + n_pool * rng.randrange(0, 4)
        ops.append((OP_FILL, a, b))
    if n_decl == 0:
        targets = [0, 1, 2, 3, 4, 5, 6, 7]        # every query has 0 iterations
    else:
        targets = [0,                              # match on the FIRST slot
                   n_decl - 1,                     # match on the LAST slot
                   n_decl,                         # NO match (full scan)
                   n_pool - 1,                     # NO match (full scan)
                   n_decl // 2, 1]                 # matches in the middle
    q = n_ops - n_decl
    for i in range(q):
        t = targets[i % len(targets)] % n_pool
        a = t + n_pool * rng.randrange(0, 4)
        kind = OP_QD if i % 2 == 0 else OP_QC      # both consumers, alternating
        ops.append((kind, a, 0))
    return ops


def tiled(rng, nwin, stride):
    """The measured corpus."""
    cap = cap_of(stride)
    out = []
    for k in range(nwin):
        nd = 0 if k % 16 == 15 else N_DECL         # both arms of :2570
        # vary the op count in the two positions the last op's kind occupies,
        # so the corpus is not one op stream repeated
        n_ops = cap if k % 3 else cap - 1
        ops = benign_ops(rng, nd, n_ops)
        if k % 4 == 2:                             # swap the query order
            head, tail = ops[:nd], ops[nd:]
            out.append(window(rng, stride, nd, head + tail[::-1]))
        else:
            out.append(window(rng, stride, nd, ops))
    return b"".join(out)


# ---------------------------------------------------------------------------
# the assertion half of A2a rule 1
# ---------------------------------------------------------------------------

def decode(win):
    """(n_decl, n_pool, n_ops, pool, ops) exactly as every rung derives it."""
    def rd32(o):
        return win[o] | (win[o + 1] << 8) | (win[o + 2] << 16) | (win[o + 3] << 24)

    def rd64(o):
        return rd32(o) | (rd32(o + 4) << 32)

    stride = len(win)
    cap = cap_of(stride)
    n_decl = rd32(0) % (MAXD + 1)
    n_pool = 1 + rd32(4) % MAXP
    n_ops = rd32(8) % (cap + 1)
    pool = [rd64(POOL_OFF + 8 * j) for j in range(MAXP)]
    ops = []
    for o in range(n_ops):
        p = OPS_OFF + OP_BYTES * o
        ops.append((win[p] % 3, rd32(p + 1), rd32(p + 5)))
    return n_decl, n_pool, n_ops, pool, ops


def _check_arms(name, blob, stride):
    """Refuse to write a corpus that misses an arm, re-deriving every claim
    from the bytes just written. Returns a list of problems."""
    bad = []
    nwin = len(blob) // stride
    if nwin == 0:
        return [f"{name}: no complete window at stride {stride}"]
    decl_arms = set()          # {False, True} for `ce->num_interfaces > 0`
    ops_seen = set()
    raw_wrap = False           # some op byte >= 3, so `% 3` is not the identity
    hdr_wrap = [False, False, False]
    q_arms = set()             # 'zero', 'first', 'last', 'none', 'mid'
    consumers = set()
    uncovered = 0              # a QUERY ran with some slot unwritten
    out_of_order = 0
    n_q = 0
    for k in range(nwin):
        win = blob[k * stride:(k + 1) * stride]
        n_decl, n_pool, n_ops, pool, ops = decode(win)
        decl_arms.add(n_decl > 0)
        if n_decl and n_pool <= n_decl:
            bad.append(f"{name}: window {k} has n_pool={n_pool} <= "
                       f"n_decl={n_decl}, so the no-match arm of the scan loop "
                       f"is unreachable in it")
        # the head words' `%` must not be the identity somewhere
        raw = (win[0] | (win[1] << 8) | (win[2] << 16) | (win[3] << 24),
               win[4] | (win[5] << 8) | (win[6] << 16) | (win[7] << 24),
               win[8] | (win[9] << 8) | (win[10] << 16) | (win[11] << 24))
        if raw[0] >= MAXD + 1:
            hdr_wrap[0] = True
        if raw[1] >= MAXP:
            hdr_wrap[1] = True
        if raw[2] >= n_ops + 1:
            hdr_wrap[2] = True
        # walk the op stream exactly as a rung does
        written = [None] * n_decl
        nfill = 0
        seen_query = False
        for (kind, a, b) in ops:
            ops_seen.add(kind)
            if kind == OP_FILL:
                if seen_query:
                    out_of_order += 1
                d = (a % n_decl) if n_decl else 0
                if n_decl:
                    if written[d] is not None or d != nfill:
                        out_of_order += 1
                    written[d] = b % n_pool
                    nfill += 1
            else:
                seen_query = True
                n_q += 1
                consumers.add(kind)
                if any(w is None for w in written):
                    uncovered += 1
                t = a % n_pool
                if n_decl == 0:
                    q_arms.add("zero")
                elif written[0] == t:
                    q_arms.add("first")
                elif t not in written:
                    q_arms.add("none")
                elif written[n_decl - 1] == t and t not in written[:n_decl - 1]:
                    q_arms.add("last")
                else:
                    q_arms.add("mid")
        if any(win[OPS_OFF + OP_BYTES * o] >= 3 for o in range(n_ops)):
            raw_wrap = True
    if decl_arms != {False, True}:
        bad.append(f"{name}: `if (ce->num_interfaces > 0)` at "
                   f"zend_compile.c:2570 takes only the arm(s) "
                   f"{sorted(decl_arms)} -- BOTH are required, because the "
                   f"n_decl == 0 arm allocates nothing at all and a rung that "
                   f"allocated anyway would agree everywhere else")
    if ops_seen != {OP_FILL, OP_QD, OP_QC}:
        bad.append(f"{name}: op codes reached {sorted(ops_seen)}, want all of "
                   f"[0 FILL, 1 QUERY_DEREF, 2 QUERY_CMP]")
    if consumers != {OP_QD, OP_QC}:
        bad.append(f"{name}: consumers reached {sorted(consumers)} -- the row "
                   f"exists because d09cdd9f71f3 lands at two DIFFERENT "
                   f"severities on these two, so a corpus with one of them "
                   f"cannot show the result")
    if not raw_wrap:
        bad.append(f"{name}: every op byte is already < 3, so the kernel's "
                   f"`% 3` is the identity everywhere and a rung that omitted "
                   f"it would agree on every window")
    for i, w in enumerate(hdr_wrap):
        if not w:
            bad.append(f"{name}: head word {i}'s `%` is the identity on every "
                       f"window, so a rung that omitted it would agree")
    want_q = {"zero", "first", "last", "none", "mid"}
    if q_arms != want_q:
        bad.append(f"{name}: the scan loop reaches arms {sorted(q_arms)}, want "
                   f"{sorted(want_q)} -- zero iterations, a match on the first "
                   f"slot, a match on the last, no match at all (the full "
                   f"scan) and a match in the middle")
    if out_of_order:
        bad.append(f"{name}: {out_of_order} FILL(s) are out of order, repeated "
                   f"or after a QUERY. Benign means the FILLs write 0.."
                   f"n_decl-1 each exactly once in INCREASING order before any "
                   f"QUERY, because R3 is PHP 5.2.0's append-and-count repair "
                   f"and its slot order is the FILLs' arrival order")
    if uncovered:
        bad.append(f"{name}: {uncovered} of {n_q} QUERY op(s) run with a slot "
                   f"still unwritten, i.e. on the defect. ../spec.md pins the "
                   f"measured corpus clear of it, because check.py stage 7h "
                   f"requires R1h clean on every input here and R1h still "
                   f"NULL-dereferences an unwritten slot")
    return bad


def write(name, n_iters, stride, body, declared_len=None):
    path = os.path.join(HERE, name)
    payload = slb.pack_head1_bytes(stride, body)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<5d} "
          f"cap={cap_of(stride):<3d} blob={len(body):<9d} "
          f"windows={len(body) // stride if stride else 0:<6d} "
          f"file={os.path.getsize(path)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()

    for mod in (4, 8, 16):
        if SMALL_STRIDE % mod == LARGE_STRIDE % mod:
            print(f"REFUSING TO WRITE: strides {SMALL_STRIDE}/{LARGE_STRIDE} "
                  f"are both == {SMALL_STRIDE % mod} mod {mod}")
            return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod "
          f"4, 8 and 16; caps {cap_of(SMALL_STRIDE)}/{cap_of(LARGE_STRIDE)}")

    small = tiled(random.Random(SEED + 1), SMALL_WINS, SMALL_STRIDE)
    large = tiled(random.Random(SEED + 2), LARGE_WINS, LARGE_STRIDE)
    problems = (_check_arms("small.bin", small, SMALL_STRIDE)
                + _check_arms("large.bin", large, LARGE_STRIDE))
    if problems:
        print("REFUSING TO WRITE -- the corpus misses an arm "
              "(PROTOCOL_PHP.md A2a rule 1):")
        for p in problems:
            print(f"    {p}")
        return 1
    print("  arm coverage ok on both measured inputs")

    write("small.bin", 25_000, SMALL_STRIDE, small)
    write("large.bin", 10_000, LARGE_STRIDE, large)

    # ---- the adversarial five ------------------------------------------
    # n_iters is small: every one of these calls does the same thing and there
    # is nothing to learn from doing it 25 000 times.
    rng = random.Random(SEED + 9)
    S = SMALL_STRIDE

    # (1) the compare-only consumer over an UNWRITTEN slot.
    #     zend_compile.c:1951 reads the slot and does not dereference it, so no
    #     rung faults -- R1 compares whatever `malloc` left there, R1h compares
    #     NULL, and both answer "no match".  ⭐ R3 is the one that diverges:
    #     its array is one element long, so it examines ONE slot where every
    #     other rung examines two, and the folded scan index differs.
    write("adversarial-cmp.bin", 64, S,
          window(rng, S, 2, [(OP_FILL, 0, 0), (OP_QC, 1, 0), (OP_QC, 0, 0)]))

    # (2) an unwritten slot EXISTS and a QUERY_DEREF runs, but slot 0 matches
    #     and the loop breaks before reaching slot 1.  MUST-NOT-FIRE: the fault
    #     needs the unwritten slot to be REACHED, not merely to exist, and
    #     without this control "R1 faults when a slot is unwritten" is untested
    #     in the direction that matters.
    write("adversarial-shadowed.bin", 64, S,
          window(rng, S, 2, [(OP_FILL, 0, 0), (OP_QD, 0, 0)]))

    # (3) (1)'s op stream with the coverage COMPLETED.  MUST-NOT-FIRE: without
    #     it, (1)'s R3 divergence could be the op shape rather than the
    #     coverage and nothing in the number would say which.
    write("adversarial-covered.bin", 64, S,
          window(rng, S, 2, [(OP_FILL, 0, 0), (OP_FILL, 1, 1),
                             (OP_QC, 1, 0), (OP_QC, 0, 0)]))

    # (4) the control for all of them: a stride larger than the blob, so the
    #     driver skips the loop and makes NO kernel call.  If this one ever
    #     showed a diagnostic, the diagnostic would not be from the kernel.
    write("adversarial-nowin.bin", 64, S + 64,
          window(rng, S, 2, [(OP_FILL, 0, 0), (OP_QC, 1, 0)]))

    # (5) a declared payload length past the bytes present.  The driver must
    #     exit 5; nothing about ph53 is involved and that is the point.
    body = window(rng, S, 2, [(OP_FILL, 0, 0), (OP_QC, 1, 0)])
    write("adversarial-trunc.bin", 64, S, body,
          declared_len=8 + len(body) + 4096)
    return 0


if __name__ == "__main__":
    sys.exit(main())
