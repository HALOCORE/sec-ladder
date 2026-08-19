#!/usr/bin/env python3
"""p03: generate every control and every proof mutant from the SHIPPED sources.

`.memory/05-layout.md` item 11: a Verus file that does not verify cleanly cannot
live in a pattern directory, and `.memory/02-bench-rules.md` records the closed
residual that a control generator must not emit sources which compile against a
*gitignored* copy of `common/` — p08's leaves the shipped
`#[path = "../../common/driver.rs"]` in its output, which from `.temp/` resolves
to `.temp/common/driver.rs` and works only by luck. So every control here is

  * derived from the shipped source by **exact-string substitution with an
    asserted hit count**, so it cannot silently drift when the rung is edited;
  * rewritten to point at the **real, hashed** `common/driver.rs` by an
    absolute path derived from `__file__`;
  * written under `.temp/p03/controls/`, never into the pattern directory.

    python3 patterns/p03-bounded-stack/controls/gen_controls.py
    python3 patterns/p03-bounded-stack/controls/gen_controls.py --list

Three families:

  r3_* / r4_*  admissible-class searches. The R3 ones are safe Rust and cost
               nothing to admit; the R4 ones are `unsafe` and are **not rungs
               until their R5 twin verifies** (`.memory/01-ladder.md`: a rung
               covered by an `identity` pin is chained to the prover), so each
               ships a `*_twin.rs` and `../NOTES.md` 10b has the verdicts.
  m_*          mechanism controls. Each is here to price one named lever, not
               to be a rung. Most are out of contract by `idiom.forbidden`;
               the two `m_clamp_unsafe*` are out by JUDGEMENT and not by the
               ruler (dead code inserted to move a number, `../NOTES.md` 4b),
               which is why they ship twins too — an R4 candidate the ruler
               admits is not a rung until Verus has seen it.
  p_*          proof mutants. Each must FAIL Verus, and for a different reason.

Every `r3_*` here is checked against the gate's own ruler
(`harness/check.py::spelling_matches`) at 0 forbidden hits and 0 required
misses; `.temp/p37/contract.py` prints that verdict for any candidate file.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p03", "controls")

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
# R3 side: in-contract safe spellings. `.memory/01-ladder.md` finding 3 requires
# at least two independent in-contract R3 spellings with the cheaper quoted;
# these are the alternates and ../NOTES.md 10a is the span they define.
# ---------------------------------------------------------------------------
R3 = {
    # The op stream consumed as 5-byte records instead of indexed by `5*k`.
    # In contract: the cursor spelling is deliberately NOT pinned (see the
    # `idiom.why`), and every pinned spelling survives.
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
        ("""        }
        k = k + 1;
    }
    acc.wrapping_mul(31)""",
         """        }
    }
    acc.wrapping_mul(31)""", 1),
    ],
    # The counted loop as a `for` over a range rather than a `while`.
    "r3_forloop": [
        ("""    let mut k: usize = 0;
    while k < nops {""", """    for k in 0..nops {""", 1),
        ("""        }
        k = k + 1;
    }
    acc.wrapping_mul(31)""",
         """        }
    }
    acc.wrapping_mul(31)""", 1),
    ],
    # The stack reached through a slice rather than through the array, so the
    # bound the checker uses is a runtime `len()` instead of the type's 64.
    "r3_slicestack": [
        ("""    let mut stack: [u64; STACK_CAP] = [0; STACK_CAP];""",
         """    let mut stack_arr: [u64; STACK_CAP] = [0; STACK_CAP];
    let stack: &mut [u64] = &mut stack_arr[..];""", 1),
    ],
    # ------------------------------------------------------------------
    # The invariant as a HOISTED LENGTH ASSERTION, which is what
    # `.memory/01-ladder.md`'s R3 row names as an R3 technique. These three
    # are the CHEAP end of p03's in-contract R3 class and they were missing
    # until TASK_036_REVIEW found the first one and TASK_037 the cheapest;
    # `../NOTES.md` 10a is the span they define. Against the gate's own ruler
    # (`check.spelling_matches`) all three are 0 forbidden hits, 0 required
    # misses -- `assert!` is not in `idiom.forbidden`, and none of them
    # disturbs a required spelling. They differ ONLY in where the assertion
    # sits, and that is worth three controls rather than one because the
    # placement is worth 2 Ir per dropped push and 2 per executed pop.
    #
    # `r3_assert_tail` (TASK_036_REVIEW's `x_assert`, moved to the back edge)
    # is the cheapest in-contract R3 found on BOTH blobs.
    "r3_assert_tail": [
        ("""        }
        k = k + 1;
    }""",
         """        }
        assert!(sp <= STACK_CAP);
        k = k + 1;
    }""", 1),
    ],
    # The same assertion at the loop HEAD: identical per-pop cost, but LLVM
    # then knows `sp == STACK_CAP` on the dropped-push edge and materialises
    # the constant (`cmp $0x40 ; jne ; mov $0x40,%r15d`), which costs 2 Ir on
    # every push the guard drops. Byte-identical to `m_clamp`.
    "r3_assert_head": [
        ("""        let op: u8 = w[4 + 5 * k];""",
         """        assert!(sp <= STACK_CAP);
        let op: u8 = w[4 + 5 * k];""", 1),
    ],
    # And the same assertion inside the POP arm, where it does not dominate
    # the back edge: the loop-carried range is never established, so the
    # assertion SURVIVES as a runtime test (`cmp $0x41,%r15 ; jae <panic>`,
    # read off the listing) and is paid on every POP operation, executed or
    # not -- while still deleting the pop's own bounds check.
    "r3_assert_pop": [
        ("""        } else {
""",
         """        } else {
            assert!(sp <= STACK_CAP);
""", 1),
    ],
    # The fourth placement: the index bound stated at the point of use, after
    # the decrement. Dearest of the four, and it lands on `m_mask`'s exact
    # numbers (3243 / 8803) from a different machine code -- which is why
    # ../NOTES.md 10a can say the mask exclusion protects nothing.
    "r3_assert_idx": [
        ("""                sp = sp - 1;
""",
         """                sp = sp - 1;
                assert!(sp < STACK_CAP);
""", 1),
    ],
}

# ---------------------------------------------------------------------------
# R4 side: unsafe candidates. NOT rungs until the twin verifies.
# ---------------------------------------------------------------------------
R4 = {
    "r4_forloop": [
        ("""    let mut k: usize = 0;
    while k < nops {""", """    for k in 0..nops {""", 1),
        ("""        }
        k = k + 1;
    }
    acc.wrapping_mul(31)""",
         """        }
    }
    acc.wrapping_mul(31)""", 1),
    ],
    # Raw pointers into the opcode stream and into the stack -- the spelling a C
    # programmer reaches for. Expected to be DISQUALIFIED at the pinned vstd.
    "r4_ptr": [
        ("""        let op: u8 = unsafe { *buf.get_unchecked(off + 4 + 5 * k) };""",
         """        let base = unsafe { buf.as_ptr().add(off + 4 + 5 * k) };
        let op: u8 = unsafe { *base };""", 1),
        ("""        let val: u64 = unsafe { *buf.get_unchecked(off + 5 + 5 * k) } as u64
            + 256 * (unsafe { *buf.get_unchecked(off + 6 + 5 * k) } as u64)
            + 65536 * (unsafe { *buf.get_unchecked(off + 7 + 5 * k) } as u64)
            + 16777216 * (unsafe { *buf.get_unchecked(off + 8 + 5 * k) } as u64);""",
         """        let val: u64 = unsafe { *base.add(1) } as u64
            + 256 * (unsafe { *base.add(2) } as u64)
            + 65536 * (unsafe { *base.add(3) } as u64)
            + 16777216 * (unsafe { *base.add(4) } as u64);""", 1),
    ],
    # The stack as a slice, with `get_unchecked` on the slice rather than on the
    # array -- the R4 mirror of r3_slicestack.
    "r4_slicestack": [
        ("""    let mut stack: [u64; STACK_CAP] = [0; STACK_CAP];""",
         """    let mut stack_arr: [u64; STACK_CAP] = [0; STACK_CAP];
    let stack: &mut [u64] = &mut stack_arr[..];""", 1),
    ],
    # `assert!` on the unsafe rung. In contract by the same ruler that admits
    # `r3_assert_*`, and the point of it is the TWIN: Verus answers
    # `panic is not supported`, so this spelling is available to the safe
    # class and not to the unsafe one (`../NOTES.md` 10b).
    "r4_assert": [
        ("""        let op: u8 = unsafe { *buf.get_unchecked(off + 4 + 5 * k) };""",
         """        assert!(sp <= STACK_CAP);
        let op: u8 = unsafe { *buf.get_unchecked(off + 4 + 5 * k) };""", 1),
    ],
}

# The Verus twin of each R4 candidate: the same exec edit applied to verus.rs.
# `.memory/01-ladder.md` / TASK_026 §0 item 3 -- run this BEFORE differencing any
# unsafe-side variant, and read the ERROR TEXT, not the exit code.
R4_TWIN = {
    "r4_forloop_twin": ("verus.rs", [
        ("""    let mut k: usize = 0;\n""", "", 1),
        ("""    while k < nops
        invariant
            k <= nops,
            sp <= STACK_CAP,""", """    for k in 0..nops
        invariant
            sp <= STACK_CAP,""", 1),
        ("""        decreases nops - k,
    {
        let op: u8 = buf_get_unchecked""",
         """    {
        let op: u8 = buf_get_unchecked""", 1),
        ("""        k = k + 1;
    }
    acc.wrapping_mul(31)""", """    }
    acc.wrapping_mul(31)""", 1),
    ]),
    "r4_ptr_twin": ("verus.rs", [
        ("""        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);""",
         """        let base = unsafe { buf.as_ptr().add(off + 4 + 5 * k) };
        let op: u8 = unsafe { *base };""", 1),
    ]),
    # NOTE the extra substitutions: the shipped accessors take `&[u64; 64]`, so
    # a slice-backed stack does not even TYPECHECK against them (measured:
    # `error[E0308]: mismatched types`, twice). Making this candidate a rung
    # therefore means respelling the TRUSTED BASE, not the rung -- so the twin
    # below changes the accessor signatures too, and ../NOTES.md 10b reports
    # that as a cost rather than hiding it.
    #
    # ⚠ TASK_036_REVIEW: the FIRST version of this twin failed with `E0502` x2
    # and `E0596`, and ../NOTES.md read those as a verdict about Rust. They were
    # defects in THIS FILE. The `E0502`s came from an extra ghost invariant
    # clause `stack_arr@.len() == STACK_CAP` and a ghost `assert` that both read
    # `stack_arr` while it is mutably borrowed -- clauses the control itself
    # added and the candidate does not need. The `E0596` came from
    # `let stack:` with no `mut`, which the verus.rs spelling needs because it
    # passes `&mut stack` rather than a reborrow. Both are repaired below and
    # the candidate then verifies `9 verified, 0 errors`:
    #
    #   * `&mut stack_arr` (the unsizing coercion vstd supports) instead of
    #     `&mut stack_arr[..]`, bound as `let mut stack`;
    #   * the ghost `assert` split -- on `stack_arr@` BEFORE the borrow and on
    #     `stack@` after it, so no ghost expression reads the borrowed array;
    #   * `&mut *stack` / `&*stack` reborrows at the two call sites.
    #
    # Same 1 + 3 TCB lines and the same `requires` as the shipped accessors --
    # only the parameter TYPES move.
    "r4_slicestack_twin": ("verus.rs", [
        ("""    let mut stack: [u64; STACK_CAP] = [0; STACK_CAP];
    // Ghost only: `[0; 64]`'s view IS the all-zeros sequence. vstd's
    // `axiom_spec_array_fill_for_copy_type` gives it pointwise; `=~=` lifts that
    // to sequence equality.
    assert(stack@ =~= zero_stack());""",
         """    let mut stack_arr: [u64; STACK_CAP] = [0; STACK_CAP];
    // Ghost only: `[0; 64]`'s view IS the all-zeros sequence. vstd's
    // `axiom_spec_array_fill_for_copy_type` gives it pointwise; `=~=` lifts that
    // to sequence equality. Stated BEFORE the borrow, and carried across it.
    assert(stack_arr@ =~= zero_stack());
    let mut stack: &mut [u64] = &mut stack_arr;
    assert(stack@ =~= zero_stack());""", 1),
        ("""fn stack_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)""",
         """fn stack_get_unchecked(v: &[u64], i: usize) -> (r: u64)""", 1),
        ("""fn slb_twin_stack_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)""",
         """fn slb_twin_stack_get_unchecked(v: &[u64], i: usize) -> (r: u64)""", 1),
        ("""fn stack_set_unchecked(v: &mut [u64; 64], i: usize, x: u64)""",
         """fn stack_set_unchecked(v: &mut [u64], i: usize, x: u64)""", 1),
        ("""fn slb_twin_stack_set_unchecked(v: &mut [u64; 64], i: usize, x: u64)""",
         """fn slb_twin_stack_set_unchecked(v: &mut [u64], i: usize, x: u64)""", 1),
        ("""                stack_set_unchecked(&mut stack, sp, val);""",
         """                stack_set_unchecked(&mut *stack, sp, val);""", 1),
        ("""stack_get_unchecked(&stack, sp)""",
         """stack_get_unchecked(&*stack, sp)""", 1),
    ]),
    # The twin of `m_clamp_unsafe` (exec side under MECH). It exists because
    # `.memory/01-ladder.md` and TASK_026 §0 item 3 say an R4 candidate is not
    # a rung until its R5 twin verifies, and this is the one that ANSWERS the
    # project's standing "nobody has built an admissible R4 that MOVES": it
    # verifies with ZERO new trusted items and measures -118 / +497 against
    # `R4ship`. Ghost-free edit -- the dead test needs no invariant clause,
    # because `sp <= STACK_CAP` is already one.
    "m_clamp_unsafe_twin": ("verus.rs", [
        ("""        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);""",
         """        if sp > STACK_CAP {
            return 0;
        }
        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);""", 1),
    ]),
    # ... and the twin of the back-edge placement, which is the one that
    # actually bounds the R4 endpoint: `9 verified, 0 errors`, -118 / -207.
    "m_clamp_unsafe_tail_twin": ("verus.rs", [
        ("""        }
        k = k + 1;""",
         """        }
        if sp > STACK_CAP {
            return 0;
        }
        k = k + 1;""", 1),
    ]),
    # The twin of `r4_assert`, and the measured asymmetry: this one does not
    # verify, and the error is `panic is not supported`, i.e. `is not
    # supported` -- disqualifying at the pinned vstd by
    # `.memory/01-ladder.md`'s own rule.
    "r4_assert_twin": ("verus.rs", [
        ("""        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);""",
         """        assert!(sp <= STACK_CAP);
        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);""", 1),
    ]),
}

# ---------------------------------------------------------------------------
# Mechanism controls. OUT of contract by construction; each prices one lever.
# ---------------------------------------------------------------------------
MECH = {
    # `idiom.forbidden`: masking the index. Prices how much of the surviving
    # check the mask actually removes -- the answer is not all of it.
    "m_mask": ("safe_tuned.rs", [
        ("""                acc = acc.wrapping_mul(31).wrapping_add(stack[sp]);""",
         """                acc = acc.wrapping_mul(31)
                    .wrapping_add(stack[sp & (STACK_CAP - 1)]);""", 1),
    ]),
    # THE LINEARISATION CONTROL, and p03's analogue of p05's `probe2.rs`: a
    # provably-dead test at the top of the loop that hands LLVM the invariant
    # `sp <= STACK_CAP` it will not derive. If this deletes the surviving check,
    # the mechanism is "the optimiser failed the lemma the proof proves" and not
    # something else.
    "m_clamp": ("safe_tuned.rs", [
        ("""        let op: u8 = w[4 + 5 * k];""",
         """        if sp > STACK_CAP {
            return 0;
        }
        let op: u8 = w[4 + 5 * k];""", 1),
    ]),
    # The same dead test on the UNSAFE rung, so the lever can be read on both
    # sides rather than only on the one it flatters.
    "m_clamp_unsafe": ("unsafe.rs", [
        ("""        let op: u8 = unsafe { *buf.get_unchecked(off + 4 + 5 * k) };""",
         """        if sp > STACK_CAP {
            return 0;
        }
        let op: u8 = unsafe { *buf.get_unchecked(off + 4 + 5 * k) };""", 1),
    ]),
    # The same dead test on the unsafe rung's BACK EDGE rather than its head.
    # TASK_037: the placement is worth 2 Ir per dropped push on both sides --
    # at the head LLVM learns `sp == STACK_CAP` on the dropped-push edge and
    # materialises the constant; on the back edge it learns only the range.
    # This is the cheapest admissible R4 found (twin: `9 verified, 0 errors`).
    "m_clamp_unsafe_tail": ("unsafe.rs", [
        ("""        }
        k = k + 1;""",
         """        }
        if sp > STACK_CAP {
            return 0;
        }
        k = k + 1;""", 1),
    ]),
    # `idiom.required[4]`: the dispatch is a real branch. This is the branchless
    # spelling, built to be measured and reported, not to be a rung.
    "m_branchless": ("safe_tuned.rs", [
        ("""        if op == 0 {
            if sp < STACK_CAP {
                stack[sp] = val;
                sp = sp + 1;
            }
        } else {
            if sp > 0 {
                sp = sp - 1;
                acc = acc.wrapping_mul(31).wrapping_add(stack[sp]);
            }
        }""",
         """        let is_push: bool = op == 0;
        let can_push: bool = is_push & (sp < STACK_CAP);
        let can_pop: bool = (!is_push) & (sp > 0);
        let widx: usize = if can_push { sp } else { STACK_CAP - 1 };
        let ridx: usize = if can_pop { sp - 1 } else { 0 };
        let keep: u64 = if can_push { val } else { stack[widx] };
        stack[widx] = keep;
        let popped: u64 = stack[ridx];
        acc = if can_pop {
            acc.wrapping_mul(31).wrapping_add(popped)
        } else {
            acc
        };
        sp = if can_push { sp + 1 } else if can_pop { sp - 1 } else { sp };""", 1),
    ]),
    # C's uninitialised array, priced on the Rust side: the `[0u64; CAP]` fill
    # replaced by a MaybeUninit array. `idiom.forbidden`, and it exists only so
    # the C-vs-Rust initialisation term is a measurement.
    "m_uninit": ("unsafe.rs", [
        ("""    let mut stack: [u64; STACK_CAP] = [0; STACK_CAP];""",
         """    let mut stack: [u64; STACK_CAP] = unsafe {
        core::mem::MaybeUninit::uninit().assume_init()
    };""", 1),
    ]),
}

# ---------------------------------------------------------------------------
# Proof mutants. Each must FAIL, and for a different reason.
# ---------------------------------------------------------------------------
PROOF = {
    # One character, in the trusted item AND its twin so the signatures still
    # match. The shipped config still verifies; only 5c-twin sees it.
    "p1_weak_requires": [
        ("""fn stack_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i < v@.len(),""",
         """fn stack_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i <= v@.len(),""", 1),
        ("""fn slb_twin_stack_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i < v@.len(),""",
         """fn slb_twin_stack_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i <= v@.len(),""", 1),
    ],
    # R1's bug written into R5: delete the pop guard from the EXEC code.
    "p2_nopopguard": [
        ("""            if sp > 0 {
                sp = sp - 1;
                acc = acc.wrapping_mul(31).wrapping_add(stack_get_unchecked(&stack, sp));
            }""",
         """            sp = sp - 1;
            acc = acc.wrapping_mul(31).wrapping_add(stack_get_unchecked(&stack, sp));""", 1),
    ],
    # The invariant weakened by one, which is what LLVM would need to be handed
    # and is one past what is true.
    "p3_weak_invariant": [
        ("""            sp <= STACK_CAP,""", """            sp <= STACK_CAP + 1,""", 1),
    ],
    # The push guard widened by one: the array overflow this pattern does NOT
    # model, so that it is on record that the OTHER guard is load-bearing too.
    "p4_push_offbyone": [
        ("""            if sp < STACK_CAP {
                stack_set_unchecked(&mut stack, sp, val);""",
         """            if sp < STACK_CAP + 1 {
                stack_set_unchecked(&mut stack, sp, val);""", 1),
    ],
}


def emit(name, base, pairs):
    text = sub(src(base), pairs, name)
    if PATH_SHIPPED in text:
        text = text.replace(PATH_SHIPPED, PATH_FIX)
    dst = os.path.join(OUT, name + ".rs")
    open(dst, "w").write(text)
    return dst


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    plan = ([(n, "safe_tuned.rs", p) for n, p in R3.items()]
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
