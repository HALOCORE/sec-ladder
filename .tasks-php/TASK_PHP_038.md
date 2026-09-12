# TASK_PHP_038 — REVIEW the statistic findings, and **TRY TO BREAK F85**

**Role:** research **reviewer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_038_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM.** The last time a task in this
programme was told to *try to break* a prior task's headline rather than build
on it, it succeeded — F78, where *"closes to the digit with no residue"* turned
out to be an **arithmetic identity true of any input pair, including a false
mechanism**. ⭐ **That is the single most productive instruction this programme
has issued. You are the second.**

⚠⚠ **AND YOUR SUBJECT IS THE MANAGER'S OWN WORK, WHICH HAS BEEN WRONG FOUR
TIMES IN ONE ROUND** — F74's rule (F80), its premise (F82), its mechanism (F83)
and its generalisation (F84). **Not one error was arithmetic. Every one was
found by bringing a second method to something published from one probe or two
rows.** ▶ **Assume the same is true of what you are reviewing and go looking.**

**Read**, in this order:
1. ⭐⭐ **`.temp/mgr172/STATISTIC-DECISION-DRAFT.md` — the subject.** It is an
   **unreviewed proposal** and it says so.
2. `RECAP_PHP.md` — **F74, F80, F82, F83, F84, F85, F86**, and **open items 52,
   54, 60, 62, 64**. ⚠ F74 carries **two** in-place corrections; read them.
3. `.temp/mgr172/NOTES.md` — §7 and §9 are F83 and F84; **§10 is a `grep` error
   of mine** that asserted an absence from a line-based match on a phrase that
   wraps. **§8 is a rule-11 slip of mine.** Both are relevant to how much you
   should trust the rest.
4. The probes, all `--selftest` PASS: `.temp/mgr172/{identity_null,inclusive_ir,
   bc_sweep,flip_exact}.py` and `.temp/mgr170/{callee_share,spread_stat,
   null_control}.py`. ⭐ **Run every `--selftest` yourself and say so.**
5. `.tasks/PROTOCOL.md` — rules 6, **9**, 10, 11, 13, **14**. **Rule 9 is why
   this task exists**: none of F83–F86 may enter `.memory-php/` until you have
   been over it.
6. `harness/check.py`'s null-control docstring (search `269.52`) — **the frozen
   harness's own treatment, which is more careful than my probe was.**

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`,
`common-php/`, or `patterns-php/`** — this task measures and argues; it builds
no row. **You may add probes under `.temp/php38/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ **`grep -a` ALWAYS** (F35) — ⭐ **and see §5.6: a line-based grep cannot find a
prose phrase that wraps.**

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`14/0`**, first and last.
Both verified by the manager immediately before writing this. ⚠ **Nothing in
your scope should move either. If one moves, you have staled a measurement —
stop and report.**

---

## §1 ▶ THE PRIMARY TARGET: F85

**The claim.** Of 38 sign flips between family A and the whole-program figure
over 366 comparisons, **28 (76 %) are cross-language (C vs a Rust rung)**, and
on `ph29` they **survive family C**: A says `c-gcc` is **+33.01 %** dearer than
`safe_naive` on `large.bin` while **B, C and W1 all say ≈ 1 % CHEAPER**,
agreeing to ~2 pp.

⭐⭐⭐ **If that holds it is the most important finding in the programme**, because
the C-vs-Rust column is *"what does memory safety cost"* and A is this project's
most-published statistic. **If it does not hold, it is my fifth correction in
two days and I would much rather hear it from you.**

**Attack it in this order:**

1. ⚠⚠ **ITEM 64 IS THE MEASUREMENT AND IT IS CHEAP. DO IT FIRST.** `ph29`'s
   flips are re-derived against C; **`ph07`'s 6 and `ph03`'s 6 are NOT — they
   are family-B only**, and F84 showed B confounded **in both directions** by up
   to ~266 `Ir`/call. ▶ **Their binaries are on disk and md5-verifiable, and
   `.temp/mgr172/sweep_cg.sh` is the single regeneration entry point.** Add the
   C cells and report. ⚠ **If `ph07`'s or `ph03`'s flips do NOT survive C, F85's
   generalisation is broken and you have found it.**
2. ⚠ **CHECK THE BINARIES BEFORE BELIEVING ANY NUMBER.** `.temp/build/` is
   gitignored scratch that outlives sessions. `inclusive_ir.py::verify_binaries`
   compares the on-disk `kernel` md5 against the published record's `md5_fn`;
   **every probe of mine that reports numbers does this, and one that did not
   would be measuring a different program.** Confirm it, per row.
3. ⚠⚠ **THE OBVIOUS CONFOUND I HAVE NOT EXCLUDED: `n_iters` AND THE FIXED
   TERM.** F83 measures W1's fixed per-program cost at **~0.9 %** with **~0.075 %**
   failing to cancel. **I did not check whether the fixed term differs
   systematically between a C rung and a Rust rung** — different runtimes,
   different start-up. ▶ **If it does, part of the cross-language whole-program
   gap is start-up rather than per-call work, and family C (which excludes
   `main`) is the arbiter.** C and W1 agreeing to ~1 pp on `ph29` is evidence
   against this, **but it is not the test.** The test is the fixed term itself.
4. ⭐ **THE CONTROL THAT IS ALREADY THERE, AND USE IT**: two `ph29` comparisons
   do **not** flip (`c-gcc` vs `safe_naive` small; `c-gcc` vs `safe_tuned`
   large) and **agree across all four families**. A pipeline artefact should
   have moved them too. ▶ **Is that control strong enough? Say so either way.**
5. ⚠ **AND THE INTERPRETATION, WHICH IS SEPARATE FROM THE NUMBER.** Even if
   every flip survives, *"A is wrong on the cross-language column"* needs the
   further claim that the callee work **belongs** to the rung. F83's finding is
   that on an **R4/R5** pair it does **not** (byte-identical kernels, work in
   libc, caused by layout). ⚠⚠ **On a C-vs-Rust pair it plausibly DOES** — the C
   rung really links the shim and really allocates (F71, item 54). ▶ **Rule on
   this: is the cross-language callee work rung-attributable? It is the hinge,
   and the draft asserts rather than argues it.**

## §2 F86 — check the algebra, then try to break the conclusion

**Claims:** (a) `inside_share ≡ A/B`, so `a_ratio = (s_a/s_b)·b_ratio` is an
**identity** and *"the share ratio explains the disagreement"* explains nothing;
(b) a flip occurs **iff `1` lies strictly between the two ratios** — 0
mispredictions in 366; (c) therefore **no function of the shares alone can
certify A at any threshold**, so **publish both, always**.

1. **Verify (b) by hand on three cells**, not by re-running my script.
2. ⚠ **(c) is the load-bearing one and it is a NEGATIVE claim** — *no such
   function exists*. ▶ **Try to build one.** A function of the shares **plus a
   declared minimum effect size** might work, and rows do declare `Ir` floors in
   `spec.md`. **If you can build it, (c) is too strong.**
3. ⚠ **The BLIND class (14 cells) has no test at all** — the straddle predicate
   is a strict inequality and `a_ratio == 1` fails it. ▶ **Propose one, or say
   why it needs none.**
4. ⓘ I tried to reduce (b) to a scalar `|effect| < |mismatch|` and it is
   **refuted 30 of 346** — kept running and labelled in the probe. **Check that
   the counterexample list really is the wrong-side case I claim it is.**

## §3 F83 / F84 — the secondary targets

1. **F83's environment control** is one binary at three environment sizes,
   spread **0**. ⚠ **Is three enough, and is env size the right lever?**
   `check.py` attributes its ±7 to *a per-call **stack array**'s alignment* —
   ▶ **does `ph03`'s kernel even have one?** If not, my control tests a
   mechanism that could not have applied, and the real confound is untested.
2. **F84's `−1.00` claim**: `ph00` reads B `−1.000` / C `0.000`, and I assert
   this explains `check.py`'s documented **34 PAT cells at exactly `−1.00`**.
   ⚠⚠ **That is ONE PHP row generalised to 34 PAT cells and it is exactly the
   shape of error I keep making.** ▶ **Test it on a PAT row** — read-only,
   binaries in `.temp/build/`.
3. **F83's `p25` residual**: C `+167.872` vs B `+269.520`, leaving **~+101.65
   Ir/call unexplained.** I declined to invent a mechanism. ▶ **Find it, or
   confirm it is not cheaply findable.**

## §4 Traps

1. ⚠⚠ **`.temp/` IS GITIGNORED.** Every probe you are reviewing lives there and
   so does every number's provenance. **A committed claim resting on gitignored
   scratch is open item 65's defect** — ▶ **say which of F83–F86's numbers could
   not be reproduced from a fresh clone.**
2. ⚠ **`callee_share.py` and `flip_exact.py` DISAGREE on the flip count** (37 vs
   38) and I did **not** run that to ground — my parse of the former's output
   failed and I moved on. ▶ **Settle it.** One of them is wrong about a
   comparison, and which one matters.
3. ⚠ **Read the ERROR TEXT, not the exit code**, on any Verus run.
4. ⚠ **Declare your expectations before running each probe.** `_034` did and the
   expectations caught two of its own errors *"that would not have been visible
   from the output alone"*.
5. ⚠ **A must-fire case that fires for the WRONG REASON is worth nothing** (F79).
6. ⚠ **Do not bump the Verus/vstd pin.** ⚠ `clang` is at `~/tools/llvm/bin/clang`.
7. ⚠⚠ **`~266 Ir/call` is a number from ONE row.** If you quote it, quote the
   row. **Do not max a null over mode, level or input** — `check.py`'s own
   warning, which F82 violated in the finding that quotes it approvingly.

## §5 Definition of done

1. **Item 64 measured** — `ph07` and `ph03` against family C, with the binary
   md5 check, and the verdict on each flip.
2. **A ruling on §1.5** — is cross-language callee work rung-attributable? This
   is the hinge and it is a judgement; **argue it, do not assert it.**
3. **F86 (c) either survives your attempt to build a counterexample, or does
   not.** Say which.
4. **§3's three secondary attacks**, each answered or explicitly declined **as a
   scope reduction rather than a result**.
5. **§4.2 settled** — 37 or 38, and why.
6. ⚠ **A verdict per finding: UPHELD / UPHELD-NARROWED / REFUTED / UNTESTED.**
   ⭐ **`UNTESTED` is a perfectly good answer and is much better than a guess** —
   the draft's own §5 was staged with a blocker on itself for exactly that
   reason.
7. Both brackets, first and last, at `66/0` and `14/0`.
8. ⭐ **What you think the DECISION should be** (draft §4), in your own words.
   It governs how every row publishes and it is currently one manager's
   unreviewed opinion.
