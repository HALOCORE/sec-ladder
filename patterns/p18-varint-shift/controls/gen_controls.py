#!/usr/bin/env python3
"""Generate p18's control cells into `.temp/p18/ctl/`, by EXACT-STRING
substitution on the shipped sources, asserting the hit count of every edit.

`.memory/05-layout.md` item 11: a control that lives only in gitignored scratch
is the self-certifying trap one level down, and a control derived by a
hand-edited copy drifts the moment a rung moves. So every control here is a
function of the committed rung sources plus the substitutions written below, and
the script fails loudly if a substitution stops matching.

    python3 patterns/p18-varint-shift/controls/gen_controls.py
    bash    patterns/p18-varint-shift/controls/build_controls.sh
    bash    patterns/p18-varint-shift/controls/verify_controls.sh

WHAT EACH CONTROL IS FOR
------------------------

**The delete-the-check controls -- ../NOTES.md 7, the rows the pattern exists
for.** Each is a rung with the shift bound removed and NOTHING else. On p18
these are the whole result, because unlike every earlier pattern the safe-Rust
one does NOT panic at the flags this benchmark measures:

    n_noguard  safe_naive without it -- ZERO `unsafe`, and at
               `-C debug-assertions=off` it prints C's silently wrong integer
    t_noguard  safe_tuned without it
    u_noguard  unsafe without it

Each is built at O0, O0d and O3 by `build_controls.sh`, which is the only place
in this project where the `O0d` axis is exercised on a cell that can fail.

**The R3 spelling spread** -- `.memory/01-ladder.md` finding 3, which four
patterns have now got wrong by publishing a point instead of its class. TWO of
these are IN contract and two are OUT, and which is which is decided by
../spec.md's `idiom` block and not by taste:

    t_1step    R3's window reslice in the ONE-STEP form `&buf[off..off + len]`
               instead of the two-step `split_at`. **IN CONTRACT** -- the
               reslice is not named anywhere in the declaration -- and it is
               `.memory/01-ladder.md` finding 3's canonical alternate, the p04
               lever.
    t_chain    R3's two fold statements written as one chained expression.
               **IN CONTRACT**: the declaration pins `.wrapping_add(val)` and
               `.wrapping_add(nb as u64)`, which both survive.
    t_iter     R3's scan driven by `w[p..].iter()`. **OUT of contract** -- it
               does not spell `while p < len`, which is a `required` entry --
               and it is measured anyway, because the price of a declaration is
               what the declaration EXCLUDES. ⚠ ../spec.md's prose called this
               "the second in-contract R3 spelling" in an early draft and the
               `idiom` block says otherwise; the block wins and the prose was
               corrected (../NOTES.md 8).
    t_pos      R3's scan replaced by `w[p..].iter().position(|&b| b & 0x80 == 0)`
               followed by a second pass. **OUT of contract** (`forbidden`), and
               a genuinely different program: two passes over the varint.

**The priced fiats** -- ../spec.md's `forbidden` list. An entry the PROVER
already excludes costs nothing to keep; an entry only the DECLARATION excludes
is a fiat and must be priced beside the number it protects (TASK_049):

    t_wshl     the guard and the shift replaced by `wrapping_shl`, which MAKES
               THE OVERSIZED SHIFT DEFINED with exactly x86's masking
               semantics -- i.e. R1's realised behaviour written on purpose. It
               is silent under debug-assertions, under Miri and under Verus and
               still returns the wrong number.
    t_cshl     the guard in library form, `checked_shl(shift)`, folded with
               `unwrap_or(0)`.
    u_ushl     R4's shift through `unchecked_shl`, i.e. the Rust spelling of
               C's undefined behaviour, inside an `unsafe` block.
    c_mask     the C analogue of `t_wshl`: `<< (shift & 63)`. Well-defined C
               that computes R1's wrong answer on purpose, so UBSan is SILENT
               on it -- the control that separates "undefined" from "wrong".
    c_ncap     the ten-byte cap, `nb < 10` in the loop condition, instead of the
               shift guard. Safe, defined -- and a DIFFERENT FUNCTION, which is
               why ../NOTES.md 0b rejected it as p18's hardened answer.
    c_reject   the rejecting hardened spelling instead of the truncating one:
               a `bad` flag and `return 0` for the varint. Also a different
               function, and it needs a second live variable, which is the
               measured reason ../NOTES.md 0b keeps truncation.

**The Verus mutants** -- ../NOTES.md 10, and `.memory/05-layout.md` item 11 is
why they live in `.temp/` and not in the pattern dir (a `verus!` file that does
not verify cannot be in `patterns/`):

    m_noguard      verus.rs with the safety line deleted. Expected:
                   `possible bit shift underflow/overflow`.
    m_noguard_ms   the same, PLUS the kernel's `ensures` weakened to `true`.
                   **This is the mutant that decides p18's headline**: if it
                   still fails, the shift obligation is intrinsic to the
                   operator and not derived from the postcondition, so a
                   memory-safety-only proof would catch R1's bug -- and if it
                   passes, it would not. p17's control-2 lesson, third
                   instance.
    m_weakreq      `buf_get_unchecked`'s `requires` weakened to
                   `i <= v@.len()`. Expected: the SHIPPED file still verifies
                   (a weaker precondition on a trusted item removes obligations
                   from callers) and the TWIN fails -- which is exactly why the
                   twin regime exists, and it is also the control that shows
                   this item has nothing to do with p18's bug.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p18", "ctl")

GUARD_RUST = """            // THE SAFETY LINE. c/kernel.c omits exactly this.
            if shift < VBITS {
                val = val | (((c & 0x7f) as u64) << shift);
            }
"""
NOGUARD_RUST = """            // SAFETY LINE DELETED -- R1's undefined shift, written in Rust.
            val = val | (((c & 0x7f) as u64) << shift);
"""

GUARD_C = """            /* THE SAFETY LINE, and the only line c/kernel.c omits. */
            if (shift < VBITS)
                val |= (uint64_t)(c & 0x7f) << shift;
"""


def sub(text, old, new, n=1, label=""):
    got = text.count(old)
    assert got == n, f"{label}: expected {n} hit(s) for {old[:60]!r}, got {got}"
    return text.replace(old, new)


def read(rel):
    return open(os.path.join(PDIR, rel)).read()


def write(name, text):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    open(p, "w").write(text)
    print(f"  {name:24s} {len(text):6d} B")


def main():
    naive = read("safe_naive.rs")
    tuned = read("safe_tuned.rs")
    unsaf = read("unsafe.rs")
    verus = read("verus.rs")
    ck = read(os.path.join("c", "kernel.c"))
    ckh = read(os.path.join("c", "kernel_hardened.c"))

    # ---- delete-the-check ------------------------------------------------
    write("n_noguard.rs", sub(naive, GUARD_RUST, NOGUARD_RUST,
                              label="n_noguard"))
    write("t_noguard.rs", sub(tuned, GUARD_RUST, NOGUARD_RUST,
                              label="t_noguard"))
    write("u_noguard.rs", sub(unsaf, GUARD_RUST, NOGUARD_RUST,
                              label="u_noguard"))

    # ---- the O0d attribution controls, and its built-in NULL ------------
    # `-C debug-assertions=on` is a BLANKET check, not a shift check, and on
    # p18 it acts on FOUR things: the `<<`, `p = p + 1`, `nb = nb + 1`, and the
    # index expression `off + p`. (`shift` steps with `wrapping_add` and the
    # fold is `wrapping_mul`/`wrapping_add`, so neither can fire -- that is what
    # ../spec.md's wrapping-shift-step entry buys.) On the UNSAFE rung it acts
    # on a fifth: the standard library's own `assert_unsafe_precondition!`
    # inside `get_unchecked`, which is codegen'd from the CALLING crate's
    # debug-assertions flag and calls
    # `SliceIndex::get_unchecked::precondition_check`. So `O0d` does not merely
    # add a shift check to R4 -- it turns R4's `unsafe` back into a CHECKED
    # access. ../NOTES.md 5.
    #
    #   *_wrapall        p, nb and off+p made wrapping. (O0d - O0) is then the
    #                    SHIFT check alone (plus precondition_check on R4).
    #   *_wrapall_gwshl  the same, and the shift performed by `wrapping_shl`
    #                    with THE GUARD STILL PRESENT, so the program is
    #                    unchanged and no debug-assertion can fire on the shift
    #                    either. On the SAFE rung (O0d - O0) must then be ZERO
    #                    -- the NULL this decomposition has to pass -- and on
    #                    the unsafe rung it is `precondition_check` alone.
    WRAPALL = (
        ("            p = p + 1;\n            nb = nb + 1;",
         "            p = p.wrapping_add(1);\n            nb = nb.wrapping_add(1);"),
    )
    GWSHL = """            // THE SAFETY LINE, kept -- only the SHIFT OPERATOR changes, to a
            // spelling `-C debug-assertions=on` cannot fire on.
            if shift < VBITS {
                val = val | ((c & 0x7f) as u64).wrapping_shl(shift);
            }
"""
    for tag, src, idx in (("n_wrapall", naive, "buf[off + p]"),
                          ("u_wrapall", unsaf, "*buf.get_unchecked(off + p)")):
        s = src
        for o, n in WRAPALL:
            s = sub(s, o, n, label=tag + "-inc")
        s = sub(s, idx, idx.replace("off + p", "off.wrapping_add(p)"),
                label=tag + "-idx")
        write(tag + ".rs", s)
        write(tag + "_gwshl.rs", sub(s, GUARD_RUST, GWSHL, label=tag + "-gwshl"))

    # ---- R3 spelling spread ---------------------------------------------
    write("t_1step.rs", sub(
        tuned,
        "    let w: &[u8] = buf.split_at(off).1.split_at(len).0;",
        "    let w: &[u8] = &buf[off..off + len];",
        label="t_1step"))
    write("t_chain.rs", sub(
        tuned,
        """        acc = acc.wrapping_mul(31).wrapping_add(val);
        acc = acc.wrapping_mul(31).wrapping_add(nb as u64);""",
        """        acc = acc.wrapping_mul(31).wrapping_add(val)
            .wrapping_mul(31).wrapping_add(nb as u64);""",
        label="t_chain"))
    write("t_iter.rs", sub(
        tuned,
        """        while p < len {
            let c: u8 = w[p];
            p = p + 1;
            nb = nb + 1;
""" + GUARD_RUST + """            shift = shift.wrapping_add(7);
            if c & 0x80 == 0 {
                break;
            }
        }
""",
        """        for &c in w[p..].iter() {
            nb = nb + 1;
""" + GUARD_RUST.replace("            ", "            ", 1) + """            shift = shift.wrapping_add(7);
            if c & 0x80 == 0 {
                break;
            }
        }
        p = p + nb;
""",
        label="t_iter"))
    write("t_pos.rs", sub(
        tuned,
        """        while p < len {
            let c: u8 = w[p];
            p = p + 1;
            nb = nb + 1;
""" + GUARD_RUST + """            shift = shift.wrapping_add(7);
            if c & 0x80 == 0 {
                break;
            }
        }
""",
        """        let rest: &[u8] = &w[p..];
        nb = match rest.iter().position(|&b| b & 0x80 == 0) {
            Some(i) => i + 1,
            None => rest.len(),
        };
        for &c in rest[..nb].iter() {
            if shift < VBITS {
                val = val | (((c & 0x7f) as u64) << shift);
            }
            shift = shift.wrapping_add(7);
        }
        p = p + nb;
""",
        label="t_pos"))

    # ---- the priced fiats: the shl family --------------------------------
    write("t_wshl.rs", sub(
        tuned, GUARD_RUST,
        """            // FORBIDDEN: `wrapping_shl` makes the oversized shift DEFINED,
            // with exactly x86's masking semantics -- R1's realised behaviour,
            // on purpose. Silent under debug-assertions, Miri and Verus.
            val = val | ((c & 0x7f) as u64).wrapping_shl(shift);
""",
        label="t_wshl"))
    write("t_cshl.rs", sub(
        tuned, GUARD_RUST,
        """            // FORBIDDEN: `checked_shl` IS the guard, in library form.
            val = val | ((c & 0x7f) as u64).checked_shl(shift).unwrap_or(0);
""",
        label="t_cshl"))
    write("u_ushl.rs", sub(
        unsaf, GUARD_RUST,
        """            // FORBIDDEN: `unchecked_shl` is the Rust spelling of C's
            // undefined behaviour, inside an `unsafe` block.
            val = val | unsafe { ((c & 0x7f) as u64).unchecked_shl(shift) };
""",
        label="u_ushl"))

    # ---- C controls ------------------------------------------------------
    write("c_mask_kernel.c", sub(
        ck,
        "            val |= (uint64_t)(c & 0x7f) << shift;",
        "            val |= (uint64_t)(c & 0x7f) << (shift & 63); /* DEFINED */",
        label="c_mask"))
    write("c_ncap_kernel.c", sub(
        ckh,
        """            /* THE SAFETY LINE, and the only line c/kernel.c omits. */
            if (shift < VBITS)
                val |= (uint64_t)(c & 0x7f) << shift;""",
        """            val |= (uint64_t)(c & 0x7f) << shift;""",
        label="c_ncap-a").replace("        while (p < len) {",
                                  "        while (p < len && nb < 10) {"))
    write("c_reject_kernel.c",
          sub(sub(ckh,
                  "    unsigned shift;\n    uint8_t c;",
                  "    unsigned shift;\n    uint8_t c;\n    int bad;",
                  label="c_reject-decl"),
              """        val = 0;
        shift = 0;
        nb = 0;""",
              """        val = 0;
        shift = 0;
        nb = 0;
        bad = 0;""",
              label="c_reject-init")
          .replace("""            if (shift < VBITS)
                val |= (uint64_t)(c & 0x7f) << shift;""",
                   """            if (shift < VBITS)
                val |= (uint64_t)(c & 0x7f) << shift;
            else
                bad = 1;""")
          .replace("        acc = acc * 31 + val;",
                   "        acc = acc * 31 + (bad ? 0 : val);"))

    # ---- Verus mutants ---------------------------------------------------
    write("m_noguard.rs", sub(verus, GUARD_RUST, NOGUARD_RUST,
                              label="m_noguard"))
    write("m_noguard_ms.rs", sub(
        sub(verus, GUARD_RUST, NOGUARD_RUST, label="m_noguard_ms-a"),
        "        r == varint_fold(buf@, off as int, len as int),",
        "        true,",
        label="m_noguard_ms-b")
        .replace("            assert(r == varint_fold(buf@, (k * stride) as int, "
                 "stride as int));\n", ""))
    # BOTH copies -- the trusted item's and the twin's. Weakening only the
    # trusted one is caught by ../spec.md's `items` pin at gate stage 5a and
    # never reaches the twin, which carries its own contract text in source; the
    # attack the TWIN regime exists for is the author who weakens both in the
    # same commit, so that is what this mutant is.
    # THE THREE-WAY MUTANT PAIR, and the sharpest thing p18 has to say about
    # what a proof buys. `wrapping_shl` VERIFIES at the pinned vstd (measured,
    # ../NOTES.md 9), so it is available to an R4 -- and it makes the oversized
    # shift a DEFINED operation, which means Verus raises no arithmetic
    # obligation on it at all. So:
    #   m_wshl      guard replaced by `wrapping_shl`, FUNCTIONAL ensures kept
    #               -> predict: the postcondition fails (the value is wrong)
    #   m_wshl_ms   the same with the ensures weakened to `true`
    #               -> predict: VERIFIES CLEAN. The bug survives a
    #                  memory-safety-only proof, because the operation is
    #                  defined. This is the exact boundary of p18's headline
    #                  and it is measured rather than asserted.
    WSHL = """            // FORBIDDEN: `wrapping_shl` -- DEFINED, and wrong.
            val = val | ((c & 0x7f) as u64).wrapping_shl(shift);
"""
    write("m_wshl.rs", sub(verus, GUARD_RUST, WSHL, label="m_wshl"))
    write("m_wshl_ms.rs", sub(
        sub(verus, GUARD_RUST, WSHL, label="m_wshl_ms-a"),
        "        r == varint_fold(buf@, off as int, len as int),",
        "        true,",
        label="m_wshl_ms-b")
        .replace("            assert(r == varint_fold(buf@, (k * stride) as int, "
                 "stride as int));\n", ""))

    write("m_weakreq.rs", sub(
        verus, "        i < v@.len(),", "        i <= v@.len(),", n=2,
        label="m_weakreq"))
    # ---- the standalone Verus probes -------------------------------------
    # Not mutants of verus.rs: three-line files that ask ONE question each, and
    # ../NOTES.md 0.2 / 9 quote their exact output. They are generated here
    # rather than left in gitignored scratch so that the quoted error text is
    # re-derivable from the committed tree.
    write("probe_shl_bare.rs", """// Does Verus raise an obligation on an UNCONSTRAINED `<<`?
use vstd::prelude::*;
verus! {
fn shl_unconstrained(x: u64, s: u32) -> (r: u64) { x << s }
fn shl_constrained(x: u64, s: u32) -> (r: u64) requires s < 64, { x << s }
fn main() { }
}
""")
    write("probe_shl_family.rs", """// Is the forbidden shl family AVAILABLE to an R4 at the pinned vstd?
// `.memory/01-ladder.md`: read the ERROR TEXT, not the exit code --
// `is not supported` disqualifies (it forces a new TRUSTED item);
// `postcondition not satisfied` disqualifies nothing.
use vstd::prelude::*;
verus! {
fn f_wrapping(x: u64, s: u32) -> u64 { x.wrapping_shl(s) }
fn f_checked(x: u64, s: u32) -> u64 { x.checked_shl(s).unwrap_or(0) }
fn f_overflowing(x: u64, s: u32) -> u64 { x.overflowing_shl(s).0 }
fn main() { }
}
""")
    # ⚠ `probe_shl_family.rs` ABORTS on `checked_shl` / `overflowing_shl` being
    # `is not supported`, so it prints NO verdict for `wrapping_shl` -- and
    # TASK_051_REVIEW M2 found ../NOTES.md quoting `probe_shl_bare.rs` (the `<<`
    # probe, which errors) beside the `wrapping_shl` result. The claim was true
    # and no committed generator produced the probe that established it. These
    # two do.
    write("probe_shl_wrapping.rs", """// Does `wrapping_shl` carry an obligation at the pinned vstd? ALONE, because
// `probe_shl_family.rs` aborts on its other two functions before saying.
use vstd::prelude::*;
verus! {
fn f_wrapping(x: u64, s: u32) -> u64 { x.wrapping_shl(s) }
fn main() { }
}
""")
    write("probe_shl_wrapping_spec.rs", """// ...and it is not merely UNOBLIGATED: it has a real vstd SPECIFICATION, so a
// false `ensures` fails with `postcondition not satisfied` rather than with
// `is not supported`. `.memory/01-ladder.md`: read the error text.
use vstd::prelude::*;
verus! {
fn f_wrapping_zero(x: u64, s: u32) -> (r: u64) ensures r == 0u64, { x.wrapping_shl(s) }
fn main() { }
}
""")
    write("probe_shl_unchecked.rs", """// ...and `unchecked_shl`, separately, because it is `unsafe`.
use vstd::prelude::*;
verus! {
fn f_unchecked(x: u64, s: u32) -> u64 { unsafe { x.unchecked_shl(s) } }
fn main() { }
}
""")
    print(f"controls in {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
