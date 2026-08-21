#!/usr/bin/env python3
"""p10's DOMAIN band: blobs whose calls are REJECTED, which no measured input is.

    python3 patterns/p10-fir-stencil/controls/gen_domain.py
    python3 patterns/p10-fir-stencil/controls/sweep_ir.py --band d --cells all \
        --inputs .temp/p10/domain --json .temp/p10/sweep_d.json

**Why this exists.** TASK_057 fitted five exact laws over bands `r`, `o`, `h`
and `e` and published them without a domain. TASK_057_REVIEW (M4) found that
every one of them breaks on a blob containing a window with `taps > n`, with
residuals exactly linear in the rejected-call fraction, and that a SIXTH
parameter sits behind the fifth: *which* guard rejected. `.memory/03-measurement.md`
says that is a MISSING COLUMN and not a caveat -- so the columns are in
`sweep_ir.shape()` (`rejwin`, `rejfar`, `fence`) and these are the blobs that
turn them on. The shapes are the reviewer's (`.temp/p10rev/gen_attack.py`),
re-derived here so they survive a `.temp/` sweep.

Every blob reuses `inputs/gen.py`'s own `window` / `emit` / `kern`, so the wire
format is the shipped one by construction and this file only chooses shapes.

**The absorbing state is the design, not an accident.** The driver picks
`k = (acc * nwin) >> 64` and `acc` starts at 0, so if window 0 returns 0 then
`k` stays 0 forever and every call hits window 0. `inputs/gen.py`'s `audit`
refuses that for a measured input (p17's trap). Here it is the instrument: it
is what makes a 100 %-rejecting blob possible at all.

⚠ **And on a `fence` blob the two C cells and the other six DIVERGE**, because
c-gcc/c-clang accept the call, so their `acc` moves and they visit a different
window sequence from the model's. Every `fence` blob here is therefore
window-HOMOGENEOUS -- every window the same shape -- so the regressors are the
same whichever sequence a cell walks. No `R1h - R1` law is fitted on them
either way: `.memory/02-bench-rules.md`'s first rule forbids costing a pair
where the unhardened rung commits UB, and `fence` is exactly where it does.
"""
import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "common"))

_spec = importlib.util.spec_from_file_location(
    "p10gen", os.path.join(PDIR, "inputs", "gen.py"))
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

N_ITERS = 8000


def tiled_shapes(shapes, seed0, pad=0):
    """Windows of DIFFERENT shapes, padded to a common stride.

    `pad` widens the stride past the longest window, which is how an ACCEPTING
    window is built beside a `rejfar` one: `last < stride` for the long window
    and `last > stride` only for the one that declares more samples than it
    carries."""
    stride = max(8 + 2 * r + 1 + n for n, r in shapes) + pad
    body = b""
    for n, r in shapes:
        w = gen.window(n, r, seed0 + 7919 * len(body))
        body += w[:stride] + b"\x00" * max(0, stride - len(w))
    return body, stride


def over(n, r, seed, stride):
    """One window that DECLARES `n` samples and is truncated to `stride` bytes,
    so `last = 8 + taps + n - 1` lands beyond the window: `rejfar` when it is
    strictly past, `fence` when it is exactly at."""
    w = gen.window(n, r, seed)
    return w[:stride] + b"\x00" * max(0, stride - len(w))


# name -> (body, stride, what it turns on)
def blobs():
    out = []

    # --- 100 % of one rejection kind each. These are the rows that PRICE a
    #     rejected call directly; the mixed ones below are what tests that the
    #     price is linear in the fraction.
    # rejwin: taps 17 against n = 3, so `n < taps` fires first.
    body, stride = tiled_shapes([(3, 8)] * 4, 999)
    out.append(("d-allwin", body, stride, "rejwin"))

    # rejfar: n = 40, r = 4 -> last = 8+9+40-1 = 56, stride 50. `last > len`.
    # Both C cells reject too, so this row is IN the R1h-R1 domain.
    body = b"".join(over(40, 4, 555 + 7919 * k, 50) for k in range(4))
    out.append(("d-allfar", body, 50, "rejfar"))

    # fence: the same window at stride 56 -> `last == len` EXACTLY. c/kernel.c
    # accepts and reads one byte past; every other cell rejects.
    body = b"".join(over(40, 4, 555 + 7919 * k, 56) for k in range(4))
    out.append(("d-allfp", body, 56, "fence"))

    # --- mixed: window 0 must ACCEPT or the absorbing state pins every call to
    #     it. These give intermediate rejected-call fractions, which is what
    #     makes "the residual is linear in the fraction" a measurement.
    body, stride = tiled_shapes([(32, 4), (3, 8), (32, 6), (4, 9)], 12345)
    out.append(("d-mixwin1", body, stride, "rejwin, ~1/2"))

    body, stride = tiled_shapes([(32, 4), (2, 12), (5, 20), (32, 5),
                                 (3, 30), (32, 7), (1, 9), (32, 3)], 12345)
    out.append(("d-mixwin2", body, stride, "rejwin, ~1/2"))

    body, stride = tiled_shapes([(32, 1), (32, 9), (2, 11), (48, 3),
                                 (64, 16), (32, 0)], 12345)
    out.append(("d-mixwin3", body, stride, "rejwin, ~1/6, across the novec edge"))

    # mixed rejfar: an accepting window of the SAME stride beside truncated
    # ones. stride 60 > 8+9+40-1 = 56, so the full window accepts; the
    # truncated ones declare n = 60 -> last = 76 > 60.
    body = (over(40, 4, 61001, 60) + over(60, 4, 61003, 60)
            + over(40, 4, 61005, 60) + over(60, 4, 61007, 60))
    out.append(("d-mixfar", body, 60, "rejfar, 1/2"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(REPO, ".temp", "p10", "domain"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for name, body, stride, what in blobs():
        p = os.path.join(a.out, name + ".bin")
        gen.emit(p, N_ITERS, body, stride)
        nwin = len(body) // stride
        vals = [gen.kern(body, k * stride, stride) for k in range(nwin)]
        nrej = sum(1 for v in vals if v == 0)
        print(f"{name:12s} stride={stride:4d} nwin={nwin:2d} "
              f"rejected {nrej}/{nwin}  win0={'ACCEPT' if vals[0] else 'REJECT'} "
              f"  turns on: {what}")
    print(f"wrote {len(blobs())} blob(s) to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
