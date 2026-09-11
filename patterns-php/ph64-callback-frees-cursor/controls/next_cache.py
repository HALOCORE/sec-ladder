#!/usr/bin/env python3
"""ph64 control -- THE COUNTERFACTUAL HARDENING, and what it does NOT buy.

    python3 patterns-php/ph64-callback-frees-cursor/controls/next_cache.py

⭐⭐ THE ROW'S SHARPEST C-SIDE FACT, MEASURED RATHER THAN ASSERTED.
`Zend/zend_llist.c` contains SIX callback-driven walks. Three of them cache the
successor before calling the callback and three advance in the `for` header:

    zend_llist_del_element          :91-104   caches_next=YES
    zend_llist_destroy              :107-121  caches_next=YES
    zend_llist_apply_with_del       :171-183  caches_next=YES   <- FIFTEEN LINES
    zend_llist_apply                :186-193  caches_next=no    <- THE DEFECT
    zend_llist_apply_with_argument  :229-236  caches_next=no
    zend_llist_apply_with_arguments :239-249  caches_next=no

`zend_llist_apply_with_del` is fifteen lines ABOVE `zend_llist_apply`, takes the
same caller-supplied `func`, and caches `next = element->next` at `:177` BEFORE
calling it. Same file, same author, same idiom written both ways. So there is a
hardening upstream ALREADY HAD IN HAND -- and this control prices it against the
one upstream actually shipped.

⚠⚠ IT IS NOT R1h AND MUST NEVER BE PRESENTED AS ONE. `PROTOCOL_PHP.md` §C:
`c/kernel_hardened.c` is the real `fix_commit`, full stop. `562f886ecb14` is what
php-5.2.2 shipped and master still carries. This file measures the road not
taken; `../spec.md`'s `idiom.forbidden[0]` pins the cached-`next` spelling ABSENT
from every rung so that no rung can quietly become it.

THE EXPECTATIONS, DECLARED BEFORE THE RUN (PROTOCOL_PHP.md §H):

  E1 must-fire      caching `next` removes EVERY wild walk. On all the
                    self-unregister-plus-reuse windows R1 follows a link out of a
                    recycled block; with `next` cached it follows the true
                    successor and the walk completes. SITE L IS FIXED.
  E2 must-fire      ... and SITE C IS NOT. On the same windows the write
                    `tick_fe->calling = 0` (basic_functions.c:2135) still lands
                    in the block the callback's own `emalloc` just took back, so
                    the recycled block is CLOBBERED. Caching `next` is a fix for
                    one of the row's two dereferences and the row cites both.
  E3 must-fire      ... and it does not restore the ANSWER either: on the latent
                    windows (self-unregister, no reuse) the cached-`next` rung's
                    u64 still differs from R1h's, because the element really was
                    freed -- `l->count`, the dtor count and the allocator tally
                    all moved. Only the upstream guard prevents the free.
  E4 must-NOT-fire  where the walk frees NOTHING, or frees an entry BEHIND the
                    cursor, R1 == R1+next_cache == R1h. Caching a pointer changes
                    nothing where the pointer was never going to die.
  E5 must-fire      ⚠⚠⚠ WHERE THE CALLBACK FREES THE CURSOR'S OWN SUCCESSOR --
                    `mode == AHEAD` -- THE CACHED-`next` RUNG IS THE ONE THAT IS
                    WRONG. Plain `zend_llist_apply` re-reads `element->next` AFTER
                    the callback, so `DEL_LLIST_ELEMENT`'s repaired link makes it
                    skip the deleted entry correctly; the cached-`next` rung
                    followed a pointer it read BEFORE the free and VISITS THE
                    FREED ELEMENT. Its `u64` differs from both R1's and R1h's.

⚠⚠ E5 WAS NOT PREDICTED. This control's first version declared E4 over every
window where "nothing is freed under the cursor" and it MISSED on 196 of 1958 --
all of them `mode == AHEAD`. The expectation was wrong, not the measurement, and
the miss is recorded here rather than quietly rewritten (PROTOCOL_PHP.md §H,
`TASK_PHP_031_REPORT` §8.8's discipline). ⭐ WHAT IT BUYS IS THE POINT: the two
hardenings are NOT ordered. `562f886ecb14` prevents the free, so it is safe
against both shapes; caching `next` trades a use-after-free of the CURRENT
element for a use-after-free of its SUCCESSOR, and leaves SITE C standing in both.
**Upstream picked the one that dominates**, and this row can say so because it
carries both sites.

⚠ This file does not import `../model.py`'s simulator for the rungs it invents;
it carries its own, so a model bug and a control bug cannot cancel. It DOES use
`model.py`'s window decoder and R1h result, which is parsing and a published
number rather than the thing under test.
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


def run(win, ln, hardened, cache_next):
    """`hardened` = 562f886ecb14's guard; `cache_next` = the counterfactual.

    Returns `(u64, flags)` where `flags` records what the two dereferences did:
    `wild` = the walk followed a link out of a recycled block (SITE L);
    `clobber` = SITE C wrote into a block the callback had taken back."""
    d = M._decode(win, ln)
    n, trigger, mode, reuse, post = (d["n"], d["trigger"], d["mode"], d["reuse"],
                                     d["post"])
    al, nodes = Al(), []
    head = tail = None
    count = 0
    st = {"fold": 0, "visits": 0, "dtors": 0, "refusals": 0, "wild": False,
          "clobber": False, "stale": False, "reuse_block": None}

    freed = set()

    def del_element(key):
        nonlocal head, tail, count
        cur = head
        while cur is not None:
            nxt = cur.next
            ret = cur.name == key
            if ret and hardened and cur.calling:
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
                freed.add(id(cur))
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
        nodes.append(nd)
        count += 1

    element = head
    guard = 0
    while element is not None and guard < 4 * n + 8:
        guard += 1
        if id(element) in freed:
            # The walk is standing on a block `pefree` has already returned.
            # Plain `zend_llist_apply` reaches this only via SITE L; the
            # cached-`next` rung reaches it by following a link it read BEFORE
            # the callback ran.
            st["stale"] = True
        nxt_cached = element.next          # zend_llist_apply_with_del:177
        if not element.calling:
            element.calling = True
            userland(element.name)
            if element.recycled:
                # SITE C -- basic_functions.c:2135 writes into the block the
                # callback's own emalloc took back. Caching `next` does not
                # move this line by one character.
                st["clobber"] = True
            element.calling = False
        if cache_next:
            element = nxt_cached
        else:
            if element.recycled:
                st["wild"] = True
                break                      # the C dereferences window bytes here
            element = element.next         # zend_llist.c:190  SITE L

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
    return (acc ^ al.tally()) & MASK, st


def main():
    fails = {k: 0 for k in ("E1", "E2", "E3", "E4", "E5")}
    first = {}
    n = {k: 0 for k in ("E1", "E3", "E4", "E5")}
    for label, win in M.Model._synthetic_windows():
        ln = len(win)
        d = M._decode(win, ln)
        acts = 1 <= d["trigger"] <= d["n"]
        is_self = d["mode"] == M.UNREG_SELF and acts
        # does the callback free the CURSOR'S OWN SUCCESSOR?
        ahead = (d["mode"] == M.UNREG_AHEAD and acts and d["trigger"] < d["n"])
        r1h = M.Model._simulate(win, ln, True)[0]
        u_plain, f_plain = run(win, ln, False, False)
        u_cache, f_cache = run(win, ln, False, True)

        if is_self and d["reuse"]:
            n["E1"] += 1
            if not f_plain["wild"]:
                fails["E1"] += 1
                first.setdefault("E1", f"[{label}] plain R1 was not wild; the "
                                       f"control's own premise is wrong")
            elif f_cache["wild"]:
                fails["E1"] += 1
                first.setdefault("E1", f"[{label}] caching `next` did NOT remove "
                                       f"the wild walk")
            if not f_cache["clobber"]:
                fails["E2"] += 1
                first.setdefault("E2", f"[{label}] SITE C did not clobber the "
                                       f"recycled block under the cached-`next` "
                                       f"rung -- E2's claim is wrong")
        elif is_self:
            n["E3"] += 1
            if u_cache == r1h:
                fails["E3"] += 1
                first.setdefault("E3", f"[{label}] the cached-`next` rung agrees "
                                       f"with R1h ({r1h}); it would then be a "
                                       f"complete fix and it is not")
        elif ahead:
            n["E5"] += 1
            if not f_cache["stale"]:
                fails["E5"] += 1
                first.setdefault("E5", f"[{label}] the cached-`next` rung did "
                                       f"NOT visit the freed successor")
            elif f_plain["stale"]:
                fails["E5"] += 1
                first.setdefault("E5", f"[{label}] PLAIN R1 visited a freed node "
                                       f"here; DEL_LLIST_ELEMENT's repaired link "
                                       f"should have made it skip")
            elif u_cache == u_plain or u_cache == r1h:
                fails["E5"] += 1
                first.setdefault("E5", f"[{label}] cached={u_cache} agrees with "
                                       f"R1={u_plain} / R1h={r1h}")
        else:
            n["E4"] += 1
            if not (u_plain == u_cache == r1h):
                fails["E4"] += 1
                first.setdefault("E4", f"[{label}] R1={u_plain} cached={u_cache} "
                                       f"R1h={r1h} where the walk frees nothing "
                                       f"ahead of the cursor")

    print(f"E1 must-fire      cached `next` removes the wild walk : "
          f"{n['E1'] - fails['E1']}/{n['E1']}   <- SITE L is FIXED")
    print(f"E2 must-fire      ... and SITE C still clobbers       : "
          f"{n['E1'] - fails['E2']}/{n['E1']}   <- SITE C is NOT")
    print(f"E3 must-fire      ... and the u64 still differs       : "
          f"{n['E3'] - fails['E3']}/{n['E3']}   <- and the ANSWER is NOT")
    print(f"E4 must-NOT-fire  identical where nothing dies ahead  : "
          f"{n['E4'] - fails['E4']}/{n['E4']}")
    print(f"E5 must-fire      ⚠ cached `next` VISITS A FREED NODE : "
          f"{n['E5'] - fails['E5']}/{n['E5']}   <- the hazard it ADDS")
    for k in sorted(first):
        print(f"  {k} first miss: {first[k]}")
    bad = sum(fails.values())
    print(f"\n=== next_cache CONTROL: {'FAIL' if bad else 'PASS'} "
          f"({bad} miss(es)) ===")
    print("\nREAD: the idiom `zend_llist_apply_with_del` already uses fifteen "
          "lines above\nfixes ONE of this row's two dereferences (SITE L, on the "
          "SELF shape) and ADDS a\nnew one (SITE L, on the AHEAD shape), while "
          "leaving SITE C standing in both.\nThe fix upstream shipped -- in a "
          "THIRD function, `user_tick_function_compare` --\nprevents the free, "
          "so it closes every shape at once. The two hardenings are NOT\n"
          "ordered by strength, and that is only visible because this row carries "
          "both sites.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
