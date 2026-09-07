# `PROTOCOL_PHP.md` — the PHP programme's addendum

⚠⚠ **`.tasks/PROTOCOL.md` IS THE PROTOCOL AND IT IS REUSED UNCHANGED.** Roles,
the manager's 14 rules, the definition of done, the report format, the
reviewer checklist and the rules for every agent are programme-independent and
live there. **Read it first.**

**This file carries only what is NEW here, and deliberately restates nothing.**
Two copies of one rule is how both go stale — `.tasks/PROTOCOL.md` rule 13 is
that lesson, and it has already escaped into a published document once.

---

## A. Extraction — the step the PAT programme never had to take

PAT kernels are **invented**, so they are correct by construction with respect
to the thing they model. **PHP kernels are EXTRACTED, and extraction can lie
about the defect in both directions.**

### A1. Declare a tier, in `spec.md`, inside the hashed block

| tier | meaning |
|---|---|
| `verbatim` | the function lifts as-is; only `TSRMLS_*` / macro plumbing is removed |
| `narrowed` | a wrapper comes off (zval unpacking, argument parsing); **the body is unchanged** |
| `modelled` | the mechanism is re-expressed because the original cannot be lifted |

⚠ **A tier is a COST, NEVER A FILTER.** `RECAP_PHP.md` open item 4 records a
candidate rejected on extraction cost; the bar does not permit that, and the
manager owes a re-adjudication. `PLAN_PHP.md` §3 governs admission and it is
C-side only.

⚠ **Group candidates by C MECHANISM, never by file.** The corpus's
`c_file_line` names the **faulting frame**, which is nearly always executor
code, while the defect is usually one call down in a standalone container.
Reading an axis by `c_file_line` measures where PHP crashes, not where it is
wrong (`PLAN_PHP.md` §4.2a; the temporal miner refuted the manager on this and
the axis went from "needs the whole executor" to 21 of 23 families lifting).

### A2. The deletion ledger

**Every deletion is listed individually, in `provenance.deletions`, with a
line citation and a reason.** Not "macro plumbing removed" — one entry per
thing removed:

```json
"deletions": [
  {"what": "TSRMLS_DC", "where": "zend_alloc.c:142", "why": "thread plumbing, no semantics"},
  {"what": "ZEND_DEBUG arms", "where": "zend_alloc.c:153-165", "why": "the shipped 5.0.0 build is not a debug build; keeping them would ADD a poison-on-free PHP does not do"}
]
```

⚠ A deletion that CHANGES BEHAVIOUR is not a deletion, it is a `modelled`
tier. If you cannot write a `why` that ends in "no semantics", you are in the
wrong tier.

### A3. ⚠ Reachability is deliverable #1, in writing, before any rung exists

A corpus row's `root_cause_id` is a claim about **PHP**, not about the kernel
you are about to extract. **Settle the defect against the kernel, before
writing a single rung.** The PAT programme got its bug-class row wrong on four
patterns, once by a factor of 2.1e9, and those were guesses where these are
measured — *"should hold better"* is not *"did"*.

### A4. Fidelity evidence, before any rung

Reproduce the corpus's **recorded** crash category and, where recorded, its
operand values, with the same binaries clean on a benign input.
⚠ **Reproducing a DIFFERENT signal is a finding to state, not a failure to
hide** — a `SEGV` where the corpus says `heap-buffer-overflow` is a result.

---

## B. ⚠⚠⚠ The allocator rule

**Any php row that allocates links `common-php/emalloc_shim.h`, or states in
`spec.md` why not.** A substituted allocator is not neutral: an earlier effort
dropped plain `malloc` in and, as a direct result, reported a real defect as
unreachable *and then invented an explanation for the upstream fix*
(`PLAN_PHP.md` §4.3).

The shim reproduces **three distinct truncations**, all cited to the pristine
tarball and all demonstrated firing with positive controls by
`common-php/emalloc_probe.c`:

| | site | what |
|---|---|---|
| T1 | `zend_alloc.c:129`, `:135` | `unsigned int real_size` — an 18-EB request becomes a **2 GiB allocation that succeeds** |
| T2 | `zend_alloc.h:53` | `unsigned int size:31` — the **recorded** size, a *different* modulus |
| T3 | `zend_alloc.c:295` | `int final_size = size*nmemb` in `_ecalloc` — a third, **signed** truncation, found at `TASK_PHP_002` and not in `PLAN_PHP.md` |

⚠ **`_safe_emalloc` protects against none of them.** It checks in 64-bit
`long` (`zend_alloc.c:224-237`) and then calls the truncating `_emalloc`
(`:238`). A shim that models only `_safe_emalloc` is not faithful.

### B1. Three mechanical consequences

1. ⚠ **`crashes_pristine_5_0_0 = False` IS NOT EVIDENCE OF ABSENCE and is
   never an admission filter.** The size-class cache (`zend_alloc.c:150-168`,
   `:263-279`) means a freed block under 88 bytes is **not returned to
   `malloc`** and is handed straight back to the next same-class request.
   Measured at `TASK_PHP_002`: under ASan the *same* use-after-free is
   **reported on an uncached block and SILENT on a cached one**. A C kernel on
   plain `malloc`/`free` reproduces **more** of these than pristine PHP does.
2. **Fold `php_shim_tally()` into the kernel's `u64`**, so the defect lands in
   the checksum the gate compares across rungs and not only in a sanitizer.
3. ⚠ **Call `php_shim_reset()` at the top of every kernel call.** The driver
   loop runs the kernel thousands of times; a cache that survives across calls
   makes call *N* depend on call *N−1* and destroys the marginal-`Ir`
   subtraction every number rests on.

### B2. ⚠ The shim is a HEADER, and the row must symlink it into `c/`

`harness/build.py:163-165` compiles **exactly three translation units** and
adding a fourth means editing `build.py`, which stales all 33 PAT measurement
records. So the implementation is `static inline` in `emalloc_shim.h`;
`emalloc_shim.c` is a standalone-probe TU and is **not on the build path**.

One TU — `c/kernel.c` — does `#define PHP_SHIM_IMPL` before the include; every
other TU includes it plain.

⚠⚠ **AND THE ROW MUST CARRY THE SYMLINK:**

```sh
ln -s ../../../common-php/emalloc_shim.h patterns-php/<row>/c/emalloc_shim.h
```

**This is not cosmetic and not optional.** `check.py`'s `common/` globs are
`driver.*`, `*.py` and `layout/*.py`, **all non-recursive**, so
`common-php/emalloc_shim.h` is in *no* gate digest by name, and
`measure.py::measurement_sources` does not reach it at all. The symlink puts
the real content under `<row>/c/emalloc_shim.h` in **both** digests
(`glob` returns symlinks and `sha256_file` follows them — measured,
`TASK_PHP_002` T4). Without it, a row's measurement record does not pin the
allocator its numbers were taken with.

---

## C. R1h is the real upstream fix

`c/kernel_hardened.c` is the `fix_commit` patch **backported and sha-pinned**,
with the commit id in `spec.md`. The PAT programme has to argue its
hand-written hardening is fair; here we do not.

⚠ **An upstream fix is not automatically correct.** The earlier attempt
measured one that, backported, still left a reachable wild write in the arm it
does not guard. **That is a result, and one of the strongest a row can carry.
Report it; do not repair it.**

---

## D. The `provenance` block

Every row carries one **inside the hashed `slb-contract` block**, so the gate
pins it and drift is detectable. `PLAN_PHP.md` §6 has the schema;
`patterns-php/SOURCES.md` §5 has a filled example.

```sh
python3 harness-php/provenance.py <row>          # one row
python3 harness-php/provenance.py --all
python3 harness-php/provenance.py <row> --no-tarball   # PARTIAL: skips the excerpt hash
```

- `extract_sha256` is the load-bearing field: it makes *"this kernel came from
  those lines of that tarball"* a **one-command check** rather than a claim.
- The validator does **not** `exec` `extract_cmd`. It derives the excerpt from
  `c_file`/`c_lines` and *separately* requires `extract_cmd` to be the
  canonical spelling of those fields, so the two failures mean different
  things: a bad span, versus a command that does not describe the span.
- A row with **no** PHP source declares `"php_provenance": false` **with a
  `why`**. A row that merely omits the block is rejected — so a missing
  provenance is always a defect and never a shrug. `ph00-smoke` is the only
  row this is for.
- ⚠ **Cite the corpus CSV's `c_file_line`, verified against the pristine
  tarball. NEVER cite a reproducer `.php` header comment** — six of them
  describe 4.0.2 code that no longer exists at 5.0.0 and one says so in its own
  text. **A reproducer is an INPUT, not a citation** (`PLAN_PHP.md` §1).
- ⚠ **NEVER cite a build tree.** Every extracted PHP tree on this box is
  patched, two of them with the allocator patch that deletes the very
  truncation §B is about (`patterns-php/SOURCES.md` §3).
- `echoes: ["pNN"]` records where a `patterns/` row covers the same mechanism.
  ⚠ **It is a cross-reference for us and NEVER a filter** — `patterns-php/` is
  fresh, and *"that's p35's mechanism"* may not refuse a candidate
  (`PLAN_PHP.md` §3.1, `DP-03`).

---

## E. Running anything — the shim, and the one command that is not optional

**Never run `harness/check.py` directly on a php row.** Everything goes
through the driver, which builds the shim, verifies the digest bridge and
checks provenance first:

⚠⚠ **A BRAND-NEW ROW COSTS FIVE COMMANDS, NOT THREE, AND THE ORDER IS
LOAD-BEARING. MEASURED AT `TASK_PHP_002` — `ph00-smoke` needed all five:**

```sh
python3 harness-php/gate.py --tool build   <row> --all   # 1. the 28 binaries
python3 harness-php/gate.py --tool measure <row>         # 2. the matrix
python3 harness-php/gate.py --tool report  <row>         # 3. the table exists
python3 harness-php/gate.py                <row>         # 4. FAILS on tables
python3 harness-php/gate.py --tool report  <row>         # 5. re-render
python3 harness-php/gate.py                <row>         # 6. green
```

- ⚠ **Step 1 is not optional.** `measure.py` **builds nothing** — it measures
  whatever binaries happen to be in the build root. `TASK_PHP_002`'s first
  `measure` run reported `static: 1 cells` and wrote a one-cell record without
  complaining.
- ⚠ **Steps 4→6 are the `gate → report → gate` chain, and no amount of
  reordering removes it.** `report.py`'s audit section renders from
  `results/gate/<row>.json`, which does not exist until a gate has run; and
  the gate's stage 9c compares the published table against a fresh render of
  **this run's** record. So the first gate on a new row *must* fail with
  `[tables] … cites no contract_sha256 at all`. `check.py::check_table_render`
  says so itself: *"`harness/report.py <row>` reads that record only after
  this run has written it, which is why `report.py` comes after the gate and
  not before."*
- ✅ **`check.py::check_published_tables`'s own "three commands, not two"
  message is about a DIFFERENT case** — a row with no measurement record at
  all. Both are true; the five-command figure is the one to plan against.

⚠⚠ **AND COMPUTE `contract_sha256` THE WAY THE GATE DOES.**
`check.py::read_contract` matches

```python
re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)
```

— the capture **keeps the newline before the closing fence**. The obvious
spelling `` ```slb-contract\n(.*?)\n``` `` hashes one byte less and gives a
different number for **every** pattern in the tree. `p01` is
`5360d6f3dd7a…` by the gate's spelling and `b5d7dc8dd173…` by the naive one,
and `5360d6f3…` is what its committed gate record carries. **A `PROTOCOL.md`
rule 6 disclosure taken with the wrong regex is unverifiable against the
record it exists to be checked against** — `ph00-smoke`'s first one was, and
is disclosed in its `NOTES.md` rather than quietly replaced.

⚠⚠ **AND `idiom.why` HAS A MANDATORY 11,003-BYTE TAIL.**
`[idiom-named-spelling]` hard-fails any `why` that does not end with the
shared named-spelling paragraph, byte-identical across every `spec.md`
(sha256 `59748cce2db5…`). **`RECAP_PHP.md`'s *"a `spec.md` `why` stays ≤ 200
words"* can therefore only mean 200 words of ROW-SPECIFIC prose before that
paragraph** — p01's row-specific half is 201 words and 1,177 chars, so p01
already complies with the rule the size note was written against it for.
⚠ Do not write the literal phrase `NAMED-SPELLING STANDARD` anywhere earlier
in the file: the gate's own reproduction command uses `str.find`, takes the
FIRST occurrence, and a stray one in your prose makes it hash the wrong
bytes. Measured at `TASK_PHP_002`.

### E1. The no-touch rule, restated only where it bites a php agent

`PLAN_PHP.md` §2.1 is the rule. What it means at the keyboard:

- **Never add, edit or delete a file under `harness/`, `common/`, `patterns/`,
  `results/` or `pilot/`.** Adding one `.py` to `harness/` or `common/` costs a
  33-pattern re-gate; editing `build.py` costs a full re-measure.
- `python3 harness/measure.py --check-stale` → **`66 record(s) examined, 0
  STALE`** at the start **and end** of every php task. ⚠ 66 is gate **plus**
  measurement records; a commit message has already misread that as
  measurement records alone.
- ⚠ **The coupling runs the other way too:** a future PAT `harness/*.py` edit
  will stale php gate records. That is correct — the dependency is real — but
  it means the two programmes are coupled through the harness even though
  neither writes the other's tree.

### E2. `common-php/`

Anything you add there must end up in **some** digest.
`python3 common-php/digest_bridge.py --regen` after every change, and
`gate.py` verifies it before every run. ⚠ **The bridge covers the GATE digest
only** — see §B2 for the measurement half.

---

## F. What a php row owes that a PAT row does not

A checklist, not a restatement of the definition of done:

1. `provenance` block, validating (`harness-php/provenance.py <row>`).
2. Tier declared, deletions itemised with line citations.
3. Reachability settled **in writing, before any rung**.
4. Fidelity evidence against the corpus's recorded crash category.
5. `kernel_hardened.c` = the real `fix_commit`, sha-pinned.
6. The allocator: linked and symlinked into `c/`, or a stated reason not to.
7. `echoes: [pNN]` where a PAT row shares the mechanism.
8. ⚠ **A cost with no mechanism is an incomplete row** (`PLAN_PHP.md` §7 rule
   12). Name *why* from the disassembly: which check elided, which load came
   back, what LLVM failed to hoist. This is the item that decides whether the
   crash course is useful.
