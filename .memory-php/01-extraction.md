# `.memory-php/01-extraction.md` — the three frames, and what cost means

> ⚠ **`.memory-php/` is the AUTHORITATIVE layer for the PHP programme, and it
> SUPERSEDES any task report it contradicts** (`.tasks/PROTOCOL.md` rule 9).
> Only findings that have survived a full engineer→reviewer cycle are here.
>
> ⚠⚠ **SCOPE: this carries ONLY what is php-specific.** The PAT `.memory/`
> 00–06 applies unchanged — same harness, same bench rules, same measurement
> discipline, same Verus notes. **Do not restate any of it here; two copies of
> one rule is how both go stale.**
>
> The narrative, the open items and findings **F1–F112** live in `RECAP_PHP.md`
> (⚠ this said *F1–F41* for **forty-nine** findings, then *F1–F90* for **eleven** more — `PROTOCOL.md` rule 13, **and it has now rotted THREE TIMES.** ✅ **`.tasks-php/boxcheck.py` CHECKS THIS LINE AGAINST the actual highest finding as of 2026-09-13, so it is the last time.**
> **Count it yourself: `grep -c '^### F' RECAP_PHP.md`.**)
> ⭐ **And the statistic decision — which column every row publishes in — is
> `.tasks-php/STATISTICS_001.md`, committed. It was in gitignored `.temp/`.**

---


- ⚠⚠⚠ **For a given row the DEFECT site, the GUARD site and the FAULTING site
  can be three different places, and the corpus's fields point at different
  ones.** `provenance.c_file`/`c_lines` name the **defect** site; the other two
  go in the row's notes. (F1: `c_file_line` names the faulting frame —
  CRASH-002's line is `array.c:1062`, its mechanism is `zend_hash.h:88`.)
- ⚠⚠ **Extraction cost must be priced at the DEFECT site too.** Four rows were
  killed by pricing the machinery of an **adjacent** frame: CRASH-136 (the
  recursion the defect completes before), CRASH-157 (the caller's backtrace),
  CRASH-033 and CRASH-053 (the guard site). **Two of them are five lines.** (F8.)
- **Tier is a COST STATEMENT, never a filter.** `verbatim` / `narrowed` /
  `modelled`. ⚠ *"The surrounding machinery is the program"* is a **tier
  assignment wearing a kill's clothes** — `PLAN_PHP.md` §3 criterion 3 is about
  the **kernel shape** (flat blob in, `u64` out), not about how much C you carry.
- ⚠⚠ **A KILL WRITTEN AS A SET HIDES ITS MEMBERS**, and this has fired **three
  times**. Reversing a rejection that covers N rows must re-adjudicate all N,
  **and the only reliable way to enumerate them is against `index.csv`, not
  against the prose.** ⚠ A coverage checker must count **admissions only** —
  the first one counted a mention in the *kill table* as coverage. (F22, F27.)
- ⚠ **An audit that only re-examines the decisions it already doubts measures
  its own priors.** The manager's kill audit never re-opened its own *upheld*
  list; five of those reverse at source. (F21.)
