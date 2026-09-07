# TASK_PHP_013 — build `ph03`, the first real PHP row

**Role:** research engineer. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_013_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md`, then `.tasks-php/PROTOCOL_PHP.md` (the php addendum —
extraction tiers, the deletion ledger, the allocator rule, the `provenance`
block), `PLAN_PHP.md` §3 §4 §5 §6, `patterns-php/CATALOGUE.md` (`ph03`, Part A
and Part B), and `.tasks-php/TASK_PHP_012_REPORT.md` §3 — **which validated this
row end to end and is your starting evidence, not a claim to re-derive from
scratch.**

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **`.web/` is being edited by a CONCURRENT SESSION — never `git add -A`, and do
not touch it.**

**Bracket**: `harness/measure.py --check-stale` → `66/0` and
`harness-php/gate.py --tool measure --check-stale` → `2/0`, first and last.

---

## §0 ⚠⚠⚠ THIS IS THE FIRST ROW. TWELVE TASKS HAVE PRODUCED NONE.

Everything before this was infrastructure, mining, a catalogue and their
reviews. **`ph03` is the first time the pipeline runs on a real PHP kernel**:
extraction from the pinned tarball, a `provenance` block, `kernel_hardened.c`
from the **real upstream fix**, all five rungs, the gate, the measurement.

⚠ **Expect the pipeline to be wrong in ways nine reviews could not find, because
none of them had a row.** **That is the point of this task.** When something
does not fit — a `spec.md` pin that cannot be stated, a `PROTOCOL_PHP.md` rule
that assumes a shape this row does not have — **report it as a finding rather
than forcing the row into it.** A row bent to fit a wrong rule teaches nothing.

## §1 The kernel

**`ph03` — `php_uudecode`, `ext/standard/uuencode.c`, CRASH-115.**
Tier **`verbatim`**. Catalogue Part B has the mechanism, trigger, benign
behaviour, blob shape and the risk.

The defect, in one line: the inner decode loop's bound is
`ee = s + (len == 45 ? 60 : (int) floor(len * 1.33))` at `:141` — **computed
from a length byte inside the data** — while the true end `e = src + src_len`
sits unused at `:133`. Both an over-read and an over-write follow.

⚠ **`TASK_PHP_012` measured the adversarial fault as a WRITE at `uuencode.c:144`**,
matching the corpus's independent record. **The corpus's own CWE is CWE-125
(read) and its `root_cause_id` says *"writes past emalloc"*.** Both limbs are
real; **`spec.md` must say which one the oracle detects, and not silently pick
one** (`PLAN_PHP.md` §4.2).

⚠ **`floor(len * 1.33)` is floating point.** An extraction that "tidies" it to
integer arithmetic **changes which `len` values trigger** — it is part of the
mechanism and is pinned.

## §2 R1h — the REAL fix, and it is fetchable

✅ **Manager-verified before this file was written.** `git fetch` of a bare SHA
is refused by the server; **the patch URL works**:

```sh
curl -sSL https://github.com/php/php-src/commit/f95c1df58349.patch
```

→ Ilia Alshanetsky, 2004-08-24, *"Fixed bug #29821 (Fixed possible crashes in
convert_uudecode() on invalid data)"*, `ext/standard/uuencode.c`, +17 lines:

```c
if (len > src_len) { goto err; }      /* before total_len += len */
ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));
if (ee > e) { goto err; }             /* the bound */
...
err:
    efree(*dest);
```

**`c/kernel_hardened.c` is `c/kernel.c` plus exactly these lines.** Record the
full sha (`f95c1df583490814b0501c56f59671193a57507b`), the subject, the date and
the sha256 of the patch bytes in the `provenance` block, and **keep the patch
under the row** so the citation survives without the network.

⚠⚠ **`TASK_PHP_012` reports that this fix leaves a SECOND, DISTINCT over-read
REACHABLE.** If that holds, it is `PROTOCOL_PHP.md` §C's strongest available
result — *the upstream fix is incomplete* — **on row 1.** **Verify it with a
detector and a must-fire control, and if it does not hold, say so.**

## §3 The five rungs

`PLAN_PHP.md` §5. **R1 C · R2 safe-naive Rust · R3 safe-tuned Rust · R4 unsafe
Rust · R5 unsafe + Verus**, × `{O0,O3}` × `{isolated,whole}`, plus **R1h**.

⚠ **`DP-02`: R4/R5 may land as FINDINGS.** If Verus cannot state the obligation
for a `floor()`-derived bound, **that is a result to report, not a reason to
change the kernel.** ⚠⚠ And `CLAUDE.md` rule 6: **nothing about Rust, Verus,
Miri or cost may change what the C row is.**

⚠ **Read `../LearnVeri/PITFALLS.md` before debugging Verus**, and grep the
**pinned** `~/tools/verus/vstd/` — including **`std_specs/`**, where the specs
for std types actually live. A trait declaration in `vstd/<mod>.rs` is **not**
the specification, and that exact confusion has produced a false *"no spec
exists"* claim twice on the PAT side.

## §4 The allocator

⚠ **Every php row carries `c/emalloc_shim.h` as a symlink — unconditionally**,
whether or not it allocates (`RECAP_PHP.md` open item 10, `TASK_PHP_008`). The
preflight refuses the row otherwise.

`ph03` **does** allocate: `emalloc(ceil(src_len * 0.75) + 1)` at `:131`.
✅ The catalogue rates it `emalloc_dependent: false` — the allocation is correct
and small, and the defect is a loop bound. **Confirm that**, because it decides
whether the shim's truncation is in play at all, and state it in `spec.md`.

## §5 Gate, measure, and the cost

`PROTOCOL_PHP.md` §E: **six commands, ~28 min.** Budget it; do not batch edits
into a running gate (`TASK_PHP_002` discarded a record that way).

⚠ **`RECAP_PHP.md` open item 9 and F14 both bind here:**
- **no php `Ir` is comparable to any PAT `Ir`**, and **no two php runs are
  comparable to each other** unless the env block matches — **so do not put a
  `pNN` number next to a `phNN` one anywhere**, including in prose;
- **`0 STALE` means "every source that was PINNED still matches"**, not
  "everything is pinned".

## §6 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php13/`. **Never `/tmp`.** ⚠ `.temp/php12/` holds the
  row's validation harness — **reuse it.** Keep generators, delete binaries.
- ⚠ **Citations resolve against the PINNED TARBALL only** (`SOURCES.md`).
- ⚠ **`env -u LD_PRELOAD`** for hand-run sanitizer probes; grep
  `AddressSanitizer`, not `ASan`.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`.
- Everything claimed must have been **RUN**, output pasted.

## §7 The calls I am least sure of

1. ⚠⚠ **That `spec.md`'s machine-readable pins, designed for invented PAT
   kernels, fit an EXTRACTED one at all.** `patterns/p01-array-sum/spec.md` is
   the template and it pins obligation counts, every `requires`/`ensures`, the
   driver loop, an `Ir` floor, identity levels and a Miri policy. **Some of
   those may be meaningless for a row whose C came out of a tarball.** **Tell
   me which, rather than inventing a value to fill the field.**
2. ⚠ **That one row is enough to shake the pipeline out.** If you finish and
   believe the second row will hit a different class of problem, **say what it
   is** so the batch order can be changed before five more are built.
3. ⚠ **That the `floor()` double is reproducible across the eight build cells.**
   `TASK_PHP_004` had to prove exactly this for the allocator's overflow
   heuristic. **If `-ffast-math` or LTO moves which `len` values trigger, that
   is a finding and the row needs a stated flag scope.**

---

**Running count: launched from 61.** `TASK_PHP_012` refuted the manager's
first-row pick **with a measurement rather than an argument** — `ph11`'s safe
and unsafe Rust rungs emit byte-identical `Ir` and both beat C — and found the
catalogue's `ph15` modelled nothing. ⚠ **It also found *"a kill written as a set
hides its members"* twice more, making three; and that the coverage checker
counted a mention in the kill table as coverage.**
**Reconciliation is the manager's job** — state what you refute and let the
manager carry it.
