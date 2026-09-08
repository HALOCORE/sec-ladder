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
> The narrative, the open items and findings F1–F41 live in `RECAP_PHP.md`.

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
