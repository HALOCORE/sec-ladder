# TASK_PHP_004 — land `TASK_PHP_003`'s corrections

**Role:** research engineer. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_004_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md`, then **`.tasks-php/TASK_PHP_003_REPORT.md`** (the
review you are landing), then `.tasks-php/TASK_PHP_002_REPORT.md` (what you are
correcting), `PLAN_PHP.md` and `.tasks-php/PROTOCOL_PHP.md`.

**The review found 2 blockers, 6 majors and 7 minors, six of them against the
manager's design.** Phase 0 does not count as done until B1 and B2 are closed.

⚠⚠⚠ **THE NO-TOUCH RULE STILL BINDS: do not edit anything under `harness/`,
`common/`, `patterns/`, `results/` or `pilot/`.** Both blockers are fixable
without a harness edit; the review says so and names where.

**Bracket the task**: `python3 harness/measure.py --check-stale` must print
`66 record(s) examined, 0 STALE` as your first and last command, both pasted.

---

## §1 The two blockers — close these first

### B1 — the "mandatory" symlink is enforced by nothing

`PROTOCOL_PHP.md:122` and `RECAP_PHP.md:165` call the `<row>/c/emalloc_shim.h`
symlink **mandatory**. Nothing checks it. The reviewer built a row that links the
shim without it: it **builds** (via `-I COMMON`) and the allocator lands in
**neither** digest. The failure it enables is concrete and permanent: fix the
shim → `--regen` → re-gate, and the gate record refreshes while the
**measurement** record stays `FRESH` for ever, carrying numbers taken under a
different allocator.

**Fix in `harness-php/gate.py`'s preflight** (the review's own recommendation —
no harness edit). ⚠ **A word in a document is not an enforcement mechanism.** Any
row that reaches the shim without the link must **fail loudly, before the tool
runs**.

⚠⚠ **Then give the fix a must-fire negative**: construct the row *without* the
link and show the preflight refusing it, and construct one *with* the link and
show it passing. A guard with no failing case is a guard nobody has tested.

### B2 — the allocator shim invents defects, in the file written to prevent that

`common-php/emalloc_shim.h:340` claims `__builtin_mul_overflow` is the *"same
predicate"* as PHP's `ZEND_SIGNED_MULTIPLY_LONG`. It is not.

✅ **Manager-verified in the pristine tarball.** `Zend/zend_multiply.h:22` guards
the exact `imul` arm with `#if defined(__i386__) && defined(__GNUC__)`. On
**x86-64 `__i386__` is not defined**, so PHP falls to the `#else` at `:34`:

```c
	long   __lres  = (a) * (b);
	double __dres  = (double)(a) * (double)(b);
	double __delta = (double) __lres - __dres;
	if ( ((usedval) = (( __dres + __delta ) != __dres))) {
```

— a **double-precision heuristic**, not an exact test. `__builtin_mul_overflow`
is exact. The reviewer measured **84,523 disagreements in 20 M samples, 100 % in
one direction: PHP raises `E_ERROR` where the shim allocates.**

⚠⚠⚠ **That is `PLAN_PHP.md` §4.3's own failure mode — a substituted primitive
inventing a defect — inside the file that exists to prevent it.** The earlier
PHP effort did exactly this with `malloc`-for-`emalloc` and published a false
explanation of an upstream fix.

**Fix:** reproduce PHP 5.0.0's **actual x86-64 predicate**, faithfully, and
line-cite it. ⚠ **Do not "improve" it** — the heuristic's inaccuracy *is* the
5.0.0 behaviour, and a more correct shim is a less faithful one. Ship a
differential probe over the same sample space showing **0 disagreements**, with a
must-fire control proving the probe can detect one.

---

## §2 The majors

3. **`root.py --sweep` cannot fail for 4 of its 7 links** — a hard-coded
   whitelist, and the engineer's own control happened to hit the one link it does
   not cover. ⚠ This is the **silent-skip** class this project has found ten
   times. Either make the sweep genuinely derive all seven, or **say in the
   docstring exactly which links it cannot check and why**. Do not leave it
   looking complete.
4. **`provenance.py` accepts an out-of-range span** (0 bytes) and never opens the
   kernel source, so `PLAN_PHP.md` §6's *"one-command check rather than a claim"*
   overclaims. Make it reject an empty or out-of-range extraction, and make it
   compare against the kernel it claims to have produced. ⚠ **Add the negative
   tests for both**, and correct §6's wording to what the tool actually does.
5. **`harness-php/*.py` is in no digest**, and `--no-provenance` leaves **no
   trace in the record**. A run certified by a tool nobody can pin is not
   certified. Fix the trace at minimum; say what the digest costs.
6. **Doc corrections**: `ph00-smoke/README.md` ships the three-command loop this
   task refuted (it is six, ~28 min); `PROTOCOL_PHP.md` §E's header says five
   over a six-command body. ⚠ `PROTOCOL.md` rule 13 — **when you correct a doc
   item, re-read its header and make it match**; a header that contradicts its own
   body is how this project published a limitation that did not exist.
7. **Settle the tree-set disagreement** the manager left open in `PLAN_PHP.md`
   §1: the reviewer counted 7 of 12 `zend_alloc.c` trees pristine, the manager 8
   of 13. Enumerate them, say which are patched and what the patch does, and
   confirm that it does **not** delete the truncation. ✅ The citation rule itself
   stands and is not in question — only its stated reason was wrong.

## §3 The minors

Land the seven from the review report. ⚠ **If you disagree with one, say so with
a measurement rather than landing it** — the reviewer is not automatically right
either.

---

## §4 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php4/`. Never `/tmp`. Keep the generator, delete the
  artefact; anything a record cites is evidence and stays.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — confirm an exact PID via
  `/proc/<pid>/cmdline`. The engineer leaked eleven shells here because
  `pgrep -f` matched their own command lines.
- ⚠ **`env -u LD_PRELOAD` for every hand-run sanitizer probe**, and grep for
  `AddressSanitizer`, not `ASan`.
- ⚠ **Do not edit files under a running gate.** `TASK_PHP_002` did, and had to
  discard a record and re-gate twice from a frozen tree.
- Everything claimed must have been **run**, output pasted.

## §5 The call I am least sure of

⚠ **B2's fix is the one I expect to be subtle, and I may be wrong about what
"faithful" means here.** Reproducing a double-precision heuristic *exactly*
across compilers is not obviously achievable — `-ffast-math`, x87 excess
precision and FMA contraction can all move it. **If a bit-exact reproduction is
not achievable, say so, quantify the residual disagreement, and put the number in
`spec.md` as a stated limitation** rather than shipping something that looks
exact and is not. A quantified, disclosed gap beats a false claim of fidelity.

Second: I have assumed **B1 is fixable in `gate.py`'s preflight with no harness
edit**, on the reviewer's word. **Verify that before building it.** If it needs a
harness edit, stop and report — that decision is the manager's, and it costs a
33-pattern re-gate.

---

**Running count: launched from 8.** ⚠ **`TASK_PHP_003` is not yet folded into
it** — it refuted the manager's stated expectation about where Phase 0 would
fall over (the digest gap **does** fire) and carried six findings against manager
design. **Reconciliation is the manager's job**; state what you refute and let
the manager carry it.

✅ **One thing worth knowing before you start, because it is the first time it has
happened on either programme: `TASK_PHP_003` checked every `file:line` the
manager marked ✅ and found ZERO unearned** — breaking the PAT side's run of four
consecutive reviews that each found one. **The marks are trustworthy; the
reasoning around two of them was not.**
