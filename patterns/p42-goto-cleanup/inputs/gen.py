#!/usr/bin/env python3
"""Deterministic input generation for p42-goto-cleanup.

Writes .bin files next to this script (gitignored -- regenerate with
`python3 patterns/p42-goto-cleanup/inputs/gen.py`). Payload layout is fixed by
../spec.md: `u64 win_len`, then the `u64` array.

Everything is derived from FIXED SEED, so two runs on two machines produce
byte-identical files and therefore identical checksums.

WHAT THIS GENERATOR HAS TO GET RIGHT, and why each is an assertion here rather
than a hope:

1. **Every window of a MEASURED input must be well formed.** `off` is
   data-derived and ranges over the whole array, so "the tag is right" has to
   hold of EVERY word, not of word 0. If one word had a wrong tag the C rung
   would leak on `small.bin` -- the gate would fail it as an input declared
   clean, and, worse, the measured cells would be timing a leaking program.
   `_check_all_tagged` asserts it.

2. **The error path must actually be REACHED on the inputs that declare it.**
   ../spec.md pins this as a `forbidden` entry ("an error path no committed
   input reaches"); `p31` died on exactly that shape. Here it is checked by
   simulation: `_paths` replays the driver loop through `model.py` and reports
   (ok, err) counts, and the writer asserts the count the case declares.

3. ⚠ **`adversarial-mixed.bin` must reach BOTH paths, and getting that wrong is
   easy.** The error path returns 0, so if the FIRST window is malformed `acc`
   never leaves 0, `off` never leaves 0, and every subsequent call reads the
   same malformed word: a "mixed" input that is in fact all-error, and a control
   with one point instead of many. Word 0 is therefore forced well-formed, and
   `_paths` asserts both counts are non-zero. (TASK_104 hit this in its own gate
   probe before the pattern existed -- ../NOTES.md 2.)

4. **The digest must depend on the payload.** The kernel folds
   `(uint8_t)(run >> 24)`, and `run` is a wrapping sum, so a byte of it can only
   depend on the input bits BELOW it -- had the digest kept `(uint8_t)run`, and
   the tag lived in the low byte, every digest byte would be a constant and the
   checksum would not read the data at all. `_check_data_dependent` builds a
   second payload of the same shape with a different seed and asserts the
   checksums differ.
"""

import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common"))
sys.path.insert(0, os.path.join(HERE, ".."))
import slb  # noqa: E402

SEED = 0x5EC1ADDE
TAG = 0xA7          # ../spec.md: the low byte of a well-formed record header
MAXWIN = 65536      # ../spec.md: the driver's ceiling on the window length

# The two measured inputs. `small` sits in L1 and `large` past L2, the way every
# pattern's pair does. The window lengths straddle a residue class on purpose:
# 97 is 1 mod 4 and 4096 is 0 mod 4, so a per-call cost that depends on
# `win_len mod 4` (LLVM's peeled scalar epilogue -- `.memory/01-ladder.md`)
# cannot hide behind a pair of inputs that are both 0 mod 4. That is the
# residue-class trap, which this project has now been caught by three times
# (p38, p46, p23).
SMALL_VALS, SMALL_WIN, SMALL_ITERS = 4096, 97, 60_000        # 32 KiB payload
LARGE_VALS, LARGE_WIN, LARGE_ITERS = 1_000_000, 4096, 1_500  # 8 MB payload


def tagged(n, rng):
    """`n` well-formed record words: random in every bit except the low byte,
    which carries the tag. The kernel's digest reads `run >> 24`, so the bits
    that vary are the ones the checksum depends on."""
    return [(rng.getrandbits(64) & ~0xFF) | TAG for _ in range(n)]


def untagged(n, rng, bad):
    """`n` words of which the first is well formed and the rest are malformed
    with probability `bad`. A malformed word gets a low byte that is not TAG."""
    out = [(rng.getrandbits(64) & ~0xFF) | TAG]
    for _ in range(n - 1):
        w = rng.getrandbits(64) & ~0xFF
        out.append(w | (0x11 if rng.random() < bad else TAG))
    return out


def _check_all_tagged(name, vals):
    bad = [i for i, w in enumerate(vals) if (w & 0xFF) != TAG]
    assert not bad, (f"{name}: {len(bad)} malformed words (first at {bad[0]}) in "
                     f"an input that must never reach the error path")


def _paths(path):
    """(ok, err) kernel calls, by replaying the driver loop through model.py --
    the same code the gate drives, so this cannot drift from it."""
    import model
    m = model.build(path)
    return m.n_ok, m.n_err


def _check_data_dependent():
    """The checksum must read the payload. Two payloads of the same SHAPE and
    different contents must not agree."""
    a = os.path.join(HERE, ".datadep-a.bin")
    b = os.path.join(HERE, ".datadep-b.bin")
    import model
    outs = []
    for p, seed in ((a, 1), (b, 2)):
        rng = random.Random(seed)
        slb.write(p, 200, slb.pack_head_body(17, tagged(128, rng)))
        outs.append(model.build(p).checksum)
    for p in (a, b):
        os.remove(p)
    assert outs[0] != outs[1], (
        f"the checksum does not depend on the payload: {outs[0]} twice. The "
        f"digest byte is taken from a bit position no input bit reaches.")
    return outs


# name -> (n_iters, win_len, vals, declared_len_override, want_err)
def cases():
    rng = random.Random(SEED)

    small = tagged(SMALL_VALS, rng)
    _check_all_tagged("small.bin", small)
    yield "small.bin", dict(n_iters=SMALL_ITERS,
                            payload=slb.pack_head_body(SMALL_WIN, small),
                            want=("all_ok",))

    large = tagged(LARGE_VALS, rng)
    _check_all_tagged("large.bin", large)
    yield "large.bin", dict(n_iters=LARGE_ITERS,
                            payload=slb.pack_head_body(LARGE_WIN, large),
                            want=("all_ok",))

    # --- adversarial group 1: inputs that REACH THE ERROR PATH. These are the
    # rows `sanitizer_expect` computes to "fires", and they are the pattern's
    # subject. n_iters is small so that the leak is a few hundred bytes rather
    # than a memory-exhaustion test: what is being demonstrated is that the
    # block is never released, not how much of it there is.
    adv = [(rng.getrandbits(64) & ~0xFF) | 0x11 for _ in range(256)]
    yield "adversarial-notag.bin", dict(
        n_iters=8, payload=slb.pack_head_body(32, adv), want=("all_err",))

    # BOTH paths, in one trace. See the module docstring, point 3.
    mixed = untagged(512, rng, 0.5)
    yield "adversarial-mixed.bin", dict(
        n_iters=64, payload=slb.pack_head_body(24, mixed), want=("both",))

    # win_len 1: the smallest allocation this kernel can make is one byte, and
    # a one-byte block is the least visible thing a leak detector could be asked
    # to see. If LeakSanitizer reports this row, size is not a variable.
    one = [(rng.getrandbits(64) & ~0xFF) | 0x11 for _ in range(64)]
    yield "adversarial-win1.bin", dict(
        n_iters=16, payload=slb.pack_head_body(1, one), want=("all_err",))

    # The driver's MAXWIN ceiling, ISOLATED: a window larger than the cap but
    # SMALLER than the array, so `win_len_w <= n_vals` passes and only the cap
    # rejects it. Without this input the cap conjunct would be untested -- every
    # other over-long window fails `<= n_vals` first, and a conjunct nothing
    # reaches is a conjunct nobody would notice being deleted.
    cap = tagged(200_000, rng)
    _check_all_tagged("adversarial-wincap.bin", cap)
    yield "adversarial-wincap.bin", dict(
        n_iters=100, payload=slb.pack_head_body(MAXWIN + 1, cap),
        want=("no_calls",))

    # --- adversarial group 2: degenerate SHAPES, which attack the driver rather
    # than the kernel and make zero kernel calls. Same set as p01's, because the
    # driver is p01's. Each must be clean: no calls, no allocation, no leak.
    deg = tagged(64, rng)
    yield "adversarial.bin", dict(n_iters=0, payload=slb.pack_head_body(8, deg),
                                 want=("no_calls",))
    yield "adversarial-empty.bin", dict(n_iters=1000, payload=b"",
                                        want=("no_calls",))
    yield "adversarial-headonly.bin", dict(
        n_iters=1000, payload=slb.pack_head_body(8, []), want=("no_calls",))
    yield "adversarial-shortlen.bin", dict(
        n_iters=1000, payload=slb.pack_head_body(4, deg[:4]), declared_len=4096,
        want=("no_calls",))
    yield "adversarial-winbig.bin", dict(
        n_iters=1000, payload=slb.pack_head_body(1 << 40, deg),
        want=("no_calls",))
    yield "adversarial-win0.bin", dict(
        n_iters=1000, payload=slb.pack_head_body(0, deg), want=("no_calls",))


def sweep_cases(rng=None):
    """`sweep-w<N>.bin`: the same 4096-word array at sixteen window lengths in
    each of TWO widely separated bands.

    These are DIAGNOSTIC, not part of the matrix -- `harness/check.py` and
    `harness/measure.py` both skip `sweep-*`.  They exist for one reason, and it
    is `.tasks/PROTOCOL.md`'s newest lesson: **a law owes an OUT-OF-BAND
    prediction, not a within-band holdout.**  `p23` produced three mutually
    inconsistent "exact" laws each with zero in-sample residual, and the
    published one mispredicted its own two shipped inputs.  Two bands 448 apart,
    each covering all four residues mod 4, let a fit on band A be tested against
    band B and against `small.bin`'s own window length, which sits between them.

    Every window is well formed (the whole array is tagged), so every sweep call
    takes the SUCCESS path -- the sweep measures the scratch, not the leak."""
    rng = rng or random.Random(SEED + 1)
    vals = tagged(4096, rng)
    _check_all_tagged("sweep", vals)
    for lo in (64, 512):
        for w in range(lo, lo + 16):
            yield f"sweep-w{w}.bin", dict(n_iters=2000,
                                          payload=slb.pack_head_body(w, vals),
                                          want=("all_ok",))


def main():
    dep = _check_data_dependent()
    print(f"data-dependence control: two payloads, same shape -> "
          f"{dep[0]} != {dep[1]}  OK")
    gen = itertools.chain(cases(), sweep_cases()) if "--sweep" in sys.argv else cases()
    for name, kw in gen:
        path = os.path.join(HERE, name)
        slb.write(path, kw["n_iters"], kw["payload"], kw.get("declared_len"))
        f = slb.read(path)
        head, body = slb.head_u64_body(f.payload[: f.declared_len])
        ok, err = _paths(path)
        want = kw["want"][0]
        if want == "all_ok":
            assert err == 0 and ok > 0, f"{name}: want all-ok, got ok={ok} err={err}"
        elif want == "all_err":
            assert ok == 0 and err > 0, f"{name}: want all-err, got ok={ok} err={err}"
        elif want == "both":
            assert ok > 0 and err > 0, (
                f"{name}: want BOTH paths, got ok={ok} err={err}. See the "
                f"module docstring, point 3.")
        elif want == "no_calls":
            assert ok == 0 and err == 0, f"{name}: want no calls, got ok={ok} err={err}"
        print(f"{name:28s} n_iters={f.n_iters:<8} declared_len={f.declared_len:<9} "
              f"present={len(f.payload):<9} win_len={head:<14} v_len={len(body):<8} "
              f"calls_ok={ok:<7} calls_err={err:<7} truncated={f.truncated}")


if __name__ == "__main__":
    main()
