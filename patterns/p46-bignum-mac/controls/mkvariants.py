#!/usr/bin/env python3
"""p46 control generator — every variant `../NOTES.md` measures, derived from the
SHIPPED sources by exact-string substitution.

`.memory/05-layout.md` step 11: a control that cannot live in the pattern dir
ships as (a) a committed generator that derives it from the shipped source by
exact-string substitution and asserts its own hit count, so it cannot drift, and
(b) a `NOTES.md` section carrying the diff, the commands and the measured
output. This file is (a); `../NOTES.md` 0b, 0c, 8a and 8b are (b).

Every substitution below asserts `count == 1` on the shipped file, so if a rung
is edited in a way that moves the spliced span, this generator **fails closed**
rather than emitting a variant that is no longer the shipped kernel plus one
change.

    controls/mkvariants.py --list
    controls/mkvariants.py --write .temp/t89/r4var
    controls/mkvariants.py --check          # every substitution still applies

The variants are NOT rungs and are not built by `harness/build.py`. Build them
the way `../NOTES.md` 8b did:

    rustc -C opt-level=3 -C debug-assertions=off -C panic=unwind \\
          --edition 2021 --cfg slb_isolated <variant>.rs -o <variant>

and for the rolled-vs-rolled control of `../NOTES.md` 8a, add
`-C llvm-args=-unroll-count=1` and build the SHIPPED sources unchanged.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)


def src(name):
    return open(os.path.join(PDIR, name)).read()


# --------------------------------------------------------------------------
# (from, old, new, side, what it tests)
# --------------------------------------------------------------------------
VARIANTS = {

    # ---- R4 side, all three admissible-shaped ---------------------------
    "r4_inline": (
        "unsafe.rs", "R4",
        "the `mac` helper written out in the loop body -- does the 2x unroll "
        "LLVM grants the safe rung depend on the helper being a call?",
        """            let bj: u64 = arr_get_unchecked(&bl, j);
            let c: u64 = arr_get_unchecked(&out, i + j);
            let (lo, hi) = mac(ai, bj, c, carry);
            arr_set_unchecked(&mut out, i + j, lo);
            carry = hi;
            j = j + 1;""",
        """            let bj: u64 = arr_get_unchecked(&bl, j);
            let t: u128 = (ai as u128) * (bj as u128)
                + (arr_get_unchecked(&out, i + j) as u128) + (carry as u128);
            arr_set_unchecked(&mut out, i + j, t as u64);
            carry = (t >> 64) as u64;
            j = j + 1;"""),

    "r4_runidx": (
        "unsafe.rs", "R4",
        "a running output index `oi` instead of `i + j`",
        """        let mut j: usize = 0;
        while j < m {
            let bj: u64 = arr_get_unchecked(&bl, j);
            let c: u64 = arr_get_unchecked(&out, i + j);
            let (lo, hi) = mac(ai, bj, c, carry);
            arr_set_unchecked(&mut out, i + j, lo);
            carry = hi;
            j = j + 1;
        }
        arr_set_unchecked(&mut out, i + m, carry);""",
        """        let mut j: usize = 0;
        let mut oi: usize = i;
        while j < m {
            let bj: u64 = arr_get_unchecked(&bl, j);
            let c: u64 = arr_get_unchecked(&out, oi);
            let (lo, hi) = mac(ai, bj, c, carry);
            arr_set_unchecked(&mut out, oi, lo);
            carry = hi;
            j = j + 1;
            oi = oi + 1;
        }
        arr_set_unchecked(&mut out, oi, carry);"""),

    # ---- THE ONE THAT IS NOT A RUNG -------------------------------------
    "r4_mutreslice": (
        "unsafe.rs", "R4 (INADMISSIBLE)",
        "THE CHEAPEST UNSAFE SPELLING FOUND AND IT IS NOT A RUNG: it takes a "
        "MUTABLE sub-slice, which the pinned vstd cannot specify -- "
        "`slice_subrange` is `&[T]`-only and `ExSliceIndex::index_mut` has a "
        "`requires` and no `ensures`, so a write through it cannot be related "
        "back to the array and R5 cannot discharge its postcondition "
        "(../NOTES.md 0c)",
        """    let mut i: usize = 0;
    while i < n {
        let ai: u64 = load_u64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m {
            let bj: u64 = arr_get_unchecked(&bl, j);
            let c: u64 = arr_get_unchecked(&out, i + j);
            let (lo, hi) = mac(ai, bj, c, carry);
            arr_set_unchecked(&mut out, i + j, lo);
            carry = hi;
            j = j + 1;
        }
        arr_set_unchecked(&mut out, i + m, carry);
        i = i + 1;
    }""",
        """    let mut i: usize = 0;
    while i < n {
        let ai: u64 = load_u64(w, 8 + 8 * i);
        let row: &mut [u64] = &mut out[i..i + m + 1];
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m {
            let bj: u64 = arr_get_unchecked(&bl, j);
            let c: u64 = unsafe { *row.get_unchecked(j) };
            let (lo, hi) = mac(ai, bj, c, carry);
            unsafe { *row.get_unchecked_mut(j) = lo; }
            carry = hi;
            j = j + 1;
        }
        unsafe { *row.get_unchecked_mut(m) = carry; }
        i = i + 1;
    }"""),

    # ---- R3 side --------------------------------------------------------
    "r3_reslice": (
        "safe_naive.rs", "R3",
        "reslice the row and the b operand once per row, then index them with "
        "a `while` -- the R3 lever without the iterator",
        """    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m {
            let bj: u64 = bl[j];
            let t: u128 =
                (ai as u128) * (bj as u128) + (out[i + j] as u128) + (carry as u128);
            out[i + j] = t as u64;
            carry = (t >> 64) as u64;
            j = j + 1;
        }
        out[i + m] = carry;
        i = i + 1;
    }""",
        """    let bs: &[u64] = &bl[0..m];
    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let row = &mut out[i..i + m + 1];
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m {
            let bj: u64 = bs[j];
            let t: u128 =
                (ai as u128) * (bj as u128) + (row[j] as u128) + (carry as u128);
            row[j] = t as u64;
            carry = (t >> 64) as u64;
            j = j + 1;
        }
        row[m] = carry;
        i = i + 1;
    }"""),

    "r3_rangefor": (
        "safe_tuned.rs", "R3",
        "reslice the row, then a `for j in 0..m` over it instead of the "
        "iterator zip",
        """    let bs: &[u64] = &bl[0..m];
    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        for (o, &bj) in out[i..i + m].iter_mut().zip(bs.iter()) {
            let t: u128 = (ai as u128) * (bj as u128) + (*o as u128) + (carry as u128);
            *o = t as u64;
            carry = (t >> 64) as u64;
        }
        out[i + m] = carry;
        i = i + 1;
    }""",
        """    let bs: &[u64] = &bl[0..m];
    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let row = &mut out[i..i + m + 1];
        let mut carry: u64 = 0;
        for j in 0..m {
            let t: u128 = (ai as u128) * (bs[j] as u128) + (row[j] as u128) + (carry as u128);
            row[j] = t as u64;
            carry = (t >> 64) as u64;
        }
        row[m] = carry;
        i = i + 1;
    }"""),

    # ---- R2 side --------------------------------------------------------
    "r2_rangefor": (
        "safe_naive.rs", "R2",
        "the same absolute-index body with `for` loops instead of `while`",
        """    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m {
            let bj: u64 = bl[j];
            let t: u128 =
                (ai as u128) * (bj as u128) + (out[i + j] as u128) + (carry as u128);
            out[i + j] = t as u64;
            carry = (t >> 64) as u64;
            j = j + 1;
        }
        out[i + m] = carry;
        i = i + 1;
    }""",
        """    for i in 0..n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        for j in 0..m {
            let bj: u64 = bl[j];
            let t: u128 =
                (ai as u128) * (bj as u128) + (out[i + j] as u128) + (carry as u128);
            out[i + j] = t as u64;
            carry = (t >> 64) as u64;
        }
        out[i + m] = carry;
    }"""),

    # ---- THE VERUS CONTROL: `c/kernel.c` written in Verus ---------------
    "v46_nosafety": (
        "verus.rs", "R5 (DELIBERATELY BROKEN)",
        "THE SAFETY LINE DELETED -- i.e. `c/kernel.c` written in Verus. Run it "
        "with `./verus_run.py`: it reports `20 verified, 1 errors`, "
        "`invariant not satisfied before loop` on `n + m <= OUTCAP`. There is "
        "no Verus spelling of the buggy rung that verifies (../NOTES.md 6a). "
        "It cannot live in the pattern dir: check.py stage 5a requires every "
        "`.rs` there containing a `verus!` block to be pinned in "
        "`verus.obligations`, and fails the gate for any pinned file reporting "
        "n_err > 0 (.memory/05-layout.md step 11).",
        """    if n + m > OUTCAP {
        return REJ;
    }
""",
        """    // SAFETY LINE DELETED -- this is c/kernel.c.
"""),
}


def build(name):
    fname, side, why, old, new = VARIANTS[name]
    s = src(fname)
    hits = s.count(old)
    if hits != 1:
        sys.exit(f"mkvariants.py: {name}: the spliced span occurs {hits} times "
                 f"in {fname}, not once -- the shipped rung moved and this "
                 f"control would no longer be 'the shipped kernel plus one "
                 f"change'. Fix the substitution, do not relax the assertion.")
    return s.replace(old, new), fname, side, why


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", metavar="DIR")
    a = ap.parse_args()
    if not (a.list or a.check or a.write):
        ap.print_help()
        return
    for name in VARIANTS:
        text, fname, side, why = build(name)
        h = hashlib.sha256(text.encode()).hexdigest()[:12]
        if a.list or a.check:
            print(f"{name:16s} {side:22s} from {fname:14s} sha256 {h}  {why}")
        if a.write:
            os.makedirs(a.write, exist_ok=True)
            p = os.path.join(a.write, f"{name}.rs")
            open(p, "w").write(text)
            print(f"wrote {p}  ({side}, from {fname}, sha256 {h})")
    if a.check:
        print(f"\n{len(VARIANTS)} substitution(s), every one applying exactly "
              f"once to its shipped source.")


if __name__ == "__main__":
    main()
