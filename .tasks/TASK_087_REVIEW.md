# TASK_087_REVIEW — attack `p19`

**Role: research reviewer.** Adversarial by design. **A review that says "looks
good" without having tried to break something is a failed review.** You report;
you do not fix. Read `.tasks/PROTOCOL.md` first (Reviewer checklist, Severity),
then `.tasks/TASK_087.md` (what was asked), `.tasks/TASK_087_REPORT.md` (what
came back), then `patterns/p19-state-machine/NOTES.md` and `spec.md`.

Scratch in `.temp/r87/` — free, I checked. **You may run `harness/check.py p19`.**
Do not run a full sweep. **Do not run `harness/measure.py` in a way that rewrites
records**; `--check-stale` is read-only and fine.

⚠ **p19 is COMMITTED (`3962cb3`, `fb9e9ef`) and the tree is clean.** If you plant
into `patterns/p19-state-machine/`, snapshot **by bytes**, restore in a
`finally:`, and verify `git status --porcelain` is empty afterwards.

---

## What landed

The 23rd pattern. Gate `PASS`, 0 failures / 0 loud / 0 blocked, Verus **12/0**
(twin 13/0), TCB 3, `identity` O0 `norel` / O3 `exact`, `0 STALE`.

**`Ir` per message byte:** R2 15.00 · R3 9.75 · R4/R5 8.75 · c-gcc 11.00 ·
c-clang 8.75. **`R2 − R4 = 6.25 = 3.00 check + 3.25 foreclosed 4× unroll`.**

⚠ **The engineer contradicted the manager four times and was right each time** —
three numbers the manager had written into the catalogue from `TASK_086`'s probe
(`exit 139`, `+5.25`, `+4.25`) plus the shippability of a three-way rung matrix.
**Those are already corrected. Do not re-report them; DO check the corrections
are right.**

---

## The attacks, in priority order

### ⚠⚠ A1 — the headline, and the thing most worth breaking

> *"LLVM lowers the bounds check to `cmp $0x8`, a STATE-RANGE check. Safe Rust's
> automatic check and the validation pass C omits are THE SAME PREDICATE —
> enforced once per access versus once per call."*

**This is p19's result. Attack it.** Is the `cmp $0x8` really the bounds check,
or is it a range check LLVM derived for another reason and the *actual* bounds
check is elsewhere or absent? **Disassemble all six rungs yourself.** If the
predicate is genuinely the same, say what would have made it *not* the same.

### ⚠⚠ A2 — is the safe/unsafe boundary REAL, or does the validation pass make R4 sound and the comparison vacuous?

The engineer's own §0b argument is that after the validation pass **`st < NST`
on every path reaching the fold, so `st & 7 == st` identically** — and that
equality *is* R5's loop invariant.

⚠ **If the pass makes the index provably in range, then R4's `get_unchecked` is
not "unsafe reintroducing the bug" — it is a redundant check removal, and the
pattern may be measuring the cost of a check that is dead in every rung.**
**Which is p05's `dead panic` situation, and p05 needed the nonlinearity
argument to make it interesting.** Ask: *is p19's check dead? If so, why does
deleting it change anything, and what exactly does R2's 15.00 vs R4's 8.75
price?*

⚠ **The related question, and it is the kill risk the task file named:** the
pattern pins **two `forbidden` entries that forbid a spelling for being SAFE**
(the table must be loaded *data*, dispatch must be by *indexing*). The engineer
calls these *"the only entries in the tree that forbid a spelling for being
safe."* **Verify that claim by grep**, and then ask the harder question: **is a
contract that forbids the safe spelling a legitimate pin, or is it
`Rust-in-C-syntax` in the other direction** — a benchmark rigged so the bug is
reachable? The AppArmor precedent is the defence; **weigh it, do not just cite
it.**

### ⚠ A3 — the CVE citations, which are NOT verified

`patterns/p19-state-machine/NOTES.md` cites **`CVE-2026-23407`** and
**`CVE-2026-23269`**. ✅ **The AppArmor SOURCE is manager-verified real** —
`.temp/t87/apparmor_match.c`, 21 467 bytes, genuine
`SPDX-License-Identifier: GPL-2.0-only` header, 5 hits for
`aa_dfa_match_until`/`verify_dfa`. ⚠ **The two CVE IDs were NOT checked and
cannot be checked offline.** **Confirm them or recommend striking them.** A
fabricated CVE number in a committed pattern doc is the kind of error that
destroys trust in everything around it, and the argument **does not need
them** — the source read carries it.

### A4 — the ordinary checklist, with the ones that bite here named

- **Constant folding / leaked constants.** Is the table genuinely coming from
  the file at run time? The whole pattern turns on it being *loaded data*.
- **Are the six rungs semantically equivalent?** R2 and R3 are claimed to agree
  on all 8 inputs. **Re-run and check.** Does any rung quietly do less work?
- **Is R2 a fair naive port or deliberately pessimised?** Its 15.00 vs R4's 8.75
  is a big gap.
- **Is R3 actually check-free, or did it move the check?**
- **The `model.py` independence.** It *computes* `sanitizer_expect` — does it
  genuinely re-derive it, or does it encode the same table walk the kernel does?
- **The TCB tally: recount it.** 3 items, 1 with a contract. Are both `ensures`
  conjuncts load-bearing and neither `requires` conjunct a tautology, as
  claimed?
- **Does R5's exec code actually match R4's?** `identity` says `exact` at O3 —
  ⚠ **and the engineer disclosed that R4's spelling was CHOSEN to match R5's**
  (`fn subrange(…)` instead of the inline `&buf[off..off+len]`, which landed at
  `differ` at O0). **Is that an honest disclosure or a rigged pin?** Weigh it.
- ⚠ **Extract kernel bytes from the LINKED binary** (`TASK_086` #238,
  manager-verified: a relocated field is zero in a `.o`, so two kernels
  differing only in a call target md5 identically there).

### A5 — the second result, which is not about Rust

> *validation is `O(table)` once and the bounds check is `O(message)`, so the
> buggy C rung is **5071 `Ir`/call cheaper than unsafe Rust at `small` and 3569
> dearer at `large`***, difference `2.25·m − 5647`, zero at m ≈ 2510.

**Check the crossover arithmetic and check the claim that
`c-gcc-h − c-gcc = +10242` and `c-clang-h − c-clang = +5637` are identical at
both inputs** — that identity is what makes "constant, not slope" a measurement
rather than a description.

### ⚠⚠ A6 — A MANAGER CLAIM, so rule 3 says someone else must attack it

Verifying the engineer's note, the manager established and committed:

> **`vstd::slice::slice_subrange` is `#[verifier::external_body]` — a trusted
> EXEC function — and p19 is the ONLY pattern in the tree that calls a vstd exec
> trusted function from its kernel. p19's published TCB is 3, none of them
> vstd's. So RECAP "Owed" 0's SIXTH ROUTE is no longer hypothetical: a published
> TCB of 3 omits a trusted exec body this kernel actually calls.**

Evidence used: `grep -l slice_subrange patterns/*/verus.rs` → p19 alone;
`vstd/slice.rs` `#[verifier::external_body] pub exec fn slice_subrange`; p19's
gate record `tcb_items ['buf_get_unchecked','load_input','emit']`.

⚠ **Attack it three ways.** *(1)* Is the grep complete — does any other pattern
reach a vstd trusted **exec** item under a different name? *(2)* Is the framing
right, or is vstd's trusted base **correctly** outside a column that means
"project-local trusted items", making this a non-finding? *(3)* If it *is* a
finding, does it change p19's published number, or only the prose around it?
**Say which.**

---

## What I want back

PROTOCOL's report format, severity-ranked (`blocker` / `major` / `minor`), each
with a **concrete failure scenario**. **3 real blockers beat 20 nitpicks.**

⚠ **PROTOCOL rule 6: give me your CLEAN NEGATIVES BY NAME.** Attacks that did
not land are worth as much as findings and stop the next agent re-running them.

---

## Constraints

- `.temp/r87/` only. No `/tmp`. Keep the generator, delete the artefact.
- **Notes in `.temp/r87/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Report durable facts; do not write them.
- **You review, you do not fix.**
- **Do not touch `harness/build.py` or `harness/asm.py`** — measurement-hashed.
- Never `pkill`/`killall`. Do not bump the Verus/vstd pin. Do not edit `pilot/`.
- ⚠ **Cite `check.py` by FUNCTION NAME, never `check.py:NNNN`.**

---

⚠ **PROTOCOL rule 2's running count is 245.** **Every agent that has contradicted
the manager with a measurement has been right — 245 times, and four of those
were this pattern's own engineer correcting numbers I wrote.** My least-sure
call here is **A6**, which is mine and is committed. **A2 is where I think the
pattern is most likely to be wrong.** Contradict either with a measurement and
say so plainly. Carry the count forward incremented by what you find.
