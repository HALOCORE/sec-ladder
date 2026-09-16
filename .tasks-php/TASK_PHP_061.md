# TASK_PHP_061 — **THE NINTH REVIEW ROUND.** ⭐⭐⭐ Eight findings, **six of them the manager's**, and `F137` claims safe Rust has an advantage the ladder's cost columns cannot express

**Role:** research **reviewer / analyst**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_061_REPORT.md` — **write the FILE** (`PROTOCOL.md`
rule 10). A report that exists only in your final message does not exist.

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM.** `.memory-php/04-process.md`
**law 12**: *a manager finding from one probe or two rows should be assumed
narrowable until a reviewer has had it.* ⛔ **Six of the eight below are
MANAGER findings, and four of those are the manager about the manager.**
Count them yourself: read `RECAP_PHP.md`'s RULE-9 table and take the rows whose
verdict column opens `⛔ UNREVIEWED`. **Do not trust this sentence** — a count
in prose about a structure rots exactly like one inside it (`F121`).

⭐⭐⭐ **THE STANDING RECORD, SO YOU KNOW WHAT NORMAL LOOKS LIKE.** **Eight
consecutive review rounds have refuted manager or engineer claims.** At `_053`
**not one finding survived as written**. At `_055` **three of four conclusions
survived and ZERO of four REASONS did**. At `_058` **zero of five manager
predictions survived**. At `_059` the manager's one deliberately
self-adversarial prediction was **the only one that held**.

> ▶ **SO: SCORE THE CONCLUSION AND THE REASON SEPARATELY, EVERY TIME, IN THOSE
> WORDS.** A finding whose conclusion holds on a ground you had to invent for it
> is **UPHELD-ON-NEW-GROUND**, not UPHELD, and that distinction has been this
> programme's most valuable single output for six rounds running.

---

## §0 ⛔ READ THIS BEFORE PLANNING YOUR TIME

**Eight findings.** It grew `2 → 4 → 7` over three task boundaries and then to
**8** when the manager filed `F138` while writing this brief — ⭐ **so measured
over the last 40 `RECAP_PHP.md` commits, today is the largest backlog the
programme has carried, and the previous record was 7.**

> ⛔⛔⛔ **THE FIRST DRAFT OF THIS PARAGRAPH SAID *"the second-largest backlog,
> with a measured peak of 9 at `f98e716`"*, AND THAT IS FALSE — CAUGHT BEFORE
> DISPATCH, FILED AS `F138`, AND LEFT HERE ON PURPOSE.** The raw open-row count
> at `f98e716` really is 9, but **six of those nine are `F120`–`F125`, which
> `_057` had already verdicted** and which appeared in the table TWICE — the
> duplication **`F131`** was filed about and later repaired by merging.
> De-duplicated, `f98e716` carried **3**. ⭐ **The de-duplicated maximum in the
> window is 7, at `1db52a3`, which is today's number.**
>
> ⭐⭐⭐ **WHY IT IS IN YOUR BRIEF RATHER THAN QUIETLY FIXED: the manager RAN THE
> TOOL and still got it wrong, because he consumed its CARDINALITY and never
> printed its MEMBERS.** ▶ That is **`F132`'s rule** — *adjudicate the SET, by
> unit text, never the number* — **holding one level up, on the RULE-9 index,
> against the person who wrote it.** §5 asks you to rule on where that knowledge
> should live; **this is a live instance, made while writing the question.**

⚠ **That is nearly twice `_059`'s load and it is NOT an instruction to go
faster.**

▶ **THE ORDER IS BY STAKES AND IT IS BINDING: §1 → §2 → §3 → §4 → §5.**

⭐⭐⭐ **STOPPING CLEANLY IS A FIRST-CLASS OUTCOME.** If you run out of depth,
**STOP AND SAY WHERE.** A report that verdicts §1 and §2 properly and says *"I
did not reach §5"* is worth more than one that touches all eight shallowly — and
the second kind is how a round produces confirmations instead of verdicts.
⭐ **§5 is four DOCUMENT findings batched behind one question.** They are last
because they are cheapest, not because they are unimportant, and **if you reach
them with little left, answer the one shared question and skip the details.**

⛔⛔ **YOUR STATED PRIORITY BINDS THE MANAGER. `F123` IS WHY.** An engineer wrote
*"it is the cheapest remaining check and it is not done"*; the manager's next
task file demoted it to *"nice to have, skip it"*; two rounds later the protocol
treated it as **impossible**, and it turned out to cost **30 seconds**.
▶ **Write a `§ ORDER TO RESUME IN` naming what is left AND the priority you
would give it. It will be CARRIED, not re-ranked.**

### 0.1 ⭐ MEASURED PREMISES — every one was RUN before this file was written

`PROTOCOL.md` **rule 14**: *run the premise before you write it into a task
file.* Each row names the command that produced it, **run at `dbb1df6`**.

| premise | command | measured |
|---|---|---|
| the checker registry passes | `python3 .tasks-php/checkers.py` | `CHECKERS PASS`, **29 filed**, ~35 s |
| the ratchet is green | `python3 .tasks-php/cbaseline_check.py` | `scanned 33 file(s); 77 hit(s); ratchet 77`, **rc 0** |
| both staleness brackets | `python3 harness/measure.py --check-stale`; the php one via `harness-php/gate.py` with `--tool measure --check-stale` | **`66 / 0 STALE`** and **`26 / 0 STALE`** |
| the backlog is derivable, not asserted | `boxcheck.rule9_rows` over `RECAP_PHP.md`, last block | **8 rows** (7 at `dbb1df6`, plus `F138`), and they are the eight sectioned below. ⚠ **Read the MEMBERS, not the count — that is `F138`** |
| **every** built row carries an R1h | scan the 12 gate records in `results-php/gate/` for `c-gcc-h`/`c-clang-h` | **12 of 12** — so `F133` has **eleven** other rows to be tested against |
| but only two rows ship a **census** control | list `census.py` under the rows' `controls/` | **`ph56` and `ph96` only** |
| ⭐⭐ `ph97` **already carries the Rust half** of `F137`'s sweep | read `opt_sweep_unchecked` in its `controls/rust_bug.json` | `O0` **rc −6 (SIGABRT)** · `O1`,`O2`,`O3` **`TIMEOUT`** |
| ⭐⭐ `ph97` carries **no C-side** opt sweep | key list of its `controls/widened_domain.json` | no `opt_sweep` key (`ph96`'s has one) |
| ⛔⛔ `ph97`'s faulting input is **`adversarial-absent.bin`**, NOT the one named `nullvalue` | `faulting_cells` in the same file | `[[absent, c-clang], [absent, c-gcc]]` |
| ⛔⛔ and `ph97`'s C faults under **BOTH** compilers at the built cell | the same file's table | rc **139** both; `si_addr=(nil)` under gcc, **`0x1`** under clang |
| the registry's surviving non-zero expectations | tally `expect`/`st_expect` over `REGISTRY` | **three**: `citecheck.py expect=1`, two `kind=landing` scripts `expect=2`. **`st_expect` is `0` on all 12 that declare one, `None` on 17** |
| `F136`'s four cells are **field-identical**, not merely zero-difference | read `ph96`'s `controls/repair_price.json` | `kernel_exclusive_ir`, `whole_program_ir` **and** `ir_per_call` identical to the last digit in all four |

⭐ **Nothing in this round needs a re-gate or a rebuild.** Everything you are
asked to attack is either arithmetic over committed records or a probe whose own
`pin` block states its cost (`ph97`'s `rust_bug.py`: *"two rustc builds and four
runs; under a minute"*; its `widened_domain.py`: *"runs the built O3/isolated
binaries; minutes"*).

---

## §1 ⭐⭐⭐ `F137` — THE HIGHEST-STAKES UNREVIEWED FINDING, AND THE ONE THE BOX SAYS TO ATTACK HARDEST

`RECAP_PHP.md` → the `F137` section; then `TASK_PHP_060_REPORT.md` §9 and
`ph96`'s `controls/widened_domain.py` + `controls/rust_bug.py` with their
`.json` outputs.

**The claim**, in the finding's own words: *the axis is not COST, it is WHETHER
DETECTION SURVIVES THE OPTIMISER.* C faults at every `-O` under gcc but returns
a **silent wrong answer** above `-O1` under clang; unsafe Rust shows the same
shape one level lower (SIGABRT at `-O0`, silent wrong answer above); safe Rust
panics at all four. ⭐ **This is the first row where safe Rust's advantage is
stated in a currency the ladder's cost columns cannot express at all** — which
under `CLAUDE.md` rule 6 is a **finding**, not a gap.

⚠⚠ **SCORE ITS THREE CLAUSES SEPARATELY. THEY HAVE VERY DIFFERENT STANDING.**

1. **The row-level measurement** (the two 4-column tables). Arithmetic over a
   committed probe; expected to survive.
2. **The generalisation** — *this is a property of the C-vs-Rust ladder, not of
   `ph96`.* **One row, one defect shape, two compilers, one box.**
3. **The ladder sentence** — *detection-survives-the-optimiser is a new axis.*
   A claim about what the programme should publish, and the one with teeth.

### 1.1 ⛔⛔ THE FALSIFIER THE FINDING NAMED IS HALF ALREADY ON DISK — AND ITS OTHER HALF NAMES THE WRONG FILE

`F137` says: *"the cheap test is any other built row with a null-sentinel
adversarial input; `ph97` is the obvious first candidate and was not swept."*
**Both halves of that sentence need correcting before you spend a minute on it,
and the corrections are §0.1's rows, not my opinion:**

- ⭐⭐ **The RUST half was already swept.** `ph97`'s `controls/rust_bug.json`
  carries `opt_sweep_unchecked`, and it reads **`O0` SIGABRT, then `TIMEOUT` at
  `O1`, `O2` and `O3`.** ▶ **That is a THIRD outcome `F137`'s binary does not
  have**: not *detected*, not *silent wrong answer*, but **hung**.
  ⚠⚠ **AND THE TWO SWEEPS ARE NOT THE SAME CONSTRUCTION** — read both before
  comparing them. On `ph96` the shipped `unsafe.rs` **answers correctly** and the
  swept variant is a **guard-deleted mutant**; on `ph97` the swept `unchecked`
  variant's own `why` says it is `unsafe.rs`, *"the one that reproduces C"*.
  ▶ **A finding that compares them must say which is which, and `F137` does not.**
- ⛔⛔⛔ **The C half's candidate input is MIS-NAMED in the finding.** `ph97` has
  a file literally called `adversarial-nullvalue.bin` and **it does not fault in
  any cell**. The faulting input is **`adversarial-absent.bin`**. The row's own
  `inputs/gen.py` says so in terms — *"`nullvalue` is the argument that IS null
  but was SUPPLIED (which does not fault, and that separation is the row's claim
  at run time)"*. ▶ **A reviewer who picked by NAME would sweep a clean input,
  find nothing at any `-O`, and report `F137` refuted.**
  ⭐⭐ **That is `F134`'s own class — reading a LABEL instead of a BODY — sitting
  inside the falsifier for a finding filed in the same round as `F134`.** Say so
  if you agree; it is evidence about the programme, not about `ph97`.

### 1.2 ⭐⭐⭐ THE DATUM THAT MAY ALREADY DECIDE CLAUSE 2, AND I HAVE DELIBERATELY NOT RULED ON IT

`ph97`'s `widened_domain.json` records, at the cell its own `pin` describes as
the built `O3/isolated` binaries, on `adversarial-absent.bin`:

| cell | exit | `si_addr` |
|---|---|---|
| `c-gcc` | **139** | `(nil)` |
| `c-clang` | **139** | **`0x1`** |

> ⭐⭐ **MANAGER READING, 2026-09-16 — REGISTERED SO YOU CAN ATTACK IT RATHER
> THAN INHERIT IT, AND IT IS NOT A VERDICT.** On `ph96`, clang above `-O1`
> goes **silent**. On `ph97`, clang at the built cell **faults**. If that cell
> really is `-O3`, then *"C's detection is build-dependent and fails the same
> way"* **does not reproduce one row over**, and clause 2 is refuted from data
> that was already committed when `F137` was written.
>
> ⛔ **THREE WAYS THIS READING COULD BE WRONG, AND I HAVE CHECKED NONE OF THEM:**
> (a) the built cell may not be `-O3` — I took that from a `pin` note, not from
> the build record; (b) `ph97`'s defect shape may differ from `ph96`'s in a way
> that makes the comparison meaningless; (c) *faults at `-O3`* does not by
> itself establish *faults at every `-O`*, which is the actual claim.
> ▶ **RE-DERIVE IT. DO NOT CITE MINE.**

▶ **THE QUESTION, AND IT CUTS BOTH WAYS:**

- **(a)** If clause 2 is **refuted**, `F137` shrinks to a row fact — still a
  good one, still `F3` firing live — and the ladder sentence in clause 3 loses
  its warrant, because a new *axis* needs more than one row.
- **(b)** If clause 2 **survives in a narrowed form** — e.g. *the optimiser can
  convert a detected fault into a silent one, and whether it does is
  compiler-, row- and level-dependent* — then it is **weaker as a headline and
  stronger as a rule**, because it then applies to every C row the programme
  will ever build and nothing in the harness currently checks for it.

⭐⭐⭐ **SETTLING (a) VS (b) IS THE MOST VALUABLE THING THIS ROUND CAN DO.**

### 1.3 The clause nobody has attacked — *"the cost columns cannot express it"*

⚠ **This is the clause that would change what the programme publishes**, and it
is asserted, not measured. ▶ **Is it true?** A detection outcome is a
**categorical** per-(cell, opt, input) value; the ladder already records
categorical per-cell facts (`identity_level`, `faulting_set`, Miri policy).
▶ **So is the right reading *"the COST columns cannot express it"* — trivially
true and uninteresting — or *"the ladder has no column for it"*, which is
false if `faulting_set` counts, or *"the ladder has no column for it ACROSS
OPTIMISATION LEVELS"*, which looks true and is the interesting one?**
⛔ **Do not let the finding be quoted at the widest of the three.**

### 1.4 The two cheap clauses — verdict them, briefly

- ⭐ **Its `F3` half.** *"A reviewer who tested only `c-clang -O3` would have
  concluded the defect was not reachable."* ▶ **Is that counterfactual true of
  THIS row's actual gate?** The row gated `PASS` with `failures: []`; find out
  whether the gate would in fact have been satisfied by a clean `c-clang` run,
  or whether some other stage would have caught it. **If the gate would have
  caught it anyway, the clause is rhetoric.**
- ⚠ **Do NOT let `F137` be quoted as *"clang miscompiles"***. The C is UB and
  clang is within its rights; the finding is about **detection**, not
  correctness. ▶ **Check that the finding's own text never slips into the wrong
  one** — and if it does, say which sentence.

---

## §2 ⭐⭐⭐ `F136` — THE UNMISUSABLE CONTRACT IS FREE, AND IT REFUTED THE MANAGER IN FOUR CELLS OF FOUR

`RECAP_PHP.md` → `F136`; `TASK_PHP_060.md` §2.6 and `_060_REPORT.md`; `ph96`'s
`controls/repair_price.py` and `repair_price.json`.

**The claim:** the two upstream-attested repairs of `ph96`'s obligation —
passing `NULL` (upstream's `cf020f133487`) versus writing the `:385`-style guard
— differ by **`+0.0000 Ir/call` on both C compilers and both inputs**, with
checksums asserted equal first. Under `c-clang` they are the **same program**
(`identity_level=exact`, 280 insns, 1070 bytes); under `c-gcc`, `counts`
(207/207 insns, 705/705 bytes).

⚠ **LAW 12 CUTS NORMALLY HERE**: engineer-measured, and it **refutes** the
manager's `P1` in four cells of four plus both headlines he offered.
⭐ **The CONCLUSION is arithmetic over committed records and will probably
survive. Spend your time on the other two things.**

### 2.1 ⛔ THE CHEAPEST POSSIBLE ATTACK, AND IT MUST BE RUN FIRST

§0.1 measured that the four cells are **field-identical** — not merely that the
difference is zero, but that `kernel_exclusive_ir`, `whole_program_ir` **and**
`ir_per_call` agree to the last digit in every one of the four.

▶ **A zero difference and a measurement that never distinguished the two builds
produce the SAME JSON.** ⭐ **So establish that the control actually built and
ran two different binaries.** The `identity` block claiming `counts` under
`c-gcc` is evidence that it did — *`exact` under clang and `counts` under gcc*
is not a pattern a single-binary bug would produce — but **read the control and
confirm it, because if this fails, `F136` does not exist.**

### 2.2 ⭐⭐ THE CLAUSE TO ATTACK IS THE MECHANISM

*"Removing the output moves the call site from `zend_interfaces.c:94`'s
contract onto `:88-93`'s, where `:89`'s `if (retval)` does the work"* — a claim
about **why** the price is zero, not that it is.

- ▶ **The quantifier is checkable and it is not obviously safe:** the finding
  says the test *"was already written once, in the callee, for all seven
  no-output call sites."* `F133`'s census says **23 real call sites, 7
  no-output, 16 output**. ▶ **Does `:88-93` in fact cover all seven, or seven
  minus something?** `ph96`'s `controls/census.json` and the pinned tarball
  settle it and neither needs a build.
- ⚠ **`identity_level=exact` under `c-clang` is the strong evidence;
  `counts` under `c-gcc` is weaker.** ▶ **Does `counts` hide a real difference
  that `exact` would not?** Two builds can have equal instruction counts and
  different instructions. **Say what `counts` does and does not license.**
- ⭐ **If the mechanism is right, it has a consequence the finding does not
  draw:** the price is zero *because of where the callee's test already is*, so
  it would **not** be zero for an obligation whose callee carries no such test.
  ▶ **Is that a narrowing `F136` should carry?**

### 2.3 The method lesson, which is the manager's and is registered

*"Registering both poles of a disjunction does not make the disjunction
exhaustive."* He offered *cheaper* and *dearer* as a matched pair and the answer
was **neither**. ▶ **Is that the right lesson, or is the right lesson that
`P1` should have had a null pole?** A one-line verdict is enough.

---

## §3 ⭐⭐⭐ `F133` — *AN R1h IS EVIDENCE ABOUT WHAT WAS CHOSEN, NOT ALWAYS ABOUT WHAT WAS KNOWN*

`RECAP_PHP.md` → `F133`; `.tasks-php/probes/ph96_arrayaccess_matrix.sh`;
`ph96`'s `controls/census.py` + `census.json`.

⭐⭐ **THIS IS THE STRONGEST LAYER-SHAPED CLAUSE THE PROGRAMME HAS OPENED ABOUT
R1h**, and the programme reads an R1h as *the repair upstream eventually found*.
`F133` says that on `ph96` the repair was **available, correct, in the same
file, and already in use on 7 of 23 call sites before the bug was filed** —
upstream's fix **copied** a sibling 99 lines up rather than discovering
anything.

⚠ **The measurement half is a four-cell natural experiment and should survive**:
one helper, four ArrayAccess handlers, two guarded/no-output sites clean and two
unguarded sites faulting at **predicted** addresses (`0x10` = `offsetof(zval,
refcount)`, `0x14` = `offsetof(zval, type)`), both computed from
`Zend/zend.h:287-293` *before* the run.

▶ **ATTACK THE GENERALISATION, NOT THE MEASUREMENT.**

- ⭐⭐ **§0.1 measured that all twelve built rows have an R1h**, so *"does this
  hold on any other row's R1h?"* has **eleven** candidates and is the review's
  main question. ⛔ **But only `ph56` and `ph96` ship a `census` control**, so on
  the other ten the instrument does not exist. ▶ **Do `ph56` first**, because it
  is the one row where the instrument is already built, and report **what a
  second row would cost** rather than running ten.
- ⚠⚠ **The generalisation has a shape worth separating.** *"Chosen, not known"*
  is three different claims: **(i)** the repair existed in the tree; **(ii)** its
  author knew it existed; **(iii)** an R1h therefore cannot be read as evidence
  of discovery. ⭐ **(i) is measurable, (ii) is not, and (iii) follows only from
  (ii).** ▶ **Does `F133` establish (ii) anywhere, or does it slide from (i) to
  (iii)?** The *"by one author"* clause in its title is doing the work — **check
  it**: same file is not same author, and 2005 `git blame` on a tarball is not
  free. **If (ii) is unestablished, the finding is UPHELD-NARROWED and the layer
  gets (i) plus a much weaker (iii).**
- ⛔ **Its scope caveat is load-bearing and must survive any quote**: *no repair
  in the 163-patch CACHE* ≠ *upstream never fixed it*. ▶ **Confirm the finding's
  own text preserves that distinction everywhere, not just where it says so.**
- ⓘ **It commits the ladder to nothing** — a C-side finding, so under
  `CLAUDE.md` rule 6 the Rust rungs' answer is a result whatever it is.

---

## §4 ⛔⛔⛔ `F135` — A RATCHET SILENCED BY EDITING ITS EXPECTATION

`RECAP_PHP.md` → `F135`; `.tasks-php/checkers.py`'s `citecheck.py` entry;
`.tasks-php/citecheck.py`'s `N5d`/`N4`.

**The claim:** `citecheck.py --selftest` failed `N5d`/`N4` for **43 commits**
while the sweep printed `ok`, because `checkers.py` named the failing arms, gave
a benign-sounding cause, and set `st_expect=1`. Both halves are now repaired
(`N5d` asserts structural disjointness — 81 live docs vs 203 extension inputs,
0 shared — and `st_expect` is `0`, derived from intent).

⚠ **Manager about the manager's own tooling. Law 12 cuts the usual way.**

### 4.1 The reviewer's stated question, now measurable

*Is `st_expect` DERIVED FROM INTENT anywhere else, or is this the only one
captured from observation?* §0.1 measured the surviving population: **three**
non-zero expectations in the whole registry — `citecheck.py expect=1` and two
`kind=landing` scripts at `expect=2` — with `st_expect` **`0` on all twelve that
declare one**.

- ▶ **So the question is now answerable in minutes, and it should be answered
  for the `expect` COLUMN AS A WHOLE, which is what nobody has done.** The two
  landing scripts' `why` text reads *"rc=2 is the refusal to re-run, which is
  correct"* — **intent-derived on its face.** `citecheck.py`'s `expect=1` is the
  adjudicated rot. ▶ **Verdict each of the three as INTENT or OBSERVATION and
  say how you told them apart** — because *"it says so in its `why`"* is the
  same kind of evidence that hid `F135` for 43 commits.
- ⛔⛔ **AND ASK THE HARDER VERSION.** `st_expect=None` on **17** entries means
  *no `--selftest` is declared*, which is not an expectation at all — it is an
  absence. ▶ **Eight of those twenty are `kind=checker`.** Is a checker with no
  declared self-test a third silencing mechanism, weaker than editing the
  expectation but in the same family? **The registry cannot currently tell
  *"has no self-test"* from *"has one and it passes"* at a glance.**

### 4.2 ⭐⭐ The layer-shaped clause — this is the part to verdict

> *A ratchet silenced by editing its EXPECTATION is silenced exactly as surely
> as one silenced by editing its INPUT, and only the second is forbidden in
> writing.*

- ▶ **Is that right, and if so does it enter `.memory-php/04-process.md` as a
  NEW law or as a clause on the existing ratchet rule?** ⭐ **Prefer the second
  unless you can say why** — the layer has taken appended clauses before and
  `F109`'s *"refinement"* turned out to be a rule the layer already carried.
- ⚠ **Attack the *"exactly as surely"*.** Editing the input destroys evidence;
  editing the expectation leaves the failure fully visible to anyone who runs
  the tool directly. **Are they really the same, or is one recoverable and the
  other not?** The finding's own history is the test case: **it was found by a
  sweep, from the registry text, which is exactly the recovery an input edit
  would have prevented.**
- ⓘ **Its supporting sentence is worth its own line**: *a benign cause does not
  make a failing arm benign.* That one looks to me like the durable part. **Say
  whether you agree and whether it is the same claim or a different one.**

---

## §5 THE FOUR DOCUMENT FINDINGS — **`F134`, `F132`, `F131`, `F138`, BATCHED BEHIND ONE QUESTION**

⚠ **Cheapest section; do it last; answer the shared question even if you skip
the details.** All four are manager self-findings about manager artefacts, and
**none of the four has proposed that anything enter `.memory-php/`.**

### 5.0 ⭐⭐⭐ THE SHARED QUESTION — **WHERE DOES A TRAP LIVE?**

`F134` asks it outright and the manager **deliberately did not decide it**: *is
a task file's `§3 TRAPS` the right home for a trap a TOOL already guards, or
does it belong in `.memory-php/04-process.md` as a law?*

▶ **Rule on it once, for all four**, because all four are instances:

| finding | the knowledge | where it currently lives |
|---|---|---|
| **F134** | *git's `xfuncname` labels a hunk with the PRECEDING function* | a **tool docstring** (`preimage_screen.py::same_function`) — and the manager, reading by hand, was not on that path |
| **F132** | *a ratchet's count is a property of PARAGRAPH BOUNDARIES, so adjudicate the SET by unit text* | a **committed tool** (`cbaseline_diff.py`, four must-fire arms) |
| **F131** | *a verdict-shaped phrase in a verdict column is a verdict, whoever wrote it* | **nowhere** — a shape repair applied to the RULE-9 table itself |
| ⭐ **F138** | *a tool that returns a SET, consumed for its CARDINALITY, has been converted back into an unchecked number by its caller* | **nowhere** — and it was made **while writing this section's question** |

### 5.0a ⛔⛔ `F138` FIRST, BECAUSE ITS ONLY REAL QUESTION IS WHETHER IT EXISTS

**The manager's claim is that `F138` is DISTINCT from `F132`**: `F132` is about a
ratchet whose count moves for reasons unrelated to its claims, whereas `F138` is
about a tool that was **correct** and a caller that **discarded** what it
returned. ▶ ***"I used the tool" is not the defence it sounds like*** is the
proposed new content.

- ⛔ **If that clause does not hold, `F138` should be MERGED INTO `F132` and not
  carried separately** — and the manager says so in advance rather than
  defending the finding. **That is a legitimate and probably the cheapest
  outcome; take it if it is right.**
- ✅ **Its measured half is arithmetic over committed records**: raw 9 vs
  de-duplicated 3 at `f98e716`, and a corrected window maximum of **7 at
  `1db52a3`**. ⚠ **Note the de-duplication rule the manager used** — *a key with
  two rows has been verdicted in one of them, so it is not open* — **and say
  whether it is right.** It is a heuristic, not a parse of the verdict column.
- ⭐⭐ **The residue worth more than the finding**: `boxcheck.rule9_rows` returns
  **no parse** on twelve of the forty commits in the window, because the block
  did not yet have its current shape. ▶ **Those are UNKNOWN, not 0** — and a
  tool that returns a falsy value for *"cannot answer"* invites exactly the
  `len()` mistake `F138` is about. **Is that worth a repair to the tool?**

⭐⭐ **THE CASE FOR A LAW, IN THE PROGRAMME'S OWN EVIDENCE:** `F132`'s instances
**2 and 3 were made by the manager in the edit that landed the review of the
ratchet, on the same day the reviewer named the mechanism.** The warning had
been read, understood, and written down **before** the edit that tripped it
twice. ▶ ***"Remember to check" is refuted as a control by the strongest
available evidence: the person who wrote the reminder.***

⛔⛔ **THE CASE AGAINST, AND IT IS NOT WEAK:** `04-process.md` is the
**authoritative layer**, and rule 9 says nothing enters until it survives a
cycle. A law per hand-error would fill it with things that are true of people in
general rather than of this programme. ▶ **If your answer is "not the layer",
say what the alternative is** — the traps list, a `PITFALLS`-style file, the
tool, or nothing — **and say it in a form the manager can act on.**

ⓘ **`F134`'s own text routes this to item 129's census as the sizing
instrument.** ▶ **Is that right, or is the home question decidable WITHOUT the
census?** ⭐ **If it is decidable without, say so — item 129 is ~289 items and
the manager has been treating it as a blocker.**

### 5.1 The residues, if you have time

- **F134** — ⛔ **Do NOT let it be quoted as moving `same_function`'s measured
  *"1 of 170"*.** The manager states in the body that he did not measure whether
  `235e6c0afe1d` is even in that screened set. ▶ **Check the body actually says
  that** and that nothing else in the finding implies otherwise.
- **F132** — ▶ **Is *"adjudicate the set, never the number"* the right repair,
  or does the PARAGRAPH UNIT itself need changing?** ⭐ The tool is committed
  with four must-fire arms and reproduces `F130`'s `1cc2c0e` baseline **without
  a worktree** — so the repair is real; the question is whether it is the right
  one. ⚠ Note that `_059` **refused** widening `BASE`/`XLANG` as framed for an
  eighth time, so *"a better regex"* is not on the table.
- **F131** — ▶ **The one clause with layer shape**: *self-narrowing must not
  share a column with review outcomes, because that erases law 12's
  distinction.* ⭐ **You are reading the repaired table right now to derive this
  round's own scope. If the repair failed, this round is mis-scoped** — so this
  is the one §5 item with a live consequence, and it is nearly free to check.

---

## §6 THE MANAGER'S PREDICTIONS, REGISTERED — **score every one**

⛔ **At `_058` these scored ZERO OF FIVE; at `_059` one of five.** They are
registered so the round has something to refute.
⚠ **`F136`'s own method lesson is applied here:** none of these five is one pole
of a matched pair, because *registering both poles of a disjunction does not
make the disjunction exhaustive.*

| | prediction | confidence |
|---|---|---|
| **P1** | ⭐⭐⭐ `F137` lands **UPHELD-NARROWED**: the row measurement survives, **clause 2 (the generalisation) is refuted or heavily narrowed** on `ph97`, and the narrowed statement needs a **third outcome category** (*hung*) that the finding's two-way split has no room for. | **medium-high — but §1.2's datum is already in my hands, so treat this as a reading I have not tested, not a forecast** |
| **P2** | `F136`'s **conclusion survives untouched** and its **mechanism survives with a narrowing**: the zero price is contingent on the callee already carrying the test, which the finding states and does not draw a consequence from. | medium |
| **P3** | `F133` lands **UPHELD-NARROWED** on the (i)/(ii)/(iii) split: *the repair existed in the tree* is measured, *its author knew* is **not established**, and the R1h rule that may enter the layer is therefore weaker than the one the finding states. | medium |
| **P4** | `F135`'s layer clause is **UPHELD and enters as a CLAUSE on the existing ratchet rule**, not as a new law — and the reviewer finds `citecheck.py`'s `expect=1` is the **only** observation-captured expectation left in the registry. | medium |
| **P5** | §5.0 is ruled **"not the layer"** for all four, with **at most one clause** entering — and the reviewer finds the home question **decidable without item 129**, which would unblock it. | **low — I am predicting against the route `F134` itself proposes** |

▶ **If you refute one, say which clause and on what evidence. If one survives,
say so plainly — a round that refutes everything is as suspicious as one that
confirms everything.**

---

## §7 TRAPS

1. ⭐ **`grep -a` ALWAYS.** `F35`. Several files here trip binary detection and
   `grep` silently reports nothing rather than failing.
2. ⛔⛔⛔ **READ DIFF BODIES, NEVER `@@` LABELS, AND NEVER ATTRIBUTE A COMPOUND
   `grep` MATCH.** `F134` — and **§1.1 shows the same class already sitting
   inside this round's own §1 falsifier.** A name is not a body: `ph97`'s
   `adversarial-nullvalue.bin` is not the null-sentinel input.
3. ⛔ **DESCRIBE A COMMAND OR PATH, DO NOT SPELL IT.** Brace expansion in a task
   document has produced `citecheck` rot **seven times**, and **three of those
   were created by a document warning about it.** Name the directory and the
   file in prose.
4. ⚠ **Quote a re-gateable reading as an EVENT, never a STATE** — *"read at
   `dbb1df6`"*, not *"the value is"* — **and date it to the commit where the
   number actually reads that way.** A cost quote dated to a commit where the
   figure was different is the defect `F126` exists to prevent.
5. ⭐⭐ **COUNT IT, DON'T ASSERT IT.** Four claims in `RECAP_PHP.md` fell to this
   in one session, three of them with the checking tool already in the repo.
   **If you state a count, derive it from what a tool PRINTS** (`F121`).
6. ⭐ **BEFORE APPENDING TO A LIST, CHECK THE LIST'S OWN PREDICATE.** The
   `which statistic` cell named a row as publishing both statistics when it
   published one, and the next editor appended beside it without checking.
7. ⭐⭐ **WRITE A CORRECTION IN PLACE OF A STALE CLAIM, NEVER BESIDE IT** — and
   **when you repair a defect in one place, check every place that shares the
   artefact.** The RULE-9 table once had **six** keys with two rows each.
8. ⛔⛔ **YOU NEVER RUN `git commit` OR `git add`** — `CLAUDE.md` rule 4.
   Read-only git is fine and you will need it. The manager commits at task
   boundaries.
9. ⛔⛔ **DO NOT EDIT ANYTHING UNDER `patterns-php/`. REPORT IT INSTEAD.**
   Controls are hashed into `source_sha256`; touching one costs a re-gate at
   ~2 m 30 s. You may **run** any control (they are read-only re-derivations
   whose `pin` blocks state their cost). You may repair tools under
   `.tasks-php/`. ⚠ **If you repair one, re-run the registry.**
10. ⛔ **No edits to `harness/`, `common/`, `patterns/`, `results/`, `pilot/` or
    `common-php/`** — the PAT side is frozen infrastructure hashed into 33 gate
    records.
11. ⛔ **No `/tmp` scratch.** Use `.temp/`, a subdir per category. **Keep the
    generator, delete the artefact** — if a number you report has no committed
    script that rebuilds it, **say so**, which is exactly what §1.2's manager
    reading does.
12. ⚠ **`.memory-php/` and `RECAP_PHP.md` are MANAGER-ONLY for writing.** Quote
    them, cite them, refute them — do not edit them.
13. ⚠ **`.web/` is edited by a concurrent session.** Do not touch it, and never
    `git add -A`.
14. ⛔⛔⛔ **NEVER REFUSE OR REMOVE A PATTERN FOR A RUST-SIDE, VERUS-SIDE OR
    LADDER-SIDE REASON.** Admission is decided **solely on the C program**.
    *"Safe Rust can't express it"*, *"no column moves"*, *"Miri doesn't see
    it"*, *"the R5 can't state the obligation"* are **ALL FINDINGS, NEVER
    KILLS.** ⭐ **`F137` is the live case**: its whole content is that safe Rust
    wins in a currency the ladder does not price, which is a **result**.
15. ⛔⛔ **A `task-notification` means STOPPED, not FINISHED** — and it can also
    mean *still running*. **Verify a gate record's source hashes, not its
    verdict.**

---

## §8 DEFINITION OF DONE

1. **Every claim scored CONCLUSION and REASON SEPARATELY, in those words.**
2. **Each verdict names its SECOND METHOD** — or says plainly there was none,
   and why. *"I re-ran the manager's tool"* is not a second method.
3. **Every percentage pays `F108`'s five things**: STATISTIC · INPUT · OPT/MODE ·
   BASE · and if the base is a C cell, **WHICH COMPILER — with both columns, or
   an explicit statement that only one was measured.**
4. **For each of the eight, say what may enter `.memory-php/` and what may
   not** — in the form the RULE-9 table takes, so the manager can apply it to
   the row rather than append below it.
5. **A `§ WHAT I AM UNSURE OF` section**, with every cost either **measured** or
   **explicitly labelled an estimate**. ⭐ `F123`: an engineer's own estimate of
   a check's cost is evidence, and this section is the one that gets demoted.
6. **A `§ ORDER TO RESUME IN`** if you stop short, naming what is left **and the
   priority you would give it**. It BINDS the manager.
7. **A numbered `§ FOR THE MANAGER`** routing anything that needs a decision, a
   dispatch, or a `RECAP_PHP.md` edit.
8. **Re-run the checker registry at the end** and report `CHECKERS PASS` or the
   exact failure. ⚠ **And re-run the ratchet** — if its count moved, **diff the
   SET by unit text with the committed tool, never the number** (`F132`).
9. **Say what you did NOT do.** A round that claims full coverage of eight
   findings in one sitting will be read as shallow, because the last eight were
   not.
