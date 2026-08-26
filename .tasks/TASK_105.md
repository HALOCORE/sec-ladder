# TASK_105 — review `p23`, and §A may be a BLOCKER

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then `.tasks/TASK_101_REPORT.md` **in
full**, then `patterns/p23-partition/` (`spec.md`, `NOTES.md`, all five rungs,
`model.py`, `controls/`), then `.memory/06-catalogue.md`'s **`p23` and `p24`
rows** — ⚠ **read `p24`'s before you start §A; it is the whole reason §A exists.**

Scratch in **`.temp/r105/`**.

---

## §A — ⚠⚠ IS `p23`'s SHIPPED POSTCONDITION VACUOUS? THIS IS A POSSIBLE BLOCKER.

`TASK_101` reports that the multiset postcondition is **separable**: the
partition verifies **`6 verified, 0 errors` WITH** the multiset clauses and
**`6/0` with every multiset clause DELETED**. On that basis **`p23` ships without
it** and does not claim it.

⚠⚠ **BUT `p24`'s ROW RECORDS EXACTLY THIS SHAPE AS AN ANTI-VACUITY FAILURE, AND
IT WAS CAUGHT BY A CONTROL THAT DID FIRE:**

> *"The 8th is the vacuity control and it PASSES: with the multiset clause
> deleted, a body that **ZEROES THE ARRAY** still satisfies `is_heap`** — the
> multiset clause carries the anti-vacuity weight."*

**So the question this review must answer first, with runs:**

> ⚠⚠ **Does `p23`'s shipped `ensures` — WITHOUT the multiset — admit a
> degenerate body?** Write the degenerate bodies and put them through Verus.
> **The obvious ones: zero the array; write the pivot everywhere; return
> immediately without moving anything; swap nothing and report `i = 0`.**

- **If any degenerate body verifies against the shipped postcondition, that is a
  BLOCKER** — the pattern's R5 certifies nothing, and `p24`'s row says this is a
  live failure mode in precisely this shape.
- **If none does, say WHY the separability is safe here and not on `p24`** — what
  carries the anti-vacuity weight in `p23` if not the multiset? ⚠ **A plausible
  answer is the two-sided partition predicate (`∀k<i: v[k] ≤ pivot` and
  `∀k≥j: v[k] ≥ pivot`) plus the returned index, which a zeroing body might
  satisfy — CHECK IT RATHER THAN ASSUMING IT.**
- ⚠ **`p23` ships with ZERO `proof fn`s and verified `16/0` FIRST ATTEMPT.** That
  is either an elegant spec or an easy one. **Mutation-test it: the standard here
  is `p24`'s 8 mutants with 7 failing, and `p29`'s 3-of-4.** **Report the ratio.**

## §B — the headline: "the safety tax is a function of SHAPE, not SIZE"

`R3 − R4` runs **`227.00 → 706.37 Ir`/call, a factor of 3.11**, with `m`, record
count and copied bytes **all fixed** and only the **pivot's rank** varying.

1. ⚠ **Verify the "all fixed" claim by reading the inputs, not the prose.** If
   anything else co-varies with pivot rank — number of swaps, branch
   mispredictions, loop trip counts — **then rank is a proxy and the headline
   should name the real variable.** ⚠⚠ **The number of SWAPS is the obvious
   confound and it is not named in the report.** A partition's swap count *is* a
   function of the pivot's rank. **Settle whether the tax tracks rank or tracks
   swaps** — they are different findings and only one is about safety.
2. **The mechanism is `k_up == k_r3c` and `k_dn == k_r4b`, exactly, at three
   ranks** — LLVM eliding the upward cursor's check and not the downward one.
   ⚠ **Three ranks is three points. Does it hold across the band?** And ⚠ **is
   the asymmetry really monotone-induction-variable vs unsigned-subtraction, or
   is it just that one loop was written with a different guard?** **Try to make
   the downward check elide** — if a legal respelling elides it, the tax is a
   spelling cost and the headline changes.
3. ⚠⚠ **BOTH SIDES SEARCHED? The report does not give lever counts, and this trap
   has caught FIVE patterns** (p10, p27, p38, p22 at 510×, p36 in mirror image).
   **Count the in-contract R3 and R4 spellings and say whether they are
   comparably searched.** **A difference is only as honest as its weaker-searched
   endpoint.**

## §C — the numbers that look fragile

- ⚠⚠ **`m == 1` gives "eight C cells, eight distinct wrong checksums, no crash —
  AND THEY MOVE UNDER A COMMENT-ONLY EDIT."** **A pinned expectation that moves
  under a comment-only edit is not reproducible.** **What exactly is pinned for
  that input, and does the gate depend on a value that is layout-dependent?**
  ⚠ **If `spec.md` pins one of those checksums, this is a defect.**
- **`R1 − R1h` is NEGATIVE on gcc** (`−39.10`/`−60.34`) with the hardened kernel
  **smaller** (157 vs 160 insns), and clang **flips sign between inputs**.
  ⚠ **A hardened build that is cheaper AND smaller than the unhardened one is
  surprising enough to deserve a mechanism, not just a measurement. Get one.**
- **Disclosed and not done, so confirm each is really out rather than wrong:**
  no `-C debug-assertions=on` column (⚠ **and what holds on 3 of 3 patterns is
  that at `-O3` with debug-assertions ON, R4 becomes DEARER than R3 — so its
  absence may hide a sign flip**); bands N and X shipped **unfitted**; and the
  band-K fit has **±30 residuals** and is explicitly **not to be quoted as a
  law** — ⚠ **check that nothing in `NOTES.md` or `spec.md` quotes it as one.**
- **`contract_sha256` moved once pre-measurement** (`22240ee4…` → `8251a676…`),
  five edits disclosed. ⚠ **Verify no pin CHANGED MEANING** — that is
  `PROTOCOL` rule 6's whole point, and `p46` showed rule 6 protects against a
  declaration edited *after* measuring and **not** against one measurement has
  since falsified.

## §D — clean negatives are wanted

The engineer **self-caught a false claim before measurement** (`i < m` vs `j > 0`
is *equivalent*, not "safe and wrong" — 800 000 randomised records, 0
differences) and corrected it in three places. ⚠ **Check the correction actually
landed in all three, and that no derived sentence still assumes the false
version.**

---

## Constraints

- **`.temp/r105/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `pilot/`, `harness/`, `synthesis/`,
  `results/` or any `patterns/*/` file.** You are a reviewer: **do not fix
  anything.** If you must plant to test something, snapshot **by bytes** and
  restore in a `finally:`, and say so.
- ⚠ **`harness/check.py` rewrites `results/gate/` in place.** If you run it,
  `git checkout -- results/gate/` afterwards and **say that you did**.
  **Do not run `harness/measure.py` or `harness/build.py`.**
- ⚠ **`env -u LD_PRELOAD` for hand-run sanitizers; `grep` logs, never `head`.**
- ⚠ **Every probe needs an arm that must fire.** The consolidated list of **seven**
  controls in this project that could not have failed is at the end of
  `.memory/03-measurement.md`. **Do not become the eighth.** The two newest
  lessons: *compute from the bytes, not from the prose describing them*, and
  *a control must reproduce the COMMAND, not the idea of the command*.
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_105_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 343** (332 + 11 from `TASK_101`). The
calls I am least sure of:

1. ⚠⚠ **That §A is a real risk rather than a manager panic.** I am reasoning by
   analogy from `p24`'s row, and **analogy is exactly how I have been wrong
   twice this week** — once asserting a control could not fire when it did, once
   striking a true `.memory/` sentence. **If `p23`'s postcondition is
   non-vacuous, say so plainly and briefly and spend your time on §B.**
2. **That the shape-not-size headline survives the swap-count confound.** I think
   swaps are the more likely regressor and rank is a proxy. ⚠ **If the tax really
   does track rank with swaps held constant, that is a stronger result than the
   report claims and it should be said louder.**
3. **That `p23` was worth building at all.** It is the tree's **15th**
   `index >= len`, and it shipped on the *new-mechanism* bar rather than on its
   bug class. ⚠ **If, having read it, you think the mechanism is not actually
   new, that is a finding about the BAR (RECAP finding 37) and not just about
   this row** — and the bar is one task old, so now is when it is cheapest to
   correct.

Carry **343** forward, incremented by what you find.
