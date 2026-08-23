#!/usr/bin/env python3
"""p36-vtable-dispatch input generator. Deterministic; the gate hashes THIS FILE
and never the blobs, so the determinism is the whole basis of the claim that the
committed `.bin` files are reproducible. Regenerate twice and diff.

File format (`.memory/02-bench-rules.md`): `u64 n_iters`, `u64 payload_len`,
payload. p36's payload is p22's, p38's, p47's, p10's and eleven others':

    word 0     u64  stride      # bytes per window
    byte 8..   u8[] blob        # the windows

Window layout (../spec.md):

    byte 0..4   nrec  u32 LE    DECLARED record count       ATTACKER DATA
    byte 4..    (opcode, operand) byte pairs                ATTACKER DATA

**THE STRUCTURAL PARAMETER THAT DECIDES WHETHER THIS PATTERN'S BUG FIRES IS ONE
BYTE.** `NOPS = 8`, opcodes are one byte, so 248 of 256 values are out of table
and a single byte edit turns a conforming blob into an adversarial one.
`audit()` refuses to write any blob carrying an out-of-table opcode unless the
row declares it, and refuses to write a declared one whose window 0 does not
carry one.

`--sweep` appends the `sweep-*` band. The prefix is the whole mechanism
(`check.py`'s inline `sweep-` test, `measure.py:64`): `sweep-*` blobs are
diagnostic, are not part of the measured matrix, and a band named otherwise
would enter it.

**THREE bands, and the middle one is p36's own axis.**

  * band **n** varies the record count with the opcode stream's *statistics*
    held fixed -- the length axis every pattern here has.
  * band **mix** ⚠ **holds the OPCODE MULTISET EXACTLY FIXED and varies only its
    ORDER.** Every blob in the band contains 32 of each of the eight opcodes per
    window and the identical operand stream; only the arrangement differs, from
    eight sorted runs of 32 through runs of 16, 8, 4 and 2, a period-8 cycle, and
    a pseudo-random permutation. **The executed instruction count is therefore
    identical across the whole band BY CONSTRUCTION** -- the same eight callees
    run the same number of times -- while the indirect call goes from a single
    target per run to a target the branch predictor cannot learn. This is the
    band that makes `Ir` and `ns` disagree for a NAMED reason, and
    `callgrind --branch-sim=yes` reports the mechanism directly as `Bi` / `Bim`
    (`.memory/00-environment.md`).
    ⚠ **`mixrand6` is the band's SIXTH-WINDOW control, added at TASK_073 on
    TASK_072_REVIEW.** Every other blob of the band repeats ONE 256-opcode
    sequence in all six windows; `mixrand6` gives each window a DIFFERENT
    permutation of the same multiset, so a history-indexed predictor has 1536
    positions to learn instead of 256 while `Ir` stays fixed by construction.
    It is what turns ../NOTES.md 7's *disclosure* about the band into a
    measurement.
  * band **t** varies the number of DISTINCT targets (1, 2, 4, 8) at a fixed
    record count. ⚠ Unlike band mix this does **not** hold the multiset fixed,
    so its `Ir` is not identical by construction; it is measured and reported
    rather than assumed (../NOTES.md 6).

⚠ **RESIDUE CLASSES.** `.memory/03-measurement.md`'s rule after p38: a fit whose
bands all sit at one residue of the regressor fits in sample and misses out of
it. p36's regressor is `nrw`, the records actually walked per window. Band n's
values are `{8, 18, 32, 46, 61, 96, 128, 151, 192, 257, 384, 512}`, which span
residues **{0, 1, 2, 5, 6, 7} mod 8** and **{0, 1, 2} mod 3**, and the row prints
both so a class-dependent fit is visible before it is published. Band mix holds
`nrw = 256` fixed on purpose -- it is not a length band and no length law is
fitted on it.
⚠ **THIS PARAGRAPH SAID `{0, 2, 4, 6}` AND "both parities of `nrw mod 3`" UNTIL
TASK_073** (TASK_072_REVIEW m3). Both were wrong, in the one file the
residue-class rule exists to make checkable, and in the strict direction: the
band's real coverage is six residues mod 8 rather than four, and `mod 3` has
three classes and no parity. `main()`'s own printed rows and ../NOTES.md 4 had
the right sets the whole time; only the documentation was wrong. The measurement
is unaffected, which is why fixing it is a comment-only edit and
`harness/measure.py --check-stale` reports **GEN-ONLY** rather than STALE.

The opcodes and operands come from a plain LCG rather than `random`, so no draw
is rejection-sampled and the stream cannot re-converge after an edit
(`.memory/05-layout.md`).
"""

import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HDR = 4                 # nrec:u32
NOPS = 8                # must equal SLB_P36_NOPS and every rung's const
SENT = 251
MASK = (1 << 64) - 1

#: THE OP SET, constant for constant identical to c/kernel.c's op0..op7.
#: Re-implemented here rather than imported from model.py on purpose: a
#: generator that imported the model could not catch a model bug.
OPS = [
    lambda x: x ^ 0x9E3779B97F4A7C15,
    lambda x: x ^ 0xFF51AFD7ED558CCD,
    lambda x: (x + 0x2545F4914F6CDD1D) & MASK,
    lambda x: (x + 0xC4CEB9FE1A85EC53) & MASK,
    lambda x: (x - 0x61C8864680B583EB) & MASK,
    lambda x: (x - 0xBF58476D1CE4E5B9) & MASK,
    lambda x: x ^ 0x94D049BB133111EB,
    lambda x: (x + 0x9E6C63D0676A9A99) & MASK,
]


# ------------------------------------------------------------------ build ----
def lcg(seed):
    """A bare Lehmer generator. Every draw consumes exactly one step, so adding
    or removing a blob shifts later blobs by a predictable amount and nothing is
    rejection-sampled."""
    x = (seed * 2 + 1) & 0xFFFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        yield x


def records(nrec, seed, ops=None):
    """`nrec` (opcode, operand) pairs. `ops` is the opcode alphabet, default the
    whole table."""
    ops = list(range(NOPS)) if ops is None else list(ops)
    g = lcg(seed)
    out = bytearray()
    for _ in range(nrec):
        out.append(ops[(next(g) >> 7) % len(ops)])
        out.append((next(g) >> 5) & 0xFF)
    return bytes(out)


def records_ordered(order, seed):
    """Records whose OPCODE sequence is given exactly and whose operand stream
    is drawn from `seed`. Band mix uses this so that two blobs differ in opcode
    ORDER and in nothing else."""
    g = lcg(seed)
    out = bytearray()
    for op in order:
        out.append(op)
        out.append((next(g) >> 5) & 0xFF)
    return bytes(out)


def window(rec, stride, nrec=None):
    """`stride` bytes: the 4-byte `nrec` header, the record pairs, zero padding.
    The padding is never read, because `nrec` stops the walk first."""
    n = len(rec) // 2 if nrec is None else nrec
    b = struct.pack("<I", n) + rec
    if len(b) > stride:
        raise SystemExit(f"gen.py: window of {len(b)} bytes exceeds stride {stride}")
    return b + b"\x00" * (stride - len(b))


def emit(path, n_iters, blob, stride):
    payload = struct.pack("<Q", stride) + blob
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", n_iters, len(payload)))
        f.write(payload)


# ------------------------------------------------------------------ audit ----
def sim(blob, off, stride):
    """The kernel's DEFINED semantics (i.e. c/kernel_hardened.c's),
    re-implemented here so the generator can assert what it is shipping.

    Returns `(result, records_walked, out_of_table_opcodes)`. The last element
    is the fact the whole pattern turns on: it counts the opcodes on which
    `c/kernel.c` -- the rung WITHOUT `op < NOPS` -- loads a code pointer from
    past the end of `TABLE` and calls it."""
    if stride < HDR:
        return 0, 0, 0
    nrec = int.from_bytes(blob[off:off + 4], "little")
    if nrec == 0:
        return 0, 0, 0
    acc, p, t, noob = 0, HDR, 0, 0
    while t < nrec:
        if stride - p < 2:
            break
        op = blob[off + p]
        arg = blob[off + p + 1]
        p += 2
        if op < NOPS:
            acc = OPS[op](acc ^ arg)
        else:
            noob += 1
            acc = (acc * 31 + SENT) & MASK
        t += 1
    return (acc * 31 + t) & MASK, t, noob


def recs_walked(blob, off, stride):
    """`nrw` for ONE window: `min(nrec, (stride - 4) // 2)`.

    ⚠ **NOT `(stride - 4) // 2`.** `nrec` is a per-window header field and the
    walk stops at whichever of the two runs out first. This is the regressor
    every p36 law is fitted against, and p22's generator records what went
    wrong when the analogous quantity was taken to be the stride alone."""
    if stride < HDR:
        return 0
    nrec = int.from_bytes(blob[off:off + 4], "little")
    return min(nrec, (stride - HDR) // 2)


def audit(name, blob, stride, allow_oob=False, expect_zero_ok=False):
    """What must hold of every shipped blob."""
    if stride < HDR:
        return None if name.startswith("adversarial") else \
            f"{name}: stride {stride} < {HDR} and it is not an adversarial row"
    nwin = len(blob) // stride
    if nwin == 0:
        return f"{name}: no whole window"
    if len(blob) % stride:
        return f"{name}: blob {len(blob)} is not a multiple of stride {stride}"
    for w in range(nwin):
        noob = sim(blob, w * stride, stride)[2]
        if noob and not allow_oob:
            return (f"{name}: window {w} carries {noob} out-of-table opcode(s) "
                    f"and the blob is not declared as an adversarial one")
        if not noob and allow_oob and w == 0:
            return (f"{name}: declared as an out-of-table blob, but window 0 "
                    f"carries no opcode >= {NOPS}")
    r0 = sim(blob, 0, stride)[0]
    # `.memory/01-ladder.md`: window 0 returning 0 is an ABSORBING STATE --
    # `acc` stays 0, the Lemire index stays 0, and every later call re-runs
    # window 0. A blob whose first window folds to 0 measures one window.
    if r0 == 0 and not expect_zero_ok:
        return f"{name}: window 0 folds to 0 (absorbing state)"
    return None


# ----------------------------------------------------------------- matrix ----
def matrix(out):
    rows = []

    # ---- small: stride 260 -> 128 records per window, L1-resident.
    S_N = 128
    small = b"".join(window(records(S_N, 7 * w + 1), HDR + 2 * S_N)
                     for w in range(40))
    rows.append(("small.bin", small, HDR + 2 * S_N, 20000, False, False))

    # ---- large: stride 2052 -> 1024 records, 8x small's fold and past L2 over
    #      40 windows (82 080 bytes).
    L_N = 1024
    large = b"".join(window(records(L_N, 13 * w + 3), HDR + 2 * L_N)
                     for w in range(40))
    rows.append(("large.bin", large, HDR + 2 * L_N, 20000, False, False))

    # ---- degenerate: every early exit, plus a window that does real work
    #      first so the blob is not absorbing.
    D_ST = HDR + 2 * 128
    d = [window(records(128, 5), D_ST)]                    # window 0: real work
    d.append(window(b"", D_ST, nrec=0))                    # nrec == 0
    d.append(window(records(20, 9), D_ST, nrec=999))       # nrec > records present
    d.append(window(records(12, 17), D_ST))                # short, padded
    degen = b"".join(d)
    rows.append(("degenerate.bin", degen, D_ST, 4000, False, False))

    # ---- adversarial-oob: **THE BUG.** One window; record 40's opcode is 8,
    #      the NEAREST out-of-table value, so `TABLE[8]` is the 8 bytes
    #      immediately after the table. Under ASan that address is a redzone and
    #      the report names `TABLE` by name; on a plain build it is whatever the
    #      linker put there.
    a = bytearray(records(128, 23))
    a[80] = 8
    oob = window(bytes(a), HDR + 2 * 128)
    rows.append(("adversarial-oob.bin", oob, HDR + 2 * 128, 100, True, True))

    # ---- adversarial-oobmax: the same edit at the FAR end of the byte range,
    #      opcode 255, i.e. 1976 bytes past the table. It is a separate row
    #      because the two do not behave the same under the sanitizer build:
    #      only the near one lands in `TABLE`'s redzone.
    b = bytearray(records(128, 29))
    b[80] = 255
    oobmax = window(bytes(b), HDR + 2 * 128)
    rows.append(("adversarial-oobmax.bin", oobmax, HDR + 2 * 128, 100, True, True))

    # ---- adversarial-nrecbig: `nrec` saturated, so only the `len - p < 2`
    #      cursor guard stops the walk. Every opcode is in table.
    nrb = window(records(128, 31), HDR + 2 * 128, nrec=0xFFFFFFFF)
    rows.append(("adversarial-nrecbig.bin", nrb, HDR + 2 * 128, 200, False, False))

    # ---- adversarial-stride5: below the driver's `stride_w >= 6`; every rung
    #      skips the loop and prints 0.
    rows.append(("adversarial-stride5.bin", b"\x01\x00\x00\x00\x00", 5, 100,
                 False, True))

    made = []
    for name, blob, stride, iters, oob_ok, zok in rows:
        emit(os.path.join(out, name), iters, blob, stride)
        made.append((name, blob, stride, iters, oob_ok, zok))
    return made


# ------------------------------------------------------------------ sweep ----
def rand_perm(nrec, seed):
    """A pseudo-random permutation of the band-mix multiset: `nrec // NOPS`
    copies of each of the eight opcodes, Fisher-Yates-shuffled from `seed` with
    this file's own LCG.

    Factored out at TASK_073 so `mix_orders`' `rand` entry and the new
    `mixrand6` blob draw from ONE implementation. `rand_perm(256, 97)` is
    byte-for-byte what `mix_orders` produced before the refactor, which is
    checked the only way that means anything: regenerate and diff the committed
    `sweep-mixrand.bin`."""
    per = nrec // NOPS
    base = [o for o in range(NOPS) for _ in range(per)]
    g = lcg(seed)
    for i in range(len(base) - 1, 0, -1):
        j = (next(g) >> 3) % (i + 1)
        base[i], base[j] = base[j], base[i]
    assert all(base.count(o) == per for o in range(NOPS))
    return base


def mix_orders(nrec):
    """The band-mix opcode arrangements. **Every one is a permutation of the
    same multiset** -- `nrec // NOPS` copies of each of the eight opcodes -- so
    the eight callees run the same number of times in every blob of the band and
    the executed instruction count is identical by construction."""
    per = nrec // NOPS
    out = {}
    for run in (per, 16, 8, 4, 2, 1):
        if run > per:
            continue
        # runs of `run`, cycling through the opcodes
        seq = []
        blocks = nrec // run
        for bidx in range(blocks):
            seq.extend([bidx % NOPS] * run)
        # `blocks` is a multiple of NOPS whenever run divides per*NOPS evenly,
        # which every value above satisfies; assert it rather than assume it.
        assert len(seq) == nrec and all(seq.count(o) == per for o in range(NOPS))
        out[f"run{run:03d}"] = seq
    # a pseudo-random permutation of the SAME multiset
    out["rand"] = rand_perm(nrec, 97)
    return out


def sweep(out):
    rows = []
    # band n: records per window. Residues of `nrw` mod 8 span {0,1,2,5,6,7} and
    # mod 3 spans {0,1,2}, so no fitted law can be an artefact of one class.
    # (This comment said {0,2,4,6} until TASK_073; the printed rows below always
    # said otherwise -- TASK_072_REVIEW m3.)
    for n in (8, 18, 32, 46, 61, 96, 128, 151, 192, 257, 384, 512):
        st = HDR + 2 * n
        rows.append((f"sweep-n{n:03d}.bin", b"".join(
            window(records(n, 53 * w + n), st) for w in range(6)), st))
    # band mix: THE OPCODE-ORDER AXIS. Same multiset, same operand stream, six
    # windows, only the arrangement differs.
    MIX_N = 256
    st = HDR + 2 * MIX_N
    for tag, seq in sorted(mix_orders(MIX_N).items()):
        rows.append((f"sweep-mix{tag}.bin", b"".join(
            window(records_ordered(seq, 61 * w + 5), st) for w in range(6)), st))
    # ⚠ `mixrand6`: SIX DIFFERENT permutations of the SAME multiset, one per
    # window, against `mixrand`'s one sequence repeated six times. The multiset
    # is still fixed per window, so `Ir` is still constant BY CONSTRUCTION; what
    # changes is how much history a predictor would have to learn (1536
    # positions against 256). Same operand seeds `61 * w + 5` as the rest of the
    # band, so the two differ in opcode ORDER and in nothing else.
    rows.append(("sweep-mixrand6.bin", b"".join(
        window(records_ordered(rand_perm(MIX_N, 97 + 13 * w), 61 * w + 5), st)
        for w in range(6)), st))
    # band t: number of DISTINCT targets, at a fixed record count. The multiset
    # is NOT held fixed here, so this band's `Ir` is measured, not assumed.
    # ⚠ The alphabets are SPREAD over the three operations rather than being
    # `0..k`: `op0`, `op1` and `op6` are all `^`, so an alphabet of `{0}` or
    # `{0,1}` makes the fold a pure xor chain that cancels itself down to a
    # 10-bit accumulator -- measured, `win0 = 752` -- and the driver's Lemire
    # index is then pinned at window 0.
    for k, alpha in ((1, [2]), (2, [2, 4]), (4, [0, 2, 4, 6]),
                     (8, list(range(8)))):
        st = HDR + 2 * 256
        rows.append((f"sweep-t{k}.bin", b"".join(
            window(records(256, 71 * w + k, ops=alpha), st)
            for w in range(6)), st))

    made = []
    for name, blob, stride in rows:
        emit(os.path.join(out, name), 2000, blob, stride)
        made.append((name, blob, stride, 2000, False, False))
    return made


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    made = matrix(a.out)
    if a.sweep:
        made += sweep(a.out)
    bad = []
    for name, blob, stride, iters, oob_ok, zok in made:
        z = zok or name.startswith("adversarial")
        p = audit(name, blob, stride, allow_oob=oob_ok, expect_zero_ok=z)
        if p:
            bad.append(p)
        nwin = len(blob) // stride if stride else 0
        if stride >= HDR and nwin:
            r0, nrw0, oob0 = sim(blob, 0, stride)
            nrws = sorted({recs_walked(blob, w * stride, stride)
                           for w in range(nwin)})
            r8 = "{" + ",".join(str(v) for v in sorted({v % 8 for v in nrws})) + "}"
            r3 = "{" + ",".join(str(v) for v in sorted({v % 3 for v in nrws})) + "}"
            nrw = f"{nrws[0]}" if len(nrws) == 1 else f"{nrws[0]}..{nrws[-1]}"
            toob = sum(sim(blob, w * stride, stride)[2] for w in range(nwin))
        else:
            r0, nrw0, oob0, toob = 0, 0, 0, 0
            nrw, r8, r3 = "0", "{}", "{}"
        print(f"{name:26s} stride={stride:5d} nwin={nwin:4d} n_iters={iters:6d} "
              f"bytes={len(blob):8d} nrw={nrw:9s} nrw%8={r8:11s} nrw%3={r3:8s} "
              f"oob={toob:3d} win0={r0}")
    for p in bad:
        print("AUDIT:", p, file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
