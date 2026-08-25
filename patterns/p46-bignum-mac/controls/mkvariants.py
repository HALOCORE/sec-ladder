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
with the SAME FLAGS `harness/build.py::rust_flags` gives every measured cell:

    ~/.cargo/bin/rustc --edition 2021 -C codegen-units=1 \\
          -C opt-level=3 -C debug-assertions=off \\
          --cfg slb_isolated <variant>.rs -o <variant>

⚠⚠ **`-C codegen-units=1` IS NOT OPTIONAL AND THIS DOCSTRING OMITTED IT UNTIL
TASK_092.** `harness/build.py` passes it to every shipped cell, so a variant
built without it is being differenced against a baseline built with it, and the
shift does **not** cancel -- only one side moved. Every figure in `../NOTES.md`
8b and 0c was 1 to 2 Ir/call off for exactly that reason and has been
re-measured; `../NOTES.md` 0c and 8b carry both columns. 8a's
rolled-vs-rolled control was unaffected because it rebuilds *both* sides.

For the rolled-vs-rolled control of `../NOTES.md` 8a, add
`-C llvm-args=-unroll-count=1` and build the SHIPPED sources unchanged.

`v46_mutreslice` is a Verus file: run it with `./verus_run.py`, and compile it
with `./verus_run.py --compile ... -C codegen-units=1 -C opt-level=3
-C debug-assertions=off --cfg slb_isolated`.
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
        "unsafe.rs", "R4 (NOT A RUNG)",
        "THE CHEAPEST UNSAFE SPELLING FOUND AND IT IS NOT A RUNG. ⚠ NOT for "
        "the reason this line gave until TASK_092 -- the pinned vstd DOES "
        "specify a mutable sub-slice at the value level "
        "(std_specs/slice.rs), and `v46_mutreslice` below is its FULL R5 and "
        "VERIFIES, 21 verified 0 errors. What disqualifies it is (a) two NEW "
        "TRUSTED ITEMS, because the pinned vstd has zero `get_unchecked` "
        "specifications, and (b) an R4/R5 pair that is `differ` at -O3 by "
        "`15n + 1` Ir/call against the `identity: unsafe == verus, O3 exact` "
        "pin (../NOTES.md 0c)",
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


    # ---- THE ONE THAT IS NOT A RUNG, AS AN R5 THAT VERIFIES ------------
    "v46_mutreslice": (
        "verus.rs", "R5 of r4_mutreslice",
        "THE FULL R5 OF `r4_mutreslice`, AND IT VERIFIES: `21 verified, 0 "
        "errors` at the pinned Verus/vstd, same count and same postcondition "
        "as the shipped verus.rs, no assume/admit/assume_specification. It is "
        "the control that REFUTES the reason ../NOTES.md 0c gave until "
        "TASK_092 for excluding `r4_mutreslice`. It is still not a rung: it "
        "adds two trusted items and its R4/R5 pair is `differ` at -O3. Four "
        "substitutions -- the nest, plus three renames of the spec fn `row`, "
        "which the exec local `row` would otherwise shadow (Rust puts both in "
        "the value namespace)",
        [
            """        let ghost out0 = out@;
        let ai: u64 = load_u64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m
            invariant
                0 <= j <= m,
                0 <= i < n,
                1 <= n <= 255,
                1 <= m <= 255,
                n + m <= OUTCAP,
                w@.len() == len,
                w@ == buf@.subrange(off as int, off + len),
                n == w@[0] as int,
                m == w@[1] as int,
                8 + 8 * (n + m) <= len,
                out@.len() == OUTCAP,
                bl@.len() == BCAP,
                forall|q: int| 0 <= q < m ==> #[trigger] bl@[q] == limb(w@, n + q),
                ai == limb(w@, i as int),
                row(w@, n as int, m as int, ai, out0, i as int, 0, 0) == row(
                    w@,
                    n as int,
                    m as int,
                    ai,
                    out@,
                    i as int,
                    j as int,
                    carry,
                ),
            decreases m - j,
        {
            let bj: u64 = arr_get_unchecked(&bl, j);
            // THE SAFETY LINE, as an obligation. `i <= n - 1` and `j <= m - 1`
            // are the loop conditions and `n + m <= OUTCAP` is the test
            // `c/kernel.c` omits, so `i + j <= n + m - 2 < OUTCAP`. Purely
            // LINEAR -- p05's counterpart is not, and that is the difference.
            let c: u64 = arr_get_unchecked(&out, i + j);
            let (lo, hi) = mac(ai, bj, c, carry);
            arr_set_unchecked(&mut out, i + j, lo);
            carry = hi;
            j = j + 1;
        }
        arr_set_unchecked(&mut out, i + m, carry);""",
            """        row(
            w,
            n,
            m,
            ai,
            out.update(i + j, mac_lo(ai, bj, c, carry)),
            i,
            j + 1,
            mac_hi(ai, bj, c, carry),
        )""",
            "rows(w, n, m, row(w, n, m, limb(w, i), out, i, 0, 0), i + 1)",
            "pub open spec fn row(",
            "// TRUSTED ITEM 4 of 5. Argument parsing",
        ],
        [
            """        let ghost out0 = out@;
        let ai: u64 = load_u64(w, 8 + 8 * i);
        let ghost mut gout: Seq<u64> = out@;
        // THE MUTABLE SUB-SLICE. `i < n` and `n + m <= OUTCAP` give
        // `i + m + 1 <= OUTCAP`, which is `index_req` for the Range.
        let row: &mut [u64] = &mut out[i..i + m + 1];
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m
            invariant
                0 <= j <= m,
                0 <= i < n,
                1 <= n <= 255,
                1 <= m <= 255,
                n + m <= OUTCAP,
                i + m + 1 <= OUTCAP,
                w@.len() == len,
                w@ == buf@.subrange(off as int, off + len),
                n == w@[0] as int,
                m == w@[1] as int,
                8 + 8 * (n + m) <= len,
                bl@.len() == BCAP,
                forall|q: int| 0 <= q < m ==> #[trigger] bl@[q] == limb(w@, n + q),
                ai == limb(w@, i as int),
                out0.len() == OUTCAP,
                gout.len() == OUTCAP,
                row@.len() == m + 1,
                row@ == gout.subrange(i as int, (i + m + 1) as int),
                forall|q: int|
                    0 <= q < OUTCAP && !(i <= q < i + m + 1) ==> #[trigger] gout[q] == out0[q],
                rowstep(w@, n as int, m as int, ai, out0, i as int, 0, 0) == rowstep(
                    w@,
                    n as int,
                    m as int,
                    ai,
                    gout,
                    i as int,
                    j as int,
                    carry,
                ),
            decreases m - j,
        {
            let bj: u64 = arr_get_unchecked(&bl, j);
            // THE SAFETY LINE, as an obligation -- now on the SUB-SLICE:
            // `j < m < row@.len()`.
            let c: u64 = slice_get_unchecked(row, j);
            proof {
                // `row@[j]` IS `gout[i + j]`: this is the step the shipped
                // NOTES.md 0c says is impossible.
                vstd::seq::lemma_seq_subrange_index(gout, i as int, (i + m + 1) as int, j as int);
            }
            let (lo, hi) = mac(ai, bj, c, carry);
            let ghost gprev: Seq<u64> = gout;
            slice_set_unchecked(row, j, lo);
            proof {
                gout = gprev.update((i + j) as int, lo);
                assert(row@ =~= gout.subrange(i as int, (i + m + 1) as int)) by {
                    assert forall|q: int| 0 <= q < m + 1 implies #[trigger] row@[q]
                        == gout.subrange(i as int, (i + m + 1) as int)[q] by {
                        vstd::seq::lemma_seq_subrange_index(
                            gout,
                            i as int,
                            (i + m + 1) as int,
                            q,
                        );
                        vstd::seq::lemma_seq_subrange_index(
                            gprev,
                            i as int,
                            (i + m + 1) as int,
                            q,
                        );
                    }
                }
            }
            carry = hi;
            j = j + 1;
        }
        let ghost gprev2: Seq<u64> = gout;
        slice_set_unchecked(row, m, carry);
        proof {
            gout = gprev2.update((i + m) as int, carry);
            assert(row@ =~= gout.subrange(i as int, (i + m + 1) as int)) by {
                assert forall|q: int| 0 <= q < m + 1 implies #[trigger] row@[q]
                    == gout.subrange(i as int, (i + m + 1) as int)[q] by {
                    vstd::seq::lemma_seq_subrange_index(gout, i as int, (i + m + 1) as int, q);
                    vstd::seq::lemma_seq_subrange_index(gprev2, i as int, (i + m + 1) as int, q);
                }
            }
        }
        // ---- THE BORROW ENDS HERE. Relate `out@` back to the ghost mirror. --
        proof {
            assert forall|q: int| 0 <= q < OUTCAP implies #[trigger] out@[q] == gout[q] by {
                if i <= q < i + m + 1 {
                    vstd::seq::lemma_seq_subrange_index(
                        out@,
                        i as int,
                        (i + m + 1) as int,
                        q - i,
                    );
                    vstd::seq::lemma_seq_subrange_index(
                        gout,
                        i as int,
                        (i + m + 1) as int,
                        q - i,
                    );
                }
            }
            assert(out@ =~= gout);
        }""",
            """        rowstep(
            w,
            n,
            m,
            ai,
            out.update(i + j, mac_lo(ai, bj, c, carry)),
            i,
            j + 1,
            mac_hi(ai, bj, c, carry),
        )""",
            "rows(w, n, m, rowstep(w, n, m, limb(w, i), out, i, 0, 0), i + 1)",
            "pub open spec fn rowstep(",
            """// TRUSTED ITEM 6 and 7 of 7, AND THEY ARE THE POINT -- unchecked READ through a slice. Same shape as
// items 1-3: the std-documented safety condition as `requires`, the single
// element read as `ensures`.
#[inline(always)]
#[verifier::external_body]
fn slice_get_unchecked(v: &[u64], i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// TRUSTED ITEM 6 and 7 of 7, AND THEY ARE THE POINT -- unchecked WRITE through a mutable slice.
#[inline(always)]
#[verifier::external_body]
fn slice_set_unchecked(v: &mut [u64], i: usize, x: u64)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// TRUSTED ITEM 4 of 5. Argument parsing""",
        ]),
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
    """Apply the variant's substitution(s) to its shipped source.

    `old`/`new` may each be a STRING (one substitution) or a LIST of strings of
    equal length (several, applied in order). Every substitution still asserts
    `count == 1` **at the point it is applied**, so a multi-substitution variant
    fails closed exactly the way a single-substitution one does. The list form
    was added at TASK_092 for `v46_mutreslice`, which needs four edits to
    `verus.rs`: the nest, and three renames of the spec fn `row` that the exec
    variant's local `row` would otherwise shadow.
    """
    fname, side, why, old, new = VARIANTS[name]
    olds = old if isinstance(old, list) else [old]
    news = new if isinstance(new, list) else [new]
    if len(olds) != len(news):
        sys.exit(f"mkvariants.py: {name}: {len(olds)} old spans against "
                 f"{len(news)} new ones")
    s = src(fname)
    for k, (o, n) in enumerate(zip(olds, news)):
        hits = s.count(o)
        if hits != 1:
            sys.exit(f"mkvariants.py: {name}: spliced span {k} occurs {hits} "
                     f"times in {fname}, not once -- the shipped rung moved and "
                     f"this control would no longer be 'the shipped kernel plus "
                     f"one change'. Fix the substitution, do not relax the "
                     f"assertion.")
        s = s.replace(o, n)
    return s, fname, side, why


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
