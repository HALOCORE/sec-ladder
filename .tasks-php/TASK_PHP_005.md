# TASK_PHP_005 — adversarial review of `TASK_PHP_004`

**Role:** research **reviewer**. Adversarial by design.
**Under review:** `TASK_PHP_004` (both blocker fixes, the 6 majors, the 7 minors)
**and the three decisions the manager made on top of it.**
**Report:** `.tasks-php/TASK_PHP_005_REPORT.md` — write the FILE
(`PROTOCOL.md` rule 10).

> **A review that says "looks good" without having tried to break something is a
> failed review.** You do **not** fix; you report. Rank `blocker` (invalidates
> the work) · `major` (wrong or misleading) · `minor` (hygiene), each with
> `file:line` and a **concrete failure scenario**, not a vibe.
> ⚠ **Do not pad. Three real blockers beat twenty nitpicks.**
> ⚠ **Name your clean negatives too** — an attack that did *not* land is worth as
> much as a finding and stops the next agent re-running it.

Read `.tasks/PROTOCOL.md` (reviewer checklist), then
`.tasks-php/TASK_PHP_004.md` and `TASK_PHP_004_REPORT.md` (what you are
reviewing), `.tasks-php/TASK_PHP_003_REPORT.md` (the review it was landing),
`PLAN_PHP.md`, `.tasks-php/PROTOCOL_PHP.md`, `RECAP_PHP.md`.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY. Do not edit it** — `PROTOCOL.md` rule 4
reserves the state layer to the manager. `TASK_PHP_004` edited it because no task
file had ever said this out loud; the content was accepted and the boundary is
now explicit (`RECAP_PHP.md` open item 16). Put everything in your report.

---

## §0 ⚠⚠⚠ RULE 3 — WHAT IS THE MANAGER'S OWN, SO YOU CAN ATTACK IT HARDEST

`PROTOCOL.md` rule 3 — *never clear your own design*. Three of these landed
**after** `TASK_PHP_004` reported and **none has been reviewed by anyone**:

| the manager decided | where | the engineer's position |
|---|---|---|
| **`results-php/preflight/` is GITIGNORED** | `.gitignore:23-29` | the engineer **declined to choose** and asked the manager to (report Problems 2) |
| **the 11 003 / 11 004 / 11 006 byte count is WITHDRAWN as false precision** | `RECAP_PHP.md:20-31` | the engineer landed **11 003** as *"correct"* and 11 004 as *"wrong"* |
| **`TASK_PHP_004`'s `RECAP_PHP.md` edits are ACCEPTED, boundary noted** | `RECAP_PHP.md` open item 16 | the engineer offered to have them reverted (Unsure 7) |
| the B1 fix belongs in `gate.py`'s preflight, no harness edit | `TASK_PHP_004.md` §1 | verified by the engineer, ✅ and by the manager |
| the whole `PLAN_PHP.md` design, unchanged since `TASK_PHP_003` | `PLAN_PHP.md` §2.1a, §3, §6, §8 | — |

✅ **Manager-verified before this file was written** (`PROTOCOL.md` rule 14 —
check them anyway, but these are the ones I actually ran):

- `python3 harness/measure.py --check-stale` → **`66 record(s) examined, 0 STALE`**
- `.gitignore:29` really contains `results-php/preflight/`, and
  `results-php/preflight/` holds **2 untracked files** (`ph00`, `_norow`)
- `git ls-files results-php/` → exactly **3** tracked files, none a preflight record
- `gate.py:187` — the shim-user detector is
  `if SHIM_HEADER.encode() in fh.read()` over `glob(cdir + "/*")`
- pristine `Zend/zend_operators.c:831` and `Zend/zend_alloc.c:295`†
  are the **only two** `ZEND_SIGNED_MULTIPLY_LONG` call sites in the tarball
  († `zend_alloc.c:234`, in `_safe_emalloc`)
- `.temp/php4/mul_probe.c:19-20` — the draw is `1 + rnd()%62` **bit widths**

---

## §1 PRIMARY TARGET — B1's guard is textual, and I think it is bypassable

`gate.py:182-188` decides "this row uses the allocator" by searching each
`<row>/c/*` file for the **literal string** `emalloc_shim.h`. Everything else in
B1 hangs off that predicate: a row it does not classify as a user is a row it
never demands the symlink from, and `TASK_PHP_004`'s nine must-fire negatives all
construct rows that **do** contain the string.

⚠ **I have read the code and NOT constructed the case. Construct it.** Candidate
bypasses, in the order I think they matter — **confirm or refute each by
building a row, gating it, and showing which digest the allocator landed in**:

1. **Indirection.** `c/kernel.c` includes `c/row_alloc.h`, and *that* includes
   the shim. Is `row_alloc.h` scanned? (It is a `c/*` file — so maybe. Say.)
2. **`c/` is globbed NON-RECURSIVELY** (`gate.py:182`). A kernel at
   `c/sub/kernel.c`.
3. **No `#include` at all** — `extern void *php_shim_emalloc(size_t);` in the
   kernel, linked against the shim's object. Does `build.py` even permit it?
4. **The Rust rungs.** R4/R5 reach C through FFI and **live in `rs/`, not `c/`**.
   A row whose *unsafe Rust* rung calls the shim is invisible to a `c/*` scan.
   ⚠ **This is the one I most expect to land**, because the ladder guarantees
   every row has Rust rungs.
5. **`common-php/emalloc_shim.c`** — the audit knows only `SHIM_HEADER`, the
   `.h`. What happens to a row that pulls in the `.c`?

**For each: does the allocator end up in the gate digest, the measurement digest,
both, or neither?** *Neither* is the B1 defect, unfixed, and is a **blocker**.

⚠ **Then the second half, and it is the same class one level up:** the guard runs
only inside `harness-php/gate.py`. **`PLAN_PHP.md` §2.1a documents the shim as
"run the unmodified `harness/check.py` out of `.temp/php-root/`" — which is
exactly how you skip the preflight.** Ask what would stop a future agent doing
that, and whether any artefact would afterwards show that they had.
⚠⚠ *"A word in a document is not an enforcement mechanism"* is
`TASK_PHP_004`'s own `.memory-php/` candidate #2. **Apply it to `gate.py`.**

## §2 B2 — the differential is strong where it looked, and I do not think it looked everywhere

The post-fix **0 / 20 M** with the control still firing **84 523** is real work
and I am not asking you to re-run it. ✅ Reproducing the reviewer's number on the
pre-fix tree first is what makes the 0 mean something. **Attack the SAMPLE SPACE
and the SCOPE instead:**

1. ⚠⚠ **The macro is named `ZEND_SIGNED_MULTIPLY_LONG` and the probe never
   tested a negative operand.** `1 + rnd()%62` bit widths gives values
   `< 2^62`, all non-negative as `long`. ✅ Manager-verified that the *other*
   call site, `zend_operators.c:831` (`mul_function`), passes
   `op->value.lval` — **signed, routinely negative**. **Extend the probe over
   negatives and zero-crossings and report the disagreement count.**
2. ⚠⚠ **`dval` is never compared.** The macro's contract is
   `(a, b, lval, dval, usedval)`; on overflow `mul_function` does
   `ZVAL_DOUBLE(result, dval)` — **`dval` is the value PHP keeps.** The probe
   compares `usedval` and `lval` only (`TASK_PHP_004_REPORT.md:196-200`).
   A shim that gets `usedval` right and `dval` wrong is wrong **in exactly the
   integer-overflow→float-promotion pattern the TYPE axis will build.**
3. **The error region is reached by luck, not by design.** 84 523/20 M = 0.42 %
   from a uniform draw. **Add a DIRECTED test** — operands near `2^53`, products
   within a few ULP of `LONG_MAX`, exact powers of two — and say whether the
   uniform draw was actually covering it or merely brushing it.
4. **Scope**: the fix was justified by *"x86-64 does not define `__i386__`"*.
   Is that recorded anywhere a future reader on a different box would hit it?
   The `#if` arm is a **build-time** property of *our* box, not of PHP.
5. The engineer's own disclosed residual — ref and shim in the **same TU**, and
   `clang -O3 -flto` never ran (`LLVMgold.so` absent). **Price both. Is the
   same-TU gap closable at acceptable cost, or is it a stated limitation?**

## §3 The majors and minors — spot-check, do not re-run

Pick the **three** you think most likely to be wrong and attack those properly;
list the rest as unexamined. My own ranking of where to look, which you should
feel free to ignore:

- **M5's kernel-overlap heuristic** (50 % / 25 % / none). Thresholds calibrated
  on **two fixtures** by the engineer's own admission. **Can you build a
  plausible `verbatim` row that scores under 50 %, or a wrong one that scores
  over?** A floor that fires on good rows and passes bad ones is worse than none.
- **M2's sweep**: post-fix it detects the **deletion** of all 7 links. Deletion
  is not derivation. **Does it discover an EIGHTH?** Add a `REPO`-relative path
  to a scratch copy of a harness module and see.
- **M6's trace** — see §4, it is now partly the manager's problem.
- `m5`'s `digest_bridge.py` **refusing** symlinked subdirectories: right call, or
  does it block a legitimate future layout?

## §4 The manager's three decisions — and the first one may have hollowed out M6

⚠⚠⚠ **I gitignored `results-php/preflight/`, and I now think that may have
undone the fix it was carrying. Attack this first; it is my worst call this
round.**

`TASK_PHP_003` M5/M6 said: `harness-php/*.py` is in no digest and
`--no-provenance` leaves **no trace in the record**. `TASK_PHP_004` fixed it by
writing `results-php/preflight/<row>.preflight.json` — the `harness-php/*.py`
hashes, the manifest hash, `provenance_skipped`, `gate_argv`. **Then I made that
directory untracked**, on the ground that it churns (`when`, `gate_argv`) on
every invocation, measured by running the preflight twice.

**So the state today: the only record of which tools certified a run, and of
whether provenance was skipped, is a gitignored file that any `git clean -xdf`
removes.** Questions, in order:

1. **Is that a `major`?** Say so plainly if it is. I will not defend it.
2. **Is there a split that gets both** — a stable, committed part (the hashes,
   the flags, the verdict) and a churny, ignored part (`when`, `gate_argv`)?
   ⚠ **Measure the churn of the stable part** across two runs before claiming
   it is stable; that is the check I got wrong last time (I scanned for `'time'`
   and `'stamp'` and missed `when`).
3. **Does anything detect the ABSENCE of a preflight record for a gated row?**
   If not, §1's bypass and this decision compound: a row can be gated with no
   preflight and leave no evidence either way.

The other two are lower stakes but are still mine and still unreviewed:

- **The withdrawn byte count.** `RECAP_PHP.md:20-31`. I claim the three figures
  measure three different cuts and that the rule's real content — *the
  row-specific half is 200 words* — holds at all three. ⚠ **Check that the
  200 is right**, and that the *rule as now worded* is enforceable by something.
  If it is enforced by nothing, say so — that is §1's lesson again.
- **Accepting `TASK_PHP_004`'s `RECAP_PHP.md` edits.** Rule 9 says a finding does
  not enter the state layer before review. Those hunks are in the state layer,
  **unreviewed, and marked as such.** ⚠ **You are that review.** Are open items
  9, 13, 14, 15 and F6's rewrite supported by the evidence, or do they say more?

## §5 Permanently in scope

- **`harness-php/` and `common-php/` are in every review's scope from now on**
  (`TASK_PHP_003` §7). The earlier PHP effort skipped its first infrastructure
  review and recorded the decision as wrong.
- ⚠ **Re-verify the two protective claims from a snapshot you take yourself**:
  `harness/measure.py --check-stale` = 66/0, and the PAT tree byte-identical.
  A clean `git status` after a run that wrote nothing proves nothing — construct
  the positive control.
- ⚠ **The php side has its own staleness check** and it is a different command:
  `harness-php/gate.py --tool measure --check-stale` (2 records today).
  `PROTOCOL_PHP.md` §E1. **Run both.**

## §6 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php5/`. **Never `/tmp`.** Keep the generator, delete the
  artefact; anything your report cites is evidence and stays.
- ⚠ **You may PLANT into tracked files to test a check, but restore them in a
  `finally:` and verify the restore BY BYTES.** Say so in the report. The manager
  will not commit while you run.
- ⚠ **Do not edit files under a running gate** (`TASK_PHP_002` discarded a record
  this way), and ⚠ **do not edit `RECAP_PHP.md`** (top of this file).
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — confirm an exact PID via
  `/proc/<pid>/cmdline`. The Phase 0 engineer leaked eleven shells because
  `pgrep -f` matched their own command lines, and for eight minutes a gate that
  had **died in preflight** looked like it was running.
- ⚠ **`env -u LD_PRELOAD` for every hand-run sanitizer probe**; grep for
  `AddressSanitizer`, not `ASan`.
- Everything you claim must have been **RUN**, output pasted.

## §7 The calls I am least sure of

1. ⚠⚠ **The preflight gitignore (§4).** Named above as my worst. I chose churn
   avoidance over durable evidence and I am not confident that was the right
   trade.
2. ⚠ **That §1's textual detector is genuinely bypassable.** I read the code and
   built nothing. **If all five candidates fail, that is a clean negative worth
   as much as a finding** — it would mean the guard is stronger than I think and
   the next agent need not re-check it.
3. ⚠ **That the negative-operand and `dval` gaps in §2 are real gaps rather than
   out of scope.** `_safe_emalloc` only ever passes non-negative `size_t` and
   ignores `dval`. **If you conclude they cannot matter for any row this
   programme will build, say so and say why** — but note the TYPE axis has an
   integer-overflow candidate and `mul_function` is where PHP's own promotion
   happens.

---

**Running count: launched from 9.** `TASK_PHP_004` refuted one figure — and it
refuted the **reviewer**, not the manager (`envp_stack_bytes` +33 → **+34**),
which turned up the better fact underneath: `ph00`'s own `envp_stack_bytes` moved
**3686 → 3695** between two runs of the same gate with no source change, so **no
two php runs are comparable to each other** either. It is a rigour signal, not a
ledger; never add it to the PAT programme's ≈965.
**Reconciliation is the manager's job, not yours** — state what you refute and
let the manager carry it.

⚠ **`TASK_PHP_003` broke the PAT side's run of four consecutive reviews that each
found a ✅ the manager had not earned: it checked every one and found ZERO
unearned, while showing the *reasoning* around two of them was wrong.** The ✅
list in §0 is this round's. **Check them the same way — the citation and the
story about it are two different claims.**
