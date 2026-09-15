#!/usr/bin/env python3
"""§1.4's CHEAP DISCRIMINATOR, written from scratch for TASK_PHP_059.

`F74`'s share exceeds 1.0 on 15 of 360 cells.  The candidate mechanism is that
the numerator is measured over `n_iters` calls while the denominator is a slope
taken at `collapse.probe_iters` = [100, 200].  ▶ **Recompute the marginal at
`n_iters` scale on an offending cell.**  If the share falls under 1.0 the slope
explanation survives; if it does not, it is something else.

    python3 .tasks-php/php59_marginal_at_n.py ph16 c-gcc-O3-isolated small.bin 24000 25000

Probe inputs are made the way `harness/check.py::_probe_input` makes them --
the same bytes with the leading `<Q` n_iters rewritten -- re-implemented here in
three lines rather than imported, so this is a second method and not a re-run.
"""
import os
import re
import struct
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VG = os.path.expanduser("~/tools/valgrind/bin/valgrind")
SCRATCH = os.path.join(REPO, ".temp", "rev059", "cg")
_SUM = re.compile(r"^summary:\s+([\d ]+)$", re.M)
_FN = re.compile(r"^fn=\(\d+\)(?:\s+(.*))?$")


def probe(src, n, out):
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "wb").write(struct.pack("<Q", n) + blob[8:])
    return out


def run(binary, inp, tag):
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, "callgrind.out." + tag)
    if os.path.exists(out):
        os.remove(out)
    subprocess.run([VG, "--tool=callgrind", "--callgrind-out-file=" + out,
                    binary, inp], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    txt = open(out, encoding="utf-8", errors="replace").read()
    total = int(_SUM.search(txt).group(1).replace(" ", ""))
    # exclusive Ir of every fn whose name contains `kernel` but not
    # `kernel_hardened` -- self cost lines only, i.e. the lines that follow an
    # `fn=` and are not inside a `cfn=`/`calls=` block.
    excl, cur, in_call = {}, None, False
    for ln in txt.split("\n"):
        m = _FN.match(ln)
        if m:
            cur, in_call = (m.group(1) or cur), False
            continue
        if ln.startswith(("cfn=", "cfi=", "calls=")):
            in_call = ln.startswith("calls=")
            continue
        if ln[:1].isdigit() or ln.startswith(("+", "-", "*")):
            if in_call:
                in_call = False
                continue
            parts = ln.split()
            if len(parts) >= 2 and cur:
                try:
                    excl[cur] = excl.get(cur, 0) + int(parts[1])
                except ValueError:
                    pass
    kern = sum(v for k, v in excl.items()
               if re.search(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])", k))
    return total, kern


def main(a):
    row, cell, inp, n1, n2 = a[0], a[1], a[2], int(a[3]), int(a[4])
    rowdir = [d for d in os.listdir(os.path.join(REPO, "patterns-php"))
              if d.startswith(row + "-")][0]
    binary = os.path.join(REPO, ".temp", "php-scratch", "build", row, cell)
    src = os.path.join(REPO, "patterns-php", rowdir, "inputs", inp)
    res = {}
    for n in (n1, n2):
        p = probe(src, n, os.path.join(SCRATCH, f"{row}.{inp}.{n}.bin"))
        res[n] = run(binary, p, f"{row}.{cell}.{n}")
        print(f"  n_iters={n:7d}  whole-run Ir={res[n][0]:14,d}  "
              f"kernel exclusive Ir={res[n][1]:14,d}")
    dtot = res[n2][0] - res[n1][0]
    dkern = res[n2][1] - res[n1][1]
    print(f"\n  marginal WHOLE-PROGRAM Ir/call over [{n1}, {n2}] = "
          f"{dtot / (n2 - n1):.2f}")
    print(f"  marginal KERNEL-EXCLUSIVE Ir/call over [{n1}, {n2}] = "
          f"{dkern / (n2 - n1):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
