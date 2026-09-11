#!/usr/bin/env python3
"""ph64 control -- WHICH `calling` FLAG `562f886ecb14` READS, AND WHY IT MATTERS.

    python3 patterns-php/ph64-callback-frees-cursor/controls/predicate.py

`562f886ecb14`'s whole hunk is

    if (ret && tick_fe1->calling) { <warn>; return 0; }

and `user_tick_function_compare(tick_fe1, tick_fe2)` is called by
`zend_llist_del_element:98` as `compare(current->data, element)` -- so
**`tick_fe1` is the LIST ELEMENT and `tick_fe2` is the SEARCH KEY**. That is not
a detail:

  * the LIST element's `calling` is 1 for exactly the duration of the userland
    call (`basic_functions.c:2109` sets it, `:2135` clears it), so it is 1 on
    precisely the elements a live `zend_llist_apply` cursor points at;
  * the SEARCH KEY's `calling` is never written at all --
    `PHP_FUNCTION(unregister_tick_function)` (`:2843-2861`) sets only
    `arguments` and `arg_count`, so in PHP the key's flag is an INDETERMINATE
    stack `int`. (`../c/kernel.c` zeroes it, which is the row's one divergence
    here and is declared in `../spec.md`.)

So the fix's soundness rests on a one-word choice, and this control prices the
other one.

⚠⚠ `harness-php/gate.py` HASHES THIS FILE AND NEVER RUNS IT. Run it by hand.

THE EXPECTATIONS, DECLARED BEFORE THE RUN (PROTOCOL_PHP.md §H):

  E1 must-fire      reading `tick_fe2->calling` -- the KEY's flag, which this
                    kernel zeroes -- makes the guard DEAD: on every one of the
                    corpus-trigger windows the "hardened" rung returns exactly
                    R1's `u64`. The fix would have been a no-op.
  E2 must-fire      ... and on the reuse windows it goes WILD, exactly like R1.
                    A guard that never fires removes no fault.
  E3 must-NOT-fire  on every window where nothing is freed under the cursor the
                    two spellings agree with each other AND with R1h. The
                    difference E1 measures is the guard firing, not the guard
                    existing.
  E4 must-fire      the shipped spelling (`tick_fe1`) refuses on exactly the
                    windows where the walk holds the element -- i.e. `refusals`
                    is 1 on a live SELF trigger and 0 everywhere else. That is
                    `TASK_PHP_031_REPORT` §4.2's invariant, measured rather than
                    argued.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import model as M  # noqa: E402

SZ_NAME, REQ_ELEM = 8, 39
MAXC, MAXE = 11, 256
T = (1000003, 1000033, 1000037, 1000039)
MASK = (1 << 64) - 1


class Node:
    __slots__ = ("next", "prev", "name", "calling", "recycled")

    def __init__(self, name):
        self.next = self.prev = None
        self.name = name
        self.calling = False
        self.recycled = False


class Al:
    def __init__(self):
        self.st = [[] for _ in range(MAXC)]
        self.na = self.nf = self.nh = self.by = 0

    def alloc(self, size):
        r = (size + 7) & ~7
        i = r >> 3
        self.na += 1
        if i < MAXC and self.st[i]:
            self.nh += 1
            return self.st[i].pop()
        self.by += r
        return None

    def free(self, size, obj=None):
        r = (size + 7) & ~7
        i = r >> 3
        self.nf += 1
        if i < MAXC and len(self.st[i]) < MAXE:
            self.st[i].append(obj)

    def tally(self):
        return (((self.na * T[0]) & MASK) ^ ((self.nf * T[1]) & MASK)
                ^ ((self.nh * T[2]) & MASK) ^ ((self.by * T[3]) & MASK)) & MASK


class Wild(Exception):
    pass


def run(win, ln, guard):
    """`guard` is one of:
         "none"  -- R1, PHP 5.0.0, no guard at all
         "fe1"   -- 562f886ecb14 AS SHIPPED: reads the LIST element's flag
         "fe2"   -- the counterfactual: reads the SEARCH KEY's flag, which
                    `unregister_tick_function` never sets"""
    d = M._decode(win, ln)
    n, trigger, mode, reuse, post = (d["n"], d["trigger"], d["mode"], d["reuse"],
                                     d["post"])
    al = Al()
    head = tail = None
    count = 0
    st = {"fold": 0, "visits": 0, "dtors": 0, "refusals": 0, "reuse_block": None}
    # the search key `PHP_FUNCTION(unregister_tick_function)` builds. Its
    # `calling` is never assigned in PHP; `../c/kernel.c` zeroes it.
    key_calling = False

    def del_element(key):
        nonlocal head, tail, count
        cur = head
        while cur is not None:
            nxt = cur.next
            ret = cur.name == key
            flag = (cur.calling if guard == "fe1"
                    else key_calling if guard == "fe2" else False)
            if ret and guard != "none" and flag:
                st["refusals"] += 1
                cur = nxt
                continue
            if ret:
                if cur.prev is not None:
                    cur.prev.next = cur.next
                else:
                    head = cur.next
                if cur.next is not None:
                    cur.next.prev = cur.prev
                else:
                    tail = cur.prev
                st["dtors"] += 1
                al.free(SZ_NAME)
                al.free(REQ_ELEM, cur)
                count -= 1
                return
            cur = nxt

    def unregister(i):
        al.alloc(SZ_NAME)
        del_element(M._name_of(win, i))
        al.free(SZ_NAME)

    def userland(nm):
        me = M._rd32(nm, 0)
        st["fold"] = (st["fold"] * 31 + me) & MASK
        st["fold"] = (st["fold"] * 31 + M._rd32(nm, 4)) & MASK
        st["visits"] += 1
        if me != trigger:
            return
        if mode == M.UNREG_SELF:
            unregister(me)
        elif mode == M.UNREG_AHEAD and me < n:
            unregister(me + 1)
        elif mode == M.UNREG_BEHIND and me > 1:
            unregister(me - 1)
        if reuse and st["reuse_block"] is None:
            got = al.alloc(REQ_ELEM)
            if got is not None:
                got.recycled = True
            st["reuse_block"] = got if got is not None else True

    for i in range(1, n + 1):
        al.alloc(SZ_NAME)
        nd = Node(M._name_of(win, i))
        al.alloc(REQ_ELEM)
        nd.prev = tail
        if tail is not None:
            tail.next = nd
        else:
            head = nd
        tail = nd
        count += 1

    element = head
    while element is not None:
        if not element.calling:
            element.calling = True
            userland(element.name)
            element.calling = False
        if element.recycled:
            raise Wild()
        element = element.next

    if post:
        unregister(post)
    acc = st["fold"]
    for v in (count, st["dtors"], st["visits"], st["refusals"], n):
        acc = (acc * 31 + v) & MASK
    if st["reuse_block"] is not None:
        al.free(REQ_ELEM)
    cur = head
    while cur is not None:
        nx = cur.next
        al.free(SZ_NAME)
        al.free(REQ_ELEM, cur)
        cur = nx
    return (acc ^ al.tally()) & MASK, st["refusals"]


def call(win, ln, guard):
    try:
        return run(win, ln, guard)
    except Wild:
        return None, None


def main():
    fails = {k: 0 for k in ("E1", "E2", "E3", "E4")}
    first = {}
    n = {k: 0 for k in ("E1", "E2", "E3", "E4")}
    for label, win in M.Model._synthetic_windows():
        ln = len(win)
        d = M._decode(win, ln)
        acts = 1 <= d["trigger"] <= d["n"]
        is_self = d["mode"] == M.UNREG_SELF and acts
        u_none, _ = call(win, ln, "none")
        u_fe1, r_fe1 = call(win, ln, "fe1")
        u_fe2, _ = call(win, ln, "fe2")

        want_ref = 1 if is_self else 0
        if u_fe1 is not None:
            n["E4"] += 1
            if r_fe1 != want_ref:
                fails["E4"] += 1
                first.setdefault("E4", f"[{label}] the shipped guard refused "
                                       f"{r_fe1} time(s), expected {want_ref}")

        if is_self and not d["reuse"]:
            n["E1"] += 1
            if u_fe2 != u_none:
                fails["E1"] += 1
                first.setdefault("E1", f"[{label}] tick_fe2 spelling gave "
                                       f"{u_fe2}, R1 gave {u_none}; it was "
                                       f"expected to be a no-op")
        elif is_self and d["reuse"]:
            n["E2"] += 1
            if u_fe2 is not None:
                fails["E2"] += 1
                first.setdefault("E2", f"[{label}] tick_fe2 spelling did NOT go "
                                       f"wild")
        else:
            n["E3"] += 1
            r1h = M.Model._simulate(win, ln, True)[0]
            if not (u_none == u_fe1 == u_fe2 == r1h):
                fails["E3"] += 1
                first.setdefault("E3", f"[{label}] none={u_none} fe1={u_fe1} "
                                       f"fe2={u_fe2} model={r1h}")

    print(f"E1 must-fire      `tick_fe2` guard == R1 (a no-op)   : "
          f"{n['E1'] - fails['E1']}/{n['E1']}")
    print(f"E2 must-fire      `tick_fe2` guard still goes WILD   : "
          f"{n['E2'] - fails['E2']}/{n['E2']}")
    print(f"E3 must-NOT-fire  all three agree where nothing dies : "
          f"{n['E3'] - fails['E3']}/{n['E3']}")
    print(f"E4 must-fire      shipped guard refuses exactly once : "
          f"{n['E4'] - fails['E4']}/{n['E4']}   <- §4.2's invariant, measured")
    for k in sorted(first):
        print(f"  {k} first miss: {first[k]}")
    bad = sum(fails.values())
    print(f"\n=== predicate CONTROL: {'FAIL' if bad else 'PASS'} "
          f"({bad} miss(es)) ===")
    print("\nREAD: `562f886ecb14` is one word away from being a no-op, and the "
          "word is which\nof the comparator's two arguments it reads. "
          "`zend_llist_del_element:98` passes\n`current->data` first, so "
          "`tick_fe1` is the element the walk is standing on -- and\nthat, not "
          "the key, is the thing whose lifetime the walk depends on.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
