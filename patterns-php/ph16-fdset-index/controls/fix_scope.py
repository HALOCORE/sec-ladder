#!/usr/bin/env python3
"""ph16 -- what each of `99e290f882c9`'s THREE POSIX guards actually buys,
measured rather than argued.

    python3 patterns-php/ph16-fdset-index/controls/fix_scope.py

`PROTOCOL_PHP.md` §C: *"An upstream fix is not automatically correct ... That is
a result, and one of the strongest a row can carry."* This file is where that
gets numbers instead of a sentence, and it is also where the two things the gate
cannot hold live:

  * `check.py` stage 7h requires R1h to be clean on every input AND
    byte-identical to R1 on every non-adversarial one, so a corpus on which any
    guard FIRES cannot be shipped in `inputs/`;
  * `inputs/` is six files. Q1 and Q2 range over the whole 14-bit index domain
    crossed with every tag and every `ctl`.

THE THREE GUARDS, all from `main/php_network.h`'s POSIX arm as the commit adds
them (`controls/99e290f882c9.patch`):

    (a)  `&& this_fd >= 0`                    at streamsfuncs.c:540
    (b)  `PHP_SAFE_FD_SET`'s `fd < FD_SETSIZE` at :541      <- the memory-safety half
    (c)  `PHP_SAFE_MAX_FD`'s clamp of `max_fd` in the CALLER

FOUR QUESTIONS:

  Q1  on the SHIPPED BENIGN CORPUS, how many times does each guard fire?
      (must be 0,0,0 -- that is what "benign" means here and what stage 7h
      requires)
  Q2  over the whole index domain, how many out-of-bounds writes does each
      guard remove, and how many values of `max_fd` does each clamp?
  Q3  ⚠ IS GUARD (a) DEAD? `this_fd` is `PH16_IDX(e)`, a 14-bit field, so it
      cannot be negative. Reported as a count over the domain and NOT argued.
  Q4  ⚠⚠ WHICH GUARD MOVES THE ANSWER, AND IT IS NOT ONLY (b). This row folds
      `max_fd`, so (c) changes the returned `u64` on inputs where (b) already
      stopped the write. The four configurations are priced apart, because a
      row that reported "R1 != R1h" and left it there would be attributing (c)'s
      effect to the memory error -- F52's shape exactly.

CONTROLS (`PROTOCOL_PHP.md` §H):

  must-NOT-fire  Q1 on `small.bin` and `large.bin`: all three guards dead.
  must-fire      Q2: guard (b) must remove EVERY out-of-range write and guard
                 (c) must clamp every `max_fd` that needs it -- i.e. the fix is
                 COMPLETE, which is what licenses R2-R5 implementing R1h's
                 function rather than a further one (unlike ph03).
  must-fire #2   an INCOMPLETE variant, `b_too_wide`, which guards
                 `fd < 2 * FD_SETSIZE` instead of `fd < FD_SETSIZE`. It must
                 leave a RESIDUE. If it did not, Q2's completeness verdict
                 would not be measuring completeness. ⚠ THE FIRST DRAFT USED
                 `fd < 512`, WHICH IS THE WRONG DIRECTION: a STRICTER bound
                 cannot leave a residue, so the control reported FAIL and was
                 right to. The incomplete variant of a bound is a WIDER one.
  must-NOT-fire  a variant with guard (b) alone must still leave `max_fd`
                 unclamped, i.e. (b) must NOT accidentally do (c)'s job.

A run that cannot evaluate says so and exits non-zero.
"""

import argparse
import importlib.util
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
FD_SETSIZE = 1024
NW = 16
MASK = (1 << 64) - 1


def load_model():
    spec = importlib.util.spec_from_file_location("ph16model",
                                                  os.path.join(ROW, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def arm(entries, guards, fds, mx, bound=FD_SETSIZE):
    """One `stream_array_to_fd_set` call under a chosen guard set.

    Returns (fds, max_fd, n_oob_writes, n_a_fired, n_b_fired)."""
    oob = a_fired = b_fired = 0
    for e in entries:
        if (e >> 14) == 0 or (e >> 14) == 1:
            continue
        f = e & 0x3FFF
        if "a" in guards and f < 0:            # cannot happen: 14-bit field
            a_fired += 1
            continue
        if "b" in guards and not (f < bound):
            b_fired += 1
        else:
            w = f // 64
            if w >= NW:
                oob += 1
            else:
                fds[w] |= 1 << (f % 64)
        if f > mx:
            mx = f
    return fds, mx, oob, a_fired, b_fired


def call(M, win, guards, bound=FD_SETSIZE):
    ctl, n_r, n_w, n_e, es = M.Model._unpack(win)
    sets = 0
    mx = 0
    oob = a_f = b_f = 0
    folded = []
    pos = 0
    for b, n in enumerate((n_r, n_w, n_e)):
        run = es[pos:pos + n]
        pos += n
        fds = [0] * NW
        if not (ctl & (1 << b)) and not (ctl & (8 << b)):
            sets += 1
            fds, mx, o, a, bb = arm(run, guards, fds, mx, bound)
            oob += o
            a_f += a
            b_f += bb
        folded.append(fds)
    c_fired = 1 if mx >= FD_SETSIZE else 0
    if "c" in guards and mx >= FD_SETSIZE:
        mx = FD_SETSIZE - 1
    if sets == 0:
        return 0xFFFFFFFF, oob, a_f, b_f, c_fired
    acc = (0 * 31 + sets) & MASK
    acc = (acc * 31 + mx) & MASK
    for fds in folded:
        h = 0
        for v in fds:
            h = (h * 31 + v) & MASK
        acc = (acc * 31 + h) & MASK
    return acc, oob, a_f, b_f, c_fired


def domain_windows():
    """A domain `inputs/` cannot carry: every tag x a spread of indices that
    straddles FD_SETSIZE, crossed with a spread of `ctl`."""
    idxs = (0, 1, 511, 512, 1022, 1023, 1024, 1025, 1279, 1280, 2047, 2048,
            3071, 3072, 8191, 16383)
    stride = 6 + 2 * 12
    for ctl in (0, 1, 8, 2 | 16, 7, 56):
        for combo in itertools.product(idxs, repeat=2):
            es = []
            for k in range(12):
                tag = (k % 4)
                es.append(((tag if tag >= 2 else tag) << 14)
                          | combo[k % 2])
            yield (bytes((ctl & 0xFF, ctl >> 8, 4, 0, 4, 0))
                   + b"".join(bytes((e & 0xFF, e >> 8)) for e in es))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    M = load_model()
    ind = os.path.join(ROW, "inputs")
    bad = 0

    # ---- Q1: the shipped benign corpus -----------------------------------
    print("== Q1  the three guards on the SHIPPED BENIGN corpus "
          "(must-NOT-fire: 0, 0, 0)")
    for name in ("small.bin", "large.bin"):
        p = os.path.join(ind, name)
        if not os.path.exists(p):
            print(f"CANNOT EVALUATE: {p} missing -- run inputs/gen.py")
            return 2
        m = M.build(p)
        a = b = c = calls = 0
        for k in range(m.nwin):
            win = m.buf[k * m.stride:(k + 1) * m.stride]
            _, _, af, bf, cf = call(M, win, "abc")
            a += af
            b += bf
            c += cf
            calls += 1
        okd = (a, b, c) == (0, 0, 0)
        print(f"   {name:12s} windows={calls:<5d} (a) fired {a}, (b) fired {b}, "
              f"(c) fired {c}  {'PASS' if okd else 'FAIL'}")
        if not okd:
            bad += 1

    # ---- Q2/Q3/Q4: the synthetic domain ----------------------------------
    wins = list(domain_windows())
    print(f"\n== Q2/Q3/Q4  over {len(wins)} synthetic windows "
          f"(every tag x 16 indices straddling FD_SETSIZE x 6 ctl values)")
    stats = {}
    for label, guards, bound in (("R1        (no guards)", "", FD_SETSIZE),
                                 ("R1 + (a)", "a", FD_SETSIZE),
                                 ("R1 + (b)", "b", FD_SETSIZE),
                                 ("R1 + (c)", "c", FD_SETSIZE),
                                 ("R1h (a+b+c)", "abc", FD_SETSIZE),
                                 ("b_too_wide (fd < 2048)", "b", 2 * FD_SETSIZE)):
        oob = a_f = b_f = c_f = 0
        vals = []
        for w in wins:
            v, o, a, bb, cc = call(M, w, guards, bound)
            oob += o
            a_f += a
            b_f += bb
            c_f += cc
            vals.append(v)
        stats[label] = (oob, a_f, b_f, c_f, vals)
        print(f"   {label:22s} out-of-bounds writes = {oob:<7d} "
              f"(a) fired {a_f:<5d} (b) fired {b_f:<6d} "
              f"max_fd out of range on {c_f} windows")

    r1_oob = stats["R1        (no guards)"][0]
    b_oob = stats["R1 + (b)"][0]
    low_oob = stats["b_too_wide (fd < 2048)"][0]
    a_fired = stats["R1 + (a)"][1]

    print("\n== the verdicts")
    okd = r1_oob > 0 and b_oob == 0
    print(f"   must-fire      guard (b) removes {r1_oob - b_oob} of {r1_oob} "
          f"out-of-bounds writes, leaving {b_oob}  "
          f"{'PASS -- the fix is COMPLETE' if okd else 'FAIL'}")
    bad += 0 if okd else 1

    okd = low_oob > 0
    print(f"   must-fire #2   an INCOMPLETE variant (fd < 2048) leaves "
          f"{low_oob} -- {'PASS, so Q2 is measuring completeness' if okd else 'FAIL'}")
    bad += 0 if okd else 1

    print(f"   Q3  guard (a) fired {a_fired} times over the whole domain. "
          f"{'⭐ IT IS DEAD: `this_fd` is a 14-bit field and cannot be negative. It is carried because it is the shipped POSIX configuration, and this is the measurement rather than the argument.' if a_fired == 0 else '⚠ IT IS NOT DEAD and NOTES.md must say so.'}")

    # Q4: does (b) alone do (c)'s job? It must NOT.
    v_b = stats["R1 + (b)"][4]
    v_abc = stats["R1h (a+b+c)"][4]
    v_r1 = stats["R1        (no guards)"][4]
    n_bc = sum(1 for x, y in zip(v_b, v_abc) if x != y)
    n_1b = sum(1 for x, y in zip(v_r1, v_b) if x != y)
    print(f"   must-NOT-fire  (b) alone still differs from (a+b+c) on {n_bc} "
          f"of {len(wins)} windows -- {'PASS, so (c) does its own work and (b) does not do it for free' if n_bc > 0 else 'FAIL'}")
    bad += 0 if n_bc > 0 else 1
    print(f"   Q4  R1 vs R1+(b) differ on {n_1b} windows and R1+(b) vs R1h "
          f"on {n_bc} (the max_fd CLAMP).")
    print(f"   ⚠⚠ THE {n_1b} IS NOT A MEASUREMENT OF THE WRITE AND MUST NOT BE "
          f"READ AS ONE. This file models each `fd_set` as its own 16-word "
          f"list, so an out-of-range write lands NOWHERE and cannot move the "
          f"fold -- it is counted in the `out-of-bounds writes` column instead. "
          f"What the write does to the VALUE needs a model of the FRAME, "
          f"because the write lands in the NEXT fd_set; that is "
          f"controls/oracle.py, which predicts R1's corrupted checksum from "
          f"the measured layout and reproduces the binary exactly. ⭐ So the "
          f"honest split is: (b) removes {r1_oob - b_oob} illegal WRITES "
          f"(this file), those writes move the returned u64 (oracle.py), and "
          f"(c) independently moves it on {n_bc} windows by clamping max_fd "
          f"(this file).")

    print("\nRESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
