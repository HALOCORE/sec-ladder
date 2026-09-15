#!/usr/bin/env python3
"""TASK_PHP_058 -- DO THE `inside_share.py` ARMS ACTUALLY FIRE?

    python3 .tasks-php/php58_mutate_arms.py

`PROTOCOL_PHP.md` §H: *"a gate run EXERCISES a validator on the rows that pass.
It does not ATTACK it."* The seven arms inside `controls/inside_share.py` are
self-reported: they print `ok` because the control's own decision functions
agree with the expectations written beside them. That is worth nothing until
somebody breaks the decision functions and checks the arms notice.

This loads the SHIPPED module from one row -- not a copy -- mutates one
decision at a time, and re-runs `arms()`. Every mutation must be caught by at
least one arm, and the LAST case is a must-NOT-fire: an unmutated module must
score 7 of 7, or the battery is measuring nothing.
"""
import importlib.util
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROW = os.path.join(REPO, "patterns-php", "ph29-recvfrom-alloc")
SRC = os.path.join(ROW, "controls", "inside_share.py")


def load():
    spec = importlib.util.spec_from_file_location("ishare_under_test", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def score(mod):
    a = mod.arms()
    return [name for name, _, ok, _ in a if not ok], len(a)


CASES = []


def case(name, mutate, must_fire):
    CASES.append((name, mutate, must_fire))


case("loose `kernel` regex -- `kernel_hardened` would be counted",
     lambda m: setattr(m, "_KERNEL", re.compile("kernel")), True)
case("kernel row parser always returns 0 instead of None",
     lambda m: setattr(m, "kernel_ir", lambda ann: 0), True)
case("missing-binary check always says nothing is missing",
     lambda m: setattr(m, "missing_binaries", lambda b, c: []), True)
case("pin check always says the pin is clean",
     lambda m: setattr(m, "pin_problems", lambda b, p, w: []), True)
case("pin asked for a path this row does not have",
     lambda m: setattr(m, "PINNED", m.PINNED + ["c/not_a_file.c"]), True)
case("NO MUTATION (must-NOT-fire)", lambda m: None, False)


def main():
    bad = []
    for name, mutate, must_fire in CASES:
        mod = load()
        mutate(mod)
        failed, n = score(mod)
        fired = bool(failed)
        verdict = "CAUGHT" if fired else "not caught"
        if fired != must_fire:
            bad.append(name)
            verdict = "*** WRONG ***  " + verdict
        print(f"  {verdict:14s} {name}")
        print(f"                 arms failing: {failed or 'none'} (of {n})")
    print()
    if bad:
        print(f"BATTERY FAILED on {len(bad)} case(s): {bad}")
        return 1
    print(f"all {len(CASES)} cases behaved as expected "
          f"({sum(1 for c in CASES if c[2])} must-fire, "
          f"{sum(1 for c in CASES if not c[2])} must-NOT-fire)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
