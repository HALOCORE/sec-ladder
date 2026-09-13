# `.memory-php/00-corpus.md` — the citation base, and what is authoritative

> ⚠ **`.memory-php/` is the AUTHORITATIVE layer for the PHP programme, and it
> SUPERSEDES any task report it contradicts** (`.tasks/PROTOCOL.md` rule 9).
> Only findings that have survived a full engineer→reviewer cycle are here.
>
> ⚠⚠ **SCOPE: this carries ONLY what is php-specific.** The PAT `.memory/`
> 00–06 applies unchanged — same harness, same bench rules, same measurement
> discipline, same Verus notes. **Do not restate any of it here; two copies of
> one rule is how both go stale.**
>
> The narrative, the open items and findings **F1–F101** live in `RECAP_PHP.md`
> (⚠ this said *F1–F41* for **forty-nine** findings, then *F1–F90* for **eleven** more — `PROTOCOL.md` rule 13, **and it has now rotted THREE TIMES.** ✅ **`.tasks-php/boxcheck.py` CHECKS THIS LINE AGAINST the actual highest finding as of 2026-09-13, so it is the last time.**
> **Count it yourself: `grep -c '^### F' RECAP_PHP.md`.**)
> ⭐ **And the statistic decision — which column every row publishes in — is
> `.tasks-php/STATISTICS_001.md`, committed. It was in gitignored `.temp/`.**

---


- **PHP 5.0.0, the pinned tarball**, sha256 `5783e0c0…d6919`, 5 595 997 B,
  3 815 entries. Read recipe and per-file manifest: `patterns-php/SOURCES.md`.
  ⚠ **Every extracted tree on this box is patched to some degree — 8 of 12 match
  the tarball, 4 do not.** Citations resolve against the **tarball**, never a
  build tree.
- ⚠⚠ **`index.csv`'s `c_file_line` is AUTHORITATIVE. The reproducer `.php`
  header comment is NOT** — six of them describe **4.0.2**, and `CRASH-017.php`
  self-labels as such. Following one **inverts the verdict**. (F2, found
  independently by two miners on two axes.)
- ⚠ **Three corpus `root_cause_id` strings are known wrong**, not merely
  imprecise: CRASH-053 (*"unchecked `make_real_object`"* — the check IS there),
  CRASH-033, and CRASH-071. **The label is a hint; the line is the claim.**
- **The corpus is 166 rows.** `patterns-php/CATALOGUE.md` catalogues **102**
  (`TASK_PHP_019`+`_020` landed by `_023`; ⚠ **count it, do not trust this line**
  — `python3 .tasks-php/quota.py`).
  ⚠ **It uses THREE id prefixes — `CRASH-`, `V5C-` and `LOGIC-`** — and all
  three are in `index.csv` with ordinary `c_file_line` and `fix_commit` cells.
  ⚠⚠ **THAT LAST CLAUSE IS UNDER CHALLENGE AND UNREVIEWED — see `RECAP_PHP.md`
  F51 / open item 39.** Measured: `V5C-015`, `V5C-116` and `V5C-173` are cited
  by `ph22`, `ph03` and `ph11` and are in **neither** the `input_id` **nor** the
  `v5c_id` column — they live only in a surviving row's **`merged_members`**,
  which is a namespace this entry does not mention. **Nothing here is retracted
  until a reviewer has looked**; the pointer is so the next agent does not
  re-derive it from scratch. `.tasks-php/coverage.py` resolves all three.
  ⚠ `LOGIC-` ids also appear under `rust-eval/`; **that is not their home and
  the rows are C-cited.** Checked deliberately, because sourcing a row from the
  port would breach `SOURCES.md`. (F40.)
- ⚠⚠⚠ **ALWAYS `grep -a` ON THE CORPUS. `grep` IN A `Bash` CALL IS BLIND TO
  41 OF THE 1 170 `.c`/`.h` FILES, SILENTLY.** It is a shell function
  dispatching to `ugrep`; on a file holding **one** non-UTF-8 byte it exits **1
  with no stdout and no stderr** — indistinguishable from *"not present"*.
  **`ext/standard/string.c` is such a file** (`Stig S\xe6ther Bakken`, line 16)
  and **13 catalogued rows cite one**. ✅ `grep -a`, `/usr/bin/grep` (GNU 3.11)
  and `rg`/the `Grep` tool are all unaffected.
  ⚠⚠ **AND A PROBE SCRIPT DOES NOT REPRODUCE IT** — shell functions are not
  exported to `sh`, so `sh probe.sh` runs GNU grep and succeeds where the same
  line pasted into a `Bash` call fails. (F35.)
  ⭐ **The row-level version of the same trap**: `TASK_PHP_016` built a history
  table by grepping for a *guard* and got it wrong **in both directions** — one
  spelling reported absence where the guard had been renamed, one unanchored
  pattern reported presence where the hit was in a different function, **and
  neither error is visible from its own output.** **Ask a question about a
  FUNCTION, not about text.**
- ⚠ **The ASan census cannot speak to the spatial axis.** (Evidence:
  `.tasks-php/ADJUDICATION_001.md` §8b. ⚠ The raw ASan log tree it was derived
  from is **gone** per rule 1 and nothing rebuilds it; §8b names the path, and
  carries the counts and a pasted sample fault chain, so it is what survives.)
  3 199 reports, and **zero of the 2 520 spatial ones fault in `Zend/` or
  `ext/standard/`** — 2 156 are inside `libmysqlclient.so.14`'s XML charset
  parser, a different shared object. Every spatial `hotness` field is
  **reasoned**, and the census is not evidence for it. (F9.)

---

## Landed 2026-09-13 from `TASK_PHP_043` — the `fix_commit` column, and how an exclusion is held

- ⛔⛔ **THE CORPUS'S `fix_commit` COLUMN NAMES *A* FIX AND IS SOMETIMES THE WRONG
  COMMIT ENTIRELY.** `ph53` / CRASH-158 is the measured instance: the column gives
  **`be8daf1f47fa` (2008-03-12)**, and the real R1h is
  **`d09cdd9f71f34deab4b99f4e63523fb94164a724` (Dmitry Stogov, 2005-06-08,
  *"Fixed valgrind errors"*, first shipped php-5.0.5)** — 1 file, 1 hunk, 2
  insertions / 1 deletion, and it **`patch -p1`es onto the pristine tarball at
  ZERO FUZZ, exit 0** (offset −14). ▶ **Bisect the one-release bracket; do not
  take the column on faith.** (F94, `PROTOCOL_PHP.md` §F5(iii).)

- ⚠⚠ **AND THE EXCLUSION OF THE WRONG COMMIT RESTS ON **ONE** ROUTE, NOT TWO.**
  F94 published *"REFUTED TWICE INDEPENDENTLY"* — the pre-image screen's
  `NOT-THE-REPAIR` **and** the 5.0.x tag walk. ⛔ **The screen route is GONE: the
  `same_function` soundness repair correctly demoted that record to
  `INAPPLICABLE-SAME-FILE`, which the screen prints as *"NOT exclusions … says
  nothing about these"*.** ✅ **The exclusion STANDS on the tag walk alone** — the
  cited `erealloc` line survives php-5.0.1–5.0.4 and is **gone at php-5.0.5**,
  **2 years 9 months before** the commit. ⭐ **The lesson is about the bookkeeping,
  not the verdict: a repair to a screen can silently withdraw a route a finding
  is still citing, and nothing re-checks the finding.** ▶ **When a screen's
  labelling changes, grep the findings that cite its verdicts.** (Items 85, 87.)

- ✅ **THE TWO ROUTES ARE NOT THE SAME EVIDENCE TWICE, AND THE SCREEN *DOES*
  DISAMBIGUATE MULTIPLE CITED SITES** — by 5.0.0 line number plus full text,
  *"better than the tag walk does"*. ⚠⚠ **The tag walk alone cannot**: a naive
  count read 2 occurrences of `erealloc(ce->interfaces` at php-5.0.4 and 1 at
  php-5.0.5 and looked self-contradictory until the **two distinct sites** were
  separated — the survivor is the inheritance-merge line at **`:1944`**, not the
  cited one. ▶ **A count-based tag walk needs site disambiguation or it is not a
  walk, it is a tally.**
