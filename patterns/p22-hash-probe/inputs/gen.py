#!/usr/bin/env python3
"""p22-hash-probe input generator. Deterministic; the gate hashes THIS FILE and
never the blobs, so the determinism is the whole basis of the claim that the
committed `.bin` files are reproducible. Regenerate twice and diff.

File format (`.memory/02-bench-rules.md`): `u64 n_iters`, `u64 payload_len`,
payload. p22's payload is p38's, p47's, p10's and nine others':

    word 0     u64  stride      # bytes per window
    byte 8..   u8[] blob        # the windows

Window layout (../spec.md):

    byte 0..4   nkey  u32 LE    DECLARED key count      ATTACKER DATA
    byte 4..    one key per byte                        ATTACKER DATA

**The structural parameter that decides whether this pattern's bug fires is
`nd`, the number of DISTINCT non-zero key bytes in a window.** The table has
`TABCAP = 64` slots; `nfill` can never exceed `nd`, so a window with `nd < 64`
can never fill the table and `c/kernel.c`'s missing capacity check can never be
reached. Every matrix and sweep blob here is generated from an alphabet of at
most `MAX_ND_SAFE = 48` distinct keys and `audit()` REFUSES to write one that
is not. Two blobs carry a per-row ceiling instead: `adversarial-full.bin`, which
carries 64 distinct keys followed by a 65th that is absent and is THE ONLY INPUT
IN THIS PATTERN ON WHICH ANY CELL FAILS TO TERMINATE, and
`adversarial-nearfull.bin`, which carries 63 and is the negative control for it.

⚠ The alphabet ceiling is belt-and-braces; the load-bearing check is that
`audit()` SIMULATES THE UNGUARDED RUNG on every window of every blob and refuses
to write one that would hang unless the row declares it.

`--sweep` appends the `sweep-*` band. The prefix is the whole mechanism
(`check.py`'s inline `sweep-` test, `measure.py:64`): `sweep-*` blobs are
diagnostic, are not part of the measured matrix, and a band named otherwise
would enter it.

**Two structural parameters vary INDEPENDENTLY in the sweep** -- `nk` (key bytes
per window) and `nd` (distinct keys drawn from) -- which is what makes
additivity extrapolation available, the only out-of-sample test this project has
that can fail (`.memory/03-measurement.md`).

⚠ **RESIDUE CLASSES of the fitted regressor are printed on every row**, because
p38's additivity miss was two-thirds a band sitting at `nw = 0 (mod 8)` while
the third did not. Band k holds `nd = 24` and band d holds `nk = 256`; band x
draws (nk, nd) pairs from neither, and the residues of `nkw` are listed so a fit
that depends on the class is visible before it is published.

⚠ **The regressor is `nkw = min(nkey, stride - 4)` PER WINDOW, and never
`stride - 4`** -- see `keys_walked()`. The first version of this diagnostic
printed `(stride - HDR) % 8`, which is the regressor `controls/sweep_ir.py:84`
explicitly warns against, and it therefore printed ONE residue for the whole of
band x, whose true residues are {0, 4, 6} (TASK_070_REVIEW F6).

⚠ On a HETEROGENEOUS blob -- the `sweep-h*` band, which exists to be one -- the
row prints a `nkw` RANGE and the set of per-window residues. The quantity the
law is fitted against there is a weighted MEAN over exactly the calls the
marginal differences, it is not an integer (98.24, 183.04, 124.00), and its
residue is not determined by the per-window set. `controls/sweep_ir.py` prints
that one; this row does not pretend to.

The keys come from a plain LCG rather than `random`, so no draw is
rejection-sampled and the stream cannot re-converge after an edit
(`.memory/05-layout.md`).
"""

import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HDR = 4                 # nkey:u32
TABCAP = 64             # must equal SLB_P22_TABCAP and every rung's const
EMPTY = 0
SENT = 251
MAX_ND_SAFE = 48        # the alphabet ceiling every non-hanging blob obeys
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


def alphabet(nd, seed):
    """`nd` DISTINCT key values, drawn from 1..255 rather than from 1..nd.

    ⚠ **This is not cosmetic and the first draft got it wrong.** `hash(k) =
    k * 2654435761 / 16777216 % 64` is very nearly injective on 1..64 (41 of 64
    slots, and injective on 1..32), so an alphabet of {1..nd} produces a table
    with **no collisions at all** and a probe loop that never executes: the
    first version of this generator shipped `maxprobe = 0` on `small.bin` and
    `2` on `large.bin`. Drawing `nd` values out of the whole byte range gives
    the birthday-collision rate a real hash table has."""
    g = lcg(seed)
    seen, out = set(), []
    while len(out) < nd:
        v = 1 + (next(g) >> 5) % 255
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def keys_from(nk, nd, seed):
    """`nk` key bytes drawn from an `nd`-value alphabet. `nd <= 255`."""
    a = alphabet(nd, seed)
    g = lcg(seed + 1)
    return [a[(next(g) >> 7) % nd] for _ in range(nk)]


def window(keys, stride, nkey=None):
    """`stride` bytes: the 4-byte `nkey` header, the keys, zero padding. The
    padding is never read, because `nkey` stops the walk first."""
    n = len(keys) if nkey is None else nkey
    b = struct.pack("<I", n) + bytes(keys)
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
    Independent of model.py on purpose: a generator that imported the model
    could not catch a model bug.

    Returns `(result, nfill, max_probe, hangs_unguarded)`. The last element is
    the fact the whole pattern turns on: it is True when this window would make
    `c/kernel.c` -- the rung WITHOUT `nfill < TABCAP` -- run for ever."""
    if stride < HDR:
        return 0, 0, 0, False
    nkey = int.from_bytes(blob[off:off + 4], "little")
    if nkey == 0:
        return 0, 0, 0, False
    tab = [EMPTY] * TABCAP
    nfill, acc, p, maxpr, hang = 0, 0, HDR, 0, False
    for _ in range(nkey):
        if stride - p < 1:
            break
        k = blob[off + p]
        p += 1
        if k != EMPTY and nfill < TABCAP:
            i = k * 2654435761 // 16777216 % TABCAP
            pr = 0
            while tab[i] != EMPTY and tab[i] != k:
                i = (i + 1) % TABCAP
                pr += 1
            maxpr = max(maxpr, pr)
            if tab[i] == EMPTY:
                tab[i] = k
                nfill += 1
            acc = (acc * 31 + i) & MASK
        else:
            if k != EMPTY and nfill == TABCAP:
                # The unguarded rung reaches its probe loop here. It terminates
                # only if `k` is already in the table.
                if k not in tab:
                    hang = True
            acc = (acc * 31 + SENT) & MASK
    return (acc * 31 + nfill) & MASK, nfill, maxpr, hang


def keys_walked(blob, off, stride):
    """`nkw` for ONE window: the number of key bytes the kernel actually walks,
    `min(nkey, stride - HDR)`.

    ⚠ **NOT `stride - HDR`.** `nkey` is a per-window header field and the walk
    stops at whichever of the two runs out first. `controls/sweep_ir.py:84`
    says the same thing about the same quantity, and says it because the first
    version of THAT script used `stride - 4` and reported residuals up to 992
    against a law whose residual is 0.00 -- and then the first version of THIS
    diagnostic used it too, printing `nk%8=4` for the whole of band x, whose
    true regressor `nkw` spans residues {0, 4, 6} (TASK_070_REVIEW F6). A
    reader auditing the residue-class design from the generator's own output
    would have concluded band x sits at ONE residue: p38's exact failure
    mode."""
    if stride < HDR:
        return 0
    nkey = int.from_bytes(blob[off:off + 4], "little")
    return min(nkey, stride - HDR)


def distinct_keys(blob, off, stride):
    if stride < HDR:
        return 0
    n = keys_walked(blob, off, stride)
    return len({b for b in blob[off + HDR:off + HDR + n] if b != EMPTY})


def audit(name, blob, stride, allow_hang=False, expect_zero_ok=False,
          max_nd=MAX_ND_SAFE):
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
        nd = distinct_keys(blob, w * stride, stride)
        hang = sim(blob, w * stride, stride)[3]
        if hang and not allow_hang:
            return (f"{name}: window {w} makes the UNGUARDED rung hang and the "
                    f"blob is not declared as a hanging one")
        if not hang and allow_hang and w == 0:
            return (f"{name}: declared as a hanging blob, but window 0 does "
                    f"NOT make the unguarded rung hang")
        if not allow_hang and nd > max_nd:
            return (f"{name}: window {w} has {nd} distinct keys, over the "
                    f"{max_nd} ceiling")
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

    # ---- small: stride 132 -> 128 key bytes per window, alphabet of 32, so
    #      the table settles at nfill = 32 (50% load) and probe chains are
    #      short but real.
    S_NK, S_ND = 128, 32
    small = b"".join(window(keys_from(S_NK, S_ND, 7 * w + 1), HDR + S_NK)
                     for w in range(40))
    rows.append(("small.bin", small, HDR + S_NK, 20000, False, False))

    # ---- large: stride 1028 -> 1024 key bytes, alphabet of 40, so the table
    #      settles at nfill = 40 (62.5% load): the probe loop runs a real
    #      number of times per key and the fold is 8x longer than small's.
    L_NK, L_ND = 1024, 40
    large = b"".join(window(keys_from(L_NK, L_ND, 13 * w + 3), HDR + L_NK)
                     for w in range(40))
    rows.append(("large.bin", large, HDR + L_NK, 20000, False, False))

    # ---- degenerate: every early exit, plus a window that does real work
    #      first so the blob is not absorbing.
    D_ST = HDR + 128
    d = [window(keys_from(128, 16, 5), D_ST)]              # window 0: real work
    d.append(window([], D_ST, nkey=0))                     # nkey == 0
    d.append(window([0] * 128, D_ST))                      # every key is EMPTY
    d.append(window(keys_from(20, 12, 9), D_ST, nkey=999))  # nkey > keys present
    degen = b"".join(d)
    rows.append(("degenerate.bin", degen, D_ST, 4000, False, False))

    # ---- adversarial-full: **THE HANGING INPUT, and the only one.** 64
    #      distinct keys fill the table; the 65th is absent from it, so
    #      c/kernel.c's probe loop has no EMPTY slot to stop at and no matching
    #      key to find. c/kernel_hardened.c and all four Rust rungs see
    #      nfill == TABCAP and fold SENT.
    full = window(list(range(1, 65)) + [65], HDR + 128)
    rows.append(("adversarial-full.bin", full, HDR + 128, 1, True, True))

    # ---- adversarial-nearfull: the NEGATIVE control for it. 63 distinct keys,
    #      then 64 more drawn from the same 63. `nfill` stops one short of
    #      TABCAP, so every rung terminates -- including c/kernel.c. This is
    #      what says the hang needs a FULL table and not merely a busy one.
    nearfull = window(list(range(1, 64)) + [1 + (t % 63) for t in range(64)],
                      HDR + 128)
    rows.append(("adversarial-nearfull.bin", nearfull, HDR + 128, 200,
                 False, False, 63))

    # ---- adversarial-nkeybig: `nkey` saturated, so only the `len - p < 1`
    #      guard stops the walk. Every key is well formed.
    nkb = window(keys_from(96, 24, 11), HDR + 128, nkey=0xFFFFFFFF)
    rows.append(("adversarial-nkeybig.bin", nkb, HDR + 128, 200, False, False))

    # ---- adversarial-allempty: every key byte is the EMPTY sentinel, so the
    #      table stays empty and every key folds SENT. nfill == 0.
    allz = window([0] * 128, HDR + 128)
    rows.append(("adversarial-allempty.bin", allz, HDR + 128, 200, False, True))

    # ---- adversarial-stride3: below the driver's `stride_w >= 4`; every rung
    #      skips the loop and prints 0.
    rows.append(("adversarial-stride3.bin", b"\x01\x00\x00", 3, 100,
                 False, True))

    made = []
    for row in rows:
        name, blob, stride, iters, hang, zok = row[:6]
        mnd = row[6] if len(row) > 6 else MAX_ND_SAFE
        emit(os.path.join(out, name), iters, blob, stride)
        made.append((name, blob, stride, iters, hang, zok, mnd))
    return made


# ------------------------------------------------------------------ sweep ----
def sweep(out):
    """Two bands, each varying ONE structural parameter with the other held
    fixed, plus an additivity band and a heterogeneous one. `sweep-*` blobs
    never enter the matrix."""
    rows = []
    # band k: key bytes per window; alphabet held at 24 (nd mod 8 == 0).
    for nk in (16, 32, 48, 64, 96, 128, 192, 256, 384, 512):
        st = HDR + 512
        rows.append((f"sweep-k{nk:03d}.bin", b"".join(
            window(keys_from(nk, 24, 31 * w + nk), st) for w in range(6)), st))
    # band d: alphabet size; key bytes held at 256 (nk mod 8 == 0).
    for nd in (1, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48):
        st = HDR + 256
        rows.append((f"sweep-d{nd:02d}.bin", b"".join(
            window(keys_from(256, nd, 37 * w + nd), st) for w in range(6)), st))
    # band x: the additivity test set -- (nk, nd) pairs neither band contains,
    # and DELIBERATELY spanning both residue classes of nk mod 8.
    for nk, nd in ((40, 6), (72, 18), (100, 30), (150, 10), (200, 44), (300, 36)):
        st = HDR + 300
        rows.append((f"sweep-x{nk:03d}n{nd:02d}.bin", b"".join(
            window(keys_from(nk, nd, 41 * w + nk + nd), st)
            for w in range(6)), st))
    # band h: HETEROGENEOUS within a blob, so a row is not a scalar multiple of
    # any band above.
    for tag, shapes in (("h1", [(64, 8), (192, 36), (32, 20)]),
                        ("h2", [(128, 3), (256, 46)]),
                        ("h3", [(96, 12), (48, 44), (224, 26)])):
        st = HDR + max(n for n, _ in shapes)
        rows.append((f"sweep-{tag}.bin",
                     b"".join(window(keys_from(n, d, 43 * t + n), st)
                              for t, (n, d) in enumerate(shapes)), st))

    made = []
    for name, blob, stride in rows:
        emit(os.path.join(out, name), 2000, blob, stride)
        made.append((name, blob, stride, 2000, False, False, MAX_ND_SAFE))
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
    for name, blob, stride, iters, hang, zok, mnd in made:
        z = zok or name.startswith("adversarial")
        p = audit(name, blob, stride, allow_hang=hang, expect_zero_ok=z,
                  max_nd=mnd)
        if p:
            bad.append(p)
        nwin = len(blob) // stride if stride else 0
        if stride >= HDR and nwin:
            r0, nf0, mp0, hg0 = sim(blob, 0, stride)
            nd0 = distinct_keys(blob, 0, stride)
            mx = max(sim(blob, w * stride, stride)[2] for w in range(nwin))
            # ⚠ THE REGRESSOR IS `nkw`, PER WINDOW, and a blob can carry more
            # than one value of it -- the sweep-h* band exists to. Print the
            # RANGE and the SET of residues, never `(stride - HDR) % 8`, which
            # collapses a whole band onto one class (TASK_070_REVIEW F6).
            nkws = sorted({keys_walked(blob, w * stride, stride)
                           for w in range(nwin)})
            res = "{" + ",".join(str(v % 8) for v in sorted({v % 8
                                                             for v in nkws})) + "}"
            nkw = (f"{nkws[0]}" if len(nkws) == 1
                   else f"{nkws[0]}..{nkws[-1]}")
        else:
            r0, nf0, mp0, hg0, nd0, mx = 0, 0, 0, False, 0, 0
            nkw, res = "0", "{}"
        print(f"{name:30s} stride={stride:5d} nwin={nwin:4d} n_iters={iters:6d} "
              f"bytes={len(blob):8d} nd(w0)={nd0:3d} nfill(w0)={nf0:3d} "
              f"maxprobe={mx:3d} nkw={nkw:9s} nkw%8={res:9s} "
              f"hang={'YES' if hg0 else 'no':3s} win0={r0}")
    for p in bad:
        print("AUDIT:", p, file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
