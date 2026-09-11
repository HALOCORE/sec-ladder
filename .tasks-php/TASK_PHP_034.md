# TASK_PHP_034 — the R1h hunt for `ph45`, and the build brief for the FIRST TYPE ROW

**Role:** research **engineer**, investigation only. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_034_REPORT.md` — **write the FILE** (rule 10).

⭐ **You are the hunt, not the build.** `TASK_PHP_031` did this job for `ph64`
and `TASK_PHP_032` built straight from its §6 without restating it. **Produce a
§6-shaped BUILD BRIEF** and let the build task point at it. ⚠ *Two copies of one
specification is how both go stale.*

⚠ **READ-ONLY on the tree.** You add no pattern directory, edit no `spec.md`,
and gate nothing. Scratch under `.temp/php34/`. **Never `/tmp`.**

⚠⚠ **A CONCURRENT TASK (`TASK_PHP_033`) IS EDITING
`patterns-php/ph29-recvfrom-alloc/` AND RE-GATING IT.** Do not read `ph29` as a
stable template and **do not touch it**. Your template for conventions is
`patterns-php/ph07-strcut-cursor/` — discharged, re-gated, read-only for you.

**Read**, in this order:
1. `.tasks/PROTOCOL.md` — rules 9, 10, 11, 13, **14**.
2. `.tasks-php/PROTOCOL_PHP.md` — **§C and §F5 are the heart of this task**;
   also §G/§G1 and §A2a.
3. `.memory-php/` 00–04 **in full** — authoritative; supersedes any task report.
4. ⭐⭐ **`.tasks-php/TASK_PHP_031_REPORT.md` in full.** It is the only completed
   R1h hunt. §1 is the method, §3 is the verdict shape, §4 is *"is the fix
   correct AND complete?"*, §6 is the brief shape you must produce, and §7 is
   what it found wrong in its own task file. **Copy its method, not its
   conclusions.**
5. `patterns-php/SOURCES.md` §2 — the tarball read recipe.
6. `patterns-php/CATALOGUE.md` — `ph45`'s Part A row (line ~139) and Part B
   block (line ~591).

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/` — a **concurrent session**
edits it.
⚠ **`grep -a` ALWAYS** (F35: plain `grep` is `ugrep` here and exits 1 with no
output on 41 of 1170 corpus files, **silently**). ⭐ **Ask about a FUNCTION, not
about text.**
⚠ **No `until … sleep` poller loops.** Foreground `sleep` is blocked; a previous
task leaked ~60 shells that way. One tracked background job, wait for its
notification.

**Bracket**: not required — you gate nothing. ⚠ If you run one anyway, `_033` may
be mid-re-gate; a moved `ph29` figure is **its** work, not damage.

---

## §1 Why `ph45`, and why the hunt comes first

**The type axis is at ZERO rows.** Spatial has 3 (`ph03`, `ph07`, `ph16`,
`ph29`), temporal has 1 (`ph64`, row 5). `ph45` is the manager's pick as the
cheapest first type row, from `.temp/mgr168/type_triage.py` (`--axis type`,
29 rows triaged, 11 passing every cheapness gate):

```
ph45      5 lines  mbfl_filt_conv_html_dec_ctor   mbfilter_htmlent.c:CRASH-123  fix=e8901dc17087
ph96     12 lines  zend_std_unset_dimension       zend_object_handlers.c:CRASH-061
ph58     16 lines  generate_free_switch_expr      zend_compile.c:CRASH-055
```

⭐ **And it sidesteps F24's shared-`zval.h` prerequisite entirely** — the debt
that makes most type rows expensive. **Verified by the manager against the
pinned tarball**, not inherited:

* `zval` occurrences in `mbfilter_htmlent.c`: **0**
* its includes: `config.h`, `string.h`, `strings.h`, `mbfilter.h`,
  `mbfilter_htmlent.h`, `html_entities.h` — **no Zend header**

⚠ **The hunt comes before the build because `ph64` established that it must.**
`TASK_PHP_031` corrected three of the manager's premises and refuted the
manager's *"I lean two rows"*. Assume this file has the same error rate.

---

## §2 What is measured, what is the manager's, and what is unreviewed

### ✅ Measured against the pinned tarball (sha256 `5783e0c0…d6919`, 5 595 997 B)

`ext/mbstring/libmbfl/mbfl/mbfl_convert.h:49`
```c
	int cache;
```
`ext/mbstring/libmbfl/filters/mbfilter_htmlent.c`
```c
:161	filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);
:169		mbfl_free((void*)filter->cache);
:178	char *buffer = (char*)filter->cache;
:183			buffer[0] = '&';
```
**Five lines, one struct field, two functions.** That is the whole mechanism:
a heap pointer stored in an `int`, truncated; freed through the truncated
value; cast back and written through.

### ✅ Measured from `index.csv` (corpus row `CRASH-123` / `V5C-123`)

| field | value |
|---|---|
| `vuln_class` | `memory-corruption` |
| `engine_locus` | **`pure-ext`** |
| `cwe` | `CWE-787` |
| `category` | `wild-pointer-deref` |
| `fix_commit` | **`e8901dc17087`** — one id, one fix, so **item 48 does not arise** |
| `history_status` | `historical-known` |
| `merged_members` | *(empty)* |
| `confidence` | `high` |
| ⚠ `crashes_pristine_5_0_0` | **`False`** — **§3 is about this** |

### ✅ Measured from the fix survey (`.temp/mgr/batch/fixsurvey.json`)

```
sha      e8901dc17087        author  Moriyoshi Koizumi      date  Mon, 21 Feb 2005
subject  - Fix bug #30573 (compiler warning due to invalid type cast)
files    ext/mbstring/libmbfl/filters/mbfilter_htmlent.c
         ext/mbstring/libmbfl/mbfl/mbfl_convert.h        n_files 2   bytes 2398
verdict  same-file
```

⚠⚠ **F45's shape: the subject calls it a COMPILER-WARNING fix, not a crash
fix.** That is the pattern that has misled this programme before, and §C's
standing rule applies — **an upstream fix is not automatically correct.**

⭐ **But the counter-evidence is strong and it is structural, not rhetorical:
the commit touches BOTH cited files** — the file with the truncating store *and*
the file with the field declaration — in 2 398 bytes. A pure warning-silencing
change would cast at the use site; changing the *declaration* is what actually
removes the defect. **Settle which it is by reading the patch, not the subject.**

### ⚠ UNREVIEWED — the manager's, and it carries no review

Everything in §3 below. `TASK_PHP_031` overturned three premises of its own task
file; treat these the same way and **say so in §7 of your report if they are
wrong.**

---

## §3 ⭐⭐ THE QUESTION I MOST WANT ANSWERED

**`crashes_pristine_5_0_0` is `False`. Why — and what does the row have to do to
make the defect DETERMINISTIC?**

The admission bar is C-side and this row clears it on mechanism. But a row
prices nothing unless its adversarial input **reliably** exhibits the error, and
here the trigger depends on **where the allocator happens to put the block**:
`(int)ptr` only loses information when the pointer exceeds 32 bits, and the
sign-extension back through `(char*)` only goes wild when bit 31 is set.

⚠ **My hypothesis, and it is UNVERIFIED — do not adopt it, test it.** On a
modern 64-bit Linux the heap sits far above 2³², so truncation should be close
to guaranteed, which would make `False` surprising. Candidate explanations, none
confirmed: the corpus's crash determination used a build where the filter path
was never reached; the truncated value happened to stay mappable; the build was
32-bit; or the `False` is about the *shipped input* rather than the mechanism.
**Find out which.** A clean negative here is worth as much as a finding —
`_031` §4.4 is the precedent.

⭐ **The precedent for FORCING it is in this corpus already: `ph29`.**
`common-php/emalloc_shim.h` transcribes PHP's own allocator line-for-line, which
makes the allocator's behaviour deterministic **and puts it in the checksum**
(`PROTOCOL_PHP.md` B1.2) rather than only in a sanitizer. `ph45` plausibly needs
the same move — an allocation whose returned address is controlled — and if so,
**say exactly what it must guarantee**, because that is the thing a build task
will otherwise stall on. ⚠ `ph29` is being re-gated by `_033` **right now**:
read `common-php/emalloc_shim.h` (stable), not `ph29/`.

---

## §4 What you must deliver

1. **The R1h verdict, `_029`/`_031` shape.** Is `e8901dc17087` the fix? Quote
   the hunk. Does it apply to pristine 5.0.0 — and if it is a backport, what is
   the fuzz, frame by frame?
2. **§C's second half: is the fix CORRECT, and is it COMPLETE?** `_031` §4 is
   the template. ⚠ If it silences a warning without removing the truncation,
   **that is a finding and the row still stands** — you then owe the question of
   what R1h ships instead, or whether the row has none.
   ⚠⚠ **Do NOT "scan tags until one suits."** That trap has been refused twice.
3. **§3 answered**, with evidence.
4. **The tier.** The catalogue says `verbatim`. `ph64`'s was corrected
   `verbatim → narrowed` during its build. **Re-derive it; do not inherit it.**
5. **A §6-shaped BUILD BRIEF**: the spans and their `extract_sha256`, the
   trigger, the fixture, the oracle, the benign corpus, what R1h ships, and the
   mechanical items a build task trips on.
6. **The oracle, measured.** `_031` §6.4 called this *"the thing that would have
   stalled a build task"* and it was right. The catalogue proposes
   `u64 = decoded bytes + (allocs, frees)`. ⚠ **`ph64`'s catalogue oracle turned
   out to measure NOTHING.** Test this one before recommending it.

---

## §5 ⚠ The traps this specific task walks into

1. ⚠⚠ **The catalogue's own `risk` line for `ph45` says: *"cite `:178` and
   `:183`"*.** `ADJUDICATION_001.md` §0/§1b give `:177` and `:181` — **off by
   one and by two.** The CSV's `:183` is right, and the manager's tarball read
   above confirms `:178` and `:183`. Use the verified lines.
2. ⚠ The catalogue calls `ph45` **"the only row in 166 with its own
   invariant."** That is a strong claim and it is load-bearing for the R5 rung.
   **Test it or attribute it; do not repeat it.**
3. ⚠ **`(int)` truncation is IMPLEMENTATION-DEFINED, not UB**, and the
   round-trip back through `(char*)` is where it becomes wild. Getting that
   boundary right matters: F46's strengthening is that the measured corpus
   should not evaluate UB, so **state precisely which step is which** and keep
   the benign corpus on the defined side.
4. ⚠ **The ladder question is NOT an admission question.** Safe Rust cannot
   store a pointer in an `i32` at all, so R2/R3 must model the field some other
   way (an index, a handle). ⚠⚠ **That is a RESULT to report, never a kill** —
   *"safe Rust can't express it"* is explicitly listed in `CLAUDE.md` rule 6
   among the reasons that are **findings, never kills**. Admission is decided
   **solely on the C program**. If you find yourself arguing about the Rust
   side, you have left the bar.
5. ⚠ `mbfl_malloc` is libmbfl's own wrapper, not `emalloc`. Establish what it
   actually is in 5.0.0 before assuming either.
6. ⚠ `html_enc_buffer_size` — find its definition; it decides the allocation and
   therefore the fixture.

---

## §6 What I am least sure of

* **§3, most of all.** `crashes_pristine_5_0_0 = False` is the one field that
  could turn this from "cheapest first type row" into "needs a forcing
  mechanism first", and I have a hypothesis rather than a measurement.
* **Whether the warning-fix commit really removes the defect.** The two-file
  footprint says yes; the subject says be careful. I have not read the patch.
* **The tier.** I am repeating the catalogue, which was wrong about `ph64`'s.
* **Whether 5 lines is the real size.** `ph64` was described as *"8 lines, no PHP
  machinery"* and `_031` measured **~140**. The five lines here are the
  *mechanism*; the *extraction* may be much larger once
  `mbfl_convert_filter` and the ctor/dtor plumbing come along. **Measure the
  extraction, not the mechanism**, and say both numbers.
