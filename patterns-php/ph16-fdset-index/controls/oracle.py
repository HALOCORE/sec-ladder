#!/usr/bin/env python3
"""ph16 -- THE ORACLE: does the corrupted checksum come from the WRITE, or from
something else in the frame?

    python3 patterns-php/ph16-fdset-index/controls/oracle.py

This row's headline is that the defect is witnessed **without a sanitizer and
without scaffolding**: an over-index lands in `PHP_FUNCTION(stream_select)`'s
*other two* `fd_set`s, which the function reads back, so the value it returns
moves. `../NOTES.md` §3.

⚠⚠⚠ **F52 IS THE HAZARD THIS FILE EXISTS FOR: a probe whose setup encodes the
answer evaluates fine and is wrong.** R1 and R1h differ on the adversarial
inputs for TWO reasons, and only one of them is the memory error:

    (i)  the out-of-bounds WRITE lands in a neighbouring `fd_set`;
    (ii) `max_fd` is not clamped, because `99e290f882c9` guard (c)
         (`PHP_SAFE_MAX_FD`) is absent from R1 -- and this row FOLDS `max_fd`.

A control that only said *"R1 != R1h"* would be satisfied by (ii) alone, on a
row whose whole claim is (i). So this file does not compare the two rungs. It
**predicts R1's exact corrupted checksum from the measured stack layout** and
compares that with the binary:

    the three fd_sets are 48 contiguous 64-bit words, `rfds` at word 0, `wfds`
    at 16, `efds` at 32; `FD_SET(d, &X)` writes word `base(X) + d / 64`, in
    range or not; writes landing outside the 48 words are not modelled and are
    counted separately as `escaped`.

If the prediction reproduces the binary's output BIT FOR BIT, there is nothing
left over: the corruption is exactly the write, in exactly the place the layout
says, and no other mechanism is contributing.

⚠ **The layout is gcc's.** Measured (`../NOTES.md` §3): under gcc the three sit
at `+0 / +128 / +256` from `&rfds` and under clang at `+0 / -128 / -256` --
contiguous under both, in OPPOSITE ORDER. `--layout desc` predicts the clang
ordering. Which compiler puts which set lowest is a fact about the frame, not
about PHP, and the row states it rather than assuming one.

CONTROLS (`PROTOCOL_PHP.md` §H):

  must-fire      `--only max-fd-alone` predicts R1 with the write SUPPRESSED
                 and only `max_fd` unclamped. It MUST NOT match the binary. If
                 it did, the corruption would be invisible and the row's oracle
                 would be measuring (ii).
  must-NOT-fire  every BENIGN input: the same prediction machinery, R1 and R1h
                 and the model all agree, and `escaped` is 0. A prediction that
                 "worked" on benign input by luck would show up as a
                 disagreement here.
  must-fire #2   `--only wrong-layout` predicts against the gcc binary using
                 CLANG's measured layout (`efds` lowest). It MUST NOT match --
                 otherwise the prediction is insensitive to the ordering and
                 proves nothing about WHERE the write lands. ⚠ This control is
                 sharper than the obvious "use an impossible layout" one, which
                 collapses to the same number as `max-fd-alone`: with the sets
                 far apart every out-of-range write escapes the folded words,
                 so the two negatives would be one negative twice.

A run that cannot evaluate says so and exits non-zero.
"""

import argparse
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
BUILD = os.path.join(REPO, ".temp", "php-scratch", "build",
                     os.path.basename(ROW).split("-")[0])
MASK = (1 << 64) - 1
NW = 16
FD_SETSIZE = 1024
ENV = {k: v for k, v in os.environ.items() if k != "LD_PRELOAD"}

#: word offsets of rfds / wfds / efds inside the 48-word block, MEASURED.
LAYOUTS = {
    "asc": (0, 16, 32),        # gcc:   rfds lowest
    "desc": (32, 16, 0),       # clang: efds lowest
    "spread": (0, 64, 128),    # a layout no compiler produced -- control
}


def load_model():
    spec = importlib.util.spec_from_file_location("ph16model",
                                                  os.path.join(ROW, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def predict_call(M, win, base, guards, write_oob=True, nblock=48):
    """One kernel call, R1-with-a-layout. `guards` is a subset of 'bc'.

    Returns (u64, escaped-write-count)."""
    ctl, n_r, n_w, n_e, es = M.Model._unpack(win)
    flat = [0] * nblock
    mx = 0
    sets = 0
    escaped = 0
    pos = 0
    for b, n in enumerate((n_r, n_w, n_e)):
        run = es[pos:pos + n]
        pos += n
        if ctl & (1 << b):
            continue                                   # X_array == NULL
        if ctl & (8 << b):
            sets += 0                                  # Z_TYPE_P != IS_ARRAY
            continue
        sets += 1
        for e in run:
            if (e >> 14) == 0 or (e >> 14) == 1:
                continue
            f = e & 0x3FFF
            if ("b" in guards) and f >= FD_SETSIZE:
                pass                                   # PHP_SAFE_FD_SET
            elif write_oob or f < FD_SETSIZE:
                w = base[b] + f // 64
                if 0 <= w < nblock:
                    flat[w] |= 1 << (f % 64)
                else:
                    escaped += 1
            if f > mx:
                mx = f
    if "c" in guards and mx >= FD_SETSIZE:
        mx = FD_SETSIZE - 1                            # PHP_SAFE_MAX_FD
    if sets == 0:
        return 0xFFFFFFFF, escaped
    acc = (0 * 31 + sets) & MASK
    acc = (acc * 31 + mx) & MASK
    for b in range(3):
        h = 0
        for i in range(NW):
            h = (h * 31 + flat[base[b] + i]) & MASK
        acc = (acc * 31 + h) & MASK
    return acc, escaped


def predict_file(M, path, base, guards, write_oob=True, nblock=48):
    m = M.build(path)
    if not m.entered:
        return m.checksum, 0
    tab = [predict_call(M, m.buf[k * m.stride:(k + 1) * m.stride], base,
                        guards, write_oob, nblock) for k in range(m.nwin)]
    acc = 0
    esc = 0
    for _ in range(m.n_iters):
        k = (acc * m.nwin) >> 64
        r, e = tab[k]
        esc += e
        acc = (acc * 31 + r) & MASK
    return acc, esc


def hardened(cell):
    """`c-gcc-O3-isolated` -> `c-gcc-h-O3-isolated`. Written as a function
    because the obvious `replace("c-gcc-", "c-gcc-h-")` is compiler-specific and
    printed the R1 value under an `R1h` label for every clang cell."""
    parts = cell.split("-")
    return "-".join(parts[:2] + ["h"] + parts[2:])


def run_cell(cell, inp):
    p = os.path.join(BUILD, cell)
    if not os.path.exists(p):
        return None, None, f"missing binary {p}"
    r = subprocess.run([p, inp], capture_output=True, text=True, env=ENV,
                       timeout=1800)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layout", choices=sorted(LAYOUTS), default="asc")
    ap.add_argument("--only", choices=("max-fd-alone", "wrong-layout", "main"))
    ap.add_argument("--cell", default="c-gcc-O3-isolated",
                    help="the binary to compare against (gcc lays the three "
                         "fd_sets out ascending; see --layout)")
    args = ap.parse_args()

    if not os.path.isdir(BUILD):
        print(f"CANNOT EVALUATE: no build root at {BUILD} -- run "
              f"`python3 harness-php/gate.py --tool build ph16-fdset-index --all`")
        return 2
    M = load_model()
    ind = os.path.join(ROW, "inputs")
    benign = ["small.bin", "large.bin"]
    adv = ["adversarial-redzone.bin", "adversarial-silent.bin"]
    for f in benign + adv:
        if not os.path.exists(os.path.join(ind, f)):
            print(f"CANNOT EVALUATE: inputs/{f} missing -- run inputs/gen.py")
            return 2

    base = LAYOUTS[args.layout]
    bad = 0

    # ---- must-NOT-fire: the benign corpus -------------------------------
    if args.only in (None, "main"):
        print("== must-NOT-fire: on BENIGN input the prediction, R1, R1h and "
              "the model all agree and nothing escapes")
        for f in benign:
            p = os.path.join(ind, f)
            pred, esc = predict_file(M, p, base, "")
            rc1, so1, _ = run_cell(args.cell, p)
            rc2, so2, _ = run_cell(hardened(args.cell), p)
            want = M.build(p).checksum
            ok = (str(pred) == so1 == so2 == str(want) and esc == 0
                  and rc1 == rc2 == 0)
            print(f"   {f:26s} predicted={pred} R1={so1} R1h={so2} "
                  f"model={want} escaped={esc}  {'PASS' if ok else 'FAIL'}")
            if not ok:
                bad += 1

    # ---- the main claim --------------------------------------------------
    if args.only in (None, "main"):
        print(f"\n== THE CLAIM: R1's corrupted checksum, predicted from the "
              f"'{args.layout}' layout alone")
        for f in adv:
            p = os.path.join(ind, f)
            pred, esc = predict_file(M, p, base, "")
            predh, _ = predict_file(M, p, base, "bc")
            rc1, so1, se1 = run_cell(args.cell, p)
            rc2, so2, _ = run_cell(hardened(args.cell), p)
            hit = (str(pred) == so1)
            print(f"   {f}")
            print(f"      R1  predicted = {pred}")
            print(f"      R1  measured  = {so1}   (exit {rc1})"
                  + (f" stderr={se1[:60]!r}" if se1 else ""))
            print(f"      R1h predicted = {predh}   measured = {so2}")
            print(f"      writes that left the three-fd_set block: {esc}")
            print(f"      {'PASS  the corruption is EXACTLY the write' if hit else 'FAIL  the prediction does not reproduce the binary'}")
            if not hit:
                bad += 1

    # ---- must-fire: max_fd alone must NOT explain it ---------------------
    if args.only in (None, "max-fd-alone"):
        print("\n== must-fire: suppress the WRITE and leave `max_fd` "
              "unclamped -- this must NOT match the binary")
        for f in adv:
            p = os.path.join(ind, f)
            pred_no_write, _ = predict_file(M, p, base, "b")   # guard (b) only
            _, so1, _ = run_cell(args.cell, p)
            ok = str(pred_no_write) != so1
            print(f"   {f:30s} max_fd-only = {pred_no_write}  measured = {so1}"
                  f"  {'PASS (differs)' if ok else 'FAIL -- the row would be measuring max_fd, not the write'}")
            if not ok:
                bad += 1

    # ---- must-fire #2: a layout no compiler produced ---------------------
    if args.only in (None, "wrong-layout"):
        other = "desc" if args.layout == "asc" else "asc"
        print(f"\n== must-fire #2: predict with the OTHER compiler's measured "
              f"layout ('{other}'). This must NOT match.")
        for f in adv:
            p = os.path.join(ind, f)
            pred_w, _ = predict_file(M, p, LAYOUTS[other], "")
            _, so1, _ = run_cell(args.cell, p)
            ok = str(pred_w) != so1
            print(f"   {f:30s} {other}-layout = {pred_w}  measured = {so1}"
                  f"  {'PASS (differs)' if ok else 'FAIL -- the prediction is insensitive to the layout'}")
            if not ok:
                bad += 1

    print("\nRESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
