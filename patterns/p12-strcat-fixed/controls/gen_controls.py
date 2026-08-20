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

Six families:

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
  **m*  the bulk-copy lowering, de-confounded** (TASK_040_REVIEW major 5).
        ../NOTES.md 3a's four cells confound "where the check is" with "which
        call it is", because the only once-per-string cell is also the only
        `copy_from_slice` cell. `m1` is a *safe byte loop* with no bulk call
        anywhere in its source and it still lowers to `memcpy`; `m4` is R4 with
        only the SOURCE load checked and it does not. Together they say the
        lowering needs BOTH ends of the copy free of a per-iteration check.
  **k*  the counter-design to ../NOTES.md 1's structural claim** (blocker 1 of
        TASK_040_REVIEW). p12 published "a row on which a write bug fires cannot
        also be a checksum-agreeing row" as a law about writes. It is a law
        about p12's FOLD. Zero-initialise `dst`, fold it at fixed extent, drop
        `dlen` from the result, and put rejection exactly at capacity, and the
        checked and unchecked kernels print IDENTICAL checksums while the
        unchecked one still executes an out-of-bounds store. Run them on
        `fillreject.bin`, which this file also builds. ⚠ The price is that the
        unchecked cell executes UB on every call, so it is a CONTROL and this
        pattern does not ship it as a row.
  **a*  route A, built.** The plain additive capacity test with its `usize`
        overflow discharged p17's way. ../NOTES.md 11a used to call p12's R4
        endpoint zero-width on the inference that this could not verify; it
        verifies (15/0, twin 18/0) and is 17.00/92.00 Ir/call cheaper than the
        shipped R4. Out of contract (`required[1]`), so a control and not a
        rung -- but the endpoint it collapsed is not degenerate.

`pads.py` in this directory attributes the surviving panic landing pads of any
of these to source `line:col`, which is what turns a pad COUNT into a claim
about which check survived.

Two blobs come out of here as well: `narrow.bin` for `n1` and `fillreject.bin`
for the `k*` pair. Neither is an `inputs/*.bin`, and each says why in its own
docstring below.
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

# The k* family's three edits, named so the two controls share them verbatim.
_CAPFOLD_OLD = ("    for (i = 0; i < dlen; i++)\n"
                "        acc = acc * 31 + (uint64_t)dst[i];\n"
                "    return (acc * 31 + (uint64_t)dlen) * 31 + (uint64_t)nstr;")
_CAPFOLD_NEW = ("    for (i = 0; i < DST_CAP; i++)\n"
                "        acc = acc * 31 + (uint64_t)dst[i];\n"
                "    return acc * 31 + (uint64_t)nstr;")
_CHECK_OLD = ("        /* THE CHECK. In `size_t`, so it cannot itself overflow. */\n"
              "        if (dlen + slen <= DST_CAP) {\n"
              "            for (i = p; i < q; i++)\n"
              "                dst[dlen++] = buf[off + i];\n"
              "        }")
_CHECK_NEW = ("        for (i = p; i < q; i++)\n"
              "            dst[dlen++] = buf[off + i];")

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

    # ---- the bulk-copy lowering, de-confounded ---------------------------
    ("m1_reslice_byteloop", TUNED, [
        ("            dst[dlen..dlen + slen].copy_from_slice(&w[p..q]);\n"
         "            dlen = dlen + slen;",
         "            let d: &mut [u8] = &mut dst[dlen..dlen + slen];\n"
         "            let sv: &[u8] = &w[p..q];\n"
         "            let mut i: usize = 0;\n"
         "            while i < slen {\n"
         "                d[i] = sv[i];\n"
         "                i = i + 1;\n"
         "            }\n"
         "            dlen = dlen + slen;", 1)],
     "R3 with the copy spelled as a SAFE BYTE LOOP over two reslices taken "
     "once per string -- no `copy_from_slice`, no bulk call anywhere in the "
     "source. It still lowers to `memcpy@GLIBC_2.14`, which is what separates "
     "../NOTES.md 3a's mechanism (WHERE the check is) from the alternative "
     "explanation (`copy_from_slice` is a different routine carrying its own "
     "bound). In contract: it misses only `required[3]`, same as shipped R3."),

    ("m4_u_srcchecked", UNSAFE, [
        ("            let mut i: usize = p;\n"
         "            while i < q {\n"
         "                let b: u8 = unsafe { *buf.get_unchecked(off + i) };\n"
         "                unsafe { *dst.get_unchecked_mut(dlen) = b; }\n"
         "                dlen = dlen + 1;\n"
         "                i = i + 1;\n"
         "            }",
         "            let mut i: usize = p;\n"
         "            while i < q {\n"
         "                let b: u8 = buf[off + i];\n"
         "                unsafe { *dst.get_unchecked_mut(dlen) = b; }\n"
         "                dlen = dlen + 1;\n"
         "                i = i + 1;\n"
         "            }", 1)],
     "R4 with the DESTINATION store still unchecked and only the SOURCE load "
     "checked -- the cell that decides whether `on the destination` is "
     "load-bearing in ../NOTES.md 3a. It is not: `m4` loses the `memcpy` "
     "lowering just as R2 does. A control, never a rung: it is an unsafe rung "
     "with half its `get_unchecked` calls, so it is neither R3 nor R4."),

    # ---- the counter-design: a benign row on which the write bug fires ----
    ("k1_capfold_hardened", KERNH, [
        ("    uint8_t dst[DST_CAP];", "    uint8_t dst[DST_CAP] = {0};", 1),
        (_CAPFOLD_OLD, _CAPFOLD_NEW, 1)],
     "R1h with ONE edit to the fold: `dst` is zero-initialised, the destination "
     "fold runs over the whole fixed array instead of over `dst[0..dlen]`, and "
     "`dlen` is not folded into the result. The checksum is then a function of "
     "state the out-of-bounds store cannot reach. Build it beside `k2` and run "
     "both on `fillreject.bin`."),

    ("k2_capfold_nocheck", KERNH, [
        ("    uint8_t dst[DST_CAP];", "    uint8_t dst[DST_CAP] = {0};", 1),
        (_CAPFOLD_OLD, _CAPFOLD_NEW, 1),
        (_CHECK_OLD, _CHECK_NEW, 1)],
     "`k1` with the capacity check DELETED -- the same one-line deletion that "
     "turns R1h into R1. UNSOUND BY CONSTRUCTION and built only as evidence: on "
     "`fillreject.bin` it prints k1's checksum EXACTLY, at every `n_iters`, "
     "while ASan reports `stack-buffer-overflow, WRITE of size 1`. That pair is "
     "the whole of `.memory/02-bench-rules.md`'s *a WRITE bug forces the "
     "adversarial row, it does NOT force the perf row*."),

    # ---- route A, built --------------------------------------------------
    ("a1_verus_routeA", VERUS, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {",
         "        if dlen + slen <= DST_CAP {", 1),
        ("pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)\n"
         "    requires\n        off + len <= buf@.len(),",
         "pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)\n"
         "    requires\n        off + len <= buf@.len(),\n"
         "        buf@.len() <= isize::MAX,", 1),
        # the outer walk, the scan and the copy loops each carry it
        ("buf@.len() <= usize::MAX,", "buf@.len() <= isize::MAX,", 3),
        ("    if stride_w >= 4 && stride_w <= n_blob as u64 {",
         "    if stride_w >= 4 && stride_w <= n_blob as u64 "
         "&& n_blob <= isize::MAX as usize {", 1),
        ("                4 <= stride <= n_blob,\n"
         "                buf@.len() == n_blob,",
         "                4 <= stride <= n_blob,\n"
         "                buf@.len() == n_blob,\n"
         "                n_blob <= isize::MAX,", 1)],
     "Route A of ../NOTES.md 5b, MADE TO VERIFY: the plain additive capacity "
     "test, with the `usize` overflow `r1_verus_plain_additive` fails on "
     "discharged p17's way -- one extra `requires buf@.len() <= isize::MAX`, "
     "the three loop invariants raised from `usize::MAX`, one extra driver "
     "conjunct and one extra driver invariant. `15 verified, 0 errors`, twin "
     "`18 verified, 0 errors`. Out of contract (`required[1]` pins the shipped "
     "`&&` spelling), so it is a control -- but it is the R4-side variant that "
     "shows p12's R4 endpoint is not degenerate."),

    ("a2_unsafe_routeA", UNSAFE, [
        ("        if slen <= DST_CAP && dlen + slen <= DST_CAP {",
         "        if dlen + slen <= DST_CAP {", 1),
        ("    if stride_w >= 4 && stride_w <= n_blob as u64 {",
         "    if stride_w >= 4 && stride_w <= n_blob as u64 "
         "&& n_blob <= isize::MAX as usize {", 1)],
     "Route A's exec code -- the two `a1` edits that are NOT ghost. This is "
     "what route A costs in instructions, and `md5_fn` equal to `a1`'s is what "
     "makes `R4 == R5 exact` survive the respelling. It differs from "
     "`r3_unsafe_plain_additive` by the driver's third conjunct, which is a "
     "once-per-process compare outside the loop and moves no marginal."),
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


def fillreject_blob():
    """`.temp/p12/controls/fillreject.bin` -- the input the k* pair runs on.

    64 windows, each four 32-byte strings (totalling exactly `DST_CAP`) and then
    one 8-byte string. The capacity check therefore fires **once per window**,
    on the last string only, and every byte the unchecked cell copies past the
    checked one lands entirely OUTSIDE `dst[0..128]` -- so the 128 in-bounds
    bytes are byte-identical in the two, and a fold at fixed extent cannot tell
    them apart. The overflow is exactly **+8**, which ../NOTES.md 0 measures as
    the silent, `rc=0` regime in both compilers.

    A CONTROL blob and deliberately not an `inputs/*.bin`: the unchecked cell
    executes UB on every call and no p12 row may do that."""
    import random
    import struct
    rng = random.Random(0xF1117E)
    nz = bytes([0x5a] + list(range(1, 256)))
    lens = [32, 32, 32, 32, 8]

    def window():
        body = bytearray()
        for n in lens:
            body += rng.randbytes(n).translate(nz) + b"\x00"
        return len(lens).to_bytes(4, "little") + bytes(body)

    wins = [window() for _ in range(64)]
    stride = len(wins[0])
    assert all(len(w) == stride for w in wins), "windows must be one stride"
    body = b"".join(wins)
    payload = struct.pack("<Q", stride) + body
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "fillreject.bin")
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", 20000, len(payload)) + payload)
    print(f"  {os.path.relpath(path, REPO)}  (64 windows, 4x32 then 8, "
          f"stride {stride}, the check fires once per window at +8)")


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
    fillreject_blob()
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
