#!/usr/bin/env python3
"""Generate p09's controls into `.temp/p09/controls/`, by EXACT-STRING
substitution off the shipped rungs, asserting every hit count.

    python3 patterns/p09-bitset/controls/gen_controls.py [--list]

Why a generator rather than committed sources (`.memory/05-layout.md` demand 11):
a Verus control that does not verify cleanly cannot live in a pattern dir at all
-- `check.py` requires every `.rs` in the dir carrying a `verus!` block to be
pinned in `verus.obligations` and fails the gate for any pinned file with
`n_err > 0` -- and `build.py`'s `--cell` list is closed. So the most valuable
controls, the ones that show what an obligation is load-bearing *for*, have
nowhere to live except `.temp/`. This file is what makes them reproducible; it
is inside `source_sha256` (the glob covers `patterns/*/controls/*.py`), and every
substitution asserts its own hit count so a control cannot silently drift off the
rung it claims to be one edit from.

`REPO` is derived from `__file__`, and the `#[path = "../../common/driver.rs"]`
include is rewritten to the real, hashed file -- both are the fixes TASK_022 and
TASK_023 landed on p08's and p16's generators after measuring that a control
emitted into `.temp/` resolves `../../common/driver.rs` to a *gitignored copy*
and therefore compiles by luck on this checkout and not at all on a fresh clone.

THE FOUR FAMILIES
=================
**1. SEEDING (`m_*`) -- p03's `m_clamp` transplanted to a shift.** p03 measured
that LLVM keeps a provably-dead check because it cannot find the invariant
UNSEEDED, and that handing it the fact as a dead test deletes the check outright
in Rust *and in C*, i.e. it is analysis seeding rather than an inability to prove
the lemma. p09 asks the same question about a bound derived through `>>`:

    m_clamp       R3 + a DEAD `if (q >> 6) >= nwords { return 0; }`
    m_clamp_hi    ...`> nwords`, ONE PAST the invariant   -- negative control
    m_clamp_far   ...`>= 0x1000000`, true but useless     -- negative control
    m_clamp_u     the same dead clamp on R4, to check it is a no-op there

**2. THE THREE BUGS (`x_*`) -- and the headline pair is `x_shift5` / `x_shift7`,
which differ from the shipped rung by ONE CHARACTER IN THE SAME POSITION.**

    x_shift7      `q >> 6` -> `q >> 7`. q/128 <= q/64, so under `q < nbits` it
                  is ALWAYS a legal word index: wrong answer, in bounds, ZERO
                  instruction cost, invisible to every rung, to ASan/UBSan, to
                  Miri and to a memory-safety-only proof. THE HEADLINE.
    x_shift5      `q >> 6` -> `q >> 5`. q/32 >= q/64, so it overshoots: a SECOND
                  SPATIAL bug, caught by memory safety alone (NOTES.md 6).
    x_mask31      `q & 63` -> `q & 31`. In range, wrong answer, invisible to
                  memory safety -- but a TWO-character edit costing +32% on R4.
    x_mask3       `q & 63` -> `q & 3`, the ONE-character mask edit, for the same
                  reason: the cost story has to be told at matched edit distance.
    x_scale4      `8 * (q >> 6)` -> `4 * (q >> 6)`, a MISALIGNED word read, and
                  the second measured member of the invisible class: the
                  obligation is `C*(nwords-1) + 8 <= 8*nwords`, so every scale
                  BELOW 8 is in bounds exactly as every shift digit ABOVE 6 is.
                  It is here so that `q >> 7` is published as the sharpest
                  member of a family and not as a curiosity (TASK_039).

**3. R3-SIDE SPAN (`r3_*`) -- in-contract respellings, for the cheapest-found
figure `.memory/01-ladder.md` requires beside any headline.**

    r3_wordslice  reslice the WORD REGION separately, so the length the derived
                  index is checked against is exactly `8*nwords`
    r3_wordchunks ...and walk the popcount pass with `chunks_exact(8)`
    r3_qchunks    walk the QUERY array with `chunks_exact(4)`

**5. THE VERUS MUTANTS (`m_shift7*`, `m_shift5*`, `m_mask31*`,
`m_control_msonly`).** These are the twelve rows of NOTES.md 6a and they are why
this file exists at all: a `verus.rs` that does not verify cleanly cannot live in
the pattern dir. `_msonly` strips the functional `ensures`, both loop invariants
that carry it and the driver's consuming assert, leaving only the memory-safety
obligations -- which is `.memory/04-verus.md`'s mandatory positive control, and
`m_control_msonly` is the row that shows the stripped probe is not blind.
`m_shift7*` is the headline: an index bug that stays inside the bitset, so the
memory-safety-only configuration discharges it at `19 verified, 0 errors` and the
whole-specification one at `20 verified, 0 errors` once the spec moves to match.

**4. THE C-SIDE BOUNDS CHECK (`c_*`).** p03's "it is not Rust-specific" result
needs a C rung that HAS a bounds check, because R1h has none -- its only check is
the range check on `q`. So:

    c_check       R1h + an explicit manual bounds check on the word read
    c_check_clamp ...plus the same dead clamp `m_clamp` uses

Every control is checked against `harness/check.py::spelling_matches` by
`.temp/p09/pins.py` before any of its numbers are quoted -- TASK_038 asks for it
because p03 shipped two controls that were out of contract and one reached a
published mechanism.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PDIR = os.path.dirname(HERE)
OUT = os.path.join(REPO, ".temp", "p09", "controls")
DRIVER_RS = os.path.join(REPO, "common", "driver.rs")


def sub(src, old, new, n=1):
    """Exact-string substitution that asserts its own hit count."""
    got = src.count(old)
    if got != n:
        raise SystemExit(f"gen_controls: expected {n} occurrence(s) of\n"
                         f"  {old!r}\nfound {got}. The shipped rung moved; fix "
                         f"this generator rather than the number it produces.")
    return src.replace(old, new)


def rung(name):
    return open(os.path.join(PDIR, name)).read()


def fixpath(src):
    """Rewrite the driver include to the real, hashed file (TASK_022/TASK_023)."""
    return sub(src, '#[path = "../../common/driver.rs"]',
               f'#[path = "{DRIVER_RS}"]')


# ---- the exact spans every control is one edit from ------------------------
GUARD_RS = """        if q < nbits {
            let w: u64 = load_u64("""
SHIFT_RS = "let w: u64 = load_u64(win, ws + (8 * (q >> 6)) as usize);"
SHIFT_RS_ABS = "let w: u64 = load_u64(buf, ws + (8 * (q >> 6)) as usize);"
SHIFT_RS_U = "let w: u64 = load_u64(buf, ws + (8 * (q >> 6)) as usize);"
MASK_RS = "if w & (1u64 << (q & 63)) != 0 {"
MASK_C = "if (w & ((uint64_t)1 << (q & 63)))"
SHIFT_C = ("if (q < nbits) {\n"
           "            uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));")

POPLOOP_RS_T = """    let mut i: u64 = 0;
    while i < nwords {
        let w: u64 = load_u64(win, ws + (8 * i) as usize);
        acc = acc.wrapping_mul(31).wrapping_add(w.count_ones() as u64);
        i = i + 1;
    }"""
QLOOP_RS_T = """    while k < nq {
        let q: u64 = load_u32(win, qs + (4 * k) as usize);"""


def controls():
    out = {}
    t = fixpath(rung("safe_tuned.rs"))
    n = fixpath(rung("safe_naive.rs"))
    u = fixpath(rung("unsafe.rs"))

    # ---- 1. seeding -------------------------------------------------------
    for tag, test in (("m_clamp", "(q >> 6) >= nwords"),
                      ("m_clamp_hi", "(q >> 6) > nwords"),
                      ("m_clamp_far", "(q >> 6) >= 0x1000000")):
        out[tag] = sub(t, GUARD_RS,
                       "        if q < nbits {\n"
                       f"            if {test} {{\n"
                       "                return 0;\n"
                       "            }\n"
                       "            let w: u64 = load_u64(")
    out["m_clamp_u"] = sub(
        u, """        if q < nbits {
            let w: u64 = load_u64(""",
        """        if q < nbits {
            if (q >> 6) >= nwords {
                return 0;
            }
            let w: u64 = load_u64(""")
    # The DISCRIMINATOR. `m_clamp` hands LLVM the fact about the WORD INDEX --
    # p03's `m_clamp` shape exactly. `m_clampb` hands it the fact about the BYTE
    # OFFSET, i.e. one inference step further along: from `q >> 6 < nwords` to
    # `ws + 8*(q>>6) + 8 <= len` needs the length check AND a multiply by 8. If
    # the first does nothing and the second deletes the checks, p09's seeding
    # failure is at the MULTIPLY and not at the shift, which is a different
    # answer from p03's and has to be measured rather than assumed.
    out["m_clampb"] = sub(t, GUARD_RS,
                          "        if q < nbits {\n"
                          "            if ws + (8 * (q >> 6)) as usize + 8 > len {\n"
                          "                return 0;\n"
                          "            }\n"
                          "            let w: u64 = load_u64(")
    # `m_clampb`'s own negative controls, p03's shape: ONE PAST the fact the
    # access needs (`+ 7` where it needs `+ 8`), and a dead test that is true but
    # says nothing about this address at all.
    out["m_clampb_lo"] = sub(t, GUARD_RS,
                             "        if q < nbits {\n"
                             "            if ws + (8 * (q >> 6)) as usize + 7 > len {\n"
                             "                return 0;\n"
                             "            }\n"
                             "            let w: u64 = load_u64(")
    out["m_clampb_far"] = sub(t, GUARD_RS,
                              "        if q < nbits {\n"
                              "            if ws + (8 * (q >> 6)) as usize + 8 > 0x7fffffff {\n"
                              "                return 0;\n"
                              "            }\n"
                              "            let w: u64 = load_u64(")
    out["m_clampb_u"] = sub(
        u, """        if q < nbits {
            let w: u64 = load_u64(""",
        """        if q < nbits {
            if ws + (8 * (q >> 6)) as usize + 8 > off + len {
                return 0;
            }
            let w: u64 = load_u64(""")
    out["m_clampb_n"] = sub(
        n, """        if q < nbits {
            let w: u64 = load_u64(""",
        """        if q < nbits {
            if ws + (8 * (q >> 6)) as usize + 8 > off + len {
                return 0;
            }
            let w: u64 = load_u64(""")

    out["m_clamp_n"] = sub(
        n, """        if q < nbits {
            let w: u64 = load_u64(""",
        """        if q < nbits {
            if (q >> 6) >= nwords {
                return 0;
            }
            let w: u64 = load_u64(""")

    # ---- 2. the two bugs --------------------------------------------------
    out["x_mask31_t"] = sub(t, MASK_RS, MASK_RS.replace("q & 63", "q & 31"))
    out["x_mask31_n"] = sub(n, MASK_RS, MASK_RS.replace("q & 63", "q & 31"))
    out["x_mask31_u"] = sub(u, MASK_RS, MASK_RS.replace("q & 63", "q & 31"))
    out["x_shift5_t"] = sub(t, SHIFT_RS, SHIFT_RS.replace("q >> 6", "q >> 5"))
    out["x_shift5_n"] = sub(n, SHIFT_RS_ABS, SHIFT_RS_ABS.replace("q >> 6", "q >> 5"))
    out["x_shift5_u"] = sub(u, SHIFT_RS_U, SHIFT_RS_U.replace("q >> 6", "q >> 5"))
    # THE HEADLINE PAIR. `q >> 7` is the SAME character position as `q >> 5` and
    # the opposite direction: q/128 <= q/64, so under `q < nbits` the index is
    # always legal (q/128 <= q/64 < ceil(nbits/64) == nwords). Nothing in the
    # ladder sees it -- not the bounds check, not ASan/UBSan, not Miri, not the
    # memory-safety proof -- and it costs zero instructions.
    out["x_shift7_t"] = sub(t, SHIFT_RS, SHIFT_RS.replace("q >> 6", "q >> 7"))
    out["x_shift7_n"] = sub(n, SHIFT_RS_ABS, SHIFT_RS_ABS.replace("q >> 6", "q >> 7"))
    out["x_shift7_u"] = sub(u, SHIFT_RS_U, SHIFT_RS_U.replace("q >> 6", "q >> 7"))
    # `q & 31` is a TWO-character substitution ("63" -> "31"); `q & 3` is the
    # one-character one, so the mask bug's R4 cost can be quoted at the same edit
    # distance as the index bug's. Both are in range and both are invisible.
    out["x_mask3_u"] = sub(u, MASK_RS, MASK_RS.replace("q & 63", "q & 3"))
    # The SECOND member of the invisible class, found by looking one step past
    # `q >> 7` (TASK_039). The access needs `ws + C*(q>>6) + 8 <= buf.len()`,
    # which the invariants reduce to `C*(nwords-1) + 8 <= 8*nwords`: true for
    # every C <= 7 and false for C = 9. So a misaligned read at HALF the stride
    # is in bounds on every input, wrong on every input, and one byte of machine
    # code away from the shipped rung -- the SIB scale field.
    out["x_scale4_t"] = sub(t, SHIFT_RS, SHIFT_RS.replace("8 * (q >> 6)",
                                                          "4 * (q >> 6)"))
    out["x_scale4_n"] = sub(n, SHIFT_RS_ABS,
                            SHIFT_RS_ABS.replace("8 * (q >> 6)",
                                                 "4 * (q >> 6)"))
    out["x_scale4_u"] = sub(u, SHIFT_RS_U,
                            SHIFT_RS_U.replace("8 * (q >> 6)",
                                               "4 * (q >> 6)"))

    # ---- 3. the R3-side span ---------------------------------------------
    out["r3_wordslice"] = sub(
        sub(t, """    let ws: usize = 8;
    let qs: usize = ws + (8 * nwords) as usize;""",
            """    let ws: usize = 8;
    let qs: usize = ws + (8 * nwords) as usize;
    let wr: &[u8] = &win[ws..qs];"""),
        SHIFT_RS, "let w: u64 = load_u64(wr, (8 * (q >> 6)) as usize);")
    out["r3_wordchunks"] = sub(
        out["r3_wordslice"], POPLOOP_RS_T,
        """    let mut i: u64 = 0;
    for c in wr.chunks_exact(8) {
        let w: u64 = load_u64(c, 0);
        acc = acc.wrapping_mul(31).wrapping_add(w.count_ones() as u64);
        i = i + 1;
    }
    let _ = i;""")
    out["r3_qchunks"] = sub(
        sub(t, QLOOP_RS_T,
            """    let qr: &[u8] = &win[qs..qs + (4 * nq) as usize];
    for c in qr.chunks_exact(4) {
        let q: u64 = load_u32(c, 0);"""),
        """        k = k + 1;
    }
    acc = acc.wrapping_mul(31).wrapping_add(hits);""",
        """        k = k + 1;
    }
    let _ = k;
    acc = acc.wrapping_mul(31).wrapping_add(hits);""")

    # THE CHEAPEST IN-CONTRACT SAFE SPELLING FOUND: all three levers at once --
    # walk the query array with `chunks_exact(4)`, and seed the optimiser with
    # the byte-offset fact the shift-derived access needs.
    out["r3_best"] = sub(out["r3_qchunks"], GUARD_RS,
                         "        if q < nbits {\n"
                         "            if ws + (8 * (q >> 6)) as usize + 8 > len {\n"
                         "                return 0;\n"
                         "            }\n"
                         "            let w: u64 = load_u64(")

    # ---- 5. the Verus mutants --------------------------------------------
    v = fixpath(rung("verus.rs"))
    VSHIFT = "let w: u64 = load_u64(buf, ws + (8 * (q >> 6)) as usize);"
    VMASK = "if w & (1u64 << (q & 63)) != 0 {"
    VPROOF = """            proof {
                lemma_guard_bounds_word(q, nbits);
                lemma_and63_is_mod64(q);
            }"""
    QINV = """            qrun(buf@, ws as int, qs as int, k as int, nq as int, nbits, acc, hits) == qrun(
                buf@,
                ws as int,
                qs as int,
                0,
                nq as int,
                nbits,
                0,
                0,
            ),
"""
    WINV = """            wrun(buf@, ws as int, i as int, nwords as int, acc) == qrun(
                buf@,
                ws as int,
                (ws + 8 * nwords) as int,
                0,
                nq as int,
                nbits,
                0,
                0,
            ),
"""
    ENS = """    ensures
        r == bitset_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,"""
    CONSUME = """            // Ghost only: this is what *consumes* the kernel's `ensures`.
            assert(r == bitset_fold(buf@, (k * stride) as int, stride as int));
"""

    def msonly(src):
        """Strip the FUNCTIONAL specification and leave the memory-safety
        obligations. `.memory/04-verus.md`: without this control a clean run
        after stripping proves nothing, because it is equally consistent with
        the probe being blind -- which is what `m_control_msonly` rules out."""
        src = sub(src, QINV, "")
        src = sub(src, WINV, "")
        src = sub(src, ENS, """{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,""")
        return sub(src, CONSUME, "")

    out["m_control_msonly"] = msonly(v)
    out["m_shift5"] = sub(v, VSHIFT, VSHIFT.replace("q >> 6", "q >> 5"))
    out["m_shift5_msonly"] = msonly(out["m_shift5"])
    out["m_shift5_spec"] = sub(
        out["m_shift5"],
        "pub open spec fn word_of(q: u64) -> int {\n    q as int / 64\n}",
        "pub open spec fn word_of(q: u64) -> int {\n    q as int / 32\n}")
    # ---- 5b. `q >> 7`, the UNDERSHOOTING index ---------------------------
    # The same four rows as the mask bug, on an INDEX. `m_shift7_bare` shows what
    # the one ghost line buys: without it the proof cannot even see that the
    # smaller shift is bounded by the larger, so it fails for a proof-weakness
    # reason (the same shape as the bare `q & 31`, NOTES.md 6a's caveat). With it
    # the only remaining error is the FUNCTIONAL one, and stripping the
    # functional spec leaves 19/0 -- the index bug memory safety cannot see.
    P7 = VPROOF.replace(
        "            }",
        "                assert((q >> 7) <= (q >> 6)) by (bit_vector);\n            }")
    out["m_shift7_bare"] = sub(v, VSHIFT, VSHIFT.replace("q >> 6", "q >> 7"))
    s7 = sub(out["m_shift7_bare"], VPROOF, P7)
    out["m_shift7"] = s7
    out["m_shift7_msonly"] = msonly(s7)
    # ...and the author's misunderstanding reaching the specification, which is
    # `m_mask31_spec`'s row for the index. `word_of` alone is not enough: the
    # bridge lemma still asserts `(q >> 6) == word_of(q)`, which is then FALSE,
    # so it fails for a proof-engineering reason rather than a semantic one
    # (17 verified, 2 errors). Move the lemma too and it is 20 verified, 0 errors.
    out["m_shift7_spec"] = sub(
        s7, "pub open spec fn word_of(q: u64) -> int {\n    q as int / 64\n}",
        "pub open spec fn word_of(q: u64) -> int {\n    q as int / 128\n}")
    out["m_shift7_spec2"] = sub(
        out["m_shift7_spec"],
        """pub proof fn lemma_guard_bounds_word(q: u64, nbits: u64)
    requires
        q < nbits,
    ensures
        (q >> 6) == word_of(q),
        (q >> 6) < nwords_of(nbits),
{
    lemma_shr6_is_div64(q);
}""",
        """pub proof fn lemma_guard_bounds_word(q: u64, nbits: u64)
    requires
        q < nbits,
    ensures
        (q >> 7) == word_of(q),
        (q >> 7) < nwords_of(nbits),
{
    lemma_shr6_is_div64(q);
    assert(vstd::arithmetic::power2::pow2(7) == 128) by {
        vstd::arithmetic::power2::lemma2_to64();
    }
    assert((q >> 7) <= (q >> 6)) by (bit_vector);
}""")

    # ...and the scale edit on the proof side. NOTE THE ASYMMETRY, measured:
    # this one needs NO ghost line at all. `m_scale4` fails only the functional
    # invariant (17/1) and `m_scale4_msonly` is `18 verified, 0 errors` off the
    # shipped proof text -- where `q >> 7` needed `assert((q >> 7) <= (q >> 6))
    # by (bit_vector)` before the memory-safety side would close. The reason is
    # that `4*(q>>6) + 8 <= 8*nwords` is LINEAR in facts the loop invariant
    # already carries, while `q >> 7 < nwords` is a bit-vector fact about a
    # shift the invariant never mentions.
    out["m_scale4"] = sub(v, VSHIFT, VSHIFT.replace("8 * (q >> 6)",
                                                    "4 * (q >> 6)"))
    out["m_scale4_msonly"] = msonly(out["m_scale4"])

    m31 = sub(v, VMASK, VMASK.replace("q & 63", "q & 31"))
    # `q & 31` also fails a SECOND, non-substantive obligation -- the shift-amount
    # bound on `1u64 << (q & 31)` -- because the supporting lemma names 63 and
    # nothing then proves `(q & 31) < 64`. Supply it, so the single remaining
    # error is the functional one. NOTES.md 6a says to quote THIS row.
    out["m_mask31_fixshift"] = sub(
        m31, VPROOF,
        VPROOF.replace("            }",
                       "                assert((q & 31) < 64) by (bit_vector);\n            }"))
    out["m_mask31_msonly"] = msonly(out["m_mask31_fixshift"])
    out["m_mask31_spec"] = sub(
        sub(sub(m31,
                "pub open spec fn bit_of(q: u64) -> u64 {\n    (q as int % 64) as u64\n}",
                "pub open spec fn bit_of(q: u64) -> u64 {\n    (q as int % 32) as u64\n}"),
            VPROOF,
            VPROOF.replace("            }",
                           "                assert((q & 31) == (q as int % 32) as u64) by (bit_vector);\n"
                           "                assert((q & 31) < 64) by (bit_vector);\n            }")),
        "        (q & 63) == bit_of(q),\n", "")

    # ---- 4. the C side ----------------------------------------------------
    c = rung(os.path.join("c", "kernel_hardened.c"))
    out["c_check.c"] = sub(
        c, SHIFT_C,
        "if (q < nbits) {\n"
        "            if (ws + (size_t)(8 * (q >> 6)) + 8 > buf_len)\n"
        "                return 0;\n"
        "            uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));")
    out["c_check_clamp.c"] = sub(
        out["c_check.c"],
        "if (ws + (size_t)(8 * (q >> 6)) + 8 > buf_len)",
        "if ((q >> 6) >= nwords)\n"
        "                return 0;\n"
        "            if (ws + (size_t)(8 * (q >> 6)) + 8 > buf_len)")
    out["x_mask31.c"] = sub(
        c, "            if (w & ((uint64_t)1 << (q & 63)))\n"
           "                hits = hits + 1;",
        "            if (w & ((uint64_t)1 << (q & 31)))\n"
           "                hits = hits + 1;")
    out["x_shift5.c"] = sub(
        c, "if (q < nbits) {\n"
           "            uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));",
        "if (q < nbits) {\n"
        "            uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 5)));")
    out["x_shift7.c"] = sub(
        c, "if (q < nbits) {\n"
           "            uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 6)));",
        "if (q < nbits) {\n"
        "            uint64_t w = load_u64(buf, ws + (size_t)(8 * (q >> 7)));")
    out["c_check_clamp.c"] = sub(out["c_check_clamp.c"], "    (void)buf_len;",
                                 "    /* buf_len is used below */")
    out["c_check.c"] = sub(out["c_check.c"], "    (void)buf_len;",
                           "    /* buf_len is used below */")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    cs = controls()
    if a.list:
        for k in sorted(cs):
            print(k)
        return 0
    os.makedirs(OUT, exist_ok=True)
    for k, v in sorted(cs.items()):
        name = k if k.endswith(".c") else k + ".rs"
        open(os.path.join(OUT, name), "w").write(v)
        print(f"  {name:22s} {len(v):6d} B")
    print(f"{len(cs)} control(s) -> {os.path.relpath(OUT, os.getcwd())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
