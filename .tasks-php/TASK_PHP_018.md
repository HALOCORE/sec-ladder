# TASK_PHP_018 — land `TASK_PHP_017` into `ph07`: a new R1h, an unrestricted corpus, and the spellings control

**Role:** research **engineer**. **One agent, alone.** `PROTOCOL.md` rule 1 — you
are not the reviewer, and you are not the agent who built this row.
**Report:** `.tasks-php/TASK_PHP_018_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative — it supersedes any
task report it contradicts), **`.memory/02-bench-rules.md`** (the `fixed-R4
bound` rule; §2 below turns on it), `.tasks-php/PROTOCOL_PHP.md`,
**`.tasks-php/UPSTREAM_002.md`** (manager, unreviewed — §1 is built on it),
**`.tasks-php/TASK_PHP_017_REPORT.md`** §1, §3 and §4, and
`patterns-php/ph07-strcut-cursor/` in full.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠⚠ **A SECOND AGENT IS RUNNING AND READS `patterns-php/CATALOGUE.md`,
`.tasks-php/PROTOCOL_PHP.md`, `PLAN_PHP.md` and `.tasks-php/ADJUDICATION_00*.md`.
DO NOT EDIT ANY OF THOSE** (`PROTOCOL.md` rule 11). §4 says what to do instead.
⚠ **`.web/` belongs to a CONCURRENT SESSION — never `git add -A`, never touch it.**
⚠ **No `git add` / `git commit`.** Read-only git is fine.
⚠ Scratch under `.temp/php18/`. **Never `/tmp`.** `.temp/php17/` holds the
reviewer's `v1.rs`, `REBUILD.sh`, `fn.py` and `REFETCH.sh`, and `.temp/mgr165/`
holds mine — **reuse them, do not re-derive them.**

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`6/0`**, **first and
last**. ⚠ The php number is expected to stay 6; if a record goes STALE mid-task
that is the re-gate you are about to do, not a defect.

⚠⚠ **THE TWO TRAPS THAT HAVE ALREADY BITTEN THIS ROW** — `PROTOCOL_PHP.md` §F
5–6: **`grep -a` always**, and **ask about a FUNCTION, not about text.** ⚠ The
second one bit *me* while writing `UPSTREAM_002`: a grep for hunk (b)'s own
source line reports it **absent from php-5.3.0**, where it is present and
respelled `(unsigned int)from`. **Use `.temp/php17/r1h/fn.py`.**

---

## §1 ⚠⚠⚠ THE BIG ONE — `ph07`'s R1h changes, and this is a REBUILD of the row

**Read `UPSTREAM_002.md` before anything else in this section.** Measured, at
source, on nineteen tags: `cb3cca21b345`'s **hunk (b)** —

```c
if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) { len = Z_STRLEN_PP(arg1) - from; }
```

— was **removed by upstream** in `c2471b495009` (Moriyoshi Koizumi, 2009-09-23)
as **bug #49354, with a regression test**, and is absent from `php-5.2.12`
onward and from `php-5.3.2` onward. Set beside the row's own `fix_scope.py`:
hunk (b) **removes none** of the reads past `val[slen]`, and **changes the
answer on 15 870 of 117 612 benign calls**.

⚠⚠⚠ **So `check.py` stage 7h was RIGHT.** The row reads its refusal as a gate
limitation and works around it by keeping the fix's guards dead in
`inputs/gen.py`. **The gate detected the same defect PHP's maintainers detected
four years later.**

**→ THE DECISION (mine, and it is the manager's to make): `ph07`'s R1h becomes
the guard configuration upstream CONVERGED on — hunk (a) alone — pinned as
`php-5.2.12 … php-5.2.17`, `PHP_FUNCTION(mb_strcut)` body sha256
`26e2099e33433c74`.** Do it in this order and **stop at 1c if it fails**:

**1a. ⚠ FIRST, ANSWER THE QUESTION THAT CAN INVALIDATE THE WHOLE PLAN.**
F41 says R2–R5 *are ports of R1h*. **Do the Rust rungs implement hunk (b)'s
clamp?** If they do, then on the newly-admitted ~13.5 % of the benign domain
they will disagree with R1 — **and that disagreement is CORRECT, because hunk
(b) is a behaviour bug.** They must lose it too, and `verus.rs`'s spec and
`model.py` must be checked for the same clamp. **Report what you found before
you change anything.** ⚠ If removing it breaks the R5 proof, **that is a
finding, not a blocker** — report it and say what the obligation became.

**1b. `c/kernel_hardened.c` = hunk (a) alone**, at upstream's own position,
honouring `TASK_PHP_017`'s **R1h TRANSPLANT RULE** (report §3, the boxed rule —
the repair frame must be one the kernel *already runs on every call*; for this
row it is, `mbstring.c:1787-1805`). Keep the two-hunk variant **in `controls/`**
with the 13.5 % rate, and add `c2471b495009.patch` beside
`cb3cca21b345.patch` — the removal is now part of the row's evidence.

**1c. `inputs/gen.py`: DROP the hunk-(b) restriction, keep the hunk-(a) one.**
`gen.py`'s docstring currently requires *"NO window on which **either**
`cb3cca21b345` guard fires"*. Hunk (a) (`from > string->len → RETURN_FALSE`) is
the **adversarial** case and must stay dead on the benign corpus — that is what
"benign" means here, not a restriction. Hunk (b)'s constraint goes. ⚠ **Assert
the new domain explicitly, and assert that windows with
`from + length > slen` are now PRESENT** — a fixture that silently keeps the old
shape is the failure mode this whole task exists to remove. **Re-run
`_check_span()` and every other `_check_*` in that file; if one of them was
quietly relying on the restriction, say which.**

**1d. `spec.md`.** `idiom.required[4]` pins R1h as *"the real upstream fix
`cb3cca21b345` and NOTHING ELSE"*. That is **inside the hashed block**, so this
is a re-gate — expected and budgeted. Re-word it to pin the **configuration**:
tag range, function, body sha256, and the two commits (added 2005, half removed
2009). ⚠ **`why` must state the choice and the alternative, not just the
result** — `PROTOCOL.md` rule 9's spirit: the row publishes what it decided
*and* what it decided against.

**1e. Re-gate and re-measure.** `harness-php/gate.py` — the six-command cycle
(open item 11, ~28 min). **Every number on this row moves.** Report the new
ladder in full, and **say which of F41's three measured claims survive**:
(a) *the over-read does not change the answer*, (b) *the 2010 walk rewrite alone
still over-reads*, (c) *the fix costs a CONSTANT, not a rate*. ⭐ **(c) is now
measured on ONE comparison instead of two and should get cleaner, not just
smaller — say whether it did.**

## §2 ⚠⚠ THE SPELLINGS CONTROL — open item 27, and the rule is NOT "re-ship R3"

`TASK_PHP_017` B1 built a safe, in-contract R3 that beats the shipped one:
`+13.50 % → +2.62 %` against R4, zero `unsafe`, identical checksums on all seven
inputs, in contract by `harness/check.py::spelling_matches` itself. The source
is `.temp/php17/spell/v1.rs` and the harness is `REBUILD.sh` beside it.

⚠⚠⚠ **DO NOT REPLACE `safe_tuned.rs`.** `.memory/02-bench-rules.md` forbids
re-shipping a rung because a cheaper in-contract spelling was found. **Publish
BOTH, LABELLED**: the shipped cell is a **`fixed-R4 bound`**, and beside it the
**cheapest-found in-contract** counterpart. That is what `ph03`'s own hashed
`why` has demanded all along, and `ph07` becomes the **first php row to
discharge it**.

1. **Port `controls/spellings.py`** from the four PAT rows that have one —
   `patterns/{p13-strncpy-trunc,p34-refcount-stack,p42-goto-cleanup,p49-interned-pool}/controls/spellings.py`.
   ⚠ **Read all four before writing yours**; they are the only worked examples.
2. ⚠⚠ **RE-DERIVE `v1`'s NUMBER. Do not carry `+2.62 %` over.** It was measured
   on the **restricted** corpus §1c deletes. A figure measured against a corpus
   that no longer exists is exactly the defect this programme keeps finding.
3. ⚠ **Search the R4 side too, at least once.** `SYNTHESIS.md:271-277` — the
   headline moves toward whichever side you did not search, and on 19 searched
   PAT rows **eleven found no cheaper R4**. ⭐ **A clean negative here is a
   result**: *"the R4 endpoint is degenerate on this row"* is publishable and is
   the honest counterpart to B1. Say what you tried, and how long you looked.
4. Report **both** ladders, both labelled, and say plainly which number the
   crash course may quote.

## §3 ⚠ THE PROVENANCE GAP — open item 25

`TASK_PHP_017` M1: `provenance.c_lines` pins `mbfilter.c:1179-1259` — **one
span** — while the row lifts **three**: that span, `mbfilter_utf8.c:39-56` (the
table, disclosed as `divergences[6]`), and **`mbstring.c:1774-1812` (the
wrapper), disclosed nowhere as a lifted span** — and `mbstring.c` is **exactly
the frame R1h occupies**, which §1 makes more load-bearing, not less. The 75 %
(39/52) overlap report is therefore computed against a span containing neither
the fix nor its frame.

⚠ **This is a `harness-php/` change, so it costs NO PAT re-gate** — but it moves
the php preflight record. **Make `provenance` accept a LIST of spans**, keep
single-span rows working unchanged (`ph03` and `ph00` must not move), and
re-run. ⚠ **If the schema change turns out to cost more than one row's worth of
churn, STOP, report the price, and pin the third span in `spec.md` prose
instead** — a disclosed span beats a schema you had to fight.

## §4 What to PROPOSE and NOT land

⚠ **Rule 9, and rule 11 — the files below are open in another agent.** Write
these into your report as exact proposed text; **the manager lands them.**

1. **`PROTOCOL_PHP.md` §C — the second admissible R1h form.** §C says R1h is
   *the real upstream `fix_commit`*. §1 ships a **tagged upstream
   configuration**, pinned by `(tag range, function, body sha256)`. Propose the
   wording. ⚠⚠ **And attack it first**: it is a protocol extension invented to
   make one row work, which is the exact shape `TASK_PHP_017` refused for the
   §A2a clause. **`UPSTREAM_002.md` §4 claims the difference is that §A2a
   narrowed the evidence to fit the artefact while this widens the artefact to
   fit the evidence. Say whether you believe that**, and say so plainly if you
   do not — I would rather find out here than after four more rows.
2. **`PROTOCOL_PHP.md` §A2a — the clause `ph07` proposed.** If §1 lands,
   **item 24 closes by DELETION**: no clause is needed. Confirm that in one
   sentence, or explain what still needs one.
3. **`.memory-php/02-ladder.md`** — the R1h transplant rule, the ph07 ladder,
   and F31's stage-7h limitation, which §1 **partly retracts**: stage 7h was
   right here. Propose the corrected text.

## §5 What I am least sure of

1. ⚠⚠⚠ **That §1 is worth a rebuild of row 2 at all.** The cheap alternative is
   to land `TASK_PHP_017`'s guard clause and keep the R1h the row has.
   **If, once you are inside it, the rebuild looks like it buys less than it
   costs, SAY SO AND STOP AT §1a.** §2 and §3 are independent of it and are
   worth doing either way. ⚠ **A refusal here is a result and will be published
   as one** — `CLAUDE.md` rule 6's shape, one level up.
2. ⚠⚠ **That a subset of a commit may be called R1h.** My argument is that
   `php-5.2.12`'s configuration is a stronger citation than a commit because it
   is what upstream *kept*. **It is still a subset of a labelled security fix,
   presented as that fix.** If you think the row must instead ship the whole
   2005 commit and disclose the 13.5 %, argue it.
3. ⚠ **That `r202895` in the removal commit's message is `cb3cca21b345`.** I did
   **not** verify it and `UPSTREAM_002` says so. Either resolve it or leave the
   sentence marked unverified. **Do not let it into the row.**

---

**Running count: launched from 74.** `TASK_PHP_017` refuted this row's headline
by construction, refuted three of the manager's claims, and produced eighteen
clean negatives. ⚠ **It also declined to land a rule that would have made one
row's problem into everyone's protocol.** This task exists because it was right;
**hold §4.1 to the same standard, including when the rule is mine.**
