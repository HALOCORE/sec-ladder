# TASK_PHP_060 — ROW 12: `ph96`, **T6's SECOND ROW, WHICH CLOSES THE FAMILY** — and the first row in this programme with **TWO upstream-attested repairs to price against each other**

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_060_REPORT.md` — **write the FILE** (rule 10).

---

## §0 ⛔ READ FIRST, IN THIS ORDER

1. `patterns-php/CATALOGUE.md` — **`ph96`'s own Part B entry** (search `ph96 ·`),
   and **`ph60`'s**, whose `⚠ risk` note is where T6's three merges were undone.
   ⚠ **§2.5 below finds the `ph96` entry INCOMPLETE. Read it, then read §2.5.**
2. `.tasks-php/TASK_PHP_056.md` **and** `_056_REPORT.md` — **`ph97`, the sibling
   T6 row, and your closest template.** ⭐ **Clone the DESIGN, not the text.**
3. `.tasks-php/PROTOCOL_PHP.md` — §A1 tiers, **§A3a criterion 2 and its
   obligation 5**, §B/§B1a the allocator rule, §B5 family-B publishability,
   **§C R1h**, §E the six-command sequence, §F6/§F6a, §H.
4. `patterns-php/ph97-optarg-unwritten/` — the most recent row, same family.
5. `.memory-php/03-numbers.md` — the **five** things every percentage owes,
   **and `02-ladder.md`'s F74 block: that bar is NOT a gate.**

---

## §1 Why this row

**`T6` is 5 catalogued rows with 1 built** (`python3 .tasks-php/quota.py` →
`T6  5  1  OWES 1`). **`ph96` closes the family**, and T6 is the family whose
thesis is that **one obligation (`I12`, *a fallible call's failure must be
tested*) is failed five different ways**, three of them with the guard *present
and passing*.

⭐⭐⭐ **BUT THE REASON THIS ROW IS WORTH A TASK IS BIGGER THAN CLOSING A FAMILY,
AND I MEASURED IT WHILE SCOPING (§2.2–§2.6).** `ph96`'s repair hardens `I12` **by
removing the output rather than testing it** — and it turns out **both repair
strategies were already written, correctly, in the same file, by the same
author, before the bug was reported.** ▶ **This is the first row that can price
TWO upstream-attested C-side repairs of ONE obligation against each other.**
Every other row in the programme has exactly one R1h.

⚠⚠ **THE COST OF PICKING IT, STATED SO IT CAN BE HELD AGAINST ME: the temporal
axis stays at ONE built row while 15 of the 26 owed rows are temporal.** ⛔ **And
the ground that was used to defer temporal rows before is REFUTED AND INVERTED**
(`_057` §3.2): executed reproducers fault on **78.6 % of type rows, 58.5 % of
spatial, 38.7 % of temporal**, so §A3a's oracle helps a *type* row about twice as
much as a temporal one. ▶ **Waiting does NOT make a temporal row cheaper. ROW 13
IS TEMPORAL, and it should expect §A3a criterion 2 to read `NO CLI REPRODUCER`
more often than not and to lean on ASan/Miri instead.** That is a METHOD
consequence to plan for, **not** a reason to defer again (`CLAUDE.md` rule 6).

---

## §2 THE MANAGER'S DECISIONS, AND THE FACTS BEHIND THEM

> ⚠ **`PROTOCOL.md` rule 14: a premise in a task file is one an engineer has no
> reason to doubt.** Everything in §2.1–§2.6 was measured by me on 2026-09-15
> from the pinned tarball (`sha256 5783e0c0…d6919`, re-verified byte-exact) and
> from the 5.0.0 CLI. **Re-run anything you depend on** — but you are
> *building*, not re-deriving.

### 2.1 ⭐ THE MECHANISM, QUOTED FROM THE PRISTINE TARBALL

```
Zend/zend_object_handlers.c
 506  static void zend_std_unset_dimension(zval *object, zval *offset TSRMLS_DC)
 507  {
 508  	zend_class_entry *ce = Z_OBJCE_P(object);
 509  	zval *retval;
 510  	
 511  	if (instanceof_function_ex(ce, zend_ce_arrayaccess, 1 TSRMLS_CC)) {
 512  		zend_call_method_with_1_params(&object, ce, NULL, "offsetunset", &retval, offset);
 513  		zval_ptr_dtor(&retval);
 514  	} else {
```

and the callee that guarantees the sentinel:

```
Zend/zend_execute_API.c
 592  	/* we may return SUCCESS, and yet retval may be uninitialized,
 593  	 * if there was an exception...
 594  	 */
 595  	*fci->retval_ptr_ptr = NULL;
 ...
 870  	if (EG(exception)) {
 871  		zend_throw_exception_internal(NULL TSRMLS_CC);
 872  	}
 873  	return SUCCESS;
```

and the dereference:

```
Zend/zend_execute_API.c
 384  ZEND_API void _zval_ptr_dtor(zval **zval_ptr ZEND_FILE_LINE_DC)
 389  	(*zval_ptr)->refcount--;
```

**All line citations verified exact against the tarball.** ⭐⭐ **The C author
wrote a comment naming this exact hazard, then wrote a defensive unconditional
NULL-store at `:595` to make the hazard *detectable* — and `:513` does not
detect it.** `I12/O1` names the case verbatim: *"a NULL return, sentinel, status
code, **or NULL-able out-parameter** must be tested"*; `I16/O2` is *"the outputs
of an aborted call must not be … destroyed"*, which is the `zval_ptr_dtor` half.

### 2.2 ⭐⭐⭐ THE 2×2 THE CATALOGUE ENTRY DOES NOT MENTION — **MEASURED, NOT ARGUED**

`zend_object_handlers.c` calls the **same helper** from **four** ArrayAccess
handlers. I ran all four against the 5.0.0 oracle under the `segaddr` shim:

```
$ sh .tasks-php/probes/ph96_arrayaccess_matrix.sh
HANDLER        SITE   CONTRACT                   RC      FAULT
offsetGet      :384   output + GUARD :385        rc=255  none   ok
offsetSet      :413   NO-OUTPUT (NULL)           rc=255  none   ok
offsetExists   :427   output, UNGUARDED          rc=139  0x14   ok
offsetUnset    :512   output, UNGUARDED          rc=139  0x10   ok
benign(none)   --     nothing throws             rc=0    none   ok
```

- `rc=255` is PHP's **own** `Fatal error: Uncaught exception` — the **correct**
  behaviour, not a silent wrong answer. I checked the text, not just the code.
- `0x10` = `offsetof(zval, refcount)`; `0x14` = `offsetof(zval, type)`. **Both
  follow from `Zend/zend.h:287-293` on LP64** — the `zvalue_value` union is 16 B
  because `zend_object_value` is `{zend_object_handle handle; zend_object_handlers *handlers;}`.
  ⭐ **The offsets were computed from the struct BEFORE the run and matched.**
  ▶ **So the fault address alone says WHICH site ran.**

⭐⭐⭐ **BOTH CORRECT SPELLINGS AND BOTH WRONG SPELLINGS ARE IN ONE FILE.** `:385`
is `if (!retval)` — the output contract, guarded, **2 lines after** an identical
call. `:413` passes `NULL` — the no-output contract, **99 lines before** `:512`.
▶ **The 2005 repair did not invent a strategy; it copied the sibling.**

### 2.3 ⭐⭐ AND THE NO-OUTPUT CONTRACT WAS ALREADY SUPPORTED IN 5.0.0, WITH THE VERY TEST `:513` OMITS

```
Zend/zend_interfaces.c
  48  	fci.retval_ptr_ptr = retval_ptr_ptr ? retval_ptr_ptr : &retval;
  ...
  88  	if (!retval_ptr_ptr) {
  89  		if (retval) {
  90  			zval_ptr_dtor(&retval);
  91  		}
  92  		return NULL;
  93  	}
```

**`:89 if (retval)` is the NULL test `:513` is missing, written by the same hand,
in the function being called.** ▶ **The helper offers two contracts, one of which
CANNOT be misused, and it already disposed of the value correctly on that path.**

⭐ **CENSUS, and it is a real denominator.** 23 real `zend_call_method*` call
sites in 5.0.0 (26 grep hits − 3 macro definitions in `zend_interfaces.h`):
**7 already take the no-output contract** (`spl_engine.h:46`/`:56`,
`spl_iterators.c:967`, `zend_object_handlers.c:413`, `zend_objects.c:78`,
`zend_interfaces.c:228`/`:239`), **16 take the output contract.** ▶ **Re-derive
this yourself if you cite it; it is a one-line grep and I want it checked.**

### 2.4 ⛔⛔ THE R1h **BINDS BUT DOES NOT APPLY.** IT NEEDS A 3-LINE BACKPORT, AND I VERIFIED THE BACKPORT IS UPSTREAM'S OWN CHANGE

```
From cf020f133487d36a8b1d9cfd16ec456f7f07952e
Marcus Boerger, Sat 19 Mar 2005 15:06:39 +0000 — "- Fix #31185"
 Zend/zend_object_handlers.c | 4 +---

-	zval *retval;
-	zend_call_method_with_1_params(&object, ce, NULL, "offsetunset", &retval, offset);
+	zend_call_method_with_1_params(&object, ce, NULL, "offsetunset", NULL, offset);
-	zval_ptr_dtor(&retval);
```

Measured by me in a standalone `git init` repo over the pristine file:

- ✅ **The patch BINDS** — its `From` sha matches its filename. It is **not** one
  of **F115**'s three mis-bound cached patches. **Check yours the same way; do
  NOT re-fetch** (the standing rule on the cache is *report, do not guess*).
- ⛔ **`git apply --check` → `rc=1`, and also `rc=1` at `-C1` and `-C0`.** The
  patch's pre-image carries `SEPARATE_ARG_IF_REF(offset);` and
  `zval_ptr_dtor(&offset);` — **two context lines that did not exist in 5.0.0.**
  They are an unrelated later change. ⚠ **`ph55` NOTES §5's trap fired on me
  here**: my first run printed `EXIT=0`, which was `head`'s status, not
  `git apply`'s. ▶ **Take the verdict from the BYTES.**
- ✅ **The 3-line hand backport reproduces upstream's diffstat EXACTLY**:
  `1 file changed, 1 insertion(+), 3 deletions(-)` against the commit's own
  `Zend/zend_object_handlers.c | 4 +---`. ▶ **So the semantic change is
  upstream's; only the context is not.** **§C requires you to declare it as a
  BACKPORT, with that diffstat as the evidence it is faithful.**
- ✅ **`preimage_screen.py --row ph96 --verbose` → `CANDIDATE`, 1 record.**
  ⚠ Quote it as a **CANDIDATE**, the screen's *positive* label. **Cite 0
  exclusions, not 0** (F68/D11).

⭐⭐ **OBLIGATION 5 IS CHEAP AND I AM REQUIRING IT.**
`.tasks-php/probes/rebuild_hardened_php.sh` builds 5.0.0, applies a row's R1h,
rebuilds and re-runs the trigger — **30 s cold, 683 ms incremental, no sudo, no
network** (F123). It is **pinned to `ph97`'s patch path; edit step 4.** ▶ **Prove
the backport actually removes the fault. Do not assume it.**

### 2.5 ⚠⚠ THE SECOND LIMB — `:427-429` — IS REAL, IS UNDOCUMENTED, AND HAS **NO CACHED REPAIR**

`zend_std_has_dimension` at `:427` has the **same defect**, and it derefs the
NULL **twice**: `:428 result = i_zend_is_true(retval);` (at `0x14`) and then
`:429 zval_ptr_dtor(&retval);`. **The catalogue's `ph96` entry names only
`:509`/`:512-513`.**

⭐ **Measured across all 163 cached patches, by diff BODY:**

| limb | repair in the cache |
|---|---|
| `offsetunset` `:512-513` | **`cf020f133487`, uniquely** |
| `offsetexists` `:427-429` | ⛔ **NONE** |

⚠⚠ **STATE THE SCOPE WHEN YOU CITE THAT.** It is the **163-patch screened
corpus cache**, not php-src's full history. **"No repair in the cache" is a
result (F10); "upstream never fixed it" is a claim this box cannot support.**

> ⚠ **TWO METHOD TRAPS BIT ME HERE AND THEY WILL BIT YOU.** (a) I first read the
> **`@@ … @@` hunk-header function label** as "this patch touches that function"
> — **it names the function the hunk STARTS AFTER**, and `235e6c0afe1d` looked
> like an `unset_dimension` repair and is a `call_user_call` one. (b) I then ran
> a compound `grep -al 'A\|B'` and attributed the hit to `A` when it matched
> `B`. ▶ **Both are *a check that reads prose and calls it code* (item 115's
> class). Read diff BODIES, and never attribute a compound match.**

▶ ⭐ **MANAGER'S DECISION: the row models the CONTRACT, not the site.** Build
**one** kernel implementing the helper plus **all four consumer shapes**; the
2×2 then lives inside the measured artefact at near-zero extra cost, because
they share the callee. **Do NOT build two rows.** ⚠ **If the build says this is
the wrong call, overrule me with the measurement and say so.**

### 2.6 ⭐⭐⭐ THE ROW'S NEW LADDER QUESTION: **PRICE BOTH REPAIRS**

Every other row has one R1h. This one has **two strategies, both attested in the
vulnerable file**:

| | strategy | C-side spelling | attested at |
|---|---|---|---|
| **R1h-noout** | **remove the output** | pass `NULL`, delete the local and the dtor | `:413`, **and upstream's `cf020f133487`** |
| **R1h-guard** | **test the output** | `if (!retval) { … }` before use | `:385` |

▶ **Build the upstream one as the row's `kernel_hardened.c` (that is what §C
means by R1h), and the other as a `controls/` entry with its own measurement.**
**Report both costs with both C columns.** ⭐ **Either answer is a result**: if
removing the output is cheaper, the row says *the unmisusable contract is also
the faster one*; if it is dearer, it says *safety-by-construction had a price
here and upstream paid it*. **Do not predict which and then find it.**

### 2.7 THE KERNEL — the blob, the fold, and the allocator

- **Blob** (the catalogue's own words): *"a call-outcome stream carrying
  `(status, wrote_out)` **independently**."* ⛔⛔ **THE TWO FLAGS MUST BE
  INDEPENDENT.** *"A kernel that derives `wrote_out` from `status` has deleted
  the mechanism and rebuilt `ph60`"* — that is the catalogue's own `⚠ risk`
  note, and it is the single easiest way to fail this row. ⭐ **The whole point
  is that `status == SUCCESS` and `wrote_out == false` co-occur**; that is what
  `:592-595`'s comment says in English.
- Add a third independent field for **which of the four consumer shapes** the
  record drives (§2.5's decision).
- **Benign fold**: `u64` over `(status, wrote_out, shape)` per call plus the
  count of each outcome. **Ordinary calls write the output and it is released
  exactly once.**
- ⚠ **§B1a: keep allocations O(1) per kernel call** so A1/B1 agree (item 78).
  The `zval` here is a fixed-size record; **do not model the allocator**.
- ⛔ **Make `small.bin` and `large.bin` GENUINELY DIFFERENT SIZES.** `ph64`
  shipped both at **9 bytes** — one alignment draw sampled twice — and it
  silently weakened every two-input argument that row made (F119/M4).

### 2.8 TIER, STATISTIC, AND THE PREDICTIONS

* **TIER** — the catalogue says `narrowed`. ⚠ **That is a mining-wave label and
  `ph55` REFUTED its own.** ▶ **Declare what you measured** (§A1).
* ⭐⭐⭐ **`inside_share` PER CELL AS A MATRIX, BEFORE the statistic is chosen.**
  ⛔⛔ **A HIGH SHARE IS NOT A CERTIFICATE AND F74's TWO-CONDITION BAR IS NOT A
  GATE** — `_059` settled this and **four documents said so before it**. On
  `ph55`, `c-gcc` vs `c-gcc-h` the bar **ADMITS** a pair where A1 reads exactly
  `+0.0000 %` against a 66.14 `Ir`/call whole-program difference; on `ph03` it
  **REJECTS** the `unsafe`-vs-`verus` pair whose true A1 difference is **known
  to be exactly 0**. ▶ **Use the share to EXPLAIN a disagreement. Never to
  withhold a column.**
* ⚠⚠ **TWO quantities wear the name `inside_share`** (F129) — F74's
  (`kernel_exclusive_ir/n_iters ÷ marginal_ir_per_call`) and the `W` one
  (`kernel exclusive Ir ÷ callgrind summary total Ir`). **Label which you mean,
  every time.**
* ⛔⛔ **EVERY PERCENTAGE OWES FIVE THINGS: STATISTIC · INPUT · OPT/MODE · BASE ·
  and if the base is a C cell, WHICH COMPILER — with BOTH C COLUMNS, or an
  explicit statement that only one was measured** (F108). **One column is not a
  number with error bars; it is a DIFFERENT SIGN** — on `ph29` the same figure
  is `+33 %` under `c-gcc` and `−4.36 %` under `c-clang`. **Never quote an `O0`
  figure as a performance result.** ▶ Run `.tasks-php/cbaseline_check.py
  --ratchet` before finishing; **adjudicate any new hit BY HAND, never widen the
  regex**, and **adjudicate the SET by unit text, not the count**
  (`cbaseline_diff.py`, F132).
* ⛔⛔ **ANY FAMILY-B FIGURE IS BOUND BY §B5**, with **two verdicts per pair**:
  *magnitude resolvable?* and *sign stable?* `.tasks-php/php50_align_sweep.py`
  does it with no build and no gate. ⚠ **`_055` found §B5's `iff` ARGUMENT to be
  a non-sequitur while its measurement stands — apply the rule, do not repeat
  its justification as established.**

**PREDICTIONS, REGISTERED.** ⚠ **Eight consecutive review rounds have refuted
manager or engineer claims; in `_059` FIVE of my claims fell, including both
load-bearing halves of the finding the round was convened for. That is the
expected yield — score these honestly, either way.**

1. ⭐⭐ **P1 — R1h-noout IS CHEAPER THAN R1h-guard**, because it deletes a store,
   a branch and a call where the guard only adds a branch. ▶ **Falsifier: any
   `O3/isolated` cell where guard ≤ no-out, on either input, with both C
   columns.** ⓘ If it holds, **this is the row's headline**: *the contract that
   cannot be misused is also the cheaper one.*
2. **P2 — R2 AND R3 CANNOT REPRODUCE THE DEFECT AT ALL**, because a safe-Rust
   translation returns a value (`Option<T>`/`Result`) rather than writing
   through an out-parameter, so *"SUCCESS but unwritten"* is **unrepresentable**.
   ⚠⚠ **`CLAUDE.md` rule 6: that is a FINDING, NEVER A PROBLEM.** ▶ **But say
   WHICH safe behaviour you built and why**: an R2 mirroring the C's control
   flow with `.unwrap()` **panics** (a detected fault); one that handles `None`
   has **deleted the bug**. **Both are legitimate and they are different rows of
   the ladder's *does the defect survive?* column.** ▶ **Declare the choice and
   its ground in `spec.md`.**
3. **P3 — R5's obligation is `I12/O1` stated directly** as a precondition on the
   release accessor, discharged from the helper's post-condition, at **zero
   run-time cost**. ▶ **Falsifier: any R5 cell differing from R4 at `O3`.**
4. **P4 — the R1h does NOT apply as-is and the 3-line backport is semantically
   upstream's** (§2.4, already measured; scored for the record).
5. **P5 — stage 7h will have something to say**, as it did on `ph97`: the
   hardened build turns a **crashing** input into a **clean fatal**, which
   changes benign output on an input that previously died. ▶ **If 7h refuses
   this row, F43/F47 applies: a gate stage that refuses your row is a hypothesis
   about your row first. Report it; do NOT edit the gate.**

---

## §3 TRAPS

1. ⛔⛔⛔ **A LIVENESS CHECK MAY NOT BE TRUNCATED AND MAY NOT MATCH ITSELF**
   (item 113). `pgrep` feeding a decision gets **no `head`, no `tail`** — a
   truncated one raced `ph55`'s gate against itself. ▶ **Confirm
   `/proc/<pid>/cmdline` for an exact PID; best of all, need no `pgrep`.**
   ⛔ Never `pkill` / `killall` / substring-match. Prefer `timeout <N> <cmd>`.
2. ⚠⚠⚠ **`grep -a` ALWAYS** (F35). A line-grep misses a phrase that wraps.
3. ⛔ **F101 / item 109 — `kernel_fingerprint` is PATH-SENSITIVE and fired LIVE
   in BOTH directions on `ph52`.** ▶ Clone `ph52`/`ph55`'s repair: fixed-width
   `vNN` slug, asserted equal-path-length invariant, `asm.py::identity_level`.
   ⓘ **Suggested row directory: `ph96-outparam-unwritten`** — same length class
   as `ph97-optarg-unwritten`, which keeps the sibling comparison path-stable.
4. ⛔⛔ **A BACKTICK IN AN `idiom.required`/`forbidden` ENTRY IS A PIN** (item
   100, three instances in three tasks). **Run `spellings.py --audit-only` on any
   contract prose BEFORE quoting it, and read the output.**
5. ⛔⛔ **§H: a validator lands with its must-fire negatives INSIDE it**, feeding
   `problems` so stage 9b sees them. ⚠ **Never in gitignored `.temp/`.**
   ⭐ **If a checker is a grep, ADJUDICATE hits by hand and RATCHET.**
   ⛔ **A registry with no count literal IS the ratchet** — **a bound is not a
   derivation.** ⓘ `.tasks-php/checkers.py` is at **29 filed / 29 on disk**;
   **if you add a `.py` or `.sh` under `.tasks-php/`, FILE IT** — it globs both,
   and it caught my new probe within a minute of my writing it.
6. ⚠⚠ **A `c/*` COMMENT MAY POINT AT AN ARGUMENT; IT MAY NOT STATE THAT
   ARGUMENT'S VERDICT** (§F6a). ▶ **§2.4's `CANDIDATE` sentence, §2.5's
   scope caveat and §2.6's two-strategy note go in `NOTES.md`, which is
   gate-only. `c/*` is the MEASUREMENT digest and costs 32 cells to repair.**
7. ⛔ **A `spec.md` / `NOTES.md` MUST NOT CITE `.temp/`** (§F6) — cite the
   committed probe. ⭐ **`.tasks-php/probes/ph96_arrayaccess_matrix.sh` and
   `probes/segaddr.c` are committed; cite THOSE, never the workdir or the `.so`
   you build from them.**
8. ⚠ **`.temp/php96/` only — never `/tmp`.** Keep the generator, delete the
   artefact; if a blob has no script that rebuilds it, write one.
9. ⚠ **A comment is not code.** Test behaviour, not text. ⓘ **On this row the
   comment at `:592-594` is unusually load-bearing as EVIDENCE OF INTENT — quote
   it as the author's stated hazard, never as proof of runtime behaviour.**
10. ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY for writing.**
    ⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`,
    `pilot/`, `common-php/`.** ⚠ **No `git add` / `git commit`.** Never touch
    `.web/` — a concurrent session owns it.
11. ⛔ **QUOTE A RE-GATEABLE READING AS AN EVENT, NEVER A STATE** (F119/M2).
    *"`contract_sha256` was `X` at commit `Y`"*, never *"`contract_sha256` is
    `X`"* — two such quotes went stale inside one round.
12. ⛔ **WHEN YOU REPAIR A DEFECT FOUND IN ONE PLACE, CHECK EVERY PLACE THAT
    SHARES THE ARTEFACT.** `_059` named `ph16`'s Δshare table; `ph03` and `ph29`
    carried the same table with the same two defects and were missed for a day.
13. **Brackets**: `harness/measure.py --check-stale` → **`66/0`** (must NEVER
    move); `harness-php/gate.py --tool measure --check-stale` → **`24/0` before
    you start, `26/0`** once this row's two records land. **Quote first and
    last.** ⓘ Both were green at `HEAD` when this file was written.

---

## §4 DEFINITION OF DONE

1. ⭐⭐⭐ **§2.2's MATRIX RE-RUN AND RECORDED AS AN EVENT** — all four cells, both
   fault addresses, the benign control, the binary named, **both §A3a cautions
   repeated in `NOTES.md`** (oracle build ≠ museum default; a clean run is not
   evidence of absence, F3). **If it does not reproduce, that is the headline
   and the task stops there.**
2. **The row built at all five rungs + R1h**, gated, verdict quoted **from the
   gate record, named**.
3. ⭐⭐ **§2.6's SECOND repair built as a `controls/` entry and PRICED**, with
   both C columns. **No extra rung, no extra gate.**
4. ⭐⭐ **§2.4's obligation 5 discharged**: the backport rebuilt and the trigger
   re-run against both builds, showing the fault gone. **Declare it a BACKPORT
   and give the diffstat evidence.**
5. ⭐ **§2.7's independence honoured**: `status` and `wrote_out` independent in
   the blob. **Show the input where `status == SUCCESS` and `wrote_out == false`
   together**, and the one where the call genuinely fails.
6. ⭐ **§2.5 recorded in `NOTES.md` WITH ITS SCOPE** — the second limb, its
   distinct fault address, and *"no repair in the 163-patch cache"* stated as a
   cache result and **not** as a claim about upstream.
7. **`inside_share` per cell as a matrix, BEFORE the statistic is chosen**;
   **which of the two quantities you mean, labelled**; both statistics labelled;
   **both C columns on every cross-language figure**; any family-B figure
   cleared through §B5 with **two verdicts**.
8. **The five §2.8 predictions scored, either way, by name.**
9. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** `UNTESTED` and *"I could
   not tell"* are valued answers, and they are what the reviewer reads first.
   ⚠ **If you route a question to the manager, put it HERE and say so in the
   report's headline** — `_059` found a routed ruling request buried in a row's
   `NOTES.md` that I never answered and then contradicted in print.
10. **Brackets quoted first and last.**
11. ⛔ **If a prediction survives, say so plainly. Do not manufacture a
    refutation to have something to report.**
12. ⚠ **If you stop mid-row, stop CLEANLY and write a `§N ORDER TO RESUME IN`**
    — `_051` did exactly that and `_052` finished the row from it. **A
    task-notification means STOPPED, not FINISHED** (item 118).
