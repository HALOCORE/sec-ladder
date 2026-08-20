#!/usr/bin/env python3
"""p06's controls: every variant this pattern measured, derived from the SHIPPED
sources by exact-string substitution, with the hit count asserted.

`.memory/05-layout.md` rule 11: a control that does not verify cleanly (or that
verifies against a *different* contract) cannot live in a pattern dir at all --
`check.py` requires every `.rs` in the dir with a `verus!` block to be pinned in
`verus.obligations` and fails the gate for any pinned file reporting `n_err > 0`,
and `build.py`'s `--cell` list is closed. So the controls are `.temp/` artefacts
and **this generator is the committed reproduction path**. It is inside
`source_sha256` (TASK_021 closed `patterns/*/controls/*.py`), so a control that
drifts moves the gate record.

    python3 patterns/p06-rotate/controls/gen_controls.py           # write them
    python3 patterns/p06-rotate/controls/gen_controls.py --list    # names only

Outputs land in `.temp/p06/controls/`. The `#[path = "../../common/driver.rs"]`
attribute is rewritten to the real, hashed file (TASK_022/023's lesson: left
alone it resolves to `.temp/common/driver.rs`, which happens to exist today and
would not on a fresh clone).

Four families.

**A. The delete-the-check controls (../NOTES.md 7).** The reduction removed from
each Rust rung, so that "safe Rust reproduces the harm bit-for-bit in regime 1
and panics in regime 2" is a measurement rather than an argument. This is p12's
control shape and p17's control 1.

**B. The Verus mutants (../NOTES.md 10).** `msonly` is the one that earns its
keep: the reduction deleted AND the functional postcondition replaced by a
memory-safety-only one. It **verifies**, which is the finding -- the spec that
catches R1's bug in regime 1 is the FUNCTIONAL one, and a memory-safety proof of
this kernel is blind to it. `weakreq` and `tautology` are the two that must FAIL
something the gate checks.

**C. The R3-side spelling span (../NOTES.md 8).** Six spellings of the rotate and
of the window reslice, four in contract and two forbidden -- the forbidden pair
is built anyway, because `.memory/01-ladder.md` says a fiat's price must be
published beside the number it protects.

**D. The C hardening span (../NOTES.md 0, 3).** Two more spellings of the safety
line, both computing the same function as the shipped `r %= m`.
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p06", "controls")
DRIVER = os.path.join(REPO, "common", "driver.rs")


def src(name):
    return open(os.path.join(PDIR, name)).read()


def fix_paths(text):
    """Point `#[path]` at the real, hashed `common/driver.rs`.

    Left alone the relative path resolves against the OUTPUT directory, i.e.
    `.temp/common/driver.rs`, which is p08's latent defect (TASK_022)."""
    return text.replace('#[path = "../../common/driver.rs"]',
                        f'#[path = "{DRIVER}"]')


def sub(text, old, new, n=1, what=""):
    """Exact-string substitution with the hit count asserted."""
    got = text.count(old)
    if got != n:
        raise SystemExit(f"gen_controls.py: {what}: expected {n} occurrence(s) "
                         f"of {old!r}, found {got} -- the shipped source moved "
                         f"and this control would silently stop being the "
                         f"variant it claims to be")
    return text.replace(old, new)


# --------------------------------------------------------------- the pieces --
# The safety line, verbatim, in each language. Family A deletes it; family D
# respells it.
RUST_REDUCE = """        // THE SAFETY LINE. c/kernel.c omits exactly this.
        if m != 0 {
            r = r % m;
        } else {
            r = 0;
        }
"""
VERUS_REDUCE = """        // THE SAFETY LINE. c/kernel.c omits exactly this. The `m != 0` arm is
        // not decoration: `r % 0` is a division by zero, and `degenerate.bin`
        // declares a record with `nelem == 0`.
        if m != 0 {
            r = r % m;
        } else {
            r = 0;
        }
"""
C_REDUCE = """        if (m != 0)
            r %= m;
        else
            r = 0;
"""

# The R3 reverse block, verbatim (three copies in safe_tuned.rs).
R3_REV = """        if a < b {
            let s: &mut [u8] = &mut scr[a..b];
            let n: usize = s.len();
            let (front, back) = s.split_at_mut(n / 2);
            for (x, y) in front.iter_mut().zip(back.iter_mut().rev()) {
                core::mem::swap(x, y);
            }
        }
"""


def family_a():
    """Delete the reduction from each Rust rung. NOTES.md 7."""
    out = {}
    for rung, marker in (("safe_naive", RUST_REDUCE),
                         ("safe_tuned", RUST_REDUCE),
                         ("unsafe", RUST_REDUCE)):
        t = src(f"{rung}.rs")
        t = sub(t, marker, "        // THE SAFETY LINE, DELETED. This is R1's bug in Rust.\n",
                1, f"a_nored_{rung}")
        out[f"a_nored_{rung}"] = fix_paths(t)
    return out


MSONLY_ENSURES = """    ensures
        r == r,
"""

# The one-token bug that makes the pattern's point, and it took a rebuild to
# find it. The FIRST draft of `msonly` simply deleted the reduction -- and it
# does not verify, because a proof quantifies over all inputs and the unreduced
# kernel is genuinely memory-UNSAFE in regime 2. That is p17's control-2 lesson
# arriving on a second pattern: **the separation between "wrong" and "unsafe"
# needs a PROGRAM change, not an input.**
#
# `r %= SCR` is that change, and it is one identifier away from `r %= m`:
#
#   * it is memory-SAFE on every input -- `r < 64 == scr.len()`, so every index
#     the three reverses touch is in bounds, in regime 2 as well as regime 1;
#   * it is functionally WRONG on exactly regime 1's set -- `m <= r <= SCR` --
#     which is the same set the shipped R1 gets wrong there;
#   * so the memory-safety-only spec ACCEPTS it and the functional one REJECTS
#     it, and that is the disagreement p06 exists to exhibit.
SCRMOD = """        // THE SAFETY LINE, REPLACED BY THE WRONG MODULUS. One identifier:
        // `SCR` where the contract says `m`. Memory-safe on every input,
        // functionally wrong on exactly regime 1.
        r = r % SCR;
"""


def _drop_functional(t):
    """Remove everything that ties the exec code to `rotate_fold`.

    What is left is the memory-safety skeleton: the trusted accessors'
    `requires`, the loop bounds that discharge them, and nothing else."""
    t = sub(t, """        ensures
            walk(buf@, off as int, len as int, 0, nrec as int, 4, zero_scr(), 0) == acc,
""", "", 1, "msonly (loop ensures)")
    t = sub(t, """            walk(buf@, off as int, len as int, rec as int, nrec as int, p as int, scr@, acc)
                == walk(buf@, off as int, len as int, 0, nrec as int, 4, zero_scr(), 0),
""", "", 1, "msonly (loop invariant)")
    t = sub(t, """        assert(walk(buf@, off as int, len as int, rec_before, nrec as int, p_before,
            scr_before, acc_before) == walk(buf@, off as int, len as int, rec_before + 1,
            nrec as int, p as int, scr@, acc));
""", "", 1, "msonly (walk unfold)")
    t = sub(t, """            lemma_three_reverses(scr_loaded, m as int, r as int);
""", "", 1, "msonly (three-reverses lemma)")
    t = sub(t, """            assert(r == rotate_fold(buf@, (k * stride) as int, stride as int));
""", "", 1, "msonly (driver consume)")
    t = sub(t, """        r == rotate_fold(buf@, off as int, len as int),""",
            """        r == r,""", 1, "msonly (kernel ensures)")
    return t


def family_b():
    """The Verus mutants. NOTES.md 10."""
    out = {}

    # B1 -- the reduction simply DELETED, contract untouched. MUST FAIL: with
    # `r` unreduced, nothing bounds the store at `scr[b - 1]`. The positive
    # control for the whole proof.
    t = src("verus.rs")
    t = sub(t, VERUS_REDUCE,
            "        // THE SAFETY LINE, DELETED. This is R1's bug in Rust.\n",
            1, "b_nored")
    out["b_nored"] = fix_paths(t)

    # B2 -- the same deletion with the postcondition weakened to memory safety
    # only. **MUST ALSO FAIL**, and that is the finding it is here to make
    # precise: a memory-safety proof quantifies over ALL inputs, and the
    # unreduced kernel really is unsafe in regime 2. A weaker SPEC cannot rescue
    # it; only a program change can. p17 control 2, second instance.
    t = src("verus.rs")
    t = sub(t, VERUS_REDUCE,
            "        // THE SAFETY LINE, DELETED. This is R1's bug in Rust.\n",
            1, "b_nored_msonly")
    out["b_nored_msonly"] = fix_paths(_drop_functional(t))

    # B3 -- the WRONG MODULUS, contract untouched. MUST FAIL: `r % SCR` is not
    # `r % m`, so `lemma_three_reverses`'s `r <= m` is unavailable and the
    # postcondition is false.
    t = src("verus.rs")
    t = sub(t, VERUS_REDUCE, SCRMOD, 1, "b_scrmod")
    out["b_scrmod"] = fix_paths(t)

    # B4 -- THE MUTANT THAT EARNS ITS KEEP. The wrong modulus AND the
    # postcondition weakened to memory safety only. **MUST VERIFY.** Same
    # program as B3, same wrong answers on regime 1, and the memory-safety-only
    # spec accepts it.
    t = src("verus.rs")
    t = sub(t, VERUS_REDUCE, SCRMOD, 1, "b_scrmod_msonly")
    out["b_scrmod_msonly"] = fix_paths(_drop_functional(t))

    # B5 -- weakreq: the WRITE accessor's precondition weakened by one, in the
    # trusted item AND in its twin, which is what a single-commit weakening
    # looks like. The twin must then fail on `v[i] = x`.
    t = src("verus.rs")
    t = sub(t, """        i < old(v)@.len(),""", """        i <= old(v)@.len(),""",
            2, "b_weakreq")
    out["b_weakreq"] = fix_paths(t)

    # B6 -- tautology: the kernel's postcondition replaced by something true of
    # every program, and NOTHING else touched. p02's M7 shape -- except that on
    # p06 it does not verify, because the driver's consuming assert still names
    # the real spec. That is the `ensures`-is-load-bearing property, measured.
    t = src("verus.rs")
    t = sub(t, """        r == rotate_fold(buf@, off as int, len as int),""",
            """        r == r,""", 1, "b_tautology")
    out["b_tautology"] = fix_paths(t)
    return out


def family_c():
    """R3 spelling variants. NOTES.md 8."""
    out = {}

    # C1 -- the FORBIDDEN library one-liner for the reverse. Priced, not shipped.
    t = src("safe_tuned.rs")
    t = sub(t, R3_REV, """        if a < b {
            scr[a..b].reverse();
        }
""", 3, "c_reverse")
    out["c_reverse"] = fix_paths(t)

    # C2 -- the FORBIDDEN library one-liner for the whole rotate. Deletes the
    # three reverses outright.
    t = src("safe_tuned.rs")
    t = sub(t, R3_REV + """        a = r;
        b = m;
""" + R3_REV + """        a = 0;
        b = m;
""" + R3_REV, """        let _ = (a, b);
        scr[..m].rotate_left(r);
""", 1, "c_rotate")
    out["c_rotate"] = fix_paths(t)

    # C3 -- IN CONTRACT: `<[T]>::swap`, the other idiomatic safe reverse.
    t = src("safe_tuned.rs")
    t = sub(t, R3_REV, """        if a < b {
            let s: &mut [u8] = &mut scr[a..b];
            let n: usize = s.len();
            let mut j: usize = 0;
            while j < n / 2 {
                s.swap(j, n - 1 - j);
                j = j + 1;
            }
        }
""", 3, "c_swap")
    out["c_swap"] = fix_paths(t)

    # C4 -- IN CONTRACT: R2's indexed swap, over R3's reslice. The
    # matched-spelling R3, i.e. R3 with only the reslice and the fold tuned.
    t = src("safe_tuned.rs")
    t = sub(t, R3_REV, """        while a < b {
            let t: u8 = scr[a];
            let u: u8 = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a = a + 1;
            b = b - 1;
        }
""", 3, "c_idx")
    out["c_idx"] = fix_paths(t)

    # C5 -- IN CONTRACT: the ONE-SHOT window reslice, i.e. shipped R3 with the
    # two-step reslice lever backed out. This is what prices
    # `.memory/01-ladder.md` finding 3 on p06.
    t = src("safe_tuned.rs")
    t = sub(t, "    let w: &[u8] = buf.split_at(off).1.split_at(len).0;",
            "    let w: &[u8] = &buf[off..off + len];", 1, "c_oneshot")
    out["c_oneshot"] = fix_paths(t)

    # C6 -- R4 with the bulk load written INLINE instead of through the
    # `scr_load` helper. Not a rung: it breaks `identity: unsafe == verus, O3
    # exact`, because R5's copy has to be inside an `external_body` item. It is
    # what prices the identity pin (NOTES.md 3).
    t = src("unsafe.rs")
    t = sub(t, "        scr_load(&mut scr, buf, off + p, m);",
            "        scr[..m].copy_from_slice(&buf[off + p..off + p + m]);",
            1, "c_r4inline")
    out["c_r4inline"] = fix_paths(t)
    return out


def family_d():
    """C hardening-line spellings. NOTES.md 0 and 3."""
    out = {}
    t = src("c/kernel_hardened.c")
    out["d_cmp"] = sub(t, C_REDUCE, """        if (m == 0)
            r = 0;
        else if (r >= m)
            r %= m;
""", 1, "d_cmp")
    t = src("c/kernel_hardened.c")
    out["d_sub"] = sub(t, C_REDUCE, """        if (m == 0)
            r = 0;
        else
            while (r >= m)
                r -= m;
""", 1, "d_sub")
    return out


# ---- family E: ONE LOOP AT A TIME ------------------------------------------
#
# `.memory/01-ladder.md` finding 3, rule 1: *before attributing a cost to bounds
# checking, decompose -- change one loop at a time and re-measure. A
# whole-kernel delta attributes nothing.* p02's and p16's retractions are both
# what happens when that step is skipped.
#
# R2's checked spellings, replaced one loop at a time by R4's unchecked ones and
# nothing else:
#
#   e_revonly   the three REVERSE loops unchecked, the fold still checked
#   e_foldonly  the FOLD unchecked, the three reverses still checked
#   e_hdronly   the header and record-header DECODE unchecked, both loops checked
#
# `e_revonly + e_foldonly + e_hdronly - 2*R2` should reproduce R4 if the three
# terms do not interact.
R2_SWAP = """        while a < b {
            let t: u8 = scr[a];
            let u: u8 = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a = a + 1;
            b = b - 1;
        }
"""
R4_SWAP = """        while a < b {
            let t: u8 = unsafe { *scr.get_unchecked(a) };
            let u: u8 = unsafe { *scr.get_unchecked(b - 1) };
            unsafe { *scr.get_unchecked_mut(a) = u; }
            unsafe { *scr.get_unchecked_mut(b - 1) = t; }
            a = a + 1;
            b = b - 1;
        }
"""
R2_FOLD = """            acc = acc.wrapping_mul(31).wrapping_add(scr[i] as u64);
"""
R4_FOLD = """            acc = acc.wrapping_mul(31)
                .wrapping_add(unsafe { *scr.get_unchecked(i) } as u64);
"""


def family_e():
    """One loop at a time. NOTES.md 4."""
    out = {}
    t = src("safe_naive.rs")
    out["e_revonly"] = fix_paths(sub(t, R2_SWAP, R4_SWAP, 3, "e_revonly"))
    t = src("safe_naive.rs")
    out["e_foldonly"] = fix_paths(sub(t, R2_FOLD, R4_FOLD, 1, "e_foldonly"))
    t = src("safe_naive.rs")
    for a, b, n in (("buf[off] as usize", "unsafe { *buf.get_unchecked(off) } as usize", 1),
                    ("buf[off + 1] as usize", "unsafe { *buf.get_unchecked(off + 1) } as usize", 1),
                    ("buf[off + 2] as usize", "unsafe { *buf.get_unchecked(off + 2) } as usize", 1),
                    ("buf[off + 3] as usize", "unsafe { *buf.get_unchecked(off + 3) } as usize", 1),
                    ("buf[off + p] as usize", "unsafe { *buf.get_unchecked(off + p) } as usize", 1),
                    ("buf[off + p + 1] as usize", "unsafe { *buf.get_unchecked(off + p + 1) } as usize", 1),
                    ("buf[off + p + 2] as usize", "unsafe { *buf.get_unchecked(off + p + 2) } as usize", 1),
                    ("buf[off + p + 3] as usize", "unsafe { *buf.get_unchecked(off + p + 3) } as usize", 1),
                    ("buf[off + p + 4] as usize", "unsafe { *buf.get_unchecked(off + p + 4) } as usize", 1),
                    ("buf[off + p + 5] as usize", "unsafe { *buf.get_unchecked(off + p + 5) } as usize", 1),
                    ("buf[off + p + 6] as usize", "unsafe { *buf.get_unchecked(off + p + 6) } as usize", 1),
                    ("buf[off + p + 7] as usize", "unsafe { *buf.get_unchecked(off + p + 7) } as usize", 1)):
        t = sub(t, a, b, n, "e_hdronly")
    out["e_hdronly"] = fix_paths(t)
    return out


def all_controls():
    out = {}
    out.update(family_a())
    out.update(family_b())
    out.update(family_c())
    out.update(family_d())
    out.update(family_e())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    ctl = all_controls()
    if a.list:
        for n in sorted(ctl):
            print(n)
        return 0
    os.makedirs(OUT, exist_ok=True)
    for n, text in sorted(ctl.items()):
        ext = ".c" if n.startswith("d_") else ".rs"
        p = os.path.join(OUT, n + ext)
        with open(p, "w") as fh:
            fh.write(text)
        print(f"  {os.path.relpath(p, REPO):50s} {len(text):7d} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
