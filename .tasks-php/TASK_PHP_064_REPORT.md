# TASK_PHP_064 — REPORT. **15 files promoted, 13 findings discharged, 8 defects found in the brief and in the probes themselves**

**Role:** research engineer, one agent. **Repo at start:** `f4bda715121a`
(2026-09-17). **No `git add`/`git commit` was run.** Working surface:
`.tasks-php/` only.

> ⛔⛔ **TWO THINGS IN THIS REPORT ARE STALE BY DESIGN — IT IS A HISTORICAL
> RECORD AND ITS TEXT IS LEFT AS WRITTEN** (`CLAUDE.md`'s own precedent for the
> `RECAP.md` → `RECAP_PAT.md` rename: citations survive in reports, and only
> **runnable** ones are repaired).
>
> 1. ⚠ **`refetch_upstream002.sh` (9 mentions) IS NOW
>    `probes/refetch_f50_census.sh`.** The manager renamed it the same day: the
>    promoted name asserted that the script was written for
>    `.tasks-php/UPSTREAM_002.md`, a document created nine days later and **while
>    this task was running**. ⭐ The engineer's error was well-founded — the
>    script carries its *own* `UPSTREAM_002` label at line ~66, a scratch-era
>    survey name — so **`UPSTREAM_002` genuinely names two different things.**
>    The new name is after the FINDING it regenerates. The three promoted probes
>    that cited the old name were repaired.
> 2. ⚠ **§7's line numbers are stale.** They were measured before `F150`–`F152`
>    were written above them. ✅ **All 16 repoints LANDED**, by exact string and
>    scoped to the owning finding — a whole-file replace came back with six
>    counts high, because `F150`/`F151` quote those same paths as their SUBJECT.
>    ▶ **Do not re-run §7 against line numbers.**
>
> ⭐ **§4.2's findings against the brief are the part to read**, and four of the
> five changed something published. See `F150`'s corrected severity table.

---

## §0 ⭐ THE FIVE-LINE VERSION

1. **14 files were named; 13 were promoted and one was ALREADY PROMOTED under a
   different name** (`F102`'s `asanfill.c` ≡ `.tasks-php/asan_fill_byte.c`,
   since 2026-09-13). That is brief error **B1**.
2. **The sibling rule caught two more files** — `enclosing_fn.py`, which
   produces **F69's other headline number**, and `fn_body.py`, without which
   F50's named regenerator cannot run. Both promoted. §3.
3. ⛔⛔ **TWO PROBES ARRIVED BROKEN AND NEITHER WAS A MISSING CACHE.**
   `ph29_predict.py` crashed because **its prediction came true**;
   `item83_sim.py` exited 1 because **`ph53` was re-searched under it**.
   ▶ **A MOVED SUBJECT is a second failure mode and item 149's rule does not
   cover it.** §4.1.
4. ⛔ **THREE PUBLISHED FIGURES HAVE MOVED** and one **protocol reassurance is
   now false**: `F73`'s `0 of 6 PHP` → **1 of 14**; `F85`'s `29 of 38` → **111
   of 141** on a 2.3× corpus (the **ratio** survives, the count does not);
   `spread_stat`'s *"not one row flips sign"* → **ph45 and ph66 do**. §5.
5. `python3 .tasks-php/checkers.py` ends **`CHECKERS PASS`** with 13 new
   registry entries. Verbatim tail in §8.

---

## §1 PER FILE — promoted / partially / refused

⭐ **The worklist was taken from the tool, not from the brief**
(`python3 .tasks-php/probes/scratchdeps.py`). Its `RESTS` block gives 17
citations over 14 files and 13 findings, and I re-derived the (finding, line)
map with `scratchdeps.published_finding_deps()` rather than reading the brief's
table. The tool and the brief agree on the **count**; they disagree on **one
row** and on **one file's status** — see §2.

| # | source | landed as | state | evidence it still works |
|---|---|---|---|---|
| 1 | `.temp/mgr170/callee_share.py` | `probes/callee_share.py` | ✅ PROMOTED | `--selftest` rc 0, 4 negatives; 758 comparisons over 14 rows |
| 1b | `.temp/mgr172/STATISTIC-DECISION-DRAFT.md` | `.tasks-php/STATISTIC_DECISION_001.md` | ✅ PROMOTED (evidence doc) | 8 probe citations repointed; **all 8 now resolve** |
| 1c | `.temp/mgr170/spread_stat.py` | `probes/spread_stat.py` | ✅ PROMOTED | `--selftest` rc 0, 5 negatives; Q3 reproduces F74's headline |
| 2 | `.temp/mgr173/ph64_draws.py` | `probes/ph64_draws.py` | ✅ PROMOTED **+ guarded** | `--selftest` rc 0, 5 negatives; NOT-RUN path driven and verified |
| 3 | `.temp/mgr169/charlit_reach.py` | `probes/charlit_reach.py` | ✅ PROMOTED | `--selftest` rc 0, 6 negatives; **headline moved, §5.1** |
| 4 | `.temp/mgr168/item48_decide.py` | `probes/item48_decide.py` | ✅ PROMOTED **+ guarded** | `--selftest` rc 0, 9 arms; 27/30 `files==fixes` unchanged |
| 4b | `.temp/mgr168/enclosing_fn.py` | `probes/enclosing_fn.py` | ✅ PROMOTED — **SIBLING RULE**, §3 | `--selftest` rc 0; **`24 of 30` re-derived to the digit** |
| 5 | `.temp/mgr166/asan_reach.c` | `probes/asan_reach.c` | ✅ PROMOTED | rebuilt + re-run: **the published bytes×ASan×canary table reproduces to the row** |
| 5b | `.temp/mgr165/REFETCH.sh` | `probes/refetch_upstream002.sh` | ✅ PROMOTED **+ 3 forced fixes** | **re-run end to end, rc 0**, `.temp/mgr177/refetch-rerun.log` |
| 5c | `.temp/php17/r1h/fn.py` | `probes/fn_body.py` | ✅ PROMOTED — **SIBLING RULE**, §3 | re-derives `ph07`'s R1h pin `26e2099e33433c74` |
| 6 | `.temp/mgr169/ph29_predict.py` | `probes/ph29_predict.py` | ✅ PROMOTED **+ REBUILT**, §4.1 | `--selftest` rc 0, 5 negatives; **all six predictions verified** |
| 7 | `.temp/php43/item83_sim.py` | `probes/item83_sim.py` | ✅ PROMOTED **+ REPAIRED**, §4.1 | `--selftest` rc 0, 6 arms + 2 declared VACUOUS |
| 8 | `.temp/php43/samefunc_hole.py` | `probes/samefunc_hole.py` | ✅ PROMOTED | rc 0, 4 cases; **now a regression test**, §5.4 |
| 9 | `.temp/php19/entcount.py` | `probes/entcount.py` | ⚠ **PARTIALLY PROMOTED** | F53's two named commits re-derive exactly; **the nine-commit input set has no committed generator**, §6.1 |
| 10 | `.temp/mgr165/count_ent.py` | `probes/count_ent.py` | ✅ PROMOTED | `63/65 · 22/23 · 66/67 · 410/411` re-derived to the digit |
| 11 | `.temp/mgr176/asanfill.c` | — | ⛔ **NOT PROMOTED — ALREADY WAS**, §2 B1 | `.tasks-php/asan_fill_byte.c` is the same program + a fuller header |

**Nothing was refused.**

---

## §2 ⭐⭐ EVERY PLACE THE BRIEF IS WRONG

### B1 ⛔⛔ Item 11 is already done. `.temp/mgr176/asanfill.c` was promoted four days ago, as `.tasks-php/asan_fill_byte.c`.

The brief's table row 11 says *"`.temp/mgr176/asanfill.c` | `F102` | 14 lines,
and the **measured result changes the row**"*. **The file has been committed
since 2026-09-13.** `.tasks-php/asan_fill_byte.c` is the same program —
`malloc(64)`, print 8 heap bytes, `volatile unsigned char s[64]` in a block,
print 8 stack bytes, `free`, `return 0` — under a fuller header that adds the
`ASAN_OPTIONS=malloc_fill_byte=0` third arm and a correction of its own first
draft. `.tasks-php/TASK_PHP_045.md:90` already cites it as
*"⭐ `.tasks-php/asan_fill_byte.c`, **COMMITTED**"*.

▶ **F102's debt is a STALE POINTER, not a missing file.** The remedy is a
one-line repoint (§7, row 5476), not a promotion. ⚠ The census could not tell:
`scratchdeps.tracked_basenames` resolves by **basename**, and `asanfill.c` ≠
`asan_fill_byte.c`, so a renamed promotion is invisible to it. **That is a
general hole in the `PROMOTED` verdict, not a one-off.**

### B2 ⚠ §1.2 row 4 says *"`F70` (section), **`F69` rests on it**"*. Half right, and the wrong half is the interesting one.

`F69` does rest on `item48_decide.py` — but it rests on **`enclosing_fn.py`
equally**, and the brief quotes both numbers (*"`29 of 30` at `file:line`,
`24 of 30` by enclosing function"*) while naming only one file. The `24 of 30`
is `enclosing_fn.py`'s and **nothing else in the tree re-derives it**. See §3.

Also: `ADJUDICATION` has a `("F69", ".temp/php27/streamsfuncs.c")` row ruled
`NOTDEP`. A reader checking *"F69"* against the tool finds a **NOTDEP** row and
no `RESTS` row, which reads as *F69 has no debt*. It has one; it is booked
against F70's citation line because that is where the file is named.

### B3 ⚠ §0.3.3 says item 149's message is `NOT RUN -- NOT A PASS`. Neither worked example prints that string.

`.tasks-php/width.py` prints `⛔⛔ NOT RUN -- NO VERDICT WAS REACHED, AND THIS
IS NOT A PASS`; `probes/inclusive_ir.py::report_not_run` prints `⛔⛔ NOT RUN --
NO VERDICT WAS REACHED. THIS IS NOT A PASS.` **`width.py`'s own arm `X3d(b)`
tests for the two substrings `"NOT RUN"` and `"NOT A PASS"` separately**, which
is why both pass. I wrote the new guards to carry **both substrings
contiguously** (`NOT RUN -- NOT A PASS`) *and* the `NO VERDICT WAS REACHED`
sentence, so they satisfy `X3d(b)`'s predicate and the brief's literal reading
at once. ⓘ Minor, but a brief that quotes a string as if it were in the code is
how a reader adds a fourth spelling.

### B4 ⚠ §1.2 row 2 says `ph64_draws.py` has *"`--selftest` PASS with 5 negatives"*. True today **and only because gitignored scratch survived.**

`N3`, `N4` and `N5` all read `.temp/php-root/.temp/build/` and
`.temp/mgr173/cg/`. On this box those exist (80 profiles), so the brief's claim
is true as measured — but it is a claim about **scratch**, and the whole point of
the task is that scratch is scheduled for deletion. Before my guard, the same
command on a clean checkout printed `FAIL N3` and exited **1**, i.e. *"F89 is
refuted"*. §4.2.

### B5 ⚠ §1.2 row 5 calls `REFETCH.sh` *"the named regenerator for all of `F50`'s evidence"*. It could not regenerate anything from a clean checkout, for two reasons the brief does not mention.

(a) It opened `FN=../php17/r1h/fn.py`, a **gitignored** path. (b) It did
`cd "$(dirname "$0")"`, so promoted as-is it would have written ~25 downloaded
`.c`/`.patch` files **into the committed tree** — `CLAUDE.md` Don't #1 inverted.
Both fixed; see §4.3. ⛔ **And the name `refetch.sh` was already taken by a
different, already-promoted generator** — promoting it under the obvious name
would have overwritten F34/F35/F36's evidence.

### B6 ⚠ §1.2 row 7 quotes *"all six published A1 percentages re-derive to the digit"* as `item83_sim.py`'s live output. Its `--selftest` **exited 1** when I ran it.

The harness's load-bearing arm (`N1`) is green and the arithmetic does
re-derive; but two of the four arms had gone stale under `TASK_PHP_042`'s
re-search of `ph53`. §4.1. ⓘ Also, the probe checks **five verdict fields plus
`a1_spread_pp`**; nothing in it enumerates *"six A1 percentages"* by name, so
that phrase is `_043`'s, not the file's.

### B7 ⚠ §0.2's *"the `RESTS` block is your worklist"* is right, and §1.2's table silently drops `F74`'s second file and `F85`'s ordering.

The table's row 1 covers `callee_share.py` + the draft + `spread_stat.py` in
prose (§1.1) rather than as numbered rows, so a reader working the table top-down
does **three** files at step 1 and may count 11 rows as 11 files. The tool says
**14 files / 17 citations / 13 findings** and that is what I worked.

### B8 ⓘ §3's warning about `N20` is correct and it never fired.

No new `.temp/` path was written into a finding section (I may not edit
`RECAP_PHP.md` at all). `scratchdeps.py --selftest` rc 0 throughout.

---

## §3 ⭐⭐⭐ THE SIBLING RULE — WOULD IT HAVE CAUGHT ANYTHING BEYOND `null_control.py`? **YES. TWO FILES, AND ONE OF THEM CARRIES HALF A PUBLISHED HEADLINE.**

### 3.1 `enclosing_fn.py` — F69's *other* number

`RECAP_PHP.md:1622` (F69):

> *"at `file:line` **29 of 30** rows have every id at a distinct line, and by
> **enclosing function 24 of 30**."*

The first number is `item48_decide.py`'s. **The second is
`.temp/mgr168/enclosing_fn.py`'s**, and nothing else in the tree produces it.
Re-run on promotion: `fns==ids **24 of 30** · fns<ids 6 · unresolved 0`. Exact.

⛔⛔ **The law-11 census could not have found it, for two independent reasons,
and both are worth recording as holes:**

1. **F69's section names no file at all.** `scratchdeps.py` keys on
   *citations*; a published number whose probe is never named is invisible to
   it **by construction**. `F132`'s *"the census prints a CANDIDATE SET"* — this
   is the set's complement.
2. **The one place the siblings ARE named uses a brace expansion.** Retired item
   48 (`RECAP_PHP.md:9616`) reads
   `` `.temp/mgr168/{item48_decide,enclosing_fn,spread_axis,sha_norm}.py` ``.
   **Measured, not argued:**
   `scratchdeps.PATH_RE.findall(line)` → `['.temp/mgr168/']`, a bare directory
   with no evidence suffix, which the census then drops.
   ▶ **Four probe citations register as ZERO.**

### 3.2 `fn_body.py` — a second-order law-11 case

`refetch_upstream002.sh` is *named by F50 as the regenerator of all its
evidence*, and it calls `../php17/r1h/fn.py` once per tag. Promoting the
regenerator and leaving that in deletable scratch produces **a committed
generator that cannot generate** — `PROMOTE_001`'s defect one level further
out. Promoted as `probes/fn_body.py` (renamed: `fn.py` is far too generic for a
flat directory that has already had one basename collision this task).
⭐ Bonus corroboration: `fn_body.py mbstring-php-5.2.17.c
'PHP_FUNCTION(mb_strcut)'` → sha256 **`26e2099e33433c74`**, which is exactly the
body hash `PROTOCOL_PHP.md` §C pins as `ph07`'s R1h.

### 3.3 Siblings I found and did **not** promote — stated, not rounded off

* `.temp/mgr168/spread_axis.py` — produces F69's third set of numbers
  (*"21 of 31 temporal (68 %) · 6 of 29 type (21 %) · 3 of 42 spatial (7 %)"*),
  quoted in F69, F70 **and** `PROTOCOL_PHP.md` §C. Named only inside the brace
  expansion above. ▶ **Owed. Same argument as `enclosing_fn.py`; I stopped at
  two because the brief's order puts F50 and F44 ahead of a third F69 sibling,
  and promoting a file I had not run would have been a copy.**
* `.temp/mgr168/sha_norm.py` — fourth member of the same brace expansion; I did
  not establish that any published number is its output.
* `.temp/mgr170/NOTES.md`, `.temp/mgr172/NOTES.md`, `.temp/mgr173/NOTES.md`,
  `.temp/mgr176/NOTES.md` — the census rules these `AMBIGUOUS` (basename too
  generic). `NULLCTL_001.md` is the precedent for promoting one;
  `STATISTIC_DECISION_001.md` is this task's. The other three are **unadjudicated
  law-11 candidates**.

---

## §4 ⛔⛔ THE TWO PROBES THAT ARRIVED BROKEN — AND WHY ITEM 149 DOES NOT COVER THEM

### 4.1 **A MOVED SUBJECT is a second failure mode**

`PROMOTE_001` found two probes that crashed **without their cache**. Item 149
settled what such a check returns. **Neither of this batch's two broken probes
had a cache problem.**

**`ph29_predict.py` crashed because its prediction came TRUE.**

```
AssertionError: required[0].c no longer opens with 'emalloc(to_read + 1)'
                -- spec.md moved
```

`apply_edit`'s assert exists to refuse a stale simulation. Item 51's edit landed
at `TASK_PHP_033`, so `spec.md` now opens with the **backticked** span and the
guard fires. ▶ **A prediction tool whose prediction came true crashes on its own
success, and no amount of cache-guarding catches that.**

✅ **Rebuilt as a verifier.** It detects which image of `spec.md` is on disk. On
the POST-IMAGE it checks F72's six published numbers against the **committed**
gate record. Measured 2026-09-17:

```
spellings 12 · pairs 36 · present 22 · pins_nothing 0 · absent 2 · forbidden_hits 0
✅ ALL 6 PUBLISHED PREDICTIONS LAND EXACTLY.
```

▶ **F72's prediction was falsifiable and was not falsified — and that is now
checkable by anyone, rather than a sentence in a handoff.** Five must-fire
negatives added (`N1` perturbation, `N2` the prediction itself, `N3` `landed()`
both ways off a planted pre-image, `N4` drift vs the record, `N5` the original
assert is **kept, not weakened**).

**`item83_sim.py` exited 1 because `ph53` was re-searched under it**
(`TASK_PHP_042`, *"ph53's both endpoints move"*). Two arms, two different
failures:

* ⛔ **`N4` reported a move that had not happened.** It compared the reading-(a)
  exclusion set as a **LIST**. After the rebuild each bitmask variant matches
  `required[4]` **twice** (`wrote[i]` *and* `[bool; MAXD]`), so the list held six
  entries with duplicates and the arm printed *"R4 exclusion set moved"* about a
  set that had not moved. **A membership question asked of a multiset.**
  Repaired to a `set`.
* ⛔ **`N2`/`N3` went VACUOUS.** Both perturb the **R4** endpoint, which is now
  degenerate as committed (`r4_beaters: []`). `N2` (*"excluding all R4
  challengers degenerates it"*) is then trivially satisfied by a state that was
  already degenerate; `N3` (*"excluding a dearer variant leaves it
  non-degenerate"*) asserts a state that no longer exists, and fired.
  ▶ **An arm that cannot discriminate is NOT PASSING, and an arm whose subject
  moved is not FAILING.** They now print `VACUOUS -- NOT A PASS`; the
  discriminating pair is rebuilt on the **live R3 side** (`N2r`/`N3r`, six
  beaters) with the dearest variant **derived** rather than named — which is the
  literal defect `N4` carried; and **`N5` measures the vacuity's cause** so it is
  a reading of the row rather than an assertion about it.

⚠ **F100's arithmetic survives its own row's rebuild**: `N1` reproduces all five
committed verdict fields and the bare run reproduces
`a1_spread_pp {R3: 39.899657, R4: 45.313019}`.

> ▶ **THE RULE I WOULD WRITE IF IT WERE MINE TO WRITE:** *a one-shot probe cited
> by a finding acquires a maintenance cost the moment it is committed, and
> nothing in this tree prices that.* Item 149 covers **a missing cache**. It does
> not cover **a moved subject**, which this batch hit twice, from opposite
> directions (a prediction that came true; a row that was re-searched).

### 4.2 Item 149 applied where it *does* fit — four probes guarded

| probe | what was absent | before | now |
|---|---|---|---|
| `ph64_draws.py` | valgrind, build trees, `inputs/*.bin`, 80 profiles | `FAIL N3`, **rc 1** — reads as *"F89 is refuted"*; and with trees present but cache cleaned a **bare run silently launched 80 valgrind invocations** | reports, **rc 0**, `NOT RUN -- NOT A PASS`; regeneration opt-in behind `--collect` |
| `item48_decide.py` | corpus `index.csv`, `fixsurvey.json` | `FileNotFoundError` | reports, **rc 0**; `--selftest` **splits** — six PURE string arms still run and report, three index-reading arms say they did not |
| `enclosing_fn.py` | pinned tarball, index, survey | `return 2` under *"CANNOT SELFTEST"* — **neither the filed pass nor an adjudicated red** | reports, **rc 0**, `NOT RUN -- NOT A PASS` |
| `entcount.py`, `count_ent.py` | the `html.c` **argument** | `FileNotFoundError` / `IndexError` | usage message, **rc 2** — ⚠ a missing *argument* is a usage error, **not** item 149's case, and I did not conflate them |

The `ph64_draws.py` NOT-RUN path was **driven**, not asserted: rebinding `CGDIR`
and `VALGRIND` to nonexistent paths in-process prints the banner and returns
`RC = 0`.

### 4.3 `refetch_upstream002.sh` — three forced changes, then re-run end to end

1. `cd "$(dirname "$0")"` → an explicit `.temp/mgr165/` workdir. **Promoted
   as-is it would have dropped ~25 re-derivable downloads into a committed
   tree.**
2. `FN=../php17/r1h/fn.py` → `probes/fn_body.py` (§3.2).
3. `count_ent.py` → resolved from `probes/`.
   (Plus: the `list()` helper now prints an API-error object instead of raising
   on a rate-limited response.)

✅ **Re-run end to end, rc 0** (`.temp/mgr177/refetch-rerun.log`): 19 tags'
`mb_strcut` body hashes, `c2471b495009` found as the 2009 removal and
`cb3cca21b345` as the 2005 fix, and the entity-table chain **5.0.0 `4 short` →
5.0.4 `1 short` → 5.0.5 `0` → 5.1.0 `0` → 5.2.0 `0`**.

---

## §5 ⛔ WHAT MOVED — THREE PUBLISHED FIGURES AND ONE PROTOCOL REASSURANCE

### 5.1 `F73`'s headline is no longer `0 of 6 PHP`, and the new hit is **not a character literal**

```
PAT  patterns/      33 rows  ->  0 affected, 0 forbidden   UNCHANGED
PHP  patterns-php/  14 rows  ->  1 affected, 0 forbidden
```

The hit is `ph52-concat-copy-uninit` `required[0].rust`, spelling
`` `ensures` ``, which `check.exec_code(…, "rust")` blanks to seven spaces.

* ✅ **The dangerous half is unchanged**: `forbidden` — a ban that cannot fire,
  and the half that FAILS the gate — is still **0**.
* ✅ **Nothing is hidden**: `ph52`'s gate record already carries
  `required_pins_nothing: 25` including this entry. It is visible only to a
  reader who already distrusts the field.
* ⭐ **The mechanism is a Verus clause keyword, not a C character literal**, so
  `PROTOCOL_PHP.md` §H1's *title* does not reach it while the probe's actual
  test (*any span the blanker erases*) does.

⚠⚠ **`PROTOCOL_PHP.md` §H1 asserted `✅ LATENT, NOT LIVE: 0 affected spellings
across 33 PAT rows and 6 PHP rows`, and cited the gitignored probe.** Two
consequences:

1. **That citation was never in the law-11 census at all.**
   `scratchdeps.scan_set()` returns `RECAP_PHP.md` + `.memory-php/*.md` and
   **nothing else** — not `PROTOCOL_PHP.md`, not `CATALOGUE.md`, not
   `PLAN_PHP.md`, not any `spec.md`/`NOTES.md`. `F151`'s class
   (`ph53/verus.rs`) at a new site.
2. ⛔ **I EDITED `PROTOCOL_PHP.md` §H1.** It is in my working surface and in no
   digest (its own §B1a measures that). I struck the stale sentence, repointed
   the citation at `probes/charlit_reach.py`, and added a dated, marked
   **UNREVIEWED engineer correction** with the re-measured table. **I did not
   change the RULE** — whether the heading should be re-spelled *"a spelling the
   blanker erases"* is a rule change and is routed to the manager.
   ▶ **If you disagree, it is one contiguous block and deleting it restores the
   file.**

### 5.2 `F85`'s count has moved; its **ratio** has not

`callee_share.py --flips` over the corpus gated today:

| | F85 (2026-09-12, 6 rows) | today (2026-09-17, 14 rows) |
|---|---|---|
| comparisons | 366 | **758** |
| sign flips | 38 | **141** |
| cross-language | **29 (76.3 %)** | **111 (78.7 %)** |

⭐ **The claim survives a 2.3× corpus; the number does not.** Quote `29 of 38`
with its date and its row set — **never off a fresh run of the file**.

⚠ And the script's own closing `RULE` line (*"where `|Δinside_share| ≤ 0.02` the
two families agree on DIRECTION"*) is refuted by its own output four lines
above: `flips with Δshare <= 0.02` has gone **0 → 6 → 13**. F74 records the
middle correction in place (`RECAP_PHP.md:7463`); the third step is new.

### 5.3 `spread_stat.py`'s Q1 has reversed — and **nothing published is refuted**

`.temp/mgr170/NOTES.md` §1c concluded ***"Not one row flips sign across all five
statistics"*** and §1h re-asserted it (*"remains true"*). Today the probe prints
**`⚠⚠⚠ SIGN FLIPS on: ph45, ph66`**, so item 52 is a **direction** question on
this corpus, not only a precision one.

✅ **Checked before claiming it**: I grepped `RECAP_PHP.md` and `.memory-php/`
for *"precision question"*, *"DIRECTION one"*, *"no row changes sign"* — **zero
hits**. The sentence never left gitignored scratch. So there is **no finding to
correct**; what is refuted is the assumption that a probe's printed conclusion is
a fact rather than a reading of one day's corpus. (`ph45`'s reversal is
independently on file as **F87**; `ph66` is simply newer than the note.)

✅ **What DOES reproduce unchanged** is F74's actual published observation — Q3
still resolves `ph03 → A1`, `ph16 → A1`, `ph29 → A1`, **`ph64 → B1`**.

### 5.4 `samefunc_hole.py`'s meaning has changed, and that is the result

The `same_function` guard was **repaired**. All four cases now come out as
wanted and the script prints `✅ no hole found by these four cases`. ▶ **It is no
longer a hole-finder; it is a regression test for the repair**, and `CASE 4` is
what stops the repair over-correcting into demoting honest hunks. **A
counterexample whose target has been fixed is the one people delete, and the one
that has to stay.**

### 5.5 ⭐ WHERE I ALMOST SHIPPED A FALSE CLAIM, AND HOW IT WAS CAUGHT

`samefunc_hole.py` ends with *"⭐ REACH ON THE REAL CORPUS … counted below over
every screened record's matched hunks"* — **and then returns.** Nothing is
counted. My first draft of its header concluded that F95's *"✅ Live reach on the
real corpus is `0`"* therefore had *"no producer in this tree at all"*.

**That is FALSE, and I found it by grepping the code instead of trusting my own
header.** `.tasks-php/preimage_screen.py --selftest` carries
**`N13 MUST-NOT-FIRE: the zero-context branch must reach NOTHING in the real
corpus`**, which walks every screened record's `same_function_evidence` and
fails the checker if any hits it. Measured 2026-09-17:
`records hitting the zero-context branch: 0 []`, `--selftest` rc 0 — and that
checker is **committed and in the routine sweep**.

▶ **So the defect is a dangling promise in one file, not an unsourced published
claim.** Both the corrected header and the printed line now say so, and say that
the first draft said otherwise. This is §0.3.1's refusal discipline applied to
**my own** prose.

---

## §6 ANYTHING I HAD TO LEAVE — PLAINLY

### 6.1 ⛔ **`F53`'s nine-commit corpus has no committed generator.** (Partial promotion.)

F53 says *"`entcount.py` run at **nine** PHP-5.0 commits touching `html.c`
between 5.0.3 and 5.0.4"* and **names only two of them**.
`refetch_upstream002.sh` fetches *tags*, not intermediate commits.

✅ **F53's load-bearing half re-derives exactly.** Fetched `b9ff04703f16` fresh
and ran the promoted probe (`.temp/mgr177/f53-rederivation.log`):

```
ent_uni_338_402    declares 65   has 63   SHORT
ent_uni_spacing    declares 23   has 23   ok
ent_uni_8592_9002  declares 411  has 411  ok
```

**Two of the three are already `ok` two months before `56adfe1f3cf1`** — exactly
F53's claim, by the compiler rather than by a regex.

⛔ **The other seven commits are a judgement F53's author made and did not
record.** The header carries the exact API + `curl` recipe. **Writing it as a
script is owed and I deliberately did not do it**, because that would be a new
generator authored in a promotion pass, encoding *my* choice of "which nine".

### 6.2 Three probes have **no must-fire negatives at all**, and one of them is the file the programme cites three times as a cautionary tale

`count_ent.py`, `entcount.py`, `fn_body.py` are all filed
`negatives="none", kind="tool"`. That is honest and **it is not a pass.**
`count_ent.py` is the loudest: its v1 shipped a false claim that the manager
quoted twice, `RECAP_PHP.md` names it three times as the precedent for *a broken
computation rendering as a positive claim*, and it still has no arm. **I did not
add arms in the promoting pass**, because adding them hides which behaviour was
inherited — but the debt is real and it is recorded in each file's header and in
its registry `why`.

### 6.3 What is NOT re-derivable on a clean checkout, per file

* `ph64_draws.py` — pinned valgrind, `.temp/php-root/` build trees,
  `patterns-php/*/inputs/*.bin`, 80 callgrind profiles. **All gitignored with
  generators; `CLAUDE.md` Don't #1 being obeyed.** Guarded.
* `item48_decide.py`, `enclosing_fn.py` — the corpus `index.csv` and the pinned
  tarball live in **another repo** and are not re-derivable from here at all.
  Guarded.
* `refetch_upstream002.sh`, and F53's recipe — **network**.
* `asan_reach.c` — a clang with ASan. ⚠ I re-ran it at **`-O1` only**; F50
  claims identity at `-O0`/`-O1`/`-O3` and **I did not re-run that three-way
  check.** Stated in the file.

### 6.4 Claims in the brief I could not verify

* *"Of the 13 findings, only `F89` and `F95` have ever been reviewed."* I did
  not audit all 13 headings. I did observe that **`F100` is `REVIEWED AND
  NARROWED`** (its section heading says so, and its R4 half is **withdrawn**),
  which makes the count at least three. ▶ **Possible brief error; I am not
  asserting it, because I checked one heading and not thirteen.**
* *"For 11 of 13 there is no second method anywhere in the tree."* Unverified as
  stated, and §5.5 shows one counterexample to the *shape* of that claim: F95's
  `0` does have a second producer.

### 6.5 Artefacts

`.temp/mgr177/` holds two evidence logs (`refetch-rerun.log`,
`f53-rederivation.log`); the compiled `asan_reach` binary and the downloaded
`html-*.c` blobs were deleted (`CLAUDE.md` Don't #1). `.temp/mgr165/` now holds
the regenerator's own cache again, exactly as it did before — that directory is
gitignored and skipping cached files is what makes a re-run cheap.

---

## §7 ⛔ CITATION REPOINTS FOR `RECAP_PHP.md` — I MAY NOT EDIT IT; HERE ARE THE EXACT LINES

Line numbers are against `RECAP_PHP.md` at commit `f4bda71`. **Each `old` is
unique on its line.** ⭐ The five marked **AUTO** would flip `LIVE → PROMOTED` in
`scratchdeps.py` on commit anyway (bare-name citations whose basename becomes
tracked) — **repoint them regardless**, because the text still points a reader
at a gitignored directory.

| # | line | finding | old (exact substring) | new (exact substring) | AUTO? |
|---|---|---|---|---|---|
| 1 | **1611** | F70 | `` `item48_decide.py` `` | `` `.tasks-php/probes/item48_decide.py` `` | AUTO |
| 2 | **1851** | F72 | `` `ph29_predict.py` `` | `` `.tasks-php/probes/ph29_predict.py` `` | AUTO |
| 3 | **1897** | F72 | `` `ph29_predict.py` `` | `` `.tasks-php/probes/ph29_predict.py` `` | AUTO |
| 4 | **1915** | F73 | `` `.temp/mgr169/charlit_reach.py` `` | `` `.tasks-php/probes/charlit_reach.py` `` | — |
| 5 | **5476** | F102 | `` `.temp/mgr176/asanfill.c` `` | `` `.tasks-php/asan_fill_byte.c` `` | — |
| 6 | **5648** | F100 | `` `.temp/php43/item83_sim.py` `` | `` `.tasks-php/probes/item83_sim.py` `` | — |
| 7 | **6020** | F95 | `` `.temp/php43/samefunc_hole.py` `` | `` `.tasks-php/probes/samefunc_hole.py` `` | — |
| 8 | **6570** | F90 | `` `.temp/mgr173/ph64_draws.py` `` | `` `.tasks-php/probes/ph64_draws.py` `` | — |
| 9 | **6636** | F89 | `` `.temp/mgr173/ph64_draws.py` `` | `` `.tasks-php/probes/ph64_draws.py` `` | — |
| 10 | **6986** | F85 | `` `.temp/mgr172/STATISTIC-DECISION-DRAFT.md` `` | `` `.tasks-php/STATISTIC_DECISION_001.md` `` | — |
| 11 | **6986** | F85 | `` `callee_share.py` `` | `` `.tasks-php/probes/callee_share.py` `` | AUTO |
| 12 | **7396** | F74 | see the block below — **do not compress it** | see the block below | AUTO |
| 13 | **8191** | F53 | `` `entcount.py` `` | `` `.tasks-php/probes/entcount.py` `` | AUTO |
| 14 | **8335** | F50 | `` a `REFETCH.sh` that `` | `` a `.tasks-php/probes/refetch_upstream002.sh` that `` | — |
| 15 | **8396** | F50 | `` `.temp/mgr166/asan_reach.c` `` | `` `.tasks-php/probes/asan_reach.c` `` | — |
| 16 | **8924** | F44 | `` `.temp/mgr165/count_ent.py` `` | `` `.tasks-php/probes/count_ent.py` `` | — |

⛔⛔ **ROW 12 IN FULL, AND DO NOT USE A BRACE EXPANSION.** A brace expansion is
exactly the spelling that made four `.temp/mgr168/` citations invisible to the
census (§3.1). Write the three paths out.

* **old:** `` `spread_stat.py` · `callee_share.py` · `null_control.py` ``
* **new:** `` `.tasks-php/probes/spread_stat.py` · `.tasks-php/probes/callee_share.py` · `.tasks-php/probes/null_control.py` ``

⭐ **Two more repoints that are NOT law-11 citations but are now stale pointers:**

* `RECAP_PHP.md:9606` (open item 35) — `` `.temp/mgr168/enclosing_fn.py` `` →
  `` `.tasks-php/probes/enclosing_fn.py` ``.
* `RECAP_PHP.md:9616` (retired item 48) — the brace expansion
  `` `.temp/mgr168/{item48_decide,enclosing_fn,spread_axis,sha_norm}.py` ``.
  Two of the four are now promoted. ⚠ **Whatever it becomes, it must not remain
  a brace expansion** — see §3.1.

⚠ **`.tasks-php/` is in no digest, so none of this costs a re-gate** — and
neither did any of the promotions.

---

## §8 ✅ `python3 .tasks-php/checkers.py` — FINAL LINES, VERBATIM

**13 new registry entries** were filed by hand, each with a `why`:
`probes/{callee_share,spread_stat,ph64_draws,charlit_reach,item48_decide,enclosing_fn,ph29_predict,item83_sim,samefunc_hole,entcount,count_ent,fn_body}.py`
and `probes/refetch_upstream002.sh`.
ⓘ `probes/asan_reach.c` and `.tasks-php/STATISTIC_DECISION_001.md` get **no**
entry: `checkers.py::_disk()` files `.py` and `.sh` only, and a `.c` probe or an
evidence document is evidence, not a checker. That matches the existing
`probes/segaddr.c` / `asan_fill_byte.c` / `NULLCTL_001.md` precedent.

⚠ **No `"<n> arms"` claim was filed in any new `why`**, on purpose: several of
these probes print the arm name and the verdict on **different lines**, which
`checkers.py::_arms_in` reads as **zero arms** (open item 131's dialect blind
spot). Filing a count would have made `N12` fail for a reason that is not about
the count.

⚠ **`citecheck.py` is unchanged at rc 1** — the single standing
`TASK_PHP_048.md:337` false positive, exactly as filed (`expect=1`). **No new
`rot` was introduced.** Its law-11 warning block still reports 31 citations over
21 findings, and **will keep doing so until the §7 repoints land**: the census
reads `git ls-files`, so a promotion becomes visible when the manager commits
(`F147`), and the *citations themselves* still name `.temp/`.

**Registry line, verbatim** (`REGISTRY` carries no count literal; this is
derived on every run):

```
REGISTRY: 56 filed, 56 on disk (no literal -- the registry IS the ratchet)
  checkers 36 · of which FLAG-GATED negatives 17 -- these are the ones a bare sweep does not check
```

**Final lines, verbatim** (`python3 .tasks-php/checkers.py`, 2026-09-17,
**exit code 0**):

```
ARM-COUNT CLAIMS -- `why` prose vs what the checker PRINTS
  ok cbaseline_check.py       claims  12  observed  12
  ok contract_audit.py        claims   8  observed   8
  ok probes/flip_exact.py     claims   6  observed   6
  ok probes/identity_null.py  claims   9  observed   9
  ok probes/item139_sibling_census.py claims  10  observed  10
  ok task_cost.py             claims  19  observed  19

CHECKERS PASS
```

The thirteen new entries, as the sweep ran them:

```
  ok probes/callee_share.py   --selftest   rc=0 (expect 0)
  ok probes/charlit_reach.py  --selftest   rc=0 (expect 0)
  ok probes/enclosing_fn.py   --selftest   rc=0 (expect 0)
  ok probes/item48_decide.py  --selftest   rc=0 (expect 0)
  ok probes/item83_sim.py     --selftest   rc=0 (expect 0)
  ok probes/ph29_predict.py   --selftest   rc=0 (expect 0)
  ok probes/samefunc_hole.py               rc=0 (expect 0)
  ok probes/spread_stat.py    --selftest   rc=0 (expect 0)
```

ⓘ `probes/ph64_draws.py`, `probes/entcount.py`, `probes/count_ent.py`,
`probes/fn_body.py` and `probes/refetch_upstream002.sh` are filed `kind="tool"`
and are **deliberately not swept** — the first needs gitignored profiles and
build trees (a checker that reddens when scratch is cleaned is reporting on the
scratch), the next three need a command-line argument, and the last needs the
network. Their standing states were measured by hand on 2026-09-17 and are
recorded in §1 and in each file's header.

**Nothing was left red.**

---

## §9 FILES ADDED / CHANGED (for the manager's commit)

```
A  .tasks-php/STATISTIC_DECISION_001.md          (evidence doc, F85)
A  .tasks-php/probes/asan_reach.c                (F50)
A  .tasks-php/probes/callee_share.py             (F85, F74)
A  .tasks-php/probes/charlit_reach.py            (F73)
A  .tasks-php/probes/count_ent.py                (F44)
A  .tasks-php/probes/enclosing_fn.py             (F69 -- SIBLING RULE)
A  .tasks-php/probes/entcount.py                 (F53)
A  .tasks-php/probes/fn_body.py                  (F50 -- SIBLING RULE)
A  .tasks-php/probes/item48_decide.py            (F70 / F69)
A  .tasks-php/probes/item83_sim.py               (F100)
A  .tasks-php/probes/ph29_predict.py             (F72)
A  .tasks-php/probes/ph64_draws.py               (F89, F90)
A  .tasks-php/probes/refetch_upstream002.sh      (F50, F44, F45)
A  .tasks-php/probes/samefunc_hole.py            (F95)
A  .tasks-php/probes/spread_stat.py              (F74)
A  .tasks-php/TASK_PHP_064_REPORT.md             (this file)
M  .tasks-php/checkers.py                        (13 entries, one comment block)
M  .tasks-php/PROTOCOL_PHP.md                    (§H1 only -- see §5.1, revertible)
```

⛔ **No `git add`, `git commit`, `git stash` or any history-mutating git command
was run.** ⛔ Nothing under `RECAP_PHP.md`, `.memory-php/`, `harness/`,
`common/`, `patterns/`, `results/`, `results-php/`, `pilot/`, `common-php/` or
`patterns-php/*/` was touched — verified by `git status --porcelain`, which lists
exactly the eighteen paths above and nothing else.
