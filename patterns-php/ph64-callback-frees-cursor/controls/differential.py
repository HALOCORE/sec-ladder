#!/usr/bin/env python3
"""ph64 control -- THE SHIPPED C AGAINST THE REFERENCE MODEL, off the corpus.

    python3 patterns-php/ph64-callback-frees-cursor/controls/differential.py

It builds `controls/dump.c` against the row's own `c/kernel.c` and
`c/kernel_hardened.c`, feeds both binaries windows this file constructs, and
compares three numbers per window: the C's, `../model.py`'s STRUCTURAL
simulation, and `../model.py`'s CLOSED FORM (`llist_fold`, which is what the
gate evaluates this row's `ensures` against).

⚠⚠ WHY IT EXISTS BESIDE `model.py::selfcheck`. `selfcheck` drives the model's
two implementations against each other; it never opens a compiler. `check.py`
drives the C against the model, but only on the six `inputs/*.bin` -- and
`PROTOCOL_PHP.md` §A2a rule 2 is the standing lesson that *"`inputs/` is not a
domain"*. This file closes the third edge of that triangle over ~2 600 windows
spanning every (list length x trigger x mode x post x reuse) combination.

⚠⚠ `harness-php/gate.py` HASHES THIS FILE AND NEVER RUNS IT. Run it by hand and
paste the output; the expectations below are the only thing between it and a
silent wrong number.

THE EXPECTATIONS, DECLARED BEFORE THE RUN (PROTOCOL_PHP.md §H):

  E1 must-fire      for EVERY window: `c/kernel_hardened.c`'s u64 ==
                    `Model._simulate(hardened=True)` == `Model.llist_fold`.
                    Three spellings, one number, none of them the others.
  E2 must-fire      `mode == SELF` with a live trigger and NO reuse -- the
                    corpus's own trigger: the C's R1 completes and DIFFERS from
                    its R1h. If it agreed, this row's measured oracle would be
                    empty.
  E3 must-NOT-fire  `mode != SELF`, or `trigger` names no live entry: the C's R1
                    and R1h agree, WITH the reuse allocation on as well as off.
                    Without this, E2's divergence could be the allocation.
  E4 must-fire      `mode == SELF`, live trigger, reuse ON: the C's R1 dies on a
                    SIGNAL. All four `DEL_LLIST_ELEMENT` arms.
  E5 must-NOT-fire  no other window makes the C's R1 die.
  E6 must-fire      the sweep reaches all four `DEL_LLIST_ELEMENT` arms.

⚠ E2 and E4 are the two halves of the same defect, and the row ships BOTH: E2 is
what the measured `u64` sees on the pristine cached allocator, E4 is what a
sanitizer sees once the freed block is handed back out. `TASK_PHP_031_REPORT`
§6.4 and `../NOTES.md` §6.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
sys.path.insert(0, ROW)
import model as M  # noqa: E402

REPO = os.path.dirname(os.path.dirname(ROW))
OUT = os.path.join(REPO, ".temp", "php32")


def build():
    os.makedirs(OUT, exist_ok=True)
    bins = {}
    for tag, src in (("r1", "kernel.c"), ("r1h", "kernel_hardened.c")):
        b = os.path.join(OUT, f"ph64_dump_{tag}.bin")
        cmd = ["gcc", "-std=c99", "-Wall", "-Wextra", "-O1", "-g",
               "-I", os.path.join(REPO, "common-php"),
               "-I", os.path.join(ROW, "c"),
               os.path.join(HERE, "dump.c"), os.path.join(ROW, "c", src),
               "-o", b]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-2000:])
            raise SystemExit(f"differential.py: cannot build {src}")
        bins[tag] = b
    return bins


def drive(binary, wins):
    inp = "".join(f"{len(w)} {w.hex()}\n" for w in wins)
    r = subprocess.run([binary], input=inp, capture_output=True, text=True)
    out = []
    for line in r.stdout.splitlines():
        f = line.split()
        out.append(("CRASH", int(f[2])) if f[1] == "CRASH" else ("OK", int(f[1])))
    if len(out) != len(wins):
        raise SystemExit(f"differential.py: {binary} returned {len(out)} of "
                         f"{len(wins)} rows; stderr={r.stderr[-400:]}")
    return out


def windows():
    for _, w in M.Model._synthetic_windows():
        yield w
    for slots in (40, 300):
        for mode in range(4):
            for reuse in (0, 1):
                for trig in (0, 1, slots // 2, slots):
                    for post in (0, 1, slots // 2, slots):
                        yield M.Model._mkwin(slots, slots - 1, trig,
                                             mode | (reuse << 16), post)


def main():
    bins = build()
    wins = list(windows())
    print(f"windows: {len(wins)}")
    c1 = drive(bins["r1"], wins)
    c1h = drive(bins["r1h"], wins)

    fails = {k: 0 for k in ("E1", "E2", "E3", "E4", "E5")}
    first = {}
    n = {k: 0 for k in ("E2", "E3", "E4")}
    arms = set()
    for i, w in enumerate(wins):
        ln = len(w)
        m = M.Model.__new__(M.Model)
        m.buf, m.stride = w, ln
        sim, info = m._simulate(w, ln, True)
        closed = m.llist_fold(w, 0, ln)
        arms |= info["arms"]
        d = M._decode(w, ln)
        acts = 1 <= d["trigger"] <= d["n"]
        is_self = d["mode"] == M.UNREG_SELF and acts

        if not (c1h[i] == ("OK", sim) and closed == sim):
            fails["E1"] += 1
            first.setdefault("E1", f"win {i} ({ln}B): C-R1h={c1h[i]} "
                                   f"simulated={sim} closed_form={closed}")
        if is_self and not d["reuse"]:
            n["E2"] += 1
            if c1[i] == c1h[i]:
                fails["E2"] += 1
                first.setdefault("E2", f"win {i}: C R1 == R1h == {c1[i]} on the "
                                       f"corpus trigger; the oracle is empty")
        elif not is_self:
            n["E3"] += 1
            if c1[i] != c1h[i]:
                fails["E3"] += 1
                first.setdefault("E3", f"win {i}: C R1={c1[i]} R1h={c1h[i]} with "
                                       f"mode={d['mode']} trigger={d['trigger']} "
                                       f"reuse={d['reuse']}")
        if is_self and d["reuse"]:
            n["E4"] += 1
            if c1[i][0] != "CRASH":
                fails["E4"] += 1
                first.setdefault("E4", f"win {i}: C R1 survived SELF+reuse "
                                       f"(n={d['n']} trigger={d['trigger']})")
        elif c1[i][0] == "CRASH":
            fails["E5"] += 1
            first.setdefault("E5", f"win {i}: C R1 died with mode={d['mode']} "
                                   f"trigger={d['trigger']} reuse={d['reuse']}")
    missing = sorted(set(M.ARMS) - arms)
    print(f"E1 must-fire      C-R1h == simulated == closed form : "
          f"{len(wins) - fails['E1']}/{len(wins)}")
    print(f"E2 must-fire      C R1 != C R1h (the latent case)   : "
          f"{n['E2'] - fails['E2']}/{n['E2']}")
    print(f"E3 must-NOT-fire  C R1 == C R1h everywhere else     : "
          f"{n['E3'] - fails['E3']}/{n['E3']}")
    print(f"E4 must-fire      C R1 SIGNALS on reuse             : "
          f"{n['E4'] - fails['E4']}/{n['E4']}")
    print(f"E5 must-NOT-fire  nothing else signals              : "
          f"{len(wins) - n['E4'] - fails['E5']}/{len(wins) - n['E4']}")
    print(f"E6 must-fire      DEL_LLIST_ELEMENT arms reached    : {sorted(arms)}"
          + (f"  MISSING {missing}" if missing else ""))
    for k in sorted(first):
        print(f"  {k} first miss: {first[k]}")
    bad = sum(fails.values()) + len(missing)
    print(f"\n=== differential CONTROL: {'FAIL' if bad else 'PASS'} "
          f"({bad} miss(es)) ===")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
