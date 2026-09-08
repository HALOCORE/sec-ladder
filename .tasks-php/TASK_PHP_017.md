# TASK_PHP_017 — adversarial review of `ph07`, and of the manager's four surveys

**Role:** research reviewer. **One agent, alone.** `PROTOCOL.md` rule 1: you are
**not** the engineer who built this row.
**Report:** `.tasks-php/TASK_PHP_017_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md` (the reviewer checklist), **`.memory-php/`** (the
authoritative layer — it supersedes any task report it contradicts),
`.tasks-php/PROTOCOL_PHP.md`, **`.tasks-php/TASK_PHP_016_REPORT.md`** (what you
are reviewing) and `patterns-php/ph07-strcut-cursor/` in full.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY for WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **`.web/` belongs to a CONCURRENT SESSION — never `git add -A`, never touch it.**
⚠ **No `git add` / `git commit`.** Read-only git is fine.
⚠ Scratch under `.temp/php17/`. **Never `/tmp`.** `.temp/php12–16/` hold the
earlier harnesses and `ph07`'s own probes — **reuse them.**

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`6/0`**, first and last.

⚠⚠ **TWO TRAPS THAT HAVE ALREADY BITTEN THIS ROW** — `PROTOCOL_PHP.md` §F 5–6:
`grep -a` **always** (plain `grep` is silently blind to 41 corpus files, and a
probe script does **not** reproduce it), and **ask about a FUNCTION, not about
text** — this row's history table was wrong in *both* directions and the first
version **passed a green gate**.

---

## §1 The row — `ph07` gated `PASS` and I do not want it confirmed, I want it attacked

`ph07-strcut-cursor`, `mbfl_strcut`'s `mblen_table` arm, `mbfilter.c:1179-1259`,
CRASH-124, tier `narrowed`. Contract `be5f5818ffa625c7`, R5 **21/0** (24/0 twin),
2 justified `loud`. **The engineer's report is unusually good and that is exactly
why it needs a hard review** — a strong report is the one whose claims get
repeated without checking.

**Attack these in order. They are ranked by what it costs us if they are wrong.**

1. ⚠⚠⚠ **THE HEADLINE: *"`R3`'s two walks are BYTE-FOR-BYTE `R2`'s, so no safe
   spelling removes that check."*** This is the row's result and it is a claim of
   **non-existence**, which is the hardest kind to make and the easiest to get
   wrong. **Try to refute it by construction**: write a safe-Rust variable-stride
   walk that beats R3, in contract. `iter()`-based? `chunks`? `get()` with a
   checked-add? A precomputed stride table indexed by a `u8` (the compiler may
   know `mbtab[b] <= 6`)? ⚠ **If you find one, the row's headline changes and
   that is a RESULT, not a failure — report it.** ⚠ **If you cannot, say what you
   tried**, because *"nobody found one"* and *"none exists"* are different
   claims and only the first is ours to make.
2. ⚠⚠ **THE PROOF. R5 says 21/0 — does its postcondition say anything?**
   `ph03`'s review killed 17 of 19 mutants; do the same here.
   ⚠ **Specifically attack `lemma_mbtab_matches`**: the report says the 256-entry
   table costs the proof one lemma with **no `assume` and no sixth trusted
   item**. **Verify that**, and check the `broadcast use` scoping change did not
   quietly weaken a spec while making it verify in 5 s.
3. ⚠⚠ **THE R1h FIDELITY QUESTION, WHICH THE ROW STATES AND DOES NOT SETTLE.**
   `cb3cca21b345` is a **caller-side** fix (`PHP_FUNCTION(mb_strcut)` in
   `ext/mbstring/mbstring.c`) and this row's kernel is `mbfl_strcut`. The row
   puts the guard in the `kernel()` wrapper, at upstream's own position, and
   `NOTES.md` §4d states the residual question. **Is that R1h faithful, or is it
   a hand-written control wearing a real sha?** ⚠ **This is not a `ph07` question
   only — `FIXSURVEY_001.md` says 8 rows have this shape and 3 of them are an
   executor defect fixed in the compiler.** **Whatever you decide here becomes
   the rule for those.**
4. ⚠⚠ **OPEN ITEM 24 — THE §A2a CLAUSE INVENTED TO MAKE THIS ROW GATEABLE.**
   `inputs/gen.py` refuses a window with `from + length > string->len` and
   asserts `cb3cca21b345-fires=0`, because hunk (b) **changes benign output on
   15 870 of 117 612 non-crashing calls** and stage 7h requires R1h ≡ R1 on every
   non-adversarial input. The proposed clause is in the report §4 item 3 and is
   **deliberately NOT landed** (rule 9). ⚠⚠ **Attack it as a RULE, not as a row
   fix**: does it license a corpus chosen to make a row pass? What stops the next
   engineer from narrowing the fixture until an inconvenient fix goes quiet?
   **If it needs a guard clause, write the guard clause.**
5. ⚠ **THE THREE BIG MEASURED CLAIMS. Re-derive, do not re-read.**
   (a) *"the over-read does not change the answer"* — 15 333 calls, **7** fillers,
   0 move; must-fire control moves 13 293. **Is 7 fillers enough, and are they
   adversarial or merely different?**
   (b) *"the 2010 walk rewrite alone still over-reads on 13 293 calls."*
   (c) *"the fix costs a constant, not a rate"* — +7.3 `Ir`/call gcc, +9.2 clang,
   marginal identical to four decimals.
6. ⚠ **THE ROW'S OWN CAVEATS — check they are bounded where they claim to be.**
   `memcpy` outside `kernel_exclusive_ir` (3 rungs call it, 3 do not; claimed
   **~2 %**), and the wall-clock spread (**5.4 %** between two rungs that are the
   same 255 instructions).

## §2 ⚠⚠ AND REVIEW THE MANAGER. Four surveys shipped unreviewed while you were building.

`PROTOCOL.md` rule 3 — **never clear your own design.** All four are mine, all
four are already cited by `PROTOCOL_PHP.md` or `.memory-php/`, and **none has
been through a reviewer.** ⚠ **Two of them have already been corrected once by
me, which is evidence they need a second pair of eyes, not evidence they are
now right.**

1. ⚠⚠ **`FIXSURVEY_001.md` + F38/F40 — the `fix_commit` column.** The load-bearing
   claim is *"the column names **a** fix, not necessarily the one that removes the
   5.0.0 defect"*, resting on **five** hand-checks of which **three** came out
   that way (`ph12`, `ph21`, `ph22`). **Check at least two of the three
   yourself**, and **check one I called `same`/correct** (`ph29`, `ph16`) — a
   survey that only verifies its exceptions measures its own priors
   (`.memory-php/01`). ⚠ **`ph22`'s is the one I most want re-run**: I first
   published *"PHP shipped it for 21 years"* and then withdrew it.
2. ⚠⚠ **`ADJUDICATION_002.md` — `ph92`/`ph93`, now IN the catalogue.** I withdrew
   two kills on the ground that their stated reasons are **cost** judgements
   under a heading that says `exact`. **Is that right, and are the two rows
   really distinct C mechanisms?** ⚠ **The bar is C-side only** — if you think
   they are exact duplicates, say so **with the C**, not with a cost or a
   ladder argument. ⚠ **Also check what I did NOT re-examine**: the remaining
   `C.1` rows, four of which say *"merged by the corpus itself"*. I verified
   three via `merged_members`; **the rest are unchecked.**
3. ⚠ **`UPSTREAM_001.md` — the four batch rows' fix windows** (`ph12` `ph16`
   `ph21` `ph29`). The next four tasks build on this. **Spot-check one window
   end-to-end.**
4. ⚠⚠ **F39 — the spellings claim, and it is the one that could embarrass us
   publicly.** I assert that both rows' ladders are **unlabelled `fixed-R4`
   bounds**, that `ph03`'s own hashed `why` already demands *"an in-contract
   spread beside its headline"*, and that the PAT record shows the missing
   number moves **against safe Rust** (3 of 4 searched rows; `p22` **510×**).
   **Verify the PAT figures at source** — `results/SYNTHESIS.md` §2 and
   `.memory/02-bench-rules.md` — **and tell me if I have overstated the
   direction.** ⚠ **`SYNTHESIS.md` wins over `RECAP_PAT.md` and over me**
   (`CLAUDE.md`).

## §3 What I am least sure of

1. ⚠⚠ **That `ph07`'s R1h is admissible at all** (§1.3). If a caller-side guard
   transplanted into the kernel is *not* the real fix, then **this row's R1h and
   8 others need a different rule**, and I would rather find that now than after
   four more rows.
2. ⚠⚠ **That I was right to land the §F 5–6 protocol edits on my own evidence
   while leaving the engineer's §A2a clause unlanded.** That split is a judgement
   about whose unreviewed work counts, and **it may just be self-serving.** Say
   so if it is.
3. ⚠ **That two rows is enough to publish the `ph03`-vs-`ph07` contrast** (F41):
   *rate vs constant*, *dead-and-incomplete vs complete*, *tuning recovers most
   vs tuning recovers none of the pattern's own loop*. **It is n = 2.** If the
   contrast is being overdrawn, **say what a third row would have to look like to
   settle it** — that is more useful to me than a caution.

---

**Running count: launched from 74.** `TASK_PHP_016` built the row, **found and
corrected its own defect after a green gate**, refuted four things in the state
layer including two of mine, and answered all three of the calls it was asked
about. ⚠ **It also did what this task asks of you** — it disbelieved a manager
premise and checked it. **Do that to the four surveys in §2.**
