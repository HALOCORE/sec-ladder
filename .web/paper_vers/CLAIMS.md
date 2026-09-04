# `paper_vers/CLAIMS.md` — what every version may and may not say

**This file is committed on purpose.** The verification behind it lived in
`.temp/`, which is gitignored and gets cleared; the *conclusions* have to outlive
it, because every one of them is a claim some draft of this paper actually made
and had to withdraw.

It spans all versions. `ver_A`, `ver_B` and `ver_C` are different framings of one
corpus, and a claim that is false is false in all three.

**Authority order for anything not here:** `../../.memory/` 00–06 (supersedes any
task report it contradicts) → `../../RECAP.md` → `../../results/SYNTHESIS.md` →
`../../results/gate/*.json` → the pattern's own `NOTES.md`/`spec.md`.

⚠ **Re-run `python3 build_data.py` before believing any count.** Upstream moves
during a session: during ver_A's writing the pattern count went 24→26 and the
verified-item total moved 357→350.

---

## 1. DO NOT CLAIM

Every line below was written into a draft, or into a brief a writer was given,
and is wrong. The correct form follows each.

1. ❌ **"6,144 bytes is the largest per-call working set."** The `work/call` field
   carries **five different units** across patterns (`B`, `probe`, `taps`, `cmp`,
   and bare) and one `model.py` says so outright — *"Units are the pattern's own
   — elements here."* One pattern's bare `4096` is 4096 `u64` = **32,768 bytes**.
   ✅ Scope it to one pattern, or drop the superlative. ⚠ **The parent repo's own
   `RECAP.md` still carries this error**, having already corrected 4,328 → 6,144;
   fixing the regex is not enough, because the unit is per-pattern.
2. ❌ **"The sign flips on p12, p13 and p42."** ✅ **Two** patterns. The third's
   reversal is a different object — a published span's endpoints — in a different
   table, and its search state prints `undeclared`.
3. ❌ **"510×"** unqualified. ✅ It is the **large** band; on the small band the
   same comparison is 62.5×.
4. ❌ **"rustc's LLVM is / is not bit-for-bit clang's."** `TOOLCHAIN.md` says same
   version and never addresses bit-identity; `results/SYNTHESIS.md` twice asserts
   bit-for-bit. **Live in-tree contradiction.** ✅ Claim the version only, and say
   the tree does not settle the rest.
5. ❌ **"Hardened C costs +5/+12 instructions, flat."** True of **one** pattern.
   ✅ Across the 25 patterns shipping a hardened rung the delta is **median 24**,
   range **−125…+10,242 (gcc)** and **−108…+5,637 (clang)**, negative on three
   patterns. The claim that survives is *writing the check is cheap where the
   check is all you are adding.*
6. ❌ **"Delete the safe rung's check and it panics."** ✅ True on **4 of the 8**
   patterns carrying the control; **conditional on 2** (the stripped rung prints
   C's answer bit-for-bit, exit 0, in the in-bounds regime); **false on 2** — one
   stripped safe rung is **bit-identical to C** at both measured optimisation
   levels, and another **hangs** instead of panicking.
7. ❌ **"The CVE port verifies clean."** ✅ `9 verified, 1 error` with the
   functional specification present — and **the failing obligation is the
   functional one, never an access obligation.** `10 verified, 0 errors` requires
   stripping the spec to a tautology. Write *every memory-safety obligation
   discharges*.
8. ❌ **"The constant-time mutant's obligation count is unchanged."** ✅ The
   **kernel's** is (3 → 3); the file total moves 12 → 14. The word *kernel* is
   load-bearing.
9. ❌ **"It leaks through timing."** ✅ Measured as **+7,088 instructions per
   call** between two inputs printing identical checksums. **No wall-clock or
   cycle measurement of the leak exists in the tree**, and the pattern's own notes
   say constant instruction count is a *necessary, not sufficient* condition.
10. ❌ **"A recursive kernel verifies and dies of stack overflow."** ✅ **There is
    no such pattern.** It is a *refused* catalogue candidate: its run logs contain
    zero occurrences of the exit code the claim quotes, its build script never
    invokes the prover, its sources do not survive a clone, and its own report
    says the verified function is not the same kernel. `RECAP.md` upstream
    registers it in a "family of three" — **a summary of a measurement is not the
    measurement.**
11. ❌ **"The handle table lets a use-after-recycle through."** ✅ That pattern is
    the **opposite** result; its own contract *forbids* the recycling design
    because the bug would become logical. The recycle finding belongs to a
    **reviewed probe on refused rows**, and its Miri evidence is a grep count on
    an invocation that also swallows failures — write *"Miri reported nothing"*,
    never *"Miri certifies it clean"*.
12. ❌ **"under `#![forbid(unsafe_code)]`"** of any shipped rung. It appears on
    **zero** shipped rungs; only on gitignored probes.
13. ❌ **"`harness/build.py` enables `_FORTIFY_SOURCE`."** ✅ It passes no such
    flag; **Ubuntu gcc's default at `-O2`/`-O3`** does. And the discriminator for
    the sanitizer blinding is the `_chk` symbol, **not the compiler** — clang with
    fortification forced on goes blind the same way.
14. ❌ **"ASan never sees the out-of-range shift."** Argued from the defect's
    shape, **never isolated** — there is no ASan-only build in the tree. And the
    stronger *"not ASan, not Miri, not a proof"* was **refuted in-tree**: UBSan
    fires, Miri fires (as a panic, so its UB flag stays false), the prover fires.
15. ❌ **"Nothing catches an infinite loop."** ✅ True of the **static** instruments
    only. A `decreases` clause catches it at compile time and a plain `timeout` at
    run time. Honest form: *nothing on this ladder **emits** the capacity check —
    the rungs that terminate write it by hand.*
16. ❌ **Proof totals without the words "shipped rungs."** With the one control
    included they are 357/110/235, not 350/108/230. ⚠ This exact defect shipped
    once: the site published the larger figures while the research published the
    smaller.
17. ❌ **The sanitizer fired/clean counts as a property of the matrix.** ✅ They come
    from **one build configuration** — gcc `-O1 -fsanitize=address,undefined`,
    isolated mode, the plain kernel only. No clang, no hardened rung, no Rust.
18. ❌ **"0 UB in 194 Miri runs"** unqualified. ✅ **192 executed, 2 blocked** at the
    180-second budget; no seed pinned; no flags set; and **Miri only ever runs the
    unsafe rung** — no safe rung in this project has been under it.
19. ❌ **"Ghost code fully erases" / "the proved binary is byte-identical."** ✅
    **Zero executed instructions** holds everywhere; *byte-identical* fails on one
    pattern, whose trait-declared ghost function is codegenned as a stub occupying
    a vtable slot (40 bytes against 32).
20. ❌ **"Nineteen claims were retracted"** with no denominator. Either supply one
    or do not lead with the count.
21. ❌ **Presenting one-edit mutants as gate results.** `controls_json` is `{}` on
    25 of the 26 gate records. ✅ *Reproducible from a committed generator; not
    gate-certified.* And where even the generator is missing — the flagship
    four-rung table's three Rust rows — say that the C row is the shipped rung and
    gate-certified while the Rust rows are scratch that does not survive a clone.
22. ❌ **"`undeclared` in the search-state column means nobody searched."** ✅ The
    tree states the opposite verbatim: *"An `undeclared` in this column means
    **nobody wrote an entry**, and it has never meant **nobody searched**."* The
    binary search prints `undeclared` and carries a **four-spelling** search in
    which **the shipped spelling is the dearest**.
23. ❌ **"Safety is free here"** read off a zero difference. **Nothing in the gate
    distinguishes a deleted check from two rungs that happened to compile to the
    same bytes.** This bounds the *delete-and-re-measure* method the report
    recommends, so it ships with the method.

---

## 2. FOUR THESES THE CORPUS CANNOT CARRY

1. **"Memory safety costs about X%."** The bucket distribution moves at searched
   values with two sign flips; 14 of 26 rows are undeclared; 4 are unlicensed for
   differencing; the identity pin holds one endpoint above its floor by a measured
   −17,526 instructions per call; one pattern's percentage is **wrong in sign at
   the other input**. No cross-pattern wall clock exists.
2. **"Rust catches it."** Zero of **4,104** adversarial runs end with a rung
   refusing to continue where the model says exit 0 — **not one bounds check fires
   anywhere in the shipped matrix** — and hardened C matched the model everywhere.
3. **"A proof buys memory safety free" / "verified means done."** The
   proved-minus-unsafe zero is a **tautology**: the identity pin entails it. A
   proof-enabling change cost 8.5% of one kernel and shipped described as free.
   No compile-time or authoring-hours data exists, so the price is a **floor**.
4. **"This corpus shows Rust is safer than hardened C."** It cannot distinguish
   them on outcomes. What it distinguishes is **non-optionality**, and only the
   deleted-check control measures that — on 4 of 8 patterns (see §1.6).

---

## 3. STANDING WORDING RULES

1. **"Plain, unchecked C"**, never "idiomatic C". A copy with the capacity in
   scope and no check is a defect, not an idiom, and calling it idiomatic is the
   cheapest attack on the paper.
2. **Never a bare "the shipped rung"** where a pattern ships six. Name the rung
   and name the input.
3. **No pattern IDs as nouns.** "A binary search", "a bitset probe" —
   `\pat{p07}` only where the reader might go look.
4. **Every number ships its scope where a screenshot cannot separate them** —
   the same sentence *or the one immediately after it*, and the one after is
   usually better.
   ⚠⚠ **AMENDED, and the old wording caused real damage.** This rule used to read
   *"in the same sentence"*, full stop. Nine writers applied it under four
   reviewers who each demanded more scope, and it produced sentences like *"they
   agree — firing together on two, silent together on three — though those three
   mix `no` with `vacuous`, which the legend insists differ; require one value
   and it is two of ten."* Every clause in that is true and the sentence is
   unreadable. **A short following sentence defeats the screenshot just as well
   and costs the reader nothing.** State the number, stop, then state the scope.
5. **Every limitation ships its direction.** *"Per-call constants transfer to your
   code; fractions of our kernels do not, because your function does other work."*
   A bare *"these are micro-kernels"* after a big claim reads as excuse-making and
   costs more trust than it saves.
6. **Round.** Full digits only where the exactness is the evidence — a gap of
   exactly zero, a residual of 0.000000.
7. **Verus's `N verified` counts items** — functions, loop bodies, sub-proofs —
   **not verification conditions.** Say so once before leaning on such a number.
8. **Write "cheapest found", never "minimum".** ⚠ *"Four patterns' published
   minima have since been beaten"* is the **stalest** version of this count and
   the tree disagrees with itself — four, five, five, five and six across six
   sources. They are **minima, not patterns**, and they belong to two or three
   patterns, not four. The supported form: **five published minima have been
   retracted across three patterns, plus two more elsewhere.** And a cheapest-found
   figure must name its **input** as well as its spelling — on one kernel no single
   safe spelling is cheapest on both blobs.
9. **Do not editorialise about C or Rust without a measurement.**
10. **Quote published papers from the PDF**, via a page-ranged read. The extracted
    text under `ref_papers/.temp/` **interleaves the two columns** and will
    corrupt any quotation.

---

## 4. HOW THIS FILE WAS PRODUCED, AND HOW TO EXTEND IT

Four grounding agents re-derived the corpus from `results/gate/*.json` and the
pattern sources; three reviewers then ran blind over a finished draft. **They
contradicted each other three times, and every settlement improved the paper** —
that is the argument for running them blind and in parallel rather than in
sequence.

Two rules that produced most of the entries above:

- **Open the log, not the write-up.** Entry §1.10 exists because two agents went
  to the primary artefacts and found a registered finding had no surviving
  evidence.
- **Ask which way the gaps point.** A separate reviewer, commissioned only to ask
  that, found four omissions in a finished draft **all favouring safe Rust** —
  one of them already on this project's own list of the omissions that
  constituted its documented coverage bias the previous time. Every figure in that
  draft reproduced correctly. **Checking a document's numbers cannot detect this.**

⚠ The supervisor's own rulings need the same treatment: one of them was
over-generalised from a single input to a whole pattern, and a reviewer caught
it. Entry §1.7's neighbour — which input discloses and which does not — is the
residue of that correction.
