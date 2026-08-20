#!/usr/bin/env python3
"""Generate p12's controls into `.temp/p12/controls/`.

`.memory/05-layout.md` item 11: a Verus file that does not verify cleanly cannot
live in the pattern directory (`check.py` requires every `.rs` there with a
`verus!` block to be pinned in `verus.obligations` and fails the gate for any
pinned file reporting errors). So every broken-on-purpose variant is **generated
from the shipped source by exact-string substitution with an asserted hit
count**, which is what stops it drifting away from the cell it is a control for.

    python3 patterns/p12-strcat-fixed/controls/gen_controls.py
    python3 patterns/p12-strcat-fixed/controls/gen_controls.py --list

Then, per ../NOTES.md:

    ./verus_run.py .temp/p12/controls/<name>.rs [--cfg slb_twin]
    ~/.cargo/bin/rustc --edition 2021 -C codegen-units=1 -C opt-level=3 \\
        -C debug-assertions=off --cfg slb_isolated \\
        .temp/p12/controls/<name>.rs -o .temp/p12/controls/<name>
    /usr/bin/gcc -std=c99 -Wall -Wextra -O3 -DSLB_ISOLATED -I common \\
        -I patterns/p12-strcat-fixed/c common/driver.c \\
        .temp/p12/controls/<name>.c patterns/p12-strcat-fixed/c/main.c \\
        -o .temp/p12/controls/<name>

Four families:

  **p*  proof mutants.** Each one must FAIL, and each for a different reason.
  **n*  the narrow-type check.** A capacity check that is present, looks right,
        and waves a 256-byte string straight through -- the answer to "R1h is
        the safe cell, so what is left to get wrong?"
  **d*  the deleted check.** What safe Rust does where C corrupts: R2 with the
        capacity check removed PANICS rather than overflowing, which is the p12
        analogue of p02's control and the evidence for "the safe rung cannot
        express the bug".
  **s*  the R3-side span.** In-contract respellings of the safe-tuned rung,
        for the cheapest-found figure `.memory/01-ladder.md` requires beside
        every headline.
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
PDIR = os.path.join(REPO, "patterns", "p12-strcat-fixed")
OUT = os.path.join(REPO, ".temp", "p12", "controls")

# Every rung source lives one directory deeper once copied into .temp, so the
# `#[path]` include has to grow one `../`.
FIXPATH = ('#[path = "../../common/driver.rs"]',
           '#[path = "../../../common/driver.rs"]')

VERUS = os.path.join(PDIR, "verus.rs")
UNSAFE = os.path.join(PDIR, "unsafe.rs")
NAIVE = os.path.join(PDIR, "safe_naive.rs")
TUNED = os.path.join(PDIR, "safe_tuned.rs")
KERNH = os.path.join(PDIR, "c", "kernel_hardened.c")

#: (name, source, [(old, new, expected_hits)], what it is for)
CONTROLS = [
    # ---- proof mutants ---------------------------------------------------
    ("p1_no_capacity_check", VERUS, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {\n",
         "        if true {\n", 1)],
     "R1's bug, written into R5. The copy loop stores at `dlen` with nothing "
     "bounding it, so `dst_set_unchecked`'s `i < old(v)@.len()` is not "
     "discharged. This is THE mutant for p12: it is the exact line c/kernel.c "
     "omits, and it must fail on the WRITE precondition and not on the "
     "postcondition."),

    ("p2_weak_write_requires", VERUS, [
        ("fn dst_set_unchecked(v: &mut [u8; 128], i: usize, x: u8)\n"
         "    requires\n        i < old(v)@.len(),",
         "fn dst_set_unchecked(v: &mut [u8; 128], i: usize, x: u8)\n"
         "    requires\n        i <= old(v)@.len(),", 1),
        ("fn slb_twin_dst_set_unchecked(v: &mut [u8; 128], i: usize, x: u8)\n"
         "    requires\n        i < old(v)@.len(),",
         "fn slb_twin_dst_set_unchecked(v: &mut [u8; 128], i: usize, x: u8)\n"
         "    requires\n        i <= old(v)@.len(),", 1)],
     "One character, in the trusted write accessor AND in its twin, so the "
     "signatures still match and `spec.md`'s item pin does not move. The "
     "SHIPPED configuration still verifies -- a weaker precondition only "
     "removes obligations from callers -- and only `--cfg slb_twin` sees it, "
     "because `v[i] = x` under `i <= v.len()` is a real out-of-bounds store. "
     "This is the whole case for the twin regime, on a WRITE."),

    ("p3_slotwise_write_ensures", VERUS, [
        ("    ensures\n        final(v)@ == old(v)@.update(i as int, x),\n{\n"
         "    unsafe {",
         "    ensures\n        final(v)@[i as int] == x,\n{\n"
         "    unsafe {", 1)],
     "The trusted write's `ensures` weakened from a whole-sequence equality to "
     "a statement about slot `i` alone -- i.e. it stops saying `nothing else "
     "moved`. `.memory/02-bench-rules.md`'s p02 worked example argues for the "
     "strong form; this mutant is what happens without it. The kernel can no "
     "longer relate `dst@` to `copy_into`, so the functional postcondition "
     "fails."),

    ("p4_taut_kernel_ensures", VERUS, [
        ("    ensures\n        r == strcat_fold(buf@, off as int, len as int),",
         "    ensures\n        r == r,", 1)],
     "The kernel's functional postcondition replaced by a tautology. It must "
     "fail at the DRIVER, where `assert(r == strcat_fold(...))` consumes it -- "
     "that assert is the only thing between the `ensures` and decoration "
     "(`.memory/04-verus.md`), and this mutant is the check that it is doing "
     "its job."),

    # ---- the narrow-type capacity check ----------------------------------
    ("n1_uchar_sum", KERNH, [
        ("        /* THE CHECK. In `size_t`, so it cannot itself overflow. */\n"
         "        if (dlen + slen <= DST_CAP) {",
         "        /* THE CHECK, in a narrower type. `dlen` is at most 128 and a\n"
         "         * 128-byte destination invites `unsigned char` for both, so\n"
         "         * this is not a strawman -- and a 256-byte string wraps the\n"
         "         * sum to 0, passes, and is copied in full. */\n"
         "        {\n"
         "        unsigned char sum = (unsigned char)(dlen + slen);\n"
         "        if (sum <= DST_CAP) {", 1),
        ("        acc = acc * 31 + (uint64_t)slen;",
         "        }\n        acc = acc * 31 + (uint64_t)slen;", 1)],
     "R1h with the capacity check computed in `unsigned char`. The check is "
     "present, reads correctly, and is defeated by any string whose length is "
     "congruent to something small mod 256."),

    # ---- what safe Rust does where C corrupts ----------------------------
    ("d1_naive_nocheck", NAIVE, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {\n",
         "        {\n", 1)],
     "R2 with the capacity check deleted -- the same edit that turns R1h into "
     "R1. In C it corrupts the frame; in safe Rust `dst[dlen] = b` PANICS, "
     "because the bound is the array's and not the programmer's. This is the "
     "p12 evidence for `the safe rung cannot express the bug`, and it is "
     "p02's control on a fixed-size destination."),

    ("d2_unsafe_nocheck", UNSAFE, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {\n",
         "        {\n", 1)],
     "R4 with the same deletion. UNSOUND BY INSPECTION and built only to be "
     "run under Miri: `get_unchecked_mut` past the array is exactly R1's bug "
     "with no canary and no ASan. It is a control, never a rung -- "
     "`.memory/01-ladder.md` forbids an unsound R4."),

    # ---- the capacity-check spelling: three routes to one obligation ------
    ("r1_verus_plain_additive", VERUS, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {",
         "        if dlen + slen <= DST_CAP {", 1)],
     "R5 with the additive capacity test alone -- route A of ../NOTES.md 5b, "
     "and the reason the shipped rungs carry a left conjunct. Verus reports "
     "`possible arithmetic underflow/overflow`: nothing at the pinned vstd "
     "bounds `slen` below `usize::MAX`, so `dlen + slen` is not provably "
     "overflow-free. Route A ships only with p17's second `requires` and a "
     "third driver conjunct, which p17 measured at zero instructions."),

    ("r2_verus_subtraction_first", VERUS, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {",
         "        if slen <= DST_CAP - dlen {", 1)],
     "R5 with the capacity test respelled subtraction-first -- route B, the "
     "idiom p02 and p16 adopted. It verifies (`15 verified, 0 errors`) and is "
     "the DEAREST of the three in instructions."),

    ("r3_unsafe_plain_additive", UNSAFE, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {",
         "        if dlen + slen <= DST_CAP {", 1)],
     "Route A's exec code, for the instruction count. It is what route A "
     "compiles to, since its extra `requires` and driver conjunct are ghost."),

    ("r4_unsafe_subtraction_first", UNSAFE, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {",
         "        if slen <= DST_CAP - dlen {", 1)],
     "Route B's exec code, for the instruction count."),

    # ---- the R3-side span ------------------------------------------------
    ("s1_tuned_indexed_fold", TUNED, [
        ("    acc = dst[..dlen]\n        .iter()\n"
         "        .fold(acc, |h, &b| h.wrapping_mul(31).wrapping_add(b as u64));",
         "    let mut i: usize = 0;\n    while i < dlen {\n"
         "        acc = acc.wrapping_mul(31).wrapping_add(dst[i] as u64);\n"
         "        i = i + 1;\n    }", 1)],
     "R3 with the destination fold spelled as an indexed loop instead of an "
     "iterator. In contract: `idiom.required[6]`'s Rust spelling pins the "
     "OPERATION (`.wrapping_mul(31).wrapping_add(`) and not the loop form, and "
     "this variant keeps it."),

    ("s2_tuned_bytefold_reslice", TUNED, [
        ("    acc = dst[..dlen]\n        .iter()\n"
         "        .fold(acc, |h, &b| h.wrapping_mul(31).wrapping_add(b as u64));",
         "    let live: &[u8] = &dst[..dlen];\n"
         "    let mut i: usize = 0;\n    while i < live.len() {\n"
         "        acc = acc.wrapping_mul(31).wrapping_add(live[i] as u64);\n"
         "        i = i + 1;\n    }", 1)],
     "R3 with the destination fold indexed through a reslice taken ONCE, so "
     "the bound the loop is checked against is the reslice's own length rather "
     "than the loop-carried `dlen`. This is p03's seeding question on p12's "
     "second range check -- the one whose bound comes from an invariant."),

    ("s3_tuned_copy_byteloop", TUNED, [
        ("            dst[dlen..dlen + slen].copy_from_slice(&w[p..q]);\n"
         "            dlen = dlen + slen;",
         "            let mut i: usize = p;\n            while i < q {\n"
         "                let b: u8 = w[i];\n"
         "                dst[dlen] = b;\n"
         "                dlen = dlen + 1;\n                i = i + 1;\n"
         "            }", 1)],
     "R3 with the copy spelled as a byte loop over the reslice instead of "
     "`copy_from_slice`. In contract -- `idiom.required[3]` pins the byte loop "
     "for R1/R1h/R2 and leaves R3 free -- and it is the R3-side variant that "
     "isolates the COPY spelling from the reslice and the iterator fold."),
]


def narrow_blob():
    """`.temp/p12/controls/narrow.bin` -- the input that separates the `size_t`
    capacity check from the `unsigned char` one.

    One window: a 256-byte string followed by an 8-byte string. The shipped R1h
    rejects the first (`256 > 128`) and accepts the second, ending with
    `dlen == 8`. `n1_uchar_sum` computes `(unsigned char)(0 + 256) == 0`, finds
    it `<= 128`, and copies all 256 bytes into a 128-byte destination.

    It is a CONTROL blob and deliberately not an `inputs/*.bin`: adding it to
    the matrix would put a ninth row through the gate for a cell the gate does
    not build."""
    import random
    import struct
    rng = random.Random(0x5EC1ADDE ^ 0xC0FFEE)
    nz = bytes([0x5a] + list(range(1, 256)))
    body = (rng.randbytes(256).translate(nz) + b"\x00"
            + rng.randbytes(8).translate(nz) + b"\x00")
    win = (2).to_bytes(4, "little") + body
    payload = struct.pack("<Q", len(win)) + win
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "narrow.bin")
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", 8, len(payload)) + payload)
    print(f"  {os.path.relpath(path, REPO)}  (one window, strings 256 + 8)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for name, src, _, why in CONTROLS:
            print(f"{name:26s} <- {os.path.relpath(src, REPO)}\n    {why}\n")
        return 0
    os.makedirs(OUT, exist_ok=True)
    narrow_blob()
    for name, src, subs, _why in CONTROLS:
        txt = open(src).read()
        for old, new, hits in subs:
            got = txt.count(old)
            if got != hits:
                print(f"gen_controls.py: {name}: pattern occurs {got} times, "
                      f"expected {hits} -- the shipped source moved under this "
                      f"control and the control is now measuring something "
                      f"else:\n  {old[:90]!r}", file=sys.stderr)
                return 1
            txt = txt.replace(old, new)
        if src.endswith(".rs"):
            txt = txt.replace(*FIXPATH)
        ext = ".c" if src.endswith(".c") else ".rs"
        path = os.path.join(OUT, name + ext)
        open(path, "w").write(txt)
        print(f"  {os.path.relpath(path, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
