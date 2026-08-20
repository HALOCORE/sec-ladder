# TASK_048 — p06's corrections, and the question underneath B1: can a pattern shrink its TCB by pushing the axiom into vstd?

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_047_REVIEW_REPORT.md`
in full — it is your whole task** — then `.tasks/TASK_047.md` and
`.tasks/TASK_047_REPORT.md` (what was asked and what you reported), then
`.memory/01-ladder.md` **finding 3** (`:435` — read the actual rule, not the
paraphrase) and **the direction-test "IT FIRED" block**,
`.memory/02-bench-rules.md`'s **"NEVER re-ship a rung"** and its two-number
reporting corollary, `.memory/03-measurement.md` (**the layout modes are at
`:789-921`, not in `05-layout.md`**), and `.memory/04-verus.md` **`:133` and
`:813`**, both of which the review shows are false.

**Read the good news first.** **The missing layout population was built and your
headline survives it** — `P(A>B) = 900/900` on both compilers and both inputs,
mode-matched, worst case still +15.50% / +53.68%, no sign flip. And the `d_cmp`
control you never ran shows **91.6% of gcc's +88.08 ns really is the divide**.
The manager's arithmetic objection (*"2.8 cycles per divide is below any x86
divider's throughput"*) was **wrong** and is withdrawn: it divided by the probe's
`+1.00 Ir/record` instead of the shipped law's `+8.00`, giving ~95 records/call
where the truth is ~12. At 12 records the ns figure lands on a divide's latency
exactly. **Your headline stands.** Most of this task is restating, not
re-deriving.

## The question I actually need answered — it is bigger than p06

B1 is right that `scr_load` is removable. But the review also records that
**the axiom relocates into vstd** rather than disappearing: what discharges the
write-back is `vstd/array.rs:175 ref_mut_array_unsizing_coercion` plus
`copy_from_slice`'s `assume_specification`. So the trust does not vanish — it
moves from a wrapper *this pattern's author wrote* into a specification *vstd
ships*.

**Trusted-base size is one of the five axes this project compares.** If a pattern
can shrink its published TCB by choosing a spelling whose axioms live in vstd,
then the TCB column is gameable and **every pattern's number means something
other than what it says.** That is a finding about the metric, not about p06.

⚠ **This is the call I am least sure of in this task, and it changes every
pattern's headline TCB, so settle it before you edit a number.** My reading:

> A hand-written `external_body` wrapper and a vstd `assume_specification` are
> both trusted, but they are not the same *kind* of trusted — one has an
> `ensures` the pattern's author invented and no one else reads, the other is
> shared, reviewed upstream, and used by every Verus program. So report **two
> numbers**, the way this project already reports two everywhere else:
> **author-written trusted items**, and **vstd assumed specifications relied
> upon**.

**If that is the wrong accounting, name the right one with the measurement** —
count what the alternatives actually give across p06 and p02, and say which
number a reader of the TCB column would be misled by. Whatever you choose, apply
it to p06 and **state what it would do to every other pattern's published TCB**
(you may compute that; do not edit other patterns to match).

## The two blockers

1. **`scr_load` is removable at zero codegen cost and the recorded reason is
   false.** `verus.rs:423-425`, `NOTES.md:510`, `NOTES.md:947` and your report
   all say the `split_at_mut` route "changes the exec text of four rungs". It
   does not: R5 without the wrapper is **18 verified / 0 errors**, twin **23/0**,
   `md5_raw 6608a63b5c52` — **byte-identical to shipped R4 and R5**, identity pin
   holding, checksums identical. **Land it on p06** and correct the attribution
   in all three places.
   - Because the codegen is byte-identical, this is **not** a re-ship under
     `.memory/02-bench-rules.md` — no rung's machine code changes and no
     published `Ir` moves. Say so explicitly, because the rule's text is about
     spellings and a reader will reach for it.
   - ⚠ **And answer the direction test in writing.** Removing a trusted item
     makes the trusted base *smaller*, which is the direction that flatters this
     project's thesis — exactly the shape the test exists to catch. My reading is
     that the test governs **declaration** edits and this is a **measurement**
     (the obligations discharge; the machine code is unchanged), which is the
     same category p13's repair fell into. **If that reasoning is wrong, say so**
     — it is the precedent that will license the next four TCB edits.
   - **p02**: the review shows `copy_bytes`'s contract discharges too (`2/0`, no
     `external_body`, no `unsafe`), so `.memory/04-verus.md:133` and `:813` are
     false in both halves. **Verify it yourself, then land it on p02 IF AND ONLY
     IF the codegen is byte-identical and `check.py p02` stays green — otherwise
     stop and report.** p02 is the project's strongest result; a hard stop is
     the right default. Whatever happens, p02's own `NOTES.md`, `README.md` and
     TCB tally must end consistent with the outcome.

2. **"R3 is `O(n)` at 2.00 Ir/byte" is one spelling's property, and p06 published
   the point instead of the class.** Your own in-contract, zero-`unsafe` control
   `c_idx` is **105 flat, 0.00 Ir/byte**, with an exact parameter-free law
   `Σα'(m mod 4) + 1`, α' = {13,15,16,17}, predicting **+80.00 (small)** and
   **+187.00 (large)** — both measured. And **zero of the shipped R3's 2.00
   Ir/byte is a bounds check**: it is the `zip`/`Rev` adaptor's two exhaustion
   tests per item (`cmpq +425`, `je +416`, `jne +360`, `jb −391`), and `pads.py`
   gives `safe_tuned` and `c_idx` **identical 11 pads at identical `line:col`**.
   - **Do not re-ship R3.** Publish both numbers, labelled, with the input named
     (`.memory/02-bench-rules.md`'s corollary): shipped R3, and cheapest-found
     in-contract R3.
   - Correct `NOTES.md:248`, `NOTES.md:420-425` and `README.md:41-47`, which
     carry the point as though it were the class.
   - **The "R3 dearer than R2" inversion is `small`-only and spelling-specific.**
     Say that wherever it appears. ⚠ The manager asked whether finding 3 needs a
     `.memory/` correction; the review's answer is **no — finding 3 is right and
     p06 did not follow it** (finding 3 is *"write two independent in-contract R3
     spellings and quote the cheaper"*, not *"always quote R3"*). **This is the
     fourth pattern to hit that failure mode** (p02, p16, p05). If you disagree,
     say so with the measurement.

## The three majors

3. **The two-number rule is satisfied on `small` only, and `large` carries the
   headline.** On `large`: gcc shipped **+57.80%** vs cheapest in-contract
   **+4.86%** — 11.9× — and **clang's cheapest in-contract hardening is 7.19%
   FASTER than the bug.** That last figure is unpublished and is a headline in
   its own right: on p06's `large`, *hardening is negative-cost on clang*.
   Publish both blobs' pairs.
4. **23% of gcc's published `+8.00·nrec` law is executed alignment padding.**
   `divq +1.000/rec`, **`nopl`/`nop` +1.833/rec**, `movzbl +4`, `movb +2`;
   `-fno-align-loops` moves the law **+95.00 → +73.00**. Decompose the law in
   `NOTES.md` and say which term is the safety line. `.memory/03-measurement.md`
   records only the *static* alignment caveat, so **write the executed-padding
   result into `NOTES.md` as the durable form** and the manager will lift it.
5. **"The twin is the sole catcher" and "caught by nothing but `spec.md`'s pin"
   are both false.** `b_weakreq` also fails the **contract pin** (2 clause diffs,
   simulated with `check.py`'s own comparator) and `b_scrmod_msonly` also breaks
   the **identity pin** (`n_fn 174/166` vs 208). Correct p06's §10, and add the
   qualifier the review asks for — the claim is *Verus-level* sole catcher, not
   sole catcher. **Then audit the same sentence in p02 and p12 and REPORT what
   you find — do not edit those patterns for this item.**

## The five minors

6. **`controls/verify_controls.sh`'s header documents controls that do not exist**
   (`a_nored_verus`, `b_msonly`) **and states expectations the pattern refutes**
   (that `b_msonly` and `b_tautology` must verify). It is the mutants'
   reproduction path, so its docstring is evidence.
7. **`b_scrmod` fails by `Resource limit (rlimit) exceeded`, not by the recorded
   obligation** (`NOTES.md:869`), and the pinned counts hide the difference. A
   mutant that dies of resource exhaustion is a weaker control. Either make it
   fail on an obligation or record what it actually does.
8. **`.copy_within(` is a forbidden spelling the prover does NOT exclude**
   (`vstd/std_specs/slice.rs:235`), so it is p13's **third** bucket — fiat, price
   unpublished — while `spec.md`'s `idiom.why` claims every fiat's price is
   published. Price it, and fix the stated reason (`copy_within` is `ptr::copy`
   within one slice, not a rotate through a temporary). `from_le_bytes` and
   `chunks_exact` are correctly disposed of; leave them.
9. **`results/gate/p06-rotate.json`'s `adversarial-past48.bin/c-gcc` stdout is
   not reproducible** (it reads uninitialised frame bytes past `scr` — the
   pattern's own point). A gate record carrying a number that changes every run
   must say so where a reader meets it.
10. **`α(m mod 8)` still has no mechanism.** Reported per-residue by you and
    unexplained by the review. Try once; if it does not fall out, say so and
    leave it named.

## Done when

Items 1–10 land plus the TCB-accounting decision; `check.py p06` green on a
complete run (and `check.py p02` green if you touched p02); `--check-stale`
clean; tables regenerated; `contract_sha256` moves if you touch the hashed block.
Every figure that moved is restated **everywhere it appears** — `NOTES.md`,
`README.md`, `spec.md` prose, and the results tables.

## Constraints

No root; no `/tmp` (scratch `.temp/p48/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/`** — item 5's
audit is a report, not a fix. **The only patterns you may edit are `p06` and —
under item 1's hard stop — `p02`.** Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
**no `nohup … &`**; no self-matching `pgrep` wait-loops. **Measurements in the
FOREGROUND, interleaved by cell.**

⚠ **`check.py p06` rewrites `results/gate/p06-rotate.json`** (ASLR addresses and
item 9's nondeterministic stdout). The reviewer hit this and restored with
`git checkout --`. Know which changes are yours before you leave the tree.

The reviewer's scratch is `.temp/r47/` with the layout population (`clayout.py`),
the `d_cmp` control, `pads.py`, the `c_idx` sweep, the vstd probes and
`repro.sh` **already built** — **reuse rather than rebuild.** Notes to
`.temp/p48/NOTES.md`.

**If a prescription here is wrong, say so with the measurement.** Seventy-one
agents have contradicted the manager and all seventy-one were right — you were
one of them seven times in one task, including on the sign of your own pattern's
headline. The manager's arithmetic objection in `TASK_047_REVIEW.md` item 1 is
already withdrawn above; **the TCB-accounting question at the top of this file is
the one I most expect to be wrong about**, and unlike the others it will govern
every pattern this project has left to build.
