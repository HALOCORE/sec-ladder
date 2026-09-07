# TASK_PHP_007 — adversarial review of `TASK_PHP_006`

**Role:** research **reviewer**. Adversarial by design.
**Under review:** `TASK_PHP_006` — the B1 fix, the seven landed findings, and
**the manager decisions taken on top of it.**
**Report:** `.tasks-php/TASK_PHP_007_REPORT.md` — write the FILE.

> **A review that says "looks good" without having tried to break something is a
> failed review.** You do **not** fix; you report. Rank `blocker` · `major` ·
> `minor`, each with `file:line` and a **concrete failure scenario**.
> ⚠ **Do not pad. One real blocker beats twenty nitpicks.**
> ⚠ **Name your clean negatives** — an attack that did not land is worth as much
> as a finding and stops the next agent re-running it.

Read `.tasks/PROTOCOL.md`, then **`.tasks-php/TASK_PHP_006_REPORT.md`** and
`TASK_PHP_006.md`, then `TASK_PHP_005_REPORT.md` (the review being landed),
`PLAN_PHP.md`, `.tasks-php/PROTOCOL_PHP.md`.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY — do not edit it.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**

**Bracket**: `harness/measure.py --check-stale` → `66/0` and
`harness-php/gate.py --tool measure --check-stale` → `2/0`, first and last.

---

## §0 RULE 3 — what is the manager's own

| the manager decided | where |
|---|---|
| **forbid `c/<subdir>/` on the php side rather than fix the glob** | `RECAP_PHP.md` open item 17; the engineer measured an escape hatch and did **not** enable it |
| **accept "no size rule" + a reported-not-enforced size** | open item 19 |
| accept the preflight-record split, per-run append, absence-as-note | open item 18 |
| the whole `PLAN_PHP.md` design, unchanged | §2.1a, §3, §6, §8 |

⚠ **`TASK_PHP_006` refuted the manager twice and the reviewer once, and all
three refutations were correct.** Do not assume the remaining manager calls are
sounder than those were.

---

## §1 PRIMARY TARGET — the new detector is a subprocess, and subprocesses fail

`gate.py::_tu_closure` now runs **`gcc -MM`** over `build.py`'s TU list under
both `-DSLB_ISOLATED` states and intersects by `realpath`. It replaced a string
search that had two bypasses. **Attack the replacement, not the thing it
replaced.**

1. ⚠⚠ **What happens when `gcc -MM` FAILS?** A row mid-edit, a missing header, a
   syntax error, a `#error`, a generated file that does not exist yet. **Does the
   detector fall open or closed?** A detector that silently returns "no shim" on
   a compile error is the same class of defect as the one it replaced, and it is
   *more* likely to fire, because rows under construction do not compile.
   **Construct it.**
2. **The engineer disclosed that `_tu_closure` hard-codes `gcc`** while
   `build.py` builds with **both** `gcc` and `clang`. Find a construct where the
   two closures differ (`__has_include`, `#include_next`, a GCC-only builtin
   guard), or show the concern is empty.
3. **Both `-DSLB_ISOLATED` states** — is that actually the whole space
   `build.py` compiles in? Check its flag matrix against what `_tu_closure`
   simulates. A third state the audit does not simulate is a third bypass.
4. ⚠ **The fallback path.** Text detection survives "for rows that don't
   preprocess". **When is it reached, and can a row reach it deliberately?** If a
   row can *choose* the weaker detector by not compiling, F-1 is reopened.
5. **~115 ms/row was measured on how many rows?** The audit runs over **every**
   row on every invocation. At 80 catalogue rows that is ~9 s per preflight —
   check the scaling claim, and whether it is per-row or per-TU.

## §2 The `c/<subdir>` refusal, and the escape hatch that was measured but not built

`c_subdir_audit` refuses `patterns-php/*/c/<subdir>/`. The engineer measured
that **a flat symlink beside a subdirectory file lands the real bytes in both
digests**, and deliberately did **not** enable it, on the ground that nothing
would force the *next* file added to get a link.

- **Is the refusal itself sound?** Can a row still get a file into `c/` that the
  digest misses — a symlink to a directory, a file the glob's `isfile()` drops
  for another reason, a name with a newline or a glob metacharacter?
- ⚠ **Re-derive the escape hatch.** If the flat symlink really does land in both
  digests, then the manager's *"forbid it for ever"* is a bigger claim than it
  needs to be, **and this is the manager's least-sure call** — say so if the
  cheaper design is safe.

## §3 F-2's record, and F-4's floor

- **The preflight record is now COMMITTED and APPENDED per run.** Attack the
  growth: `_norow.preflight.json` accumulates one entry per distinct command
  line (the engineer flagged this). **Does it converge or grow without bound?**
  Does anything prune it? Is the "absence is a NOTE, not a failure" call right,
  or does it recreate the gap M6 was opened for?
- **F-4's overlap fix.** The `#if 0` bypass is closed — **is `#if 1`? `#ifdef
  NEVER`? a `/* … */` block comment spanning the citation? a `__COUNTER__`
  guard?** The reviewer found one spelling; find the next. And **re-check the
  clean negative**: the realistic 68 % lift must still pass.

## §4 Permanently in scope

- `harness-php/` and `common-php/` are in **every** review's scope.
- ⚠ **Re-verify the protective claims from your own snapshot** —
  `.temp/php5/snapshot.py` exists and is re-runnable, and ⚠ **the engineer
  disclosed it did NOT use it**, relying on `git status` instead. Do it properly:
  a clean `git status` after a run that wrote nothing proves nothing.
- ⚠ The engineer **did not** add the `-m32` `#error` guard to `emalloc_shim.h`
  (`TASK_PHP_005` §2.4), judging it adjacent behaviour-change work. **Is that
  right, or is it a hole?** On `-m32` the shim keeps the heuristic where real PHP
  takes the exact `imul`, and nothing detects it.

## §5 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php7/`. **Never `/tmp`.** ⚠ `.temp/php5/` and
  `.temp/php6/` hold the previous generators — **reuse, do not delete.**
- ⚠ **You may PLANT into tracked files, but restore in a `finally:` and verify
  the restore BY BYTES.** Say so. The manager will not commit while you run.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`.
- ⚠ **`env -u LD_PRELOAD`** for hand-run sanitizer probes; grep
  `AddressSanitizer`, not `ASan`.
- Everything claimed must have been **RUN**, output pasted.

## §6 The calls I am least sure of

1. ⚠⚠ **§1.1 — that the new detector fails CLOSED.** I did not ask for it and
   the report does not say. **If `gcc -MM` failing means "this row does not use
   the shim", the blocker is not closed, it has moved** — and rows under
   construction are exactly the population that does not compile.
2. ⚠ **The `c/<subdir>` ban (§2).** Mine, and the engineer has already shown my
   stated reason was narrower than I thought. **If the flat-symlink design is
   safe with a check, my ban is over-strict and I want to know now**, before the
   catalogue is written around it.
3. ⚠ **That "absence is a NOTE" is enough.** The engineer judged a hard failure
   to be a deadlock and said it might be wrong. I accepted. **Two judgements in a
   row with no adversarial pass is exactly the configuration this project keeps
   finding defects in.**

---

**Running count: launched from 15.** `TASK_PHP_006` refuted three — **two
against the manager** (`gcc -MM` is affordable; the structural size rule was
unsatisfiable and would have been the *fourth* failed version) and one against
the reviewer (F-5's table measured the wrong span, making the corpus maximum
appear as its minimum). ⚠ **And a manager figure that had motivated three
successive versions of a rule turned out to be invented** — `p01`'s `why` is
2 057 words, not the *"~7,000"* the manager wrote into a task file and an
engineer later cited back as the rule's justification.
**Reconciliation is the manager's job** — state what you refute and let the
manager carry it.
