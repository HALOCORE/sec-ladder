# TASK_PHP_006 — land `TASK_PHP_005`'s corrections

**Role:** research engineer. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_006_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md`, then **`.tasks-php/TASK_PHP_005_REPORT.md`** (the
review you are landing — it names every file:line and ships a generator for
every finding under `.temp/php5/`), then `.tasks-php/TASK_PHP_004_REPORT.md`,
`PLAN_PHP.md` and `.tasks-php/PROTOCOL_PHP.md`.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY — do not edit it.** `PROTOCOL.md` rule 4.
This sentence exists because `TASK_PHP_004` edited it in good faith when no task
file had ever forbidden it (`RECAP_PHP.md` open item 16). Everything goes in your
report; the manager lands the state layer.

⚠⚠⚠ **NO EDITS UNDER `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
`harness/*.py` and `common/*.py` are hashed into all 33 PAT gate records.
⚠ **F-1 will tempt you to fix `check.py`'s glob. DO NOT** — see §1.2.

**Bracket**, first and last command, both pasted:
```sh
python3 harness/measure.py --check-stale                  # 66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale  #  2 record(s) examined, 0 STALE
```

---

## §1 The blocker — F-1, and it is the whole point of the task

`gate.py:182-188` decides "this row uses the allocator" by searching `<row>/c/*`
for the literal string `emalloc_shim.h`. **Two spellings get round it**, both
constructed by the reviewer, both compiling, linking and running a live
allocator into **neither digest** with the preflight green
(`.temp/php5/b1_bypass.py`, `buildtest.sh`):

1. `#include "emalloc_shim.c"` — `SHIM_HEADER` is only the `.h`, and the `.c`
   sits on `-I COMMON`. ⚠ `emalloc_shim.c`'s own header comment says it *"IS NOT
   ON THE PATTERN BUILD PATH AND CANNOT BE"* — **true of `build.py`'s TU list,
   false of the preprocessor, and that sentence is why the audit missed it.**
   Fix the comment as well as the code.
2. `c/<subdir>/*` — `glob(cdir + "/*")` is non-recursive.

**Close both.** ⚠⚠ **And re-run the reviewer's own eight fixture rows** — the
fix is not landed until `ph53-subdir` and `ph54-dotc` are refused, `ph51-linked`
and `ph55-extern` still pass, and `ph50-direct` still fails for the original
reason. **A fix that breaks a clean negative is not a fix.**

### 1.1 ⚠ The audit greps text; the compiler is the authority

F-8: the audit **false-positives** on a row whose only mention is the comment
*"deliberately does NOT include emalloc_shim.h"* — which is the sentence
`PLAN_PHP.md` §4.3 and `emalloc_shim.h:6-9` **tell a non-allocating row to
write.** The message then asserts an `include(s)` that does not exist and offers
a fix that would pin an allocator the row never uses.

**Decide the detector properly and say why you chose it.** The obvious repair is
to require the name inside an `#include` on the same line; the stronger one is to
ask the preprocessor (`gcc -MM` with `build_c`'s real `-I` flags gives the exact
TU closure, and the reviewer already used it). ⚠ **A preprocessor-based detector
would close 1, 2 and F-8 at once and would not have a spelling** — price it, and
if you reject it, say what it costs.

### 1.2 ⚠⚠ The `c/` subdirectory half is BIGGER than the allocator — and you must NOT fix it

`check.py:10314` and `measure.py:226` glob `<row>/c/*` non-recursively and drop
the directory entry with `if os.path.isfile(s)`, so **any source file in a `c/`
subdirectory is in no digest at all**, and `check.py`'s `--no-build` staleness
scan misses it too.

✅ **No row is affected** — `find patterns patterns-php -mindepth 3 -maxdepth 3
-type d -path '*/c/*'` is empty. **Fixing the glob is a `harness/` edit and costs
a 33-pattern re-gate for zero present benefit; the manager has decided against
it** (`RECAP_PHP.md` open item 17).

**So: make the php preflight REFUSE any `patterns-php/*/c/` subdirectory
outright**, with a message that says why (the digest cannot see it) and points at
open item 17. ⚠ Php rows are *extracted* C and `c/zend/` is an ordinary thing to
want — **this refusal will be met by a real person with a real reason, so the
message has to be good.**

### 1.3 The preflight is skippable and leaves no trace

`grep -c preflight harness/{check,measure,report}.py` → `0 0 0`, and
`PLAN_PHP.md` §2.1a documents running `check.py` out of the shim directly.
**You cannot close this without a harness edit** — so **do not try**. Instead
make §2's record good enough that its *absence* is detectable, and say plainly in
`PROTOCOL_PHP.md` what is and is not enforced.

## §2 The majors

**F-2 — the preflight record.** ⚠ **The manager's gitignore decision is
REVERSED** (`RECAP_PHP.md` open item 18): the reviewer measured that only `when`
moves across two runs (`sha256(rest)` identical, `gate_argv` a function of the
command). Land all three parts:
- **commit the record**, minus `when` (drop it, or split it to an ignored
  sidecar); update `.gitignore` and delete the wrong rationale sitting there now;
- **fix the per-row overwrite** — a later preflight currently **erases**
  `provenance_skipped: true`. Key on the run, or append;
- **make an absence detectable**: after this task, a php gate record with no
  preflight record should be visible to *something*. ⚠ If you cannot do that
  without a harness edit, say so and say what the cheapest honest substitute is.

**F-3 — the fidelity claim.** `common-php/emalloc_shim.h:462` (digest-pinned) and
the shim's prose claim 8 cells; 5 were run. The reviewer ran the other three
(`.temp/php5/mul_probe_missing.sh`): 0/20 M, control firing. **Correct the text
to state what was measured, by whom, and with which flags** — including that
`clang -O3 -flto` **links** with `-fuse-ld=lld` (`build.py:169-172` inserts it),
so `TASK_PHP_004_REPORT.md` Problem 1 is a limitation that does not exist.
⚠ This is a **digest-pinned** file: expect a `ph00` re-gate, and budget it.
⚠ Also fix `emalloc_shim.h:465-468`'s *"Do not 'simplify' the parameter types"* —
`_safe_emalloc` passes `size_t`, but `zend_operators.c:831` (`mul_function`, the
TYPE axis's own candidate) passes **`long`**, and that UB is PHP's. The comment
should describe both callers, not forbid one.

**F-4 — the overlap floor passes DEAD CODE.** A division kernel citing
multiplication, with the citation behind `#if 0`, scores **100 %**
(`_normalise` drops lines starting with `#`). Fix the normaliser and **keep the
reviewer's three-case harness as the regression test** — including case A
(a realistic `verbatim` lift at 68 %), because the floor must not become too
high while you are making it less easy. ⚠ **And correct the claim itself**: the
check never reads `main.c`, the driver loop or the build, so **a pass is not
evidence that the cited lines are compiled.** Say that where the tool says
anything.

**F-5 — the size rule.** ⚠⚠ **The manager has now written this rule twice and
both versions failed; the third is NOT the manager's to invent.**
`RECAP_PHP.md` open item 19. **Measure the distribution of the row-specific
`why` across all 33 PAT rows and `ph00`, then propose one of:**
(a) a limit the corpus supports, (b) a **structural** rule (e.g. the first
paragraph is a self-contained summary, unbounded thereafter), or (c) **no rule
at all**, argued. ⚠ **Whatever you propose must come with the check that
enforces it, or be explicitly proposed as unenforced.** An unenforced size rule
is what produced both failures.

## §3 The minors

Land F-6 (preflight repairs before it checks — `check()` before `build()`),
F-7 (`gate.py <row> --preflight` forwards the flag; ⚠ **the manager's own 06:55
record is an instance**), F-9 (`digest_bridge.py`'s message is false for
`layout/` specifically — special-case it against `GLOB_PATTERNS` rather than
assert something untrue), F-10 (`--sweep` is quote-sensitive;
`harness/limbs.py:66` is a live single-quoted instance, benign today), F-11
(open items 13/14 — **report the wording, the manager lands it**), F-12
(`TASK_PHP_005.md:51`'s `zend_alloc.c:295` → `:234`; ⚠ a task file is history,
so **propose** the treatment rather than rewriting it).

⚠ **If you disagree with any of these, say so with a measurement rather than
landing it.** The reviewer is not automatically right either — `TASK_PHP_004`
refuted `TASK_PHP_003` on `+33` vs `+34` and was correct.

## §4 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php6/`. **Never `/tmp`.** ⚠ `.temp/php5/` holds the
  reviewer's generators — **reuse them, do not delete them.**
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — confirm an exact PID via
  `/proc/<pid>/cmdline`. Eleven shells were leaked here once because `pgrep -f`
  matched their own command lines.
- ⚠ **Do not edit files under a running gate** (`TASK_PHP_002` discarded a
  record that way).
- ⚠ **`env -u LD_PRELOAD` for hand-run sanitizer probes**; grep
  `AddressSanitizer`, not `ASan`.
- Everything claimed must have been **RUN**, output pasted.

## §5 The calls I am least sure of

1. ⚠⚠ **That §1.2's refusal is the right trade.** I am choosing to **forbid a
   legitimate directory layout on the php side for ever** rather than pay a
   33-pattern re-gate once. If php rows genuinely need `c/<subdir>/` — and
   extracted PHP headers are the obvious case — **that trade is wrong and I want
   to be told now, with the row that needs it**, not after twenty rows have been
   contorted around it.
2. ⚠ **That a preprocessor-based detector (§1.1) is affordable.** `gcc -MM` per
   row per preflight may be too slow, or may fail on rows that do not compile
   yet. **If it is impractical, the string detector with an `#include` guard is
   fine — but then say out loud that the guard has a spelling.**
3. ⚠ **F-5 is the one where I most expect to be wrong**, because I have been
   twice. If the honest answer is *"no size rule"*, **say so** — `RECAP_PHP.md`
   currently has none and that is a stable state, not an emergency.

---

**Running count: launched from 12.** `TASK_PHP_005` refuted three: two against
the engineer (the 5-of-8 config matrix; the `clang -flto` limitation that does
not exist) and **one against the manager** (the gitignore rationale). It also
found the first unearned ✅ of this programme, **and it was the manager's**
(`zend_alloc.c:295` for `:234`). ⚠ **Nine of its attacks were clean negatives,
including all four the manager named on B2** — read them before re-running any.
**Reconciliation is the manager's job** — state what you refute and let the
manager carry it.
