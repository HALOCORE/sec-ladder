#!/usr/bin/env python3
"""Generate p27's control rungs by exact-string substitution on the shipped ones.

Every control is a NAMED, SINGLE-LEVER edit of a shipped rung, produced by an
exact-string replacement so that a reviewer can see what moved without reading a
second copy of the kernel (`.memory/02-bench-rules.md`). The substitutions are
asserted to fire: a lever that silently matched nothing would look like a
measured null.

    python3 patterns/p27-handle-table/controls/gen_controls.py [--out DIR]

Defaults to `.temp/p27/controls/`. The generated `.rs` are re-derivable and are
deleted once the measurements are green; this file is the evidence.

THE CONTROLS, and what each is for:

  r4_tabchecked   R4 with the handle table indexed CHECKED (`tab[h]`,
                  `live[h]`) instead of through `arr_get_unchecked` /
                  `arr_set_unchecked`. **This is the shipped rung's earlier
                  draft**, and it is here because the draft asserted -- without
                  measuring -- that `h < ntab` plus `ntab <= TABCAP` already
                  deletes rustc's check. It does not: three
                  `panic_bounds_check` sites survive at -O3 and the lever is
                  worth 41.70 Ir/call on small (../NOTES.md 4). It is NOT an
                  admissible R4, and it is not offered as one; it is the
                  measurement that justifies two trusted items.

  r4_bufchecked   R4 with the WINDOW read checked (`buf_get_unchecked`'s body
                  becomes `v[i]`) and the table left unchecked. The second of
                  the two U-license levers.

  r4_allchecked   R4 with BOTH checked -- **zero U-license trusted items**, so
                  it carries exactly the spatial checks R3 carries while keeping
                  R4's hand-written epilogue and raw table. It is what attributes
                  the +102.84 half of `R3 - R4` that ../NOTES.md 5e used to leave
                  as "inside the kernel": the two levers are exactly additive and
                  their sum is DEARER than R3, so none of `R3 - R4` is the
                  lifetime guarantee (../NOTES.md 5f). Not an admissible R4 --
                  it is the measurement that attributes the gap.

  r4_epiclear     R4 with the epilogue's DEAD `arr_set_unchecked(&mut live, j,
                  0u8)` store restored -- i.e. the R4 this pattern shipped at
                  TASK_060, before TASK_061 deleted the line. It is the "before"
                  side of ../NOTES.md 8a and prices the store at 6.81 / 10.49
                  Ir/call. The store is dead (`live` is a kernel local, `j` only
                  increases, nothing reads `live[j]` again), R3 has no
                  counterpart to it, and leaving it in flattered the safe rung.

  r3_issome       R3 with R2's liveness spellings restored -- `is_some()` then
                  `tab[h] = None` on CLOSE, `is_some()` then `unwrap()` on READ.
                  IN CONTRACT: `spec.md`'s idiom block pins the operations and
                  leaves the spelling of the test free, exactly as p14 leaves
                  its fold loop unpinned. This is the second in-contract R3
                  spelling ../NOTES.md 8 quotes against the shipped one.

  r2_epilogue     R2 with an EXPLICIT epilogue (`while j < ntab { tab[j] = None;
                  j += 1 }`) added before the return, so that the safe rungs and
                  the unsafe rungs walk the same loop. It prices the one
                  deliberate structural asymmetry in the ladder: the shipped
                  safe rungs have no epilogue because dropping the table IS the
                  epilogue. OUT OF CONTRACT as a rung -- the drop still runs
                  afterwards, so this program frees twice-scanned -- and it is a
                  measurement of the asymmetry, not a candidate.

  r5_vstdpure     R5 calling `vstd::raw_ptr::allocate` / `deallocate` directly
                  instead of the local `rec_alloc` / `rec_free` copies. **It has
                  a SMALLER trusted base -- five items instead of seven -- and
                  it is not a rung**, because vstd carries no `#[inline]` on
                  either, so the call is GOT-indirect and cross-crate and the
                  R4/R5 identity pin drops to `differ` at both opt levels. It is
                  the measurement behind ../NOTES.md 5a and 6a, and it is the
                  concrete form of TASK_055 §2.5's alarm: the
                  zero-project-local-axiom configuration exists and this
                  project's own `identity` pin excludes it.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PD))
DEFAULT_OUT = os.path.join(REPO, ".temp", "p27", "controls")


def sub(src, pairs, name):
    """Exact-string substitution, with every lever asserted to fire."""
    out = src
    for old, new in pairs:
        n = out.count(old)
        if n != 1:
            raise SystemExit(f"gen_controls.py: {name}: lever matched {n}x, "
                             f"expected 1:\n{old[:120]}")
        out = out.replace(old, new)
    return out


CHECKED = [
    ("""                arr_set_unchecked(&mut tab, ntab, q);
                arr_set_unchecked(&mut live, ntab, 1u8);""",
     """                tab[ntab] = q;
                live[ntab] = 1u8;"""),
    ("""            if h < ntab && arr_get_unchecked(&live, h) == 1u8 {
                rec_close(arr_get_unchecked(&tab, h));
                // THE LINE THE C RUNG FORGOT.
                arr_set_unchecked(&mut live, h, 0u8);""",
     """            if h < ntab && live[h] == 1u8 {
                rec_close(tab[h]);
                // THE LINE THE C RUNG FORGOT.
                live[h] = 0u8;"""),
    ("""            if h < ntab && arr_get_unchecked(&live, h) == 1u8 {
                let v: u8 = rec_read(arr_get_unchecked(&tab, h));""",
     """            if h < ntab && live[h] == 1u8 {
                let v: u8 = rec_read(tab[h]);"""),
    ("""        if arr_get_unchecked(&live, j) == 1u8 {
            rec_close(arr_get_unchecked(&tab, j));
        }""",
     """        if live[j] == 1u8 {
            rec_close(tab[j]);
        }"""),
]

# The WINDOW read, checked. One accessor, one call site shape -- replacing the
# body is enough, because every window read goes through it.
BUFCHECKED = [
    ("""fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}""",
     """fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    v[i]
}"""),
]

# The dead store the shipped R4 does NOT have, restored. This is the "before"
# side of ../NOTES.md 8a's before/after and the thing that prices it.
EPICLEAR = [
    ("""        if arr_get_unchecked(&live, j) == 1u8 {
            rec_close(arr_get_unchecked(&tab, j));
        }""",
     """        if arr_get_unchecked(&live, j) == 1u8 {
            rec_close(arr_get_unchecked(&tab, j));
            arr_set_unchecked(&mut live, j, 0u8);
        }"""),
]

ISSOME = [
    ("""            if h < ntab && tab[h].take().is_some() {""",
     """            if h < ntab && tab[h].is_some() {
                tab[h] = None;"""),
    ("""            if h < ntab {
                match &tab[h] {
                    Some(rec) => {
                        acc = acc.wrapping_mul(31).wrapping_add(**rec as u64);
                    },
                    None => {
                        acc = acc.wrapping_mul(31).wrapping_add(SENT);
                    },
                }
            } else {""",
     """            if h < ntab && tab[h].is_some() {
                let v: u8 = **tab[h].as_ref().unwrap();
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {"""),
]

EPILOGUE = [
    ("""    // No epilogue: `tab` is dropped here and that frees every live record.
    acc.wrapping_mul(31).wrapping_add(ntab as u64)""",
     """    let mut j: usize = 0;
    while j < ntab {
        tab[j] = None;
        j = j + 1;
    }
    acc.wrapping_mul(31).wrapping_add(ntab as u64)"""),
]

VSTDPURE = [
    ("    let (base, Tracked(raw), Tracked(dealloc)) = rec_alloc(RECSZ, 1);",
     "    let (base, Tracked(raw), Tracked(dealloc)) = allocate(RECSZ, 1);"),
    ("    rec_free(p, RECSZ, 1, Tracked(raw), Tracked(dl));",
     "    deallocate(p, RECSZ, 1, Tracked(raw), Tracked(dl));"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    unsafe = open(os.path.join(PD, "unsafe.rs")).read()
    tuned = open(os.path.join(PD, "safe_tuned.rs")).read()
    naive = open(os.path.join(PD, "safe_naive.rs")).read()
    verus = open(os.path.join(PD, "verus.rs")).read()

    # r5_vstdpure additionally DELETES `rec_alloc`, `rec_free` and their twins,
    # which are dead once the exec code calls vstd's API directly. Without the
    # deletion the control would still declare seven trusted items and its whole
    # point -- that the vstd-pure configuration publishes FIVE -- would be
    # unmeasurable.
    pure = sub(verus, VSTDPURE, "r5_vstdpure")
    a0 = "// TRUSTED ITEM 4 of 7, and **the one that is not what it looks like.**"
    a1 = "// --------------------------------------------------------- the record ops ---"
    i, j = pure.index(a0), pure.index(a1)
    pure = pure[:i] + pure[j:]
    tabchecked = sub(unsafe, CHECKED, "r4_tabchecked")
    made = [("r4_tabchecked.rs", tabchecked),
            ("r4_bufchecked.rs", sub(unsafe, BUFCHECKED, "r4_bufchecked")),
            ("r4_allchecked.rs", sub(tabchecked, BUFCHECKED, "r4_allchecked")),
            ("r4_epiclear.rs", sub(unsafe, EPICLEAR, "r4_epiclear")),
            ("r3_issome.rs", sub(tuned, ISSOME, "r3_issome")),
            ("r2_epilogue.rs", sub(naive, EPILOGUE, "r2_epilogue")),
            ("r5_vstdpure.rs", pure)]
    # the `#[path]` to common/driver.rs is one level shallower from .temp/p27/
    for name, txt in made:
        depth = os.path.relpath(REPO, a.out).count("..")
        txt = txt.replace('#[path = "../../common/driver.rs"]',
                          f'#[path = "{"../" * depth}common/driver.rs"]')
        open(os.path.join(a.out, name), "w").write(txt)
        print(f"  {name}")
    print(f"gen_controls.py: {len(made)} controls -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
