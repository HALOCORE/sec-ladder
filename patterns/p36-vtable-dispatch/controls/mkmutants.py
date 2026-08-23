#!/usr/bin/env python3
"""p36 proof mutants: derive a deliberately broken `verus.rs` from the shipped
one by exact-string substitution, run Verus on it, and show it FAILS.

⚠ **A Verus control that does not verify cleanly cannot live in a pattern dir at
all** (`.memory/05-layout.md` item 11): `check.py` stage 5a requires every `.rs`
in the pattern that opens a `verus!` block to be pinned in `verus.obligations`,
and fails the gate for any pinned file with `n_err > 0`. So the mutants are
`.temp/` artefacts and THIS is the committed generator that derives them, with
every substitution asserting its own hit count so a mutant cannot silently drift
from the rung it mutates.

⚠ **Run with `--multiple-errors`.** `.memory/04-verus.md` §2b prescribes it and
p22 skipped it; its review then found a mutant failing on a different obligation
than the delivery claimed, plus a third error nobody had seen. This script
passes `--multiple-errors 20` always and prints the FULL error list.

    python3 patterns/p36-vtable-dispatch/controls/mkmutants.py --list
    python3 patterns/p36-vtable-dispatch/controls/mkmutants.py --run m1
    python3 patterns/p36-vtable-dispatch/controls/mkmutants.py --run all
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p36", "mutants")
VERUS_RUN = os.path.join(REPO, "verus_run.py")


def sub(text, old, new, n=1):
    got = text.count(old)
    if got != n:
        raise SystemExit(f"mkmutants.py: expected {n} occurrence(s) of\n"
                         f"  {old!r}\nfound {got}. verus.rs moved; fix this "
                         f"generator rather than the mutant.")
    return text.replace(old, new)


def shipped():
    return open(os.path.join(PDIR, "verus.rs")).read()


# ---------------------------------------------------------------- mutants ----
def m1():
    """DELETE THE SAFETY LINE -- `c/kernel.c`'s bug, written into R5.

    The dispatch becomes unconditional, so `tab_get_unchecked`'s
    `requires i < NOPS` has nothing to discharge it. This is the mutant the
    whole pattern is about."""
    s = shipped()
    return sub(s, """        if op < NOPS {
            acc = tab_get_unchecked(op).apply(acc ^ arg);
        } else {
            acc = acc.wrapping_mul(31).wrapping_add(SENT);
        }""",
        """        acc = tab_get_unchecked(op).apply(acc ^ arg);""")


def m2():
    """A WRONG FUNCTIONAL SPEC -- `op_spec`'s constant for opcode 3 changed.

    Nothing about memory safety moves; the kernel's `ensures` simply stops
    describing what the table does. It is here to show that the postcondition is
    load-bearing rather than decorative, i.e. that `op_fold` really is pinned to
    the dynamic types in `TABLE`."""
    s = shipped()
    return sub(s, """    } else if i == 3 {
        x.wrapping_add(0xc4ceb9fe1a85ec53)""",
        """    } else if i == 3 {
        x.wrapping_add(0xc4ceb9fe1a85ec54)""")


def m3():
    """AN INCONSISTENT TRUSTED POSTCONDITION -- `tab_get_unchecked`'s `ensures`
    shifted by one slot.

    `.memory/05-layout.md` item 5 asks every pattern for at least one mutant of
    exactly this shape -- a trusted postcondition made INCONSISTENT rather than
    merely weaker -- and this is p36's.

    ⚠ **THE PREDICTION MADE ABOUT IT WAS WRONG AND IS RECORDED HERE RATHER THAN
    QUIETLY CORRECTED.** It was written expecting the mutant to VERIFY in the
    shipped configuration (the item is `external_body`, so Verus never reads its
    body) and to be caught only by the twin. Measured, it fails in BOTH: the
    kernel's functional `ensures` ties slot `op` to `op_spec(op, ..)` through
    `run`, so an `ensures` that hands back the WRONG SLOT breaks the loop
    invariant immediately. That is a stronger result than the one predicted --
    on p36 the functional postcondition alone catches an inconsistent trusted
    contract -- and `m4` is the mutant that really does need the twin."""
    s = shipped()
    return sub(s, """    ensures
        r == TABLE@[i as int],
{
    unsafe { *TABLE.get_unchecked(i) }
}""",
        """    ensures
        r == TABLE@[(i as int + 1) % (NOPS as int)],
{
    unsafe { *TABLE.get_unchecked(i) }
}""")


def m4():
    """A TRUSTED PRECONDITION WEAKENED OFF BY ONE -- `buf_get_unchecked`'s
    `requires i < v@.len()` becomes `i <= v@.len()`.

    ⚠ **THIS IS THE ONE THE TWIN EXISTS FOR.** In the shipped configuration the
    item is `external_body`, so Verus never looks at the body and the weaker
    precondition simply makes every call site EASIER -- the file still verifies
    while the accessor now claims a one-past-the-end read is licensed, which is
    an axiomatised falsehood. `--cfg slb_twin` swaps in the checked body `v[i]`,
    which cannot be proved in bounds under `i <= v@.len()`, and the twin run
    fails. This is `.memory/04-verus.md`'s *"a `requires` deleted from an
    external_body wrapper -- same count, no diagnostic, and every caller's
    obligation silently gone"*, in its off-by-one form.

    ⚠ **THE WEAKENING HAS TO BE APPLIED TO BOTH COPIES, AND FINDING THAT OUT WAS
    ITSELF A MEASUREMENT.** The first version of this mutant changed the TRUSTED
    item's `requires` only. The result was `12 verified, 0 errors` shipped AND
    `14 verified, 0 errors` under the twin -- because the twin carries its own
    copy of the contract text and kept `i < v@.len()`, so it verified against
    the STRONG precondition while the trusted item shipped the weak one. What
    catches that shape is not Verus at all: it is the GATE, whose stage 5c-twin
    requires the twin's signature and contract to equal the trusted item's. So
    the twin regime has TWO independent teeth and this mutant exercises the
    second one only when both copies move together."""
    s = shipped()
    return sub(s, """    requires
        i < v@.len(),
    ensures
        r == v@[i as int],""",
        """    requires
        i <= v@.len(),
    ensures
        r == v@[i as int],""", n=2)


MUTANTS = {
    "m1": (m1, "delete `op < NOPS` -- c/kernel.c's bug in R5", ["shipped"]),
    "m2": (m2, "`op_spec` constant wrong at opcode 3", ["shipped"]),
    "m3": (m3, "`tab_get_unchecked`'s trusted `ensures` shifted by one slot",
           ["shipped", "twin"]),
    "m4": (m4, "`buf_get_unchecked`'s trusted `requires` weakened off by one",
           ["shipped", "twin"]),
}


def run(name):
    fn, desc, cfgs = MUTANTS[name]
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}.rs")
    open(p, "w").write(fn())
    print(f"=== {name}: {desc}")
    print(f"    {os.path.relpath(p, REPO)}")
    for cfg in cfgs:
        args = [VERUS_RUN, p, "--multiple-errors", "20"]
        if cfg == "twin":
            args += ["--cfg", "slb_twin"]
        r = subprocess.run(args, capture_output=True, text=True)
        txt = (r.stdout + r.stderr).strip()
        print(f"--- ./verus_run.py {os.path.relpath(p, REPO)} --multiple-errors 20"
              f"{' --cfg slb_twin' if cfg == 'twin' else ''}")
        for line in txt.splitlines():
            print(f"    {line}")
        print(f"    [exit {r.returncode}]")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run", default="all")
    a = ap.parse_args()
    if a.list:
        for n, (_, d, c) in sorted(MUTANTS.items()):
            print(f"  {n}  {d}   [configs: {', '.join(c)}]")
        return 0
    for n in (sorted(MUTANTS) if a.run == "all" else [a.run]):
        run(n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
