# TASK_012 — ship p17's real artefact: the slice-relative guard

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_011_REVIEW_REPORT.md`
in full** — this task exists because of it, its BLOCKER 1b is constructive and
the reviewer already built and measured the thing you are shipping. Then
`.memory/01-ladder.md` **finding 5** (already corrected by the manager; do not
re-apply those edits), and `patterns/p17-http-range/NOTES.md`.

The reviewer's rigs are in `.temp/review011/`. **Reuse them.**

## What happened, in one paragraph

p17 shipped claiming a program that is *provably memory-safe and still leaks*.
The review found the shipped demonstration does not leak: the excess bytes R1
reads on `adversarial-leak` are indices `{0..7}`, which is `nsuf` plus the three
suffix `u16`s — **the attacker's own request table**. So p17 as shipped shows
*memory-safe and functionally wrong*, which is real but weaker. The review then
showed the claimed artefact **does exist, one token away**: the guard
`start >= -(body_start as i64)` is strictly *stronger* than a bounds check,
because the driver hands the kernel the **whole blob** and a bounds check only
requires the *slice*-relative index to be ≥ 0. Use

```
start >= -((off + body_start) as i64)
```

and the mutant verifies identically (`9 verified, 1 errors`, functional only;
`10 verified, 0 errors` with the functional spec stripped) **and** reads a
neighbouring window: the reviewer's two-window probe showed the output tracking
the victim window's secret — `14940305438379539953` vs `10930790086150322769` —
with no panic and no `unsafe`.

Your job is to turn that probe into a shipped, reproducible artefact.

## Deliverables

1. **`patterns/p17-http-range/verus_leak.rs`** — R5 with the sign guard replaced
   by the slice-relative one, everything else identical. Not a rung, not in the
   measured matrix; a control, the way `safe_naive_verus.rs` is for p01.
   Build it via whatever `build.py` path already serves non-rung controls; if
   there is none that fits, **report that rather than adding a build axis**.
2. **`inputs/gen.py` gains `adversarial-crosswin`** — **at least two windows**,
   with a distinguishable secret in window 0 and a suffix in a later window whose
   `start` reaches back into it. Note the tension with p16's one-window rule: `k`
   is pseudo-random, so you cannot control which window is hit on a given call.
   **Resolve it by making the demonstration differential, not positional** — the
   claim is *"change the victim's bytes, the output changes, nothing panics"*, and
   that holds however `k` lands. Generate two variants differing only in window
   0's secret and diff the outputs. Say in `spec.md` why this input is exempt
   from the one-window rule.
3. **The three-way table in `NOTES.md`**, replacing the current headline:

   | guard | Verus | memory safety | reads a neighbour? |
   |---|---|---|---|
   | none (`verus_nocheck`) | both obligations fail | no | — |
   | `start >= -(body_start)` (shipped) | 9/1, functional only | yes | **no** — attacker's own header |
   | `start >= -((off + body_start))` | 9/1, functional only | yes | **yes** |
   | shipped R5 (sign guard) | 10/0 | yes | no, and correct |

   Fill in the real numbers; that table is the finding. **Row 2 vs row 3 is the
   entire point** — same verification result, opposite security outcome, one
   token apart.
4. **Verify no obligation is hiding.** `.memory/04-verus.md` item 2b: run
   `--multiple-errors 20` and separately strip the functional spec and confirm
   `N verified, 0 errors`. Keep a positive control (a mutant that *does* break
   memory safety) so the probe is shown to be able to see a second error.
5. **`check.py p17` still green on a complete run** after your changes, and the
   contract pins updated if the new input moves any of them. A new input changes
   `requires`/`ensures` coverage counts; re-derive, do not hand-edit.

## Corrections to land in the pattern while you are there

All from the review; the manager has already landed the `.memory/` side.

- **`NOTES.md`'s headline must be restated.** It currently claims disclosure. Its
  own §541/§771 already say the true thing ("serves the attacker *its own*
  metadata") — the headline contradicted the body.
- **`NOTES.md` §598-605's Miri caveat is false.** R4 reads index 0 and
  `n_blob-1` on all four non-degenerate inputs; p17's Miri coverage is *better*
  than p16's, not thinner. Delete the caveat and say what was measured.
- **§3b's `9.9991 / 5.7491` are driver-contaminated** by the final `println!`'s
  digit count. The zero-residue lag-4 pair gives **exactly 10.0000 / 5.7500**.
  Re-quote, and note that p16's constants therefore reproduce *exactly*.
- **The frequency caveat is an underclaim.** `scaling_cur_freq` is unreliable on
  this box (`.memory/00-environment.md`) — it read 800 MHz while the core ran
  3.80–3.89 GHz. p17 may quote **3.02–3.05 cycles/byte**.

## Scope — read this before you start

This is a **small, bounded** task: one control file, one input, one table, four
corrections. It is not a licence to rework p17.

- Do **not** change any measured rung's source. The perf numbers must not move.
- Do **not** touch `harness/` or `common/`.
- If shipping the control needs a build change, **stop and report it** — an
  unbuilt control described accurately in `NOTES.md` with the reviewer's
  reproduction command is an acceptable outcome and better than a new build axis.

## Done when

1. `verus_leak.rs` exists, verifies with the stated counts, and the two-window
   differential demonstration is reproduced **by you** with pasted output.
2. `adversarial-crosswin` is generated by `gen.py` and documented in `spec.md`,
   including why it is exempt from the one-window rule.
3. The three-way table is in `NOTES.md` with real numbers, and the headline is
   restated to match it.
4. The four corrections above are applied.
5. `check.py p17` green on a complete run; paste the verdict line.
6. Your report says explicitly whether the "reads a neighbour" result reproduced
   **for you**, independently of the reviewer's numbers. If it does not, that is
   the finding and the claim comes out of `.memory/01-ladder.md` entirely — say
   so plainly and do not rescue it.

## Constraints

No root; no `/tmp` (scratch `.temp/p17b/`, reuse `.temp/review011/`); **no
`git add`/`git commit`**; do not edit `pilot/` or `.memory/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`.

Notes to `.temp/p17b/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Ten agents have
contradicted the manager's written instructions and all ten were right; the last
two corrected headline claims the manager had written from a report without
re-measuring. This task is the second such correction in a row, so treat its
premises with the same suspicion.
