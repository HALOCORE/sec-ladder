#!/usr/bin/env python3
"""p13 control: the R5 twins of the R4-side candidates `controls/spellings.py`
prices, so that "reachable by an R5" is a Verus run and not an assertion.

`../spec.md` pins `identity: unsafe == verus, O3 exact`, so a p13 R4 is not
merely a program that may use `unsafe`: it must have a byte-identical R5 twin
that Verus verifies. An R4 spelling with no admissible R5 is a **control** and
never an endpoint of a published bound -- p05's `c4_hu16_nz` and p16's `r4_hdr`
are the precedent, and `.memory/01-ladder.md` finding 14 is the mechanism.
**That mechanism is real and it is also the most available WRONG explanation on
this project**, which is why p13 measures it per candidate instead of citing it:

    u1_bulk_copyfill    copy_nonoverlapping + write_bytes
                        -> 17 verified / 0 errors, twin 24 / 0.  REACHABLE, at
                           the cost of TWO new trusted items (TCB 5 -> 7).
    u4_bounded_consumer `while d < DST_CAP && ...`
                        -> 19 / 0, twin 22 / 0 -- the SHIPPED counts, unmoved.
                           REACHABLE, no new TCB.
                           So the prover does NOT exclude it and the exclusion
                           is ../spec.md's English -- a FIAT, priced rather
                           than asserted.
    R3's own consumer   `dst.iter().position(|&b| b == 0)`
                        -> `is not supported` at the pinned vstd. NOT
                           reachable, and that is what actually excludes the
                           R4/R5 side from R3's consumer spelling.

The bulk pair's counts differ from the shipped 19/22 on purpose: it DELETES the
copy and the fill loop bodies from `kernel` (7 -> 5, so 19 -> 17) and adds two
trusted items whose twins carry a loop each (17 + 3 + 2 + 2 = 24), and
`../spec.md`'s pins would all move if it were ever shipped. It is not shipped; ../NOTES.md 10 publishes it as the R4-side
endpoint and says what shipping it would cost.

A broken or alternate proof cannot live in the pattern directory
(`.memory/05-layout.md` item 11: `check.py` requires every `verus!`-bearing
`.rs` there to be pinned and to verify), so everything here is written to
`.temp/p13/spellings/` and derived from the SHIPPED `verus.rs` by exact-string
substitution with asserted hit counts.

    python3 patterns/p13-strncpy-trunc/controls/gen_bulk_r5.py [outdir]
    python3 patterns/p13-strncpy-trunc/controls/spellings.py --verus
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))

# ---- two new TRUSTED items + two verified twins, for the bulk pair ----------
# Each `ensures` is stated in the pattern's OWN spec functions, which is what
# the two intrinsics literally compute:
#   copy_nonoverlapping(buf+off+p, dst, n)  ==  copy_into(dst, buf, off, p, 0, n)
#   write_bytes(dst+from, 0, DST_CAP-from)  ==  fill_zero(dst, from)
V5_ITEMS = """
// ---- TASK_046 R4-SIDE CANDIDATE: TRUSTED ITEMS 6 and 7 ---------------------
// Not shipped. `controls/gen_bulk_r5.py` explains why they are priced here and
// not in verus.rs: both raise the TCB from 5 to 7, and a shipped rung would owe
// an SLB-TRUSTED-ARGUMENT block for each.
#[inline(always)]
#[verifier::external_body]
fn copy_bytes_arr(src: &[u8], off: usize, p: usize, v: &mut [u8; 32], n: usize)
    requires
        off + p + n <= src@.len(),
        n <= DST_CAP,
    ensures
        final(v)@ == copy_into(old(v)@, src@, off as int, p as int, 0, n as int),
{
    unsafe {
        core::ptr::copy_nonoverlapping(src.as_ptr().add(off + p), v.as_mut_ptr(), n);
    }
}

#[cfg(slb_twin)]
fn slb_twin_copy_bytes_arr(src: &[u8], off: usize, p: usize, v: &mut [u8; 32], n: usize)
    requires
        off + p + n <= src@.len(),
        n <= DST_CAP,
    ensures
        final(v)@ == copy_into(old(v)@, src@, off as int, p as int, 0, n as int),
{
    assert(src@.len() == vstd::slice::spec_slice_len(src));
    let ghost v0 = v@;
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n <= DST_CAP,
            off + p + n <= src@.len(),
            src@.len() <= usize::MAX,
            v@.len() == DST_CAP,
            copy_into(v@, src@, off as int, p as int, i as int, n as int) == copy_into(
                v0,
                src@,
                off as int,
                p as int,
                0,
                n as int,
            ),
        decreases n - i,
    {
        let b: u8 = src[off + p + i];
        v[i] = b;
        i = i + 1;
    }
}

#[inline(always)]
#[verifier::external_body]
fn fill_zero_arr(v: &mut [u8; 32], from: usize)
    requires
        from <= DST_CAP,
    ensures
        final(v)@ == fill_zero(old(v)@, from as int),
{
    unsafe {
        core::ptr::write_bytes(v.as_mut_ptr().add(from), 0u8, DST_CAP - from);
    }
}

#[cfg(slb_twin)]
fn slb_twin_fill_zero_arr(v: &mut [u8; 32], from: usize)
    requires
        from <= DST_CAP,
    ensures
        final(v)@ == fill_zero(old(v)@, from as int),
{
    let ghost v0 = v@;
    let mut j: usize = from;
    while j < DST_CAP
        invariant
            from <= j <= DST_CAP,
            v@.len() == DST_CAP,
            fill_zero(v@, j as int) == fill_zero(v0, from as int),
        decreases DST_CAP - j,
    {
        v[j] = 0;
        j = j + 1;
    }
}
"""

V5_ANCHOR = """// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md."""

V5_COPY_OLD = """        let mut i: usize = 0;
        // "The copy from here is the whole copy." p12's copy invariant with the
        // destination cursor replaced by `i` -- p13 always starts at slot 0,
        // which is what makes this the easy half of the proof.
        while i < n
            invariant
                i <= n <= DST_CAP,
                n as int <= q as int - p as int,
                p <= q <= len,
                dst@.len() == DST_CAP,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                copy_into(dst@, buf@, off as int, p as int, i as int, n as int) == copy_into(
                    dst_before,
                    buf@,
                    off as int,
                    p as int,
                    0,
                    n as int,
                ),
            decreases n - i,
        {
            let b: u8 = buf_get_unchecked(buf, off + p + i);
            dst_set_unchecked(&mut dst, i, b);
            i = i + 1;
        }
"""
V5_COPY_NEW = """        assert(n as int <= q as int - p as int);
        copy_bytes_arr(buf, off, p, &mut dst, n);
        assert(dst@ == copy_into(dst_before, buf@, off as int, p as int, 0, n as int));
"""

V5_FILL_OLD = """        let mut j: usize = n;
        // "The fill from here is the whole fill." Same shape, on the half of
        // `strncpy` that costs `DST_CAP - n` bytes of writing nobody asked for.
        while j < DST_CAP
            invariant
                n <= j <= DST_CAP,
                dst@.len() == DST_CAP,
                fill_zero(dst@, j as int) == fill_zero(dst_copied, n as int),
            decreases DST_CAP - j,
        {
            dst_set_unchecked(&mut dst, j, 0);
            j = j + 1;
        }
"""
V5_FILL_NEW = """        fill_zero_arr(&mut dst, n);
"""

# ---- the consumer candidates ----------------------------------------------
V5_CONS_OLD = """        while dst_get_unchecked(&dst, d) != 0
            invariant
                d < DST_CAP,
                dst@.len() == DST_CAP,
                dst@[DST_CAP - 1] == 0u8,
                scan_dst(dst@, d as int) == scan_dst(dst@, 0),
            decreases DST_CAP - d,
        {
            assert(dst@[d as int] != 0u8);
            assert(d != DST_CAP - 1);
            d = d + 1;
        }
"""
V5_CONS_BOUNDED = """        while d < DST_CAP && dst_get_unchecked(&dst, d) != 0
            invariant
                d <= DST_CAP,
                dst@.len() == DST_CAP,
                scan_dst(dst@, d as int) == scan_dst(dst@, 0),
            decreases DST_CAP - d,
        {
            assert(dst@[d as int] != 0u8);
            d = d + 1;
        }
"""
V5_CONS_HEAD_OLD = """        let mut d: usize = 0;
"""
V5_CONS_POSITION = """        let d: usize = dst.iter().position(|b| *b == 0u8).unwrap_or(DST_CAP);
        if false {
"""


def sub(txt, old, new, hits=1):
    got = txt.count(old)
    if got != hits:
        raise SystemExit(f"substitution matched {got}, expected {hits}:\n"
                         f"{old[:200]}")
    return txt.replace(old, new)


def emit(outdir):
    """Write the R5 candidates and return `[(label, path)]`."""
    os.makedirs(outdir, exist_ok=True)
    base = open(os.path.join(PDIR, "verus.rs")).read()
    out = []

    t = sub(base, V5_ANCHOR, V5_ITEMS + "\n" + V5_ANCHOR)
    t = sub(t, V5_COPY_OLD, V5_COPY_NEW)
    t = sub(t, V5_FILL_OLD, V5_FILL_NEW)
    # `dst_copied` is only read by the fill invariant the bulk call replaced.
    t = sub(t, "        let ghost dst_copied = dst@;\n", "")
    p = os.path.join(outdir, "u1_bulk_copyfill_verus.rs")
    open(p, "w").write(t)
    out.append(("u1_bulk_copyfill", p))

    t = sub(base, V5_CONS_OLD, V5_CONS_BOUNDED)
    p = os.path.join(outdir, "u4_bounded_consumer_verus.rs")
    open(p, "w").write(t)
    out.append(("u4_bounded_consumer", p))

    # R3's own consumer spelling, for the `is not supported` measurement. The
    # `if false {` keeps the following block syntactically attached, so the
    # ONLY thing Verus can object to is `position` itself.
    t = base.replace(V5_CONS_HEAD_OLD, V5_CONS_POSITION, 1)
    t = sub(t, "        assert(d as int == scan_dst(dst@, 0));\n",
            "        }\n        assert(d as int == scan_dst(dst@, 0));\n")
    p = os.path.join(outdir, "u5_position_consumer_verus.rs")
    open(p, "w").write(t)
    out.append(("u5_position_consumer", p))
    return out


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        REPO, ".temp", "p13", "spellings")
    for label, path in emit(d):
        print(f"  {label:22s} {os.path.relpath(path, REPO)}")
