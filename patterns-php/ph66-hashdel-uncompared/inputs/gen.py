#!/usr/bin/env python3
"""ph66-hashdel-uncompared -- regenerate `inputs/*.bin`.

    python3 patterns-php/ph66-hashdel-uncompared/inputs/gen.py

Deterministic: same seed, same bytes. The `.bin` files are gitignored artefacts
and THIS FILE is the generator (`CLAUDE.md` "Don't" rule 1).

============================================================================
THE RECORD, AND THE ONE INVARIANT THE BENIGN CORPUS MUST KEEP
============================================================================
Four bytes: `ctl`, `sel`, payload low, payload high. `ctl` carries three
independent bits -- op (insert/delete), kind (string key/numeric index) and
`coll`. ⭐ `coll` is the trigger: it makes the record's numeric index be
`zend_inline_hash_func(key_of(sel), nKeyLength)`, which is the value
`_zend_hash_index_update_or_next_insert` stores verbatim in `p->h`, so the
numeric bucket and the string key collide by CONSTRUCTION and no preimage is
needed (`.tasks-php/probes/ph66_djbx33a_collide.py`).

⛔⛔ **THE MEASURED CORPUS MUST NOT REACH THE DEFECT, AND THIS FILE IS WHERE
THAT IS ENFORCED.** `check.py` stage 7h requires R1 and R1h to return the same
u64 on every NON-adversarial input -- *"R1 and R1h must agree wherever the bug is
not exercised, or the R1-vs-R1h cost comparison is between two different
programs"*. So `small.bin` and `large.bin` are built under a partition:

    S = sel 0..31    may be DELETED by string key
    C = sel 32..63   may be used as a COLLIDING index

and no `coll` record ever names a sel in S. Because the 64 keys' hashes are
pairwise distinct AND all above 255 (`_check_keys` asserts both), a string-key
delete of `key_of(s)` for `s in S` can never meet a numeric bucket: every
numeric bucket's `h` is either a plain index in 0..255 or `hash(key_of(c))` for
some `c in C`. ⭐ That is a DERIVATION, and `_check_benign` re-derives it the
other way round -- by running the model's R1 and R1h over every window and
requiring them equal -- so neither the argument nor the check stands alone.

============================================================================
ARM COVERAGE -- PROTOCOL_PHP.md A2a rule 1
============================================================================
A random stream reaches most arms most of the time, which is exactly the
failure `ph03` shipped for a whole task. Every window therefore opens with a
PROLOGUE that reaches each arm by construction, and `_check_arms` then asserts
the arms are reached by the calls the driver ACTUALLY MAKES (windows are picked
from a checksum-derived index, so an arm in an unvisited window is not reached).

The prologue's last three records are the interesting one:

    ins_idx  coll c      a NUMERIC bucket at h = hash(key_of(c))
    ins_str  c           a STRING bucket with the SAME h, now at the chain HEAD
    del_idx  coll c      an INDEX delete that must WALK PAST the string bucket

⭐ It is benign on both rungs and it is the shape the repair is about: two
buckets with equal `h` and different KIND in one chain. `nKeyLength` spans 3..10
across the 64 keys, so `zend_inline_hash_func`'s unrolled `>= 8` arm and its
`switch` tail are both driven.
"""

import argparse
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common-php"))
sys.path.insert(0, os.path.join(HERE, ".."))
import slb    # noqa: E402
import model  # noqa: E402

REC = model.REC
NKEY = model.NKEY
SEED = 0x50D3

#: ⚠ Neither stride is a multiple of REC, so every window ends in a trailing
#: partial record nothing may consume; and they differ mod 4, 8 and 16, so no
#: alignment residue is shared. ⛔ They are also GENUINELY DIFFERENT SIZES --
#: `ph64` shipped `small.bin` and `large.bin` both at 9 bytes, one draw sampled
#: twice, which silently weakened every two-input argument that row made
#: (F119/M4).
SMALL_STRIDE, SMALL_WINS = 66, 24
LARGE_STRIDE, LARGE_WINS = 517, 60

S_LO, S_HI = 0, 31      # sels that may be DELETED by string key
C_LO, C_HI = 32, 63     # sels that may be used as a COLLIDING index


def rec(op, kind, coll, sel, val=0x2A):
    return bytes([(op & 1) | ((kind & 1) << 1) | ((coll & 1) << 2),
                  sel & 0xFF, val & 0xFF, (val >> 8) & 0xFF])


def prologue(rng):
    """Records that reach every arm of the container, by construction."""
    s1 = rng.randint(S_LO, S_HI)
    s2 = rng.randint(S_LO, S_HI)
    c1 = rng.randint(C_LO, C_HI)
    pi = rng.randint(0, 255)
    return (
        rec(0, 0, 0, s1, 0x11)          # ins_str, new
        + rec(0, 0, 0, s1, 0x12)        # ins_str, UPDATE arm
        + rec(0, 1, 0, pi, 0x13)        # ins_idx plain, new
        + rec(0, 1, 0, pi, 0x14)        # ins_idx plain, UPDATE arm
        + rec(1, 0, 0, s2)              # del_str that MISSES
        + rec(0, 0, 0, s2, 0x15)        # ins_str s2
        + rec(1, 0, 0, s2)              # del_str that HITS via memcmp
        + rec(0, 1, 1, c1, 0x16)        # ins_idx COLLIDING -> a numeric bucket
        + rec(0, 0, 0, c1, 0x17)        # ins_str with the SAME h, at the head
        + rec(1, 1, 1, c1)              # del_idx that WALKS PAST it
        + rec(1, 1, 0, pi)              # del_idx plain that HITS
    )


def filler(rng, n):
    """`n` benign records: string ops only on S, `coll` only on C."""
    out = bytearray()
    for _ in range(n):
        kind = rng.randint(0, 1)
        op = rng.randint(0, 1)
        val = rng.randint(0, 0xFFFF)
        if kind == 0:                                   # string key
            # a string INSERT may name any sel; a string DELETE only S.
            sel = rng.randint(S_LO, S_HI) if op == 1 \
                else rng.randint(0, NKEY - 1)
            out += rec(op, 0, 0, sel, val)
        else:
            coll = rng.randint(0, 1)
            if coll:
                out += rec(op, 1, 1, rng.randint(C_LO, C_HI), val)
            else:
                out += rec(op, 1, 0, rng.randint(0, 255), val)
    return bytes(out)


def window(rng, stride):
    nrec = stride // REC
    pro = prologue(rng)
    assert len(pro) // REC <= nrec, "prologue does not fit in the window"
    body = pro + filler(rng, nrec - len(pro) // REC)
    return body + bytes(rng.randint(1, 255) for _ in range(stride - len(body)))


def tiled(rng, nwins, stride):
    return b"".join(window(rng, stride) for _ in range(nwins))


# ==========================================================================
# the refusals
# ==========================================================================
def _check_keys():
    """The 64 keys: distinct, distinct hashes, all hashes out of the plain-index
    range and inside `long`, all bytes positive, and `nKeyLength` straddling 8."""
    bad = []
    keys = [model.key_of(s) for s in range(NKEY)]
    hs = [model.djbx33a(k) for k in keys]
    if len(set(keys)) != NKEY:
        bad.append(f"the {NKEY} keys are not pairwise distinct "
                   f"({len(set(keys))} distinct)")
    if len(set(hs)) != NKEY:
        bad.append(f"the {NKEY} key hashes are not pairwise distinct "
                   f"({len(set(hs))} distinct) -- `coll` would then name two "
                   f"keys' bucket at once and the partition below is unsound")
    if min(hs) <= 255:
        bad.append(f"key hash {min(hs)} is inside the PLAIN INDEX range 0..255, "
                   f"so a plain numeric bucket could collide with a string key "
                   f"and the benign corpus would reach the defect")
    if max(hs) >= (1 << 63):
        bad.append(f"key hash {max(hs)} is >= 2^63, so "
                   f"`(long)h >= (long)ht->nNextFreeElement` at zend_hash.c:401 "
                   f"reads it NEGATIVE -- a real 5.0.0 behaviour, but one this "
                   f"row does not model and must not reach by accident")
    lens = {len(k) for k in keys}
    if min(lens) > 7 or max(lens) < 8:
        bad.append(f"nKeyLength range {sorted(lens)} does not straddle 8, so "
                   f"one of zend_inline_hash_func's two arms is dead")
    for k in keys:
        if any(b > 127 for b in k):
            bad.append(f"key {k!r} has a byte above 127; `*arKey` is a SIGNED "
                       f"char on x86-64 and the rungs would have to agree on "
                       f"sign extension")
            break
    return bad


def _check_benign(name, body, stride):
    """R1 and R1h must agree on EVERY window -- not merely on the visited ones.

    ⛔ This is the half `check.py` stage 7h would catch late and expensively;
    catching it here is the point of a generator that refuses."""
    bad = []
    nw = len(body) // stride
    for k in range(nw):
        win = body[k * stride:(k + 1) * stride]
        a = model.simulate(win, hardened=False)
        b = model.simulate(win, hardened=True)
        if a != b:
            bad.append(f"{name}: window {k} REACHES THE DEFECT -- R1={a} "
                       f"R1h={b}. A measured input must not.")
            break
    return bad


def _check_arms(name, path, adversarial):
    """Run the model's own arm census over the calls the DRIVER makes."""
    m = model.build(path)
    bad = [f"{name}: {p}" for p in m.selfcheck()]
    if not adversarial and m.checksum is None:
        bad.append(f"{name}: no checksum")
    return bad


def write(name, n_iters, stride, body, declared_len=None):
    path = os.path.join(HERE, name)
    payload = slb.pack_head1_bytes(stride, body)
    slb.write(path, n_iters, payload, declared_len)
    nw = len(body) // stride if stride else 0
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<6d} "
          f"blob={len(body):<8d} windows={nw:<5d} recs/win={stride // REC:<4d} "
          f"table={model.table_size(stride // REC):<5d} "
          f"file={os.path.getsize(path)}")
    return path


def adv_window(stride, recs):
    """One window exactly, so the checksum-derived index cannot avoid it."""
    body = b"".join(recs)
    assert len(body) <= stride, f"{len(body)} > {stride}"
    return body + bytes(((i * 37) % 255) + 1 for i in range(stride - len(body)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()

    problems = _check_keys()
    if problems:
        print("REFUSING TO WRITE -- the key alphabet is unsound:")
        for p in problems:
            print(f"    {p}")
        return 1
    print(f"  key alphabet ok: {NKEY} distinct keys, {NKEY} distinct hashes, "
          f"min hash {min(model.djbx33a(model.key_of(s)) for s in range(NKEY))}, "
          f"nKeyLength "
          f"{sorted({len(model.key_of(s)) for s in range(NKEY)})}")

    for mod_ in (4, 8, 16):
        if SMALL_STRIDE % mod_ == LARGE_STRIDE % mod_:
            print(f"REFUSING TO WRITE: strides {SMALL_STRIDE}/{LARGE_STRIDE} "
                  f"are both == {SMALL_STRIDE % mod_} mod {mod_}")
            return 1
    if SMALL_STRIDE % REC == 0 or LARGE_STRIDE % REC == 0:
        print(f"REFUSING TO WRITE: a stride that is a multiple of {REC} carries "
              f"no trailing partial record, so nothing checks that a rung stops "
              f"at `nrec`")
        return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod 4, "
          f"8 and 16, and neither is a multiple of {REC}")

    small = tiled(random.Random(SEED + 1), SMALL_WINS, SMALL_STRIDE)
    large = tiled(random.Random(SEED + 2), LARGE_WINS, LARGE_STRIDE)
    problems = (_check_benign("small.bin", small, SMALL_STRIDE)
                + _check_benign("large.bin", large, LARGE_STRIDE))
    if problems:
        print("REFUSING TO WRITE -- a measured input reaches the defect:")
        for p in problems:
            print(f"    {p}")
        return 1
    print("  benign ok: R1 == R1h on every window of both measured inputs")

    paths = [write("small.bin", 20_000, SMALL_STRIDE, small),
             write("large.bin", 2_500, LARGE_STRIDE, large)]

    # ---- the adversarial five -------------------------------------------
    st = SMALL_STRIDE
    s, c = 3, 3   # one selector, so the string key and the index really collide

    # ⭐⭐⭐ CELL D. The string key is inserted FIRST, so the colliding numeric
    # bucket ends up at the chain HEAD and `unset($a["..."])` destroys IT.
    # BOTH HALVES WRONG AT ONCE: the key you named survives, the key you never
    # named dies, and the kernel returns normally.
    paths.append(write("adversarial-celld.bin", 64, st, adv_window(st, [
        rec(0, 0, 0, s, 0xABC),      # $a['key'] = ...
        rec(0, 1, 1, c, 0xDEF),      # $a[hash('key')] = ...
        rec(1, 0, 0, s),             # unset($a['key'])  <- destroys the INDEX
        rec(0, 1, 0, 9, 0x111),      # a bystander, so the fold has company
    ])))

    # CELL A. Only the numeric bucket is present; the string-key delete
    # destroys it and reports SUCCESS for a key that was never there.
    paths.append(write("adversarial-cella.bin", 64, st, adv_window(st, [
        rec(0, 1, 1, c, 0xDEF),
        rec(0, 1, 0, 9, 0x111),
        rec(1, 0, 0, s),
    ])))

    # DEEP. The colliding numeric bucket is buried under several same-slot
    # buckets, so the defect fires at the END of a walk rather than at its head.
    # ⚠ The bystanders are PLAIN indices congruent to the victim's slot, chosen
    # from the table size the stride implies -- a string key with the victim's
    # own hash would sit AHEAD of it in the chain and the delete would find the
    # right bucket, which is `adversarial-orderctl`'s job and not this file's.
    slot = model.djbx33a(model.key_of(c)) & (model.table_size(st // REC) - 1)
    deep = [rec(0, 1, 1, c, 0x100)]
    deep += [rec(0, 1, 0, slot + 16 * j, 0x200 + j) for j in range(1, 7)]
    deep += [rec(1, 0, 0, s)]
    paths.append(write("adversarial-deep.bin", 64, st, adv_window(st, deep)))

    # ⭐ ORDERCTL -- the MUST-NOT-FIRE adversarial input, and the row needs one.
    # The SAME two keys in the OTHER order: the string key is inserted LAST, so
    # it is at the chain head and the string-key delete finds the bucket it
    # named. R1 and R1h agree here, which is what makes "the blob selects WHICH
    # element dies, never WHETHER a fault occurs" a measured statement.
    paths.append(write("adversarial-orderctl.bin", 64, st, adv_window(st, [
        rec(0, 1, 1, c, 0xDEF),
        rec(0, 0, 0, s, 0xABC),
        rec(1, 0, 0, s),
        rec(0, 1, 0, 9, 0x111),
    ])))

    # MANY. Several colliding pairs at once, so one window destroys several
    # unrelated elements and the surviving-key fold moves by more than one entry.
    many = []
    for sel in (2, 5, 11, 23):
        many.append(rec(0, 0, 0, sel, 0x300 + sel))
        many.append(rec(0, 1, 1, sel, 0x400 + sel))
    for sel in (2, 5, 11, 23):
        many.append(rec(1, 0, 0, sel))
    paths.append(write("adversarial-many.bin", 64, st, adv_window(st, many)))

    # The control: a stride larger than the blob, so the kernel is never called.
    paths.append(write("adversarial-nowin.bin", 64, 4096,
                       adv_window(st, [rec(1, 0, 0, s)])))

    problems = []
    for p in paths:
        base = os.path.basename(p)
        problems += _check_arms(base, p, base.startswith("adversarial"))
    # ⛔ THE DEFECT-ARM RULE HAS ONE DECLARED EXEMPTION AND IT IS NOT BY NAME:
    # `adversarial-orderctl.bin` exists to show the defect NOT firing on the
    # same two keys in the other order, and `adversarial-nowin.bin` makes no
    # call at all. Both are checked HERE, positively, rather than being excused.
    for nm, want_defect in (("adversarial-orderctl.bin", False),
                            ("adversarial-nowin.bin", False)):
        mm = model.build(os.path.join(HERE, nm))
        if mm.any_defect != want_defect:
            problems.append(f"{nm}: any_defect={mm.any_defect}, want "
                            f"{want_defect}")
        problems = [q for q in problems
                    if not (q.startswith(nm) and "defect arm" in q)]
    if problems:
        print("REFUSING THE CORPUS -- the model's own census objects "
              "(PROTOCOL_PHP.md A2a):")
        for q in problems:
            print(f"    {q}")
        return 1
    print("  arm coverage ok on every input, and every adversarial input "
          "reaches the defect arm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
