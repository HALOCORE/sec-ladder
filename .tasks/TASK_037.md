# TASK_037 — land p03's two blockers, and stop calling a two-compiler result a Rust result

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_036_REVIEW_REPORT.md`
in full** — it is your whole task — then `.memory/01-ladder.md`'s **finding 10
(p03)** and the paragraph where *"nobody has, on any pattern"* was retired. **Both
are already written by the manager and are the wording to follow rather than
re-invent.**

**Your causal claim survived**, confirmed by three negative controls you had not
built. What follows is the prose around it, plus one control-generator repair.

## The manager's ruling, which you need before item 1

**`assert!(sp <= STACK_CAP)` IS an admissible R3 spelling.** The gate's own
matcher takes it (0 forbidden hits, 0 required misses); `.memory/01-ladder.md`'s
R3 definition names *"hoisted length assertions"* as a technique; and it is a
**runtime check, not dead code**, so the argument that keeps `m_clamp` a control
does not reach it. Excluding it *after* seeing it is cheaper would be exactly the
retroactive move this project has a rule against.

## The two blockers

1. **p03's in-contract R3 span is wrong at the bottom.** `NOTES.md:915` ("cheapest
   found, both blobs"), `:927` (the span), `:942` ("the cheapest spelling is the
   same on both blobs") and `README.md`'s matching sentence. Corrected: the span is
   **−113 … +5110** on `small` and **+212 … +17237** on `large`; `x_assert` wins
   `small` and `x_assert_pop` wins `large`, so **the cheapest spelling differs
   between the two blobs**. And say it plainly: **the published `3.00000` Ir per
   executed pop is the SHIPPED SPELLING's rate, not the class's** — the class
   reaches `1.00000` and `−1.00000`. The fixed-R4 bound survives as an upper
   bound; what it bounds is now **negative** on `small`.
   Ship `x_assert` and `x_assert_pop` in `controls/gen_controls.py` so the span is
   re-derivable from the tree.

2. **§10b is wrong twice.**
   - **Withdraw "the unsafe class is bounded by Rust's borrow checker"**
     (`NOTES.md:996-1003`). The `E0502`s came from ghost clauses
     `controls/gen_controls.py:186-203` itself adds and the `E0596` from a missing
     `mut` — **two generation defects reported as language verdicts.** Fix the
     generator, and ship the third spelling that verifies `9/0`.
   - **p03 has the project's FIRST admissible R4 that moves.** `m_clamp_unsafe`:
     twin `9 verified, 0 errors`, zero new trusted items, identity pin
     byte-for-byte, **−118 / +497**. So `:985` ("the pair interval is DEGENERATE")
     and `:1010` ("the first pattern where searching it turned up nothing") are
     refuted, and p03 has a **non-degenerate pair interval** — the first here.
     Pair it with the measured asymmetry: `assert!` on the unsafe side is
     `error: panic is not supported`, so **the safe class reaches a spelling the
     unsafe class cannot.**

## The two majors

3. **Stop calling it a Rust result.** `NOTES.md:353-356` is true of p03 but reads
   as a fact about safe Rust. Measured: clang keeps a *manual C* bounds check at
   **4.00000 Ir per executed pop exactly**, gcc keeps it too, and **both delete
   100% of it given the identical clamp** — the clamped-with-check binary
   byte-identical to the clamped-without-check one, in both compilers. **Two
   independent middle-ends fail the same lemma the same way, and gcc shares none
   with rustc.** Write it as *"any compiler asked to prove this"*.
   Add the second qualification too: **LLVM does eventually derive the fact** —
   in `m_clamp`'s output the clamp is *gone* and the `sp > 64` path is treated as
   unreachable — so this is analysis **seeding / phase ordering**, not an
   inability to prove the lemma, and that is a *different* failure from p05's.

4. **The "same basic block" mechanism is refuted** (`NOTES.md:297`,
   `README.md:79`). Hoisting the push guard into the loop head is **byte-identical
   to shipped R3**. The real discriminator: **the push guard supplies the UPPER
   bound the access needs, locally; the pop guard supplies only the LOWER bound,
   and the upper must come from the loop-carried invariant.** Two in-contract
   controls confirm it. Also note that `x_popidx` (`if sp > 0 && sp - 1 <
   STACK_CAP`) lands on `m_mask`'s exact numbers **in contract**, which undercuts
   §10a's "forbidding `m_mask` raises the figure, against interest" — restate or
   drop that argument.

## The minors

5. **`NOTES.md:1198`** says §5b tallies **8** TCB lines; §5b's table and the gate
   both say **10**.
6. **`NOTES.md:231-232`** claims the `memset` cost "is part of the C-vs-Rust rows
   in §3". §3 is kernel-exclusive and therefore **excludes** the 43–50 Ir only the
   Rust rungs pay (`c-clang` −12.29% kernel-exclusive vs −13.47% whole-program).
7. **§4 labels a row `unsafe/verus`** but the sweep never measured R5
   (`.temp/p03/kir-band-*.json` has no `verus` row). Defensible at O3 — say what
   was run.
8. **The `ns` direction on `small` is resolved, not unresolved.** Seven
   independent correct-protocol readings across two sessions at **−10.6 … −11.0%**
   against a 3.4–6.5% identical-copy floor. Your hedge was too weak; **the
   magnitude** (7–15% across layout modes) is what stays a range.
9. **Add the design caveat to §4**: the pooled fit is rank 5/5 but **every pair of
   bands is rank-deficient**, and `epop > 0` on only 12 of 89 blobs, `dpush > 0`
   on 9 of 89 — thin support carried by the zero residual rather than by the
   design. That is worth saying beside a law with `maxres 0.000000`.

## Done when

Items 1–9 land; `check.py p03` green; `md5_fn` unchanged; the table regenerated
with `harness/report.py`; `harness/measure.py --check-stale` clean. Only p03's
gate needs re-running unless you touch something shared — you should not.

## Constraints

No root; no `/tmp` (scratch `.temp/p37/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. **Prose and `patterns/p03-bounded-stack/controls/*.py`
only — nothing in `harness/`, no rung source, no cell relinked.** Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill, **and no monitor wait-loops with self-matching `pgrep`
patterns**. **Measurements in the FOREGROUND, interleaved by cell.** Delete your
binaries and blobs when the gate is green.

The reviewer's scratch is `.temp/r36/` with all 22 controls and the fit scripts —
**reuse rather than rebuild**. Notes to `.temp/p37/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Forty-seven
agents have contradicted the manager and all forty-seven were right — you were one
of them twice on p03 alone. What I am least sure of is **item 1's completeness**:
the reviewer explicitly did not search for an in-contract R3 cheaper than
`x_assert`, and noted that six published minima have been refuted six times on
this project. **If you find one, the span moves again and I would rather that
happen now than in the next review.** Spend a little effort looking before you
write the number down.
