# TASK_PHP_003 — adversarial review of Phase 0

**Role:** research **reviewer**. Adversarial by design.
**Under review:** `TASK_PHP_002` (the whole Phase 0 tree) **and the manager's
own design and corrections**.
**Report:** `.tasks-php/TASK_PHP_003_REPORT.md` — write the FILE.

> **A review that says "looks good" without having tried to break something is a
> failed review.** You do **not** fix; you report. Rank findings `blocker`
> (invalidates the work) · `major` (wrong or misleading) · `minor` (hygiene),
> with file:line and a **concrete failure scenario**, not a vibe.
> ⚠ **Do not pad. Three real blockers beat twenty nitpicks.**
> ⚠ **Name your clean negatives too** — an attack that did *not* land is worth
> as much as a finding and stops the next agent re-running it.

Read `.tasks/PROTOCOL.md` (reviewer checklist), `PLAN_PHP.md`,
`.tasks-php/TASK_PHP_002.md`, `.tasks-php/TASK_PHP_002_REPORT.md`,
`.tasks-php/PROTOCOL_PHP.md`, `RECAP_PHP.md`.

---

## §0 ⚠⚠⚠ RULE 3: THE THING YOU ARE REVIEWING IS PARTLY THE MANAGER'S OWN DESIGN

`PROTOCOL.md` rule 3 — *never clear your own design* — binds here, and the
manager is telling you which parts are its own so you can attack them hardest:

| the manager designed | where |
|---|---|
| **the symlink-shim mechanism itself** | `PLAN_PHP.md` §2.1a — including the `p01` digest comparison it cites as proof |
| the no-touch rule and its cost table | `PLAN_PHP.md` §2.1 |
| the `provenance` block schema | `PLAN_PHP.md` §6 |
| the phase structure and the C-side bar restatement | `PLAN_PHP.md` §3, §8 |
| **the four corrections landed after the engineer reported** | `PLAN_PHP.md` §4.3 (third truncation, `:40-44`), `RECAP_PHP.md` (the repaired `why` rule, findings F1–F5) |

**Designer-validates-own-design is the configuration this project keeps finding
defects in.** The manager also marked several sentences ✅ *manager-verified*.
⚠⚠ **Four consecutive reviews on the PAT side each found a ✅ the manager had
not earned. Check them.** They are, exactly: the staleness bracket, the
untouched-PAT-tree claim, the `ph00-smoke` verdict, `fixture.py:31`'s `PILOT`,
`zend_alloc.c:40-44`, `zend_alloc.c:295`, `zend_alloc.h:53`,
`zend_alloc.c:129/132`, `zend_compile.h:285/287`, `zend.h:388/391`,
`zend_compile.c:1196-1197`, `zend_ptr_stack.h:44-49`, `zend_hash.h:88`, the
`why` byte counts, and the three miners' recounts.

---

## §1 The primary target — and it is the one the manager is least sure of

⚠⚠⚠ **`common-php/*.h` IS IN NO GATE DIGEST.** `check.py`'s three `common/`
globs (`driver.*`, `*.py`, `layout/*.py`) are **all non-recursive**, and
`emalloc_shim.h` matches none of them. The engineer closed this with **two**
mechanisms — a `digest_bridge.py` for the gate half and a mandatory
`<row>/c/` symlink for the measurement half.

**Attack it.** Specifically:

1. **Construct the miss.** Edit `common-php/emalloc_shim.h` in a way that would
   change a measured number, re-run the gate, and see whether anything fires.
   ⚠ If nothing does, that is a **blocker** — it is the exact gap that left ten
   committed control sources in no digest at all on the PAT side.
2. **Is the bridge itself hashed?** A digest mechanism that is not in the digest
   it maintains is a mechanism anyone can silently disable.
3. **Is the `<row>/c/` symlink MANDATORY or merely conventional?** If a future
   row can omit it and still gate green, the measurement half is unprotected.
   Find out by building a row without one.
4. **Two mechanisms for one property is exactly what `RB012` M6 priced on the
   earlier PHP effort**: 4 of 6 plausible new artefacts were pinned by neither.
   **Enumerate the artefact kinds a php row can ship and say which digest, if
   any, covers each.**

## §2 The shim

- **Is `--sweep` vacuous?** It claims to re-derive the link list from the harness
  sources rather than trusting the spec. **Ask what would make it FAIL.** Delete
  a link and see whether it says so; add a `REPO`-relative path to a scratch copy
  of a harness module and see whether it is found. ⚠ A sweep with a hard-coded
  list is the *silent-skip* class this project has found ten times.
- **Seven links: complete, or just more than five?** The manager's five were
  wrong. Verify `pilot` really is required (`fixture.py:31`) **and** hunt for an
  eighth. `~`-expansions, `os.environ` reads and anything derived from
  `sys.argv[0]` are not `REPO`-relative and will not show up in a `REPO` sweep.
- **`PYTHONDONTWRITEBYTECODE=1`** — is it set on *every* path into the harness,
  including `measure.py` and `report.py`, or only in `gate.py`? A stray
  `.pyc` written with the shim path as `co_filename` is a real contamination of
  the PAT tree.
- ⚠ **Re-derive the manager's `p01` digest proof yourself** (`PLAN_PHP.md`
  §2.1a). It is the single load-bearing claim under the whole design.

## §3 `ph00-smoke`

- ⚠ **Were its pins RE-DERIVED or COPIED?** `.memory/05-layout.md` step 5: *"a
  pattern whose `spec.md` pins are copied from p01 without being re-derived is a
  pattern whose gate certifies p01."* Check the obligation counts, identity
  levels, the `Ir` floor and the Miri policy against what the gate actually
  reports for `ph00`.
- **Mutate its proof and confirm the gate fails.** If it does not, the smoke test
  proves the pipeline runs, not that it checks anything.
- The engineer disclosed that **`contract_sha256` has a spelling** and that its
  first Rule-6 disclosure used the wrong one. ⚠ **Verify the disclosure against
  `git`**, per rule 6 — and note the rule's own hole: on a *new* pattern the
  `git show HEAD:` diff is **vacuous**, so the recorded first hash is the only
  evidence.
- Does `ph00`'s `provenance` block really say, in terms, that it has **no PHP
  provenance** and prices nothing? A future reader mistaking it for a php row is
  the failure mode.

## §4 The allocator shim

- **Fidelity, line by line, against the pristine tarball** (sha256
  `5783e0c0…d6919`) — not against a build tree, all of which are patched.
- **All three truncations present?** `zend_alloc.c:129` (`unsigned int
  real_size`), `zend_alloc.h:53` (`unsigned int size:31`),
  `zend_alloc.c:295` (`int final_size = size*nmemb`, signed, in `_ecalloc`).
- ⚠ **The probe's positive control: does it actually fire?** *"A detector that is
  not running looks exactly like a detector that found nothing."* And
  ⚠ **`env -u LD_PRELOAD`** — a dynamically linked ASan binary refuses to start
  behind this shell's `LD_PRELOAD` **and still exits 1**. Grep for
  `AddressSanitizer`, not `ASan`.
- The report claims ASan **reports** a UAF on a 96-byte block and is **silent**
  on a 24-byte one. **Reproduce it.** It is the evidence behind `RECAP_PHP.md`
  F3, which the manager has already written into the plan as a rule.

## §5 The provenance validator

- The **must-fire negative** — does a wrong line span really get rejected, and
  for the right reason?
- **What does it NOT cover?** A correct `extract_sha256` over the *wrong file*, a
  correct span in a *patched* tree, a missing block entirely, a block whose
  `extract_cmd` does not match its own `c_lines`.
- Is it wired into anything, or does it only run when someone remembers? ⚠ *"A
  standalone script nobody runs"* is how the PAT side's item 23 recurred twice.

## §6 The manager's four corrections

Each was landed **after** the engineer reported and **none has been reviewed**:

1. `zend_alloc.c:39-43` → `:40-44`. Correct now?
2. The third truncation written into `PLAN_PHP.md` §4.3 — is the manager's
   *description* of it right, or just the line number?
3. The repaired `why` rule in `RECAP_PHP.md` — is *"the row-specific half ≤ 200
   words"* actually satisfiable? **Measure it on `ph00`.** ⚠ The manager has now
   written this rule **twice** and the first version was impossible.
4. `RECAP_PHP.md` findings F1–F5 and open items 9–12 — do they say what the
   evidence supports, or more?

## §7 Also in scope, permanently

- **`harness-php/` and `common-php/` are in every review's scope from now on.**
  The earlier PHP effort recorded the opposite decision, then recorded it as
  *wrong*: skipping the first infrastructure review cost two harness defects
  that reached published numbers.
- **Independently re-verify the two protective claims**, from a snapshot you take
  yourself, not from the engineer's: `measure.py --check-stale` = 66/0 STALE, and
  the PAT tree byte-identical. ⚠ **A clean `git status` after a run that wrote
  nothing proves nothing about a run that would have** — construct the positive
  control.

---

## §8 Rules

- **No `git add`/`git commit`.** Read-only git is fine.
- Scratch under `.temp/php3/`. Never `/tmp`.
- ⚠ **You may PLANT into tracked files to test a check, but you must restore
  them in a `finally:` and verify the restore by bytes.** Say so in the report.
  The manager will not commit while you run.
- `timeout <N> <cmd>`. No `pkill`/`killall` — confirm an exact PID via
  `/proc/<pid>/cmdline` first. ⚠ The engineer leaked eleven shells here because
  `pgrep -f` matched their own command lines; for eight minutes a gate that had
  **died in preflight** looked like it was running.
- Everything you claim must have been **run**, with output pasted.

---

**Running count: launched from 8.** `TASK_PHP_001` refuted three named manager
claims plus the *"123 ASan reports"* error; `TASK_PHP_002` refuted four more (the
five-link shim, `:39-43`, the missing third truncation, and the unsatisfiable
`why` rule). **Reconciliation is the manager's job, not yours** — state what you
refuted and let the manager carry it.

⚠⚠ **The manager's honest expectation: the `common-php/*.h` digest gap (§1) is
where this falls over, and the two-mechanism fix is the part most likely to be
wrong. Prove me right or wrong with a constructed case, not an argument.**
