#!/usr/bin/env python3
"""p19-state-machine input generator. Deterministic; the gate hashes THIS FILE
and never the blobs, so the determinism is the whole basis of the claim that the
committed `.bin` files are reproducible. Regenerate twice and diff.

File format (`.memory/02-bench-rules.md`): `u64 n_iters`, `u64 payload_len`,
payload. p19's payload is p36's, p22's, p38's, p47's and eleven others':

    word 0     u64  stride      # bytes per window
    byte 8..   u8[] blob        # the windows

Window layout (../spec.md):

    byte 0    .. 2048   the transition table, NST rows of 256   ATTACKER DATA
    byte 2048 .. stride the message                             ATTACKER DATA

**THE TABLE IS ATTACKER DATA AND THAT IS THE WHOLE PATTERN.** With a
tool-generated table the bug is unreachable (../NOTES.md 0a run A, exhaustive);
p19 exists because real DFA decoders -- AppArmor's policy engine among them --
unpack their transition tables from an untrusted blob and validate them once.
`audit()` refuses to write any blob carrying an entry >= NST unless the row
declares it, and refuses to write a declared one that carries none.

⚠ **AND IT AUDITS THE HARM, NOT JUST THE BYTES.** `sim_unvalidated()`
re-implements `c/kernel.c` -- the rung with no validation pass -- and reports
whether the walk leaves `[0, n_blob)`. Every row declares `oob` and the audit
fails if the declaration and the simulation disagree. That is what keeps
`adversarial-confuse` honest: its table entry of 8 is out of table but the row
it names lands INSIDE the window's own message region, so the read is defined
and no sanitizer has anything to say. **THREE ROWS DIFFERING IN ONE BYTE OF ONE
TABLE ENTRY GIVE THREE DIFFERENT OUTCOMES**: 8 is in bounds and silent, 10 is
0..255 bytes past the blob and ASan names the object, 255 is 65 280 bytes past
and ASan reports a bare SEGV. The family is shipped so that the claim "this bug
class is memory-unsafe" is bounded rather than blanket, and so that "the
sanitizer catches it" is bounded too.

`--sweep` appends the `sweep-*` band. The prefix is the whole mechanism
(`check.py`'s inline `sweep-` test, `measure.py:64`): `sweep-*` blobs are
diagnostic, are not part of the measured matrix, and a band named otherwise
would enter it and cost a full re-measure.

**ONE band, and it is the length axis the two published laws are fitted on.**
`sweep-m*` varies the MESSAGE length `m = stride - 2048` with the table held
byte-identical across the whole band, so every difference is the fold and
nothing else. The laws are `R2 - R4 = 6.25*m - 8` and `R3 - R4 = 1.00*m - 2`.

⚠ **RESIDUE CLASSES** (`.memory/03-measurement.md`, the rule that came out of
p38): a fit whose bands all sit at one residue of the regressor fits in sample
and misses out of it. p19's regressor is `m`, and the unroll factor of the
unchecked fold is **4**, so `m mod 4` is the class that could hide a term. The
band's values are
`{64, 97, 128, 130, 150, 191, 195, 256, 333, 340, 384, 512, 701, 1024, 1365,
2048, 3072, 4096, 5001}`, which cover **all four residues mod 4** and **all
eight mod 8** -- and `main()` prints the coverage, so a class-dependent fit is
visible before it is published rather than after.

The table entries and message bytes come from a plain LCG rather than `random`,
so no draw is rejection-sampled and the stream cannot re-converge after an edit
(`.memory/05-layout.md`).
"""

import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NST = 8                       # must equal SLB_P19_NST and every rung's const
TBL = NST * 256               # 2048
REJ = 0xD1B54A32D192ED03
MASK = (1 << 64) - 1


# ------------------------------------------------------------------ build ----
def lcg(seed):
    """A bare Lehmer generator. Every draw consumes exactly one step, so adding
    or removing a blob shifts later blobs by a predictable amount and nothing is
    rejection-sampled."""
    x = (seed * 2 + 1) & 0xFFFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        yield x


def table(seed):
    """A VALID transition table: `TBL` bytes, every entry in `[0, NST)`."""
    g = lcg(seed)
    return bytes((next(g) >> 9) % NST for _ in range(TBL))


def message(m, seed):
    """`m` message bytes over the full byte range."""
    g = lcg(seed)
    return bytes((next(g) >> 5) & 0xFF for _ in range(m))


def window(tbl, msg):
    if len(tbl) != TBL:
        raise SystemExit(f"gen.py: table is {len(tbl)} bytes, not {TBL}")
    return tbl + msg


def emit(path, n_iters, blob, stride):
    payload = struct.pack("<Q", stride) + blob
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", n_iters, len(payload)))
        f.write(payload)


def emit_truncated(path, n_iters, blob, stride, extra):
    """Declare `extra` more payload bytes than the file carries. A conforming
    driver notices and exits 5."""
    payload = struct.pack("<Q", stride) + blob
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", n_iters, len(payload) + extra))
        f.write(payload)


# ------------------------------------------------------------------ audit ----
def sim(blob, off, stride):
    """The kernel's DEFINED semantics (i.e. c/kernel_hardened.c's),
    re-implemented here so the generator can assert what it is shipping.
    Deliberately NOT imported from model.py: a generator that imported the
    model could not catch a model bug."""
    if stride <= TBL:
        return 0, 0
    w = blob[off:off + stride]
    nbad = sum(1 for e in w[:TBL] if e >= NST)
    if nbad:
        return REJ, nbad
    st, acc = 0, 0
    for b in w[TBL:]:
        st = w[st * 256 + b]
        acc = (acc * 31 + st) & MASK
    return (acc * 31 + st) & MASK, 0


def sim_unvalidated(blob, off, stride, n_blob):
    """`c/kernel.c`: the fold with NO validation pass. Returns
    `(reads_outside_blob, max_index_reached)`. Stops at the first read that
    leaves `[0, n_blob)` -- what a real run finds there is not defined."""
    if stride <= TBL:
        return False, 0
    st, hi = 0, 0
    for p in range(off + TBL, off + stride):
        idx = off + st * 256 + blob[p]
        hi = max(hi, idx)
        if idx >= n_blob:
            return True, idx
        st = blob[idx]
    return False, hi


def audit(name, blob, stride, oob=False, bad_ok=False, zero_ok=False):
    """What must hold of every shipped blob."""
    if stride <= 0:
        return f"{name}: stride {stride}"
    if len(blob) % stride:
        return f"{name}: blob {len(blob)} is not a multiple of stride {stride}"
    nwin = len(blob) // stride
    if nwin == 0:
        return f"{name}: no whole window"
    nbad_total = 0
    for w in range(nwin):
        nbad = sim(blob, w * stride, stride)[1]
        nbad_total += nbad
        if nbad and not bad_ok:
            return (f"{name}: window {w} carries {nbad} out-of-table entr(ies) "
                    f"and the blob is not declared as an adversarial one")
    if bad_ok and nbad_total == 0:
        return (f"{name}: declared as an out-of-table blob, but no window's "
                f"table carries an entry >= {NST}")
    got_oob = any(sim_unvalidated(blob, w * stride, stride, len(blob))[0]
                  for w in range(nwin))
    if got_oob != oob:
        return (f"{name}: declared oob={oob} but c/kernel.c's walk "
                f"{'DOES' if got_oob else 'does NOT'} leave the blob")
    r0 = sim(blob, 0, stride)[0]
    # `.memory/01-ladder.md`: window 0 returning 0 is an ABSORBING STATE --
    # `acc` stays 0, the Lemire index stays 0, and every later call re-runs
    # window 0. A blob whose first window folds to 0 measures one window.
    if r0 == 0 and not zero_ok:
        return f"{name}: window 0 folds to 0 (absorbing state)"
    return None


# ----------------------------------------------------------------- matrix ----
def confuse_blob(entry, m, seed):
    """One window whose table drives the walk into state `entry`, which is out
    of table. The first 256 message bytes are all in `[0, NST)` on purpose:
    row `entry` of the table, for a small `entry`, IS those bytes, so after the
    confusion the walk lands back on a valid state and the only thing that
    happened is that the message was read as if it were a transition row.

    With `entry = 8` the read stays inside the window: defined, silent, wrong.
    With `entry = 255` it is 65 280 bytes past the window: out of the blob.
    The two blobs differ in ONE byte of the table."""
    tbl = bytearray(table(seed))
    tbl[0 * 256 + 0] = 3            # state 0, byte 0 -> state 3
    tbl[3 * 256 + 1] = entry        # <-- THE BAD ENTRY: state 3, byte 1 -> entry
    g = lcg(seed + 977)
    head = bytes((next(g) >> 11) % NST for _ in range(256))
    tail = bytes((next(g) >> 5) & 0xFF for _ in range(m - 256))
    msg = bytearray(head + tail)
    msg[0] = 0                      # drives state 0 -> 3
    msg[1] = 1                      # drives state 3 -> `entry`
    return window(bytes(tbl), bytes(msg))


def matrix(out):
    rows = []

    # ---- small: 16 windows of 2048 table + 256 message, L1/L2-resident.
    S_M = 256
    small = b"".join(window(table(7 * w + 1), message(S_M, 71 * w + 5))
                     for w in range(16))
    rows.append(("small.bin", small, TBL + S_M, 8000,
                 dict(oob=False, bad_ok=False, zero_ok=False)))

    # ---- large: 16 windows of 2048 table + 4096 message, 16x small's fold.
    L_M = 4096
    large = b"".join(window(table(13 * w + 3), message(L_M, 131 * w + 11))
                     for w in range(16))
    rows.append(("large.bin", large, TBL + L_M, 2000,
                 dict(oob=False, bad_ok=False, zero_ok=False)))

    # ---- degenerate: the shapes that fold to nothing, with a window that does
    #      real work FIRST so the blob is not absorbing.
    #
    #      ⚠ **THE REJ PATH IS NOT HERE, AND IT CANNOT BE.** A window with an
    #      out-of-table entry is exactly a window on which `c/kernel.c`
    #      disagrees with every other rung, so a blob carrying one is an
    #      `adversarial-*` blob BY CONSTRUCTION -- the gate requires every cell
    #      to agree on a non-adversarial input, and the first version of this
    #      row put an invalid table in window 1 and failed eight checksum rows
    #      and the sanitizer row with it. REJ is covered by
    #      `adversarial-confuse` and `adversarial-oob`, on which the four Rust
    #      rungs and both hardened C cells all return it.
    D_M = 128
    d = [window(table(5), message(D_M, 23))]                     # real work
    d.append(window(bytes(TBL), message(D_M, 37)))               # all-zero table
    d.append(window(table(41), bytes(D_M)))                      # all-zero msg
    d.append(window(table(43), message(D_M, 47)))                # real work
    degen = b"".join(d)
    rows.append(("degenerate.bin", degen, TBL + D_M, 2000,
                 dict(oob=False, bad_ok=False, zero_ok=False)))

    # ---- adversarial-confuse: **STATE CONFUSION WITH NO MEMORY EVENT.** One
    #      table entry names state 8, the NEAREST out-of-table value; row 8 is
    #      the window's own first 256 message bytes. c/kernel.c reads them,
    #      returns a wrong answer, exits 0, and neither sanitizer fires. Every
    #      other rung returns REJ.
    A_M = 512
    conf = confuse_blob(NST, A_M, 101)
    rows.append(("adversarial-confuse.bin", conf, TBL + A_M, 100,
                 dict(oob=False, bad_ok=True, zero_ok=True)))

    # ---- adversarial-oobnear: **THE SAME BLOB WITH ONE BYTE CHANGED.** The
    #      entry is 10, so the next row starts at window byte 2560 -- 0..255
    #      bytes PAST a 2 560-byte blob, i.e. in the allocator's redzone. This
    #      is the row on which ASan names the object.
    oobnear = confuse_blob(10, A_M, 101)
    rows.append(("adversarial-oobnear.bin", oobnear, TBL + A_M, 100,
                 dict(oob=True, bad_ok=True, zero_ok=True)))

    # ---- adversarial-oob: **THE SAME BLOB WITH THAT ONE BYTE SET WIDER.** The
    #      entry is 255, so the next row starts 65 280 bytes into a 2 560-byte
    #      blob -- past the redzone and off the mapped page. ASan reports a
    #      bare SEGV instead of a heap-buffer-overflow, which is the point of
    #      shipping the two rows: how far past the object the index lands
    #      decides WHICH diagnostic you get, and one attacker byte decides that.
    oob = confuse_blob(255, A_M, 101)
    rows.append(("adversarial-oob.bin", oob, TBL + A_M, 100,
                 dict(oob=True, bad_ok=True, zero_ok=True)))

    # ---- adversarial-tiny: stride below the table size. The driver enters the
    #      loop (its only guard is `stride_w > 0`) and the KERNEL's `len <= TBL`
    #      test returns 0 on every call, so the degenerate branch every rung
    #      carries is reachable from the measured domain instead of being dead
    #      code the proof still has to discharge.
    rows.append(("adversarial-tiny.bin", message(256, 61), 64, 100,
                 dict(oob=False, bad_ok=False, zero_ok=True)))

    # ---- adversarial-shortlen: `payload_len` declares 64 bytes more than the
    #      file carries. Handled in `slb_load` / `driver::load`, exit 5.
    made = []
    for name, blob, stride, iters, kw in rows:
        emit(os.path.join(out, name), iters, blob, stride)
        made.append((name, blob, stride, iters, kw))
    short = b"".join(window(table(7 * w + 1), message(S_M, 71 * w + 5))
                     for w in range(2))
    emit_truncated(os.path.join(out, "adversarial-shortlen.bin"), 100,
                   short, TBL + S_M, 64)
    made.append(("adversarial-shortlen.bin", short, TBL + S_M, 100,
                 dict(oob=False, bad_ok=False, zero_ok=False)))
    return made


# ------------------------------------------------------------------ sweep ----
#: The message lengths of band `m`. Chosen to cover every residue mod 4 (the
#: unchecked fold's unroll factor) and every residue mod 8.
SWEEP_M = [64, 97, 128, 130, 150, 191, 195, 256, 333, 340, 384, 512, 701,
           1024, 1365, 2048, 3072, 4096, 5001]


def sweep(out):
    """Band m: the message length axis, table held byte-identical."""
    made = []
    tbl = table(2027)
    for m in SWEEP_M:
        blob = b"".join(window(tbl, message(m, 3 * m + 7)) for _ in range(4))
        name = f"sweep-m{m:05d}.bin"
        emit(os.path.join(out, name), 400, blob, TBL + m)
        made.append((name, blob, TBL + m, 400,
                     dict(oob=False, bad_ok=False, zero_ok=False)))
    return made


# ------------------------------------------------------------------- main ----
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* band")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    made = matrix(a.out)
    if a.sweep:
        made += sweep(a.out)

    bad = 0
    for name, blob, stride, iters, kw in made:
        problem = audit(name, blob, stride, **kw)
        if problem:
            print(f"AUDIT FAIL  {problem}", file=sys.stderr)
            bad += 1
            continue
        nwin = len(blob) // stride
        r0, nb = sim(blob, 0, stride)
        m = stride - TBL if stride > TBL else 0
        print(f"{name:28s} stride={stride:6d} m={m:6d} "
              f"nwin={nwin:3d} blob={len(blob):8d} iters={iters:6d} "
              f"bad_entries={nb} win0={r0}")

    # The three confusion rows must differ in EXACTLY ONE byte from each other
    # -- that is the claim the family is shipped to make.
    b1 = dict((n, b) for n, b, *_ in made)
    base = "adversarial-confuse.bin"
    for other in ("adversarial-oobnear.bin", "adversarial-oob.bin"):
        if base not in b1 or other not in b1:
            continue
        c, o = b1[base], b1[other]
        d = [i for i in range(len(c)) if c[i] != o[i]]
        print(f"\n{base} vs {other}: {len(d)} byte(s) differ, at {d} "
              f"({c[d[0]] if d else '-'} -> {o[d[0]] if d else '-'})")
        if len(d) != 1:
            print(f"AUDIT FAIL  {base} and {other} must differ in one byte",
                  file=sys.stderr)
            bad += 1

    if a.sweep:
        r4 = sorted({m % 4 for m in SWEEP_M})
        r8 = sorted({m % 8 for m in SWEEP_M})
        print(f"\nsweep band m: {len(SWEEP_M)} lengths, "
              f"m mod 4 covers {r4}, m mod 8 covers {r8}")

    if bad:
        raise SystemExit(f"{bad} blob(s) failed the audit")


if __name__ == "__main__":
    main()
