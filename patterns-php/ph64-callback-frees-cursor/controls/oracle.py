#!/usr/bin/env python3
"""ph64 control -- THE ORACLE. Does R1 differ from R1h, on exactly the windows
where it must and on no others?

    python3 patterns-php/ph64-callback-frees-cursor/controls/oracle.py

⚠⚠ `harness-php/gate.py` HASHES THIS FILE AND NEVER RUNS IT (`TASK_PHP_022` m6),
so the must-NOT-fire cases below are the only thing between this control and a
silent wrong number. Run it by hand and paste the output.

⚠⚠⚠ WHY THIS CONTROL EXISTS AT ALL, AND IT IS THE HALF A BUILD TASK RUNS ON.
`CATALOGUE.md:795` proposes this row's `u64` be *"a fold of the ids the walk
invoked"*. On the corpus's own trigger that oracle MEASURES NOTHING:
`REAL_SIZE(sizeof(zend_llist_element) + sizeof(user_tick_function_entry) - 1)`
is 40, `40 >> 3 = 5 < MAX_CACHED_MEMORY`, so the freed element goes into
`AG(cache)[5]`, is NOT returned to `malloc`, and its payload is untouched --
`element->next` still reads the true successor and the visit fold is
BIT-IDENTICAL between the two rungs. `TASK_PHP_031_REPORT` §6.4 measured that
and the row's `u64` is built to survive it: the fold is only PART of it, and
`l->count`, the dtor count, the refusal count and all four allocator counters
are the rest.

THE EXPECTATIONS, DECLARED BEFORE THE RUN (PROTOCOL_PHP.md §H):

  E1 must-NOT-fire  `mode != SELF` or `trigger` names no live entry: R1 == R1h,
                    with the reuse allocation ON as well as OFF. Without this,
                    E2's and E3's divergence could be the ALLOCATION rather than
                    the free, and nothing in the number would say which.
  E2 must-fire      `mode == SELF`, live trigger, NO reuse -- THE CORPUS TRIGGER:
                    R1 completes, and its `u64` DIFFERS. This is the latent case.
  E2a must-fire     ... and the VISIT FOLD ALONE is EQUAL on those same windows.
                    The catalogue's proposed oracle is empty here and this is the
                    line that says so.
  E3 must-fire      `mode == SELF`, live trigger, reuse ON: R1's cursor is a
                    block that has been freed AND handed back out, so the model
                    refuses to invent a trajectory and raises `Wild`. All four
                    `DEL_LLIST_ELEMENT` arms.
  E4 must-NOT-fire  no window outside E3's set raises `Wild`.
  E5 must-fire      every one of the four arms is reached by the sweep.

The two rungs are `../model.py::Model._simulate(hardened=False/True)` -- the
STRUCTURAL simulation, driven at both rungs, so the difference is a measurement
and not a claim. `controls/differential.py` is the other half: it checks that
simulation against the SHIPPED C.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import model as M  # noqa: E402


def windows():
    """Every (n x trigger x mode x post x reuse) up to eight entries, plus two
    long lists so `MAX_CACHED_ENTRIES` and a real `n` are exercised."""
    for label, w in M.Model._synthetic_windows():
        yield label, w
    for slots in (40, 300):
        for mode in range(4):
            for reuse in (0, 1):
                for trig in (0, 1, slots // 2, slots):
                    for post in (0, 1, slots // 2, slots):
                        yield (f"slots={slots} trig={trig} mode={mode} "
                               f"reuse={reuse} post={post}",
                               M.Model._mkwin(slots, slots - 1, trig,
                                              mode | (reuse << 16), post))


def fold_only(win, ln, hardened):
    """The visit fold ALONE -- the oracle `CATALOGUE.md` proposes -- recomputed
    without the counters, so E2a can say what it does and does not see."""
    d = M._decode(win, ln)
    n, trigger, mode = d["n"], d["trigger"], d["mode"]
    reuse = d["reuse"]
    # Re-run the structural simulation and read the fold out of `info` is not
    # possible (info carries no fold), so recompute the visit ORDER here from
    # the schedule -- which is exactly what makes this an independent check.
    skipped = 0
    if 1 <= trigger <= n and mode == M.UNREG_AHEAD and trigger < n:
        skipped = trigger + 1
    if not hardened and 1 <= trigger <= n and mode == M.UNREG_SELF and reuse:
        return None                      # R1 goes wild; no defined fold
    acc = 0
    for i in range(1, n + 1):
        if i == skipped:
            continue
        nm = M._name_of(win, i)
        acc = (acc * 31 + M._rd32(nm, 0)) & M.MASK
        acc = (acc * 31 + M._rd32(nm, 4)) & M.MASK
    return acc


def main():
    fails = {k: 0 for k in ("E1", "E2", "E2a", "E3", "E4")}
    first = {}
    n = {k: 0 for k in ("E1", "E2", "E3")}
    arms = set()
    for label, win in windows():
        ln = len(win)
        d = M._decode(win, ln)
        acts = 1 <= d["trigger"] <= d["n"]
        is_self = d["mode"] == M.UNREG_SELF and acts

        r1h, info = M.Model._simulate(win, ln, True)
        arms |= info["arms"]
        try:
            r1 = M.Model._simulate(win, ln, False)[0]
            wild = False
        except M.Wild:
            r1, wild = None, True

        if is_self and d["reuse"]:
            n["E3"] += 1
            if not wild:
                fails["E3"] += 1
                first.setdefault("E3", f"[{label}] R1 did NOT go wild")
        else:
            if wild:
                fails["E4"] += 1
                first.setdefault("E4", f"[{label}] R1 went wild with "
                                       f"mode={d['mode']} trigger={d['trigger']}")
            elif is_self:
                n["E2"] += 1
                if r1 == r1h:
                    fails["E2"] += 1
                    first.setdefault("E2", f"[{label}] R1 == R1h == {r1} on the "
                                           f"corpus trigger; the oracle is empty")
                f1 = fold_only(win, ln, False)
                f1h = fold_only(win, ln, True)
                if f1 != f1h:
                    fails["E2a"] += 1
                    first.setdefault("E2a", f"[{label}] the VISIT FOLD differs "
                                            f"({f1} vs {f1h}); the catalogue's "
                                            f"oracle would have worked here and "
                                            f"this control's premise is wrong")
            else:
                n["E1"] += 1
                if r1 != r1h:
                    fails["E1"] += 1
                    first.setdefault("E1", f"[{label}] R1={r1} R1h={r1h} with "
                                           f"mode={d['mode']} "
                                           f"trigger={d['trigger']} "
                                           f"reuse={d['reuse']}")
    missing = sorted(set(M.ARMS) - arms)
    print(f"E1  must-NOT-fire  R1 == R1h              : "
          f"{n['E1'] - fails['E1']}/{n['E1']}")
    print(f"E2  must-fire      R1 != R1h (latent)     : "
          f"{n['E2'] - fails['E2']}/{n['E2']}")
    print(f"E2a must-fire      visit fold IS EQUAL    : "
          f"{n['E2'] - fails['E2a']}/{n['E2']}  "
          f"<- the catalogue's oracle measures nothing")
    print(f"E3  must-fire      R1 goes WILD on reuse  : "
          f"{n['E3'] - fails['E3']}/{n['E3']}")
    print(f"E4  must-NOT-fire  nothing else goes wild : "
          f"{n['E1'] + n['E2'] - fails['E4']}/{n['E1'] + n['E2']}")
    print(f"E5  must-fire      DEL_LLIST arms reached : {sorted(arms)}"
          + (f"  MISSING {missing}" if missing else ""))
    bad = sum(fails.values()) + len(missing)
    for k in sorted(first):
        print(f"  {k} first miss: {first[k]}")
    print(f"\n=== ORACLE CONTROL: {'FAIL' if bad else 'PASS'} ({bad} miss(es)) ===")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
