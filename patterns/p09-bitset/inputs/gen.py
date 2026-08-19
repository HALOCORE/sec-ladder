#!/usr/bin/env python3
"""Generate p09's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and since TASK_021 `harness/check.py` hashes it into `source_sha256`, so every
law measured on these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p09-bitset/inputs/gen.py            # the 5 matrix inputs
    python3 patterns/p09-bitset/inputs/gen.py --sweep    # + the three sweep bands

Payload layout (../spec.md), p16's/p17's/p05's/p07's/p11's/p03's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nbits u32 LE      declared bit count    ATTACKER DATA
    byte 4..8    nq    u32 LE      declared query count  ATTACKER DATA
    data_start = 8 ; avail = len - 8 bytes actually present
    nwords = (nbits + 63) >> 6
    words   : nwords * 8 bytes at window byte 8              u64 LE
    queries : nq * 4 bytes after them                        u32 LE bit indices

and the kernel probes bit `q` of the bitset for each query. The guard that R1
omits, and the only thing it omits, is the range check on the bit index:

    R1   w = load_u64(buf, ws + 8*(q >> 6)); ...            /* no test */
    R1h  if (q < nbits) { w = load_u64(buf, ws + 8*(q >> 6)); ... }

--------------------------------------------------------------------------
WHY EVERY QUERY IN `small` AND `large` IS IN RANGE
--------------------------------------------------------------------------
`.memory/02-bench-rules.md` requires all rungs -- **R1 included** -- to print the
same checksum on the two measured inputs. R1 has no `q < nbits` test, so a single
out-of-range query on `small` or `large` would make R1 fold a word the checked
rungs skip and the two would disagree. So `small` and `large` are 100% guarded
and R1-vs-R1h there is the cost of a check that is **always taken**, with the
signature, the decoders and the popcount pass all held fixed.

The consequence, stated because it is a real limitation of the shipped matrix and
not a detail: **on `small` and `large` the two regressors `nq` and `xguard`
(guarded queries) are the same number.** Only `sweep-d*` separates them, and only
`sweep-w*` separates either from `nwords`. That is the whole reason those bands
exist and it is why ../NOTES.md 4 reports the rank of the pooled design before it
reports a coefficient (`.memory/01-ladder.md`, p03: a band that holds one
regressor constant cannot identify it, and a per-band fit can return garbage at
zero residual).

The `sweep-d*` band deliberately violates the all-in-range rule, which is sound
because `harness/check.py` and `harness/measure.py` both skip the `sweep-` prefix
(`.memory/05-layout.md`: that prefix IS the mechanism). Its out-of-range queries
are drawn from `[nbits, nbits + 63]` so that even R1 stays inside the window --
nothing faults if somebody runs a C cell on one by hand, and the band measures
the guard rather than the crash.

--------------------------------------------------------------------------
small AND large DIFFER IN BIT-SET DENSITY, NOT ONLY IN SIZE
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues and
records p01's modulus 4, p02's 16, p16's 4, p17's 4, p05's 8-and-16, p07's
octave, p11's string length and p03's pop density. p09's second axis is the
**bit-set density** -- the fraction of set bits in the words, which is both the
`hits` rate of the query loop and the popcount pass's input distribution -- so
`small` is ~50% and `large` ~25%. `_check_residues()` additionally asserts that
`nbits`, `nq`, `nwords` and the stride differ mod 4, 8, 16 and 32 between the
two, and that both `nbits` are NOT multiples of 64 so that both exercise a
partial last word.

**`stride` is congruent to 0 mod 4 by construction** (`8 + 8*nwords + 4*nq`), so
the stride is checked mod 8, 16 and 32 only; asserting mod 4 would be asserting
something the format forbids. There is no unroll factor to alias against: the
query loop is a data-dependent branch on an attacker word, and ../NOTES.md 1
checks on the disassembly that neither gcc, clang nor rustc unrolls it.

--------------------------------------------------------------------------
SIZES
--------------------------------------------------------------------------
  * `small`: 12 windows x 1108 B = 13.0 KiB, inside this box's 32 KiB L1.
    nbits 1100 (18 words), 239 queries, all in range, ~50% of bits set.
  * `large`: 1900 windows x 4328 B = 7.84 MiB, ~8x this box's 1 MiB/core L2, so
    the window the driver jumps to is cold. nbits 7990 (125 words), 830 queries,
    all in range, ~25% of bits set.
  * every adversarial input is exactly one window (`n_blob == stride`), for
    p16's, p17's, p07's, p11's and p03's reason: `k = (acc * nwin) >> 64` is
    pseudo-random over `[0, nwin)`, so with several windows the malformed one is
    hit only probabilistically.
  * **window 0 must serve something** (p17, `.memory/01-ladder.md`): a window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`. Every
    window here returns `(acc*31 + nbits)*31 + nq` with `nbits != 0`, so no
    window can return 0 except by failing the length check on purpose, which is
    exactly and only what `adversarial-count` does -- and that file has ONE
    window, so `k` is 0 regardless and the absorbing state cannot bite.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run, so the cost of a row is the payload `to_vec` (a bulk copy --
`head1_u64_bytes`) plus `4 x stride` bytes read. That is 4432 byte-visits on
`small` and 17 312 on `large`, against `.memory`'s measured budget of ~3.05 M in
180 s, so both rows are ~180x inside it. The only cost is the 8.2 MB `to_vec`;
p07's 12 MB one passes.
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "common"))
import slb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 0x5EC1ADDE  # "sec-ladder", fixed forever: the .bin files are gitignored
                   # and must be regenerable byte-for-byte from this file alone.

HDR = 8                                   # nbits:u32 + nq:u32

# The two measured shapes. The pop-... the BIT-SET density is the second axis and
# `_check_residues()` is what holds it apart from the first.
SMALL_NBITS, SMALL_NQ, SMALL_SETP = 1100, 239, 0.50
SMALL_WINS = 12
LARGE_NBITS, LARGE_NQ, LARGE_SETP = 7990, 830, 0.25
LARGE_WINS = 1900

SMALL_ITERS, LARGE_ITERS = 6000, 1500
ADV_ITERS = 8                             # R1 executes UB on one of them; there
                                          # is nothing to learn from doing it
                                          # 6000 times.

RESIDUE_MODULI = (4, 8, 16, 32)


# ------------------------------------------------------------------ shapes ---

def nwords_of(nbits):
    """`(nbits + 63) >> 6`, the same expression every rung computes."""
    return (nbits + 63) >> 6


def stride_of(nbits, nq):
    return HDR + 8 * nwords_of(nbits) + 4 * nq


def words(rng, nwords, setp):
    """`nwords` u64 words with each bit set independently with probability
    `setp`. The density is both the query loop's `hits` rate and the popcount
    pass's input distribution, so one knob moves both -- which is what makes it
    a usable second axis rather than two."""
    out = []
    for _ in range(nwords):
        w = 0
        for b in range(64):
            if rng.random() < setp:
                w |= 1 << b
        out.append(w)
    return out


def queries(rng, nq, nbits, nguard):
    """`nq` bit indices of which exactly `nguard` satisfy `q < nbits`.

    The out-of-range ones are drawn from `[nbits, nbits + 63]` so that even a
    rung with no guard stays inside the window -- see the module docstring."""
    assert 0 <= nguard <= nq
    qs = [rng.randrange(0, nbits) for _ in range(nguard)]
    qs += [nbits + rng.randrange(0, 64) for _ in range(nq - nguard)]
    rng.shuffle(qs)
    return qs


def window(nbits_decl, nq_decl, ws, qs):
    """A window: the two declared counts, then the words, then the queries.

    `nbits_decl`/`nq_decl` are written verbatim rather than derived from `ws`
    and `qs`, so that `adversarial-count` can declare a shape the window cannot
    hold -- which is the row that shows the length check is in every rung."""
    out = bytearray(nbits_decl.to_bytes(4, "little"))
    out += nq_decl.to_bytes(4, "little")
    for w in ws:
        out += (w & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little")
    for q in qs:
        out += (q & 0xFFFFFFFF).to_bytes(4, "little")
    return bytes(out)


def guarded(qs, nbits):
    """How many queries take the guard. This is the regressor ../NOTES.md 4's
    laws are linear in, and on `small`/`large` it equals `nq` -- see the module
    docstring for why, and why the sweep is what separates the two."""
    return sum(1 for q in qs if q < nbits)


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    or residue artefact. Returns a list of problems (empty when healthy)."""
    bad = []
    if abs(SMALL_SETP - LARGE_SETP) < 0.10:
        bad.append(f"small and large bit-set density ({SMALL_SETP}, "
                   f"{LARGE_SETP}) are within 0.10 of each other; the bit-set "
                   f"density IS p09's second axis (../spec.md) and the two "
                   f"measured inputs must sit on different points of it")
    for label, v in (("small nbits", SMALL_NBITS), ("large nbits", LARGE_NBITS)):
        if v % 64 == 0:
            bad.append(f"{label} ({v}) is a multiple of 64, so its last word is "
                       f"full; ../spec.md requires both measured inputs to "
                       f"exercise a PARTIAL last word, because `nwords = "
                       f"ceil(nbits/64)` is where the shift derivation is "
                       f"tightest")
    pairs = [("nbits", SMALL_NBITS, LARGE_NBITS, RESIDUE_MODULI),
             ("nq", SMALL_NQ, LARGE_NQ, RESIDUE_MODULI),
             ("nwords", nwords_of(SMALL_NBITS), nwords_of(LARGE_NBITS),
              RESIDUE_MODULI),
             # stride is == 0 (mod 4) by construction (8 + 8*nwords + 4*nq), so
             # asserting mod 4 would assert something the format forbids.
             ("stride", stride_of(SMALL_NBITS, SMALL_NQ),
              stride_of(LARGE_NBITS, LARGE_NQ), (8, 16, 32))]
    for label, a, b, moduli in pairs:
        for m in moduli:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    return bad


def tiled(rng, nwin, nbits, nq, setp, nguard=None):
    """`nwin` windows, identical in *shape* and different in *content*.

    Every window has the same `nbits`, the same `nq` and therefore the same
    `work_per_call`; the words and the query list differ per window, so the
    driver's anti-collapse barrier stays honest and no two windows produce the
    same checksum."""
    if nguard is None:
        nguard = nq
    out = bytearray()
    nw = nwords_of(nbits)
    for _ in range(nwin):
        out += window(nbits, nq, words(rng, nw, setp),
                      queries(rng, nq, nbits, nguard))
    return bytes(out)


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<9d} "
          f"n_blob={len(body):<10d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- adversarial-oob: a bit index far beyond nbits --------------------------
#
# THE SPATIAL BUG. One window, `nbits = 128` (2 words), and one query is
# 0x00FFFFFF. Every checked rung skips it; R1 computes `q >> 6 = 262143` and
# reads `words + 8*262143`, i.e. **2 MiB past a 208-byte allocation**. ASan
# reports `heap-buffer-overflow`. Note what makes this a *spatial* bug and not
# an arithmetic one: the guard is on `q` and the access is on `q >> 6`, so the
# check that is missing is two operators away from the address that is wrong.
OOB_NBITS, OOB_NQ = 128, 20
OOB_Q = 0x00FFFFFF

# ---- adversarial-edge: q == nbits, q == nbits-1, partial last word ----------
#
# THE SILENT ONE, and it is the sharper of the two. `nbits = 100` so `nwords =
# 2` and bits 100..127 are padding inside a word that exists. The query list
# contains 99 (the last real bit), 100 (`== nbits`), 127 (the last padding bit)
# and 128 (one word past). Every checked rung skips all but 99; R1 folds words
# 1, 1, 1 and 2 -- and words 1 and 2 are **inside the same allocation**, because
# the query array follows the word array. So R1 returns a different answer with
# **no diagnostic from any sanitiser**, which is p17's shape arriving on a
# pattern whose other adversarial row does fire. `model.py`'s
# `sanitizer_expect` derives "clean" here rather than tabulating it.
EDGE_NBITS, EDGE_NQ = 100, 24
EDGE_QS = (99, 100, 127, 128)

# ---- adversarial-count: the declared shape the window cannot hold -----------
#
# THE CONTROL. `nq = 4096` against a window holding 20 queries, so
# `8*nwords + 4*nq = 16400 > avail = 96`. The length check is in every rung, so
# every rung returns 0 -- and a 0 checksum is a weak oracle, which is why this
# row is here for the *behaviour* table and the sanitiser row rather than for
# its value: it is the input that would fire ASan in R1 if the missing check
# were the length one, and it does not.
COUNT_NBITS, COUNT_NQ_DECL, COUNT_NQ = 128, 4096, 20

# `--sweep`: three bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix.
#
# **Band N -- the QUERY-COUNT axis, 64 consecutive counts**, at fixed `nbits`
# and 100% guarded. 64 consecutive values is two full cycles of any modulus up
# to 32.
SWEEP_N_NBITS = 512
SWEEP_N_NQ = tuple(range(8, 72))

# **Band D -- the GUARD-TAKEN axis at fixed query count.** Band N moves `nq`
# with the guarded count locked to it, so every per-query constant it yields is
# confounded with the guarded count. Band D moves the guarded count over 13
# values at a fixed 240 queries, which is what separates the per-QUERY term from
# the per-GUARDED-QUERY term (`.memory/01-ladder.md`: separating exactly this
# kind of pair is where p16's `nrec + 3` and p05's "+11.00 flat" both died).
SWEEP_D_NBITS = 512
SWEEP_D_NQ = 240
SWEEP_D_NGUARD = tuple(range(0, 241, 20))

# **Band W -- the WORD-COUNT axis at fixed query count and fixed guarded count.**
# Without it the popcount pass's per-word term is collinear with the intercept
# in every other band and the pooled design is rank 3, not 4. ../NOTES.md 4
# reports the measured rank rather than asserting it.
SWEEP_W_NQ = 120
SWEEP_W_NBITS = tuple(64 * n + 30 for n in range(2, 28, 2))

SWEEP_ITERS = 2000
SWEEP_WINS = 8
SWEEP_SETP = 0.375


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p09 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: nbits {SMALL_NBITS}/{LARGE_NBITS}, nq "
          f"{SMALL_NQ}/{LARGE_NQ}, nwords "
          f"{nwords_of(SMALL_NBITS)}/{nwords_of(LARGE_NBITS)}, strides "
          f"{stride_of(SMALL_NBITS, SMALL_NQ)}/"
          f"{stride_of(LARGE_NBITS, LARGE_NQ)}, bit-set density "
          f"{SMALL_SETP}/{LARGE_SETP}")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_NBITS, SMALL_NQ),
          tiled(rng, SMALL_WINS, SMALL_NBITS, SMALL_NQ, SMALL_SETP))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_NBITS, LARGE_NQ),
          tiled(rng, LARGE_WINS, LARGE_NBITS, LARGE_NQ, LARGE_SETP))

    # ---- adversarial ------------------------------------------------------
    # (1) THE spatial bug: one query 0x00FFFFFF, 2 MiB past the allocation.
    nw = nwords_of(OOB_NBITS)
    qs = queries(rng, OOB_NQ - 1, OOB_NBITS, OOB_NQ - 1)
    qs = [OOB_Q] + qs
    write("adversarial-oob.bin", ADV_ITERS, stride_of(OOB_NBITS, OOB_NQ),
          window(OOB_NBITS, OOB_NQ, words(rng, nw, 0.5), qs))

    # (2) the off-by-one and the partial last word -- silent in every build.
    nw = nwords_of(EDGE_NBITS)
    qs = list(EDGE_QS) + queries(rng, EDGE_NQ - len(EDGE_QS), EDGE_NBITS,
                                 EDGE_NQ - len(EDGE_QS))
    write("adversarial-edge.bin", ADV_ITERS, stride_of(EDGE_NBITS, EDGE_NQ),
          window(EDGE_NBITS, EDGE_NQ, words(rng, nw, 0.5), qs))

    # (3) CONTROL: the length check, which IS in every rung.
    nw = nwords_of(COUNT_NBITS)
    write("adversarial-count.bin", ADV_ITERS, stride_of(COUNT_NBITS, COUNT_NQ),
          window(COUNT_NBITS, COUNT_NQ_DECL, words(rng, nw, 0.5),
                 queries(rng, COUNT_NQ, COUNT_NBITS, COUNT_NQ)))

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for nq in SWEEP_N_NQ:
            write(f"sweep-n{nq:03d}.bin", SWEEP_ITERS,
                  stride_of(SWEEP_N_NBITS, nq),
                  tiled(rng, SWEEP_WINS, SWEEP_N_NBITS, nq, SWEEP_SETP))
        for g in SWEEP_D_NGUARD:
            write(f"sweep-d{g:03d}.bin", SWEEP_ITERS,
                  stride_of(SWEEP_D_NBITS, SWEEP_D_NQ),
                  tiled(rng, SWEEP_WINS, SWEEP_D_NBITS, SWEEP_D_NQ,
                        SWEEP_SETP, nguard=g))
        for nbits in SWEEP_W_NBITS:
            write(f"sweep-w{nwords_of(nbits):03d}.bin", SWEEP_ITERS,
                  stride_of(nbits, SWEEP_W_NQ),
                  tiled(rng, SWEEP_WINS, nbits, SWEEP_W_NQ, SWEEP_SETP))
    return 0


if __name__ == "__main__":
    sys.exit(main())
