#!/usr/bin/env python3
"""Deterministic input generation for p01-array-sum.

Writes .bin files next to this script (gitignored -- regenerate with
`python3 patterns/p01-array-sum/inputs/gen.py`). Payload layout is fixed by
../spec.md: `u64 win_len`, then the `u64` array.

Everything is derived from FIXED SEED, so two runs on two machines produce
byte-identical files and therefore identical checksums.
"""

import itertools
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "common"))
import slb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 0x5EC1ADDE

# Values are full-range u64. The kernel sums with wrapping arithmetic and has no
# precondition on element values (../spec.md), so there is nothing to keep them
# small for -- and full-range values make sure nobody's "sum cannot overflow"
# assumption survives unnoticed.
def values(n, rng):
    return [rng.getrandbits(64) for _ in range(n)]


# name -> (n_iters, win_len, n_vals, declared_len_override, payload_override)
def cases():
    rng = random.Random(SEED)

    # small: 2000 u64 = 16 000 B, fits a 32 KiB L1d with room to spare.
    #
    # win_len 501, not 500, on purpose. R2's per-call instruction overhead
    # depends on `win_len mod 4` -- LLVM peels a 4-element scalar epilogue when
    # the trip count is a multiple of the vector width -- so it is +29 at
    # residue 0 and +11/+13/+15 at residues 1/2/3. `.memory/01-ladder.md`
    # records that the pilot's write-up quoted a single number from three data
    # points that were all residue 0, and overstated the cost ~2x. `large` uses
    # 4096 (residue 0), so the two canonical inputs straddle residues and the
    # default results table cannot hide the effect. Run `gen.py --sweep` for the
    # full picture.
    small_vals = values(2000, rng)
    yield "small.bin", dict(n_iters=200_000, payload=slb.pack_head_body(501, small_vals))

    # large: 1 500 000 u64 = 12 MB, well past the 1 MiB L2 (and past L3 slice).
    large_vals = values(1_500_000, rng)
    yield "large.bin", dict(n_iters=20_000, payload=slb.pack_head_body(4096, large_vals))

    # --- adversarial: degenerate shapes. p01 models no memory-safety bug (it is
    # the calibration pattern), so its adversarial inputs are the ones that catch
    # a sloppy *driver*: zero iterations, no payload, a length field that lies,
    # a window longer than the array, a zero window.
    adv_vals = values(64, rng)

    # n_iters = 0: the loop must never run and the driver must print 0.
    yield "adversarial.bin", dict(n_iters=0, payload=slb.pack_head_body(8, adv_vals))

    # payload_len = 0: no head word at all.
    yield "adversarial-empty.bin", dict(n_iters=1000, payload=b"")

    # head word present, no values: win_len 8 > n_vals 0.
    yield "adversarial-headonly.bin", dict(n_iters=1000, payload=slb.pack_head_body(8, []))

    # declared payload_len far exceeds the bytes actually in the file. A driver
    # that trusts the field reads 4 KiB of whatever follows.
    yield "adversarial-shortlen.bin", dict(
        n_iters=1000, payload=slb.pack_head_body(4, adv_vals[:4]), declared_len=4096
    )

    # win_len = 2^40: bigger than the array, and bigger than 32 bits, so a
    # driver that truncates to u32 before comparing would sail past the guard.
    yield "adversarial-winbig.bin", dict(n_iters=1000, payload=slb.pack_head_body(1 << 40, adv_vals))

    # win_len = 0: an empty window. `nwin` would be n_vals + 1, so off could
    # equal n_vals -- one past the end.
    yield "adversarial-win0.bin", dict(n_iters=1000, payload=slb.pack_head_body(0, adv_vals))


def sweep_cases(lo=500, hi=516, n_vals=2000, n_iters=2000):
    """`sweep-w<N>.bin`: the same array at every window length in [lo, hi), so
    per-call `Ir` can be plotted against `win_len mod 4`.

    These are diagnostic, not part of the matrix: `harness/check.py` and
    `harness/measure.py` both skip `sweep-*`. They exist because a per-call
    overhead measured at a single window length is not a number, it is a
    coincidence -- see the comment on `small.bin`."""
    rng = random.Random(SEED)
    vals = values(n_vals, rng)
    for w in range(lo, hi):
        yield f"sweep-w{w}.bin", dict(n_iters=n_iters,
                                      payload=slb.pack_head_body(w, vals))


def main():
    gen = itertools.chain(cases(), sweep_cases()) if "--sweep" in sys.argv else cases()
    for name, kw in gen:
        path = os.path.join(HERE, name)
        slb.write(path, kw["n_iters"], kw["payload"], kw.get("declared_len"))
        f = slb.read(path)
        head, body = slb.head_u64_body(f.payload[: f.declared_len])
        print(f"{name:28s} n_iters={f.n_iters:<8} declared_len={f.declared_len:<9} "
              f"present={len(f.payload):<9} win_len={head:<14} v_len={len(body):<8} "
              f"truncated={f.truncated}")


if __name__ == "__main__":
    main()
