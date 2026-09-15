# TASK_PHP_057 — **THE REVIEW ROUND: NINE UNREVIEWED FINDINGS AND THE THREE CLAUSES `F96` STILL OWES.** ⛔ The backlog has GROWN for two rounds and is the largest since the mining wave

**Role:** research **reviewer / analyst**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_057_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM.** `.memory-php/04-process.md`
**law 12**: *a manager finding from one probe or two rows should be assumed
narrowable until a reviewer has had it.* **Five of the nine findings below are
manager findings from one probe each.**

⭐⭐⭐ **THE STANDING RECORD, QUOTED SO YOU KNOW WHAT NORMAL LOOKS LIKE.** **Six
consecutive review rounds have refuted manager or engineer claims.** At `_053`
**not one finding survived as written**. At `_055` **three of four conclusions
survived and ZERO of four REASONS did** — *"the programme's characteristic
failure mode is a conclusion surviving while its reason dies."* ▶ **So: score
the CONCLUSION and the REASON separately, every time, and say so in those
words.** A finding whose conclusion holds on a ground you had to invent for it
is **UPHELD-ON-NEW-GROUND**, not UPHELD, and the distinction is the round's most
valuable output.

---

## §0 ⛔ THE SCOPE IS BIG. READ THIS PARAGRAPH BEFORE PLANNING YOUR TIME.

**Nine findings plus three prediction clauses is more than any previous round
took**, and the honest reason is that the manager built two rows' worth of
process while the review queue stood still. ⛔ **DO NOT SPREAD YOURSELF EVENLY.**

▶ **THE ORDER BELOW IS BY STAKES AND IT IS BINDING.** Work §1 → §2 → §3 → §4 in
order. ⭐ **If you run out of depth, STOP AND SAY WHERE.** A report that verdicts
§1 and §2 properly and says *"I did not reach §4"* is worth more than one that
touches all nine shallowly — and the second kind is how a round produces
confirmations instead of verdicts.

⭐ **Most of this is CHEAP.** Every figure in §1, §3 and §4 comes from committed
records, a committed tool, or a binary that already exists. **No build, no
re-gate, and — except §2 — no callgrind run.** ⛔ **If you find yourself needing
to build a rung, stop and say why**; that is itself an answer.

⚠ **`TASK_PHP_056` may be running or may have just landed (row 11, `ph97`).**
**If a `ph97` row directory exists under the php patterns tree, read it as
evidence and do not edit it.**

> ⓘ **That sentence names the directory in words rather than as a path, and the
> reason is trap §6.6 below**, which the manager tripped writing this very file:
> the glob spelling scored as `citecheck` rot the moment it was saved, because a
> row the *other* task is still creating does not exist yet. **Sixth instance of
> *a check that reads prose and calls it code*, and the second created by a
> document warning about it.** ▶ **The fix is the rule, not an exemption:
> describe the command, describe the path.**

---

## §1 ⭐⭐⭐ HIGHEST STAKES — `F120`, BECAUSE IT IS A RULE THAT BINDS EVERY FUTURE ROW

**`F120` and the `PROTOCOL_PHP.md` §A3a it created are a rule the manager wrote,
about a measurement the manager took, on a row the manager chose, in one
sitting.** It now obliges every future row. **This is the single most attackable
thing in the programme right now and it is first for that reason.**

### 1.1 The measurement — re-run it, do not take it

Claimed: on the oracle CLI, `mb_get_info()` → `SIG11 si_code=1 si_addr=(nil)`,
exit `139`; `mb_get_info("internal_encoding")` → `ISO-8859-1`, exit `0`, same
binary, same run. The instrument is `.tasks-php/probes/segaddr.c`.

▶ **Re-run both.** Then ask the questions the manager did not:

1. ⭐ **Does it fault WITHOUT the `LD_PRELOAD`?** If the shim is load-bearing for
   the crash, the measurement is about the shim.
2. ⭐⭐ **Is `si_addr=(nil)` actually `strcasecmp`'s read, or could it be
   something else on the way?** There is no gdb. **Say what you can and cannot
   distinguish** — an honest *"I cannot separate these two hypotheses"* is the
   answer this section most wants.
3. ⚠ **Does `-n` matter?** (It skips `php.ini`.) A crash that depends on the
   ini state is a different claim.
4. ⭐ **Does the BENIGN control cover the branch the trigger takes?** The manager
   ran `internal_encoding`; the faulting line is the `"all"` compare. **Run
   `mb_get_info("all")` too.** If it answers cleanly, the row's benign domain is
   wider than the control shown, and F120's table under-states its own evidence.

### 1.2 The rule — and this is where the round earns its keep

`PROTOCOL_PHP.md` §A3a imposes four obligations. **Attack them:**

- ⛔⛔ **THEY ARE NOT THE RIGHT FOUR, AND THE MANAGER REFUTED HIMSELF BEFORE YOU
  ARRIVED. READ THIS BEFORE ANYTHING ELSE IN §1.**
  §A3a requires four things: run the trigger, run a benign control, capture
  `si_addr`, write it as an EVENT. **A fifth was considered and dropped —
  *re-run the trigger against the R1h POST-IMAGE build*, which would make the
  upstream fix's efficacy measurable on real PHP.** It was dropped because
  `TASK_PHP_054` agent B wrote *"the hardened build still crashes — **NOT
  MEASURED**, I cannot rebuild PHP 5.0.0"*, and the manager hardened that into
  a reason.

  ⛔ **IT IS FALSE.** There is a **tracked, idempotent, documented** build script
  at `.app-tests/oracle/build-php-5.0.0.sh` in the `php-in-safe-rust` repo whose
  own header says *"Idempotent: CLEAN extract+build each run; reuses the cached
  tarball"*, builds with **no sudo and no system install**, and works around the
  absent `flex`/`bison` with a stub plus a timestamp guard. **Four 5.0.0 builds
  with four different recorded `cflags` already exist on this box**, two of them
  carrying `.buildinfo` files. ⭐ Agent B meant *"not within my task"*; **the
  manager read it as *"not possible here"* and wrote a protocol section around
  it.** `PROTOCOL.md` **rule 14**, exactly — *a premise in a task file is one an
  engineer has no reason to doubt* — with the manager as the one who doubted too
  little.

  ▶ **SO THE QUESTION IS NOT *"is the claim true"*. IT IS:**
  1. ⭐⭐ **What does a hardened-5.0.0 build actually COST** — wall-clock, disk,
     and how the R1h patch is applied given the script re-extracts cleanly each
     run? **Measure it; do not estimate it.**
  2. ⭐⭐⭐ **Should §A3a require it, or merely permit it?** ⚠ **Requiring it
     makes every row pay for a full PHP build**, and §A3a's whole merit is being
     cheap enough that nobody skips it. **Permitting it may mean nobody ever
     does it.** ▶ **Recommend one, with the cost you measured.**
  3. ⚠ **What would it buy that the applied post-image does not?** `_056`
     verified the `ph97` patch's bytes without building anything. **Be concrete
     about the gap** — my answer is *"whether the fix actually stops the
     fault, rather than whether it looks like it should"*, but that is the
     manager's answer again and it is worth exactly as much as the last one.

  ⓘ **The manager did NOT run the build**, deliberately: `_056` was measuring
  instruction counts at the time, and a concurrent PHP compile would have
  competed for the machine. **That is the only reason. It is not evidence about
  the cost.**
- ⛔⛔ **DOES §A3a QUIETLY DOWN-RANK ROWS WITH NO CLI REPRODUCER?** Most temporal
  rows have none. §A3a says *"where a reproducer exists"* and F120 says in terms
  that a clean run is not a kill (**F3**, `CLAUDE.md` rule 6). ▶ **Is that
  enough, or does a rule that rewards measurable rows bias the corpus the way
  `CLAUDE.md` rule 6's audit found the admission bar did — invisibly, because it
  lives in the BAR and not in any row?** ⭐ **That audit found six of ten
  temporal refusals came from exactly this shape. Take the question seriously.**
- ⚠ **Is the *"say which build"* caution sufficient?** The binary is
  `php-in-safe-rust`'s oracle (`-O3 -march=native -flto`, mysql+webext). **Does a
  fault address measured on THAT build license anything about 5.0.0 as shipped?**

### 1.3 `F116`, which `F120` rests on

`F116` claimed a working 5.0.0 CLI exists, that 14 of 36 corpus reproducers
SIGSEGV, and that **zero manager documents cited it**. The first is now obvious.
▶ **Spot-check the 14 — `grep -ac 'rc=139' .temp/php54B/corpus_repro.log`** —
and ⚠ **note that the log is GITIGNORED**: say whether the claim is re-derivable
from a committed generator, which is `CLAUDE.md` rule 1's test, or whether it
rests on scratch, which is **F51/F99's defect** and has now bitten three times.

---

## §2 ⭐⭐ `F96`'s R2 / R4 / R5 — THE ONLY CLAUSES OF `F96` STILL OWED

`F96` is **verdicted per group** at `_055` (seven groups). **R3 was verdicted by
`_042` §3.** ▶ **R2, R4 and R5 are what is left, and nothing else.**

| | predicted | claimed MEASURED |
|---|---|---|
| **R2** | ≈ R1h — *"5.2.0's repair reinvented by the type system"*, niche-optimised to one word | ⛔ **`+6.97 %` against R1h's `+0.23 %`** |
| **R4** | the `MaybeUninit::uninit()` fill **elides**, byte-identical to R1; *"if not, R4 is DEARER than the C"* | ⛔ **only PARTLY elided — and R4 is `18.9 %` CHEAPER than R1** |
| **R5** | no hand-rolled ghost state | ⚠ **HALF-REFUTED**: none for memory safety, **one `Seq<Option<u32>>` for the VALUE postcondition** |

▶ **For each: does the number reproduce from `ph53`'s committed records, and
does the SENTENCE owe anything it does not pay?**

⛔⛔ **F108's five things: STATISTIC · INPUT · OPT/MODE · BASE · and if the base
is a C cell, WHICH COMPILER, with BOTH columns.** ⚠ **`_055` found `F96`'s
group (d) paying two of five.** ▶ **Expect the same here and check it
explicitly** — `+6.97 %`, `+0.23 %` and `18.9 %` are all quoted bare.
⭐ **R2-vs-R1h is Rust-vs-C, so the C-compiler clause DOES apply** — unlike
group (d), which was Rust→Rust. **Say which compiler, and give both.**

⚠ **R4's is the sharpest prediction in the programme** — it offered two arms and
the truth was outside both. ▶ **Verify that is really so**, because *"outside
both arms"* is exactly the kind of claim that flatters the person who wrote it.

⚠ **R5's half-refutation names a `Seq<Option<u32>>`.** ▶ **Find it in
`patterns-php/ph53-iface-tail-uninit/verus.rs` and say whether it is ghost state
for the VALUE postcondition or for memory safety** — the whole half-refutation
turns on that distinction, and it is checkable in minutes.

---

## §3 `F115`, `F118`, `F119` — the three with real research stakes

### 3.1 `F115` — three of 163 cached patches do not bind to their filename sha

⛔⛔ **DO NOT RE-FETCH ANYTHING FROM THE NETWORK.** The standing decision is
**REPORT, do not guess, never re-fetch**. `fixsurvey.py --offline` and the cache
under `.temp/mgr/batch/patches/` are what you have. ▶ **Re-derive the three**
with `fixsurvey.py`'s `binding_verdict` / `scan_bindings`, and verify its `§H`
arms B1–B6 and the derived B7 ratchet can actually fail.

⚠ **The mechanism is UNEXPLAINED and the finding says so.** ▶ **Do not supply an
explanation you cannot test.** The valuable output here is *what the survey's
guard could and could not have seen* — it checked the header's SHAPE, not its
CONTENT — and **whether any other guard in this repo has the same shape.**

### 3.2 `F118` — the row-11 screen

Three agents, three different picks, no kills, **2 836 report lines**, and the
manager chose `ph97` over `ph66` and `ph90`. ⚠ **The manager's `P2` was refuted
by its own control and its five "best mechanical picks" ranked 91 of 102 rows.**

▶ **The decision to check is not the pick, it is the GROUND:** the manager
overruled the temporal axis staying at one built row *"because F116 lowers the
cost of a temporal row too."* ⭐⭐ **Is that true?** F116/§A3a lowers the cost of
establishing that the C faults — **but §1.2 asks whether most temporal rows even
HAVE a CLI reproducer.** ⛔ **If they do not, the ground for the row-11 decision
is circular and the manager owes a corrected justification.** ▶ **This is the
highest-value single question in §3.**

### 3.3 `F119` — item 117's closure

✅ Cheap: `ph53`'s gate record at three commits carries `envp_stack_bytes`
**3686 / 3697 / 3698** with a bit-identical `marginal_ir_per_call` block
(md5 `79716501c531`). ▶ **Re-derive all three from the records, as EVENTS.**
⚠ **`.temp/php50/sw_ph53.json` is GITIGNORED** — cite the gate records as the
durable evidence and the sweep as re-derivable.

⛔ **DO NOT BUILD THE SWEEP EXTENSION.** The mechanism (100 % of the ±7 swing is
inside a libc `memset` callee that `kernel_exclusive_ir` excludes structurally)
is why. ▶ **But DO check that mechanism claim** — it is the load-bearing reason
an item was closed rather than investigated, and it is quoted from
`.memory/03-measurement.md` rather than measured here.

---

## §4 `F114`, `F117`, `F121`, `F122` — process and tooling, lowest stakes, cheapest

⚠ **Reach these only if §1–§3 are properly done.** Say plainly if you did not.

- **`F114`** — `F96` was never one finding; four reviewer rounds had it in scope
  and two filed verdicts on its result 2 under their own numbers. ▶ **Check the
  four task reports say what F114 says they say.** ⭐ The interesting question is
  structural: *the table's one-cell-per-finding shape is what forced the
  mis-filing.* **Is that true, or is it a story fitted after the fact?**
- **`F117`** — `citecheck` red for a false reason; several checkers' negatives
  flag-gated. ▶ **Run `python3 .tasks-php/checkers.py` and read its output.**
- **`F121`** — three count literals in *prose about* the registry, one created by
  the fix; `probes/` outside the ratchet. ▶ **The claim to attack is the general
  one**: that `.memory-php/04-process.md` law 6 should cover prose about code.
  ⛔ **It is NOT in the layer and does not go there on your say-so.**
- **`F122`** — rot rose for SPLIT report naming, not for in-flight tasks.
  ▶ **Re-run the two-spelling measurement.** ⚠ **And check `N6c`**: the widening
  must not have swallowed a real rot. Try a citation that *should* be rot.

---

## §5 THE MANAGER'S PREDICTIONS, REGISTERED

⚠ **Refute them if they are wrong; confirm them plainly if they are right. Do
not manufacture a refutation to have something to report** — that instruction is
in every task file and it matters most in a round this size.

1. **P1 — §1.2's down-rank question is REAL and I have not answered it.** I
   predict you will find that **a clear majority of the 31 temporal catalogue
   rows have no single-line CLI reproducer**, which makes §A3a's *"where a
   reproducer exists"* do more work than I gave it credit for.
   ▶ **Falsifier: a count over the catalogue's `▸ trigger` lines showing most
   temporal rows DO have one.**
   ⓘ **P1b, added after P1 and pointing the other way** — having already been
   wrong once in this section, I now predict **§A3a will need a FIFTH
   obligation and I will have got its FORM wrong too**: I expect the right
   answer to §1.2's question 2 is *"required for rows whose R1h is one hunk,
   permitted otherwise"*, and I expect that to be refuted as a distinction that
   tracks the manager's convenience rather than the evidence. ⭐ **Say so if it
   survives; I would rather be right than interesting.**
2. **P2 — F96's R2/R4/R5 numbers will REPRODUCE, and their SENTENCES will owe
   F108's five things.** Conclusions survive, reasons and labels do not — the
   programme's standing pattern. ▶ **Falsifier: any of the three numbers failing
   to reproduce from the records.**
3. **P3 — §3.2's circularity is REAL.** I predict my row-11 ground (*"F116
   lowers temporal cost too"*) will turn out to be **true in principle and weak
   in practice**, and that I owe a corrected justification for choosing `ph97`
   over a temporal row. ⭐ **I am predicting against myself here deliberately; if
   you find the ground sound, say so and I will withdraw the prediction, not the
   ground.**
4. **P4 — nothing in §4 will be refuted outright**, because all four are
   measurements over committed artefacts rather than inferences. ⚠ **If P4
   holds, that is a REAL result and not a dull one**: it would be the first
   round in seven where a whole class survived, and it would say the defect rate
   lives in the INFERENCES, not the measurements.

---

## §6 TRAPS

1. ⚠⚠⚠ **`grep -a` ALWAYS** (F35). A line-grep misses a phrase that wraps.
2. ⛔ **READ `citecheck`'s COUNT, NEVER ITS EXIT CODE.** It exits `1` on one
   adjudicated false positive and will do so all round.
3. ⛔ **RUN `checkers.py`, NOT A HAND LOOP** — several checkers hide their §H
   negatives behind `--selftest` and a bare run reads a REPORT as a VERDICT.
4. ⛔ **QUOTE A RE-GATEABLE READING AS AN EVENT, NEVER A STATE** (F119/M2).
   Two `contract_sha256` quotes went stale inside one round.
5. ⚠⚠ **A NUMBER IN PROSE *ABOUT* A TOOL GOES STALE LIKE ONE IN THE TOOL**
   (F121). **Seven instances now.** ▶ **Do not write a count into your report
   that you cannot point at a command for.**
6. ⛔ **DESCRIBE A COMMAND, DO NOT QUOTE IT**, when the command contains a
   path-shaped string under a scanned directory — `citecheck` reads it as a
   citation and it becomes rot. **Five instances, one of them created by the
   explanation of another.**
7. ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY for writing.**
   ⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`,
   `pilot/`, `common-php/`.** ⚠ **No `git add` / `git commit`.** Never touch
   `.web/` — a concurrent session owns it.
8. ⚠ **`.temp/php57/` only — never `/tmp`.** Keep the generator, delete the
   artefact.
9. ⛔ **⚠⚠⚠ `CLAUDE.md` rule 6 binds you too.** *"Safe Rust can't express it"*,
   *"no column moves"*, *"Miri doesn't see it"* are FINDINGS, never grounds to
   drop or down-rank a row. **If you conclude a row should be reconsidered, the
   only admissible grounds are C-side.**
10. **Brackets**: `harness/measure.py --check-stale` → **`66/0`** (must NEVER
    move); `harness-php/gate.py --tool measure --check-stale` → **`22/0`**, or
    **`24/0`** if `_056` has landed. **Quote first and last. You should move
    neither** — if you do, you have run something you should not have.

---

## §7 DEFINITION OF DONE

1. ⭐⭐⭐ **EVERY FINDING YOU REACH GETS A VERDICT IN THE PROGRAMME'S OWN
   VOCABULARY**: `UPHELD` · `UPHELD-NARROWED` · `UPHELD-ON-NEW-GROUND` ·
   `REFUTED IN PART` · `REFUTED` · `NOT A MEASURABLE CLAIM`. **And the
   CONCLUSION and the REASON are scored separately, in those words.**
2. ⭐⭐ **A LIST OF WHAT YOU DID NOT REACH**, by section, with one line on what
   it would have cost. **This is a deliverable, not an apology.**
3. ⭐⭐⭐ **§1.2's two hard questions ANSWERED or explicitly declared
   unanswerable** — are §A3a's four obligations the right four, and does §A3a
   down-rank rows with no reproducer?
4. **§2's three clauses verdicted**, each checked against F108's five things.
5. **§3.2's circularity question answered** — it is the highest-value single
   question in §3.
6. **The four §5 predictions scored, by name, either way.**
7. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** `UNTESTED` and *"I could
   not tell"* are valued answers and are read first.
8. ⭐⭐ **FOR EACH FINDING YOU UPHOLD: name the SECOND METHOD you used.** `F96`
   stood unreviewed for four rounds on a *"no cheap second method"* ground that
   was wrong twice over, and every group turned out to have one. ▶ **If you
   uphold something on the strength of the original evidence alone, SAY SO** —
   that is not a verdict, it is a re-reading.
9. **Brackets quoted first and last.**
10. ⛔ **If a finding survives intact, say so plainly.** Six rounds of refutation
    is a record to be proud of, not a quota to fill.
