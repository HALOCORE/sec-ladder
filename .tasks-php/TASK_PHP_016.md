# TASK_PHP_016 — build `ph07`, the second row

**Role:** research engineer. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_016_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md`, then **`.memory-php/`** (the authoritative layer — it
supersedes any task report it contradicts), `.tasks-php/PROTOCOL_PHP.md`,
`PLAN_PHP.md` §3–§6, `patterns-php/CATALOGUE.md` (`ph07`), and
**`.tasks-php/TASK_PHP_013_REPORT.md`** (how `ph03` was built — your model) plus
**`TASK_PHP_015_REPORT.md`** (the corrected template you are building on).

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **`.web/` belongs to a CONCURRENT SESSION — never `git add -A`, never touch it.**

**Bracket**: `harness/measure.py --check-stale` → `66/0` and
`harness-php/gate.py --tool measure --check-stale` → **`4/0`**, first and last.

---

## §1 The row

**`ph07` — `mbfl_strcut`, `ext/mbstring/libmbfl/mbfl/mbfilter.c`, CRASH-124.**
Tier **`narrowed`**. `mbfl_string` reduces to `{val,len}`; `mblen_table` is a
static array; no `-lm`.

The defect, verified by the manager at source — **the start walk's only exit is
`n > from`, and `p` is never compared against `string->val + string->len`:**

```c
for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }
```

⚠ `len = string->len` **is** read at the top, but only for the clamps *after* the
walk — too late. ⭐ **And the same function's SECOND walk is bounded**
(`if (k >= (int)string->len)`), so `mbfl_strcut` guards its end search and not
its start search. **That asymmetry is the row's finding and belongs in
`NOTES.md`.**

**Why this row:** the first `narrowed` extraction (so the first real test of the
tiers *and* of `provenance.py`'s overlap report), the second `DP-07` pointer
cursor, and one of the three `F27` recoveries — **building it validates that
recovery.**

## §2 R1h — ⚠ the manager corrected `TASK_PHP_015` here; read `RECAP_PHP.md` F34

`TASK_PHP_015` reported that **no `fix_commit` exists**. ✅ **That is wrong and a
fix does exist.** 5.4.0's **prologue** carries the missing bound:

```c
if (from < 0 || length < 0) { return NULL; }
if (from >= string->len)    { from = string->len; }   /* <-- the guard */
```

✅ **Manager-verified across tags**: 5.0.0's `mbfl_strcut` body is
**byte-for-byte identical to 5.3.0's** (4 708 B); 5.4.0 rewrites it (7 065 B) and
carries the clamp.

**Your job:** ⚠ **identify the COMMIT that introduced that clamp** and use it as
`fix_commit`, per `PROTOCOL_PHP.md` §F item 5. The rewrite is between the 5.3 and
5.4 branches. `https://github.com/php/php-src/commit/<sha>.patch` works;
`git fetch` of a bare SHA does **not**. ⚠ **If the clamp arrived in a large
rewrite rather than a targeted fix, say so and cite the rewrite** — that is the
row's history, and *"the fix shipped inside an unlabelled rewrite"* is itself the
finding.

⚠⚠ **`kernel_hardened.c` must be the REAL guard, not a hand-written one.** If
after real effort you cannot pin a commit, **stop and report** — do not invent a
control and call it upstream.

## §3 The corrected template — use it, do not re-derive it

`TASK_PHP_015` landed `PROTOCOL_PHP.md` §A2a's **two** rules, which replaced the
manager's single wrong one:

1. **the fixture must REACH every arm and ASSERT it**;
2. **`selfcheck` must drive its two implementations over a domain IT
   CONSTRUCTS** — not over the shipped inputs.

⚠⚠ **`ph03` shipped for a full task with `model.py` and `verus.rs` computing
different functions, and the fixture hid it because it emitted one value.**
**Do not repeat that.** `ph03`'s repaired `model.py`/`selfcheck` is your pattern.

## §4 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php16/`. **Never `/tmp`.** ⚠ `.temp/php12–15/` hold the
  earlier harnesses — reuse, do not delete.
- ⚠ **Citations resolve against the PINNED TARBALL only** (`SOURCES.md`).
- ⚠ **`env -u LD_PRELOAD`** for hand-run sanitizer probes; grep
  `AddressSanitizer`, not `ASan`.
- ⚠ **A sanitizer limb is a claim about YOUR allocator** (`.memory-php/02`).
  Say *"a detector fires under this allocator"*, not *"PHP faults"*.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`. **Three agents running have had `pgrep -f` match their
  own poller shells and report a finished gate as running.**
- Everything claimed must have been **RUN**, output pasted.

## §5 The calls I am least sure of

1. ⚠⚠ **That `narrowed` works at all.** `ph07` is the first — `PLAN_PHP.md` §4's
   tiers are my design and no row has tested the middle one. **If the deletion
   ledger, the overlap report or the tier definition does not fit a real
   `narrowed` lift, say which and how it should read** rather than forcing the
   row into it.
2. ⚠ **That the `mblen_table` can be lifted as static data without becoming a
   `modelled` row.** It is a 256-byte array per encoding. **If reproducing it
   faithfully means dragging in the encoding registry, the tier is wrong.**
3. ⚠ **That one row per task is still the right size.** `ph03` took a very long
   task; `TASK_PHP_015` correctly stopped early rather than bolt a row onto a
   template fix. **If `ph07` finishes with room to spare, say so** — the batch is
   `ph21 → ph16 → ph12 → ph29` and I would rather pair them than not.

---

**Running count: launched from 74.** `TASK_PHP_015` **refuted the manager's
fixture rule** — *"span the parameter"* is unachievable inside a fixed stride and
names the fixture as the only repair when the cheaper, stronger one is in the
model — and it checked its replacement against `ph07`'s own source before writing
it down, which is the check the manager had not made. ⚠ **It also reported that
`ph07` has no `fix_commit`; the manager verified that against three upstream tags
and it is wrong** (§2). **Reconciliation is the manager's job** — state what you
refute and let the manager carry it.
