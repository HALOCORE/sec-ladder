#!/usr/bin/env python3
"""ph64 control -- UPSTREAM'S OWN REGRESSION TEST, replayed.

    python3 patterns-php/ph64-callback-frees-cursor/controls/bug41037.py

`562f886ecb14` ships `ext/standard/tests/general_functions/bug41037.phpt` INSIDE
the commit; `controls/bug41037.phpt` is those 23 lines, byte for byte, sliced out
of `controls/562f886ecb14.patch`. Its `--EXPECTF--` block is:

    hello
    Warning: unregister_tick_function(): Unable to delete tick function executed
             at the moment in %s on line %d
    Done
    hello
    Warning: ...
    hello
    Warning: ...

i.e. **the tick function runs THREE times and the refusal fires THREE times**,
and the list is still there at the end. That is upstream's own statement of what
the fix does, and it is a statement about a shape this row can drive: ONE
registered tick function whose callback unregisters ITSELF, dispatched three
times.

⚠⚠ `harness-php/gate.py` HASHES THIS FILE AND NEVER RUNS IT. Run it by hand.

⚠ This file does NOT import `../model.py`. It carries its own 40-line simulator
of `zend_llist_apply` + `zend_llist_del_element` + the comparator, so a model bug
and a control bug cannot cancel -- which is the same reason `inputs/gen.py`
re-derives rather than importing.

THE EXPECTATIONS, DECLARED BEFORE THE RUN (PROTOCOL_PHP.md §H):

  E1 must-fire      R1h, self-unregistering, 3 dispatches: 3 visits, 3 refusals,
                    0 dtors, `l->count == 1` at the end. That IS the phpt's
                    three `hello`s and three warnings.
  E2 must-fire      R1, the same input: **1 visit**. `DEL_LLIST_ELEMENT` sets
                    `l->head = current->next`, which is NULL on a one-entry list,
                    so dispatches 2 and 3 walk an EMPTY list and the tick
                    function never runs again. Upstream's test would print ONE
                    `hello` and no warning -- a visibly different program, and on
                    a real 5.0.0 build it is worse than that (the element is also
                    dereferenced at `basic_functions.c:2135` after the free).
  E3 must-NOT-fire  the same three dispatches with the callback unregistering a
                    name NOBODY has: both rungs give 3 visits, 0 refusals,
                    0 dtors. Without this, E1/E2's difference could be "the
                    callback called `unregister_tick_function` at all".
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHPT = os.path.join(HERE, "bug41037.phpt")


class Node:
    __slots__ = ("next", "prev", "name", "calling")

    def __init__(self, name):
        self.next = self.prev = None
        self.name = name
        self.calling = False


def run(hardened, dispatches, self_name, target_name):
    """One tick function, `dispatches` rounds of `php_run_ticks`.

    `zend_llist_{apply,del_element}` and `user_tick_function_{call,compare}`,
    transcribed. `target_name` is what the callback asks to unregister."""
    head = Node(self_name)
    tail, count = head, 1
    st = {"visits": 0, "refusals": 0, "dtors": 0}

    def del_element(key):
        nonlocal head, tail, count
        current = head
        while current is not None:
            nxt = current.next                              # zend_llist.c:97
            ret = current.name == key                       # the comparator
            if ret and hardened and current.calling:        # 562f886ecb14
                st["refusals"] += 1
                current = nxt
                continue
            if ret:
                if current.prev is not None:                # DEL_LLIST_ELEMENT
                    current.prev.next = current.next
                else:
                    head = current.next
                if current.next is not None:
                    current.next.prev = current.prev
                else:
                    tail = current.prev
                st["dtors"] += 1
                count -= 1
                return
            current = nxt

    for _ in range(dispatches):
        element = head                                      # zend_llist.c:190
        while element is not None:
            if not element.calling:                         # :2108
                element.calling = True                      # :2109
                st["visits"] += 1                           # the `echo "hello"`
                del_element(target_name)                    # :2860
                element.calling = False                     # :2135  SITE C
            element = element.next                          # :190   SITE L
    return dict(st, count=count)


def main():
    # ⚠ THE `--EXPECTF--` BLOCK ONLY. The FIRST version of this control counted
    # `hello` over the WHOLE file and got 4, because the `--FILE--` section
    # contains the `echo "hello";` that produces them -- and it read as "R1h
    # visits 3, upstream says 4", i.e. a MISS against a number that was wrong.
    # It was caught by E1's declared expectation and it is recorded here rather
    # than quietly repaired: a control that counts the wrong thing evaluates
    # fine (PROTOCOL_PHP.md §H).
    whole = open(PHPT).read()
    expect = whole.split("--EXPECTF--", 1)[1]
    n_hello = expect.count("hello")
    n_warn = expect.count("Unable to delete tick function")
    print(f"controls/bug41037.phpt: {n_hello} x `hello`, {n_warn} x the refusal "
          f"warning  <- upstream's own --EXPECTF--")

    bad = []
    r1h = run(True, 3, "a", "a")
    if not (r1h["visits"] == n_hello and r1h["refusals"] == n_warn
            and r1h["dtors"] == 0 and r1h["count"] == 1):
        bad.append(f"E1 MISS: R1h gave {r1h}, upstream's test says visits="
                   f"{n_hello} refusals={n_warn} dtors=0 count=1")
    r1 = run(False, 3, "a", "a")
    if r1["visits"] != 1:
        bad.append(f"E2 MISS: R1 gave {r1}; the one-entry list should be EMPTY "
                   f"after the first dispatch, so exactly one `hello`")
    ctl_h = run(True, 3, "a", "zzz")
    ctl_1 = run(False, 3, "a", "zzz")
    for lbl, r in (("R1h", ctl_h), ("R1", ctl_1)):
        if not (r["visits"] == 3 and r["refusals"] == 0 and r["dtors"] == 0
                and r["count"] == 1):
            bad.append(f"E3 MISS: {lbl} with a callback that unregisters a name "
                       f"nobody has gave {r}; both rungs must be identical there")

    print(f"E1 must-fire      R1h  : {r1h}")
    print(f"E2 must-fire      R1   : {r1}")
    print(f"E3 must-NOT-fire  R1h  : {ctl_h}")
    print(f"E3 must-NOT-fire  R1   : {ctl_1}")
    for b in bad:
        print("  " + b)
    print(f"\n=== bug41037 CONTROL: {'FAIL' if bad else 'PASS'} "
          f"({len(bad)} miss(es)) ===")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
