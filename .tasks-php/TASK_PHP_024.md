# TASK_PHP_024 — `ph07`'s refuted hashed `why`, and four defects in `extra_spans`

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_024_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative),
`.tasks-php/PROTOCOL_PHP.md`, **`.tasks-php/TASK_PHP_022_REPORT.md`** (M1, M2,
m3, m4, m6 and its post-notification §4 items — **that report is where every
item below comes from**), and `patterns-php/ph07-strcut-cursor/` in full.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **Do not edit `patterns-php/CATALOGUE.md`** — `TASK_PHP_023` owns it.
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ Scratch under `.temp/php24/`. **Never `/tmp`.** `.temp/php18/` and
`.temp/php22/` hold the rebuild's and the review's probes — **reuse them.**

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`6/0`**, first and last.
⚠ **§1 is a hashed-block edit, so a `ph07` re-gate is expected and budgeted**
(open item 11: six commands, ~28 min — ⚠ `TASK_PHP_018` needed **11** rounds and
every extra one caught a real defect, so budget more).

---

## §1 `ph07` publishes four figures its own rebuild refuted (open item 36)

1. ⚠⚠ **`spec.md`'s hashed `identity[0].why` cites 255 instructions and three
   hashes — `702235d5f057…`, `b20b2fd9aa42e532`, `b3ecc80e00209841` — all
   PRE-rebuild values.** The hash still matches because the text was never
   edited, **so no gate can see this**, and `NOTES.md` claims the addendum pass
   covered it, **which is a false disclosure.** Re-derive each figure from the
   current record and correct both.
2. ⚠⚠ **`c/kernel.h:20-25` names `d9dda48f8a7e` as R1h** while the file ships
   `cb3cca21b345` hunk (a) — **and `spec.md`'s own `forbidden[2]` calls
   `d9dda48f8a7e` a *different function*.** It is inside `source_sha256`.
3. **m3** — `NOTES.md`'s rule-6 fence disclosure **names 4 against 27 moved**.
4. **m4** — `NOTES.md` §10d quotes a **pre-rebuild** `negatives` log (and says so
   in its own last line, which is a disclosure that documents rather than fixes).
5. **`controls/bug49354.py`'s docstring says it *"shares no code with
   `fix_scope.py`"* and the table and clamps are BYTE-IDENTICAL COPIES.** ✅ The
   conclusion is safe — three independent checks agree — **but the disclosure is
   false and it is load-bearing evidence.** Fix the sentence, or share the code
   deliberately and say so.
6. **`controls/spellings.py` re-implements `measure.py`'s statistic** rather than
   importing it. ⚠ **Its first draft measured a different statistic and landed
   1 % off the record.** Import it, or state why the copy is necessary.
7. ⚠ **m6 — the gate hashes `controls/*.py` and never runs them.** **Do not fix
   this here** (it is a `harness/` property); report whether any php row's
   `controls/` would now fail if run.

⚠⚠ **THE RULE-6 QUESTION THIS ROW KEEPS RE-ASKING, and I want an answer, not a
fix:** the hashed `why` is the one place a stale figure is invisible to every
check. **Is there a cheap check that would have caught it** — e.g. a preflight
that greps the `why` for numerals and prints them beside the current record for
a human to compare? **Price it; do not build it** unless it is under ~30 lines
in `harness-php/` (a `harness/` edit is a 33-pattern re-gate).

## §2 Four defects in the `extra_spans` change (open item 37)

All four were found **after** the manager committed the change.

1. ⚠⚠ **`provenance.py:836-837`'s disclosure is measurably FALSE.** It says
   *"adding a span cannot make the number go up for free"*. Union overlap is
   `|hit|/|want|` over deduplicated sets, so **a span above the current fraction
   RAISES it** — measured on `ph07`'s own excerpts: primary alone **75 %
   (39/52)** → primary + the 100 % table span **77 % (44/57)**. ✅ The set
   semantics *do* defend against citing the same span twice (unchanged at 61 %).
   **Rewrite the disclosure to say what is true, and keep the measurement in
   the comment.**
2. ⚠⚠ **A `php_provenance: false` row short-circuits before any `extra_spans`
   validation**, so a wholly bogus extra span passes. **Fix, with a must-fire
   control.**
3. **`gate.py:300` cites `provenance.py:841-843`** for the dotted-row glob; the
   change moved it to **`:924`**, and `:841-843` is now the per-span overlap
   loop. **Citation rot introduced BY the change.**
4. **Claim (i)'s *"byte-identical"* holds for the DEFAULT invocation only** —
   under `--no-tarball`, `ph03` gains `for any of 1 span(s)`. **Either restore
   byte-identity or correct the claim.**

⚠ **`harness-php/` is not hashed into any PAT record, so §2 costs no PAT
re-gate** — but it moves the php preflight record. **Re-run `--all` and confirm
`ph03` and `ph00-smoke` are unchanged where they should be.**

## §3 What I am least sure of

1. ⚠⚠ **That §1.1 is worth a re-gate.** The figures are wrong, invisible to
   every check, and inside the block that defines the row's identity — but no
   number anyone quotes comes from there. **If you think the honest fix is a
   `NOTES.md` correction plus a standing note that the `why` is stale, argue
   it** — that is cheaper and I would take it.
2. ⚠ **That §2.2 is a real hole rather than a documented one.** A row with
   `php_provenance: false` is declaring it has no provenance; **maybe an unvalidated
   extra span on such a row is harmless.** Say which.
3. ⚠⚠ **That I should have committed the `extra_spans` change at all before it
   was reviewed.** I did, and four defects arrived afterwards (F48). **If the
   right lesson is "the manager should not commit a `harness-php/` change inside
   a row's commit", say so** — it is a process finding and it is mine.
