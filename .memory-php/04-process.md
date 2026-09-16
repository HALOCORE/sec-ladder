# `.memory-php/04-process.md` — what the manager keeps getting wrong

> ⚠ **`.memory-php/` is the AUTHORITATIVE layer for the PHP programme, and it
> SUPERSEDES any task report it contradicts** (`.tasks/PROTOCOL.md` rule 9).
> Only findings that have survived a full engineer→reviewer cycle are here.
>
> ⚠⚠ **SCOPE: this carries ONLY what is php-specific.** The PAT `.memory/`
> 00–06 applies unchanged — same harness, same bench rules, same measurement
> discipline, same Verus notes. **Do not restate any of it here; two copies of
> one rule is how both go stale.**
>
> The narrative, the open items and findings **F1–F142** live in `RECAP_PHP.md`
> (⚠ this said *F1–F41* for **forty-nine** findings, then *F1–F90* for **eleven** more — `PROTOCOL.md` rule 13, **and it has now rotted THREE TIMES.** ✅ **`.tasks-php/boxcheck.py` CHECKS THIS LINE against the actual highest finding as of 2026-09-13, so it is the last time.**
> **Count it yourself: `grep -c '^### F' RECAP_PHP.md`.**)
> ⭐ **And the statistic decision — which column every row publishes in — is
> `.tasks-php/STATISTICS_001.md`, committed. It was in gitignored `.temp/`.**

---


⚠⚠ **A fixture that exercises one value of the parameter the defect switches on
is blind to the defect's own arm.** `ph03`'s generator emitted length **45
exclusively**, so the benign inputs never took the `floor(len*1.33)` arm the
whole pattern is about — and `45 ≡ 0 (mod 3)` was exactly what hid a real
model/proof divergence for 42 of 63 length bytes. **The generator must span the
parameter that selects the code path the defect lives on.** ⚠ *This phrasing is
from ONE row and is being tested on `ph07`, where the cursor is driven by a
static table rather than a length byte; if it does not cover both, it is wrong.*
  ✅ **Early support, checked against the rest of the batch**: every one of
  `ph12` (the omitted `length` argument that disables the guard), `ph21` (the
  `strlen × mult` residue that decides whether the store narrows), `ph16` (the
  index range straddling `FD_SETSIZE`) and `ph29` (the size straddling the
  `REAL_SIZE` truncation) **has exactly such a parameter**, and in each case a
  single-value fixture would exercise the wrong arm. **Four of five rows fit the
  rule before it was tested on any of them.**

Five failures, all the manager's, all caught by an engineer or reviewer:

1. ⚠⚠ **A refuted mechanism is not a licence for the design it argued
   against.** A reviewer disproved an *asserted* deadlock and said in terms it
   was not recommending the hard failure; the manager asked for the hard failure
   anyway, and it deadlocked the fresh-clone path permanently. **Refuting the
   ARGUMENT for a decision does not establish its opposite.** (F13.)
2. ⚠ **A success condition is part of a design and does not travel with the
   shape of a bug.** *"Show it converges"* was right for the fresh-clone
   deadlock, where repetition **is** the repair, and wrong for the orphan-record
   one, where it never can be. (F19.)
3. ⚠ **A whitelist written from the layouts you INTEND is not a whitelist over
   the layouts that EXIST.** Both whitelists the manager wrote failed on first
   contact: one refused **all 33 built rows** (`__pycache__/`), the other was
   simultaneously insufficient and over-strict. **Run it against the corpus
   before shipping it — it costs one command.** (F18.)
4. ⚠ **A wrong enumeration is not an unboundable one.** Pricing the first as the
   second is how a fixable bug gets priced as a phase. The idiom detector had
   **no** complete enumeration; the row enumeration is one call. (F16.)

5. ⚠⚠⚠ **A rule written for other people is not a rule you have read.** The
   handoff's size box says, in capitals, *"DO NOT ARBITRATE THAT BYTE COUNT — IT
   HAS THREE ANSWERS AND THE DISAGREEMENT IS A DEFINITION, NOT AN ERROR."* The
   manager arbitrated it **four sections below the warning**, on an engineer's
   plausible claim, and was wrong — `check.py:1910` is `11003`. ⚠ **Rule 14 with
   the roles reversed: an ENGINEER premise the manager had no reason to doubt,
   and did not check** — one `grep` would have.

⚠⚠ **And the standing one, which has now landed on three separate documents
including the one that states it: THE CITATION AND THE STORY ABOUT IT ARE TWO
DIFFERENT CLAIMS.** Running the grep does not check the prose. Three citation
defects sat inside the adjudication whose headline exhibit argued that a kill had
priced the wrong frame.

⚠ **Rule 14's shape has fired twice**: a premise stated as fact in a task file is
one an engineer has no reason to doubt, and it **comes back as evidence**. The
*"123 ASan reports"* figure, and the *"~7 000-word `why`"* that motivated **three
successive versions of a size rule** and was never measured (`p01`'s is 2 057).

---

## Landed 2026-09-13 from `TASK_PHP_043` — the process laws the review round settled

6. ⭐⭐⭐ **A FIGURE A VALIDATOR ASSERTS IS COMPUTED FROM THE TREE, OR IT IS NOT
   ASSERTED.** **Four hardcoded figures in `.tasks-php/` validators went stale in
   one session**: `preimage_screen.py`'s `N10e` (*"26/17"*); `task_cost.py`'s `N7`
   (*"total/rows ≈ 6.5"*, stale **three times within the hour** — 6.50 → 6.67 →
   6.83 → 6.00); `citecheck.py`'s `N1` (asserted a defect a task had repaired);
   and `task_cost.py`'s `owed = 34  # floor 40 - built 6` **after `built` became
   7**, which made the tool print `~97` while `RECAP_PHP.md`'s own prose said 33
   rows were owed. ▶ **All four were repaired the same way — computed,
   scale-free, or a capability claim — and `N9` now fails the moment `owed` is
   re-pinned.** ⚠ **The tell is a comment that states the arithmetic**
   (`# floor 40 - built 6`): **it is the derivation, so write it as code.**
   (Items 93, 87, 88; `RECAP_PHP.md` tasks cell.)

   ⭐⭐⭐ **EXTENDED 2026-09-16 BY `TASK_PHP_061` §4.4/§5.0 — from VALIDATORS to
   DOCUMENTS, and from NUMBERS to SETS. Reviewer-landed, covering `F135`,
   `F138` and `F132` at once, and deliberately NOT a new law:**

   > *…and the same applies to a figure a **DOCUMENT** asserts about the tree:
   > if a committed tool prints it, quote the tool's output **and the commit you
   > ran it at**, never a literal. ⚠ **And a tool that prints a SET must be RUN
   > for its set** — calling its function and taking `len()` is not running it,
   > and the count is a valid **tripwire** and an invalid **adjudication**.
   > ⭐ A benign cause does not make a failing arm benign.*

   ⚠⚠ **WHY THIS AND NOTHING ELSE FROM THAT ROUND'S EIGHT FINDINGS.** `_061`
   §5.0 measured **four homes for a trap — a tool docstring, a committed tool's
   output, a handoff finding, and a protocol section IN CAPITALS — and all four
   failed against the text's own author** (`F134`, `F138`, `F132`, and `F139`
   at nine and a half hours). ▶ ***Location is not the variable***, so a law
   about **where traps live** must NOT enter: the general claim *a document is
   not a control* is exactly a fact about people in general. ⭐ **The clause
   above is programme-specific for one reason only — it names an artefact this
   programme has: a committed checker that prints the thing.**
   ⓘ **The durable home for each of those four is an arm in a tool that prints,
   and three of the four already have one.** ⛔ **There is no ratchet rule
   anywhere in this layer to append to** — measured, zero hits across `00`–`04`
   and PAT's `.memory/` — which is why `F135` routes here.

7. ⭐⭐ **A CONTROL CLONED BETWEEN ROWS CARRIES ITS DEFECTS, AND ONLY THE ROW
   THAT WRITES *NEW* NEGATIVES FINDS THEM — FIVE INSTANCES AND ONE SUCCESSFUL
   FORWARD PREDICTION.** The shared `controls/spellings.py` machinery is
   monotone in suite size: **54 cases missed two · 75 missed one · 128 found one ·
   161 found the fourth · and `TASK_PHP_043` found the FIFTH** — the `invariant`
   field's opening clause (*"Every variant is in contract … over EVERY backticked
   idiom entry"*) is **false as written in 5 of 5 php rows**, because
   `required_absent` is non-empty on variants the row ships, **including on R3's
   `v0_shipped`**. ⓘ PAT's two copies do not carry the clause. ⭐ **Item 81
   PREDICTED the fifth before it was found.** ▶ **So budget a new negative suite
   per row and expect a sixth.** (F101, item 89.)

8. ⚠⚠⚠ **A SOUNDNESS TEST CAN BE *NECESSARY AND NOT SUFFICIENT*, AND THAT IS
   INDISTINGUISHABLE FROM SOUND UNTIL SOMEBODY ATTACKS THE DEGENERATE INPUT.**
   `preimage_screen.py`'s `same_function` guard — *the matched hunk must contain
   no function-definition header before its first changed line* — **passed
   VACUOUSLY on a hunk with zero leading context**: with no context there is no
   header to find, so it returned a **proof** from a hunk carrying no evidence.
   ⭐ **That is F95's own headline defect — a soundness test promoting an
   exclusion to a proof — recurring INSIDE F95's repair, written by the manager,
   one round later.** ✅ Live reach 0, so latent. ▶ **Now fails closed, with a
   must-fire negative on the zero-context hunk and a must-not-fire on the same
   hunk with one context line, so it rejects the absence of evidence rather than
   the hunk.** (Item 87.)

9. ⭐⭐ **AUDIT THE *DEGENERATE* INPUTS, NOT THE INTERESTING ONES.** I asked
   whether `citecheck.py`'s `inherited = set.intersection(*per_spec.values())`
   breaks when a row is **ADDED**. It does, and it breaks **loud**, which is safe.
   ▶ **The real hole was the single-row case: the intersection over one set IS
   that set, so every citation classified as *inherited*, ALL of them were
   suppressed, and `N2` still passed** — because its condition (*"present in all
   rows"*) is **vacuously true of one row**. ⭐ **A checker that silently checks
   nothing** (F10's shape). ▶ **So enumerate 0 rows, 1 row, all-identical — the
   inputs nobody finds interesting.** (Item 88.)

10. ⚠⚠ **NAME THE FILE EVERY FIELD CAME FROM — AND THE FINDING WRITTEN
    IMMEDIATELY AFTER THE ONE THAT ESTABLISHED THIS RULE BROKE IT.** F99's lesson
    is that `verus_checked` and `problems` are **not gate-record fields** and a
    reader who looks for them there reasonably concludes the verification was
    invented. ▶ **The very next finding, F100, quoted the twin verdicts `31/0`
    and `32/0` in a paragraph whose other fields came from
    `controls/spellings.json` — where `verus_checked` is a bare `true`, not a
    count. The figures are in the row's `NOTES.md:550` and `:741`.** (Item 84.)

11. ⛔⛔ **A PUBLISHED FINDING WHOSE ONLY EVIDENCE IS A GITIGNORED PROBE IS A
    FINDING THAT WILL NOT SURVIVE A CLEAN CHECKOUT.** F92 answers open item 68
    `NO` in a committed document, and its measurement lives in
    `.temp/php39/width.py` — **gitignored, and its `--selftest` no longer
    completes** (a `ZeroDivisionError` at `X3b`, ⭐ **because its check now passes
    MORE cleanly than the guard expected**). ▶ **The fix is the one F99
    prescribes: commit the probe beside the other checkers.** ⚠ **The same shape
    covers every probe behind every finding in F88–F101.** (Item 86, F99.)

12. ⭐⭐⭐ **THREE REVIEW ROUNDS IN A ROW HAVE REFUTED MANAGER CLAIMS, AND THE
    PATTERN IS STABLE ENOUGH TO PLAN AROUND: A MANAGER FINDING FROM ONE PROBE OR
    TWO ROWS SHOULD BE ASSUMED NARROWABLE UNTIL A REVIEWER HAS HAD IT.**
    `TASK_PHP_038` refuted three (F80/F82/F83/F84's corrections); `TASK_PHP_039`
    refuted F90; `TASK_PHP_043` cost **one published headline and four
    qualifiers** and **refuted the manager's own route to its biggest result**.
    ⚠⚠ **Not one of the corrections across all three rounds was arithmetic.**
    **Every one came from a second method applied to something published from a
    single probe, a two-row sample, or a restatement of a definition mistaken for
    a measurement.** ▶ **The operational consequence: the review round is not
    optional tidying and deferring it compounds** — the backlog went 5 → 14 in
    one round, and rule 9 bars every one of those from this layer while it grows.

✅✅ **CYCLE CLOSED 2026-09-13 BY `TASK_PHP_047`. THE MATERIAL BELOW IS NOW
REVIEWED** — F97/F102/F104 **UPHELD-NARROWED**, F106 **UPHELD and under-stated**,
F105 **REFUTED in its `97.6 %` clause**, F103's decomposition **REFUTED**, F96
**still UNREVIEWED**. ⭐⭐ **Law 12 held: not one of the five survived unchanged**
— which is itself the strongest evidence for law 12 that this programme has.
⚠ **The banner below is kept because the defect it records was the manager's.**

⛔⛔⛔ **EVERYTHING FROM HERE TO THE END OF THIS FILE WAS `UNREVIEWED`, MANAGER, 2026-09-13.**
It comes from `TASK_PHP_044`, `_045` and `_046`, which are **ENGINEER** tasks:
`PROTOCOL.md` **rule 9** requires an engineer→reviewer cycle and **these have had
only the engineer half.** ⭐ It is kept here rather than held back, under the same
convention `02-ladder.md`'s family-B sensitivity paragraph used — **marked, not
hidden** — because a later session needs the rule and the mark tells it what the
rule is worth.
>
⚠⚠ **AND THE MARK IS HERE BECAUSE I LANDED THIS MATERIAL UNMARKED FIRST.** I
wrote the RULE-9 STATE block one day earlier, landed `04-process.md` law 12
(*a manager finding from one probe or two rows should be assumed narrowable until
a reviewer has had it*) — **and then put seven unreviewed entries into the layer
that supersedes everything.** ▶ **Caught by auditing before a handoff, which is
the only reason it is marked at all.** → the RULE-9 STATE block in `RECAP_PHP.md`
names which findings these are and what a review round owes.

13. ⛔⛔⛔ **§H CAN BE SATISFIED BY GITIGNORED EVIDENCE, AND ON FOUR OF FIVE ROWS
    IT WAS.** `PROTOCOL_PHP.md` §H says *a validator change lands with its
    must-fire negatives, or it does not land.* ▶ **If those negatives live under
    `.temp/`, the validator ships and the proof that it can FAIL does not.**
    **Measured: 13 §H-at-risk citations across `ph16`, `ph29`, `ph45` and `ph53`,
    out of 30 `.temp/` citations in 11 committed `controls/*` files.**
    ⭐⭐ **AND `citecheck.py` — the checker that exists to find exactly this —
    scanned `spec.md` + `NOTES.md` only, so it was blind to the layer holding the
    worst instance.** F10's *a checker that silently checks nothing*, third
    instance. ✅ Repaired 2026-09-13 with negatives; the §H subclass is matched on
    the **citing line**, not the path, because the role is what matters.
    ⭐ **THE RIGHT PER-ROW REPAIR IS NOT "COMMIT THE SUITE" BUT "MOVE THE ARMS
    INSIDE THE VALIDATOR"**, so they run on every invocation and feed `problems`
    — then emptying the guarded constant is a **red gate** (stage 9b
    `FRESH+VERDICT-FAILED`), not a better-looking number. (Item 97.)

14. ⛔⛔ **A C KERNEL'S COMMENTS ARE HASHED AT **MEASUREMENT** PRICE, SO
    PROVENANCE PROSE INSIDE ONE IS EFFECTIVELY FROZEN.** `c/*` is in the
    measurement digest, so correcting a *comment* that has aged costs a **32-cell
    re-measure**. **First instance: `ph53`'s `c/kernel_hardened.c:8-9` asserts a
    screen route that F95's own repair withdrew, and it cannot be repaired at
    re-gate price.** ▶ **THE RULE GOING FORWARD: a C kernel comment carries NO
    provenance claim that can age — point at `spec.md` instead.** ⓘ That is what
    the rest of the corpus already does, so it is nearly free. ⚠ **And when one
    is already stuck, say so in the two places that CAN be edited** (`spec.md`'s
    `provenance` note and `NOTES.md`), so a later reader finds it **known** rather
    than undetected. (Item 98.)

15. ⚠⚠ **READ THE BODY, NOT THE PROSE BESIDE IT — AND A LIST OF WHAT A FILE DOES
    **NOT** DO IS NOT A LIST OF WHAT IT DOES.** The manager asserted in a task
    file that `common-php/emalloc_shim.h` *"zeroes fresh blocks and poisons `0x5a`
    on free"*. **Both halves are false**: the `memset(p, 0, …)` is inside
    `php_shim_ecalloc`, where zeroing is the *contract* — `emalloc` does not zero
    — and `0x5a` appears in the header's own **"WHAT IS DELIBERATELY NOT
    MODELLED"** section, as a ZEND_DEBUG behaviour the shim omits **on purpose**.
    ⭐ **Same class as `spelling_matches`'s *a comment is not code*, and the
    SECOND time in one session**: a textual guard written for `width.py` fired on
    the comment documenting the very defect it was written to catch.
    ⚠⚠ **It was a rule-14 premise — a task-file assertion an engineer has no
    reason to doubt — and the engineer checked it anyway, which is the only
    reason it was caught.** ⓘ The corrected reason is **stronger**: the shim uses
    plain `malloc`, so ASan's `0xbe` is a **runtime option default**
    (`ASAN_OPTIONS=malloc_fill_byte=0` gives zeros), not a compile-time property.
    (Item 96.)

16. ⭐⭐⭐ **AN ARM MAY ASSERT AN EFFECT'S *DIRECTION* ONLY TO DEFEND A
    **PUBLISHED** FINDING, AND ONLY IF IT PRINTS THE MEASURED MARGIN BESIDE THE
    FLOOR — AND IT NEEDS A RETIREMENT CONDITION.** A check that asserts the
    direction of something still being **estimated** can only report a changed
    conclusion **as a tool failure**, which is the data being blamed for the
    hypothesis. Three instances are on file: `task_cost.py`'s **`N11`** (the
    first-in-family premium, refuted in sign at `n = 8` after standing on
    `n = 1`), **`N13`** (refuted the day it was written), and **`N5`** (whose
    `not rising` enforced the flat-trend conclusion **that its own file
    produces**). ✅ The model to copy is `width.py` `N4`/`N3b` and `php_null.py`
    `N8`/`N9`/`N7b`: they re-assert a **published** result so the tool speaks
    when it stops reproducing, **and firing is the point.**

    ⛔⛔ **THE SPLIT IS NOT A PROPERTY OF THE ARM. It is a property of the arm's
    RELATION TO A FINDING'S CURRENT STATUS — AND THAT STATUS CHANGES WITHOUT THE
    ARM CHANGING.** `N11` was a textbook defending arm right up to the moment
    the premium was refuted, at which point it became a textbook offending one,
    **with no edit to it.** ▶ **So the margin clause is the whole mechanism, not
    a nicety: an arm that prints its margin turns a refutation into a VISIBLY
    SHRINKING NUMBER instead of a hard failure, which is the transition handled
    safely.** ⭐ ***An arm that asserts a published direction without printing
    the margin is an offending arm that has not been caught yet.***
    ▶ **And every such arm needs a written RETIREMENT CONDITION: a registered
    prediction with no expiry becomes a pin.**

    ⚠ **Scope, stated because the first wording was withdrawn for being too
    broad**: *"an arm must not assert a sign"* would have damaged **five correct
    arms**. ⚠ The sweep behind this covered **four** checkers, 59 arms; **five
    more are unswept** and speak a different arm dialect. (`RECAP_PHP.md` F126,
    F128, item 130; narrowed and landed at `TASK_PHP_059` §4.)
