# TASK_155 — review `p34`, and attack the `0.00` GRADIENT first

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read first: `.tasks/TASK_154_REPORT.md` **in full** (631 lines);
`patterns/p34-refcount-stack/`; `.tasks/TASK_154.md` (what was asked);
`.temp/mgr149/NOTES.md` (the manager's pre-build verification — **its §1 proof is
the manager's own and rule 3 says a different agent must attack it**);
`CLAUDE.md` **rule 6**; `.memory/03-measurement.md` entries **19–22**;
`patterns/p28-intrusive-lists/` and `patterns/p32-free-list-pool/` (the two
nearest temporal rows).

## ⚠⚠⚠ THE ONE THING YOU MAY NOT DO

**You may not recommend refusing, shrinking or retiring this row for any
RUST-SIDE, VERUS-SIDE or LADDER-SIDE reason.** *"The safe `Rc` port cannot
express the bug"*, *"the R5 models the counter itself because vstd has no
`strong_count`"*, *"the benign gradient is zero so there is nothing to price"* —
**every one is a FINDING, and the last is this row's HEADLINE.**
✅ **A row may fall on ONE ground only: its C MECHANISM duplicates a BUILT
row's.** That is item 1.

## What to attack, in order of what a wrong answer costs

1. ⚠⚠ **THE C-MECHANISM DISTINCTION.** The claim is that the repair site is a
   **third position**: `p27`, `p29`, `p32` fix the READ; `p28` fixes the DESTROY
   path; `p34`'s read is correct by construction so **only the ACQUIRE can be
   repaired**, an unbounded distance from the harm. ⚠ **`p28` is the sharpest
   attack — both are "a real `free()` then a read of the freed block", both
   safety lines are maintaining WRITES that ask nothing, and both are
   `heap-use-after-free` on two compilers. Is the distinction IN THE C CODE, or
   only in the vocabulary the manager used to describe it?** ⚠ Also try `p32`
   (a recycle rather than a free) and the **unbuilt but ADMITTED `p25`**
   (`.temp/mgr155/NOTES.md`) — if `p34` and `p25` duplicate each other, **say so
   now**, before `p25` is built.

2. ⚠⚠⚠ **HEADLINE 1 — `0.00 Ir`, AND IT IS THE CLAIM MOST LIKELY TO BE A
   TAUTOLOGY OF ITS OWN PLUMBING.** The manager verified from the record that
   `c-gcc` and `c-gcc-h` carry **byte-identical `marginal_ir_per_call` in all 8
   cells**, and `c-clang`/`c-clang-h` likewise — 16 cells, no exceptions.
   ⚠⚠ **THAT IS EXACTLY THE SHAPE OF A CHECK THAT COULD NOT HAVE FAILED**
   (RECAP item 2: the manager's own `axiom_decls` tautology). **ASK WHAT WOULD
   MAKE IT NON-ZERO, THEN MAKE IT NON-ZERO.** Concretely:
   - **Is `c/kernel_hardened.c` actually built and actually measured**, or did a
     fallback measure `c/kernel.c` twice? ✅ The manager checked the two files
     differ by exactly one line (`t->rc = t->rc + 1`, `+1/−0`) and the record's
     `source_sha256` re-derives clean — **but that is not the same as proving the
     hardened BINARY is the one whose `Ir` was recorded.**
   - ⚠ **PLANT A COST INTO `c/kernel_hardened.c`** — a loop, a volatile store —
     re-measure that one cell, and confirm the number MOVES. **If it does not,
     every `0.00` in this row is an artefact.** ⚠ Restore in a `finally:` and
     **verify by BYTES against HEAD.**
   - ⚠ The engineer reports the STATIC count DOES move (`+1` at `-O3`, `+5` at
     `-O0`). **Confirm that, because it is the evidence the binaries differ.**

3. ⚠⚠ **THE PROOF THAT NO BENIGN INPUT EXECUTES THE SAFETY LINE — IT IS THE
   MANAGER'S OWN AND PROTOCOL RULE 3 REQUIRES A DIFFERENT AGENT TO ATTACK IT.**
   *"The safety line is the kernel's only increment, so every `rc` is
   permanently 1; any executed `DUP` leaves two stack entries naming a
   one-reference object, and the two releases that must follow go `1 → 0`
   (free) then `0 → underflow`."* **Try to construct a benign input containing a
   `DUP` that stays memory-safe in R1.** Consider: the `ntop < P34_CAP` guard, an
   early `break` on a short stream, a `DUP` whose object is never released,
   stack exhaustion, `nops` overflow. ⚠ **And check `controls/no_dup.py` is a
   real derivation over the SHIPPED blobs, not a restatement of `gen.py`'s
   intent** — *"0 DUP ops on every matrix input, 48 adversarial"* is exactly the
   kind of count that can be read off the generator instead of the artefact.

4. ⚠⚠ **THE SAFE-ARENA BIT-FOR-BIT CLAIM — the row's biggest headline.**
   `controls/safe_arms.py` reports that a safe INDEX-ARENA port under
   `#![forbid(unsafe_code)]` reproduces `c/kernel.c` on **8/8 inputs including
   the recycle divergence** (`16102462438644451328`, which the manager confirmed
   equals the record's `adversarial-recycle.bin/c-gcc` stdout), while the `Rc`
   port **cannot compile** the bug (`E0507`/`E0502`). ⚠ **Attack both halves.**
   Is the arena port an honest idiomatic port, or a transliteration built to
   match? ⚠⚠ **AND THE `E0507`/`E0502` HALF IS THE ONE THIS PROJECT HAS BEEN
   WRONG ABOUT BEFORE: `p25`'s `E0502` and `p28`'s `E0382`/`E0499` were BOTH
   non-distinguishing — seven controls with no container at all printed the same
   `E0502`, and the `E0382` was a plain double move.** **Demand a control that
   CANNOT have the bug and check it does not print the same error.**

5. ⚠ **THE SURVIVING NOVELTY CLAIM, AND THE MANAGER'S DERIVATION OF IT.** The
   build task's claim was **false on both halves** (engineer-refuted). What the
   manager then re-derived and wrote into `composition.py`'s `CAVEATS["p34"]` is
   narrower: *"the FIRST TEMPORAL row with a DETECTOR-ONLY cell; the other three
   rows holding one are `p18`, `p38`, `p42`, none temporal."* ⚠ **Attack the
   derivation, not just the conclusion.** It used `sanitizer[input].fired`,
   `adversarial[input/c-gcc].diverges`, and **`len(rows) == 1` as a
   reproducibility proxy** — ⚠ **is that proxy sound?** And **why did `p29` and
   `p32` fall out of both lists** — is that right, or an artefact of the filter?

6. ⚠⚠ **THE FLATTERING-DIRECTION TRAP, SEVENTH INSTANCE — AND THE ENGINEER
   CAUGHT ITS OWN.** `controls/spellings.py` found the shipped-pair `R3−R4` gap
   at `-O0` overstates by **2.88×/3.36×** once both sides are searched; at `-O3`
   the shipped pair *is* cheapest-found. ✅ **Good.** ⚠ **Now attack the
   CORRECTED figure:** the engineer says *"one lever per side, cheapest FOUND,
   not minimum"* and did **no C-side spelling search at all** (named as the
   weakest endpoint). **Count the levers on each side and say which endpoint is
   weaker.** ⚠ **And check every figure is given at BOTH optimisation levels** —
   `p35`'s lesson is that the comparison can REVERSE, and this report says
   `arr_get_unchecked` and `R2`-vs-`R3` both do.

7. ⚠ **`model.py` AND ENTRY 19.** The task predicted the harm would be
   unrepresentable in Python and the engineer **contradicted that**:
   `sanitizer_expect` is **DERIVED**, from "a touch of a returned-to-allocator
   object". ⚠⚠ **A derived check owes an arm that SHOWS IT FIRING** — the
   engineer ships a six-cell must-fire arm; **run it, and break the model to
   confirm it reports rather than crashes.** ⚠ **And the engineer flags its own
   argument as unreviewed: the derivation models glibc LIFO recycling, which
   ASan's quarantine does not.** **That is your job.**

8. ⚠ **THE R5.** `24 verified / 0 errors`, `7` trusted items, **`0`
   `axiom_decls`**, `5` twins at `29/0`, `blocked []`. Claimed **first
   multiset-flavoured obligation in the tree**
   (`perms[k].value().rc == cnt(ids, k)`), with leak-freedom as a corollary.
   ⚠ **State-novelty claims are this project's most-refuted class — check it.**
   ⚠ Verify the mutant battery: **`X2` FAILS where `p32`'s equivalent VERIFIES
   and `X1` FAILS where `p35`'s VERIFIES** — **re-derive both**, since that is a
   three-row comparison resting on one agent's runs. ⚠ Try the arms the battery
   lacks: `assume(false)` (must be a FAIL unless declared — check it is not
   declared), an unreachable body, a `requires` nothing can discharge.
   ⚠ **`global layout` is reported as a SIXTH body-less form `vparse.axiom_decls`
   does not see. Confirm, and say whether that is a gate hole.**

9. ⚠ **`identity` is `norel` at BOTH levels**, not `exact`. Mechanism claimed:
   link layout, a rip-relative `lea` to the opcode jump table, with all
   norel/norm digests and counts identical. ⚠ **Verify it is layout and not R4/R5
   exec DRIFT** — the reviewer checklist asks *"does R5's exec code actually
   match R4's?"*, and `norel` at both levels is unusual for this tree.

10. ⚠ **Positive controls, per detector.** `ctl_asan.c` and `ctl_ubsan.c` both
    ship. **Confirm each EXECUTES and each licenses the detector column it is
    quoted for** — `p35` exists partly because an ASan-shaped control cannot
    license a UBSan column, and the manager found the same gap again in `p25`'s
    demonstration this session. ⚠ Check clang has not eliminated either.
    ⚠ **Also check the Miri invocation is well-formed** — `TASK_148` shipped one
    missing `--` that scored a NON-RUN as *"no UB"*. `runs: 8` in the record.

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. **Is `p34` FINISHED?** ⚠ Gate-green is not finished — a pattern is finished
   when a reader can find its result. **Check `results/synthesis.md` carries it
   and that the published table matches a fresh render.**
3. ⚠⚠ **ANYTHING THE MANAGER OVERSTATED**, and there are three fresh places to
   look: the **commit message of `dd46507`**, **`CAVEATS["p34"]` in
   `harness/tools/composition.py`**, and the **`TEMPORAL 5`** edit to
   `.memory/02-bench-rules.md`. ⚠⚠ **The manager has shipped a wrong or
   over-general sentence into a task file or a committed artefact in EVERY
   RECENT PATTERN — `p28d`'s `hp`, *"ASan structurally never reports a WRITE"*,
   repair 3's cost premise, the coin-flip band, and now `p34`'s novelty claim.
   Assume the same here and look for it.**
4. ⚠ **The engineer's own disclosed gaps** — a `NOTES.md` edit after the green
   run that invalidated `source_sha256` and was reverted (**verify by bytes that
   the revert is complete**); no C-side spelling search; no `-O1` column; the
   two admissible R4 variants verified but their **R4≡R5 pairing not
   re-derived**. **Close the last one or say why it cannot be closed.**
5. ✅ **CLEAN NEGATIVES ARE WORTH AS MUCH AS FINDINGS** (PROTOCOL rule 6). Name
   the attacks that did NOT land so the next agent does not re-run them.

## Rules

- `.temp/t155/` only. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md` or `patterns/p34-*/`.** No `git add`/`git commit`.
- ✅ **You MAY run `harness/check.py` and `harness/measure.py`** — a single
  pattern, never the tree. ⚠ A single pattern's gate can take **30+ minutes**;
  run it in the background and wait on the exact PID.
- ⚠ **If you plant into `patterns/p34-*/` — and item 2 asks you to — restore in
  a `finally:` and verify by BYTES against HEAD.** ⚠ **`c/*` and `*.rs` are
  MEASUREMENT-HASHED**, so a plant that outlives its restore stales the record;
  re-derive `source_sha256` afterwards with the one-liner in
  `TASK_154_REPORT.md` §14.
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log — not
  with a regex alternation, and not with a loop matching a prefix a log header
  shares with its verdict.** Three mechanisms, one cure
  (`.memory/03-measurement.md` 21–22). Expect `p34` = `PASS`, `blocked []`.
  ⚠ **And `rc=$?` after a PIPE reads the LAST command's status, not the
  script's — the manager did exactly that this session and misread a FAILING
  `composition.py --check` as `rc=0`.**
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
  **Copy from them; do not modify them.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ Grep
  `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec exists".
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`;
  **every harm probe owes a positive control that must fire, in the detector
  whose column it licenses.**
- ⚠ `python3 harness/tools/contract_diff.py p34` says what moved inside the
  hashed block, from `git` alone. ⚠ The contract moved once during the build
  (`1fa98c8a… → f1537d7f…`, a deletion the gate's stage 5c forced); **verify
  that disclosure.**
- Report to `.tasks/TASK_155_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 882.** ⚠ `TASK_154_REPORT.md`'s
closing paragraph records **six manager claims contradicted by measurement** but
**did not carry a measurement figure forward**; the manager reconciles here and
sets the launch figure at **882**. Carry it forward in your own closing
paragraph. ⚠ **Reconciliation across branches is the manager's job, not yours.**
