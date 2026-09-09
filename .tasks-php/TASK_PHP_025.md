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

`fds` is **the caller's**: `fd_set rfds, wfds, efds;` at `:657` in
`PHP_FUNCTION(stream_select)`. ✅ **Confirmed exactly**, including that
`TASK_PHP_020_REPORT.md:131`'s `:658` is off by one and harmless.

**Machine facts, measured** (`.temp/mgr166/fdfacts.c`): `FD_SETSIZE 1024`,
`sizeof(fd_set) 128` bytes, index 4096 → word 64 → **byte offset 512, past the
object**. `FD_SET` is a pure bit-set macro and **never consults the fd table**.

⚠⚠ **TWO TRIGGERS, AND THE TASK MUST NOT BLUR THEM.** The *PHP-level* trigger
needs > 1024 real streams and an `RLIMIT_NOFILE` to match. The *kernel-level*
trigger does not — the extracted kernel takes a blob of indices, and any index
≥ 1024 is out of bounds. **Both are true.** `PLAN_PHP.md` §4.2's reachability
deliverable is about the kernel; the PHP-level statement belongs in `NOTES.md`
as the row's provenance, not as its trigger.

**Tier `verbatim`** — it is a `static` helper, so the lift is the function
(`UPSTREAM_001.md` §6). ✅ Already tier-checked; do not re-tier it.

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
Options, in the order I would try them — **but this is yours to decide and
report, not mine:**

1. **A canary/checksum oracle** — neighbouring objects in the same frame with
   known contents, checked after the kernel runs. The catalogue block already
   recommends this. ⚠ It depends on frame layout, so **it must be verified to
   actually neighbour the `fd_set` at BOTH `-O0` and `-O3`**, and a canary the
   compiler reorders away is a probe that silently passes.
2. **`_FORTIFY_SOURCE`** — real, upstream, and it fires. ⚠ But it is a *third*
   configuration beside the plain and sanitizer builds, and `.memory-php/02`'s
   rule is that **a sanitizer limb is a claim about YOUR toolchain** — the same
   caution applies doubled here.
3. **A heap `fd_set`** so ASan's redzone is in range. ⚠⚠ **This changes the
   storage class the row is ABOUT** (`ph17` is already catalogued as exactly
   that variation). **If you do it, it is a control, never the row.**

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
3. **`spec.md`'s hashed `why` must be true when you write it.** ⚠⚠ `ph07`'s
   cites four figures its own rebuild refuted, **and no gate can see it** because
   the hash still matches the unedited text. **Write the `why` LAST, after every
   number is final**, and say in your report that you did.

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

1. ⚠⚠ **That §3 has a good answer at all.** It is possible the honest outcome is
   *"R1's fault is not observable by any oracle we are willing to ship, so the
   row's R1 rung is witnessed by construction (the index is provably ≥ 1024) and
   not by a detector."* **That is an acceptable result — say it plainly if it is
   the true one.** What is not acceptable is a canary that passes because the
   compiler moved it.
2. ⚠ **That `spellings.py` belongs in the first task rather than a follow-up.**
   `ph07` needed **11 gate rounds**. If carrying §4.1 turns this into two tasks,
   **say so and stop at a green row with the debt declared** — that is what
   `ph03` did, and the debt is now two rows old, which is why I am asking.
3. ⚠⚠ **That `verbatim` survives the oracle.** If witnessing the fault requires
   surrounding the `fd_set` with scaffolding the original does not have, the tier
   may really be `narrowed`. **Re-tier it if the evidence says so** — the tier is
   a cost statement, never a filter, and getting it wrong in the safe direction
   costs nothing.

---

⚠ **Out of scope, deliberately.** The manager found that `99e290f882c9` patches
**four** unchecked fd-set sites and the catalogue has **one** — `streamsfuncs.c:577`
(`FD_ISSET`, a read) and `ext/sockets/sockets.c:536,563` are uncatalogued, and
`sockets.c` has no rows at all (`.temp/mgr166/NOTES.md` §2). **That is
`TASK_PHP_026`'s question, not yours.** If your reading of the C bears on it,
**write a paragraph and move on** — do not adjudicate and do not build them.
