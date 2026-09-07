# PLAN_PHP — the PHP programme (`patterns-php/`)

**One sentence.** Take real memory-safety defects out of PHP 5.0.0's C source,
build each one as a self-contained kernel at the same five rungs the PAT
programme uses, and measure what safety costs — so that the people porting PHP
to safe Rust can be handed a crash course grounded in *their own code* rather
than in invented examples.

> **Status.** Written 2026-09-07 at the opening of the programme. Nothing is
> built. §8 is the schedule; §10 is the decision register. Everything here is a
> design decision, not a measurement — **no number in this file has been
> measured yet**, and any that appears is cited to where it came from.

---

## §0 What this is, and what it is not

| | |
|---|---|
| **It is** | a **fresh, self-contained** corpus. A report will eventually be written from `patterns-php/` **alone**, so every row must stand on its own evidence. |
| **It is not** | an extension of `patterns/`. That corpus is our internal understanding of the pattern space; it is not the public result. |
| **What carries over** | the *method* — the five rungs, `spec.md` pins, an independent `model.py`, the gate, the manager→engineer→reviewer loop, and every hard-won measurement rule. |
| **What does not carry over** | `patterns/`'s **rows**. A php row is never killed because a `pNN` already has that mechanism (§3). |
| **Deliberately out of scope** | the existing Rust port at `php-in-safe-rust/php-rust/`. See §5.4. |

---

## §1 The corpus, and the citation base

**PHP 5.0.0 is the single citation base. PHP 4.0.x is ignored entirely.**

Every `file:line` in this programme is cited against the **pristine museum
tarball**, never against a build tree:

```
php-5.0.0.tar.gz
sha256  5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
size    5595997 bytes        entries  3815
found   /home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
read    tar -xzOf <tarball> php-5.0.0/<path> | sed -n '<a>,<b>p'
```

⚠⚠ **THIS PARAGRAPH SAID *"every extracted tree on this box is patched"* AND
GAVE `REAL_SIZE(size)→(size)` AS THE REASON. BOTH WERE WRONG — REFUTED AT
`TASK_PHP_003`, and the manager's recount agrees: of **13** extracted
`zend_alloc.c` trees, **8 are byte-identical to the pristine tarball**, the
allocator patch is in a **small minority**, and ✅ **it does not delete the
truncation anyway.**

✅ **THE RULE SURVIVES; ONLY ITS STATED REASON FELL.** Cite the tarball, because
a *some-trees-are-patched* corpus is one where you cannot tell by looking which
tree you are in — and `build/php-4.0.2/` really does carry modern-gcc patches,
and 4.0.x is out of scope regardless (`DP-06`). ⚠ **A rule that survives with a
false reason is the shape this project has already been burned by twice** (a
right verdict resting on a wrong reason), so the reason is corrected here rather
than quietly dropped.

✅ **THE TREE-SET DISAGREEMENT IS SETTLED — `TASK_PHP_004`, and it was a SCOPE
disagreement, not a content one.** There are **12** `php-5.0.0/Zend/zend_alloc.c`
files on this box, plus **one** `php-4.0.2` one. **8 of the 12 are
byte-identical** to the tarball. So the manager's **8** and **13** are each
right about a different set (13 only if the 4.0.2 tree, which cannot be
pristine-5.0.0, is counted); the reviewer's **12** is right and their **7** is
one short. The full enumeration, with each patch and what it does, is
`patterns-php/SOURCES.md` §3; the raw list is `.temp/php4/trees_500.txt`.
⚠ The consequential patch is **`ZEND_DISABLE_MEMORY_CACHE 0 → 1`** in the two
`-nocache` trees — an allocator with **no size-class cache at all** — and it was
named nowhere. `REAL_SIZE(size)→(size)` is in exactly **one** tree, at `:132`,
and ✅ **verified not to delete the truncation**: `real_size` is still
`unsigned int` and the store at `:129`/`:135` is what truncates
(`.temp/php4/real_size_probe.c`).

⚠⚠ **The tarball lives under another project's gitignored `.temp/`, which that
project's own convention makes deletable at any time.** This is the hazard
`common/census/README.md` already names — *"a census whose corpus cannot be
re-identified is a census nobody can check"*. **Phase 0 must therefore land a
`patterns-php/SOURCES.md` carrying the tarball sha256 and a per-file manifest**,
the same way `common/census/php.manifest` does for 4.0.2.

### ⚠⚠⚠ THE CSV IS AUTHORITATIVE; THE REPRODUCER `.php` COMMENT IS NOT

**Found independently by the spatial and temporal miners, and manager-verified.**
`index.csv`'s `c_file_line` resolved **exactly** on every citation either agent
checked. The `input/crash/*.php` **header comments do not** — six of them
describe PHP **4.0.2** code that no longer exists at 5.0.0, and
`CRASH-017.php`'s says so in its own text:

```
 * php-4.0.2:ext/standard/url.c:345:  str = emalloc(3 * len + 1);   // int arith
```

Pristine 5.0.0 `ext/standard/url.c:499` is `safe_emalloc(3, len, 1)` — **the int
overflow is already fixed**, which is why the CSV points at `zend_alloc.c`.
⚠⚠ **Following the comment instead of the CSV would have inverted the verdict**:
substitute plain `malloc` and `malloc(4 GiB)` succeeds under overcommit, so the
defect vanishes. §4.3 firing before a kernel was extracted.

Also drifting: two `root_cause_id` strings (`…line738` → really `:734`;
`…line218` → really `:247`), `CRASH-012.php`'s header (`array.c:1645` is a `}`;
the CSV's `:2060` is right), and `CRASH-066`'s `.re` cross-references (+5 / −6).

**Rule: cite the CSV line, verified against the pristine tarball. Never cite a
reproducer comment. A reproducer is an INPUT, not a citation.**

### The three mining substrates

| substrate | what it gives | path |
|---|---|---|
| **166-root-cause corpus** | per row: `root_cause_id`, `cwe`, `c_file_line`, **`fix_commit`**, `crashes_pristine_5_0_0` (60 True), and a reproducing `.php` | `paper/evaluation/security/vuln-corpus-5.0/index.csv` + `input/crash/` |
| **20 invariants, blind-labelled** | an independent C-side classification: obligations, T1/T2/T3 tiers, per-case labels produced by analysts **forbidden to read the Rust port**, against a vocabulary frozen and committed before labelling | `paper/invariants-list.md`, `paper/invariants-166.json` |
| **ASan on real traffic** | ⚠ **THIS ROW SAID "123 ASan reports" AND THAT WAS A MANAGER MISREAD THAT REACHED THREE TASK PROMPTS** (`TASK_PHP_001`). `REPORT.md`'s 123 is one curated pass (18 apps × 8 pages) and the column beside it reads **7 DISTINCT SITES**; the real population is `asan-logs/` = **2534 files / 3199 report occurrences**. ✅ Manager-verified. **Quote "7 distinct sites" for independent defects and the occurrence counts for frequency — never 123 as a census.** | `php-in-safe-rust/.temp/san_tests/` |

⚠ The `fix_commit` column is worth more than it looks: it means **R1h is the
real upstream patch and the adversarial input is the real reproducer**, neither
invented. The PAT programme has to argue that its hand-written
`kernel_hardened.c` is a fair hardening; here we do not.

### Axis coverage — why this corpus, for these three axes

Derived from `index.csv` (2026-09-07), against `composition.py --check` on the
built PAT tree:

| axis | CWEs | php rows | `patterns/` has |
|---|---|--:|--:|
| **temporal** | 416 (56) · 401 (15) · 562 (5) · 590 (4) · 415 (2) · 911 (2) · 824 (1) | **85** | 6 |
| **spatial** | 125 (22) · 787 (12) · 190 (13) | **47** | 15 |
| **type / init** | 843 (11) · 476 (14) · 664 (5) · 908 (2) · 822 (1) · 457 (1) | **34** | 2 |

The two axes the PAT programme is thinnest on are the two this corpus is
richest in. That is the programme's structural argument for existing.

---

## §2 Infrastructure — the parallel tree, and the one rule that matters

### 2.1 ⚠⚠⚠ THE NO-TOUCH RULE

Two globs decide the cost of every infrastructure decision here:

```
harness/check.py     srcs = … glob(REPO/harness/*.py) …      → gate  source_sha256   (all 33)
                              glob(REPO/common/*.py) …
                              glob(REPO/common/driver.*) …
harness/measure.py   measurement_sources() = … harness/{build,asm,measure}.py …
                                              common/{driver.*,slb.py}          → MEASUREMENT source_sha256   (all 33)
```

Therefore:

| act | cost |
|---|---|
| add **any** `.py` to `harness/` or `common/` | **33 gate records stale** → a full re-gate sweep (≈2 h) |
| edit `harness/build.py` (needed for a second pattern root) | **33 measurement records stale** → 33 re-measures **+** `report.py` **+** a second gate run *per pattern* |
| ~~import `harness.build` and rebind its roots~~ | ⚠ **does not work — 5 hard-coded paths, §2.1a** |
| **run the unmodified harness through a SYMLINK ROOT** (§2.1a) | **zero** — manager-verified against a committed digest |

**The rule: the PHP programme never edits `harness/` or `common/`.** Reading and
executing a file does not move its hash; only editing does.

### 2.1a ⚠ HOW it reuses them — MEASURED, and the first design was WRONG

This section originally said *"import the modules and rebind `build.PATTERNS`,
`measure.RESULTS` and the gate's output root"*. **That does not work, and the
manager ran it before writing the task file** (`PROTOCOL.md` rule 14). Five
paths are **hard-coded** and follow no rebind:

```
harness/report.py:89     os.path.join(REPO, "patterns", pattern, "spec.md")
harness/report.py:238    os.path.join(REPO, "patterns", pattern, "spec.md")
harness/check.py:8903    os.path.join(REPO, "results", "tables", f"{pat}.md")
harness/check.py:9128    os.path.join(REPO, "results", "tables", want)
harness/check.py:10534   os.path.join(REPO, "results", "gate")
```

✅ **What works instead, and it needs no wrappers at all: a SYMLINK ROOT.**
Every module derives `REPO = dirname(dirname(abspath(__file__)))`, and
`os.path.abspath` **does not resolve symlinks** — so running the *unmodified*
gate out of a shim directory of symlinks makes `REPO` the shim, and *every*
path, hard-coded ones included, follows:

```
<shim>/harness      -> ../harness          (the real, unmodified PAT harness)
<shim>/common       -> ../common-php       (§2.2)
<shim>/patterns     -> ../patterns-php
<shim>/results      -> ../results-php
<shim>/verus_run.py -> ../verus_run.py
```

**Manager-verified, and the check was chosen so that it could fail:** the source
digest computed through the shim for `p01` was compared against the *committed*
`results/gate/p01-array-sum.json`:

```
shim keys      35
committed keys 35
KEYS IDENTICAL  : True
HASHES DIFFERING: none
```

Identical keys **and** identical hashes, because `relpath(s, REPO)` yields
`harness/check.py` either way and `sha256_file` reads through the symlink. So a
php gate record carries correct, real provenance for the harness it actually
ran.

⚠ **Two consequences to plan for, not to be surprised by:**

1. **A future PAT `harness/*.py` edit will stale php gate records too.** That is
   *correct* — the dependency is real — but it means the two programmes are
   coupled through the harness even though neither writes the other's tree.
2. **`common-php/` is in NO digest under the glob as written** (`srcs` names
   `common/`, not `common-php/`). The shim's `common ->  common-php` symlink is
   what closes this: php-only files land under the key `common/…` in *php*
   records only, and `common-php/` re-exports the PAT `common/driver.*` and
   `slb.py` it reuses. ⚠ **Phase 0 must verify this leaves nothing unhashed** —
   an unhashed shared file is the exact gap that cost the PAT programme ten
   committed control sources in no digest at all.

⚠ This is not caution for its own sake. `RECAP_PAT.md` records the measured
consequence of the alternative: *"one harness edit, one 30-minute gate re-run"
is true of `check.py` and **false of `build.py`** — that costs a full re-measure
and churns published timing prose."*

**Acceptance test for Phase 0, and it must be run before and after:**
`python3 harness/measure.py --check-stale` → **0 STALE / 66 examined**.
⚠ 66 is gate **plus** measurement records; a commit message has already misread
that as measurement records alone.

### 2.2 The tree

```
.temp/php-root/        the SYMLINK SHIM the gate is run out of (§2.1a); gitignored,
                       rebuilt by harness-php/root.py -- a derived artefact
patterns-php/          the rows.  pNN → phNN-<slug>            (numbering: §2.3)
patterns-php/SOURCES.md  tarball sha256 + per-file manifest    (§1)
harness-php/           the driver: builds the shim root and invokes the UNMODIFIED
                       PAT gate through it; adds php-only stages of its own
common-php/            php-only shared code — payload decoders, emalloc_shim  (§4.3)
                       plus re-exports of the PAT common/ files it reuses (§2.1a)
results-php/           gate + measurement records, tables
.tasks-php/            TASK_PHP_NNN.md specs + reports; see its README.md.
                       PROTOCOL_PHP.md is an ADDENDUM to .tasks/PROTOCOL.md,
                       not a fork.  ⚠ DOTTED because .tasks/ is dotted, while
                       results-php/ is NOT because results/ is not: the mirror
                       matches the PAT tree name for name, for auditability
.memory-php/           the php programme's authoritative layer
PLAN_PHP.md            this file
RECAP_PHP.md           the handoff document — START HERE for this programme
```

- **`.tasks/PROTOCOL.md` is reused unchanged** — roles, the manager's rules,
  definition of done, the reviewer checklist are all programme-independent.
  `.tasks-php/PROTOCOL_PHP.md` is an **addendum** carrying only what is new
  (extraction, provenance, the allocator). Forking the protocol would double
  the maintenance of the one document both programmes rely on.
- `verus_run.py` at the repo root is **reused read-only**. Executing it is free.
- `.web/` is untouched: it derives its pattern list from `results/gate/`, so
  `results-php/` is invisible to it until we deliberately teach it. **Do not
  teach it before the php corpus has something worth publishing.**

### 2.3 Naming

`ph01-<slug>`, `ph02-<slug>`, … — a distinct prefix from `pNN` **on purpose**,
so that no cross-citation between the two programmes can ever be ambiguous.
(The PAT programme's own `D1` records what two ladders in one repo cost.)

---

## §3 The admission bar

**Inherited verbatim from `.memory/02-bench-rules.md` — a candidate is admitted,
or not, SOLELY on whether the C program makes sense:**

1. ✅ correct on normal/benign inputs, so performance is measurable;
2. ✅ exhibits the target error on ≥1 adversarial input — **demonstrated with a
   detector firing and a positive control that must also fire**, not argued;
3. ✅ fits the kernel shape: a flat blob in, a `u64` out, the shared driver
   loop. A structure may live *inside* the kernel driven by an opcode stream
   decoded from the blob (`p27` holds 32 raw pointers this way);
4. ✅ `c/kernel_hardened.c` differs from `c/kernel.c` by the safety line and
   nothing else — **and here it is the real upstream `fix_commit`** (§4.4).

**⚠⚠⚠ NOTHING about Rust, Verus, Miri, cost gradients or what the ladder can
"price" may EVER remove a row.** *"Safe Rust can't express it"*, *"safe Rust
reproduces the bug bit-identically"*, *"there's no cost gradient"*, *"the R5
can't state the obligation"*, *"Miri doesn't see it"*, *"the bug is in-bounds so
it's logical not temporal"* — **all findings, never kills.** The PAT programme
lost six admissible rows to this bias precisely because it lived in the bar
rather than in any one row, where no row-level review could see it.

### 3.1 ⚠⚠ DUPLICATION — THIS IS WHERE THE PHP BAR **DIFFERS** FROM THE PAT BAR

| | PAT (`patterns/`) | **PHP (`patterns-php/`)** |
|---|---|---|
| duplicates a **`patterns/`** row's C mechanism | n/a | ✅ **ADMITTED. Not a consideration at all.** |
| duplicates another **`patterns-php/`** row's C mechanism | kill | ⚠ **a slight variation is ADMITTED as its own row** |
| C-side duplication, exact | kill | kill |

**User decision, 2026-09-07, and it supersedes `CLAUDE.md` rule 6's duplication
clause for this corpus only:** *"for patterns-php/ it is fresh — we don't
consider duplication with patterns/ at all, because later we are picking
patterns-php/ only to write a self-contained report. patterns/ is what we
internally know … Even within patterns-php, slight variations I am still okay
with as a different pattern."*

**Consequence, and it must not be quietly re-tightened:** an engineer or
reviewer may **not** refuse a php candidate with *"that's p35's mechanism"* or
*"that's p02 again"*. Knowledge from the PAT row carries over and should be
cited; the row still gets built. A php row that replicates a PAT mechanism **at
a real call site** is a *replication*, which is evidence.

⚠ The one thing still owed: each row records `echoes: pNN` where a PAT row
covers the same mechanism, **as a cross-reference for us, never as a filter**.

### 3.2 The spatial ban is lifted here

`RECAP_PAT.md` records a standing user priority — **no new spatial rows** — under
which the biggest documented coverage gap in the whole project was refused:
`ptr_offset`, the pointer-cursor walk, which the idiom census found in **all 22
corpus programs**, ranked 2nd or 3rd in 15, share 0.4 %–26.1 %, median 6.9 %,
and **zero in all 33 kernels**. That ban scoped `patterns/`. The user has asked
for spatial coverage in `patterns-php/`, and PHP's parsers are built out of
exactly that idiom (`ext/standard/url.c`'s scheme scan reads `*(e+2)`, `*(e+3)`,
`*(e+5)`). **A php spatial candidate whose C mechanism is a pointer cursor
rather than an index compare is worth more than one that is not**, and the
mining task flags them explicitly.

---

## §4 Extraction — the step the PAT programme never had to take

PAT kernels are **invented**, so they are correct by construction with respect
to the thing they model. PHP kernels are **extracted**, and extraction can lie
about the defect in both directions. This is the single largest new risk and it
has already produced a documented failure (§4.3).

### 4.1 Declared tiers

Every row declares its tier in `spec.md`, inside the hashed block:

| tier | meaning |
|---|---|
| `verbatim` | the function lifts as-is; only `TSRMLS_*` / macro plumbing is removed |
| `narrowed` | a wrapper comes off (zval unpacking, argument parsing); **the body is unchanged** |
| `modelled` | the mechanism is re-expressed because the original cannot be lifted |

**Every deletion is listed, individually, with a line citation and a reason.**

### 4.2a ⚠⚠⚠ `c_file_line` NAMES THE FAULTING FRAME, NOT THE DEFECT

**The temporal miner refuted the manager's axis prediction on this, and the
mechanism is reusable.** The manager predicted the CWE-416 mass would need the
whole executor and rate `modelled`. Grouped by **mechanism** instead of by file,
the axis is **23 families, 11 `verbatim` / 10 `narrowed` / 2 `modelled`** — nine
in ten lift. ✅ Manager-recomputed from the artefact.

The prediction read plausible because the corpus's `c_file_line` points at where
PHP **crashed**, which is nearly always executor code, while the defect is
usually one call down in a **standalone container**: `zend_ptr_stack.h` (68
lines, no zval, no TSRM, 5 rows), `zend_objects_API.c`, `zend_opcode.c`, and
`zend_hash.h:88`'s `typedef Bucket* HashPosition;`. CRASH-002's line is
`array.c:1062`; its mechanism is `zend_hash.h:88`.

**Rule: group candidates by C MECHANISM, never by file. Reading the axis by
`c_file_line` measures where PHP crashes, not where it is wrong.**

### 4.2 ⚠ Settle the defect against the kernel you are about to extract, BEFORE writing any rung

A corpus row's `root_cause_id` is a claim about **PHP**, not about the kernel we
will extract. The PAT programme got its bug-class row wrong on four patterns,
once by a factor of 2.1e9 — and those were guesses where these are measured, so
these should hold better. *"Should"* is not *"did"*. **Reachability is
deliverable #1 of every build task, in writing, before any rung exists.**

### 4.3 ⚠⚠⚠ A SUBSTITUTED ALLOCATOR IS NOT NEUTRAL

`Zend/zend_alloc.c`'s `_emalloc` assigns `REAL_SIZE(size)` into a **32-bit
`unsigned int real_size`**, so an 18-exabyte request truncates to a ~2 GiB
allocation that **succeeds**. An earlier effort substituted plain `malloc`
during extraction and, as a direct result, **reported a real defect as
unreachable and then invented an explanation for the upstream fix**.

⚠⚠⚠ **THERE ARE THREE TRUNCATIONS, NOT ONE.** The third was found at
`TASK_PHP_002` and ✅ manager-verified: `Zend/zend_alloc.c:295`, inside
`_ecalloc`, is

```c
	int final_size = size*nmemb;
```

— a **signed 32-bit** product passed straight to `_emalloc`, so
`ecalloc(0x40000000, 4)` allocates **0 bytes and succeeds**. A shim that models
only `_emalloc` misses the calloc path entirely.

⚠⚠ **AND THERE IS A SECOND TRUNCATION THIS SECTION DID NOT KNOW ABOUT**, found
by the spatial miner and ✅ manager-verified: `Zend/zend_alloc.h:53` declares the
*recorded* size as `unsigned int size:31` — a 31-bit bitfield, distinct from
`real_size`. And **`_safe_emalloc` checks in 64-bit `long` and then calls the
truncating `_emalloc`**, so it does not protect against either.

⚠⚠⚠ **CONSEQUENCE FOR ADMISSION, AND IT IS NOT OPTIONAL:
`crashes_pristine_5_0_0 = False` IS NOT EVIDENCE THAT A DEFECT IS ABSENT.**
`zend_alloc.c:40-44` forces the size-class cache on in both `#ifdef` arms (⚠ this
said `:39-43` and was **wrong by one**, caught at `TASK_PHP_002`), and
`san_tests/REPORT.md` §2 measures **63.5 % of PHP's heap traffic never reaching
`malloc`**. **A C kernel on plain `malloc`/`free` will reproduce MORE of these
than pristine PHP does** — 40 of the 85 temporal rows are `False` and mostly for
this reason. **Do not use that column as an admission filter.** Fold an
`(allocs, frees)` tally into the kernel's `u64` so the defect lands in the
checksum and not only in a sanitizer.

⚠⚠⚠ **AND THE SHIM ITSELF DID THIS ONCE — SEE `RECAP_PHP.md` F6.** For one
task `_safe_emalloc`'s guard was modelled with `__builtin_mul_overflow` on the
claim that it was the *"same predicate"* as `ZEND_SIGNED_MULTIPLY_LONG`. It is
not: `zend_multiply.h:22` guards the `imul` arm with `#if defined(__i386__)`,
so on x86-64 PHP uses a **double-precision heuristic**, and the exact builtin
allocates where PHP raises `E_ERROR` — **84,523 times in 20 M samples, 100 % in
that direction**. ✅ Fixed at `TASK_PHP_004`. ⚠ **The heuristic's inaccuracy IS
the behaviour: a more correct shim is a less faithful one.**
⚠⚠ **THE REUSABLE RULE: *"modelled by an equivalent builtin"* IS A CLAIM THAT
NEEDS A DIFFERENTIAL TEST, NOT A COMMENT** — and the differential test needs a
**must-fire control**, because the original probe's own control
(`SE CONTROL: a true 64-bit overflow IS refused`) exercised only the region
where the two predicates agree and therefore could not see this.

**Rule: any allocating php row links `common-php/emalloc_shim.*` — faithful and
line-cited against the pristine tarball — or states in `spec.md` why not.**
⚠ Enforcing this on the earlier attempt exposed **three** link sites, not one.
⚠ **And "links it" is now CHECKED, not conventional** — ⚠⚠ **and since
`TASK_PHP_008` §0 the check is UNCONDITIONAL: `harness-php/gate.py`'s preflight
refuses ANY row, allocating or not, that does not carry
`<row>/c/emalloc_shim.h` as a symlink to `common-php/emalloc_shim.h`.** The
symlink is what puts the allocator in **both** digests. It used to refuse only
rows a detector judged to be shim users, and **that detector was built twice
and bypassed twice** (`TASK_PHP_005` F-1 on the string search, `TASK_PHP_007`
B1/B2 on `gcc -MM`) — the question *"does this row use the allocator?"* has an
unbounded answer space, so the rule stopped asking it. `PROTOCOL_PHP.md` §B2
has the full argument and the price; it was enforced by nothing until
`TASK_PHP_004`.
⚠ And the truncation is a *multiplier on every sizing defect in the engine*, not
a pattern of its own; it was correctly retired from that catalogue as a
mechanism. Do not re-propose it as a row.

### 4.4 R1h is the real upstream fix

`c/kernel_hardened.c` is the `fix_commit` patch backported, sha-pinned, with the
commit id recorded in `spec.md`. ⚠ **An upstream fix is not automatically
correct** — the earlier attempt measured one that, backported, **still left a
reachable wild write in the arm it does not guard**. That is a *result*, and one
of the strongest a row can carry. Report it; do not repair it.

### 4.5 Fidelity evidence

Before any rung: reproduce the corpus's **recorded** crash category and, where
recorded, its operand values — with the same binaries clean on a benign input.
⚠ Reproducing a *different* signal (a `SEGV` where the corpus says
`heap-buffer-overflow`) is a finding to state, not a failure to hide.

---

## §5 The rungs

### 5.1 All five (user decision, 2026-09-07)

R1 C · R2 safe naive · R3 safe tuned · R4 unsafe · R5 unsafe + Verus, × {O0, O3}
× {isolated, whole}, plus R1h. Same as PAT.

### 5.2 R4 and R5 may land as findings

Where Verus cannot state the obligation, **that is the row's result** — `p42`
ships exactly that way and is one of the most-cited rows in the PAT tree. Do not
chase a proof past the point where the *inability* is the more informative
output, and do not let an R5 difficulty influence admission (§3).

### 5.3 ⚠ The trap that has fired seven times: search BOTH sides

A rung comparison is only as honest as its **weaker-searched endpoint**. Seven
PAT patterns published a difference whose losing side had never been searched;
one was 510× wide. **Count the levers on each side, say whether they are
comparable, ship a `controls/spellings.py` that makes the search re-derivable,
and give the figure at BOTH optimisation levels** — one PAT row's comparison
*reverses* between `-O0` and `-O3`.

### 5.4 ⚠⚠ THE EXISTING RUST PORT IS OUT OF SCOPE

`php-in-safe-rust/php-rust/` is **not** a carefully written translation and must
not influence this study. **No `safe_shipped` cell.** An engineer may read it for
orientation and must not cite it as evidence, benchmark against it, or let it
shape a rung's spelling.

**User decision, 2026-09-07:** *"assessing which ones of an existing imperfect
translation are good/bad will delay all the way after we finish everything.
Don't let that crappy translation influence our main study right now."*

⚠ This is a **deferral, not a deletion**. Once `patterns-php/` is built, "where
does the shipped port land on each of these scales?" becomes a well-posed
question with a ready-made instrument — and it is exactly the question the crash
course's readers will ask. Recorded here so it is not re-derived.

---

## §6 Provenance — "a reference of C code versions"

Every row carries a `provenance` object **inside the hashed `slb-contract`
block**, so the gate pins it and a drift is detectable:

```json
"provenance": {
  "php_version":  "5.0.0",
  "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
  "c_file":       "ext/standard/url.c",
  "c_lines":      [463, 489],
  "extract_cmd":  "tar -xzOf <tarball> php-5.0.0/ext/standard/url.c | sed -n '463,489p'",
  "extract_sha256": "<sha256 of that excerpt>",
  "tier":         "verbatim",
  "deletions":    [{"what": "TSRMLS_DC", "why": "thread-safety plumbing, no semantics"}],
  "root_cause_ids": ["…"],
  "cwe":          "CWE-125",
  "fix_commit":   "…",
  "invariant":    "I1", "obligation": "O2",
  "echoes":       ["p16"],
  "uses_allocator": true,
  "uses_allocator_why": "kernel.c calls php_shim_emalloc on every element; the T1 truncation is the defect"
}
```

⚠⚠⚠ **`uses_allocator` IS DECLARED, NEVER DETECTED, AND NOTHING MAY DEPEND ON
IT BEING RIGHT** (`TASK_PHP_008` §0.4). The row's author states whether the
kernel's numbers were taken under `common-php/emalloc_shim.h`; a **reviewer**
checks it against the kernel. **No digest, no verdict and no audit reads it.**

**It exists because the project stopped asking the question mechanically.**
Two guards answered *"does this row use the allocator?"* — a string search
(`TASK_PHP_004`) and `gcc -MM` (`TASK_PHP_006`) — and **both were bypassed
twice** (`TASK_PHP_005` F-1, `TASK_PHP_007` B1/B2), because that question has an
unbounded answer space: every preprocessor spelling, every flag combination,
every compiler. `TASK_PHP_008` made the `c/emalloc_shim.h` symlink
**unconditional** so the question is no longer load-bearing, and this field is
what a human reads instead. ⚠ **If it ever acquires a consumer it has become a
third detector** — `provenance.py::ALLOC_KEY`'s comment is the warning, and it
is deliberately absent from `REQUIRED` for the same reason.

`extract_sha256` is the load-bearing field: it makes ***"those lines of that
tarball hash to this"*** a one-command check rather than a claim.

⚠⚠ **THIS SENTENCE SAID *"THIS KERNEL came from those lines"* AND THAT WAS AN
OVERCLAIM** — `TASK_PHP_003` M5, corrected at `TASK_PHP_004`. The validator
**never opened `c/kernel.c`**; the word `kernel` appeared in the module only
inside this sentence. It now does, and here is the honest split:

| | |
|---|---|
| ✅ checked | tarball sha256 · `c_file` in `php-5.0.0.manifest` · the span is **non-empty and in range** · its sha256 · `extract_cmd` is the canonical spelling · a row declaring PHP provenance ships a kernel at all |
| ⚠ **reported, not checked** | the **heuristic line overlap** between the excerpt and `c/kernel*.{c,h}`, printed beside the tier's expectation (`verbatim` 50 %, `narrowed` 25 %, `modelled` none) — ⚠ **it no longer REFUSES a row** (`TASK_PHP_008` §2): its correctness depended on recognising every spelling of "this block is dead", and `TASK_PHP_007` M2 measured **nine more** past the `#if 0` that `TASK_PHP_006` fixed. Printed with it: how many preprocessor conditions the heuristic could not evaluate. |
| ✗ **not** checked | `tier` · `deletions` · `root_cause_ids` · `cwe` · `fix_commit` · `invariant` · `obligation` · `echoes` · **`uses_allocator`** — free-text declarations, every one |

⚠ **An out-of-range span used to PASS**: `sed` prints nothing past EOF and the
caller compared `sha256(b"")`, so a transposed line number verified green and
printed `0 bytes`. ⚠ **The overlap is evidence about the tier, not a proof of
extraction**, and the measured number is always printed so a reader can judge
it. Negatives: `.temp/php4/m5_prov_test.py`.

---

## §7 Measurement rules inherited

From `.memory/03-measurement.md` and the earlier php attempt. One line each;
the full argument is at the citation.

1. **Never a static count without a paired `Ir`** — the ranking has inverted.
2. **Every C-vs-Rust claim needs the clang column.** gcc is the distro baseline.
3. **Identity claims cite raw machine-code bytes**; normalised text collides.
4. **The proof must cover the measured call site.**
5. **`O0` is for reading the lowering.** No performance claim rests on one.
6. **Report ns, never cycles** — this box's clock is set by other tenants.
7. **Kernel-exclusive `Ir` misses whatever the rung calls out to.**
8. **`Ir(main)` compares Rust to Rust only**; never rescued by subtraction.
9. ⭐ **An input's *content* is a measurement parameter — vary it or state it.**
   This killed a headline in the earlier attempt: the comparison's *sign*
   depended on the escape density of the test input.
10. **`Ir` over-counts glibc bulk copies** (memset flips at 2–4 KiB, memcpy at
    8 K). Above threshold carry a marginal-vs-marginal wall cross-check.
    ⚠ Check the premise before invoking it — it was **false** for one kernel
    that had zero bulk copy in all seven cells.
11. ⭐ **A substituted allocator is not neutral** (§4.3).
12. ⭐ **A cost with no mechanism is an incomplete row.** Name *why* from the
    disassembly: which check elided, which load came back, what LLVM failed to
    hoist.
13. ⭐ **Shared work in the denominator compresses every ratio toward 1.0.**
    Publish the shared-work fraction beside any ratio.
14. ⚠ **Hand-run ASan is blind on this box and fails silently to the exit code.**
    This shell inherits `LD_PRELOAD=…/libstdbuf.so`; a dynamically linked ASan
    binary refuses to start behind it **and still exits 1**. Use
    `env -u LD_PRELOAD`, and grep for `AddressSanitizer`, not `ASan`.
    (`harness/check.py` uses `-static-libasan` and is unaffected.)

---

## §8 Phases

| phase | deliverable | shape |
|---|---|---|
| **0 — foundation** | `SOURCES.md` + manifest · `harness-php/` proving the no-touch rule · `common-php/emalloc_shim.*` · `.tasks-php/PROTOCOL_PHP.md` · the `provenance` block · **`measure.py --check-stale` = 0 STALE / 66 before and after** | 1 engineer + 1 reviewer, **one agent at a time** |
| **1 — the catalogue** | `patterns-php/CATALOGUE.md`: every candidate with version, sha256, verified `file:line`, mechanism read from the pristine source, CWE, `fix_commit`, invariant/obligation, tier estimate, distinctness, blob-drivability | mining is **read-only** → up to 3 agents in parallel · adjudication + review is 1 at a time |
| **2 — build** | rows, axis-interleaved: **spatial** first (cheapest, `verbatim`, validates the machinery on real code), then **type**, then **temporal** (the mass, and where extraction gets hard) | 1 agent at a time, build → review → land → **write the finding** |

**The loop is four steps, not three.** A pattern is finished when a reader can
find its result, not when its gate is green — two PAT patterns were gate-green,
reviewed and corrected, and then absent from the findings for 45 and 35 tasks
while the status box counted them done.

**Cost.** The PAT programme's *measured* rate is **~3 tasks per row**. There is
no time or token limit on this programme, so the quota is set by how many
distinct mechanisms Phase 1 actually finds, not by a budget — but the rate is
the number to plan against, and Phase 1's output is what makes the quota
decidable. **Do not fix a row count before Phase 1 reports.**

---

## §9 What the crash course needs out of this

The eventual audience is engineers porting PHP to safe Rust. That shapes what
every row must be able to answer, and it is worth writing down before the rows
exist, because it is what stops the corpus becoming a table nobody can act on:

1. **Here is the C you are about to translate**, cited to the line.
2. **Here is what goes wrong**, with the real reproducer and the real upstream fix.
3. **Here is the naive safe-Rust translation** — safe, and what it costs.
4. **Here is the tuned one** — and *why* it is cheaper, read off the disassembly.
5. **Here is what `unsafe` buys, and what a proof costs to take it back.**
6. **Here is which invariant moved, and how far up the enforcement ladder.**

⚠ Item 4 is the one that decides whether the course is useful, and it is rule
12 restated: *a cost with no mechanism is an incomplete row.*

---

## §10 Decision register

| id | decision | source |
|---|---|---|
| `DP-01` | Parallel tree (`patterns-php/`, `harness-php/`, `results-php/`, `.tasks-php/`, `.memory-php/`, `common-php/`); the PAT harness is imported, never edited | user 2026-09-07 + the hashing measurement in §2.1 |
| `DP-02` | **All five rungs**, R4/R5 allowed to land as findings | user 2026-09-07 |
| `DP-03` | `patterns-php/` is **fresh**: no cross-corpus duplication check; slight variations admitted as separate rows | user 2026-09-07 |
| `DP-04` | `RECAP.md`→`RECAP_PAT.md`, `PLAN.md`→`PLAN_PAT.md`; `RECAP_PHP.md`/`PLAN_PHP.md` are new | user 2026-09-07 |
| `DP-05` | **No `safe_shipped` cell.** The existing Rust port is reference-only and out of scope; the "where does the port land" question is **deferred**, not deleted | user 2026-09-07 |
| `DP-06` | **PHP 5.0.0 only.** 4.0.x ignored | user 2026-09-07 |
| `DP-07` | The spatial ban is scoped to `patterns/`; spatial rows are wanted here, and pointer-cursor mechanisms rank above index ones | user 2026-09-07 + census finding 45 |
| `DP-08` | `.tasks/PROTOCOL.md` is reused; `.tasks-php/PROTOCOL_PHP.md` is an addendum, not a fork | manager, §2.2 |
| `DP-09` | Concurrency: up to **3 agents in parallel for read-only investigation/mining**; **1 at a time** for construction and review (multiple may be alive; resume with `SendMessage`) | user 2026-09-07 |
