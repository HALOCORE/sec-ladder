#!/usr/bin/env python3
"""ph64 control -- the three windows `controls/asan_fidelity.sh` drives.

Emitted rather than retyped, from `../inputs/gen.py`'s own layout rules, so the
fidelity probe and the shipped corpus cannot describe different windows."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "inputs"))
import gen  # noqa: E402

CASES = [
    ("trigger-no-reuse", dict(n=8, trigger=4, mode=gen.UNREG_SELF, post=0,
                              reuse=0, wild=False)),
    ("trigger-with-reuse", dict(n=8, trigger=4, mode=gen.UNREG_SELF, post=0,
                                reuse=1, wild=True)),
    ("control-no-free", dict(n=8, trigger=4, mode=gen.UNREG_NONE, post=0,
                             reuse=1, wild=True)),
]

for label, kw in CASES:
    w = gen.adv(552, **kw)
    print(f"{label} {len(w)} {w.hex()}")
