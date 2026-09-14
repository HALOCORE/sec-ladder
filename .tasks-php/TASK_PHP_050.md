# TASK_PHP_050 — **SWEEP ITEM 112**, and review `F109` · `F107` · `F96` behind it

**Role:** research **reviewer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_050_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM.** Five consecutive rounds have
refuted manager or engineer claims: `_038` (three), `_043` (a headline and four
qualifiers), `_044` (three of `_043`'s), `_047` (**six verdicted, not one
survived as written**), `_049` (**the manager's own item-111 headline**).
`.memory-php/04-process.md` **law 12** is now the best-supported process law on
file. ▶ **Assume the same of everything below.**

⭐ **AND THE ROUND THAT MATTERS MOST IS §1, WHICH IS NOT A REVIEW AT ALL — IT IS
A SWEEP NOBODY HAS RUN, OVER A PUBLISHED STATISTIC FAMILY.**

---

## §0 STOP INSTRUCTION, AND THE READ LIST

**Four subjects: item 112 (the sweep), then F109, F107, F96.**
▶ **WORK IN ORDER. WHEN YOUR DEPTH RUNS OUT, STOP AND SAY WHERE.**
⭐ **A round that does §1 properly and names §§2–4 UNREVIEWED is worth more than
one that claims four.** `UNTESTED` and *"I could not tell"* are valued answers.

**Read**, in this order:

1. `RECAP_PHP.md` — **open item 112** (the brief), then **item 99** (the same
   phenomenon, now closed with a mechanism), then **F109 · F107 · F96**, then
   the **RULE-9 STATE block** (it names your scope).
2. `.tasks-php/TASK_PHP_048_REPORT.md` — **§4c** (the `argv[1]` control),
   **§3c** (the family-B point value that was never measurable), **§12 item 6**
   (the engineer's own statement that no sweep was done).
3. `patterns-php/ph55-opdata-stride/controls/argv_align.py` — ⭐ **the only
   control in the corpus that measures this. You are cloning its DESIGN.**
4. `.tasks-php/STATISTICS_001.md` — family B's definition and its known defects.
5. `.memory-php/03-numbers.md` — the five things every percentage owes.

---

## §1 ⭐⭐⭐ PRIORITY 1 — **THE ITEM 112 SWEEP: IS FAMILY B AN ALIGNMENT ARTEFACT ANYWHERE ELSE?**

**The problem, in one line:** `marginal_ir_per_call` is **bimodal**, the step on
`ph55`'s clang cells is **`7.0029 Ir/call`**, item 99 measured the same
phenomenon at **`±14–28 Ir`** on `ph53` — **and every `ph*` row derives its
family-B figures as a DIFFERENCE OF TWO CELLS FROM A SINGLE RECORD.**
⭐ **`ph55` caught it only because it happened to own a control measuring the
step. No other row has one.**

### 1.1 The sweep itself — cheap, read-only, and nobody has done it

▶ **For every `results-php/gate/*.json`, pull `marginal_ir_per_call`, and for
every family-B difference a row publishes or could publish, report the
magnitude against the alignment step.**

⭐ **The deliverable is a TABLE with a column nobody has computed: `|Δ| / step`.**
**Flag everything under ~3×.** ⚠ **State the step you used per row and how you
got it** — `ph55`'s `7.0029` is measured on that row; **do not assume it
transfers.** ⛔ **If the step is not measurable from committed records for a
row, say `UNTESTED` for that row rather than borrowing `ph55`'s.**

### 1.2 ⛔⛔ THE ROW THE MANAGER IS WORRIED ABOUT — **CHECKED, NOT ASSERTED, AND THE EVIDENCE CUTS BOTH WAYS**

**`patterns-php/ph64-callback-frees-cursor/NOTES.md:414-415`** publishes
`R1h − R1`:

| | `small` | `large` |
|---|---:|---:|
| **gcc** | **+15.98 Ir/call** (+0.037 %) | **+16.95 Ir/call** (+0.005 %) |
| **clang** | **+18.34 Ir/call** (+0.044 %) | **+18.33 Ir/call** (+0.006 %) |

⛔ **The same order of magnitude as the artefact.**
⭐ **BUT: four cells, two compilers, two inputs, agreeing within `2.4 Ir`, all
the same sign — which an alignment artefact would not produce.**
▶ **SETTLE IT.** ⚠ **Do not settle it by repeating the manager's reasoning; that
is an argument, and this programme has been wrong five rounds running on
arguments.** ⭐ **Find a measurement.** ⓘ The obvious one: **`argv_align.py`'s
design applied to `ph64`'s binaries** — same binaries, same input bytes, swept
`argv[1]` lengths. **If `ph64`'s figures are stable across the sweep, they are
real; if they move by 7–28 Ir, they are not.**

⚠ **`ph64` is the row that publishes the only B1 headline**, so this is the
highest-stakes cell in the sweep. ⓘ ✅ Note that B1 headline
(`safe_tuned` vs `unsafe`) is a **DIFFERENT QUANTITY** from the `R1h − R1` lines
above and is separately checked at **`0.0087 pp`** (F89's table). **Do not
conflate them** — and say which you are testing, every time.

### 1.3 ⭐⭐ CLONE THE **TWO-VERDICT** DESIGN, BECAUSE ONE VERDICT THROWS AWAY A REAL RESULT

`argv_align.py` reports **two** verdicts per pair — ***magnitude resolvable?***
and ***sign stable?*** — and `_048` §4c records why: one pair was `+216 k` or
`+76 k` Ir depending which side of the step it landed on, **both positive**, so
**the magnitude is not quotable and the sign is.** ⛔ **A single verdict would
have discarded a usable sign result to avoid quoting an unusable magnitude.**
▶ **Any checker you write reports both.**

### 1.4 THE RULING OWED

▶ **May a family-B figure be published at all without such a control?** ⭐ **Your
answer becomes a `PROTOCOL_PHP.md` §B rule if it is yes-with-conditions.**
⚠ **Consider the cheaper alternative before demanding a control per row: is
there a magnitude floor below which a family-B difference is simply not
publishable?** ⓘ That is how `.memory-php/03-numbers.md` already treats W1
(*"do not quote to more than 2 dp"*).

⛔⛔ **DO NOT RE-MEASURE ANY ROW AND DO NOT RE-GATE ANYTHING.** If the sweep
needs a build, **it is out of scope — say so and say what it would cost.**

---

## §2 ⚠⚠ PRIORITY 2 — **F109**, ROW 9, WHOSE MATERIAL IS BEING HELD OUT OF THE LAYER PENDING YOU

⭐ **Two things in F109 would change `.memory-php/` and are deliberately held
back** (the RULE-9 block says so). **Verdict each:**

1. ⭐⭐ **THE `inside_share` REFINEMENT.** F109 says: *a HIGH `inside_share` is
   **not** a certificate — what matters is whether **the DIFFERENCE** lands
   inside the symbol, not how much of the cell A1 sees.* **Evidence:** `ph55`'s
   C cells are **74–83 %**, `c/kernel.c` and `c/kernel_hardened.c` compile to a
   **byte-identical `kernel` symbol** under both compilers (`asm.py` `exact`),
   **one of the two binaries SEGVs**, and **A1 reports the fix at `0.000 %` on
   every C cell.** ▶ **Re-derive the byte-identity and the `0.000 %`**, and rule
   on whether the general statement is sound or over-read from one row.
   ⚠ **`STATISTICS_001.md` §4 may already say this** — the engineer thinks it
   does. **If so, the finding is a worked instance and not a new rule, and that
   is a narrowing worth making.**
2. **ITEM 99's CLOSURE.** The W1 instability is now attributed to
   **`len(argv[1])`**, a `7 Ir/call` step, *inferred from the step's size and
   shape and explicitly **NOT PROVEN***. ▶ **Is the attribution sound, or is it
   a plausible story fitted to a step?** ⭐ **`argv_align.py` sweeps eight
   lengths — does the step land where the stack-alignment story predicts?**

**And the rest of F109, at the bounded bar** — **(i)** re-derive the headline
NUMBER from a named artefact or write `UNTESTED`; **(ii)** one sentence on
scope; **(iii)** a verdict. ⭐ **Cheap and high-value:** the claim that
**`unsafe.rs` with the bug is *strictly worse than C*** on
`adversarial-nullcall.bin` — **UB taken by LLVM, no crash, a third wrong
value.** ▶ **Reproduce it; it is the row's most quotable sentence and it rests
on one observed run.**

---

## §3 PRIORITY 3 — **F107**, THE `_047` REVIEW ROUND

⭐ **A review round is itself a finding and gets the same treatment.** Its
load-bearing claim is **§1.7: option (b) does not exist**, on which the manager
has already acted (proceeding under (c)) and which is in the question put to the
user. ▶ **Re-derive the three grounds from `harness-php/gate.py`'s header and
`root.py` yourself.** ⛔ **If (b) does exist after all, say so loudly — the
manager has told the user it does not.**
⚠ Also check F107's *"three of four refutations came from a second input or a
second document"* generalisation: **is that a real pattern or a retrofit?**

---

## §4 PRIORITY 4 — **F96**, UNREVIEWED THROUGH THREE ROUNDS

`ph53`'s build record plus a four-prediction ledger. **Two rounds have looked for
a cheap second method and not found one; `_047` checked whether `ph52` supplies
it and it does not.** ▶ ⭐ **Check whether `ph55` does** — it is a third `T3`-ish
row with a witness and a dispatch. **If it does not, `UNREVIEWED` is the honest
answer for a third time and you should say so plainly rather than manufacture a
bar it can clear.**

---

## §5 ⛔ Scope, brackets, traps

⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`patterns-php/`, `results/`, `results-php/`, `pilot/`.** New checkers go in
`.tasks-php/` (**no digest, free**). Scratch under `.temp/php50/`.
⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY for writing.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`20/0`** (⭐ **20 now, not
18 — row 9 landed**), **first and last**, both verified by the manager
immediately before writing this. ⚠ **Nothing in your scope can move either.**

1. ⛔⛔⛔ **A LIVENESS CHECK MAY NEVER BE TRUNCATED** — item **113**, new. A
   `pgrep … | head` hid a live process and **raced a gate against itself**; two
   `check.py` runs shared a scratch dir and reported **different** failures.
   ▶ **`pgrep` feeding a decision gets NO `head`, NO `tail`, NO `| head -N`.**
   ⭐ Third instance of *a tool that silently reports less than it found*
   (`ls | head -30` read as a deletion; F35's `grep -a`) — **and the first that
   corrupted a run rather than a reading.**
2. ⚠⚠⚠ **`grep -a` ALWAYS** (F35). A line-grep cannot find a phrase that wraps.
3. ⛔ **Every percentage names WHICH INPUT · WHICH STATISTIC · WHICH OPT/MODE ·
   WHICH BASE · and if the base is a C cell, WHICH COMPILER** — five things
   (F108). ⛔ **Never quote an `O0` figure as a performance result.**
4. ⚠ **A magnitude floor with every sign claim.**
5. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match.
6. ⚠ **A truncated `ls`/`head` is not evidence of absence.**
7. ⛔ **Any checker you write carries its must-fire negatives INSIDE it**
   (§H), never in `.temp/`. **If it is a grep, ADJUDICATE hits by hand and
   ratchet — do not tune the regex.** ⓘ `contract_audit.py` and
   `cbaseline_check.py` are the two models; **both caught the manager.**
8. ⓘ **NAME THE FILE EVERY FIELD CAME FROM** (F99, item 84).
9. ⚠ **`.temp/php50/`: keep the generator, delete the artefact.**

---

## §6 Definition of done

1. ⭐⭐⭐ **THE ITEM 112 SWEEP TABLE**, with the `|Δ| / step` column, every row
   covered or explicitly `UNTESTED`, and **a verdict on `ph64`'s `R1h − R1`
   figures reached by MEASUREMENT and not by argument.**
2. **The §1.4 ruling**, with the cheaper magnitude-floor alternative considered.
3. **F109: a verdict on the `inside_share` refinement and on item 99's
   attribution**, plus the bounded bar on the rest — ⭐ **including reproducing
   *"unsafe Rust with the bug is strictly worse than C"*.**
4. **F107 and F96 as far as you got.**
5. ⛔⛔ **A COVERAGE TABLE: F96, F107, F109, each exactly one of UPHELD /
   UPHELD-NARROWED / REFUTED / UNREVIEWED** — plus **item 112: UPHELD /
   REFUTED / UNDECIDABLE-WITHOUT-A-BUILD.** ▶ **This decides what enters
   `.memory-php/`; an honest `UNREVIEWED` is as useful as a verdict.**
6. ⭐ **AN EXPLICIT LIST OF WHAT MUST NOT ENTER `.memory-php/`**, if you refuted
   anything the RULE-9 block lists as pending.
7. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.**
8. **Brackets `66/0` / `20/0`, unmoved, quoted first and last.**
9. ⛔ **If something survives everything you throw at it, THAT IS A RESULT.**
   `_049` upheld the effect while refuting the story about it. **Do not
   manufacture a refutation — and do not manufacture a confirmation either.**
