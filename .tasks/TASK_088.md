# TASK_088 — land `p19`'s corrections, then the gate work that has been queuing

**Role: research engineer.** Two halves, and **do them in this order** — the p19
corrections are cheap and bounded; the gate work stales every record and must go
last so its sweep covers p19's corrected files too.

Read `.tasks/PROTOCOL.md`, then this file, then
`.tasks/TASK_087_REVIEW_REPORT.md` (**the four majors and four minors are the
first half of your work**), then `RECAP.md` "Owed" **0** (the second half).

Scratch in `.temp/t88/` — free, I checked.

---

## PART A — `p19`'s corrections (do this first)

All four majors are **prose**, none inside `contract_sha256`. **Do not move
`contract_sha256`.** The review names the cost of each site; **re-derive it, do
not trust it.**

### A1 — strike the uniqueness claim (major 1)

`NOTES.md:42-43`, `spec.md:212`, `README.md:35` say the two `forbidden` entries
are *"the only entries in this tree that forbid a spelling for being SAFE"*.
**False.** **p36 `forbidden[2] `op & 7`` / `[3] `op % 8`` / `[5]` / `[6]`** and
**p03 `forbidden[1] `& (STACK_CAP - 1)``** do the same thing, each with the
reason in its own `idiom.why` — and **p36 is the pattern p19 names as its nearest
sibling.**

⚠ **Keep the practice, strike only the uniqueness.** Forbidding the safe spelling
is **not** Rust-in-C-syntax in reverse: the alternative is a benchmark whose bug
is unreachable or absent, and p03 and p36 already established the precedent.
**Say that p19 is the third instance and cite both.**

### A2 — the two published laws (major 2)

`NOTES.md` §11 and `inputs/gen.py:45` publish `R2 − R4 = 6.25·m − 8` and
`R3 − R4 = 1.00·m − 2`. **The intercepts are wrong at every residue class and
there is an unmodelled `m mod 4` term.** Re-fitted from the **committed** band,
exact, zero scatter within each class:

```
R2 - R4 = 6.25m - 6      (m≡0 mod 4)   R3 - R4 = 1.00m + 4   (m≡0 mod 4)
        = 6.25m - 12.25  (m≡1)                 = 1.00m + 3   (m≡1,2,3)
        = 6.25m - 14.5   (m≡2)
        = 6.25m - 16.75  (m≡3)
```

⚠⚠ **And the published laws disagree with p19's OWN gate-measured cells** —
1594 vs 1592, 260 vs 254, 25594 vs 25592, 4100 vs 4094 — **while `NOTES.md` §4
prints the measured numbers two sections above the law that contradicts them.**

✅ **The headline survives**: OLS over 19 lengths gives `6.250530·m` and
`1.000035·m`, and **every m ≡ 0 (mod 4) is exact**. **Keep the slopes; strike or
re-state the intercepts, and state the residue structure with its mechanism** —
R4 unrolls 4× and its scalar epilogue body is 11 instr/byte against 8.75, worth
**2.25 per epilogue byte**.

⚠ **Re-fit from the committed blobs yourself** rather than copying the review's
numbers. The band exists precisely so the law is re-derivable from a hashed
generator, and **nobody has done it from the committed inputs** — the shipped law
came from a 5-length probe.

**Cost:** `inputs/gen.py` is in the **measurement** record's `source_sha256`, but
a **docstring-only** edit classifies **GEN-ONLY**, not a re-measure. **Verify
that with `measure.py --check-stale` before and after; if it reads STALE rather
than GEN-ONLY, STOP and report** — do not re-measure to make it green.

### A3 — the CVE citations (major 3)

✅ **`CVE-2026-23407` is REAL, correctly quoted, and its description matches
p19's bug exactly** (*"reads `k = DEFAULT_TABLE[j]` and uses `k` as an array
index without validation"*). **Keep it and lean on it harder.**

⚠⚠ **`CVE-2026-23269` is REAL but MISQUOTED AND MISATTRIBUTED.** Its actual
title is *"apparmor: validate DFA start states are in bounds in unpack_pdb"*;
p19 quotes a **paraphrase in quotation marks** and says *"That is
CVE-2026-23269's shape"* — **it is not.** That bug is an untrusted **start
state**; p19's kernel starts at `st = 0` and models no start state at all. **The
shape is 23407's.**

Sites: `c/kernel.c:7`, `c/kernel.h:52`, `README.md:18`, `NOTES.md:67`,
`spec.md:65`.

⚠⚠ **`c/kernel.c` and `c/kernel.h` are in the MEASUREMENT record's
`source_sha256`, so a comment-only edit there reads STALE, not GEN-ONLY.**
**Decide and report which you did:** either (i) re-measure **p19 only** and say
what it cost, or (ii) fix the four non-measurement sites and leave a one-line
pointer in the two C files' comments that does not itself name a CVE. ⚠ **State
the reasoning; do not leave a wrong CVE attribution standing in a shipped file
just because it is hashed.**

### A4 — the minors

1. `NOTES.md` §4 and §8d cite *"`.memory/01-ladder.md` finding 7"* / *"finding
   5"* for what is **RECAP finding 7**. ⚠ **This is the live numbering collision
   RECAP documents as having *"already sent agents to the wrong finding"*.**
   **Cite the pattern by name, never the number.** `patterns/p38-alias-pun/NOTES.md:328`
   has the same mis-citation — **fix p19's; report p38's, do not fix it.**
2. `safe_tuned.rs:19` says *"all **nine** inputs"*; the gate checks **eight**.
3. `NOTES.md` §4 says *"Miri: 7 of 7"*; the record has **eight**.

### A5 — re-gate

`harness/check.py p19` green, and `measure.py --check-stale`. ⚠ **Expect
`0 STALE` unless A3 route (i) was taken; if so, say so explicitly.**

---

## PART B — the gate work (do this second; it stales every record)

**`RECAP.md` "Owed" 0.** `TASK_084` closed B1/B2/B3 and the published column;
`TASK_084_REVIEW` then found the walk feeds **one of three detectors**.

### B5 — the `#[path]` walk's other two detectors (TASK_084_REVIEW major 1)

`_axiom_items` was widened to `_path_includes`. **`_trusted_items` was not** —
*the function immediately above it, same shape, same purpose* — nor the TCB
inventory `tcb = [i for i in item_list if i.external]` in `check_verus_contract`,
nor the `assume(`/`admit(` keyword shout. So an `external_body` with a **false
`ensures`** in a `#[path]`-included module ships **fully green with no gate
output at all**: `grep -c <name> gate.log` → **0**, the gate prints *"3 TCB
items"*, `synthesis.md` **byte-identical**.

✅ **Clean negative that bounds it:** `unsafe` in an included module **is**
caught, so **the vector is false claims about SAFE operations** — exactly the
threat `_check_axiom_decls`' own docstring names.

**Widen all three the same way `_axiom_items` was.**

### B6 — the minors from `TASK_084_REVIEW`

- **minor 1** — a shared axiom in `common/driver.rs` lands in **all 22**
  records' `path_included` entries, so the published total reads **22** for
  **one** axiom. **Dedupe on `(key, name, line)` for `path_included` rows.**
- **minor 4** — a `pub(crate) trait` under an external-trait attribute
  under-counts to one `ExW::?` (`trait_spans`' item-position guard stops at
  `)`). ⚠ **Remember `impl_spans`' LIMIT 2 guard is the live trap here** —
  `trait_spans` already had to allow `]`.
- **minor 5** — a `#[path]` include resolving *inside* `pdir` that is also a
  pinned obligation source gets **two keys** and is **counted twice**.

### B7 — the manager's own citation habit, in a shipped hashed document

`patterns/p01-array-sum/spec.md` cites `check.py:67-72` and `check.py:2943`,
against `.memory/02-bench-rules.md`'s **"name the FUNCTION and give NO LINE
NUMBER AT ALL"**. They landed in the same commit that grew `check.py` by **+127
lines**. **Replace with function names.** It is prose above the fence, so it
costs a **gate re-run, not a contract move** — ⚠ **verify that yourself with the
two-line check in `.memory/05-layout.md` rather than trusting this sentence.**

### B8 — sweep and re-publish

Full 22 + p19 = **23-pattern** sweep, then `synthesis/licence.py --emit
synthesis/licence.json` **BEFORE** `synthesis/synthesize.py` — that order is
mandatory or 23 `LICENCE STALE` verdicts publish. ⚠ **Budget ~45 min for the
sweep.**

⚠⚠ **AND THE ACCEPTANCE TEST MUST BE ONE COMMAND FROM SOURCE TO PUBLISHED
NUMBER.** `TASK_084`'s limb 3 was a good test that still missed, because it was
**verified in two halves and the join was never run**: one script proved
*source → gate log*, another proved *hand-edited JSON → `synthesis.md`*. The
review then reproduced the failure on **three** routes. **Plant a real
`external_body` with a false `ensures` in a `#[path]`-included module, run the
real gate, and diff the regenerated `synthesis.md`.** ⚠ **A byte-identical
`synthesis.md` under a planted false `ensures` is the failure this limb exists to
catch.**

---

## Constraints

- `.temp/t88/` only. **No `/tmp`.** Keep the generator, delete the artefact.
- **Notes in `.temp/t88/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Report durable facts; the manager lands them.
- ⚠ **Do not touch `harness/build.py` or `harness/asm.py`** — measurement-hashed;
  an edit costs a full 43-minute re-measure of 17 records.
- Do not edit `pilot/`. Do not bump the Verus/vstd pin.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- ⚠ **Cite `check.py` by FUNCTION NAME, never `check.py:NNNN`** — B7 exists
  because the manager did not.

---

⚠ **PROTOCOL rule 2's running count is 249.** **Every agent that has contradicted
the manager with a measurement has been right — 249 times, and the last four were
this pattern's own review, one of them against a claim the manager had
committed.** The calls I am least sure of here: **(a) that A3's two C-file sites
really do read STALE rather than GEN-ONLY** — the review says so from the
provenance rules and nobody has run it; and **(b) that B5's three widenings are
inert on the current tree** — they should be, because nothing in `common/` is an
`external_body`, **but if any of them turns a pattern red, STOP and report rather
than editing 23 `spec.md` files.** Carry **249** forward incremented by what you
find.
