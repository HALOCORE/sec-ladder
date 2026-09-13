# TASK_PHP_049 — **IS THE C BASELINE A FREE PARAMETER?** Attack item 111, which is the manager's own work from one probe

**Role:** research **reviewer / analyst**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_049_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM — AND THE SUBJECT IS THE
MANAGER'S, FROM ONE PROBE, POINTING WHERE THE MANAGER WANTED IT TO POINT.**
`.memory-php/04-process.md` **law 12**: *a manager finding from one probe or two
rows should be assumed narrowable until a reviewer has had it.* ⭐⭐ **`_047`
just measured law 12 at five for five — of six findings verdicted, NOT ONE
survived as written.** ▶ **Assume the same here. Item 111 is a QUESTION the
manager routed, not a finding; nothing from it is in `.memory-php/` and nothing
goes there on your say-so either.**

⭐ **THIS TASK IS CHEAP: every number in item 111 came from committed records
with NO build and NO callgrind run.** ⛔ **So if you find yourself needing to
build something, stop and say why** — that is itself the answer to deliverable 3.

---

## §0 WHY THIS RUNS BEFORE ROW 9

**Row 9 (`_048`, written and waiting) will publish cross-language figures.** If
item 111 holds, *how* it publishes them changes. ▶ **That is the only reason this
jumps the queue, and it is why the task is scoped to measurement and ruling
rather than to a corpus-wide repair.**

**Read**, in this order:

1. `RECAP_PHP.md` — **open item 111** (it is the whole brief, with the manager's
   numbers and the manager's own statement of the confound), then the ⭐ **which
   statistic** cell at `:82`, then **`ph03`'s row-1 table and its note 4** near
   `:1010-1042`, then **F85 · F86 · F91 · F92**.
2. `.tasks-php/STATISTICS_001.md` — **all of it**, and note that **§at `:92` names
   `c-gcc` explicitly** where the RECAP summary cell says *"C"*.
3. `.memory-php/03-numbers.md` — the `inside_share` rule and the four qualifiers.
4. `.tasks-php/TASK_PHP_047_REPORT.md` §2 — ⭐ **the worked example of how a
   one-input number dies on a second input.** That is this task's method.

---

## §1 ⭐⭐⭐ DELIVERABLE 1 — **RE-DERIVE IT, AND CHECK THE MANAGER DID NOT PICK THE ROW AND THE INPUTS WHERE IT WORKS**

**The claim, from `results-php/ph29-recvfrom-alloc.json`, A1
(`kernel_exclusive_ir`), `O3/isolated`:**

| input | baseline | C dearer than `safe_naive` by |
|---|---|---:|
| `large.bin` | `c-gcc` | **+33.01 %** ← reproduces RECAP's published `+33 %` |
| `large.bin` | `c-clang` | **−4.36 %** |
| `small.bin` | `c-gcc` | +39.92 % |
| `small.bin` | `c-clang` | **+0.95 %** |

▶ **ATTACK IT:**

1. **Re-derive all four independently** and say which file and which field.
2. ⛔⛔ **THE SELECTION QUESTION, AND IT IS THE MAIN ONE.** `ph29` is **one row**,
   `safe_naive` is **one rung**, and `O3/isolated` is **one cell**. ▶ **Sweep the
   FULL cross product** — every row, every Rust rung (`safe_naive`, `safe_tuned`,
   `unsafe`, `verus`), every input, `O0`/`O3`, `isolated`/`whole` — **and report
   how often the `c-gcc` → `c-clang` swap changes the SIGN.** ⭐ **A rate is the
   answer; `ph29` may be an outlier and the manager would not know.**
3. ⚠ **Check the `~1 % cheaper` comparison is even like-for-like.** RECAP says
   *"three other statistics say ~1 % cheaper"*. ▶ **Which three, on which cell,
   and against which C baseline?** ⛔ **If those three were themselves computed
   against `c-gcc`, then "clang's A1 agrees with them" is comparing a clang
   number to three gcc numbers and the agreement is not evidence of what the
   manager says it is.** **This is the single most likely way item 111 is wrong.**

---

## §2 ⭐⭐ DELIVERABLE 2 — **THE CORPUS-WIDE SIGN-FLIP COUNT**

**The manager's table, A1, `small.bin`, clang relative to gcc, identical extracted C:**

| row | O3/isolated | O0/isolated | O0/whole |
|---|---:|---:|---:|
| `ph03` | −15.27 % | −23.53 % | −23.55 % |
| `ph07` | −16.27 % | −18.92 % | −18.92 % |
| `ph16` | −1.86 % | ⭐ **+32.91 %** | +31.55 % |
| `ph29` | −27.85 % | −24.08 % | −24.11 % |
| `ph45` | −9.91 % | ⭐ **+7.96 %** | −0.45 % |
| `ph52` | −15.51 % | −42.11 % | −42.17 % |
| `ph53` | −29.96 % | −20.32 % | −22.27 % |
| `ph64` | −2.30 % | ⭐ **+17.39 %** | +17.39 % |

**8 rows · |min| 1.86 % · median 15.51 % · |max| 42.17 %; the sign reverses
between `O0` and `O3` on three of eight.**

▶ **Re-derive it, extend it to `large.bin`, and then answer the question that
matters: HOW MANY PUBLISHED OR PUBLISHABLE CROSS-LANGUAGE CLAIMS IN THIS CORPUS
WOULD CHANGE SIGN UNDER `c-gcc` → `c-clang`?**

⭐ **Distinguish three populations and report them separately** — they have very
different consequences:

| | |
|---|---|
| **published** | a figure that appears in `RECAP_PHP.md`, `.memory-php/`, `STATISTICS_001.md` or a row's `NOTES.md`/`README.md` |
| **publishable** | a cell pair a row could quote but does not |
| **already labelled** | a figure that names its C baseline ⭐ **`STATISTICS_001.md:92` does; the RECAP summary cell does not** |

⚠ **F85/F86's flip machinery exists** — `.temp/php38/flip_columns.py`,
`.temp/mgr172/flip_exact.py`. ⛔⛔ **BOTH ARE GITIGNORED and may not survive; if
they are gone, say so and write your own rather than reporting an absence as a
result.** ⚠⚠ **AND F86's own warning: its first classifier scored `BLIND` as
`FLIP` and inflated 38 to 52 — make sure you are using the corrected one, or
your own.**

---

## §3 ⛔⛔⛔ DELIVERABLE 3 — **SETTLE THE ATTRIBUTION CONFOUND, AND *"NEEDS FAMILY C"* IS A VALUED ANSWER**

**The objection:** A1 is **symbol-scoped**, so a compiler that inlines
differently moves work across the `kernel` boundary **without changing the work
done**. `inside_share` is **22.24 %** on `ph52`'s C cells — A1 sees under a
quarter of the C's work, and *which* quarter is a codegen choice.

**What the manager offers against the simplest version of that, and you should
attack both legs:**

1. **At `O0`, `isolated` and `whole` agree to ≤ 0.1 pp on six of eight rows**,
   and `O0` is where inlining is minimal — yet the gap is 8–42 % there.
   ⚠ **Verify the ≤ 0.1 pp claim on all eight rows and both inputs.** ⛔ **And
   check `ph45`, where `O0/isolated` (+7.96 %) and `O0/whole` (−0.45 %) DISAGREE
   IN SIGN — the manager's own table shows it and the manager's sentence says
   "six of eight". What is happening on that row?**
2. ⭐ **The static size goes the WRONG WAY for the attribution story.** `ph29`,
   `O3/isolated`, symbol `kernel`, from the measurement record's own `static`
   block: **`c-gcc` `n_nopad` 338 / 1388 B** against **`c-clang` 476 / 2176 B** —
   **clang holds 41 % more static code while executing 27.85 % fewer dynamic
   instructions.** ▶ **Is that really a loop-transformation signature, or can a
   compiler inline a COLD helper (adding static code that rarely runs) while
   keeping a HOT one as a call (removing dynamic work from the symbol)?**
   ⛔ **That single alternative would restore the confound completely. Settle it
   — `harness/asm.py` is the gate's only objdump pipeline and it can show you the
   call sites.**

⭐⭐ **AND THE ANSWER MAY HONESTLY BE *"THIS NEEDS THE WHOLE-PROGRAM COLUMN"* —
WHICH IS ITEM 62, DELIBERATELY UNBUILT.** ▶ **If so, SAY SO AND STOP**, because
that re-scopes item 62 from *"is A the wrong column"* to *"is the C baseline a
free parameter"*, and **that re-scoping is worth more than a forced answer.**
⛔ **DO NOT BUILD FAMILY C IN THIS TASK.**

---

## §4 ⭐ DELIVERABLE 4 — **WHAT MUST A CROSS-LANGUAGE FIGURE BE LABELLED WITH, AND WHAT WOULD ENFORCE IT?**

⭐⭐ **THE RULE ALREADY EXISTS AND WAS WRITTEN AT ROW 1**, in `ph03`'s own table,
note 4:

> ⚠ *"`c-clang` beats `c-gcc` by 15.4 %, **which is larger than every safety
> effect on this row**. A compiler difference, not a safety difference — **quote
> a rung against a rung, never against "C"**."*

⛔ **And the *"biggest open thread"* sentence says "C".** ✅ **`STATISTICS_001.md`
gets it right.** ⭐ **So the ARGUMENT DOCUMENT is more careful than the SUMMARY
CELL — the pattern `CLAUDE.md` records for the PAT side, where `SYNTHESIS.md`
twice beat `RECAP_PAT.md`.**

▶ **DELIVER: (a)** a census of where cross-language figures appear **unlabelled**;
**(b)** a ruling on whether *"quote a rung against a rung"* is sufficient as
written or needs the baseline named explicitly; **(c)** ⭐ **a CHECK that would
enforce it** — `boxcheck.py`/`citecheck.py` are the models, and
`contract_audit.py` is the newest and carries the **ratchet + hand-adjudication**
pattern you should copy if your check is a grep.
⛔⛔ **IF YOU WRITE A CHECK IT LANDS WITH ITS MUST-FIRE NEGATIVES INSIDE IT**
(`PROTOCOL_PHP.md` §H), **not in `.temp/`** — item 97 measured 13 §H-at-risk
citations across 4 rows for exactly that.
⚠ **A grep has a spelling** (F10). ⭐ **`contract_audit.py` found 4 false
positives in 6 hits and adjudicates every one BY HAND rather than tuning the
regex — because tuning a regex until the count looks right is the anti-pattern
this programme keeps catching.**

---

## §5 ⚠ WHAT THIS TASK MAY **NOT** CONCLUDE

* ⛔ **It may NOT conclude that family C or item 62 is unnecessary.** F85's
  corpus-wide count — **29 of 38 sign flips live in A and 28 of 29 SURVIVE family
  C** — is untouched by anything in item 111, and if those flips survive C then
  C ≈ A on them and the compiler story would have to explain that too. ▶ **If
  you can check whether the 28 survivors are gcc-vs-clang sensitive, that is the
  single most valuable thing in this task** — but a null there does not license
  the opposite conclusion either.
* ⛔ **It may NOT propose editing `harness/`** — hashed into all 33 PAT gate
  records — **or re-measuring anything.**
* ⛔ **It may NOT rewrite `RECAP_PHP.md` or `.memory-php/`.** Manager-only.

---

## §6 ⛔ Scope, brackets, traps

⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`patterns-php/`, `results/`, `results-php/`, `pilot/`.** ⭐ **This task measures
and argues; it edits nothing that is hashed.** New checkers go in
`.tasks-php/` (in **no digest**, free). Scratch under `.temp/php49/`.
⚠ **No `git add` / `git commit`.** Never touch `.web/` — a concurrent session
owns it.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`18/0`**, **first and
last**, both verified by the manager immediately before writing this.
⚠ **Nothing in your scope can move either.** ⓘ The php bracket covers **gate**
records too, so `18/1` mid-task from a gate-only file is legitimate — **but
nothing here should move even that.**

1. ⚠⚠⚠ **`grep -a` ALWAYS** (F35) — 41 corpus files exit 1 silently under plain
   `grep`, and a line-grep cannot find a prose phrase that **wraps**.
2. ⛔ **Never publish a percentage without WHICH INPUT, WHICH STATISTIC, WHICH
   OPT/MODE, and — the whole point of this task — WHICH BASELINE.**
3. ⚠ **A magnitude floor with every sign claim.** An outlier test in this
   programme once fired at `0.00 pp`.
4. ⚠ **Do not quote a W1 figure to more than 2 dp** — item 99: W1 moves
   ±14–28 Ir across regenerations while every A1 figure is bit-identical.
5. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match.
6. ⚠ **A truncated `ls`/`head` is not evidence of absence.**
7. ⚠ **`.temp/php49/`: keep the generator, delete the artefact.** If a blob has
   no script that rebuilds it, write one first.
8. ⓘ **NAME THE FILE EVERY FIELD CAME FROM** (F99, item 84).

---

## §7 Definition of done

1. **Deliverable 1** — the four figures re-derived, **the selection question
   answered with a full sweep**, and ⭐ **an explicit yes/no on whether the
   *"three other statistics"* were themselves computed against `c-gcc`.**
2. **Deliverable 2** — the corpus-wide sign-flip count, split into **published /
   publishable / already-labelled**, on both inputs.
3. **Deliverable 3** — a verdict on the attribution confound, with the cold-helper
   alternative explicitly addressed. ⭐ ***"Needs family C"* is a valued answer.**
4. **Deliverable 4** — the unlabelled census, the ruling, and a check if one is
   warranted (**with its negatives inside it**).
5. ⛔⛔ **A ONE-LINE VERDICT ON ITEM 111 ITSELF: UPHELD / UPHELD-NARROWED /
   REFUTED / UNDECIDABLE-WITHOUT-FAMILY-C.**
6. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** `_047` listed 14 and named
   where its depth ran out; that is the standard.
7. **Brackets `66/0` / `18/0`, unmoved, quoted first and last.**
8. ⛔ **If item 111 survives everything you throw at it, THAT IS A RESULT.** Do
   not manufacture a refutation — and do not manufacture a confirmation either,
   which is the likelier failure here because the manager framed it as
   consequential.
