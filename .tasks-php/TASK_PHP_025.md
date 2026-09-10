# TASK_PHP_025 — build `ph16-fdset-index`, row 3

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_025_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative — it supersedes any
task report it contradicts), `.tasks-php/PROTOCOL_PHP.md`, `PLAN_PHP.md` §3–§4,
`patterns-php/SOURCES.md`, and **`patterns-php/ph07-strcut-cursor/` in full** —
that is the current best row and your template. `patterns-php/CATALOGUE.md`'s
`ph16` block is the row; `.tasks-php/UPSTREAM_001.md` §4 is its upstream fix;
`.tasks-php/TASK_PHP_020_REPORT.md:131` is its audit line; **`.temp/mgr166/`**
is the manager's re-read of the C, with a `REFETCH.sh` that regenerates all of it.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`** —
`harness/*.py` and `common/*.py` are hashed into all 33 PAT gate records and an
edit costs a 33-pattern re-gate. **Import and rebind, as `harness-php/root.py` does.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ Scratch under `.temp/php25/`. **Never `/tmp`.** `.temp/php11/fdset_probe.c` is
the existing `FD_SET` probe and `.temp/php18/` the `ph07` build's — **reuse them.**

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`6/0`**, first and last.

---

## §1 The row, re-read at source by the manager

`ext/standard/streamsfuncs.c:541`, pristine 5.0.0 (sha256 `5783e0c0…d6919`):

```c
static int stream_array_to_fd_set(zval *stream_array, fd_set *fds, php_socket_t *max_fd TSRMLS_DC)
{
	php_socket_t this_fd;
	...
		if (SUCCESS == php_stream_cast(stream, PHP_STREAM_AS_FD_FOR_SELECT | PHP_STREAM_CAST_INTERNAL, (void*)&this_fd, 1)) {
			FD_SET(this_fd, fds);          /* :541 -- nothing tests this_fd < FD_SETSIZE */
```

`fds` is **the caller's**: `fd_set rfds, wfds, efds;` at `:658` in
`PHP_FUNCTION(stream_select)`. ⚠⚠ **THIS FILE ORIGINALLY SAID `:657` AND CALLED
`TASK_PHP_020_REPORT.md:131`'s `:658` "off by one and harmless". `_020` WAS
RIGHT, THE ERROR WAS THE MANAGER'S, AND `TASK_PHP_025` CAUGHT IT** — I mis-read
my own `sed -n '655,660p'`, whose fourth line is 658. **The correction was
inverted, which is worse than the drift it claimed to fix** (F56).

**Machine facts, measured** (`.temp/mgr166/fdfacts.c`): `FD_SETSIZE 1024`,
`sizeof(fd_set) 128` bytes, index 4096 → word 64 → **byte offset 512, past the
object**. `FD_SET` is a pure bit-set macro and **never consults the fd table**.

⚠⚠ **TWO TRIGGERS, AND THE TASK MUST NOT BLUR THEM.** The *PHP-level* trigger
needs > 1024 real streams and an `RLIMIT_NOFILE` to match. The *kernel-level*
trigger does not — the extracted kernel takes a blob of indices, and any index
≥ 1024 is out of bounds. **Both are true.** `PLAN_PHP.md` §4.2's reachability
deliverable is about the kernel; the PHP-level statement belongs in `NOTES.md`
as the row's provenance, not as its trigger.

**Tier: the catalogue says `verbatim`, and ⚠ I am no longer sure it survives.**
`TASK_PHP_012` M4's recheck (re-run by the manager, `UPSTREAM_001.md:240-252`)
cleared it — but **that test asks one question: is the defect site inside a
`PHP_FUNCTION` / argument-parsing frame?** `ph16` is a `static` helper, so it
passes. ⚠⚠ **The test is not the definition.** `PLAN_PHP.md:342-343` says
`verbatim` is *"the function lifts as-is; only `TSRMLS_*` / macro plumbing is
removed"* and `narrowed` is *"a wrapper comes off (zval unpacking…); the body is
unchanged"* — and `stream_array_to_fd_set` iterates a `zend_hash` of `zval **`
and calls `php_stream_from_zval_no_verify` / `php_stream_cast`. **None of that
is macro plumbing.** If your kernel drives `FD_SET` from a blob of indices, the
zval unpacking has come off and the body is unchanged, **which is `narrowed`
by the book.**

**Decide it yourself, from `PLAN_PHP.md` §4's definitions, and say which test
you applied.** ⚠ The tier is a **cost statement, never a filter** — no admission
turns on it — but `provenance.py` reports kernel overlap against the declared
tier's expectation (`verbatim` 50 %, `narrowed` 25 %), so **a mis-declared
`verbatim` landing at 30 % hands a reviewer a frightening number with no way to
tell a wrong tier from a bad extraction** (`UPSTREAM_001.md:255-262`). ⚠ **This
is the same shape as F44 — a rate that tracks the TEST rather than the rows —
and it is my error for writing *"already tier-checked, do not re-tier"* into an
earlier draft of this file.**

## §2 R1h — the guard, and the finding inside it

`99e290f882c9` (2004-09-17, Wez, *"Bug #24189: possibly unsafe select(2) usage"*).
⚠ **10 files, 27 368 B — cite the HUNK, not the commit** (`PROTOCOL_PHP.md` §F).
The patch is fetched at `.temp/mgr166/99e290f882c9.patch`. It adds to
`main/php_network.h`:

```c
#ifdef PHP_WIN32
# define PHP_SAFE_FD_SET(fd, set)    FD_SET(fd, set)                                    /* NO CHECK */
#else
# define PHP_SAFE_FD_SET(fd, set)    do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)
#endif
```

⭐ **A macro named `PHP_SAFE_…` whose safety is `#ifdef`-conditional, and the
Win32 comment is CORRECT** — Win32's `fd_set` is a counted array of `SOCKET`s,
so the bound lives in the platform's data structure rather than in the code.
**R1h is the POSIX branch** (we build POSIX) **and `kernel_hardened.c` must say
which branch it compiles and why.** This is settled at `UPSTREAM_001.md:147-170`
and re-confirmed from the patch — **do not re-litigate it, but do state it.**

⚠ The fix also adds `&& this_fd >= 0` at the call site. **That is a second,
separate guard** (a negative fd, from a failed cast). Decide whether it is in
your kernel's contract and say so either way — `ph03` and `ph07` both had a
two-hunk fix and both had to make this call explicitly.

## §3 ⚠⚠ THE ORACLE PROBLEM — this row's real design question

**Stock ASan does not see this defect.** Measured, and in the catalogue block:
a write 8 bytes past the object reports `stack-buffer-overflow`; **the same write
384 bytes past is SILENT**, because it clears the redzone into unpoisoned stack.
Glibc `_FORTIFY_SOURCE` *does* catch it
(`*** bit out of range 0 - FD_SETSIZE on fd_set ***`).

**So the R1 rung cannot be witnessed by the detector every other row uses.**

⭐ **THE MANAGER RAN IT** rather than citing it (`PROTOCOL.md` rule 14) —
`.temp/mgr166/asan_reach.c`, one write per process at a chosen distance past a
128-byte on-stack `fd_set`, with a `volatile` canary array standing in for the
caller's other locals. **Identical at `-O0`, `-O1` and `-O3`:**

| bytes past the object | ASan | canary |
|---|---|---|
| 8, 16 | ✅ **REPORTED** `stack-buffer-overflow` | — |
| **32 … 512** | ⚠ **SILENT** | ⭐ **CAUGHT IT** |
| 4096 | ⚠ SILENT | INTACT — past the canary's own 512 bytes |

**Three things this settles, and one it does not:**

1. ✅ **The catalogue's premise HOLDS — and the boundary is 32 bytes, not
   somewhere near 384.** The redzone on this object is 32 bytes wide. **An
   engineer who tested only the catalogue's `8` and `384` would place the
   cliff anywhere in between.**
2. ⭐⭐ **THE CANARY ORACLE WORKS, ACROSS THE WHOLE RANGE WHERE ASan FAILS, at
   every `-O` level** — and **it works for exactly the reason ASan fails.**
   Past the redzone the write lands in a *live neighbouring object*, so the
   address is legitimate and there is nothing for a sanitizer to report — but
   it is an object we control and can check. **Build the row on this.**
3. ⚠ **Reach is bounded by the canary, not by the defect.** At 4096 nothing in
   the frame sees it. `stream_select` really does have three `fd_set`s and
   several `int`s in one frame, so **size the canary to the index range your
   fixture drives, and state the range over which your oracle is complete.**
4. ⚠ **`volatile` is load-bearing** — it is what stops the compiler eliminating
   the canary. **A canary the compiler reorders or drops is a probe that
   silently passes**, so assert its address relative to the `fd_set` at run time
   rather than assuming the layout.

Two alternatives, **for a control, not the row**: **`_FORTIFY_SOURCE`**, which
is real and upstream and does fire (`*** bit out of range 0 - FD_SETSIZE on
fd_set ***`) — ⚠ but it is a *third* configuration and `.memory-php/02`'s rule
that **a sanitizer limb is a claim about YOUR toolchain** applies doubled; and a
**heap `fd_set`**, which puts ASan's redzone back in range — ⚠⚠ **but that
changes the storage class the row is ABOUT**, and `ph17` is already catalogued
as exactly that variation.

⚠⚠⚠ **AND WHATEVER YOU FIND HERE, IT CANNOT KILL OR SHRINK THE ROW.** *"The
sanitizer cannot see it"* is a **FINDING** — `CLAUDE.md` rule 6, `PLAN_PHP.md`
§3. It is, in fact, one of the more interesting things this corpus has produced:
**a real memory-safety defect that the standard C detector misses and that
Rust's own runtime checker would not.** If R4-under-Miri catches what R1-under-ASan
does not, **that asymmetry is a headline result — measure it and write it down.**

## §4 Deliverables beyond the standard row

1. ⚠⚠ **`controls/spellings.py` FROM THE START, both sides.** `ph07` is the only
   row that has discharged this and `ph03` owes both (`.memory-php/02-ladder.md`).
   **Do not ship a `fixed-R4 bound` alone.** Publish both numbers labelled:
   `R3ship − R4ship`, and cheapest-found in-contract `inf(R3 found) − R4ship`.
   ⚠ **No pair interval** — `min(R3 found) − min(R4 found)` differences two upper
   bounds and bounds nothing. Port `ph07`'s script; **import `measure.py`'s
   statistic rather than re-implementing it** (`ph07`'s first draft re-implemented
   it and landed 1 % off the record).
2. **The fixture rule** (`PROTOCOL_PHP.md` §A2a, both limbs): the fixture must
   **reach every arm and assert it**, and `selfcheck` must drive its two
   implementations **over a domain it constructs**, not over the shipped inputs.
   ⚠ **`ph03` shipped for a full task with `model.py` and `verus.rs` computing
   different functions and the fixture hid it.** Do not repeat that.
3. **`spec.md`'s hashed `why` must be true when you write it.** ⚠⚠ `ph07`'s was
   **not four stale figures but NINE — a whole pre-rebuild snapshot**, and **no
   gate could see it**, because the hash still matched text nobody had edited
   **and every qualitative verdict it supported was still right** (F54). **Write
   the `why` LAST, after every number is final**, re-derive each numeral from the
   record you are shipping, and **say in your report that you did.**
4. ⚠⚠⚠ **`PROTOCOL_PHP.md` §H — NEW, AND IT BINDS THIS TASK.** *A change to a
   validator lands with its **must-fire negatives** in the same change, or it
   does not land.* **Your `controls/*.py` are validators**, and so is anything
   you add under `harness-php/`. ⚠ **A green gate EXERCISES a control; it does
   not ATTACK it** — three passing rows say nothing about what your control does
   to a row that should fail. **Every control ships with at least one must-fire
   and one must-NOT-fire case, run, with output pasted.** This rule exists
   because a validator shipped with a 16-line derivation log and no control, and
   four defects followed.

## §5 Rules

- ⚠ **Citations resolve against the PINNED TARBALL only** (`SOURCES.md`).
- ⚠⚠ **`grep -a` ALWAYS** — `grep` dispatches to `ugrep`, which exits 1 with **no
  output** on the 41 non-UTF-8 corpus files. A silent empty result is the trap.
  **Ask about a FUNCTION, not about text.**
- ⚠⚠ **A probe that CANNOT EVALUATE must SAY SO and exit non-zero — never `ok`.**
- ⚠ **`env -u LD_PRELOAD`** for hand-run sanitizer probes; grep
  `AddressSanitizer`, not `ASan`.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`.
- **Keep the generator, delete the artefact** (`CLAUDE.md` rule 1).
- Everything claimed must have been **RUN**, output pasted.

## §6 What I am least sure of

1. ⚠ **That §3's canary survives contact with a REAL kernel.** I measured it on
   a probe I wrote, where I controlled the frame. **In the extracted kernel the
   `fd_set` and the canary are in whatever frame the lifted function has**, and
   `verbatim` means I do not get to add locals to it freely. **If honouring the
   tier costs you the oracle, say which you dropped and why** — and note that
   *"R1's fault is witnessed by construction (the index is provably ≥ 1024) and
   not by a detector"* is an acceptable result, plainly said. What is not
   acceptable is a canary that passes because the compiler moved it.
2. ⚠ **That `spellings.py` belongs in the first task rather than a follow-up.**
   `ph07` needed **11 gate rounds**. If carrying §4.1 turns this into two tasks,
   **say so and stop at a green row with the debt declared** — that is what
   `ph03` did, and the debt is now two rows old, which is why I am asking.
3. ⚠⚠ **That `verbatim` is right at all** — see §1. Two independent reasons to
   doubt it: the hash/stream unpacking (§1), and the oracle, because **if
   witnessing the fault requires surrounding the `fd_set` with scaffolding the
   original frame does not have**, that is a second departure. **Re-tier it if
   the evidence says so** — the tier is a cost statement, never a filter, and
   getting it wrong in the safe direction costs nothing.

---

⚠ **Out of scope, deliberately.** The manager found that `99e290f882c9` patches
**four** unchecked fd-set sites and the catalogue has **one** — `streamsfuncs.c:577`
(`FD_ISSET`, a read) and `ext/sockets/sockets.c:536,563` are uncatalogued, and
`sockets.c` has no rows at all (`.temp/mgr166/NOTES.md` §2). **That is
`TASK_PHP_026`'s question, not yours.** If your reading of the C bears on it,
**write a paragraph and move on** — do not adjudicate and do not build them.
