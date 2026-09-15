# TASK_PHP_056 — ROW 11: `ph97`, **T6's FIRST ROW** — and the first row in this programme whose criterion 2 is **MEASURED, NOT ARGUED**

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_056_REPORT.md` — **write the FILE** (rule 10).

---

## §0 ⛔ READ FIRST, IN THIS ORDER

1. `patterns-php/CATALOGUE.md` — **`ph97`'s own Part B entry** (search `ph97 ·`),
   **and `ph60`'s**, whose `⚠ risk` note is where T6's three merges were undone.
2. `.tasks-php/TASK_PHP_054_REPORT_S4S5S6T2T4T6.md` — **§2.6 (`ph97` deep
   verification)**, **§1.1** (the `ph96`–`ph102` fixsurvey gap), **§3** (cost
   verdicts), **§4** (why T6 first). ⭐ **That report is why this row is next.**
3. `.tasks-php/PROTOCOL_PHP.md` — **§A3a (NEW, and this row is its first
   customer)**, §A1 tiers, §B/§B1a the allocator rule, §B5 family-B
   publishability, §C R1h, §E the six-command sequence, §F6/§F6a, §H.
4. `patterns-php/ph56-fetchmode-arith/` and `patterns-php/ph55-opdata-stride/` —
   **the two most recent rows and your closest templates.** ⚠ **Clone the
   DESIGN, not the text.**
5. `.memory-php/03-numbers.md` — the **five** things every percentage owes.

---

## §1 Why this row

**`T6` is 5 catalogued rows with 0 built** (`python3 .tasks-php/quota.py`), so it
is the **largest untouched family in the corpus** and the only one where a
second row can close it outright. `TASK_PHP_054` screened 13 empty families with
three agents, killed nothing, and **two of the three independent picks were T6
or adjacent**; agent C, who held T6, called it *"the best family I screened and
I believe it beats every `E` family"*.

⭐ **`ph97` is the cheapest row in the corpus by a distance**: one line of C is
the upstream fix, one line of PHP is the trigger, and — measured below — the
crash is **deterministic and the fault address is `(nil)`**.

⚠⚠ **THE COST OF PICKING IT, STATED SO IT IS NOT HIDDEN.** The temporal axis
stays at **one built row** while **15 of the 30 owed rows are temporal**. That
was overruled on one ground only: **F116/§A3a lowers the cost of a temporal row
too**, because the expensive part of a temporal row is establishing that the
C really faults, and that is now an executable question. ▶ **Row 12 is `ph96`
(closes T6); row 13 SHOULD be temporal.**

---

## §2 THE MANAGER'S DECISIONS, AND THE FACTS BEHIND THEM

> ⚠ **`PROTOCOL.md` rule 14: a premise in a task file is one an engineer has no
> reason to doubt.** Every fact in §2.1–§2.4 was measured by the manager on
> 2026-09-15 from the pinned tarball (`sha256 5783e0c0…d6919`) and from the
> 5.0.0 CLI. **Re-read any you depend on** — but you are *building*, not
> re-deriving.

### 2.1 ⭐⭐⭐ THE MECHANISM, QUOTED FROM THE PRISTINE TARBALL

```
ext/mbstring/mbstring.c
3209  PHP_FUNCTION(mb_get_info)
3210  {
3211  	char *typ = NULL;
3212  	int typ_len;
3213  	char *name;
3214
3215  	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "|s", &typ, &typ_len) == FAILURE) {
3216  		RETURN_FALSE;
3217  	}
3218
3219  	if (!strcasecmp("all", typ)) {
```

and the parser that makes it reachable:

```
Zend/zend_API.c
 485  			case '|':
 486  				min_num_args = max_num_args;
 487  				break;
 511  	if (num_args < min_num_args || num_args > max_num_args) {
 537  	while (num_args-- > 0) {
```

**All nine line citations verified exact.** `"|s"` puts `|` first, so at `:486`
`max_num_args` is still **0** and `min_num_args` becomes **0**; `:511`'s count
test passes with `num_args = 0`; the write loop at `:537` runs **zero** times;
`zend_parse_parameters` returns **SUCCESS**; `typ` keeps its `:3211` initialiser
`NULL`; `:3219` hands it to libc.

⭐⭐ **THE ROW'S CLAIM, IN ONE SENTENCE: the guard is PRESENT AND IT PASSES, and
it answers a different question than the one the code needs answered.** `:3215`
tests *"were the supplied arguments well-typed?"*; `:3219` needs *"was the
optional argument supplied?"*. The real test is `ZEND_NUM_ARGS()` or
`typ != NULL`. **`I12/O3`**: *a possibly-NULL pointer must not be passed to a
callee — including libc — that dereferences it without testing it.*

⭐ **A SECOND, LATENT LIMB THE CATALOGUE ENTRY DOES NOT MENTION, AND I WANT IT IN
`NOTES.md`.** `int typ_len;` at `:3212` is **uninitialised** and is written only
by the same loop that never runs — **so the one call leaves TWO outputs unwritten
and the code dereferences one of them.** `typ_len` is never read on the faulting
path, so it is **not** a second defect here; it is the same "SUCCESS does not
mean written" shape one variable over, and it is **exactly `ph96`'s mechanism**
(row 12). ▶ **Record it as an observation with its own "not load-bearing"
qualifier. Do not promote it to a limb.**

### 2.2 ⭐⭐⭐ CRITERION 2 IS **MEASURED**. THIS IS NEW, AND IT IS THE ROW'S FIRST DELIVERABLE TO INHERIT.

`PROTOCOL_PHP.md` **§A3a** landed today. For ten rows this programme *argued*
that the C exhibits its error; here is the row's, **executed**:

```
$ ORACLE=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext
$ $ORACLE -v
PHP 5.0.0 (cli) (built: Aug  5 2026 09:26:33)

$ LD_PRELOAD=<built segaddr.so> $ORACLE -n trigger.php      # <?php mb_get_info(); ?>
[segaddr] SIG11 si_code=1 si_addr=(nil)
EXIT=139

$ LD_PRELOAD=<built segaddr.so> $ORACLE -n benign.php       # mb_get_info("internal_encoding")
string(10) "ISO-8859-1"
EXIT=0
```

`si_code=1` is `SEGV_MAPERR`; `si_addr=(nil)` is a **dereference at offset 0**,
which is `strcasecmp("all", NULL)` reading the second operand's first byte —
**the catalogue's harm claim, at the address.** Build the shim from
`.tasks-php/probes/segaddr.c` (its header says how); build it under
`.temp/php97/` and delete the `.so` when your gates are green.

⚠⚠ **THE TWO CAUTIONS TRAVEL WITH IT AND YOU MUST REPEAT THEM IN `NOTES.md`**:
that binary is **php-in-safe-rust's oracle build** (`-O3 -march=native -flto`,
mysql+webext), **not** a museum-default one; and a clean run would **not** have
been evidence of absence (F3). ⭐ **A faulting run IS evidence of presence, and
that is the half this programme has never had.**

▶ **Re-run it yourself.** If it does not reproduce, **that is the report's
headline** and this task stops there.

### 2.3 ✅ THE R1h IS `f7326d627962`, ONE FILE / ONE HUNK / ONE LINE, AND IT APPLIES

```
From f7326d6279629ccd80cc77fa389584f36434a2fd
Antony Dovgal, Fri 28 Jan 2005 02:00:39 +0000 — "MFB: fix #31732"
 ext/mbstring/mbstring.c | 2 +-

-	if (!strcasecmp("all", typ)) {
+	if (!typ || !strcasecmp("all", typ)) {
```

Measured by the manager, in a standalone `git init` repo over the pristine file:

- **The patch BINDS.** Its `From` sha matches its filename — it is **not** one of
  **F115**'s three mis-bound cached patches. Check yours the same way before
  trusting it; do **not** re-fetch.
- **`git apply --check` SUCCEEDS**, reporting `Hunk #1 succeeded at 3216 (offset
  -13 lines)`. The cached patch's pre-image is a later tree (`@@ -3229`), so the
  offset is expected and is **not** a failure.
- **Applied for real, the post-image line at `:3219` is exactly**
  `if (!typ || !strcasecmp("all", typ)) {`. **Verdict taken from the BYTES, not
  the exit status** (`ph55` NOTES §5's gitignore trap).
- **`preimage_screen.py --row ph97 --verbose` → `CANDIDATE`, 1 id → 1 commit.**
  ⚠ Quote it as a **CANDIDATE**, which is the screen's *positive* label; it is
  neither `INAPPLICABLE-SAME-FILE` nor an exclusion.
- ⭐ **No census.** One hunk, one site. **Clean negative — say so**; a negative
  census is a result (F10).

⭐⭐ **THE R1h RESTORES THE BENIGN DOMAIN AND WIDENS IT.** With `typ` supplied,
behaviour is byte-identical. With `typ` absent, the patched build **answers with
the `all` array** instead of faulting — so the hardened row has **more** benign
domain than the vulnerable one, and the divergence ledger (§A2) must say so.
⚠ **Check what `gate.py` stage 7h makes of that** — it refuses an R1h that
*changes* benign output, and here the changed input is one that previously
**crashed**. ▶ **If 7h refuses this row, `RECAP_PHP.md` F43/F47 applies: a gate
stage that refuses your row is a hypothesis about your row first. Report it;
do not edit the gate.**

### 2.4 ⛔ AGENT C SAID *"THE KERNEL NEEDS **NONE** OF THE NINE COST TICKS."* I CHECKED, AND ONE OF THEM IS **REQUIRED**.

The nine: **Z**vals · **A**llocator · **H**ashTable · **V**M · **U**serland
re-entry · **G**arbage · **P**recomputation · **F**ailure injection · **2+**.

| tick | verdict |
|---|---|
| Z, H, V, U, P, 2+ | ✅ **genuinely absent.** The whole mechanism is a parameter parser plus a `strcasecmp` chain |
| **A** | ⚠ **AVOIDABLE, NOT ABSENT.** The `all` branch does `array_init` + four `add_assoc_string`. ▶ **Model the four settings as a FIXED-SIZE output. Keep allocations O(1) per kernel call** so §B1a's precondition holds and A1/B1 agree (item 78) |
| **G** | ⚠ **present in the C, not load-bearing** — §2.1's `typ_len`. Do not model it as a limb |
| ⛔ **F** | ⛔⛔ **REQUIRED, AND AGENT C'S VERDICT IS WRONG HERE.** The guard at `:3215` must be **able to fail**, or you have built a kernel with no guard — and **the row's entire claim is that a PRESENT, PASSING guard answers the wrong question.** ▶ **The blob must be able to encode *"an argument WAS supplied and its type is WRONG"*, so `RETURN_FALSE` at `:3216` is a reachable benign outcome** |

⚠ **This correction is the manager's, from reading the C, and it is the kind of
thing rule 14 obliges me to check rather than relay.** ⭐ **Agent C's ranking
stands; only its parenthetical does not.**

### 2.5 THE KERNEL — the blob, the fold, and the one substitution you must declare

- **Blob** (the catalogue's own words): *"an argument-presence bitmap + the
  argument bytes."* Concretely a stream of call records carrying **at least**
  `(supplied?, type_ok?, len, bytes)` — ⭐ **`supplied?` and `type_ok?` must be
  INDEPENDENT bits.** A kernel that derives one from the other has deleted the
  mechanism. *(This is `ph96`'s `⚠ risk` note one row early, and it is the same
  trap.)*
- **Benign fold**: `u64` = the selected settings' checksum, plus the count of
  `RETURN_FALSE` outcomes. Five selectors (`all`, `internal_encoding`,
  `http_input`, `http_output`, `func_overload`) + an unmatched-selector arm.
- ⛔⛔ **THE SUBSTITUTION, AND IT IS A MEASUREMENT DECISION AS MUCH AS A FIDELITY
  ONE: does your kernel call libc `strcasecmp`, or implement its own compare?**
  **F119's lesson is exactly this shape** — `kernel_exclusive_ir` (A1)
  **structurally excludes callee work**, and on `ph53` *100 % of a ±7 Ir swing
  lived inside a libc `memset` that A1 could not see.* **If the row's whole work
  is inside libc, A1 reads ≈ 0 and the row measures nothing.**
  ▶ **Manager's decision: implement the compare IN THE KERNEL**, so the work is
  inside the measured symbol. ▶ **And record in `NOTES.md` that `I12/O3`'s
  *"including libc"* clause is thereby narrowed to *"a callee that does not test
  its argument"*, which is the obligation's operative half.
  ⭐ **CHEAP CONTROL, AND I WANT IT: build the libc-`strcasecmp` variant too and
  report `inside_share` for both.** No extra rung, no extra gate — a `controls/`
  entry. **Either answer is a result**, and it prices F119's exclusion directly
  for the first time.
- ⚠ **Overrule any of this with evidence if the build says otherwise** — say so
  in the report, with the measurement.

### 2.6 TIER, STATISTIC, AND THE PREDICTIONS

* **TIER** — the catalogue says `narrowed`. ⚠ **That is a mining-wave label and
  `ph55` REFUTED its own.** ▶ **Declare what you measured** (§A1).
* ⭐⭐⭐ **`inside_share` PER CELL FIRST, then choose the statistic.** ⛔ **A HIGH
  SHARE IS NOT A CERTIFICATE** — `ph55`'s C cells are 74–83 % and A1 still read
  `0.000 %` on its own defect site. What matters is whether **the DIFFERENCE**
  lands inside the symbol.
* ⛔⛔ **EVERY PERCENTAGE OWES FIVE THINGS: STATISTIC · INPUT · OPT/MODE · BASE ·
  and if the base is a C cell, WHICH COMPILER — with BOTH C columns** (F108).
  **Never quote an `O0` figure as a performance result.** ▶ Run
  `.tasks-php/cbaseline_check.py --ratchet` before finishing; **adjudicate any
  new hit BY HAND, never widen the regex.**
* ⛔⛔ **ANY FAMILY-B FIGURE IS BOUND BY §B5**: publishable **iff** the two cells
  show a measured step of `0.00 Ir/call` over a full 32-residue `argv` pad sweep,
  or you clear it by the stable ratio. `.tasks-php/php50_align_sweep.py` does it
  with no build and no gate. ⚠ **Two verdicts per pair: *magnitude resolvable?*
  and *sign stable?*** ⚠⚠ **And `_055` found the `iff` ARGUMENT to be a
  non-sequitur even though the rule's measurement stands (F113) — so apply §B5,
  and do not repeat its justification as though it were established.**

**PREDICTIONS, REGISTERED.** ⚠ `ph55` refuted four of five and `ph52` five of my
statements; **six consecutive review rounds have refuted manager or engineer
claims; `_055` scored three of four conclusions surviving and ZERO of four
reasons. That is the expected yield — score these honestly, either way.**

1. ⭐⭐ **P1 — THE SAFETY IS FREE, AND FREE *BY CONSTRUCTION*.** This is the one
   C idiom whose safe-Rust replacement is a **niche optimisation**:
   `Option<&[u8]>` occupies the same bytes as a nullable pointer, so R2/R3
   should carry **no representation cost at all** over R4 on the parameter path.
   ▶ **Falsifier: any non-zero A1 step between R3 and R4 attributable to the
   optional's discriminant**, at `O3/isolated`, on both inputs, with both C
   columns present. ⓘ If it holds, **this is the row's headline and the crash
   course's paragraph**: *the null-as-absent idiom is the cheapest thing C does
   that Rust deletes outright.*
2. **P2 — R2 AND R3 CANNOT REPRODUCE THE DEFECT AT ALL**, because the type
   system will not let a `None` reach the compare. ⚠⚠ **`CLAUDE.md` rule 6: that
   is a FINDING, NEVER A PROBLEM.** ▶ **But you must say WHICH safe behaviour
   you built and why**: a naive R2 that mirrors the C's control flow with
   `.unwrap()` **panics** (a detected fault); one that handles `None` has
   **deleted the bug**. **Both are legitimate; they are different rows of the
   ladder's "does the defect survive?" column.** ▶ **Declare the choice and its
   ground in `spec.md`.**
3. **P3 — R5's obligation is `I12/O3` stated directly** as a precondition on the
   compare accessor (`typ != null`), discharged from the parser's post-condition,
   and **costs zero run-time instructions** — the proof is over a branch safe
   Rust already takes. ▶ **Falsifier: any R5 cell differing from R4 at `O3`.**
4. **P4 — `git apply` succeeds** (§2.3, already measured; scored for the record).
5. **P5 — stage 5c-twin passes cleanly, no hatch, no blocked row.** No
   `MaybeUninit` in this row, so F97's collision should not recur. `ph55` and
   `ph56` both upheld it.

---

## §3 TRAPS

1. ⛔⛔⛔ **A LIVENESS CHECK MAY NOT BE TRUNCATED AND MAY NOT MATCH ITSELF**
   (item 113). `pgrep` feeding a decision gets **no `head`, no `tail`** — a
   truncated one raced `ph55`'s gate against itself. ▶ **Confirm
   `/proc/<pid>/cmdline` for an exact PID; best of all, need no `pgrep`.**
   ⛔ Never `pkill` / `killall` / substring-match. Prefer `timeout <N> <cmd>`.
2. ⚠⚠⚠ **`grep -a` ALWAYS** (F35). A line-grep misses a phrase that wraps.
3. ⛔⛔ **MAKE `small.bin` AND `large.bin` GENUINELY DIFFERENT SIZES.** `ph64`
   shipped both at **9 bytes**, which is **one alignment draw sampled twice**,
   and it silently weakened every two-input argument the row made (F119/M4).
4. ⛔⛔ **A BACKTICK IN AN `idiom.required`/`forbidden` ENTRY IS A PIN** (item
   100, three instances in three tasks). **Run `spellings.py --audit-only` on any
   contract prose BEFORE quoting it, and read the output.**
5. ⛔⛔ **§H: a validator lands with its must-fire negatives INSIDE it**, feeding
   `problems` so stage 9b sees them. ⚠ **Never in gitignored `.temp/`.**
   ⭐ **If a checker is a grep, ADJUDICATE hits by hand and RATCHET.**
   ⛔ **A registry with no count literal IS the ratchet** — five hardcoded
   figures in `.tasks-php/` validators have gone stale. **A bound is not a
   derivation.**
6. ⛔ **F101 / item 109 — `kernel_fingerprint` is PATH-SENSITIVE and fired LIVE
   in BOTH directions on `ph52`.** ▶ Clone `ph52`/`ph55`'s repair: fixed-width
   `vNN` slug, asserted equal-path-length invariant, `asm.py::identity_level`.
7. ⚠ **A comment is not code.** Test behaviour, not text.
8. ⚠⚠ **A `c/*` COMMENT MAY POINT AT AN ARGUMENT; IT MAY NOT STATE THAT
   ARGUMENT'S VERDICT** (§F6a). `ph55` shipped one anyway because the manager's
   task file told it to record a screen's weakness and did not say where.
   ▶ **§2.3's `CANDIDATE` sentence and §2.5's substitution note go in
   `NOTES.md`, which is gate-only. `c/*` is the MEASUREMENT digest and costs 32
   cells to repair.**
9. ⛔ **A `spec.md` / `NOTES.md` MUST NOT CITE `.temp/`** (§F6) — commit the
   probe instead. ⭐ **`.tasks-php/probes/segaddr.c` is already committed; cite
   THAT, never the `.so` you built from it.**
10. ⚠ **`.temp/php97/` only — never `/tmp`.** Keep the generator, delete the
    artefact; if a blob has no script that rebuilds it, write one.
11. ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY for writing.**
    ⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`,
    `pilot/`, `common-php/`.** ⚠ **No `git add` / `git commit`.** Never touch
    `.web/` — a concurrent session owns it.
12. ⛔ **QUOTE A RE-GATEABLE READING AS AN EVENT, NEVER A STATE** (F119/M2).
    *"`contract_sha256` was `X` at commit `Y`"*, never *"`contract_sha256` is
    `X`"* — two such quotes went stale inside one round.
13. **Brackets**: `harness/measure.py --check-stale` → **`66/0`** (must NEVER
    move); `harness-php/gate.py --tool measure --check-stale` → **`22/0` before
    you start, `24/0`** once this row's two records land. **Quote first and last.**

---

## §4 DEFINITION OF DONE

1. ⭐⭐⭐ **§2.2 RE-RUN AND RECORDED AS AN EVENT** — trigger, benign control,
   `si_addr`, the build named, both §A3a cautions repeated. **If it does not
   reproduce, that is the headline and the task stops.**
2. **The row built at all five rungs + R1h**, gated, verdict quoted **from the
   gate record, named**.
3. ⭐⭐ **§2.4's `F` correction honoured**: the `:3215` guard is reachable and
   **fails on some blob input**, with `supplied?` and `type_ok?` independent.
   **Show the input that makes it fire.**
4. ⭐⭐ **§2.5's libc-vs-own-compare control built, with `inside_share` for
   both** — the first direct price on F119's callee exclusion.
5. ⭐ **§2.1's `typ_len` observation in `NOTES.md`**, with its
   *"not load-bearing"* qualifier and its pointer to `ph96`.
6. **`inside_share` per cell as a matrix, BEFORE the statistic is chosen**; both
   statistics labelled; **both C columns on every cross-language figure**; any
   family-B figure cleared through §B5 with **two verdicts**.
7. **The five §2.6 predictions scored, either way, by name.**
8. **`NOTES.md` records the R1h apply result** (offset −13, bytes verified) and
   **what stage 7h did with the widened benign domain** (§2.3).
9. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** `UNTESTED` and *"I could
   not tell"* are valued answers, and they are what the reviewer reads first.
10. **Brackets quoted first and last.**
11. ⛔ **If a prediction survives, say so plainly. Do not manufacture a
    refutation to have something to report.**
12. ⚠ **If you stop mid-row, stop CLEANLY and write a `§N ORDER TO RESUME IN`**
    — `_051` did exactly that and `_052` finished the row from it. **A
    task-notification means STOPPED, not FINISHED** (item 118).
