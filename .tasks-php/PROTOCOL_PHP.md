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

> ⚠⚠⚠ **A THIRD RULE WAS PROPOSED FOR THIS SECTION AND IS NOT HERE ON PURPOSE.
> DO NOT RE-PROPOSE IT.** `TASK_PHP_016` asked for: *"where the upstream fix
> changes benign behaviour, the measured corpus must leave its guards dead,
> `gen.py` must assert it, and the behaviour change is measured in
> `controls/`."* It was load-bearing for `ph07` as first built.
>
> ✅ **It was refused, and then the row that needed it stopped needing it.**
> `TASK_PHP_017` §4 declined it on three grounds — it makes *"does the fix
> fire?"* an unbounded corpus-selection criterion; it states as a property of
> the FIX what is a property of the GATE; and it was invented to rescue an R1h
> choice the row's own evidence called avoidable. **`TASK_PHP_018` then removed
> the need entirely**: `ph07`'s R1h became the guard configuration upstream kept
> (§C), the corpus restriction was deleted, and the row now measures the **whole**
> benign domain and gates green.
>
> ⚠⚠ **The general lesson is worth more than the rule would have been: `check.py`
> stage 7h was not an obstacle, it was CORRECT.** It refused an R1h that changes
> benign output, and the reason it changed benign output is that half of it was
> a bug PHP itself later deleted with a regression test. **A gate stage that
> refuses your row is a hypothesis about your row before it is a hypothesis
> about the gate** (`RECAP_PHP.md` F43/F47, open item 24).

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

### B1a. ⚠⚠⚠ B1.2 IS FREE ONLY AT **O(1) ALLOCATIONS PER KERNEL CALL** — and what a row does when it is not

> ⚠ **UNREVIEWED (rule 9), manager, 2026-09-12.** Discharges `RECAP_PHP.md` open
> item **54**, which has stood since F71. ⓘ The item cites *"§B2"*; the rule it
> constrains is **§B1.2**, so it is written here. ⭐ **And it costs NOTHING to
> write**: measured, `.tasks-php/PROTOCOL_PHP.md` is in **no digest** — not
> `contract_sha256` (which is `sha256` of the ```` slb-contract ```` block and
> nothing else, `check.py::read_contract`) and not `source_sha256` (40 paths,
> none of them this file). **The item was deferred for three rounds on a
> six-row-re-gate cost that does not exist.**

**THE PRECONDITION.** §B1.2 says *"fold `php_shim_tally()` into the kernel's
`u64`"*, and §B forbids a Rust rung from linking the shim — so a Rust rung
**reproduces the tally arithmetically**. ⚠ **That is free only while the number
of allocations per kernel call is O(1) in the input.** Then the Rust rung
computes a bounded count and the two rungs' allocator work is comparable.

**WHEN IT IS O(n) IT STOPS BEING FREE, AND `ph64` IS THE FIRST ROW WHERE IT IS.**
`ph64` allocates **`2n+2` blocks per call** and **60 % of the C rung's
instructions are in libc `malloc`/`free`** (F71, `TASK_PHP_032` §5). ▶ **So the
C-vs-Rust column on that row is not a safety comparison — it is largely a
comparison of an allocator against arithmetic.**

**THE DECISION — what a row does when the precondition does not hold.**

1. ⛔⛔⛔ **IT IS NOT A REFUSAL, AND THIS IS NOT NEGOTIABLE.** Admission is
   decided **solely on the C program** (`CLAUDE.md` rule 6, `RECAP_PHP.md`
   finding 53). *"There is no cost gradient"*, *"the column is not a safety
   comparison"* and *"the Rust rung cannot reproduce it cheaply"* are **FINDINGS,
   NEVER KILLS.** This bias has produced **six real refusals out of ten**.
2. **The row DECLARES the allocation order in `spec.md`** — the per-call
   allocation count as a function of the input — in a `provenance.divergences`
   entry or the `collapse.note`. **Declared, so a reader does not have to
   re-derive it from `c/kernel.c`.**
3. ⚠ **Every CROSS-LANGUAGE figure on such a row is labelled as including
   allocator work**, and **the row publishes no bare C-vs-Rust headline without
   that label.** ✅ `ph64` already took this option — *"say so loudly"* — and
   every figure is published in `marginal_ir_per_call`.
4. ⭐⭐ **AND THE POSITIVE HALF, WHICH THE ITEM DID NOT STATE: THE ROW STILL
   PRICES THE SAFETY STRATEGY.** R2-vs-R3 and R4-vs-R5 **allocate identically**,
   so the allocator term **cancels** in a same-language ratio. ▶ **The
   `fixed-R4 bound` is UNAFFECTED; it is the cross-language column that carries
   the caveat, and only that one.**

⭐⭐⭐ **THAT IS THE SAME AXIS THE STATISTIC THREAD ARRIVED AT INDEPENDENTLY.**
F89 measured the draw cancelling in a same-language ratio (**0.07 pp**) and not
cross-language (**8.63 pp**) — *"because the C rung allocates `2n+2` per call and
scales differently"*, i.e. **this rule's mechanism, measured.** And
`TASK_PHP_038` §1.5 ruled cross-language callee work **rung-attributable**.
▶ **Two threads, two methods, one boundary: same-language comparisons are clean;
cross-language ones must say what they include.**

⚠ **IT GETS WORSE ON THE TEMPORAL AXIS, NOT BETTER.** Intrusive containers
allocate **per element**, and `.memory-php/01-extraction.md`'s F1 says the
temporal defects live in exactly those containers. ▶ **Expect the precondition
to fail on most `E*` rows**, so a row that satisfies it is the exception worth
remarking on, not the rule.

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

### ⚠ WHICH `fix_commit`, WHEN A ROW'S IDS NAME SEVERAL — the §F5 spelling

⚠⚠ **UNREVIEWED. MANAGER CONSTRUCTION, 2026-09-10, LANDED WITHOUT A SECOND PAIR
OF EYES.** `RECAP_PHP.md` F48 and open item 41 are the standing record that I
have twice taken one party's construction into a standing document unattacked,
and that the rule it replaced arrived the same way. **Give this to the next
reviewer whose task touches R1h. If the reasoning below is wrong, it is one
subsection and it comes back out.**

**R1h is the `fix_commit` of the id whose `c_file_line` the row's kernel
EXTRACTS.** Singular. A kernel extracts **one** site (`PLAN_PHP.md` §3
criterion 3 — flat blob in, `u64` out); that site is one id's `c_file_line`;
that id has one `fix_commit`.

**A row's OTHER ids name other functions, and their commits are evidence about
SIBLING SITES THE ROW DOES NOT PRICE** — F50's census channel, open items 49 and
50 — **not about R1h.** ⚠ **Nothing here licenses dropping them**: the row still
cites every id it claims, and `coverage.py` still has to resolve them.

⚠ **Why not the union of the commits**: it ships a configuration **upstream never
shipped as one change**, and this whole section rests on R1h being *real upstream
code*. F43's lesson is that what upstream **kept** is the stronger citation; a
union is neither committed nor kept.

⚠⚠ **Whether those N ids belong in ONE ROW is a DIFFERENT QUESTION, decided by
§G1, and it is open item 35 — not this one.** Measured on all 30 rows whose ids
name several commits: at `file:line` **29 of 30** have every id at a distinct
line, and by **enclosing function 24 of 30**, so **no row is "one site upstream
patched N times"** and option (a) always has a spelling. ⭐ **Conflating the rung
question with the catalogue question is what made this look like the largest
unmade decision on the PHP side for as long as it did.**

⚠ **It applies to 30 of 102 rows and the load is NOT uniform** — **21 of 31
temporal (68 %)**, 6 of 29 type, **3 of 42 spatial (7 %)**. All four built rows
are spatial and none is among the 30, **so this rule went four builds without
being needed. Do not read that as four builds of evidence for it.**

⚠ **An upstream fix is not automatically correct.** The earlier attempt
measured one that, backported, still left a reachable wild write in the arm it
does not guard. **That is a result, and one of the strongest a row can carry.
Report it; do not repair it.**

⚠⚠ **AND IT MAY BE TOO BIG. `ph07`'s R1h IS A SUBSET OF ITS `fix_commit`, AND
HERE IS THE WHOLE OF WHY.** `cb3cca21b345` (2005) added two guards. Hunk (a)
closes the memory-safety defect — it removes all **15 333** out-of-bounds reads
and changes **no** benign answer. Hunk (b) removes **none** of them and changes
the answer on **13.5 %** of benign calls, and `c2471b495009` (2009-09-23)
**deleted it as bug #49354, with a regression test** that
`patterns-php/ph07-strcut-cursor/controls/bug49354.py` replays: **hunk (a) alone
agrees with upstream on all six cases; the two-hunk fix does not.** So `ph07`'s
R1h is the configuration `php-5.2.12 … php-5.2.17` shipped and kept,
`PHP_FUNCTION(mb_strcut)` body sha256 `26e2099e33433c74`. The row states that —
both commits cited, both patches under `controls/`, what each hunk buys measured
separately, and the alternative it was chosen against — **inside its hashed
`spec.md` block** (`idiom.required[4]`).
⭐ **`check.py` stage 7h refused the two-hunk version in the first hour the row
existed, and stage 7h was RIGHT**: it detected the same defect PHP's own
maintainers detected four years later, from a bug report.

⚠⚠ **WHETHER THIS GENERALISES IS OPEN. n = 1, AND NOTHING HERE PERMITS A SECOND
ROW ANYTHING.** A row that wants to do the same **brings it to the manager as a
proposal**; the shape `ph07`'s took is above, and the question to ask about a
second one is whether an **upstream artefact** decides it — a later removal, a
regression test, a bug number — rather than the row's convenience. **Without
that, *"cite a tagged configuration"* lets an engineer scan tags until one
suits**, which is choosing the fix to fit the corpus instead of the corpus to
fit the fix. ⚠ **Two drafts of this passage were written as a PERMISSION and
both were refused** — `TASK_PHP_018` §4.1 refused the manager's, `TASK_PHP_022`
§5.1 refused the manager's re-wording of it. **The asymmetry is the reason: an
under-stated observation costs one task when a second row needs it; an
over-stated norm is what has to be un-landed** (`RECAP_PHP.md` F48, open
item 24).

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
   ⭐⭐ **AND HERE IS WHERE TO GET IT, WHICH NOTHING USED TO SAY.** The corpus
   index — `paper/evaluation/security/vuln-corpus-5.0/index.csv` — has a
   **`fix_commit` column carrying a sha for all 166 rows**, and every catalogued
   row is already surveyed in **`.tasks-php/FIXSURVEY_001.md`**
   (`python3 .tasks-php/fixsurvey.py`). **Two tasks were spent on archaeology
   that one lookup answers** (`RECAP_PHP.md` F38).
   ⚠⚠ **BUT THE COLUMN NAMES *A* FIX, NOT NECESSARILY THE ONE THAT REMOVES THE
   5.0.0 DEFECT.** Of the commits checked by hand, **`ph12`, `ph21` and `ph22`
   all name a LATER hardening**, and **31 % of rows carry a fix dated 2010 or
   later**. **So the step is three-part and none of it is optional:**
   **(i)** read the column; **(ii)** fetch
   `https://github.com/php/php-src/commit/<sha>.patch` (a bare-SHA `git fetch`
   is refused); **(iii)** ⚠ **confirm against the release tags that this commit
   removes YOUR defect — if it does not, cite both and say which is which.**
   ⚠ **Check `history_status` too** (`fixed-by-rewrite` on 17 rows) **but never
   as a substitute for (iii): every batch row is `historical-known` with
   `confidence: high`, including the two whose commits are wrong.**
   ⚠ **8 rows' fixes are in a DIFFERENT FILE from the defect** and 1 (`ph36`)
   **has no sha at all** — `(bison-regeneration; no single commit)`, the one
   documented exception to this item.
6. ⚠⚠⚠ **SEARCHING THE CORPUS: ALWAYS `grep -a`.** `grep` in a `Bash` call is a
   shell function dispatching to `ugrep`, and on a file containing **one**
   non-UTF-8 byte it exits **1 with no stdout and no stderr** — which reads
   exactly like *"not present"*. **41 of the corpus's 1 170 `.c`/`.h` files are
   such files**, including **`ext/standard/string.c`**, which **13 catalogued
   rows cite**. `grep -a`, `/usr/bin/grep` and `rg`/the `Grep` tool are all fine.
   ⚠⚠ **A probe script does NOT reproduce the failure** — shell functions are not
   exported to `sh` — **so "I wrapped it in a script and it worked" proves
   nothing.** (`RECAP_PHP.md` F35.)
   ⭐ **And ask about a FUNCTION, not about text**: `TASK_PHP_016` built a
   history table by grepping for a *guard* and got it wrong in both directions —
   a renamed guard read as absent, an unanchored pattern matching a *different
   function* read as present — **and neither error is visible from its own
   output.**
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

### F6. ⛔⛔ A ROW'S `spec.md` AND `NOTES.md` MUST NOT CITE `.temp/` — commit the probe instead

> ⚠ **UNREVIEWED (rule 9), manager, 2026-09-12.** Free to write:
> `PROTOCOL_PHP.md` is in no digest (§B1a). **Enforced by
> `python3 .tasks-php/citecheck.py`**, extended the same day with four must-fire
> negatives (§H binds it).

**THE RULE.** `.temp/` is gitignored and `CLAUDE.md` constraint 6 mandates
deleting its artefacts once the gates are green. ▶ **So a `.temp/` path in a
row's `spec.md` or `NOTES.md` is a committed claim resting on evidence that is
scheduled for deletion** — and in `spec.md`'s contract block it is **frozen into
`contract_sha256`**, i.e. into the gate record of that row forever.

**WHAT TO DO INSTEAD:** if a probe is the evidence, **ship it under
`controls/`** and cite it there. ⭐ `ph53` did exactly this for two of its three
citations — `controls/mu_unwrapped.rs`, added to
`controls/negatives.py --verus` as a must-NOT-fire arm **so it is RUN on every
invocation rather than merely cited.** ▶ **That is the pattern: a committed
generator, exercised, not a pointer.**

⚠⚠ **THIS IS NOT A NEW RULE BEING IMPOSED ON A CLEAN CORPUS — IT IS A CENSUS,
AND THE CORPUS IS ALREADY IN BREACH.** Measured 2026-09-12 by the extended
`citecheck.py`:

| | |
|---|---|
| row-specific `.temp/` citations **inside a hashed `spec.md` contract** | **9, across 6 of 8 rows** — `ph00`, `ph03` ×3, `ph07`, `ph16`, `ph45` ×2, `ph53` |
| row-specific `.temp/` citations in `NOTES.md` | **~90, across all 8 rows** |
| ⛔ **already GONE** | **3** — `.temp/php13/bin`, `.temp/php16/tb`, `.temp/php36/bin` |
| inherited from the byte-identical shared `why` block (PAT-era) | **3**, and repairing those is a **six-row re-gate** — open items 55/61, **not a row's debt** |

▶ ⭐ **So `ph53` is the SIXTH row to do this and the only one that NOTICED** —
it found its own, repaired two of three, and reported the gap that let the third
through. **The rule exists because of the census, not because of that row.**

⛔ **DO NOT bulk-repair the 99.** `spec.md` and `NOTES.md` are both in
`source_sha256`, so it is a **re-gate per row and no re-measure** — batch each
row's citations with that row's next re-gate. **What this rule binds is the NEXT
row**, and `citecheck.py` is what makes that enforceable rather than remembered.

### F6a. ⭐ A `c/*` COMMENT MAY **POINT** AT AN ARGUMENT; IT MAY NOT **STATE** THAT ARGUMENT'S VERDICT

**`c/*` is in the MEASUREMENT digest, so a comment inside a C kernel is frozen at
32-cell re-measure price.** Any claim in one that a later task can refute is
therefore *effectively unrepairable* — which is `RECAP_PHP.md` **F98**, where
`ph53/c/kernel_hardened.c:8-9` still asserts *"and `preimage_screen.py` labels it
`NOT-THE-REPAIR` independently"*, a route `F95`'s own repair withdrew.

▶ **THE RULE, AND IT IS A DISTINCTION RATHER THAN A BAN:**

| | example | at risk? |
|---|---|---|
| ✅ **POINTER** | *"`NOTES.md` §7 says so in terms"* · *"`controls/fortify.py` measures both configurations"* | **NO** — it asserts nothing, so it cannot age into falsehood. If the target changes, the pointer is stale and the C file is still true |
| ✅ **SPAN CITATION** | `/* ==== basic_functions.c:2102-2137 ==== */` | **NO** — it cites the **pinned** tarball, which cannot change |
| ⛔ **VERDICT** | *"`preimage_screen.py` labels it `NOT-THE-REPAIR` independently"* | **YES** — it asserts another artefact's **conclusion**, and that artefact is not in this digest |

✅ **THE CORPUS ALREADY FOLLOWS THIS**, measured 2026-09-13 by
`.tasks-php/contract_audit.py`: **27 pointers against 6 raw verdict hits, of which
exactly 2 are real — and both are the two lines of F98's own known sentence.**
⭐ **So this ratifies practice rather than changing it, and NO ROW OWES A REPAIR.**
▶ **It binds the NEXT kernel comment.** ⓘ `contract_audit.py` adjudicates every
verdict hit by hand and fails on an **unfiled** or **stale** one, because the
classifier is a grep and greps have spellings (`RECAP_PHP.md` **F10**).

### F6b. ⓘ `results-php/preflight/_norow.preflight.json` IS **EXPECTED TO MOVE**, AND IT IS IN NO DIGEST

Taking the bracket reading this protocol requires **writes** to that file, so
`git status` shows it modified after any task that obeys its own instructions.
✅ **That is correct and costs nothing: measured 2026-09-13 over all 18 gate and
measurement records — 0 mention `preflight` at all, and 0 digest entries name a
preflight path.** ▶ **So a moved preflight record can never stale a measurement,
and it is not evidence that anything went wrong.**
⚠ **It is a DE-DUPLICATING LEDGER, not a per-invocation log** — `runs` de-dupes on
content, so **counting `runs` UNDERCOUNTS gate invocations** (`RECAP_PHP.md` item
103). ⓘ `contract_audit.py`'s `N7` fails if a preflight path is ever hashed, so
this ruling cannot go stale silently.

---

## G. Is this candidate a duplicate of a built or catalogued row?

⚠⚠ **UNREVIEWED — `TASK_PHP_023` §4.3's restatement, landed by the manager and
owing a second pair of eyes.** It is recorded here because the version it
replaces was **folklore**: `TASK_PHP_019` wrote it in a report, the manager
adopted it without review, used it himself to overturn a verdict, and it was
never written into any standing document where it could be attacked.

⚠⚠⚠ **THIS IS A CHECKLIST, NOT A DECISION PROCEDURE, AND IT MUST BE QUOTED AS
ONE.** (a)(b)(c) below have no stated level of abstraction, so **the verdict is
a function of the description, not of the C** — any pair can be made the same by
describing coarsely and different by describing finely. `TASK_PHP_019` §7
concedes the old rule returns **both answers** on `CRASH-090` and breaks the tie
from outside itself. **Describe at the level the catalogue already uses, and
state the level in the note so it can be attacked.**

> **ONE TEST, ONE BURDEN: *can I show these are the SAME?*** Kill only on a
> proof of *same* — (a) the unchecked predicate, (b) the attacker-controlled
> quantity, (c) the fault primitive, **all three**, at a stated level of
> description. Anything else is a row.

⚠ **The burden is the half that was always right**, and it is the correct
inversion of the corpus's own `merged_members` predicate (`TASK_PHP_019` §3,
verified verbatim at `TASK_PHP_023` §6.1). ⚠ **The old rule's three names had
only two outcomes** — `PLAN_PHP.md` §3.1 admits a slight variation, so
`SLIGHT VARIATION` and `DIFFERENT MECHANISM` both produce a row — which made it
look more discriminating than it is and invited arguments that change nothing.

### G1. ⚠⚠⚠ The upstream fix, and the asymmetry the old rule did not state

The old second disjunct — *"different upstream fixes, each of which leaves the
other standing"* — **is not a C-side test and it failed a measurement.**

- ✅ **A DISTINCT fix is admitted as evidence for DIFFERENT.**
- ⚠⚠⚠ **A SHARED fix is NOT evidence for SAME.** One commit routinely repairs
  unrelated errors in one file: `56adfe1f3cf1` fixes `ent_uni_338_402`'s
  **count** and, in the same patch, two pure **name** typos in a correctly-sized
  table. **Absence of a distinguishing fix is not presence of a shared
  mechanism** — and that is exactly the inference that put a false sentence into
  `ph32` (`TASK_PHP_023` §0 B2, §2.6).
- ⚠ **It is contingent** on what a maintainer noticed and in which batch, and
  **often counterfactual** (`TASK_PHP_019` §10.5 concedes one direction is).
- ⚠ **It is silent on a large part of the corpus**: `ph36` has no sha, 17 rows
  are `fixed-by-rewrite`, 31 % of fixes are 2010 or later.
- ⚠⚠ **Any fix-commit claim is verified AT THE COMMIT, never at the column** —
  §F5(iii), and `.memory-php/02-ladder.md`'s warning that the column *"names **a**
  fix for the row's function, NOT necessarily the one that removes the 5.0.0
  defect"*. **§2.6 is that warning firing on a hand-bisected chain: the disjunct
  fired correctly for `ph102` and incorrectly for `ph32`, in one paragraph.**

⚠ **The manager's own use of the old rule survives** — `CRASH-090` → `ph102` is
right, re-derived from the patch bytes — but ***"the rule got the answer right"*
and *"the rule is sound"* are different claims.**

### G2. The stop condition for a batch of new rows

⚠⚠ **`TASK_PHP_021`'s *"more than two corrections → stop"* counts heterogeneous
things.** Measured on the batch it fired on: `ph94` was *about something other
than what it said*, `ph98`'s trigger could not be set up, `ph101`'s **witness**
was incomplete while the harm occurred. **A rule keyed on the count fires on
three typos and stays silent on one `ph94`** — over-powered in one direction,
under-powered in the other.

> ⭐ **STOP ON KIND, NOT ON COUNT: if any correction changes what the row
> CLAIMS, stop — even if it is the only one.**

⚠ Under that rule `ph94` stops the batch alone, `ph101` never enters the count,
and the stop happens for the reason that was actually true. ⚠ **And `_021` had
already folded all three corrected triggers into the landing script**, so when
the rule fired there was nothing left to repair: **the stop bought a REVIEW, not
a repair** — right on the merits, wrong in its stated reason.

---

## H. ⭐ A change to a VALIDATOR lands with its must-fire negatives, or it does not land

**`TASK_PHP_024` §5.3's formulation, in answer to a question the manager asked
about his own conduct.** It replaces the obvious framing — *"don't commit a
`harness-php/` change before it is reviewed"* — which is **weaker and slightly
wrong**, and the history says why.

`8e2d834` committed `ph07`'s rebuild **and** `provenance.py`'s `extra_spans`
schema change together. `TASK_PHP_022` then found defects in both halves —
except it did not: ⚠ **all four `extra_spans` defects were in the harness half,
and the row half survived intact** (*"nothing here invalidates the rebuild"*).

**The mechanism is not the timing. It is that a validator landed with no
negatives, and a row's green gate was allowed to stand as evidence about it.**

> ⚠⚠⚠ **A GATE RUN *EXERCISES* A VALIDATOR ON THE ROWS THAT PASS. IT DOES NOT
> *ATTACK* IT.** Three green rows say nothing about what the validator does to a
> row that should fail.

- The row half shipped with `.temp/php18/` full of controls. **The validator
  change shipped with none** — its only artefact is `extra-spans.log`, **16
  lines**, and it is a *derivation*: three spans' bytes, hashes, first and last
  lines. **No mutation, no expectation, no control.**
- The eleven must-fire negatives were written **by the reviewer, after the
  commit**.
- ⚠ **Every one of the four was minutes of work** — ~250 lines of probe caught
  all of them: drive the statistic over its subsets (~40), one scratch row with
  a bogus span (~60), `grep -n 'provenance\.py:[0-9]' harness-php/` (1), run the
  CLI under both flags and diff (~50).

⚠ **`PROTOCOL_PHP.md` §B2/§B3 already record four bypassed guards, and every
repair that stuck came with negatives** — but that was a *description of what
good repairs happened to have*, never a **landing condition**. It is one now.

⚠ **Scope**: a *validator* is anything whose output is a verdict other code or a
human trusts — `harness-php/{gate,provenance}.py`, a row's `controls/*.py`, the
manager's checkers in `.tasks-php/`. **It is not a rule about commits**, and it
binds the manager exactly as it binds an engineer.

### H1. ⛔ NEVER BACKTICK A SPELLING THAT CONTAINS A **CHARACTER LITERAL** — it is a check that cannot fail

> ⚠ **UNREVIEWED (rule 9), manager, 2026-09-12.** Discharges `RECAP_PHP.md` open
> item **55**. ⭐ **The item's cost objection was FALSE** — it said *"the rule is
> real and cheap to state and there is **nowhere cheap to state it**"*, on the
> premise that `PROTOCOL_PHP.md` is hashed. **Measured: this file is in no
> digest** (not `contract_sha256`, which is the ```` slb-contract ```` block and
> nothing else; not `source_sha256`'s 40 paths). Editing it stales nothing —
> confirmed by `66/0` and `14/0` immediately after this edit.

**THE RULE.** In `idiom.required` or `idiom.forbidden`, a declared spelling must
not contain a C character literal. `exec_code`'s layer 1 blanks *"comments and
string/char literals"*, so the matcher is handed
`read_buf[recvd] =     ;` where the source says
`read_buf[recvd] = '\0';` — **the operand is gone before matching begins.**

| where | consequence |
|---|---|
| `required` | reports `pins nothing` — visible, but only to a reader who already distrusts it. ⚠ **`ph29`'s `required[1].c` is exactly this, and it names the row's own fault line** |
| ⛔⛔ `forbidden` | **a ban that CANNOT FIRE.** Since `TASK_068` `forbidden_hits` is the half that **FAILS** the gate ▶ **so this is §H's own target — a check that silently cannot fail — sitting inside frozen infrastructure** |

**THE REPAIR IS A RESPELLING, NOT A HARNESS EDIT.** Drop the literal and pin the
prefix: `read_buf[recvd] =` pins `kernel.c:247` and `hardened:175`, **one line
each**. ⛔ **No `harness/` change is proposed or wanted** — the blanking is
deliberate and documented in `exec_code`'s own docstring, and `exec_code` is
hashed.

✅ **LATENT, NOT LIVE: 0 affected spellings across 33 PAT rows and 6 PHP rows, 0
of them `forbidden`** (F73, `.temp/mgr169/charlit_reach.py`, `--selftest` PASS,
6 must-fire negatives; the detector is **differential** — it asks whether the
shipped blanker changes the span, so it cannot drift from the matcher).
⭐⭐ **AND THAT IS WHY THIS IS A WRITING RULE AND NOT A REPAIR TASK: backticking
`read_buf[recvd] = '\0'` would CREATE the first affected spelling in either
programme.** The rule exists to stop the first one, not to clean up after it.

⚠ **SCOPE, ACCEPTED RATHER THAN SOLVED.** This is php-only, so a PAT author
never sees it — item 55's real objection, and it stands. It is accepted because
the reach is **0 of 33 PAT**, so there is nothing for a PAT author to repair
today; and because the one surface that binds both programmes unhashed is
`CLAUDE.md`'s top table, which is reserved for conventions that have actually
bitten. ▶ **If a PAT row ever ships a backticked character literal, that is the
moment this moves — and `charlit_reach.py` is the check that would say so.**
