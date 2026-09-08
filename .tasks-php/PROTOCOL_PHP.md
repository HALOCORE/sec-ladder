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
| `verbatim` | the function lifts as-is; only `TSRMLS_*` / macro plumbing is removed, **or substituted where the substitution is demonstrated behaviour-preserving** — see below |
| `narrowed` | a wrapper comes off (zval unpacking, argument parsing); **the body is unchanged** |
| `modelled` | the mechanism is re-expressed because the original cannot be lifted |

⚠⚠ **`verbatim` ADMITS SUBSTITUTIONS, AND THIS TABLE DEFINED THE TIER PURELY BY
*REMOVAL* UNTIL TASK_PHP_015.** `ph03` does not remove `floor`/`ceil`: it
**adds** two `static double` definitions and two `#define`s that redirect them,
because `harness/build.py` links no `-lm` and is frozen. This row of the table
had no word for that, so a builder reading it alone would conclude that any
substitution forces `modelled` — and §A2 already carried the right test all
along. Stated plainly, because a tier that is read as stricter than it is
becomes a filter, and ⚠ *a tier is a COST, NEVER A FILTER*:

> **A substitution is admissible in `verbatim` when it is (a) itemised
> individually in the `divergences` ledger with a line citation, (b) given a
> `why` that ends in "no semantics", and (c) DEMONSTRATED behaviour-preserving
> over the reachable domain by a differential with a must-fire control — not
> asserted.** `ph03`'s libm substitution is the worked example: 0 disagreements
> over `len` 0..63 and `n` 0..10⁶, control **38**, and re-run under
> `-ffast-math` / `-march=native` / `-funsafe-math-optimizations` / `-Ofast` on
> both compilers. ⚠ **(c) is what keeps this from being a hole**: "modelled by
> an equivalent" is a claim that needs a differential and not a comment — §B's
> `ZEND_SIGNED_MULTIPLY_LONG` is the case where the equivalent builtin was
> **84 523 disagreements** away from faithful.

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

### A2. The divergence ledger

⚠⚠ **THE KEY IS `provenance.divergences` AND IT WAS `provenance.deletions`
UNTIL TASK_PHP_015. THREE OF `ph03`'s FOUR ENTRIES ARE NOT DELETIONS** (two
substitutions and one projection of the shim's NULL arm), so the ledger's own
name described a quarter of its contents — §A1's mistake one level down, and
found in the same review (TASK_PHP_014). ✅ Renamed rather than explained away:
a builder fills in the box the name describes.

**Every way the row's C differs from the cited tarball lines is listed
individually, with a `kind`, a line citation and a reason.** Not "macro
plumbing removed" — one entry per thing:

```json
"divergences": [
  {"what": "TSRMLS_DC", "kind": "deletion", "where": "zend_alloc.c:142", "why": "thread plumbing, no semantics"},
  {"what": "ZEND_DEBUG arms", "kind": "deletion", "where": "zend_alloc.c:153-165", "why": "the shipped 5.0.0 build is not a debug build; keeping them would ADD a poison-on-free PHP does not do"},
  {"what": "floor -> php_uu_floor", "kind": "substitution", "where": "uuencode.c:141", "why": "build.py links no -lm and is frozen; same double expressions, 0 disagreements over the reachable domain with a must-fire control. No semantics."}
]
```

`kind` is one of **`deletion`** (the text is gone), **`substitution`** (the text
is redirected at something that behaves identically — §A1's clause governs it)
or **`projection`** (a behaviour outside the extracted span is modelled by a
narrower one, e.g. the shim's NULL arm for PHP's `exit(1)`).

⚠ **DECLARED, NEVER DETECTED.** `provenance.py` does not read this block —
`tier`, `divergences`, `cwe`, `fix_commit`, `invariant`, `obligation` and
`echoes` are all unvalidated declarations (§D), and **nothing may come to
depend on `kind` being right**; it is documentation for a reviewer, the same
standing `uses_allocator` has. What makes the ledger worth writing is that the
`slb-contract` block is hashed, so an entry cannot be quietly withdrawn.

⚠ A divergence that CHANGES BEHAVIOUR is not a divergence, it is a `modelled`
tier. If you cannot write a `why` that ends in "no semantics", you are in the
wrong tier.

### A2a. ⚠⚠⚠ THE ORACLE'S DOMAIN IS NOT THE CORPUS

**Two rules, and they are two because they fail differently. Both come out of
one defect — `TASK_PHP_014` M1, on the first real row.**

`ph03`'s `model.py` carries two implementations of the kernel and compares them,
exactly as `PROTOCOL.md`'s definition of done wants. One of them was **the wrong
function** for a whole task: it folded every emitted byte where `verus.rs` folds
the first `total_len`, which is a different function for **42 of the 63** length
bytes. It passed because `inputs/gen.py` emitted length **45** exclusively —
`45 ≡ 0 (mod 3)` is precisely the equality case — and the generator's own
comment called the other arm *"dropped"*. So the gate's `ensures` re-derivation
was **green while checking a different postcondition from the one R5 proves**.

> **1. THE FIXTURE MUST REACH EVERY ARM OF THE BRANCH THE DEFECT LIVES ON, AND
> `inputs/gen.py` MUST ASSERT THAT IT DOES.**
>
> `ph03`'s defect is `ee = s + (len == 45 ? 60 : (int) floor(len * 1.33))` —
> **two arms** — and the benign corpus took the first one on every byte it
> shipped. The repair is a short final line, which is also what real uuencoded
> data has, so the monoculture was **unfaithful as well as blind**. ⚠ The
> load-bearing half is the **assertion**: `inputs/gen.py::_check_span` re-decodes
> what it just generated and refuses to write a corpus that misses an arm, in
> the same shape as `_check_residues`. **An intention in a comment is what ph03
> had, and it was wrong for a task.**
>
> **2. `model.py::selfcheck` MUST DRIVE ITS TWO IMPLEMENTATIONS OVER A DOMAIN IT
> CONSTRUCTS, NOT ONLY OVER THE CALLS THE CORPUS MAKES.**
>
> **A second implementation is only as strong as the domain it is exercised
> over, and six `.bin` files are not a domain.** `ph03`'s sweep is ~30 lines,
> builds 896 windows spanning `ln = 0..63` in three families, costs
> milliseconds, needs no `.bin` and no measurement. It kills **both** modelling
> errors this row has had — the `ee + 1` resume point (65/896) and M1
> (294/896) — and its must-fire and must-NOT-fire controls are
> `.temp/php15/03-sweep-mustfire.log`.

⚠⚠ **NEITHER RULE SUBSUMES THE OTHER.** Rule 1 is bounded by what a window of
fixed stride can carry — a corpus cannot span `ln = 1..63` and keep
`work_per_call` constant — so it buys *reachability*, not coverage. Rule 2
buys coverage and buys it free, but it is a check on the **model** and cannot
see a *measurement* taken down a path nothing ever executes. Write both.

⚠ **What the manager's first phrasing said, and why this one is different.**
`TASK_PHP_015` §1.3 put it as *"the generator must span the parameter that
selects the code path the defect lives on"*, and asked whether that generalises.
It does not quite: **"span the parameter" is not achievable inside a fixed
stride, and it names the fixture as the only repair when the cheaper and
stronger one is in the model.** *Reach every arm* is achievable, assertable and
row-independent. ✅ **Checked against the next row before being written here**:
`ph07`'s `mbfl_strcut` walks `p += mbtab[*p]`, so its branch arms are the
lead-byte classes (1-, 2-, 3-byte) — an all-ASCII benign corpus takes exactly
one of them, which is `ph03`'s defect with a different name. The rule applies
unchanged; only the word *parameter* had to go.

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

⚠⚠⚠ **AND ITS GUARD IS NOT AN EXACT OVERFLOW TEST.** `zend_multiply.h:22`
guards the `imul`/`adc` arm with `#if defined(__i386__) && defined(__GNUC__)`,
so on **x86-64** `ZEND_SIGNED_MULTIPLY_LONG` is the `#else` at `:36-45` — a
**double-precision heuristic** (`__dres + __delta != __dres`) that reports
overflow on products at or above 2^53 that did not overflow. The shim modelled
it with `__builtin_mul_overflow` for one task: **84,523 disagreements in 20 M
samples, 100 % of them "PHP raises `E_ERROR` where the shim allocates"**
(`TASK_PHP_003` B2). ⚠ **The inaccuracy IS the 5.0.0 behaviour: a more correct
shim is a less faithful one, and modelling it exactly would invent a defect at
every `safe_emalloc` call site.** Fixed at `TASK_PHP_004`
(`PHP_SHIM_SIGNED_MULTIPLY_LONG`); differential probe with a must-fire control
in `.temp/php4/mul_probe.c`.

⚠ **THE GENERAL RULE THIS BUYS:** *"modelled by an equivalent builtin"* is a
claim that needs a **differential test**, not a comment.

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

⚠⚠⚠ **AND EVERY ROW CARRIES THE SYMLINK — UNCONDITIONALLY, WHETHER OR NOT IT
ALLOCATES** (`TASK_PHP_008` §0):

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

⚠⚠⚠ **AND FOR ONE TASK THIS WORD "MANDATORY" WAS ENFORCED BY NOTHING.**
`TASK_PHP_003` B1 built a row that links the allocator and omits the symlink:
it **builds** (via `-I common-php`) and the allocator lands in **neither**
digest, so a later shim fix would leave that row's `Ir` numbers `FRESH` for
ever under an allocator that no longer exists. Enforced at `TASK_PHP_004` by
`harness-php/gate.py::shim_link_audit`, which runs in the preflight before
every tool over every row and exits 2 without running the tool.

⚠⚠⚠ **AND THAT ENFORCEMENT WAS A STRING SEARCH, AND A GUARD THAT IS A STRING
SEARCH IS A GUARD WITH A SPELLING. `TASK_PHP_005` F-1 GOT PAST IT TWICE.** Both
constructed rows compiled, linked and ran a live allocator
(`alloc tally = 7688571`) into **neither digest** with the preflight green:

1. `#include "emalloc_shim.c"` — the audit knew only the `.h`, and the `.c` is
   two lines that include it, sitting on `-I common-php`. ⚠ **The audit did not
   cover this spelling because `emalloc_shim.c`'s own header comment said it
   *"IS NOT ON THE PATTERN BUILD PATH AND CANNOT BE"* — true of `build.py`'s TU
   list, FALSE of the preprocessor.** Comment corrected at `TASK_PHP_006`.
2. `c/<subdir>/*.h` — `glob(cdir + "/*")` is not recursive.

~~✅ **Closed at `TASK_PHP_006` by CHANGING THE QUESTION** — `gate.py::_tu_closure`,
`gcc -MM` over `build.py`'s own TU list. **It has no spelling.**~~

⚠⚠⚠ **THAT WAS THE SECOND FIX AND IT WAS BYPASSED TWICE TOO** (`TASK_PHP_007`
B1/B2). `_tu_closure` ran `gcc -std=c99 -MM` with `_MM_CONFIGS = ([],
["-DSLB_ISOLATED"])` — **2 of the 8 preprocessor states `build.py` compiles
in**, because `build_cell` also picks `{gcc, clang}` from the cell name and
`c_flags` also passes `{-O0, -O3}`. So:

| construct | live in | audit said |
|---|---|---|
| `#ifdef __OPTIMIZE__` | all four `-O3` cells (`alloc tally = 1000`, built and run) | nothing |
| `#ifdef __clang__` | all four `c-clang-*` cells | nothing |
| `#if __has_include(...)` | all four `c-clang-*` cells | nothing |
| a `c/*.c` `build.py` never compiles | all eight | *"dead code … Not treated as a shim user"* |

⚠⚠ **The last row is worse than the hole it replaced: a FALSE NEGATIVE WEARING
A REASSURANCE**, about a row that allocates a thousand times in half the
measured cells. And the text FALLBACK **failed open** — a row could *choose* it
by shipping an include-only `c/aux.c` that refuses to preprocess standalone,
then hide the include from `_INCLUDE_RX` with a line splice or a computed
`#include`.

✅✅ **CLOSED AT `TASK_PHP_008` §0 BY MAKING THE QUESTION STOP BEING
LOAD-BEARING. EVERY ROW CARRIES THE LINK, ALLOCATING OR NOT.** The audit is
`os.path.islink` + `os.path.realpath == common-php/emalloc_shim.h`. **No
subprocess, no flag space, no compiler, no fallback, no regex** — and
`_tu_closure`, `_MM_CONFIGS`, `_INCLUDE_RX`, `_text_mentions` and the `texty`
fallback were **deleted**, not kept as advice.

⚠ **THE DURABLE LESSON, AND IT IS THE ONE TO CARRY OUT OF THIS FILE: both
fixes answered *"does this row use the allocator?"*, and that question has an
UNBOUNDED ANSWER SPACE — every preprocessor spelling, every flag combination,
every compiler. A guard whose correctness depends on enumerating idioms will be
reopened by the next idiom.** Two rounds was the evidence.

**What it costs, and it is smaller than the decision that took it assumed**
(`TASK_PHP_008`, `.temp/php8/02-digest-reality.log`): a shim edit now stales
every php row rather than only the allocating ones — but ⚠ **the GATE half of
that was ALREADY unconditional and has been since `TASK_PHP_002`**, because
`common-php/digest_bridge.py` carries the shim's sha256 and `check.py`'s
`common/*.py` glob puts *digest_bridge.py's own hash* into every php gate
record. The link adds the **measurement** half only, so the marginal price is a
re-measure plus a `report.py` render per row, on top of a re-gate already owed.
✅ **Measured on `ph00-smoke` at `TASK_PHP_008` — see that report's §5.**

⚠ **`uses_allocator` is the DECLARED answer to the question the audit stopped
asking** (`PLAN_PHP.md` §6, §D below). It is documentation for a reviewer.
**Nothing depends on it being right, and if it ever acquires a consumer it has
become a third detector.**

✅ **`TASK_PHP_006` did close a real FALSE POSITIVE** (`TASK_PHP_005` F-8): the
string detector refused a row whose only mention was the comment §4.3 of
`PLAN_PHP.md` and `emalloc_shim.h:6-9` **tell a non-allocating row to write**.
⚠ That class cannot recur, for the structural reason that there is no longer
anything to false-positive *on*: the rule does not read the row's sources.

⚠ **A word in a document is not an enforcement mechanism** — that is the
durable lesson, and it applies to every other "mandatory" in this file. ⚠⚠ **And
the second lesson, from F-1: a MECHANISM IS ONLY AS GOOD AS THE QUESTION IT
ASKS. The string search was a real mechanism, ran on every invocation, had
must-fire negatives, and was still bypassable in two lines, because it asked
*"does this text appear"* where the digest cares about *"does this file reach a
compiled translation unit"*.** ⚠⚠⚠ **AND THE THIRD, FROM `TASK_PHP_007`: the
preprocessor answered a BETTER question and was still bypassable, because the
question itself was the problem. When a guard is reopened twice, change what it
asks — do not sharpen how it asks it.**

### B3. ✅ `patterns-php/<row>/c/<subdir>/` is AVAILABLE AND PRICED, not forbidden

`harness/check.py:10314` and `harness/measure.py:226` glob `<row>/c/*`
**non-recursively** and drop the directory entry with `os.path.isfile`, so **any
source in a `c/` subdirectory is compiled and in NO digest at all** — not the
gate one, not the measurement one, and not `check.py`'s `--no-build` staleness
scan, so editing one does not even mark a binary stale. Fixing the glob is a
`harness/` edit and costs a 33-pattern re-gate (`RECAP_PHP.md` open item 17,
**carried, not closed**).

~~**Decision: forbid the layout on the php side instead**, enforced by
`gate.py::c_subdir_audit` since `TASK_PHP_006`.~~

⚠⚠ **THE BAN WAS BOTH UNSOUND AND OVER-STRICT, AND `TASK_PHP_007` M1/m1 PROVED
BOTH. Lifted at `TASK_PHP_008` §1.**

- **Unsound.** `c_subdir_audit` skipped a **symlinked** directory by name
  (`if not os.path.isdir(p) or os.path.islink(p): continue`), so
  `ln -s ../../../extract/Zend c/zend` compiled every header behind it into
  **neither digest, unrefused** — which is the natural way to build a row from
  a tarball. And `glob("c/*")` never matches a leading dot, so `c/.payload.h`
  walked round it too. ⚠ **An unsound ban is worse than an over-strict one.**
- **Over-strict.** The flat-symlink hatch was declined at `TASK_PHP_006`
  *"because nothing would force the NEXT file added to that subdirectory to get
  a link"*. The reviewer **built** the twelve lines that force it and fired
  them in both directions (`.temp/php7/07-manager-calls.log`).

✅ **What enforces it now: `gate.py::c_digest_audit`.** Every file it finds
under `<row>/c/` — following directory symlinks, cycle-safe, dotfiles included
— must share a `realpath` with some `glob("<row>/c/*")` entry that
`os.path.isfile` accepts. Two ways to satisfy it:

1. **FLATTEN** — `c/zend__zend_hash.h` for `Zend/zend_hash.h`, rewrite the
   `#include`, one deletion-ledger line (§A2). Still the cheapest answer.
2. **FLAT SYMLINK BESIDE IT** — keep `c/zend/zend_hash.h`, add
   `c/zend__zend_hash.h -> zend/zend_hash.h`. ✅ Measured at `TASK_PHP_006`
   (`.temp/php6/05-b1-rerun.log` §C), re-derived at `TASK_PHP_007`
   (`03-subdir.log`), and re-run against the new audit at `TASK_PHP_008`
   (`.temp/php8/11-digest-audit.log`, rows `ph83-flatlink` and
   `ph85-dirlink-ok`, both must-NOT-fire).

⚠ **A DOTFILE HAS NO SANCTIONED FORM** — `glob` cannot match it, so there is no
flat key to give it. Rename it. ⚠⚠ **AND NEITHER HAS A DOTTED *ROW***, since
`TASK_PHP_010` §1 — `patterns-php/.ph07-wip/` is refused **by name**. `glob`
cannot reach its records either, and the record half cannot be repaired from
here: `harness/measure.py:303` is frozen and globs `results/p*.json`, which
`.ph07-wip.json` does not match, so `--check-stale` would print `0 STALE`
having never looked at that row.

### ⚠⚠⚠ B3a. THE DANGER IS **NOT** "A SUBDIRECTORY OF `c/`". IT IS "ANY FILE `glob(<row>/c/*)` DOES NOT MATCH", AND THE SIBLING DIRECTORY IS THE ONE THAT ESCAPED

⚠⚠ **This section taught the `c/` subdirectory as the hazard, and the layout it
made most likely was the one no audit covered** (`TASK_PHP_009` M2). `#include`
with quotes resolves **relative to the directory of the including file**, so
`c/kernel.c` reaches a SIBLING with `"../aux/x.h"` — and the natural php layout
is exactly that: extracted tarball sources at `<row>/extract/Zend/…`, mirroring
their origin, one character away from the sanctioned `c/zend -> …` and with the
opposite guarantee. **Measured**: that file compiles, runs the row's own
allocator, is in **neither** digest, and editing it moved the binary's behaviour
(`tally 1 → 1000`) with **0 digest keys moved and 0 preflight problems**
(`.temp/php9/04-upward-include.log`).

✅ **Closed at `TASK_PHP_010` §2: a row may contain only `c/`, `inputs/` and
`controls/`** (`gate.py::ROW_DIRS`, refused inside `c_digest_audit`;
`__pycache__` is exempt because Python creates it). **Put extracted sources
under `c/`** — flatten, or keep the tarball's shape at `c/zend/…` with a flat
symlink beside each file, exactly as the two spellings above prescribe.

⚠ **Do NOT reach for `gcc -MD`.** An include-closure detector is what
`TASK_PHP_008` §0 deleted after two rounds; its input space is unbounded and it
needs a `build.py` edit. The whitelist is one `os.listdir` with a finite answer.

⚠⚠ **WHAT THE WHITELIST DOES NOT BOUND, AND IT IS MEASURED, NOT GUESSED**
(`TASK_PHP_010`, `.temp/php10/05-outside-row.log`): `..` **twice** leaves the
row. `#include "../../shared/x.h"` from `<row>/c/` reaches
`patterns-php/shared/x.h`; it compiles, runs, is in no digest, and **is not
refused** — `patterns-php/shared/` is not a directory *under* the row, and as a
row with no `c/` both audits skip it. **The rule bounds the escape INSIDE the
row and not the escape OUT of it.** Until that is closed, treat *"every file a
row compiles lives under `<row>/c/`"* as a **discipline**, and read a row's
`#include` lines in review: a `..` in one is a claim that needs the reviewer's
eye, not the gate's.

⚠⚠ **AND THE REASON THIS AUDIT IS SOUND WHERE THE ALLOCATOR DETECTOR WAS NOT:
IT ENUMERATES FILES — A FINITE, OBSERVABLE SET — NOT IDIOMS.** No preprocessor
state, no compiler, no flag space, no spelling. That is the distinction to
carry: §B2's guard kept being reopened because its input was unbounded; this
one's input is `os.listdir`.

⚠⚠⚠ **AND THAT SENTENCE WAS FALSE OF THE ROW LOOP FOR FIVE TASKS — TRUE OF THE
FILE WALK, FALSE OF THE ENUMERATION AROUND IT.** `_walk_files` used
`os.listdir`; the four audits that called it iterated **`glob(patterns-php/*)`**,
which never matches a leading dot, while `build.py::pattern_dir` (`os.listdir`)
and `provenance.py` both resolve a dotted row. `gate.py --preflight .ph93`
returned **rc=0** on a row carrying a regular-file allocator copy *and* an
unkeyed subdirectory source, printing `ok every patterns-php/*/c/ file has a
digest key` about a tree where that was false (`TASK_PHP_009` M1). ✅ **Made
true at `TASK_PHP_010` §1**: every row-iterating audit — `shim_link_audit`,
`c_digest_audit`, `why_sizes` and `preflight_coverage_audit` — now goes through
`gate.py::_row_dirs`, one `os.listdir`, the same set the builder compiles.
⚠ **The invariant to keep is that sentence, not the code: THE AUDIT AND THE
BUILDER MUST ENUMERATE THE SAME SET.** A wrong enumeration is not an
unboundable one — the fix was a substitution, in one call — but it is only
*checkable* because there is one call to check.

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

- `extract_sha256` is the load-bearing field: it makes *"**those lines of that
  tarball hash to this**"* a **one-command check** rather than a claim.
  ⚠ **It said *"this KERNEL came from those lines"* and that overclaimed**
  (`TASK_PHP_003` M5): until `TASK_PHP_004` the validator never opened
  `c/kernel.c` at all. It now also computes a **heuristic line overlap**
  between the excerpt and the row's `c/kernel*.{c,h}`, ~~and enforces a floor per
  tier~~ ⚠⚠ **and REPORTS it against a per-tier expectation (`verbatim` 50 %,
  `narrowed` 25 %, `modelled` none) WITHOUT REFUSING — `TASK_PHP_008` §2**,
  and refuses a row that declares PHP provenance and ships no kernel source.
  ⚠ **The overlap is evidence about the tier, not a proof of extraction**, and
  the measured number is always printed. `tier`, `deletions`, `cwe`,
  `fix_commit`, `invariant`, `obligation` and `echoes` remain **unvalidated
  declarations**; `provenance.py`'s own docstring itemises checked vs not.
  ⚠⚠ **AND THE RISK IS A FALSE PASS, NOT A FALSE REFUSAL — THIS BULLET HAD IT
  THE WRONG WAY ROUND.** `TASK_PHP_005` F-4: a kernel that implements
  **division**, cites **multiplication**, and hides the citation behind `#if 0`
  scored **100 % and was ACCEPTED**, because the normaliser dropped lines
  *starting with* `#` and so deleted the `#if 0` and `#endif` while keeping
  everything between them. The same kernel without the dead block was refused at
  11 %, so the floor works and it was the *normaliser* that did not.
  ✅ Fixed at `TASK_PHP_006` (`#if 0` regions and block comments are elided,
  `#else` arms are kept), and the regression cases live in
  `provenance.py::OVERLAP_CASES` — **run on every preflight**, ~~seven~~ **nine**
  of them, including **three** must-NOT-fire cases so that a normaliser which
  stopped measuring anything could not pass.
  `python3 harness-php/provenance.py --selftest`.

  ⚠⚠⚠ **AND THE FLOOR IS NOW REPORTED, NOT ENFORCED — `TASK_PHP_008` §2.**
  `TASK_PHP_007` M2 measured **nine more spellings** of "this block is dead"
  that the normaliser counts in full — `#if 0L`, `#if (0)`, `#if 00`, `#if !1`,
  `#ifdef NEVER_DEFINED`, `#ifndef __STDC__`, `#if defined(NOPE) &&
  defined(NOPE2)`, the undisclosed **`#if 1 … #else <payload> #endif`**, and
  `#elif 0`, which was **actively mishandled** — each scoring **100 %** on a
  kernel that divides while citing multiplication. **That is §B2's class one
  level down: a check whose correctness depends on parsing every preprocessor
  conditional will be reopened by the next one.** So the number is printed and
  the row is not refused for it.
  ✅ **`#elif 0` was FIXED ANYWAY** — a wrong number is worse than an
  unenforced one — with case **B4** (must-fire, verified against the
  `TASK_PHP_006` code, which scores it 100 %) and case **E2** (must-NOT-fire: a
  non-literal `#elif` arm CAN be compiled, so `elif → always skip` must not
  pass). Controls: `.temp/php8/04-elif-control.log`.
  ✅ **What is still ENFORCED is the exact half** — `c_file` in the manifest,
  the span in range, `extract_sha256`. Those are not heuristics.
  ⚠ Every run also prints `unevaluable_conditionals()`: **how many
  preprocessor conditions in the kernel the heuristic could not evaluate**. The
  residual is reported as a number rather than enumerated away.

  ⚠⚠⚠ **AND EVEN GREEN, A HIGH NUMBER IS NOT EVIDENCE THAT THE CITED LINES ARE
  COMPILED.** The check reads `c/kernel*.{c,h}` and never `main.c`, the driver
  loop or `build.py`, so an unused `static` function beside the one the driver
  actually calls scores full marks (`-Wall -Wextra` without `-Werror` does not
  stop it). **It measures text in a file, not code in the benchmark** —
  `RECAP_PHP.md` open item 14 recorded exactly that before the demotion, which
  is the argument for it — and it now says so itself in every message it prints.
- ⚠⚠ **`uses_allocator` — DECLARED, NEVER DETECTED** (`TASK_PHP_008` §0.4).
  The row's author states whether the kernel's numbers were taken under
  `emalloc_shim.h`; a reviewer checks it against the kernel. ⚠⚠⚠ **NOTHING MAY
  DEPEND ON IT BEING RIGHT** — no digest, no verdict, no audit reads it, and the
  `c/emalloc_shim.h` symlink is unconditional whatever it says. It is
  deliberately **not** in `provenance.py::REQUIRED`: making it a hard
  requirement is one step from making it load-bearing, and **two detectors of
  this exact fact have already been bypassed.** A missing one is reported
  loudly on every run instead.
- ⚠ **An out-of-range span used to PASS.** `sed` prints nothing past EOF and
  the caller compared `sha256(b"")`, so a transposed line number verified
  green and printed `0 bytes`. Rejected since `TASK_PHP_004`, along with a span
  that runs past EOF and one that is only whitespace. Negatives:
  `.temp/php4/m5_prov_test.py`.
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
- ⚠ **NEVER cite a build tree.** ⚠⚠ **The RULE stands; the reason this line
  gave was measured false** (`TASK_PHP_003` M3, settled at `TASK_PHP_004`):
  **8 of the 12** extracted `php-5.0.0` trees on this box carry a
  **byte-identical pristine** `Zend/zend_alloc.c`, the `REAL_SIZE(size)→(size)`
  patch exists in **exactly one** (at `:132`, not `:135`), and **it does not
  delete the truncation** — `real_size` is still `unsigned int`. The real
  reason to cite the tarball is that a *some-trees-are-patched* corpus is one
  where you cannot tell by looking which tree you are in, and the two
  `ZEND_DISABLE_MEMORY_CACHE 0→1` trees are far more consequential than the
  one this line named. Full enumeration: `patterns-php/SOURCES.md` §3.
- `echoes: ["pNN"]` records where a `patterns/` row covers the same mechanism.
  ⚠ **It is a cross-reference for us and NEVER a filter** — `patterns-php/` is
  fresh, and *"that's p35's mechanism"* may not refuse a candidate
  (`PLAN_PHP.md` §3.1, `DP-03`).

---

## E. Running anything — the shim, and the one command that is not optional

**Never run `harness/check.py` directly on a php row.** Everything goes
through the driver, which builds the shim, verifies the digest bridge and
checks provenance first.

⚠⚠ **AND THAT SENTENCE IS A CONVENTION, NOT A MECHANISM — SAID PLAINLY HERE
BECAUSE A HALF-TRUE CLAIM IS WORSE THAN NONE** (`TASK_PHP_005` §1, landed
`TASK_PHP_006` §1.3). What is and is not enforced:

⚠⚠ **THE ✅ ENFORCED ROW USED TO NAME *"the `c/` subdirectory ban, the allocator
closure"*, AND `TASK_PHP_007` m5 CALLED IT OUT: B1/B2/M1 had made both
half-true in exactly the sense a reader would take.** Rewritten at
`TASK_PHP_008` to name mechanisms that are sound rather than mechanisms that
exist.

| | |
|---|---|
| ✅ **enforced** | every check in `gate.py`'s preflight, **nine stages, eight of which can fail** — the shim link, the digest bridge, `c_digest_audit` (**every `c/` file keyed, plus since `TASK_PHP_010` the row-directory whitelist `{c, inputs, controls}` and the refusal of a DOTTED row**), the **unconditional** `c/emalloc_shim.h` symlink, the overlap self-test, the manifest, provenance, and **preflight coverage** (a failure since `TASK_PHP_008` §3, ⚠ **scoped to the row in hand since `TASK_PHP_010` §3** — another row's uncertifiable record is printed and recorded, and `gate.py --audit` is the global spelling with an exit code). All exit 2 and do not run the tool. ⚠ Stage 8, `why_sizes`, is a REPORTED number and cannot fail — that is deliberate and stated in the code. |
| ✅ **recorded** | `results-php/preflight/<row>.preflight.json`, **committed** since `TASK_PHP_006`, one entry per run, appended and never overwritten. It carries `harness_php_sha256`, the manifest hash, and whether `--no-provenance` was used. ⚠ Identical runs collapse on **content**, not adjacency (`TASK_PHP_008` M3 — two alternating routine commands used to grow it without bound), and the list is capped at `MAX_RUNS`: first, last, then evidence-carrying newest-first, then the rest. ⚠⚠ **Evidence is a PRIORITY, not an EXEMPTION, since `TASK_PHP_010` §4** — the exemption made the cap unenforceable for the only class that accumulates (`TASK_PHP_009` m2: **1000 failing runs kept 1000**, ~1.4 MB in a committed file, while the test that cleared the cap used 1000 *clean* ones, which capped at 40). A dropped evidence entry is counted in `_dropped_evidence_runs`. |
| ⚠ **not read-only** | **a FAILING run grows a COMMITTED file** (`TASK_PHP_009` m5): one failed `gate.py --tool measure --check-stale` added **52 lines** to `results-php/preflight/_norow.preflight.json`. So a probe that plants into `common-php/` dirties `results-php/` as a second-order effect — **print `git status` inside every `finally:`**, not just the sha256 of what you meant to touch. |
| ✅ **detected** | a php record with **no** preflight record beside it, **and one whose every recorded run failed, skipped provenance or ran on a broken shim** (`TASK_PHP_008` M5 — `--audit` used to ask only whether the FILE existed and called such a row `complete`). `gate.py --audit` exits 1; the preflight now **fails**. |
| ❌ **NOT enforced** | **that the wrapper ran at all.** `grep -c preflight harness/{check,measure,report}.py` → `0 0 0`; a gate record's `invocation` is `check.py`'s own argv and is **byte-identical** whether the run came through `gate.py` or straight out of the shim, which `PLAN_PHP.md` §2.1a documents as a supported spelling. Closing it needs `check.py` to know about `harness-php/`, i.e. a `harness/` edit and a 33-pattern re-gate. |
| ❌ **NOT enforced** | **the kernel-overlap floor**, demoted to a reported number at `TASK_PHP_008` §2. And ⚠ **`uses_allocator` is a declaration nothing reads.** |
| ❌ **NOT a pin** | nothing hashes the preflight record. It can prove `--no-provenance` **was** used; it cannot prove it was not. |

⚠⚠ **AND ONE THING THE DIGEST CANNOT DO, MEASURED AT `TASK_PHP_008`
(`.temp/php8/12-added-key-blindspot.log`): `measure.py::_compare` iterates the
**recorded** keys, so a file ADDED to `<row>/c/` is invisible to
`--check-stale` — adding `c/emalloc_shim.h` left `results-php/ph00-smoke.json`
reporting `FRESH`.** A row measured *before* its link exists therefore has a
record nothing will ever complain about. **The preflight is what closes that,
not the digest** — which is a reason to keep the preflight failing loudly, and
a reason not to read `0 STALE` as "every source is pinned".

⚠⚠ **AND `0 STALE` DOES NOT MEAN "EVERY PINNED SOURCE STILL EXISTS" EITHER —
IT MEANS EVERY PINNED SOURCE STILL MATCHES *OR HAS BEEN DELETED***
(`TASK_PHP_009` m3, measured in `.temp/php9/14-survival.log` §B).
`measure.py:270-278` iterates the **recorded** keys and `:338-348` increments
`bad` only on `stale or bstale`, so a **missing** file prints its own
`MISSING` line and **does not fail the run**: moving `ph00-smoke/c/emalloc_shim.h`
aside gave `FRESH … 29 source(s)` *and* `MISSING … c/emalloc_shim.h` *and*
`2 record(s) examined, 0 STALE`, exit 0. ⚠ The bracket quotes the summary line,
which is exactly where that does not show. **The preflight catches it (1
problem); `--check-stale` does not.** It is a `harness/` property, identical on
all 33 PAT rows, and it is **known, not fixed** — the fix is a `harness/` edit
and a 33-pattern re-gate.

⚠ **So the honest reading of a green php gate record is: *the tree passed the
PAT gate*. The preflight record beside it is EVIDENCE that the php-specific
checks also passed, and its absence is evidence they did not run.**

⚠⚠ **A BRAND-NEW ROW COSTS SIX COMMANDS (~28 min), NOT THREE, AND THE ORDER IS
LOAD-BEARING. MEASURED AT `TASK_PHP_002` — `ph00-smoke` needed all six:**

> ⚠ **This header said FIVE over a SIX-command body** — `.tasks/PROTOCOL.md`
> rule 13's exact failure mode (*"in a long doc item only the body gets
> maintained; the header rots"*), reproduced in a brand-new document within one
> task of the rule being restated. Corrected at `TASK_PHP_004` from
> `TASK_PHP_003` M4. The body below, `RECAP_PHP.md` open item 11 and
> `harness-php/gate.py`'s docstring now all say **six**.

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
  all. Both are true; **six** is the figure to plan against.

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
(sha256 `59748cce2db5…`).

⚠⚠⚠ **THERE IS NO SIZE RULE ON `why`, AND THAT IS NOW A MEASURED CONCLUSION
RATHER THAN AN OMISSION.** This paragraph used to read *"`RECAP_PHP.md`'s 'a
`spec.md` `why` stays ≤ 200 words' can therefore only mean 200 words of
ROW-SPECIFIC prose before that paragraph — p01's row-specific half is 201 words
… so p01 already complies"*. ⚠ **p01 is 201 against a limit of 200: the sentence
said the template complies while its own number says it does not.** That was the
third version of the rule and the second that could not be met
(`RECAP_PHP.md` open item 19). `TASK_PHP_006` measured the corpus and proposes
**(c) no rule** — see `harness-php/gate.py::why_sizes`, which carries the
argument and the numbers:

- a **word limit** is out: over the 33 built PAT rows, min 197, median 989,
  p90 1817, **max 3140**, quartiles 527 / 989 / 1544. Anything at or below the
  upper quartile refuses a quarter of the built corpus; anything the corpus
  meets permits ~3× the median. And imposing one on PAT means editing text
  **inside the hashed block** on 33 rows — 33 `contract_sha256` moves.
- a **paragraph rule** is out: ⚠ **0 of 34 `why` strings contain a single
  newline**, so none of them has a second paragraph to be "unbounded
  thereafter", and giving them one is the same 33 re-gates.
- a **first-sentence rule** is satisfiable (median 26 words, max 80) and
  **vacuous**: there are only **14 distinct openers across 34 rows**, and 22
  rows open with one of exactly two boilerplate sentences.
- ⚠ **`TASK_PHP_005` F-5's own table understates the corpus**, because it
  measured only the PREFIX. Two rows carry prose *after* the shared block —
  `p16-tlv-walk`'s tail is **3 031 words**, so p16's row-specific half is
  **3 140, the largest in the corpus**, where F-5 lists it as the smallest at
  109. `check.py:1866` says in passing that p17 does this; p16 does it four
  times harder.

**What replaces the rule:** every preflight prints and records each php row's
row-specific `why` size beside the corpus band. It is a **number in front of
the writer, not a bar** — an unenforced size rule is what produced both
previous failures, and a reported size is not a rule at all.

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
- ⚠ **THAT COMMAND DOES NOT EXAMINE `results-php/` AT ALL.** It globs
  `results/p*.json` and `results/gate/p*.json` off the *real* REPO. The php
  half is a second command and it was missing from this list until
  `TASK_PHP_004`:

  ```sh
  python3 harness-php/gate.py --tool measure --check-stale   # -> 2 record(s), 0 STALE
  ```

  Run **both**. The PAT one proves you touched nothing; the php one proves your
  own records still match their sources.
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
6. **`c/emalloc_shim.h` symlinked — ALWAYS, allocating or not** (§B2), **and
   `uses_allocator` declared** in the `provenance` block with a reason.
7. `echoes: [pNN]` where a PAT row shares the mechanism.
8. ⚠ **A cost with no mechanism is an incomplete row** (`PLAN_PHP.md` §7 rule
   12). Name *why* from the disassembly: which check elided, which load came
   back, what LLVM failed to hoist. This is the item that decides whether the
   crash course is useful.
9. ⚠⚠ **READ THE KERNEL-OVERLAP NUMBER AND SAY WHAT YOU THINK OF IT, IN
   `NOTES.md`.** `TASK_PHP_008` §2 demoted it from a floor to a report, which
   moved the judgement from the tool to a person — **you**. It is now the
   *only* thing that looks at whether the row's C resembles what it cites, and
   nothing will fail if you ignore it. ⚠ **The demotion is free today only
   because no real row has ever been adjudicated by it** — `ph00-smoke`
   declares `php_provenance: false`, so the floor never fired on anything but
   a fixture. **The first `verbatim` row is where that stops being true.**
   Read `unevaluable_conditionals`'s count beside it: a kernel with many
   conditions the heuristic cannot evaluate is a kernel whose number means
   less.
