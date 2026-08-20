#!/usr/bin/env python3
"""p04: generate every control and every proof mutant from the SHIPPED sources.

`.memory/05-layout.md` item 11: a Verus file that does not verify cleanly cannot
live in a pattern directory, and `.memory/02-bench-rules.md` records the closed
residual that a control generator must not emit sources which compile against a
*gitignored* copy of `common/`. So every control here is

  * derived from the shipped source by **exact-string substitution with an
    asserted hit count**, so it cannot silently drift when the rung is edited;
  * rewritten to point at the **real, hashed** `common/driver.rs` by an
    absolute path derived from `__file__`;
  * written under `.temp/p04/controls/`, never into the pattern directory.

    python3 patterns/p04-ring-buffer/controls/gen_controls.py
    python3 patterns/p04-ring-buffer/controls/gen_controls.py --list

Four families:

  cap60_*      **the pattern's independent variable.** The identical sources
               with `RING_CAP = 60`, i.e. NOT a power of two. `%` is then a
               magic-number division rather than a mask, LLVM's known-bits
               analysis has nothing to carry around the loop-carried phi, and
               BOTH ring bounds checks come back in the safe rung. These are
               CONTROLS and not rungs: p04's contract fixes `RING_CAP = 64`.
  r3_* / r4_*  admissible-class searches. The R3 ones are safe Rust and cost
               nothing to admit; the R4 ones are `unsafe` and are **not rungs
               until their R5 twin verifies** (`.memory/01-ladder.md`: a rung
               covered by an `identity` pin is chained to the prover), so each
               ships a `*_twin.rs` and `../NOTES.md` 10b has the verdicts.
  m_*          mechanism controls. Each prices one named lever. `m_mask` is out
               of contract by `idiom.forbidden`; the `m_clamp*` are out by
               JUDGEMENT and not by the ruler (dead code inserted to move a
               number), which is why the unsafe one ships a twin.
  p_* / m_*_msonly
               proof mutants. The `p_*` must FAIL Verus, each for a different
               reason. The `_msonly` family strips the FUNCTIONAL specification
               — the kernel's `ensures`, the relational loop invariant that
               carries it, and the driver's consuming assert — leaving only the
               memory-safety obligations. That is p09's construction, and
               `.memory/04-verus.md` makes the positive controls mandatory: a
               clean run after stripping proves nothing on its own, because it
               is equally consistent with the probe being blind.
               `m_control_msonly`, `m_nomod_msonly`, `m_offby1_msonly` and the
               three `m_false_*_msonly` are what rule that out.

Every `r3_*` and `cap60_*` here is checked against the gate's own ruler
(`harness/check.py::spelling_matches`) before any of its numbers is quoted;
`.temp/p04/pins.py <file>` prints that verdict for any candidate file.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p04", "controls")

# The shipped `#[path]` is pattern-relative; a control under .temp/ would
# resolve it to a copy that is not in `source_sha256`. Rewrite it to the real
# file, derived from this script's own location so a fresh clone works.
PATH_SHIPPED = '#[path = "../../common/driver.rs"]'
PATH_FIX = f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]'


def src(name):
    return open(os.path.join(PDIR, name)).read()


def sub(text, pairs, name):
    """Apply (old, new, n) substitutions, asserting each hit count."""
    for old, new, n in pairs:
        got = text.count(old)
        if got != n:
            raise SystemExit(f"{name}: expected {n} occurrence(s) of\n---\n{old}\n---\n"
                             f"got {got}. The shipped source moved under this "
                             f"control; fix the substitution rather than the count.")
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------------------
# THE POWER-OF-TWO LEVER. One edit, and ../NOTES.md 1a measures that it is the
# largest single effect in this pattern.
# ---------------------------------------------------------------------------
CAP60 = [("const RING_CAP: usize = 64;", "const RING_CAP: usize = 60;", 1)]
CAP60_C = [("#define RING_CAP 64", "#define RING_CAP 60", 1)]

# The dead test that hands LLVM the invariant R5 proves — p03's `m_clamp`,
# transplanted. Placed at the top of the LOOP BODY: p03 measured that placement
# decides whether it seeds anything, and ../NOTES.md 0b reproduces that (placed
# before the loop, where both cursors are 0, it is a no-op).
CLAMP_IN = ("    while k < nops {\n",
            "    while k < nops {\n"
            "        if tail >= RING_CAP || head >= RING_CAP { return 0; }\n", 1)

CAP60_CTL = {
    # The safe rung at 60: both ring bounds checks come back.
    "cap60_r3": ("safe_tuned.rs", CAP60),
    # The unsafe rung at 60: no checks, but `%` is now a real division.
    "cap60_r4": ("unsafe.rs", CAP60),
    # The naive rung at 60.
    "cap60_r2": ("safe_naive.rs", CAP60),
    # The safe rung at 60 PLUS the dead clamp: does p03's control delete the
    # check that `%` no longer deletes for us?
    "cap60_r3_clamp": ("safe_tuned.rs", CAP60 + [CLAMP_IN]),
    # ... and the same lever on the unsafe side, so it is read on both.
    "cap60_r4_clamp": ("unsafe.rs", CAP60 + [CLAMP_IN]),
    # The control that says the clamp is a no-op where the operator already
    # carries the bound: the same dead test at RING_CAP = 64.
    "cap64_r3_clamp": ("safe_tuned.rs", [CLAMP_IN]),
}

# ---------------------------------------------------------------------------
# R3 side: in-contract safe spellings. `.memory/01-ladder.md` finding 3 requires
# at least two independent in-contract R3 spellings with the cheaper quoted;
# these are the alternates and ../NOTES.md 10a is the span they define.
# ---------------------------------------------------------------------------
R3 = {
    # The op stream consumed as 5-byte records instead of indexed by `5*k`.
    # In contract: the cursor spelling is deliberately NOT pinned.
    "r3_chunks": [
        ("""    let mut k: usize = 0;
    while k < nops {
        let op: u8 = w[4 + 5 * k];
        let val: u64 = w[5 + 5 * k] as u64 + 256 * (w[6 + 5 * k] as u64)
            + 65536 * (w[7 + 5 * k] as u64)
            + 16777216 * (w[8 + 5 * k] as u64);""",
         """    for rec in w[4..4 + 5 * nops].chunks_exact(5) {
        let op: u8 = rec[0];
        let val: u64 = rec[1] as u64 + 256 * (rec[2] as u64)
            + 65536 * (rec[3] as u64)
            + 16777216 * (rec[4] as u64);""", 1),
        ("""        k = k + 1;
    }
    acc""", """    }
    acc""", 1),
    ],
    # `for k in 0..nops` instead of the `while` cursor.
    "r3_forloop": [
        ("""    let mut k: usize = 0;
    while k < nops {""", """    for k in 0..nops {""", 1),
        ("""        k = k + 1;
    }
    acc""", """    }
    acc""", 1),
    ],
    # The cheapest lever the SAFE class has on p03 -- an assertion at the loop
    # head handing LLVM the invariant. Here there is nothing left for it to
    # delete, which is the point of measuring it.
    "r3_assert_head": [
        ("    while k < nops {\n",
         "    while k < nops {\n"
         "        assert!(head < RING_CAP && tail < RING_CAP);\n", 1),
    ],
    # ---------------------------------------------------------------------
    # THE TWO-STEP RESLICE, and it is the cheapest in-contract R3 found
    # (TASK_042_REVIEW blocker 1, landed at TASK_044). `+4.00` against R4's
    # 3363/11662 on both blobs, where every spelling above measures `+5.00`.
    #
    # ⚠ It is NOT bounds-check removal. Both forms keep both checks; the
    # difference is REGISTER ALLOCATION, and it is four instructions against
    # five in the entry block (`%rdi` buf, `%rsi` buf_len, `%rdx` off,
    # `%rcx` len):
    #
    #   shipped   mov %rcx,%rax ; add %rdx,%rax ; jb ; cmp %rsi,%rax ; ja
    #   two-step  sub %rdx,%rsi ; jb            ; cmp %rsi,%rcx ; ja
    #
    # `off + len` needs a scratch register because `%rcx` is still live as
    # `len`; `buf_len - off` is computed IN PLACE in `%rsi`, which is dead
    # afterwards. The two-step form also has TWO landing pads to the shipped
    # rung's one, which is the cleanest available demonstration that pad count
    # is not the tax (../NOTES.md 10a).
    #
    # Six spellings, FIVE distinct machine codes, all at the same number; two
    # of the five are here and the rest are listed in ../NOTES.md 10a. The
    # `idiom` block pins no reslice spelling, so all of them are in contract by
    # construction -- what failed was the "cheapest found" claim, not the
    # declaration.
    "r3_reslice2_get": [
        ("    let w: &[u8] = &buf[off..off + len];",
         "    let w: &[u8] = buf.get(off..).unwrap().get(..len).unwrap();", 1),
    ],
    "r3_reslice2_split": [
        ("    let w: &[u8] = &buf[off..off + len];",
         "    let w: &[u8] = buf.split_at(off).1.split_at(len).0;", 1),
    ],
}

# ---------------------------------------------------------------------------
# R4 side. NOT rungs until their twin verifies.
# ---------------------------------------------------------------------------
R4 = {
    "r4_forloop": [
        ("""    let mut k: usize = 0;
    while k < nops {""", """    for k in 0..nops {""", 1),
        ("""        k = k + 1;
    }
    acc""", """    }
    acc""", 1),
    ],
    # The raw-pointer spelling, which p03's and p07's `r4_ptr` showed is
    # `is not supported` at the pinned vstd. Built so the disqualification is
    # a measurement here too rather than an inheritance.
    "r4_ptr": [
        ("""                unsafe { *ring.get_unchecked_mut(tail) = val; }""",
         """                unsafe { *ring.as_mut_ptr().add(tail) = val; }""", 1),
        ("""                    .wrapping_add(unsafe { *ring.get_unchecked(head) });""",
         """                    .wrapping_add(unsafe { *ring.as_ptr().add(head) });""", 1),
    ],
}

# The Verus twin of each R4 candidate: the same edit applied to verus.rs.
R4_TWIN = {
    "r4_forloop_twin": ("verus.rs", [
        ("    let mut k: usize = 0;\n", "", 1),
        ("    while k < nops\n        invariant\n",
         "    for k in 0..nops\n        invariant\n", 1),
        ("""            ) == run(buf@, off as int, 0, nops as int, zero_ring(), 0, 0, 0),
        decreases nops - k,
    {""",
         """            ) == run(buf@, off as int, 0, nops as int, zero_ring(), 0, 0, 0),
    {""", 1),
        ("""        k = k + 1;
    }
    acc""", """    }
    acc""", 1),
    ]),
    "r4_ptr_twin": ("verus.rs", [
        ("""                ring_set_unchecked(&mut ring, tail, val);""",
         """                unsafe { *ring.as_mut_ptr().add(tail) = val; }""", 1),
        ("""ring_get_unchecked(&ring, head)""",
         """(unsafe { *ring.as_ptr().add(head) })""", 1),
    ]),
    "m_clamp_unsafe_twin": ("verus.rs", [
        ("""    while k < nops
        invariant""",
         """    if tail >= RING_CAP || head >= RING_CAP { return 0; }
    while k < nops
        invariant""", 1),
    ]),
}

# ---------------------------------------------------------------------------
# Mechanism controls.
# ---------------------------------------------------------------------------
MECH = {
    # `idiom.forbidden[0]`: the mask spelling of the modulus. At RING_CAP = 64
    # this is byte-identical to the shipped `%`, which is why ../NOTES.md 10a
    # can say the exclusion protects no number.
    "m_mask": ("safe_tuned.rs", [
        ("(tail + 1) % RING_CAP != head", "(tail + 1) & (RING_CAP - 1) != head", 1),
        ("tail = (tail + 1) % RING_CAP;", "tail = (tail + 1) & (RING_CAP - 1);", 1),
        ("head = (head + 1) % RING_CAP;", "head = (head + 1) & (RING_CAP - 1);", 1),
    ]),
    # p03's `m_clamp` on the unsafe side at RING_CAP = 64, so that the R4
    # endpoint is searched with the same lever as the R3 one.
    "m_clamp_unsafe": ("unsafe.rs", [
        ("    while k < nops {\n",
         "    if tail >= RING_CAP || head >= RING_CAP { return 0; }\n"
         "    while k < nops {\n", 1),
    ]),
    # The C rung with a manual bounds check on the ring read, so p03's
    # "it is not a fact about safe Rust" question can be asked here too.
    "c_ringcheck": ("c/kernel_hardened.c", [
        ("""            if (head != tail) {
                acc = acc * 31 + ring[head];""",
         """            if (head != tail) {
                if (head >= RING_CAP) __builtin_trap();
                acc = acc * 31 + ring[head];""", 1),
    ]),
    "c_ringcheck60": ("c/kernel_hardened.c", CAP60_C + [
        ("""            if (head != tail) {
                acc = acc * 31 + ring[head];""",
         """            if (head != tail) {
                if (head >= RING_CAP) __builtin_trap();
                acc = acc * 31 + ring[head];""", 1),
    ]),
    "c_cap60": ("c/kernel_hardened.c", CAP60_C),
}

# ---------------------------------------------------------------------------
# Proof mutants. `p_*` must fail; `m_*_msonly` is the invisibility probe and
# its positive controls.
# ---------------------------------------------------------------------------
NOFULL = ("""            if (tail + 1) % RING_CAP != head {
                ring_set_unchecked(&mut ring, tail, val);
                tail = (tail + 1) % RING_CAP;
            }""",
          """            ring_set_unchecked(&mut ring, tail, val);
            tail = (tail + 1) % RING_CAP;""", 1)
NOEMPTY = ("""            if head != tail {
                acc = acc.wrapping_mul(31).wrapping_add(ring_get_unchecked(&ring, head));
                head = (head + 1) % RING_CAP;
            }""",
           """            acc = acc.wrapping_mul(31).wrapping_add(ring_get_unchecked(&ring, head));
            head = (head + 1) % RING_CAP;""", 1)

# The three edits that make a file MEMORY-SAFETY-ONLY: drop the kernel's
# functional `ensures`, the relational loop invariant that carries it, and the
# driver's consuming assert. Nothing about `head`, `tail` or either accessor's
# precondition is touched.
MSONLY = [
    ("""    ensures
        r == ring_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len`""",
     """{
    // Ghost only: mentioning `spec_slice_len`""", 1),
    ("""            run(
                buf@,
                off as int,
                k as int,
                nops as int,
                ring@,
                head as int,
                tail as int,
                acc,
            ) == run(buf@, off as int, 0, nops as int, zero_ring(), 0, 0, 0),
""", "", 1),
    ("""            assert(r == ring_fold(buf@, (k * stride) as int, stride as int));
""", "", 1),
]

FALSE_A = ("""    if nops == 0 {
        return 0;
    }""", """    if nops == 0 {
        return 0;
    }
    assert(false);""", 1)
FALSE_B = ("""        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);""",
           """        assert(false);
        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);""", 1)
FALSE_C = ("""    acc.wrapping_mul(31).wrapping_add(head as u64).wrapping_mul(31)
        .wrapping_add(tail as u64).wrapping_mul(31).wrapping_add(nops as u64)
}

// ---------------------------------------------------------------- driver ----""",
           """    assert(false);
    acc.wrapping_mul(31).wrapping_add(head as u64).wrapping_mul(31)
        .wrapping_add(tail as u64).wrapping_mul(31).wrapping_add(nops as u64)
}

// ---------------------------------------------------------------- driver ----""", 1)

PROOF = {
    # ---- must FAIL: the shipped configuration -----------------------------
    # One character in a TRUSTED item's `requires`, in the item AND its twin so
    # the contract pin does not move. Only 5c-twin sees it.
    "p1_weak_requires": [
        ("""fn ring_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i < v@.len(),""",
         """fn ring_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i <= v@.len(),""", 1),
        ("""fn slb_twin_ring_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i < v@.len(),""",
         """fn slb_twin_ring_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i <= v@.len(),""", 1),
    ],
    # R1's bug written into R5, WITH the functional specification in place.
    "p2_nofullguard": [NOFULL],
    # The memory-safety invariant weakened by one -- what LLVM would need to be
    # handed at RING_CAP = 60, and one past what is true.
    "p3_weak_invariant": [
        ("            tail < RING_CAP,", "            tail <= RING_CAP,", 1),
    ],
    # The OTHER guard deleted, with the specification in place.
    "p4_noemptyguard": [NOEMPTY],
    # ---- the INVISIBILITY probe, and its positive controls ---------------
    "m_control_msonly": MSONLY,
    "m_nofull_msonly": [NOFULL] + MSONLY,
    "m_noempty_msonly": [NOEMPTY] + MSONLY,
    # POSITIVE CONTROL 1: delete the `%` from the write cursor's update. The
    # program is then memory-UNSAFE and the msonly configuration must say so.
    "m_nomod_msonly": [
        ("                tail = (tail + 1) % RING_CAP;",
         "                tail = tail + 1;", 1),
    ] + MSONLY,
    # POSITIVE CONTROL 2: index one past the write cursor.
    "m_offby1_msonly": [
        ("                ring_set_unchecked(&mut ring, tail, val);",
         "                ring_set_unchecked(&mut ring, tail + 1, val);", 1),
    ] + MSONLY,
    # POSITIVE CONTROLS 3-5: `assert(false)` in three places, so a vacuous
    # context cannot be what is discharging the two above.
    "m_false_a_msonly": [FALSE_A] + MSONLY,
    "m_false_b_msonly": [FALSE_B] + MSONLY,
    "m_false_c_msonly": [FALSE_C] + MSONLY,
}


def emit(name, base, pairs):
    text = sub(src(base), pairs, name)
    if PATH_SHIPPED in text:
        text = text.replace(PATH_SHIPPED, PATH_FIX)
    ext = ".c" if base.endswith(".c") else ".rs"
    dst = os.path.join(OUT, name + ext)
    open(dst, "w").write(text)
    return dst


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    plan = ([(n, b, p) for n, (b, p) in CAP60_CTL.items()]
            + [(n, "safe_tuned.rs", p) for n, p in R3.items()]
            + [(n, "unsafe.rs", p) for n, p in R4.items()]
            + [(n, b, p) for n, (b, p) in R4_TWIN.items()]
            + [(n, b, p) for n, (b, p) in MECH.items()]
            + [(n, "verus.rs", p) for n, p in PROOF.items()])
    if a.list:
        for n, b, _ in plan:
            print(f"{n:24s} <- {b}")
        return 0
    os.makedirs(OUT, exist_ok=True)
    for n, b, p in plan:
        print("  " + os.path.relpath(emit(n, b, p), REPO))
    print(f"{len(plan)} control(s) -> {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
