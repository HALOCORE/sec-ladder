#!/usr/bin/env python3
"""Generate ph52's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph52-concat-copy-uninit/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel runs one window
    byte 8..   u8[] blob       windows; n_blob = payload_len - 8

A *window* is a stream of `concat_function` calls:

    byte 0..3   u32 LE  n_ops_w   n_ops = n_ops_w % (cap + 1)
    byte 4..7   u32 LE  fold_w    the accumulator's seed
    byte 8..            4 B each  { u8 t1; u8 a1; u8 t2; u8 a2 }
                                  cap = (stride - 8) // 4

and one op is one `$x . $y`, with `t % 5` selecting the arm of
`zend_make_printable_zval`'s switch for that operand and `a` carrying its
payload:

    arm 0  PH52_ARM_STRING  zend.c:190-193  EARLY RETURN, expr_copy UNTOUCHED
    arm 1  PH52_ARM_NULL    zend.c:195-197  len = 0, val = empty_string
    arm 2  PH52_ARM_BOOL    zend.c:199-206  a&1 ? estrndup("1",1) : empty_string
    arm 3  PH52_ARM_ARRAY   zend.c:213-215  estrndup("Array", 5)
    arm 4  PH52_ARM_OBJECT  zend.c:217-252  a&1 ? THE FAULTING ARM : "Object id #a"

⚠⚠⚠ **WHAT "BENIGN" MEANS HERE IS A PROPERTY OF THE CALL HISTORY, NOT OF ANY
FIELD.** ph52's uninitialised datum is a STACK slot -- `zval op1_copy, op2_copy;`
at `Zend/zend_operators.c:1148` -- and `ph52_concat_function` is `noinline`, so op
k+1's slots sit at exactly the offsets op k's did. The state a teardown at
`zend.c:243` finds there is therefore decided by the PREVIOUS op on the SAME
SIDE, and it is one of three things:

    SAFE   `IS_STRING` + `empty_string`, left by arm 1, by arm 2 with `a` even,
           or by the faulting arm itself (which is SELF-DEFUSING).  `zend.h:469
           STR_FREE` skips `empty_string`, so `:243` is DEFINED and costs no
           allocator call.
    DANG   `IS_STRING` + a pointer `zend_operators.c:1188` has already FREED,
           left by arm 2 with `a` odd, by arm 3, or by arm 4 with `a` even.
           `:243` on this state is a DOUBLE FREE.
    PASS   arm 0 does not write the slot at all, so the state is INHERITED.

**THE THREE RULES THE MEASURED CORPUS OBEYS, AND `_check_history()` RE-DERIVES
ALL THREE FROM THE BYTES IT JUST WROTE** (`PROTOCOL_PHP.md` §A2a rule 1):

  R1. No window's op 0 carries the faulting arm on either side. Op 0's
      predecessor is the last op of whichever window ran before -- and on the
      program's very FIRST call it is the C runtime's own leftovers, which are
      measured to be 0 in 12 of 16 build cells and 235 / 94 / 113 / 82 in the
      other 4. A corpus that let `:243` read that would not be reproducible.
  R2. No op presents the faulting arm on side s while side s's state is DANG.
      That is the double free, and it is `inputs/adversarial-dblfree.bin`'s job.
  R3. Every window's LAST op leaves BOTH sides SAFE, so the next window's op 0
      inherits a known state whatever order the driver's `k` visits them in.

⚠ R1 and R3 together are what make the corpus order-independent: the driver's
`k = (acc * nwin) >> 64` is a function of the answers, so a corpus whose meaning
depended on the visit order would be a corpus nobody can reason about.

⚠⚠ **THE ARMS THIS CORPUS MUST REACH**, also re-derived by `_check_history()`:
both arms of the defect's own branch `if (EG(exception))` at `zend.c:242`; all
five lifted arms on BOTH sides; both parities of `a` for arms 2 and 4; and the
object handle's 1-, 2- and 3-digit cases at `:250`. ⭐ And every measured window
carries exactly `cap` ops, so `work_per_call` is affine in the stride with NO
per-window heterogeneity -- which is the thing ph53 had to declare for family B's
sake and this row does not.
"""

import argparse
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common-php"))
sys.path.insert(0, os.path.join(HERE, ".."))
import slb  # noqa: E402
import model  # noqa: E402

OPS_OFF = model.OPS_OFF
OP_BYTES = model.OP_BYTES
NARM = model.NARM
A_STR, A_NULL, A_BOOL, A_ARR, A_OBJ = (model.ARM_STRING, model.ARM_NULL,
                                       model.ARM_BOOL, model.ARM_ARRAY,
                                       model.ARM_OBJECT)

SEED = 0x52C0FFEE

# ⚠ The two strides must differ mod 4, 8 AND 16, or family A's whole-program
# column picks up a stack-alignment artefact instead of a work difference
# (`.memory/03-measurement.md`). `main()` refuses to write otherwise.
SMALL_STRIDE = 74      # cap 16, 2 tail bytes
LARGE_STRIDE = 181     # cap 43, 1 tail byte
SMALL_WINS = 16
LARGE_WINS = 6


def u32(v):
    assert 0 <= v <= 0xFFFFFFFF, v
    return bytes((v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF))


def cap_of(stride):
    return (stride - OPS_OFF) // OP_BYTES


# ---------------------------------------------------------------------------
# the slot-state machine, written ONCE and used by both the generator and the
# checker -- ⚠ deliberately NOT imported from model.py, because the checker's
# job is to be a second opinion about what the bytes mean
# ---------------------------------------------------------------------------
SAFE, DANG, PASS = "SAFE", "DANG", "PASS"


def effect(arm, aux):
    """What this (arm, aux) leaves in the slot it is given, once
    `zend_operators.c:1188` has run."""
    if arm == A_STR:
        return PASS                             # :190-193, never written
    if arm == A_NULL:
        return SAFE                             # :195-197
    if arm == A_BOOL:
        return DANG if (aux & 1) else SAFE      # :202 allocates / :204-205
    if arm == A_ARR:
        return DANG                             # :214 allocates
    return SAFE if (aux & 1) else DANG          # :244-245 / :249 allocates


def faulting(arm, aux):
    """Does this (arm, aux) reach `zend.c:243`?"""
    return arm == A_OBJ and bool(aux & 1)


# ---------------------------------------------------------------------------
# window construction
# ---------------------------------------------------------------------------
def raw_arm(rng, arm):
    """A raw `t` byte whose `% 5` is `arm`, taken past several wraps so a rung
    that read the raw byte instead of the residue would differ."""
    return arm + NARM * rng.randrange(0, 51)        # <= 4 + 250 = 254


def window(rng, stride, ops, fold_w=None):
    """Assemble one window from a list of (arm1, aux1, arm2, aux2)."""
    cap = cap_of(stride)
    assert len(ops) <= cap, (len(ops), cap)
    if fold_w is None:
        fold_w = rng.randrange(0, 1 << 32)
    # `n_ops_w` carries a random multiple of the modulus so the kernel's `%` is
    # exercised rather than being the identity.
    no_w = len(ops) + (cap + 1) * rng.randrange(0, 3)
    out = [u32(no_w), u32(fold_w)]
    for (a1, x1, a2, x2) in ops:
        out.append(bytes((raw_arm(rng, a1), x1, raw_arm(rng, a2), x2)))
    body = b"".join(out)
    assert len(body) == OPS_OFF + OP_BYTES * len(ops)
    return body + bytes(stride - len(body))          # tail padding, never read


#: The (arm, aux) menu the benign generator draws from, tagged with what it
#: needs so the coverage obligations can be satisfied by construction.
MENU = [
    (A_STR, "lit"),
    (A_NULL, "zero"),
    (A_BOOL, "even"),       # empty_string  -> SAFE
    (A_BOOL, "odd"),        # estrndup("1") -> DANG
    (A_ARR, "any"),         # estrndup("Array") -> DANG
    (A_OBJ, "even1"),       # "Object id #N", 1 digit  -> DANG
    (A_OBJ, "even2"),       # ... 2 digits
    (A_OBJ, "even3"),       # ... 3 digits
    (A_OBJ, "odd"),         # THE FAULTING ARM -> SAFE
]


def _aux(rng, kind):
    if kind == "lit":
        return rng.randrange(0, 256)
    if kind == "zero":
        return rng.randrange(0, 256)
    if kind == "even":
        return 2 * rng.randrange(0, 128)
    if kind == "odd":
        return 2 * rng.randrange(0, 128) + 1
    if kind == "any":
        return rng.randrange(0, 256)
    if kind == "even1":
        return 2 * rng.randrange(0, 5)              # 0..8   -> 1 digit
    if kind == "even2":
        return 2 * rng.randrange(5, 50)             # 10..98 -> 2 digits
    if kind == "even3":
        return 2 * rng.randrange(50, 128)           # 100..254 -> 3 digits
    raise AssertionError(kind)


def benign_ops(rng, n_ops):
    """`n_ops` ops obeying R1, R2 and R3, and covering the whole menu on both
    sides. The state machine is simulated AS THE OPS ARE CHOSEN, so an op that
    would break R2 is never emitted rather than filtered afterwards."""
    assert n_ops >= 4, n_ops
    state = [SAFE, SAFE]        # per side; R1 is what lets us start here
    ops = []
    # A deterministic round-robin over the menu, per side, offset so the two
    # sides are not in lock step -- then the last op is forced SAFE/SAFE (R3).
    order1 = list(range(len(MENU)))
    order2 = list(range(len(MENU)))
    rng.shuffle(order1)
    rng.shuffle(order2)
    for i in range(n_ops):
        last = (i == n_ops - 1)
        chosen = []
        for side in (0, 1):
            order = order1 if side == 0 else order2
            for step in range(len(MENU)):
                arm, kind = MENU[order[(i + step + side) % len(MENU)]]
                aux = _aux(rng, kind)
                if i == 0 and faulting(arm, aux):
                    continue                         # R1
                if state[side] == DANG and faulting(arm, aux):
                    continue                         # R2
                if last and effect(arm, aux) != SAFE:
                    continue                         # R3
                break
            else:
                arm, aux = A_NULL, 0                 # always legal
            chosen.append((arm, aux))
            e = effect(arm, aux)
            if e != PASS:
                state[side] = e
        ops.append((chosen[0][0], chosen[0][1], chosen[1][0], chosen[1][1]))
    assert state == [SAFE, SAFE], state
    return ops


def tiled(rng, nwin, stride):
    """`nwin` benign windows, each filled to `cap` ops so the per-call work is
    uniform."""
    cap = cap_of(stride)
    return b"".join(window(rng, stride, benign_ops(rng, cap))
                    for _ in range(nwin))


# ---------------------------------------------------------------------------
# §A2a rule 1: re-derive the coverage from the bytes, and REFUSE to write
# ---------------------------------------------------------------------------
def decode(win):
    """(n_ops, fold_w, ops) from the raw bytes, spelled independently of
    model.unpack so the two are a real cross-check."""
    cap = (len(win) - 8) // 4
    nw = int.from_bytes(win[0:4], "little")
    fw = int.from_bytes(win[4:8], "little")
    n = nw % (cap + 1)
    ops = []
    for o in range(n):
        p = 8 + 4 * o
        ops.append((win[p] % 5, win[p + 1], win[p + 2] % 5, win[p + 3]))
    return n, fw, ops


def _check_history(name, blob, stride):
    """R1/R2/R3 plus the arm coverage. Returns a list of problems."""
    bad = []
    nwin = len(blob) // stride
    cap = (stride - 8) // 4
    arms = {0: set(), 1: set()}
    parities = {A_BOOL: set(), A_OBJ: set()}
    digitcounts = set()
    n_fault = 0
    n_fault_on_safe = 0
    short = []
    for k in range(nwin):
        win = blob[k * stride:(k + 1) * stride]
        n, _fw, ops = decode(win)
        if n != cap:
            short.append((k, n))
        state = [SAFE, SAFE]
        for i, (a1, x1, a2, x2) in enumerate(ops):
            for side, (a, x) in enumerate(((a1, x1), (a2, x2))):
                arms[side].add(a)
                if a in parities:
                    parities[a].add(x & 1)
                if a == A_OBJ and not (x & 1):
                    digitcounts.add(len(str(x)))
                if faulting(a, x):
                    n_fault += 1
                    if i == 0:
                        bad.append(f"{name} window {k}: op 0 side {side} is the "
                                   f"FAULTING arm -- R1. Its predecessor is "
                                   f"another window's last op, or the C "
                                   f"runtime's leftovers on the first call")
                    if state[side] == DANG:
                        bad.append(f"{name} window {k} op {i} side {side}: the "
                                   f"faulting arm on a DANGLING slot -- R2, "
                                   f"i.e. a double free in the measured corpus")
                    elif state[side] == SAFE:
                        n_fault_on_safe += 1
                e = effect(a, x)
                if e != PASS:
                    state[side] = e
        if ops and state != [SAFE, SAFE]:
            bad.append(f"{name} window {k}: ends in state {state}, not "
                       f"[SAFE, SAFE] -- R3, so the next window's op 0 "
                       f"inherits a DANGLING slot")
    if short:
        bad.append(f"{name}: {len(short)} window(s) carry fewer than cap={cap} "
                   f"ops ({short[:3]}), so work_per_call is not affine in the "
                   f"stride")
    for side in (0, 1):
        if arms[side] != set(range(NARM)):
            bad.append(f"{name}: side {side} reaches arms {sorted(arms[side])}, "
                       f"not all {NARM} -- PROTOCOL_PHP.md A2a rule 1")
    for a, want in ((A_BOOL, "zend.c:200"), (A_OBJ, "zend.c:242")):
        if parities[a] != {0, 1}:
            bad.append(f"{name}: arm {a}'s own branch ({want}) takes only "
                       f"{sorted(parities[a])} -- BOTH arms are required")
    if digitcounts != {1, 2, 3}:
        bad.append(f"{name}: the object handle reaches digit counts "
                   f"{sorted(digitcounts)}, not 1, 2 and 3 (zend.c:250)")
    if not n_fault:
        bad.append(f"{name}: `zend.c:243` is NEVER REACHED, so the corpus "
                   f"cannot price the line the upstream fix deletes")
    if not n_fault_on_safe:
        bad.append(f"{name}: `zend.c:243` is never reached on a SAFE slot")
    return bad


def write(name, n_iters, stride, body, declared_len=None):
    path = os.path.join(HERE, name)
    payload = slb.pack_head1_bytes(stride, body)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<5d} "
          f"cap={cap_of(stride):<3d} blob={len(body):<9d} "
          f"windows={len(body) // stride if stride else 0:<6d} "
          f"file={os.path.getsize(path)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()

    for mod in (4, 8, 16):
        if SMALL_STRIDE % mod == LARGE_STRIDE % mod:
            print(f"REFUSING TO WRITE: strides {SMALL_STRIDE}/{LARGE_STRIDE} "
                  f"are both == {SMALL_STRIDE % mod} mod {mod}")
            return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod "
          f"4, 8 and 16; caps {cap_of(SMALL_STRIDE)}/{cap_of(LARGE_STRIDE)}")

    small = tiled(random.Random(SEED + 1), SMALL_WINS, SMALL_STRIDE)
    large = tiled(random.Random(SEED + 2), LARGE_WINS, LARGE_STRIDE)
    problems = (_check_history("small.bin", small, SMALL_STRIDE)
                + _check_history("large.bin", large, LARGE_STRIDE))
    if problems:
        print("REFUSING TO WRITE -- the corpus breaks a history rule or misses "
              "an arm (PROTOCOL_PHP.md A2a rule 1):")
        for p in problems:
            print(f"    {p}")
        return 1
    print("  history + arm coverage ok on both measured inputs")

    write("small.bin", 25_000, SMALL_STRIDE, small)
    write("large.bin", 10_000, LARGE_STRIDE, large)

    # ---- the adversarial four ------------------------------------------
    # n_iters is small: every one of these calls does the same thing and there
    # is nothing to learn from doing it 25 000 times.
    rng = random.Random(SEED + 9)
    S = SMALL_STRIDE

    # (1) THE DEFECT. arm 3 (estrndup("Array")) leaves side 0 DANGLING, then the
    #     faulting arm reads it and `zend.c:243` frees it AGAIN.
    #     ⭐ FULLY DETERMINISTIC, and that is the whole of Deliverable #0: op 0
    #     WRITES the slot rather than reading it, so nothing here depends on the
    #     C runtime's leftovers or on the visit order.
    #     R1 double-frees through the shim and the TALLY MOVES, so the defect is
    #     in the published u64; R1h does not call `:243` at all.
    #     ⚠⚠ `n_iters = 1`, AND IT IS LOAD-BEARING RATHER THAN TIDY. The second
    #     `efree` pushes the SAME header into `cache[1]` twice
    #     (`zend_alloc.c:270-279`), so nothing reaches `free()` during the call;
    #     the NEXT call's `php_shim_reset()` (`emalloc_shim.h:267-269`) then frees
    #     that header twice and glibc aborts with `double free detected in
    #     tcache 2`, exit 134. At `n_iters = 1` there is no next call, R1 runs to
    #     completion, AND THE DEFECT IS IN THE PUBLISHED u64 -- which ph53's
    #     benign corpus structurally could not do. The escalation to SIGABRT is
    #     measured in `controls/dblfree.py` instead, with both n_iters.
    write("adversarial-dblfree.bin", 1, S,
          window(rng, S, [(A_ARR, 4, A_NULL, 0),
                          (A_OBJ, 1, A_NULL, 0)], fold_w=0x11112222))

    # (2) MUST-NOT-FIRE, and it is the control that makes (1) mean something:
    #     the SAME op shape with arm 1 (IS_NULL) in front instead of arm 3, so
    #     `:243` runs on a SAFE slot -- `STR_FREE` skips `empty_string` -- and
    #     nothing is freed twice. Without it, "(1) double-frees" could be "the
    #     faulting arm always double-frees" and the number would not say which.
    #     ⚠ SAME `n_iters` as (1) so the two differ in ONE op byte and nothing
    #     else; `controls/dblfree.py` is where the iteration count varies.
    write("adversarial-safe.bin", 1, S,
          window(rng, S, [(A_NULL, 4, A_NULL, 0),
                          (A_OBJ, 1, A_NULL, 0)], fold_w=0x11112222))

    # (3) the control for both: a stride larger than the blob, so the driver
    #     skips the loop and makes NO kernel call. If this one ever showed a
    #     diagnostic, the diagnostic would not be from the kernel.
    write("adversarial-nowin.bin", 64, S + 64,
          window(rng, S, [(A_NULL, 0, A_NULL, 0), (A_ARR, 2, A_BOOL, 0)]))

    # (4) a declared payload length past the bytes present. The driver must exit
    #     5; nothing about ph52 is involved and that is the point.
    body = window(rng, S, [(A_NULL, 0, A_NULL, 0), (A_ARR, 2, A_BOOL, 0)])
    write("adversarial-trunc.bin", 64, S, body,
          declared_len=8 + len(body) + 4096)

    # ⛔⛔ AND THE ONE THAT IS **NOT** HERE, STATED RATHER THAN LEFT TO BE
    # NOTICED. A window whose op 0 is the faulting arm would make `zend.c:243`
    # read the C runtime's own leftovers on the program's first kernel call --
    # measured as 0 in 12 of 16 build cells and as 235 / 94 / 113 / 82 in the
    # other 4 (../NOTES.md §4). That is a blob whose u64 is not a function of
    # the blob, so it cannot be an `inputs/` file in a tree whose gate compares
    # six rungs' checksums. It lives in `controls/firstcall.py`, which runs it
    # across all 16 cells and reports the spread. That is `.memory-php`'s F31
    # prescription, taken for ONE input rather than for the row.
    return 0


if __name__ == "__main__":
    sys.exit(main())
