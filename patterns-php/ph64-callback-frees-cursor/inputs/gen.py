#!/usr/bin/env python3
"""ph64-callback-frees-cursor: regenerate every `.bin` in this directory.

    python3 patterns-php/ph64-callback-frees-cursor/inputs/gen.py

The `.bin` files are gitignored; this script and the fixed `SEED` are what make
them reproducible byte-for-byte. Nothing here reads `../model.py`: every
assertion below re-derives what it needs from the bytes it just emitted, so a
model bug and a fixture bug cannot cancel.

WHAT A WINDOW IS
================

    [u32 nent][u32 trig][u32 mode][u32 post][ nmax x 4 slot bytes ]

    nmax    = (stride - 16) / 4        n     = 1 + nent % nmax
    trigger = trig % (n + 1)           0 = nobody's callback acts
    mode    = mode % 4                 0 NONE, 1 SELF, 2 AHEAD, 3 BEHIND
    reuse   = (mode >> 16) & 1         one same-size-class emalloc in the callback
    post    = post % (n + 1)           a top-level unregister AFTER the walk

Entry `i`'s tick-function NAME is the 8 bytes `[u32 le i][slot i]` -- the id
half makes names unique BY CONSTRUCTION, so "unregister my own name" cannot
quietly mean somebody else's. That is the exact way `TASK_PHP_031`'s own first
oracle probe was wrong (its report §8.8), and it is closed here by construction
rather than by an assertion.

⚠⚠ WHAT THE MEASURED CORPUS MAY NOT CONTAIN, AND WHY IT IS NOT A RESTRICTION
============================================================================
`mode == SELF` with `1 <= trigger <= n` is the corpus's own trigger and it is
the ONE shape on which R1 and R1h return different u64s -- R1 frees the element
the cursor holds, R1h refuses. `check.py` stage 7h requires R1h to agree with R1
on every non-adversarial input, so that shape lives in `adversarial-*.bin`,
which is where a shape that separates the two rungs belongs. ⭐ EVERYTHING ELSE
IS IN: all four `DEL_LLIST_ELEMENT` arms, deletion during the walk and at top
level, deletion of the entry AHEAD of the cursor (which shortens the list under
it), deletion of the entry BEHIND it, a `post` that names an entry the walk
already removed, and -- deliberately -- the reuse allocation itself, with no
dangerous free beside it. ⚠ That last one is §6.4's S4 control living inside the
measured corpus: the SAME same-size-class `emalloc` the adversarial windows use,
with nothing freed under the cursor, so the divergence those windows show cannot
be the allocation.

⚠ This is NOT the `ph07` situation. `ph07`'s upstream fix changed benign output
on 13.5 % of calls and the row was restricted to hide it, which `TASK_PHP_018`
had to undo. `562f886ecb14` changes benign output on NOTHING: its guard is
`ret && tick_fe1->calling`, and outside a self-unregistration `tick_fe1->calling`
is 0 at every element the comparator ever sees. The exclusion here is of the
ADVERSARIAL shape, not of a region of the benign domain.
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "common-php"))
import slb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 0x5EC1ADDE  # "sec-ladder", fixed forever: the .bin files are gitignored
                   # and must be regenerable byte-for-byte from this file alone.

HEAD = 16          # the four u32 head words
SLOT = 4           # window bytes per registered tick function
UNREG_NONE, UNREG_SELF, UNREG_AHEAD, UNREG_BEHIND = 0, 1, 2, 3

SMALL_STRIDE, SMALL_WINS = 552, 32
LARGE_STRIDE, LARGE_WINS = 4074, 2050
RESIDUE_MODULI = (4, 8, 16)

# ⚠ THE WILD POINTER, AND IT IS CHOSEN TO BE NON-CANONICAL RATHER THAN MERELY
# UNMAPPED. On the reuse path the callback's own allocation pops the just-freed
# element straight back out and fills it with the entry's name bytes, so
# `element->next` becomes `[u32 le id][slot]` read as a little-endian pointer.
# With `slot = 00 00 01 00` that is `0x0001_0000_0000_00id`: bit 48 set and bit
# 47 clear, i.e. NON-CANONICAL on x86-64, which faults on the first dereference
# whatever the process happens to have mapped. An "unmapped" address is a
# property of the run; a non-canonical one is a property of the architecture,
# and only the second makes `adversarial-*.bin` deterministic.
WILD_SLOT = bytes((0x00, 0x00, 0x01, 0x00))

# (n as a fraction of nmax, mode, trigger, post, reuse). Cycled by window index.
# ⚠ A fraction of 0.00 means n == 1 EXACTLY, and it is spelled that way rather
# than as a small fraction because `round(nmax * 0.01)` is 1 at nmax = 134 and
# **10** at nmax = 1014 -- so the `only` arm was reached on small.bin and missed
# on large.bin, and `_check_span` caught it. A fixture parameter that means one
# thing at one stride and another at another is not a parameter.
# Every entry exists to reach something `_check_span` asserts; the comment says
# which.
PROFILES = (
    (1.00, UNREG_NONE,   "none",   "none",  0),   # the pure walk, no deletion
    (0.90, UNREG_NONE,   "none",   "head",  0),   # DEL arm: head
    (0.85, UNREG_NONE,   "none",   "tail",  0),   # DEL arm: tail
    (0.80, UNREG_NONE,   "none",   "mid",   0),   # DEL arm: mid
    (0.75, UNREG_AHEAD,  "mid",    "none",  0),   # delete AHEAD of the cursor
    (0.70, UNREG_AHEAD,  "mid",    "head",  1),   # ... + reuse + a post delete
    (0.65, UNREG_BEHIND, "mid",    "tail",  0),   # delete BEHIND the cursor
    (0.60, UNREG_BEHIND, "mid",    "mid",   1),
    (0.55, UNREG_AHEAD,  "head",   "tail",  1),   # cursor at the head
    (0.50, UNREG_AHEAD,  "penult", "none",  0),   # AHEAD from n-1 deletes the TAIL
    (0.45, UNREG_BEHIND, "second", "none",  1),   # BEHIND from 2 deletes the HEAD
    (0.40, UNREG_NONE,   "none",   "none",  1),   # ⭐ reuse with NO free at all
    (0.00, UNREG_NONE,   "none",   "head",  0),   # ⭐ n == 1 -> DEL arm: only
    (0.00, UNREG_AHEAD,  "head",   "head",  1),   # ⭐ n == 1, AHEAD is a no-op
    (0.35, UNREG_AHEAD,  "mid",    "ahead", 0),   # post names an already-deleted id
    (0.30, UNREG_BEHIND, "tail",   "none",  1),   # cursor at the tail
)


def rng_for(name):
    """One INDEPENDENT stream per output file, so that an edit to `small`'s
    shape does not silently rewrite every adversarial blob."""
    return random.Random(f"{SEED:x}:{name}")


def _u32(v):
    return (v & 0xFFFFFFFF).to_bytes(4, "little")


def _pick(kind, n, trigger):
    """Resolve a trigger/post KIND to an id in `0 ..= n`."""
    if kind == "none":
        return 0
    if kind == "head":
        return 1
    if kind == "second":
        return 2 if n >= 2 else 1
    if kind == "penult":
        return n - 1 if n >= 2 else 1
    if kind == "tail":
        return n
    if kind == "mid":
        return (n + 1) // 2
    if kind == "ahead":                 # the entry the walk's AHEAD just removed
        return trigger + 1 if trigger and trigger < n else 0
    raise AssertionError(kind)


def window(rng, stride, idx):
    nmax = (stride - HEAD) // SLOT
    frac, mode, tk, pk, reuse = PROFILES[idx % len(PROFILES)]
    n = max(1, min(nmax, int(round(nmax * frac))))
    trigger = _pick(tk, n, 0)
    post = _pick(pk, n, trigger)
    assert 0 <= trigger <= n and 0 <= post <= n

    # Head words that DECODE to exactly those, with the bits the kernel does not
    # look at drawn from the stream -- so a rung that read a different bit of a
    # head word would not accidentally agree.
    nent = (n - 1) + nmax * rng.randrange(0, 3)
    trig_w = trigger + (n + 1) * rng.randrange(0, 3)
    post_w = post + (n + 1) * rng.randrange(0, 3)
    mode_w = mode | (reuse << 16) | (rng.randrange(0, 1 << 14) << 2)

    win = bytearray(_u32(nent) + _u32(trig_w) + _u32(mode_w) + _u32(post_w))
    win += bytes(rng.randrange(256) for _ in range(stride - HEAD))
    assert len(win) == stride, (len(win), stride)
    return bytes(win)


def tiled(rng, nwin, stride):
    return b"".join(window(rng, stride, i) for i in range(nwin))


# ---------------------------------------------------------------------------
# THE ASSERTIONS. Everything below re-derives from the emitted bytes.
# ---------------------------------------------------------------------------
def _rd32(b, i):
    return b[i] | (b[i + 1] << 8) | (b[i + 2] << 16) | (b[i + 3] << 24)


def _decode(win, stride):
    nmax = (stride - HEAD) // SLOT
    n = 1 + (_rd32(win, 0) % nmax)
    return (n, _rd32(win, 4) % (n + 1), _rd32(win, 8) % 4,
            (_rd32(win, 8) >> 16) & 1, _rd32(win, 12) % (n + 1))


def _arm(target, live):
    """Which of `DEL_LLIST_ELEMENT`'s four arms deleting `target` takes, derived
    from LIST POSITIONS rather than from pointers -- `zend_llist.c:74-83`:

        prev? -> prev->next = next        else -> l->head = next
        next? -> next->prev = prev        else -> l->tail = prev

    so the arm is decided by whether a live entry precedes and follows it."""
    before = any(x < target for x in live)
    after = any(x > target for x in live)
    return ("mid" if after else "tail") if before else ("head" if after else "only")


def _schedule(n, trigger, mode, post):
    """The deletions a window makes UNDER R1h, and the arm each one takes.

    ⚠ `SELF` is REFUSED by `562f886ecb14`, so it deletes nothing -- which is why
    a measured corpus may carry every other mode."""
    live = set(range(1, n + 1))
    arms, walk_del = [], 0
    if 1 <= trigger <= n:
        if mode == UNREG_AHEAD and trigger < n:
            walk_del = trigger + 1
        elif mode == UNREG_BEHIND and trigger > 1:
            walk_del = trigger - 1
    if walk_del:
        arms.append(_arm(walk_del, live))
        live.discard(walk_del)
    post_del = post if (post and post in live) else 0
    if post_del:
        arms.append(_arm(post_del, live))
        live.discard(post_del)
    skipped = walk_del if walk_del > trigger else 0
    return arms, walk_del, post_del, skipped


def _check_residues():
    """The two measured strides must differ modulo every modulus that has
    bitten this project. p01's first draft used 500 and 4096, both == 0 (mod 4),
    the single worst residue for R2, and overstated the delta 2.4x."""
    bad = []
    for m in RESIDUE_MODULI:
        if SMALL_STRIDE % m == LARGE_STRIDE % m:
            bad.append(f"small and large strides ({SMALL_STRIDE}, "
                       f"{LARGE_STRIDE}) are both == {SMALL_STRIDE % m} "
                       f"(mod {m}); pick strides of different parity or the "
                       f"delta published is one residue wearing the label of a "
                       f"constant")
    return bad


def _check_span(name, blob, stride):
    """⚠⚠⚠ THE MUST-FIRE ASSERTION -- `PROTOCOL_PHP.md` §A2a rule 1.

    A benign corpus must REACH every arm of the branch the defect lives on and
    must SAY SO mechanically. Refuses to write a corpus that misses any of:

      * ⭐ any of `DEL_LLIST_ELEMENT`'s FOUR arms. They are not interchangeable:
        the `tail` arm's `element->next` is NULL, so a recycled block CREATES a
        successor where the loop would have ended, and the `only` arm needs a
        one-entry list, which a corpus of long lists never produces;
      * a deletion DURING the walk and a deletion at top level;
      * a deletion of the entry AHEAD of the cursor -- the one case where the
        list shortens under a live cursor and `zend_llist_apply` has to survive
        it;
      * a deletion of the entry BEHIND it;
      * a `post` that names an entry the walk already deleted, so
        `zend_llist_del_element` scans the WHOLE list and matches nothing;
      * the reuse allocation both ON and OFF;
      * `trigger == 0`, i.e. a walk in which no callback touches the list;
      * `n == 1` and `n == nmax`, the two ends of the head word's range;

    and refuses one on which R1 and R1h could differ -- `mode == SELF` with a
    live trigger -- because that is the adversarial case, not a measured one.
    """
    nmax = (stride - HEAD) // SLOT
    arms, modes = set(), set()
    walk_dels = post_dels = ahead = behind = stale_post = 0
    reuse_on = reuse_off = quiet = n1 = nfull = 0
    self_live = []
    nmin, nmax_seen, ntot = 10 ** 9, 0, 0
    nwin = len(blob) // stride
    for i in range(nwin):
        win = blob[i * stride:(i + 1) * stride]
        n, trigger, mode, reuse, post = _decode(win, stride)
        a, walk_del, post_del, _ = _schedule(n, trigger, mode, post)
        arms |= set(a)
        modes.add(mode)
        walk_dels += walk_del != 0
        post_dels += post_del != 0
        ahead += (mode == UNREG_AHEAD and walk_del != 0)
        behind += (mode == UNREG_BEHIND and walk_del != 0)
        stale_post += (post != 0 and post_del == 0)
        reuse_on += reuse == 1
        reuse_off += reuse == 0
        quiet += trigger == 0
        n1 += n == 1
        nfull += n == nmax
        nmin, nmax_seen, ntot = min(nmin, n), max(nmax_seen, n), ntot + n
        if mode == UNREG_SELF and 1 <= trigger <= n:
            self_live.append(i)
    bad = []
    missing = sorted({"mid", "head", "tail", "only"} - arms)
    if missing:
        bad.append(f"{name}: DEL_LLIST_ELEMENT arms {missing} are never reached "
                   f"(got {sorted(arms)}). PROTOCOL_PHP.md A2a rule 1: the "
                   f"fixture must reach EVERY arm of the branch the defect "
                   f"lives on, and `only` in particular needs a ONE-ENTRY list")
    for want, got, what in ((1, walk_dels, "a deletion DURING the walk"),
                            (1, post_dels, "a top-level deletion after it"),
                            (1, ahead, "a deletion of the entry AHEAD of the "
                                       "cursor"),
                            (1, behind, "a deletion of the entry BEHIND it"),
                            (1, stale_post, "a `post` naming an entry the walk "
                                            "already removed"),
                            (1, reuse_on, "a window with the reuse allocation "
                                          "ON"),
                            (1, reuse_off, "a window with it OFF"),
                            (1, quiet, "a window where no callback acts"),
                            (1, n1, "a ONE-ENTRY list"),
                            (1, nfull, "a FULL list (n == nmax)")):
        if got < want:
            bad.append(f"{name}: no window has {what}")
    if self_live:
        bad.append(
            f"{name}: {len(self_live)} window(s) (first {self_live[0]}) have "
            f"`mode == SELF` with a live trigger. That is the row's own trigger: "
            f"R1 frees the element the cursor holds and R1h refuses, so the two "
            f"return different u64s and check.py stage 7h requires them to "
            f"agree on every non-adversarial input. inputs/adversarial-*.bin is "
            f"where those live")
    print(f"  span ok: {name:26s} windows={nwin:<5d} nmax={nmax:<5d} "
          f"n={nmin}..{nmax_seen} (mean {ntot // max(nwin, 1)}) "
          f"arms={sorted(arms)} modes={sorted(modes)} walk_del={walk_dels} "
          f"post_del={post_dels} stale_post={stale_post} reuse={reuse_on}/"
          f"{reuse_off} quiet={quiet} n==1:{n1} n==nmax:{nfull}")
    return bad


def adv(stride, n, trigger, mode, post, reuse, wild=False, rng=None):
    """ONE window, no slack. `stride == n_blob`, so `nwin == 1` and the driver's
    window index is always 0 -- a hostile window that is never selected would
    declare a sanitizer expectation nothing exercises."""
    nmax = (stride - HEAD) // SLOT
    assert 1 <= n <= nmax, (n, nmax)
    win = bytearray(_u32(n - 1) + _u32(trigger)
                    + _u32(mode | (reuse << 16)) + _u32(post))
    body = bytearray()
    for i in range(1, nmax + 1):
        if wild and i == trigger:
            body += WILD_SLOT
        elif rng is not None:
            body += bytes(rng.randrange(256) for _ in range(SLOT))
        else:
            body += bytes(((i * 7) & 0xFF, (i * 13) & 0xFF, (i * 29) & 0xFF, 0))
    win += body
    win += bytes(stride - len(win))
    assert len(win) == stride
    return bytes(win)


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:32s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def main():
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

    print("ph64 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod "
          + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 32 windows x 552 B = 17.3 KiB, inside this box's 32 KiB L1.
    small = tiled(rng_for("small"), SMALL_WINS, SMALL_STRIDE)
    # large: 2050 windows x 4074 B = 8.0 MiB, 8x this box's 1 MiB L2, so the
    # window the driver picks is a cold walk every call.
    large = tiled(rng_for("large"), LARGE_WINS, LARGE_STRIDE)
    problems = (_check_span("small.bin", small, SMALL_STRIDE)
                + _check_span("large.bin", large, LARGE_STRIDE))
    for p in problems:
        print("gen.py: " + p, file=sys.stderr)
    if problems:
        return 1
    write("small.bin", 1_500, SMALL_STRIDE, small)
    write("large.bin", 200, LARGE_STRIDE, large)

    # ---- adversarial: a tick function that unregisters ITSELF ---------------
    # n_iters is small: R1 executes undefined behaviour on four of these and
    # there is nothing to learn from doing it 3 000 times.

    # (1) ⭐ THE ROW'S OWN TRIGGER, AND IT IS SILENT. `mode == SELF` with no
    #     reuse: R1 frees the element the cursor holds, the 40-byte block goes
    #     into `AG(cache)[5]` instead of back to malloc, NOTHING scribbles the
    #     payload, and `element->next` still reads the true successor. The walk
    #     visits every remaining entry exactly once and no detector says a word
    #     -- and the u64 STILL differs, because `l->count`, the dtor count, the
    #     refusal count and all four allocator counters record a free that R1h
    #     refuses to make. THIS CELL IS THE ROW'S EXPLANATION: it is what
    #     `crashes_pristine_5_0_0 = False` is, and it is why the oracle has to
    #     be in the checksum. `sanitizer_expect` is `clean` here and that is a
    #     finding, not a gap.
    win = adv(552, n=8, trigger=4, mode=UNREG_SELF, post=0, reuse=0)
    write("adversarial-selfunreg.bin", 8, len(win), win)

    # (2) THE SAME FREE, MADE VISIBLE. One same-size-class `emalloc` inside the
    #     same callback -- what any PHP tick function does with any small
    #     allocation -- LIFO-pops the just-freed element straight back out, so
    #     the callback's own name bytes land in `element->next` and the walk
    #     FOLLOWS them. Middle of the list: DEL_LLIST_ELEMENT's `mid` arm.
    win = adv(552, n=8, trigger=4, mode=UNREG_SELF, post=0, reuse=1, wild=True)
    write("adversarial-reuse-mid.bin", 8, len(win), win)

    # (3) the `head` arm -- `l->head = current->next`.
    win = adv(552, n=8, trigger=1, mode=UNREG_SELF, post=0, reuse=1, wild=True)
    write("adversarial-reuse-head.bin", 8, len(win), win)

    # (4) the `tail` arm -- `l->tail = current->prev`. ⭐ This one is different
    #     in kind: `element->next` was NULL and the loop would have ENDED, so
    #     the recycled block CREATES a successor. The walk runs off the end of a
    #     list it has already finished.
    win = adv(552, n=8, trigger=8, mode=UNREG_SELF, post=0, reuse=1, wild=True)
    write("adversarial-reuse-tail.bin", 8, len(win), win)

    # (5) the `only` arm -- a ONE-ENTRY list, so neither `prev` nor `next`
    #     exists and the list is emptied under the cursor.
    win = adv(552, n=1, trigger=1, mode=UNREG_SELF, post=0, reuse=1, wild=True)
    write("adversarial-reuse-only.bin", 8, len(win), win)

    # (6) The degenerate shape: `stride > n_blob`, so the driver's guard skips
    #     the loop entirely rather than entering and breaking out of it (which
    #     would put a branch in the measured loop). Every rung prints 0 after
    #     zero kernel calls. This is the control for (1)-(5): the same driver,
    #     the same blob shape, no kernel call at all, declared clean.
    win = adv(552, n=8, trigger=4, mode=UNREG_SELF, post=0, reuse=1, wild=True)
    write("adversarial-nowin.bin", 8, len(win) + 1, win)
    return 0


if __name__ == "__main__":
    sys.exit(main())
