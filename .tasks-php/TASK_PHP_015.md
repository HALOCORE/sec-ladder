# TASK_PHP_015 — fix the template, then build `ph07`

**Role:** research engineer. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_015_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md`, **`.tasks-php/TASK_PHP_014_REPORT.md`** (the review
you are landing), `.tasks-php/TASK_PHP_013_REPORT.md` (how `ph03` was built —
your model for `ph07`), `.tasks-php/PROTOCOL_PHP.md`, `PLAN_PHP.md` §3–§6, and
`patterns-php/CATALOGUE.md` (`ph07`, Parts A and B).

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **`.web/` belongs to a CONCURRENT SESSION — never `git add -A`.**

**Bracket**: `harness/measure.py --check-stale` → `66/0` and
`harness-php/gate.py --tool measure --check-stale` → **`4/0`**, first and last.

---

## §0 Order matters: TEMPLATE FIRST, THEN THE ROW

`ph03` **survived its review** — R5's postcondition is genuinely strong, 17 of
19 mutants killed. **The row is good. Its SHAPE has one real defect, and ninety
rows would copy it.** So: land M1 and the tier clause **before** building
`ph07`, and let `ph07` be the first row built on the corrected template.

⚠ M1, M3, M4 and the row's minors **all cost a re-gate anyway** — batch them
into **one** re-gate, not three (`PROTOCOL.md` rule 6).

## §1 M1 — the model does not mirror the proof, and the fixture hides it

`spec.md:215` — **inside the hashed contract block** — claims `model.py::uu_fold`
mirrors `verus.rs`'s walk. **It does not:**

- `verus.rs:215-223` folds the **first `total_len`** emitted bytes;
- `model.py:245-255` folds **every** emitted byte (all `p`).

Equal only when `total_len == p`, i.e. **only at multiples of 3** — strict for
**42 of 63** length bytes. ⚠⚠ **The row's own `lemma_emit_covers_declared`
proves `ln <= 3*ceil(fl/4)` and `verus.rs:47-48` says equality holds only at
multiples of 3 — so the row's Verus lemma documents that its model's stated
justification is false.** `model.py:294-298` names `<=` where sameness needs `==`.

**Fix all three parts. The third is the one that generalises:**

1. **Make them agree**, and say which was right and why — `verus.rs` is what R5
   proves, so the burden is on `model.py` to match it unless you can show
   otherwise.
2. **Correct `spec.md:215` and `model.py:38-40`.** ⚠ `spec.md`'s claim is inside
   the hashed contract, so this moves `contract_sha256` — expected, disclose it.
3. ⚠⚠⚠ **FIX THE FIXTURE, AND THIS IS THE TEMPLATE RULE.**
   `inputs/gen.py:80` emits **length 45 exclusively**, calling the padding case
   *"dropped"*. But the defect is `ee = s + (len == 45 ? 60 : (int) floor(len *
   1.33))` — **so the benign fixture never once takes the `floor()` arm the
   whole pattern is about**, and `45 ≡ 0 (mod 3)` is exactly what hides M1.
   ⚠ **Real uuencoded data has a short final line**, so the monoculture is also
   *unfaithful*.

   **→ The generator must span the parameter that selects the code path the
   defect lives on.** Make it emit short final lines, and **add a must-fire**: an
   input on which the pre-fix `model.py` and `verus.rs` disagree, which the fixed
   pair agrees on. **State the rule in `PROTOCOL_PHP.md` so `ph07` and the other
   89 inherit it.**

⚠ Changing `inputs/` moves the input hashes → a re-measure. Budget it.

## §2 The rest of `TASK_PHP_014`

- **M3** — `NOTES.md:795` states the refuted `norel` as the shipped O0 identity
  level; the pin is `differ`, and `NOTES.md:26-31` says so. **Rule 13's shape:
  when you correct an item, re-read its header.**
- **M4** — §8b's **−3.0 `Ir`/line is right** (the reviewer reproduced it two
  ways) but the account is partial: the epilogue saves **9**, the new checks
  cost **6**, net −3. **Only 5 of the 9 are named and the cost side is never
  mentioned.** Complete it.
- **M5 is a RESULT, not a defect** — **2004 hunk 1 is provably redundant**
  (Verus still 25/0 with it deleted from exec *and* with it neutralised in the
  spec; all 1 953 C firings also refused by hunk 2). **Write it into
  `NOTES.md` §5 as part of the row's headline: of a two-hunk fix, one hunk is
  dead and the other incomplete.**
- **M6** — soften the ASan limb: allocated as PHP's `emalloc` really allocates
  (`ALIGN8(len+1)`) **ASan is silent**. Say *"a detector fires under this
  allocator"*, not *"PHP faults"*. ⚠ **Limbs 1 and 3 are allocator-independent
  and the finding stands** — do not over-correct.
- **The tier clause.** `verbatim` **survives** the `-lm` substitution, but
  `PROTOCOL_PHP.md` §A1 defines the tier purely by *removal* while this row
  *adds* two definitions. **Add the clause §A2 already implies: a substitution
  demonstrated behaviour-preserving is admissible.** ⚠ **And rename the
  `deletions` ledger** — 3 of `ph03`'s 4 entries are not deletions.
- The seven minors.

⚠ **M2 is ALREADY HANDLED — do not land it.** The manager's `F32` was the false
claim; `check.py:1910` is `NAMED_SPELLING_LEN = 11003` and `PROTOCOL_PHP.md` §E
is **correct**. `RECAP_PHP.md` F32 is retracted. **Change nothing in §E.**

## §3 Then build `ph07`

**`ph07` — `mbfl_strcut`, `ext/mbstring/libmbfl/mbfl/mbfilter.c:1202-1210`,
CRASH-124.** Tier **`narrowed`** — ✅ verified at source by `TASK_PHP_012`:
`for(;;)` with `m = mbtab[*p]` and **no consultation of `string->len`**.
`mbfl_string` reduces to `{val,len}`; `mblen_table` is a static array.

**Why this row is next, and what it is the first of:**
- **the first `narrowed` extraction** — the first real test of the tiers *and*
  of `provenance.py`'s overlap report at the 25 % expectation;
- **the second `DP-07` pointer cursor** — the idiom the census found in all 22
  corpus programs and **zero** of the 33 PAT kernels;
- **one of `F27`'s three recoveries** — it was killed by the same sentence as
  `CRASH-123`. **Building it validates that recovery.**

Follow `ph03`'s shape: extraction from the **pinned tarball**, a `provenance`
block, R1h from the **real** `fix_commit`
(`https://github.com/php/php-src/commit/<sha>.patch` — `git fetch` of a bare SHA
is refused; keep the patch bytes under the row), five rungs, gate, measure.

⚠ **`ph07` has no `-lm` problem, so it is also a clean test of whether the
`verbatim`/`narrowed` machinery works without that complication.**

## §4 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php15/`. **Never `/tmp`.** ⚠ `.temp/php12–14/` hold
  `ph03`'s harnesses and the reviewer's mutant driver — **reuse them.**
- ⚠ **Citations resolve against the PINNED TARBALL only** (`SOURCES.md`).
- ⚠ **`env -u LD_PRELOAD`** for hand-run sanitizer probes; grep
  `AddressSanitizer`, not `ASan`.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`. ⚠ **Two agents in a row have had `pgrep -f` match their
  own poller shells and report a finished gate as running.**
- Everything claimed must have been **RUN**, output pasted.

## §5 The calls I am least sure of

1. ⚠⚠ **That the fixture rule generalises the way I have written it.**
   *"The generator must span the parameter that selects the code path the defect
   lives on"* is my phrasing from one row. **For `ph07` — where the cursor is
   driven by a static `mblen_table` rather than by a length byte — does it even
   apply?** If it does not, **the rule is wrong and I want the version that
   covers both**, not an exception.
2. ⚠ **That `ph07` is the right second row.** It was chosen for coverage
   (`narrowed` × cursor × an F27 recovery). ⚠ **If the `narrowed` machinery
   turns out to be the hard part, a second `verbatim` row first would have been
   the safer order — say so** rather than pushing through.
3. ⚠ **That batching the template fix and a new row in one task is right.** It
   validates the fix immediately, and it also makes one task big. **If it is too
   big, stop after §2 and report** — I would rather run an extra task than get a
   rushed row.

---

**Running count: launched from 74.** `TASK_PHP_014` upheld `ph03`'s headline
under every attack and **strengthened it** (M5: half the 2004 fix is dead), gave
**fourteen clean negatives**, and caught the manager writing a **false
refutation into the state layer** — arbitrating the one byte count this
programme's own handoff says must not be arbitrated. **Reconciliation is the
manager's job** — state what you refute and let the manager carry it.
