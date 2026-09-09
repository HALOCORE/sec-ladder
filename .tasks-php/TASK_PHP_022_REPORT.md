# TASK_PHP_022_REPORT — adversarial review of the `ph07` rebuild, and of the manager's R1h decision

**Role:** research **reviewer**, one agent, alone. `PROTOCOL.md` rule 1 — I did
not build this row, I did not rebuild it, and I do not fix. I report.

**Verdict in one line:** ⭐ **§1's headline is TRUE and I wrote the proof that
demonstrates it — and the sentence RECAP promoted it into is FALSE, in a way the
row's own `NOTES.md` was already careful about.** The R1h decision survives an
independent re-derivation, the corpus is genuinely unrestricted, the ladder
reproduces to the digit, the R4 endpoint survives three more spellings, and
`bug49354.py` is a faithful replay authenticated against the patch's own blob
hash. Two **major** defects: the hashed `identity` `why` carries four figures
the rebuild refuted, and `c/kernel.h` names the wrong upstream fix.

---

## ⚠⚠⚠ READ THIS FIRST — THIS REPORT WAS COMMITTED, AND ACTED ON, WHILE IT WAS STILL BEING WRITTEN

`8e2d834` swept this file into a commit at **1087 lines**; it finished at
**1170**. `d51d231` then landed findings into `.memory-php/` from that partial
text, `9697b94` acted on §5.1, and `59738e3` opened item 36 from §6. All four
landed **while this review was running**, together with the whole `ph07` rebuild
the review is of.

⚠ **That is `PROTOCOL.md` rule 11's widened form, verbatim** — *"while a
subagent runs, do not EDIT — and do not COMMIT — any file that subagent READS or
WRITES. That includes … the subagent's own report"* — and it is the same shape
as the `TASK_149` case the rule records (*"committed a report at 970 lines that
finished at 1025"*). ✅ Nothing was lost and the landed text is faithful to what
it was taken from; the cost is that **the manager acted on a partial report**.

**What arrived AFTER `8e2d834` and is therefore in nothing that has landed:**

| | |
|---|---|
| §4.1 | the `--no-tarball` qualifier — "byte-identical" is true of the default invocation only |
| §4.2 | the corrected consumer account, and the `php_provenance: false` hole |
| **§6 m7** | **`provenance.py:836-837`'s *"adding a span cannot make the number go up"* is measurably FALSE — 75 % → 77 %** |
| **§6 m8** | **`gate.py:300`'s `provenance.py:841-843` citation went stale inside the change** |
| §7 | clean negatives 16–18 |

⚠ **And one §3.1 finding is still unlanded**: `RECAP_PHP.md:1252` and `:1754`
still say *"R4 ≡ R5 byte-identical"* without *"up to relocations"*, which
`spec.md`'s own `identity` entry carries and the record requires. It did not
reach `.memory-php/`, so the authoritative layer is clean; the handoff is not.

---

## Bracket — both, first and last

**Open**, before anything was touched:

```
$ harness/measure.py --check-stale
66 record(s) examined, 0 STALE
$ python3 harness-php/gate.py --tool measure --check-stale
FRESH  results/gate/ph00-smoke.json           29 source(s)
FRESH  results/gate/ph03-uudecode-bound.json  33 source(s)
FRESH  results/gate/ph07-strcut-cursor.json   38 source(s)
FRESH  results/ph00-smoke.json                19 source(s) + 8 input(s)
FRESH  results/ph03-uudecode-bound.json       19 source(s) + 7 input(s)
FRESH  results/ph07-strcut-cursor.json        19 source(s) + 7 input(s)
6 record(s) examined, 0 STALE
```

**Close**: see §8. ⚠ `harness-php/gate.py` is mode 644 and needs `python3` in
front — the task file's spelling fails with `Permission denied`, exactly as
`TASK_PHP_018_REPORT` warned. It cost me a run too; the warning is in the
report and not in the task file.

`git status --porcelain` was **25 entries at the start and 26 at the end**; the
one addition is **this report file** (`?? .tasks-php/TASK_PHP_022_REPORT.md`),
and the other 25 are the same 21 `M` + 4 `??` the rebuild left, unchanged.
**Nothing under `harness/`, `common/`,
`patterns/`, `results/`, `pilot/`, `patterns-php/`, `results-php/`,
`harness-php/`, `.memory-php/`, `RECAP_PHP.md`, `.tasks-php/CATALOGUE*` or
`.web/` was created, edited or deleted.** No `git add`, no `git commit`.
Scratch: `.temp/php22/` only; `.temp/php18/`, `.temp/php17/` and
`.temp/mgr165/` were read and reused, never written.

---

# §1 ⚠⚠⚠ THE HEADLINE — I WROTE THE PROOF. IT VERIFIES. AND THE SENTENCE BUILT ON IT DOES NOT.

## 1.0 The claim, and the two halves it has

`TASK_PHP_018_REPORT` §1a, promoted to `RECAP_PHP.md` F47:

> *"A memory-safety-only `ensures` would have stayed green through the entire
> rebuild **and told nobody anything**."* — and F47's section header:
> *"**ONLY A VALUE POSTCONDITION COULD HAVE NOTICED**"*.

**These are two claims and they have different answers.**

| | |
|---|---|
| *the weakened proof would have stayed green* | ✅ **TRUE. Demonstrated, not asserted — §1.1.** And more strongly than claimed: **not one character of the proof would have had to change.** |
| *…and told nobody anything / only a value postcondition could have noticed* | ❌ **FALSE — §1.4.** The gate's own stage 2 separates the two configurations on **both** benign inputs. |

⭐ **`NOTES.md:70` says only the true half** — *"A safety-only `ensures` would
have stayed green."* **The row was already careful and the handoff was not.**
That is `CLAUDE.md`'s own recorded failure mode (the report over-claiming where
`SYNTHESIS.md` was more careful) reproduced on the php side, one document up.

## 1.1 The proof, and the matrix

`.temp/php22/msproof/gen_ms.py` builds the memory-safety-only variants by
**mechanical weakening of the row's own `verus.rs`**, so the exec code is
provably the row's and only the specification differs. It audits its own output:
every needle must fire an asserted number of times, and no value-spec token
(`strcut_fold`, `walk_start`, `walk_end`, `fold_out`, `guard_from`, `guard_len`,
`head_u32`, `tally_of`, `lemma_fold_shift`) may survive **anywhere in the file**,
comments included.

`gen_ms2.py` builds the stronger reading — see §1.3.
Full log: `.temp/php22/msproof/RESULTS.log`.

| file | `ensures` | exec | plain | `--cfg slb_twin` |
|---|---|---|--:|--:|
| the row's shipped `verus.rs` | value | hunk (a) | 21 / 0 | 24 / 0 |
| **`ms_hunkab`** | **none** | **hunk (a) + (b) — PRE-018** | **17 / 0** | **20 / 0** |
| **`ms_hunka`** | **none** | **hunk (a) alone — POST-018** | **17 / 0** | **20 / 0** |
| `ms_noguard` — must FIRE | none | hunk (a) **deleted** | **16 / 1** | **19 / 1** |
| `ms_vacuous` — vacuity | none | body replaced by `0u64` | **13 / 0** | 16 / 0 |
| `ms2_hunkab` | `hi <= slen` | hunk (a) + (b) | 17 / 0 | 20 / 0 |
| `ms2_hunka` | `hi <= slen` | hunk (a) | 17 / 0 | 20 / 0 |
| `ms2_noguard` — must FIRE | `hi <= slen` | hunk (a) deleted | **16 / 1** | 19 / 1 |
| `ms2_blind` — instrumentation dropped | `hi <= slen` | hunk (a) | **17 / 0** | 20 / 0 |

`ms_noguard`'s failure is at the right obligation and nowhere else:

```
error: invariant not satisfied before loop
   --> .temp/php22/msproof/ms_noguard.rs:379:13
379 |             frm <= slen,
```

⭐⭐ **AND THE SHARPEST FORM OF THE RESULT IS A `diff`.**
`diff ms_hunkab.rs ms_hunka.rs` is **comments plus the six exec lines of hunk
(b)** and **nothing else**. Not one invariant, not one `assert`, not one ghost
binding, not one `decreases` differs between the pre-rebuild and post-rebuild
memory-safety proofs. The engineer's §6.2 — *"the one place the proof got harder
is `k = start.saturating_add(length)`, and it cost three `assert`s"* — is exactly
right, **and all three of those asserts are about `ks`, a spec quantity**. They
are value-postcondition maintenance, and the weakened proof does not have them.

⚠ **The must-fire control is what makes this worth anything.** A weakening so
aggressive that CRASH-124 also passes would prove nothing; `ms_noguard` /
`ms2_noguard` show the weakened spec still catches the row's actual defect.

## 1.2 What "memory-safety-only" cost me to define — and it is the more interesting finding

**Nothing, because for this kernel there is nothing to define.** `kernel` returns
a `u64` by value and writes no caller-visible memory. Every memory-safety
obligation lives in

* the `requires i < v@.len()` on the four trusted `external_body` items,
* the `decreases` on both walks (termination of a cursor advanced by data), and
* Verus's built-in index and arithmetic-overflow checks,

**and not one of them is an `ensures`.** So the honest memory-safety-only
specification of this kernel is the **empty postcondition**, and the weakening
is a deletion.

⚠ **That is why "it stayed green" and "it told nobody anything" are the same
fact, and why the second must not be read as a property of the ROW.** Measured:
**`ms_vacuous` — the identical kernel with its entire 132-line body replaced by
`0u64` — verifies 13 / 0.** The memory-safety-only specification does not
constrain the answer at all, which is what the row's `verus.rs:459-463` already
says in words (*"a kernel that returned 0 unconditionally would satisfy every
bounds obligation in this file"*). It is now measured rather than asserted.

⭐ **A second number that prices the same thing, and it is bigger than the row
claims.** `NOTES.md` §10b and `spec.md`'s `twin_obligations_note` record that the
rebuild took the rlimit requirement from ~10–12 plain / 15 twin down to **9 on
both**. The memory-safety-only proof verifies at **`#[verifier::rlimit(1)]`**,
plain and twin (`.temp/php22/msproof/rl1.rs`). **Essentially the entire proof
budget on this row is the value postcondition** — which is the honest way to
price it, and it is a stronger statement than "the proof got cheaper".

## 1.3 The stronger reading — and it fails for a different reason

Taking §1's wording literally (*"nothing is read past `slen`"*), I built the
strongest honest memory-safety **postcondition** as well: a ghost high-water
mark over every read of the source slice, returned and bounded.

```rust
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (res: (u64, Ghost<int>))
    requires off + len <= buf@.len(), 9 <= len,
    ensures  res.1@ <= len as int - 9,      // == slen
```

`gen_ms2.py` instruments all four `get_unchecked(s, …)` sites and **audits that
it did** (it prints `instrumented source reads: 4  uninstrumented: 0`). It costs
one ghost local, four one-line `proof` blocks and three loop invariants.
`ms2_hunkab` and `ms2_hunka` **both verify 17 / 0**, so the stronger reading
gives the same answer: **insensitive to hunk (b).**

⚠⚠ **But it is not actually stronger, and the control that shows it is
`ms2_blind`: delete all four instrumentation points and it still verifies
17 / 0.** The postcondition is satisfied by a kernel that tracks nothing. So
even an explicit *no-read-past-`slen`* `ensures` is only as good as
instrumentation that **no gate in this project forces**, and the real safety is
still carried by the trusted items' `requires`. ⭐ **That is the finding worth
carrying: on a kernel that returns a scalar, "prove memory safety" is not a
postcondition at all, and any postcondition that looks like one is bookkeeping
you have to audit by hand.**

## 1.4 ⚠⚠⚠ *"…AND TOLD NOBODY ANYTHING"* IS FALSE, AND THE ROW HAD A SECOND DETECTOR

`harness/check.py::check_checksums` (stage 2) requires **every cell** to print
the `u64` the row's `model.py` predicts, and fails if cells disagree
(`check.py:2955-2991`). Pre-rebuild, `model.py`'s three implementations, all four
Rust rungs and `verus.rs`'s exec all carried hunk (b), while `c/kernel.c` (R1)
carries no guard at all — and they agreed only because `inputs/gen.py` kept the
region where hunk (b) fires out of the corpus.

So the counterfactual has a number. `.temp/php22/checksum_probe.py` drives the
row's own `model.py` arithmetic with and without the clamp over the **shipped**
inputs:

```
small.bin    windows=32    iters=25000   moved-windows=4     (12.5%)
             checksum hunk(a) only = 0xa3cf7ad40b7e73dd
             checksum hunk(a)+(b)  = 0xbf9156aea529f3fe   DIFFERENT
large.bin    windows=2050  iters=12000   moved-windows=297   (14.5%)
             checksum hunk(a) only = 0x23cdda3228a16863
             checksum hunk(a)+(b)  = 0xbcc583bc4c8571ce   DIFFERENT
adversarial-{wild,silent,offbyone,empty}.bin      IDENTICAL (single window, not in the region)
adversarial-nowin.bin  CANNOT EVALUATE -- nwin=0, the driver never enters
2 of 7 inputs separate the two configurations by CHECKSUM ALONE (1 could not be evaluated).
```

`0xa3cf7ad40b7e73dd` = `11803788199505851357`, which is exactly the
`checksum.small.bin` every O3/isolated cell in
`results-php/ph07-strcut-cursor.json` carries — so the probe's arithmetic is the
shipped binaries', not a third model's.

⚠ **Therefore: on the rebuilt corpus, a Rust rung that had kept hunk (b) would
have failed stage 2 on `small.bin` and `large.bin` with no postcondition of any
kind.** The value `ensures` was **a** detector, not **the** detector. And in the
actual history it was not even the operative one — `TASK_PHP_018_REPORT` §1a says
plainly that the engineer *read* the rungs because §1a of the task file asked.

⚠ **A second, smaller over-claim in the same sentence.** *"Only the value
postcondition moved"* is contradicted by `NOTES.md:61-79`'s own list: the four
rungs, `verus.rs`'s exec, all three `model.py` implementations, `selfcheck`
check 2 and `inputs/gen.py` moved too. What is true is *"of the SPEC artefacts,
only the value postcondition moved"*.

### What I would land instead

The claim that survives every test I ran, and it is still a good one:

> ⭐ **A memory-safety-only `ensures` would have stayed green through the entire
> rebuild — demonstrated, `TASK_PHP_022` §1: the weakened proof verifies 17/0
> plain and 20/0 twin under BOTH guard configurations, and the two files differ
> only by hunk (b)'s six exec lines. It stays green because it says nothing: the
> same kernel with its body replaced by `0u64` also verifies (13/0), and the
> whole of this row's proof budget is the value postcondition (memory-safety-only
> verifies at rlimit 1 against the row's 9).** ⚠ **It is NOT true that only the
> value postcondition could have noticed**: on the rebuilt corpus the gate's
> stage-2 checksum separates the two configurations on both benign inputs
> (4/32 and 297/2050 windows move). **What the value postcondition uniquely
> gives is not detection — it is having to SAY which function the rung computes.**

---

# §2 THE R1h DECISION — RE-DERIVED, AND ONE OF THE MANAGER'S TWO PREMISES IS WRONG

## 2.1 Is hunk (a) alone memory-safety-complete? ✅ YES — and I did not re-read it

`.temp/php22/r1h_rederive.py` is an **independent transcription** of
`mbfilter.c:1196-1256` (not `fix_scope.py`'s, not `model.py`'s — see §5.3 for
why that matters), with the guard configuration as a parameter and the
mblen_table as a parameter.

**Structural, and it is the mechanism the row owes** (`PROTOCOL_PHP.md` §F.8):
the start walk is
`n=0; start=0; for(;;){ m=mbtab[s[n]]; n+=m; if(n>from) break; start=n; }` —
it reads `s`, `mbtab` and `from`, and **never reads `length`**. Hunk (b) assigns
**only `length`**. And the start walk is where R1 leaves the buffer: once
`start > slen`, `k = start + length >= slen` and the end walk is skipped
entirely. **So no value of hunk (b) can move an out-of-bounds read.** It is not
a measurement, it is a data dependence.

**Counted anyway**, uniform sweep over `from, length ∈ [-8, slen+11]`, `slen=16`,
1 296 pairs, with 24 bytes of heap tail past the terminator so an over-read is
observable:

```
R1 (no guards)   reads past s[slen] on  396 of 1296 pairs
hunk (b) ALONE   reads past s[slen] on  396 of 1296 pairs   <- removes NONE
hunk (a) ALONE   reads past s[slen] on    0 of 1296 pairs   <- removes ALL
hunk (a)+(b)     reads past s[slen] on    0 of 1296 pairs
```

`fix_scope.py` Q1's *"hunk (b) removes none of the 15 333"* is **upheld from an
independent implementation**, and it is now upheld with a *mechanism* rather than
a count.

## 2.2 ⚠⚠ THE `from == string->len` BOUNDARY — THE MANAGER'S STATED REASON IS NOT THE OPERATIVE ONE

The task file says `from == string->len` *"is safe only because
`mblen_table_utf8[0] == 1` at the terminator"*. **That is false.** Sweeping the
table's terminator entry with `from == slen`:

```
mbtab[0x00] = 0 -> NON-TERMINATING          max index read = 8  (= slen, in bounds)
mbtab[0x00] = 1 -> start=8 end=8            max index read = 8  in bounds
mbtab[0x00] = 2 -> start=8 end=8            max index read = 8  in bounds
   …  3, 4, 5, 6, 7 -> identical, in bounds
```

The read at `from == slen` is the NUL terminator, which is **inside** the zval
buffer (`emalloc(len+1)`, `kernel.h` says so). Whatever step the table gives, the
cursor then exceeds `from` and the loop breaks. **The operative premise is
`mbtab[b] >= 1` for every `b`** — and a `0` entry does not produce an over-read,
it produces **non-termination**.

⭐ **The row already has this right where it counts.** `verus.rs`'s
`lemma_mbtab_pos` proves exactly `mbtab_of(b) >= 1`, `verus.rs:163-165` calls it
*"THE TERMINATION PREMISE OF THE WHOLE ROW"*, and `spec.md`'s `required[5]` says
*"an attacker who could choose the table could put a zero in it"*. **So the
manager's premise is wrong and the artefact is right** — which is the good
direction for this to be wrong in, but it is the kind of premise that, stated in
a task file, comes back as evidence (`.memory-php/04-process.md`, rule 14's
shape).

**"Every encoding this kernel admits"** — the kernel admits exactly one
(`MBTAB` is a compile-time constant), but I answered the general question anyway.
All **eleven** `mblen_table_*` definitions in the pinned 5.0.0 `libmbfl`
(159 `.c`/`.h` files, comments stripped — a naive number scan reads the
`/* 0x80 */` index markers as entries and reports 258):

```
big5 uhc euccn eucjp euckr euctw sjis utf8 sjis cp936 eucjp
  every one: n=256, min=1, max in {2,3,4,6}, table[0]=1
  tables violating "256 entries and every entry >= 1": 0
```

**So the fixture's encoding is not special in either direction**, and the
`>= 1` premise the proof needs holds for every encoding `mbfl_strcut` could be
called with in 5.0.0.

## 2.3 Is `controls/bug49354.py` a faithful replay? ✅ YES — verified against the patch's own blob hash

Delegated fact-gathering, re-checked by me.

* **The phpt is authentic.** Reconstructed from `controls/c2471b495009.patch`:
  642 bytes / 21 lines (matching the patch's `@@ -0,0 +1,21 @@`), git blob sha1
  `c25b405d82032f8184a4fdf93370c008242b554c` — **which is the patch's own
  `index 000000000000..c25b405d8203`**. It is upstream's text, not a paraphrase.
* **Six cases, and six is right**: `var_dump(` ×6, `mb_strcut(` ×6, six non-empty
  `--EXPECT--` lines, `len(CASES) == 6`.
* **All six args and all six expected strings are byte-identical** to
  `bug49354.py:58-65`, compared as raw bytes. Every declared `string(N)` matches
  its own literal's byte count (12/11/11/9/0).
* **Encoding: `'UTF-8'`, passed explicitly as the 4th argument on all six calls**;
  no `mb_internal_encoding` anywhere. `bug49354.py`'s `MBTAB` is **byte-identical
  to `c/kernel.c`'s `mblen_table_utf8[]` literal, all 256 entries**. No mismatch.
* **`$crap` = `41 c3 a5 42 c3 a4 43 c3 b6 44 c3 bc`**, 12 bytes; `CRAP` is the
  same 12 bytes, and `main()` appends the zval terminator.
* **It re-implements the walk in Python and builds nothing** — so the model was
  checked against the row's **real C**, three configurations × six cases:
  **18 of 18 cells agree**, `R1h_ab` wrong on case 3 only, `R1` wrong on case 6
  only, `R1h` right on all six. ASan on R1 case 6 reports
  `heap-buffer-overflow … READ of size 1 … c/kernel.c:171 … 0 bytes after
  21-byte region`, i.e. the `<<OUT-OF-BOUNDS READ>>` the Python prints is the
  real over-read at the real line, on upstream's own test input.
* **The report's §5.1 table is supported exactly**; it is a two-row excerpt of a
  six-row table and reads as one.

⚠ **One must-fire gap (minor, and it is a LABEL overclaim, not a false pass).**
`bug49354.py:151`'s third assertion is `fails["R1"] > 0` — it tests only that R1
*disagrees with upstream*, while `:157` prints *"MUST FIRE R1 over-reads on case
6 (CRASH-124) ok"*. Four of five mutants are caught (rc=1); the fifth — replace
the OOB detection with `return b""` — still exits **0** while printing that line.
Repair is one assertion: require `render(...) == '<<OUT-OF-BOUNDS READ>>'` for
R1/case 6 specifically. ⚠ **Softer gap:** the control never reads
`c2471b495009.patch`; its six `CASES` are hardcoded, so it cannot notice its own
transcription drifting from the patch it claims to replay.

## 2.4 Is the corpus really unrestricted? ✅ YES — read from the `.bin` files, not from `gen.py`

```
small.bin  windows=32    hunk(a) FIRES on 0 | from+length>slen on   6 (18.8%) | hunk(b) would MOVE the answer on   4 (12.5%)
large.bin  windows=2050  hunk(a) FIRES on 0 | from+length>slen on 410 (20.0%) | hunk(b) would MOVE the answer on 297 (14.5%)
```

Computed by my own transcription against the shipped blobs; **it reproduces
`inputs/gen.py::_check_span`'s own printed counts exactly** (`6`/`4` and
`410`/`297`) without using `gen.py`. Hunk (a) fires on **zero** windows, which is
what "benign" has to mean.

**No residue of the hunk-(b) restriction survives.** The `min(…, slen - frm)`
clamp is gone from `window()` (`gen.py:210-212` documents the deletion and the
measurement that preceded it); the only surviving mention of hunk (b) is
`_cut(win, hunk_b)`'s **parameter**, which exists so `_check_span` can assert the
region is *present*. That is the inverse of the old restriction, which is right.

---

# §3 THE NUMBERS — RE-DERIVED

## 3.1 The ladder: **every published figure reproduces exactly**

`.temp/php22/ladder_rederive.py` recomputes the whole table from
`results-php/ph07-strcut-cursor.json` alone (`kernel_exclusive_ir`, `n_iters` and
the strides parsed out of the record's own `model` lines):

```
cell           Ir/call sm   Ir/call lg    Ir/win byte   fixed/call      vs R4   published
c-gcc              2482.4      17023.0         4.1297        198.7     28.72%   (4.1297, 198.7, 28.72) OK
c-gcc-h            2485.2      17026.1         4.1298        201.4     28.72%   (4.1298, 201.4, 28.72) OK
c-clang            2078.5      13862.3         3.3467        227.7      4.32%   (3.3467, 227.7, 4.32)  OK
c-clang-h          2084.7      13868.4         3.3467        233.9      4.31%   (3.3467, 233.9, 4.31)  OK
safe_naive         2966.3      21014.3         5.1258        131.7     59.77%   (5.1258, 131.7, 59.77) OK
safe_tuned         2061.3      14711.1         3.5926         74.6     11.98%   (3.5926, 74.6, 11.98)  OK
unsafe             1850.5      13146.8         3.2083         76.3      0.00%   OK
verus              1850.5      13146.8         3.2083         76.3      0.00%   OK
every published figure reproduced from the record: YES
```

Stage 2's own inputs agree too: across every O3/isolated cell,
`small.bin` has **1** distinct checksum and `large.bin` **1**.

⚠ **`R4 ≡ R5 byte-identical` needs its qualifier, and F47 dropped it.**

```
O0  isolated   md5_fn DIFFER   md5_fn_norel DIFFER
O0  whole      md5_fn DIFFER   md5_fn_norel DIFFER
O3  isolated   md5_fn DIFFER   md5_fn_norel SAME     <- the only cell where it holds
O3  whole      md5_fn DIFFER   md5_fn_norel DIFFER
```

✅ **`spec.md`'s `identity` entry states this correctly** (`O3: "norel"`, and its
`why` opens *"R4 == R5 at O3 UP TO RELOCATIONS, and `norel` is the honest level
rather than `exact`"*), and ✅ **the report's proposed `.memory-php/02-ladder.md`
text also says "up to relocations".** It is **F47's summary line** — *"R4 ≡ R5
byte-identical"* — and the commit message that drop it. ⚠ `.memory-php/`'s `ph03`
entry says *"BYTE-IDENTICAL … `md5_fn 33850579` on both"*, which is the stronger
`exact` level; landing `ph07` beside it as *"n = 2 on the php side"* without the
qualifier would put two different strengths of evidence under one sentence.

## 3.2 `controls/spellings.py` as a TEMPLATE

**It computes the right statistic.** Full run (~2.5 min, 18 callgrind runs) is
feasible and reproduces stage 3 exactly:

```
safe_tuned  small.bin  record= 2061.3435 here= 2061.3435  delta=0.000%
safe_tuned  large.bin  record=14711.0554 here=14711.0554  delta=0.000%
unsafe      small.bin  record= 1850.4543 here= 1850.4543  delta=0.000%
unsafe      large.bin  record=13146.7822 here=13146.7822  delta=0.000%
```

and the regenerated sidecar is **field-for-field identical to the committed one
except `measured_utc`** — all 13 per-variant fields across all 9 variants. The
control is bit-deterministic. All six `derived_from_sha256` pins **resolve and
match**. ⭐ It **pins itself**, which `check.py:9436` says no sidecar did.

⚠⚠ **But it RE-IMPLEMENTS `measure.py`'s statistic rather than importing it, and
the two are not the same function.** `spellings.py:348-369 kernel_ir` vs
`measure.py:357-372 _sum_rows`:

| | `measure.py` | `spellings.py` |
|---|---|---|
| annotate rows | **sums all** matching | takes the **first**, `break`s |
| matcher | regex on the *function field*, `(?:^\|::)kernel(?:$\|[^A-Za-z0-9_])` | `":kernel" in ln` substring on the **whole line** |
| callgrind rc | checked → `{"error": …}` | **not checked** |
| annotate text | `stdout + stderr` | `stdout` only |
| records | also `kernel_functions` (what matched) | nothing |

On `ph07` they agree to the digit. On two synthetic shapes they do not, and both
produce a **plausible wrong number rather than an error**: a function split
across two annotate rows (16 000 000 → 10 000 000), and a sibling symbol named
`kernel_prologue` (9 100 000 → 900 000). ⚠ The first is not hypothetical —
`measure.py:358-359`'s docstring exists to warn about it in terms:
*"callgrind_annotate splits one function across several `file:function` rows, so
the rows must be added up rather than the first one taken."* `spellings.py:365`
takes the first one and `break`s. Verified by me: `spellings.py` never imports
`measure.py` (its only `spec_from_file_location` is `check.py`, at `:289`). **For the first control every later php row will clone,
that is the wrong side of the trade.** The build flags currently match
`build.py` exactly — also by transcription, not by import.

⚠ **Five more things a careless clone inherits silently** (measured, not
guessed):

1. **`PROBES`' `n_iters` cancels out of the record check.** Stage 3 divides
   *both* the record's raw `kernel_exclusive_ir` and its own measurement by the
   same hardcoded constant, so a stale `n_iters` prints `delta=0.000%` while
   every absolute figure is wrong: `PROBES` stale by 2× gives
   `record=1030.6717 here=1030.6717 delta=0.000%` where the truth is `2061.3435`.
   A **non-uniform** stale value moves the headline too (`+12.05 %` vs `+11.98 %`).
   `n_iters` is never read from the `.bin` header or from the record.
2. **`PROBES`' strides (553 / 4074) are hand-transcribed magic numbers.** The
   headline % is algebraically stride-invariant, so a swapped pair prints
   `R3 -3.5926 Ir/window byte` **beside a correct `+11.98 %`**.
3. **A non-`v0_shipped` build failure appends no `problem`** (`:468-471`), so the
   variant silently leaves the search and `check.py` stage 9b reads the sidecar
   as clean.
4. **`TIE_PCT` is applied to the R4 side only.** `:587`'s
   `best = min(cands, key=ir_per_window_byte)` — the number that actually ships
   as *cheapest-found* — has no tie threshold. Invisible on `ph07` (margin 10 %).
5. **Without `--verus`, every R4 variant keeps `in_contract: True`** and nothing
   records that the stage was skipped; `r4_nozero`, the one that does *not*
   verify, would then count as admissible.

Also: `materialise`'s `#[path]` absolutisation is the one substitution in the
file with **no hit-count assertion**, and `.temp/common` exists on this box as a
symlink to `common/`, so a no-op replace still compiles and still yields
plausible numbers — `p42`'s `TASK_109` m1 bug, verbatim.

⭐ **Against the four PAT precedents, `ph07`'s is the only one that had to fix the
statistic**: `p13`, `p34`, `p42` and `p49` all use the 100-vs-200 *marginal* on
whole-program totals, where the environment block cancels in the difference;
`ph07` quotes an **absolute** kernel-exclusive figure beside the row's headline,
so nothing cancels. ⚠ Conversely `p34` prices O0 **and** O3, `p49` prices both
compilers and ships a static column beside every Ir figure; **`ph07`'s ships
neither a static nor a wall column.**

## 3.3 ⚠⚠⚠ I ATTACKED THE R4 SIDE. **THE DEGENERATE CLAIM SURVIVES — WITH THREE MORE SPELLINGS AND WITH THE METRIC OBJECTION ANSWERED**

`.temp/php22/r4attack/attack.py` reuses `spellings.py`'s own machinery
(`materialise` / `build` / `run` / `kernel_ir` / `audit`) so the numbers come out
of the row's pipeline, and adds a **whole-program** Ir column beside the
kernel-exclusive one — because the row's own `r4_nozero` note shows that
`memset`/`memcpy` work escapes `kernel_exclusive_ir`, so "degenerate" could have
been an artefact of the metric.

```
variant        kIr/call sm kIr/call lg   kIr/win-B   wIr/win-B  vs R4ship  contract  checksums
v0_shipped          1850.5     13146.8      3.2083      3.3757   +0.000%   forb=none  SAME
r4_copyslice        1851.1     13147.5      3.2083      3.3762   +0.001%   forb=none  SAME
r4_foldfroms        1861.6     13157.6      3.2082      3.3761   -0.003%   forb=none  SAME
r4_ptrwalk          1885.9     13404.3      3.2713      3.4387   +1.965%   forb=none  SAME
```

* **`r4_copyslice`** — the byte copy loop replaced by `copy_from_slice`. ⚠ Chosen
  because the pinned vstd **does** ship a spec for it
  (`~/tools/verus/vstd/std_specs/slice.rs:205`,
  `assume_specification<T: Copy>[ <[T]>::copy_from_slice ]`), so unlike
  `r4_nozero` a twin is plausible. **+0.001 % — a tie**, and the whole-program
  column moves by +0.0005 too, so the `memcpy` is not hiding a win.
* **`r4_foldfroms`** — fold from `s` instead of re-reading `out`. **−0.003 %, a
  tie by the row's own `TIE_PCT`.**
* **`r4_ptrwalk`** — both walks on a raw pointer cursor, which is what the C
  does (`p += m`). **+1.965 % WORSE.**

⭐ **So the row's *"the R4 endpoint is degenerate"* now stands on SEVEN spellings
from two independent agents, not four from one — and the whole-program column
answers the objection that the endpoint only looks degenerate because
`kernel_exclusive_ir` throws the bulk operations away.** The cost on this row is
in the walks, and nothing I tried made the walks cheaper.
`+11.98 %` is a bound over a searched endpoint. **This is the strongest single
claim in the rebuild and I could not move it.**

⚠ **One correction to `r4_nozero`'s stated reason.** The docstring says *"the
pinned vstd has no spec that makes that sound"*. Verus's own error **names one**:
`help: The following declaration may resolve this error: pub assume_specification<T, A> [std::vec::Vec::<T, A>::set_len]`. The obstacle is an
un-assumed `assume_specification`, not an absence — `CLAUDE.md`'s twice-burned
*"grep `std_specs/` before claiming no spec exists"* hazard in mild form. ✅ **It
changes nothing about the bound**: `r4_nozero` measures identically to the
shipped R4 (3.2083), so even if admitted it is a tie.

## 3.4 `r4_index0`: ✅ **the disassembly claim is TRUE, checked independently**

```
$ python3 harness/asm.py diff .temp/php22/r4attack/idx_v0_shipped.bin \
                             .temp/php22/r4attack/idx_r4_index0.bin --sym kernel
identical by raw machine-code bytes      : True
identical with pc-rel fields masked      : True
(normalised text identical)
```

Both binaries: `n_raw 258`, `n_nopad 247` — the shipped record's own numbers.
`get_unchecked(s, …)` sites in `verus.rs` go **4 → 3** (`:537` is the one that
goes; `:552`, `:602`, `:633` remain). So the claim is exact.

⚠ **But it is a smaller trusted SURFACE, not a smaller trusted BASE, and F47
says "STRICTLY BETTER ON THE TRUSTED SIDE" without saying which.** The four
`external_body` items are unchanged, `NOTES.md`'s TCB tally does not move, and
`get_unchecked` is still needed for the other three reads. **What falls is the
number of unchecked reads the axiom licenses, from 4 to 3.** ⭐ It is still a
genuinely different axis from the bench rule's — *fewer uses of a trusted item at
identical cost* — and the report's own §2b wording (*"removes one of
`get_unchecked`'s four call sites"*) is precise where the handoff's is not.

## 3.5 F41(c): ✅ **the replacement argument stands on its own**

Re-derived from the record:

```
gcc    delta small=+2.8164  delta large=+3.0734  ratio=1.091   (a RATE would give 7.37)
       marginal R1=4.129695  R1h=4.129768  residual=+7.30e-05  (0.00177% of the rate)
clang  delta small=+6.1863  delta large=+6.1046  ratio=0.987   (a RATE would give 7.37)
       marginal R1=3.346722  R1h=3.346698  residual=-2.32e-05  (-0.00069% of the rate)
```

A rate would multiply the delta by **7.37** across the two window sizes; it
multiplies by **1.09** and **0.99**. The argument needs no rounding boundary and
does not depend on the two compilers agreeing, which is exactly what the retired
§5c cross-check did depend on. **The retraction is correct and the replacement is
sound.**

**Does anything else still lean on the vanished agreement?** Grepped the row's
`.md`, `.rs` and `controls/*.py` for `5c`, `3.504e`, `3.518e`, *"three
significant figures"*, *"decomposition artefact"*. ✅ **The only surviving hits
are inside `NOTES.md`'s own retraction (`:729-738`)**, where they belong. The
other `5c` hits are `check.py`'s unrelated stage names (`5c-twin`). **Nothing
else leans on it.**

---

# §4 THE SCHEMA AND THE SPANS

## 4.1 `ph03` and `ph00-smoke` really ARE byte-identical ✅

Reconstructed the pre-change validator (`git show HEAD:harness-php/provenance.py`,
sha `2cc5dd09b2bcd007`; the working tree's is `c3344872e91bf840`), loaded both as
modules with `PATTERNS`/`MANIFEST` rebound, and ran `check_row` over all three
rows under both:

```
=== ph00-smoke             old_ok=True new_ok=True  BYTE-IDENTICAL OUTPUT
=== ph03-uudecode-bound    old_ok=True new_ok=True  BYTE-IDENTICAL OUTPUT
=== ph07-strcut-cursor     old_ok=True new_ok=True  *** OUTPUT DIFFERS ***
    - ...mbfilter.c is in the manifest (da3f5f9ef501)
    + ...mbfilter.c, mbfilter_utf8.c, mbstring.c are in the manifest (da3f5f9ef501, f8918fb92bec, 9d0bbd06beac)
    - kernel overlap 75% (39/52 ...)
    + OK+1 .../filters/mbfilter_utf8.c:39-56   852 bytes  sha256 716ba3fb219d4fb4
    + OK+2 ext/mbstring/mbstring.c:1774-1812   845 bytes  sha256 4ef738b3546c31c1
    + per-span overlap: span0 75% (39/52), span1 100% (5/5), span2 15% (3/20)
    + kernel overlap 61% (46/76 ...)
```

Cross-checked a second way, in mirrored scratch trees through the full CLI
(stdout **and** stderr, plus `--selftest`): `ph00-smoke` and
`ph03-uudecode-bound` identical, exit 0 both.

⚠ **ONE QUALIFIER, and the report's unqualified "byte-identical" does not carry
it.** Under **`--no-tarball`** `ph03` differs by one line (`provenance.py:794-796`):

```
old:  ⚠ --no-tarball: extract_sha256 was NOT verified. This is a PARTIAL check.
new:  ⚠ --no-tarball: extract_sha256 was NOT verified for any of 1 span(s). ...
```

Cosmetic, no exit code and no verdict moves, and `ph00-smoke` is identical even
there (it returns before that line). **But "byte-identical" is true of the
default invocation only**, and `--no-tarball` is a spelling `PROTOCOL_PHP.md` §D
documents and expects agents to use.

**The additive design cost essentially the churn it claimed: one row, plus one
line of a flag-gated message on a second.** And ph07's
published per-span and union numbers reproduce **exactly** — `75 % (39/52)`,
`100 % (5/5)`, `15 % (3/20)`, union `61 % (46/76)`.

## 4.2 Is an extra span validated as strictly as the primary? ✅ **YES — and I built the negatives**

Reading `harness-php/provenance.py:745-830` first: the code builds
`spans = [primary] + extra_spans` and then runs **one loop** for the `c_lines`
shape and the canonical `extract_cmd`, **one loop** for manifest membership, and
**one loop** for `excerpt()` + `extract_sha256`. Every failure is
`return False, [...]`, i.e. a refusal, not a warning — and `excerpt()`
(`:199-236`) is the same function, so the start-past-EOF, run-past-EOF and
whitespace-only refusals apply identically. **An extra span gets one check the
primary does NOT: a non-empty `why` is mandatory** (`:759-762`).

⚠ **Reading it is not enough. `.temp/php22/spansmf/mustfire.py` builds a scratch
row — symlinks to the real `ph07` with only `spec.md` replaced by a mutated copy
— and calls `check_row` on it directly, so nothing in the repo moves.** Every
mutation is applied to `extra_spans[1]`, the caller frame:

```
mutation                                   expect   got
CONTROL  unmutated                         PASS     PASS
wrong extract_sha256                       REFUSE   REFUSE   EXTRACT MISMATCH for span 2
c_lines transposed [1812,1774]             REFUSE   REFUSE   span 2: bad span 1812,1774
c_lines start past EOF                     REFUSE   REFUSE   starts past the end of ...
c_lines run past EOF                       REFUSE   REFUSE   runs past the end of ...
c_file not in the manifest                 REFUSE   REFUSE   is not in php-5.0.0.manifest
extract_cmd does not describe the span     REFUSE   REFUSE   extract_cmd does not describe
`why` removed (extra-span-only check)      REFUSE   REFUSE   extra_spans[1] has no `why`
a span field removed                       REFUSE   REFUSE   missing ['extract_sha256']
extra_spans is not a list                  REFUSE   REFUSE   must be a list of span objects
BASELINE  primary span's sha256 corrupted  REFUSE   REFUSE   EXTRACT MISMATCH for span 0

11 of 11 controls behaved as declared; 0 did not.
```

**Claim (ii) holds, with negatives.** ⭐ And because `provenance.py` is a
preflight stage that exits 2 without running the tool, **an extra span is a real,
enforced obligation**: adding one adds something the row must keep true. That is
the direction the code's own comment claims (*"adding a span cannot make the
number go up for free"*), and it is the opposite of the `tier`/`uses_allocator`
class of unvalidated declarations.

⚠ **What is NOT enforced, and it matters for §4.3:** no key outside
`provenance.py` reads `extra_spans` (grepped `harness-php/`, `common-php/`,
`model.py`, `inputs/gen.py`), and the overlap it feeds is **reported, never
enforced** (`_OVERLAP_FLOOR` is consulted only to print an expectation). So the
**spans** are pinned and their **fidelity** is not. ✅ It is inside the hashed
`slb-contract` fence (spec.md line 373, fence 32-479; `check.py::read_contract`
hashes the raw block and yields exactly the `1f1508531bd4…` the gate record
carries), so it cannot be quietly withdrawn — and
`gate.py:1243-1251` runs `provenance.py` as preflight stage 7, gates on its exit
code, and writes `provenance_stdout` into the **committed** preflight record,
which already carries the `OK+1`/`OK+2` and per-span lines verbatim.

⚠ **One pre-existing hole the audit surfaced:** a row declaring
`"php_provenance": false` short-circuits at `provenance.py:723-734`, so a wholly
bogus `extra_spans` entry (bad sha, file not in the manifest, span
`[999999, 1]`) passes with exit 0. The primary's own fields are equally
unchecked on that arm, so it is not an `extra_spans` regression — but
`ph00-smoke` is the only row that arm is for, and it should stay that way.


## 4.3 ⚠ IS `ph07`'s DECLARED TIER NOW WRONG? — **No, but the row now over-claims in a NEW place**

`tier` is `narrowed`, and per `PROTOCOL_PHP.md` §A1 it is *a COST STATEMENT,
NEVER A FILTER* — so nothing can be killed by this and no verdict moves. My
reading:

* The tier governs the **kernel's mechanism**, which is span 0
  (`mbfilter.c:1179-1259`, 75 %): a wrapper comes off, the body is unchanged.
  `narrowed` is the right word for that and it is still right.
* Span 1 (the 256-byte table, 100 %) is a `verbatim` lift, which is *stronger*
  than the declared tier and therefore not a defect.
* Span 2 (`mbstring.c:1774-1812`, **15 %**) is the problem, and it is not the
  tier. **The row now PINS a span with an `extract_sha256` for text it
  re-expresses.** Its own `why` says the kernel wrapper *"IS this code"*, and
  `TASK_PHP_017` §3 verified that semantically — but three lines match, and a
  reader who sees a pinned span with a tarball hash reasonably reads "lifted".
* ⭐ **The engineer's own finding is the right one and I would not extend
  `tier`**: a single word is the wrong shape for a three-span row, and a
  per-span `tier` is a second schema change on n = 1. **What the row owes is one
  sentence, not a schema**: `extra_spans[1].why` should say in terms that the
  span is cited as the **provenance of the guard's position and of the wrapper's
  semantics**, and that its text is re-expressed rather than lifted — which is
  what the 15 % measures. That is a `spec.md` prose-inside-the-fence edit, i.e.
  a `contract_sha256` move, so it should be batched with §6's other owed fixes
  and not taken alone.

---

# §5 THE MANAGER'S THREE UNCERTAINTIES

## 5.1 ⚠⚠⚠ *"That I was right to accept §4.1's refusal."* — **YOU WERE HALF RIGHT, AND THE HALF YOU GOT WRONG IS THE ONE YOU ASKED ABOUT**

**Holding 4.1-B was right. Landing 4.1-A as an *observation* is not, because
4.1-A is a norm.** Reading its own text:

1. **Its head clause is a deontic permission, in capitals, first:**
   > *"⚠⚠ **AND A ROW MAY SHIP A SUBSET OF ITS `fix_commit`, IF IT SAYS SO AND
   > SAYS WHY.**"*

   `MAY … IF …` is a conditional permission. Everything after it —
   *"This is a WORKED EXAMPLE, not yet a general permission"* — **qualifies a
   permission that the preceding sentence has already granted.**
2. **It carries a requirement schedule for future rows:** *"A row that wants to
   do the same **owes** … all four of (i)…(iv)"*, with *"(iii) IS THE
   LOAD-BEARING ONE"*. **An observation does not tell future rows what they
   owe.** That sentence is the definition of a norm.
3. **It goes into `PROTOCOL_PHP.md` §C**, a document whose contents are read as
   rules by every subsequent builder, immediately under the sentence that
   *defines* R1h.
4. **The difference between 4.1-A and 4.1-B is placement, not substance.**
   4.1-B puts the permission in §C's first sentence; 4.1-A appends it as a note
   under that sentence. **Both grant it. Both attach the same four disclosures.
   Both make (iii) mandatory.** The only thing 4.1-B adds is the *phrase*
   "tagged upstream configuration" in the definition — and 4.1-A already licenses
   the substance that phrase names.

⚠ **So yes: landing 4.1-A commits us to 4.1-B in practice.** The next engineer
whose R1h trips stage 7h opens §C, finds *"A ROW MAY SHIP A SUBSET OF ITS
`fix_commit`"*, writes the four disclosures, and cites protocol. **That is
precisely the failure mode (a) named** — *"instead of choosing the corpus to fit
the fix, choose the fix to fit the corpus"* — and (iii) does not close it,
because (iii) is satisfiable by *any* later upstream change to the function, and
the whole of `UPSTREAM_002` §1 is a demonstration that this function's guard set
moves across many tags.

⚠⚠ **And the engineer's own argument for holding refutes landing.** §4.1 says
*"holding it costs `ph07` nothing, because the row does not need the protocol to
change in order to ship"*. **By exactly that argument, landing 4.1-A buys nothing
either** — the row already ships, `idiom.required[4]` already discloses
everything. The only function 4.1-A performs is to tell *future* rows what they
may do. That is the thing the programme just decided it did not have the evidence
for.

⭐ **What I would land instead — the same content, with the verbs changed.**
Keep every fact; delete every deontic. Past tense, descriptive, no owed-list:

> ⚠ **`ph07`'s R1h is a SUBSET of its `fix_commit`, and here is the whole of
> why.** `cb3cca21b345` (2005) added two guards. Hunk (a) closes the
> memory-safety defect — it removes all 15 333 out-of-bounds reads and changes no
> benign answer. Hunk (b) removes **none** of them and changes the answer on
> **13.5 %** of benign calls, and `c2471b495009` (2009-09-23) **deleted it as bug
> #49354, with a regression test** that `controls/bug49354.py` replays: hunk (a)
> alone agrees with upstream on all six cases, and the two-hunk fix does not.
> So R1h is the configuration `php-5.2.12 … php-5.2.17` shipped and kept,
> `PHP_FUNCTION(mb_strcut)` body sha256 `26e2099e33433c74`. The row states that,
> with both commits cited, both patches under `controls/`, what each hunk buys
> measured separately, and the alternative it was chosen against, **inside its
> hashed `spec.md` block** (`idiom.required[4]`). ⭐ `check.py` stage 7h refused
> the two-hunk version in the first hour the row existed and **stage 7h was
> right**.
>
> ⚠⚠ **WHETHER THIS GENERALISES IS OPEN. n = 1, AND NOTHING HERE PERMITS A
> SECOND ROW ANYTHING.** A row that wants to do the same brings it to the
> manager as a proposal; the shape `ph07`'s took is above, and the question to
> ask about a second one is whether an **upstream artefact** decides it (a later
> removal, a regression test, a bug number) rather than the row's convenience —
> because without that, *"cite a tagged configuration"* lets an engineer scan
> tags until one suits.

That preserves (i)–(iv) as *description of what ph07 did* and as *the question to
ask next time*, and it grants nothing. ⚠ **The cost of getting this wrong is
asymmetric**: an under-stated observation costs one task when a second row needs
it; an over-stated norm is, on this project's own record (`.memory-php/04-process.md`
failure 1, `RECAP_PHP.md` open item 24), what has to be un-landed.

## 5.2 *"That rebuilding row 2 was worth it at all."* — **IT WAS. And the evidence that decided it is still not the manager's.**

**For**, all independently re-derived here:

* The shipped R1h **failed upstream's own regression test** on the case that *is*
  bug #49354 — and the phpt is authenticated against the patch's own blob hash,
  and the model is checked against the row's real C, 18/18 cells (§2.3).
* Hunk (b) removes **0 of 396** over-reads in an independent sweep, and cannot,
  for a data-dependence reason (§2.1).
* The corpus restriction excluded **18.8 % / 20.0 %** of the benign domain; it is
  gone, and the region is now asserted *present* (§2.4).
* The counterfactual — land `TASK_PHP_017`'s guard clause and keep the old R1h —
  would have kept a rung PHP itself files as a bug, kept the corpus restriction,
  **and landed a protocol rule invented for one row in the same session the
  programme refused a different rule for exactly that reason.**

**Against:** one task; every number moved; a cross-check retired; **and §1 shows
the rebuild's advertised best result is weaker than advertised** — the headline
is true but *"only a value postcondition could have noticed"* is not, so the
accidental payoff is smaller than F47 prices it at.

⚠⚠ **The sharp point, and it is about `UPSTREAM_002` rather than about the
rebuild: `UPSTREAM_002` alone did not justify it.** Its §1 tag sweep and §2
removal commit establish that upstream **withdrew** hunk (b). They do not
establish that hunk (b) is **wrong**. The step from *withdrawn* to *wrong* is
`bug49354.phpt`, and that is the engineer's contribution, not the manager's —
which is exactly what the engineer said and exactly why §5.1 of `TASK_PHP_018`
was a well-placed uncertainty. ⭐ **The manager offered a stopping point on
archaeology and it was declined on a behavioural test. That is the loop working.**

## 5.3 *"That `bug49354.py` and `fix_scope.py` do not share an assumption."* — ⚠ **THEY SHARE A MODEL, BY COPY, AND `bug49354.py`'s DOCSTRING SAYS THEY DO NOT**

`bug49354.py:25-28` claims it is *"deliberately a FIFTH spelling of the kernel,
**sharing no code with** `../model.py`, `../inputs/gen.py::_cut`, `fix_scope.py`
or any rung, so an agreement here is an independent one"*. **False as written:**

* **`MBTAB` is byte-identical across four files** — `bug49354.py:51-53`,
  `fix_scope.py:55-57`, `model.py:91-93`, `inputs/gen.py:113-114`, trailing
  `assert` included, 0 differing lines.
* **The caller clamps are byte-identical** — `bug49354.py:77-84` vs
  `fix_scope.py:64-71`, differing only by two trailing comments.
* **The end walk and the three clamp lines are byte-identical** —
  `bug49354.py:98-110` vs `fix_scope.py:119-130`, character for character.

**So they CAN agree for the same wrong reason** on the table, the clamps and the
end walk. ✅ **The risk did not materialise**, and there are now three independent
checks that say so: `model.py:576-628` re-derives all 256 table entries **from
`c/kernel.c`'s literal text** and fails the selfcheck on mismatch (`bug49354.py`
only asserts `len == 256`); the real-C differential agrees 18/18; and my own
transcription (§2.1, §2.4) reproduces `fix_scope.py` Q1's conclusion and
`gen.py`'s window counts without sharing a line with either. **The conclusion is
safe. The docstring is a false disclosure and should be corrected to say what is
true — that it shares the table and the clamps and differs in the walk and the
oracle.** ⚠ A false disclosure is worse than the thing it describes, because it
is what a reviewer trusts *instead of* re-checking (`PROTOCOL.md` DoD rule 6).

---

# §6 FINDINGS NOT ASKED FOR

## M1 (major) — `spec.md`'s HASHED `identity[0].why` carries FOUR figures the rebuild refuted

`patterns-php/ph07-strcut-cursor/spec.md`, inside the `slb-contract` fence:

> *"Measured, `results-php/ph07-strcut-cursor.json`, O3/isolated: **255
> instructions** and 953 bytes in BOTH cells, `md5_fn_norel` identical at
> **`702235d5f057…`**, and `md5_fn` DIFFERENT (**`b20b2fd9aa42e532`** vs
> **`b3ecc80e00209841`**)."*

Against the record it cites, **post-rebuild**:

| the hashed `why` says | `results-php/ph07-strcut-cursor.json` says |
|---|---|
| 255 instructions | **251** (`n_fn`; `n_nopad` 247, `n_raw` 258) |
| `md5_fn_norel` `702235d5f057…` | **`cc8d629987e1196f…`** |
| `md5_fn` `b20b2fd9aa42e532` | **`909a1a4db15d5bb8…`** |
| `md5_fn` `b3ecc80e00209841` | **`f6fec880e0ec2b0f…`** |

All four are the **pre-rebuild** record's values (`git show HEAD:` gives exactly
255 / `702235d5f0577f57` / `b20b2fd9aa42e532` / `b3ecc80e00209841`), and
`git diff` confirms the `identity` entry **was not touched by the rebuild**.

**Failure scenario, and it is the concrete one:** the entry's whole purpose is to
justify why the identity level is `norel` and not `exact`. A reader who does what
it invites — open the record and check — finds four mismatches and has no way to
tell whether the *level* is wrong too. (It is not: `md5_fn_norel` is still
identical and `md5_fn` still differs, so `norel` remains correct and the **gate
verdict is unaffected**.)

⚠⚠ **This is `PROTOCOL.md` rule 6's documented hole — p46's case — reproduced on
the first php row to be rebuilt.** *"A frozen declaration is evidence about WHEN
it was written, not about whether it is still true."* And the hash still matches,
which is why nothing caught it.

⚠⚠⚠ **And `NOTES.md:201-203` claims the addendum was applied:** *"per rule 6's
addendum: the hashed `idiom.why` and every rung-source doc comment were re-read
against the measured numbers in §8 before this row was finished."* **`idiom.why`
was** — I scanned it and it carries no stale ladder figure. **`identity[0].why`
is also hashed, also carries measured numbers, and was not.** The disclosure is
narrower than the rule and does not say so.

## M2 (major) — `c/kernel.h:20-25` names the WRONG upstream fix, and it is in `source_sha256`

```c
 *   c/kernel_hardened.c   R1h -- the same file plus the prologue hunk of the
 *                                real upstream fix
 *                                d9dda48f8a7e182ed8c0f56e5fde9e367131a07a
 *                                (Moriyoshi Koizumi, 2010-03-12), and nothing
 *                                else.
```

What `kernel_hardened.c:348-349` actually ships is
`if (from > str_len) { return 0xFFFFFFFFu ^ php_shim_tally(); }` — **`cb3cca21b345`
hunk (a)**, `php-5.2.12 … php-5.2.17`, and the file's own header says so at
`:10` and `:81`.

⚠ **These are different programs, and `spec.md` says so itself.**
`idiom.forbidden[2]` pins the 2010 clamp **ABSENT** precisely because
*"`cb3cca21b345` returns FALSE where the clamp returns a cut"*. So `kernel.h`
describes R1h as the very thing the contract forbids the Rust rungs from being.

`c/kernel.h` is in the measurement record's `source_sha256` and **was not touched
by the rebuild** (`git diff --stat HEAD -- c/` lists only `kernel.c` and
`kernel_hardened.c`). It has been wrong since the row was built — so it survived
`TASK_PHP_016` and `TASK_PHP_017` as well — and it is a **rung-source doc
comment**, i.e. exactly what `NOTES.md:201-203` says was re-read.

**Failure scenario:** an agent reading `c/` to answer *"what is this row's R1h?"*
gets the 2010 clamp, which is a different function; the row's `fix_scope.py`
measures it separately as `R1_2010` and it moves **5 717** answers.

## m3 (minor) — `NOTES.md`'s rule-6 fence disclosure undercounts, 4 named against 27 moved

`NOTES.md:179-185`: *"⚠ **Four edits inside the fence, every one of them forced
by §00**: `idiom.required[4]`, a new `idiom.forbidden[3]`,
`provenance.extra_spans`, and `provenance.fix_commit_removal` /
`r1h_configuration`."*

Diffing the parsed contract block HEAD → worktree: **27 leaf values moved, across
10 top-level keys.** Six of them are named nowhere in the disclosure:

```
.idiom.why                      .provenance.divergences[6].why
.provenance.extra_spans_note    .provenance.divergences[8].why
.provenance.fix_commit_note     .verus.twin_obligations_note
```

None is a defect in itself — `twin_obligations_note` had to move for the rlimit
finding, `idiom.why` for §00 — but rule 6 exists so a reviewer can check the
scope of a declaration edit **against a statement of it**, and this statement is
narrower than the edit. ✅ Checkable here only because the row is uncommitted.

## m4 (minor) — `NOTES.md` §10d quotes a PRE-rebuild negatives log, and says so in its own last line

The §10d block is labelled `.temp/php16/13-negatives.log` and ends
`verus.rs sha256 unchanged: 28811d6d6f45c3b2` — **that is `git show HEAD:`'s
hash**. The current `verus.rs` is `d1c61785e44185f8`. ✅ **I re-ran
`controls/negatives.py` against the rebuilt row and the claim is TRUE**:

```
noguard    expect FAIL got FAIL  20 verified, 1 errors  ok
nopos      expect FAIL got FAIL  p.rs:159 compute_only  ok
notable    expect FAIL got FAIL  p.rs:159 compute_only  ok
noconsume  expect PASS got PASS  21 verified, 0 errors  ok
verus.rs sha256 unchanged: d1c61785e44185f8
```

So the substance holds and only the pasted evidence is stale. Repair is to paste
this run.

## m7 (minor) — `provenance.py:836-837`'s comment about the union overlap is measurably FALSE

The `extra_spans` code documents its own safety property:

> *"A row that cites more now has MORE to resemble, which is the direction this
> check should err in: **adding a span cannot make the number go up for free.**"*

Union overlap is `|hit| / |want|` over **deduplicated line sets**
(`_normalise` returns a `set`), so **a span whose own fraction is above the
current union fraction raises it.** Measured on `ph07` itself, by driving
`kernel_overlap` over subsets of the row's three real excerpts:

```
what the row PUBLISHES (all three spans):      61% (46/76)
pre-TASK_PHP_018 state (primary span alone):   75% (39/52)
primary + the TABLE span only (span2 removed): 77% (44/57)   <-- the comment says this cannot happen
primary + caller frame only:                   58% (41/71)
```

So starting from the pre-rebuild single-span state at **75 %** and adding the
100 % table span takes the published number **UP to 77 %**. `ph07`'s union only
lands *lower* because span 2 happens to be 15 %. ✅ **The set semantics DO defend
against the narrower attack the comment probably had in mind** — citing the same
span three extra times leaves the union at `61 % (46/76)`, measured — but the
sentence as written is a general claim and it is false.

**Failure scenario:** the next row cites a second, highly-verbatim span
(a table, a header, a macro block) alongside a narrowed primary, its published
overlap goes up, and the comment says that cannot have been free. It is exactly
the wrong reassurance to leave in a check whose number is *reported, not
enforced*, and therefore judged by a person.

## m8 (minor) — a `check.py:NNNN`-class citation went stale inside the rebuild

`harness-php/gate.py:300` cites **`provenance.py:841-843`** as the dotted-row
`glob(<row>*)` resolution. The `extra_spans` change added ~60 lines above it, so
that code is now at **`:924`**, and `:841-843` today is the middle of the
per-span overlap loop:

```
841:            f_i, w_i, h_i, _ = kernel_overlap(pdir, t)
```

⚠ **This is the pointer-rot class `PROTOCOL.md` rule 13 already has a reflex
for**, and it was *introduced* by the uncommitted change: the "zero churn"
accounting counted rows re-gated, not citations invalidated. Cheap to repair
while the change is still uncommitted.

## ~~m5 (minor / process) — the finding is committed and the row is not~~ ⚠ **WITHDRAWN: FIXED OUT FROM UNDER THE REVIEW**

**As written, mid-review:** `ad88669` ("F47: row 2 rebuilt") landed
`TASK_PHP_018_REPORT.md` and `RECAP_PHP.md` **only** — 2 files — while all 21
modified and 4 untracked files of the rebuild sat in the working tree, including
`controls/bug49354.py` and `controls/c2471b495009.patch`, the load-bearing
evidence for F47 §5.1. A published finding cited numbers that were not in
history.

⚠ **`8e2d834` committed the row while this review was running, so the finding no
longer holds and I withdraw it.** `PROTOCOL.md` rule 11 governs this exactly:
*"DO NOT FIX A FINDING OUT FROM UNDER A RUNNING REVIEW … Collect while a review
runs; fix after it reports."* The last time this happened the reviewer *"had to
withdraw a live finding and keep only its mechanism"*, which is what I am doing.

**The mechanism, which survives the fix and is the part worth keeping:** the
gap between *landing a finding* and *landing the artefact the finding is about*
is invisible to every check this programme runs. Both brackets were `66/0` and
`6/0` across the whole window, the gate record was `PASS`, and
`--check-stale` reads the **working tree**, not `HEAD` — so a tree whose
evidence is uncommitted is indistinguishable from one whose evidence is
committed. ⚠ **`git status --porcelain` before a findings commit is the check,
and it costs one command.**

## m6 (minor) — the gate hashes `controls/*.py` and never runs them

`results-php/gate/ph07-strcut-cursor.json`'s `source_sha256` carries all nine
`controls/` entries and all nine match disk. But no stage of `harness-php/gate.py`
or `harness/check.py` **executes** `controls/*.py`. So `bug49354.py`'s *content*
is pinned; its **PASS is a manual result nothing re-establishes**. Not a defect
to fix (a gate that runs controls is a `harness/` change), but worth stating
plainly next to a control the programme is now leaning on.

---

# §7 CLEAN NEGATIVES — named attacks that did NOT land

So the next agent does not re-run them.

1. **The memory-safety-only proof does not refute the headline.** I built it to
   refute it. It verifies under both configurations, identically. §1.1.
2. **Nor does the stronger reading.** An explicit no-read-past-`slen`
   postcondition also verifies under both. §1.3.
3. **The weakening is not vacuous where it matters**: both `noguard` controls
   fail at `frm <= slen`.
4. **Hunk (a) alone IS memory-safety-complete** — re-derived from an independent
   transcription, structurally and by count. §2.1.
5. **The corpus really is unrestricted** — read from the `.bin` files, matching
   `gen.py`'s own counters exactly, with no residue in `gen.py`. §2.4.
6. **Every published ladder figure reproduces from the record**, to the digit,
   including all four "vs R4" percentages and both fixed terms. §3.1.
7. **`r4_index0` really is byte-identical machine code.** §3.4.
8. **The R4 endpoint survived three more spellings** (`copy_from_slice`, fold-
   from-source, raw-pointer walk) — none cheaper than a tie, none forbidden, all
   returning the shipped checksum on all seven inputs. §3.3.
9. **"Degenerate" is not an artefact of `kernel_exclusive_ir`** — the
   whole-program column moves with it. §3.3.
10. **F41(c)'s replacement argument does not depend on the retired cross-check**,
    and nothing else in the row leans on it. §3.5.
11. **`spellings.py` is bit-deterministic** — a regenerated sidecar is
    field-for-field identical except the timestamp, and all six pins resolve and
    match.
12. **`bug49354.py` can fail**: 4 of 5 mutations exit 1. Only the OOB-label
    mutation slips through. §2.3.
13. **All four Verus negatives still behave on the rebuilt `verus.rs`.** m4.
14. **No mblen_table in 5.0.0 has a zero entry or a length other than 256** — the
    termination premise holds for every encoding, not just the fixture's. §2.2.
15. **The row's `identity` LEVEL is right** even though its `why`'s numbers are
    not: `md5_fn_norel` still matches and `md5_fn` still differs. M1.
16. **`extra_spans` validation is not weaker than the primary's** — eleven
    negatives, eleven refusals, including the extra-span-only mandatory `why`.
    §4.2.
17. **The `extra_spans` schema change really did cost one row** — `ph03` and
    `ph00-smoke` are byte-identical under the old and new validators, stdout and
    stderr, plus `--selftest`. §4.1.
18. **Citing the same span repeatedly does NOT inflate the union overlap** — the
    table span cited three extra times leaves it at `61 % (46/76)`. The set
    semantics defend against duplication; they do not support the general claim
    the comment makes. §6 m7.

---

# §8 CLOSING BRACKET

```
$ harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH  results/gate/ph00-smoke.json           29 source(s)
FRESH  results/gate/ph03-uudecode-bound.json  33 source(s)
FRESH  results/gate/ph07-strcut-cursor.json   38 source(s)
FRESH  results/ph00-smoke.json                19 source(s) + 8 input(s)
FRESH  results/ph03-uudecode-bound.json       19 source(s) + 7 input(s)
FRESH  results/ph07-strcut-cursor.json        19 source(s) + 7 input(s)
6 record(s) examined, 0 STALE
```

⚠ **`git status --porcelain` is now 2 entries, not the 26 it was mid-review** —
because `8e2d834` committed the entire rebuild, and this report with it, while
the review was running (see the box at the top). The two remaining entries are
this file (` M`, i.e. now tracked and edited past the commit) and
`?? .tasks-php/land_019_020.py`, which is not mine.

✅ **Proof that the review itself changed nothing in the row**, taken after all
four commits landed:

```
$ python3 -c "re-hash spec.md's slb-contract block with check.py's own regex"
spec.md re-hashed: 1f1508531bd41975927e07f0
gate record      : 1f1508531bd41975927e07f0
MATCH
```

---

# §9 SEVERITY SUMMARY

| | finding | where |
|---|---|---|
| **major** | the hashed `identity[0].why` carries four figures the rebuild refuted (255/`702235d5`/`b20b2fd9`/`b3ecc80e`) | §6 M1 |
| **major** | `c/kernel.h:20-25` names `d9dda48f8a7e` as R1h; the file ships `cb3cca21b345` hunk (a) | §6 M2 |
| **major** | F47's *"ONLY A VALUE POSTCONDITION COULD HAVE NOTICED"* / *"told nobody anything"* is refuted by the gate's own stage 2 | §1.4 |
| major | 4.1-A is a norm, not an observation; landing it commits us to 4.1-B | §5.1 |
| minor | `spellings.py` re-implements `measure.py`'s statistic; two shapes give a plausible wrong number | §3.2 |
| minor | `spellings.py`'s `PROBES` `n_iters` cancels out of its own record check | §3.2 |
| minor | `bug49354.py`'s "sharing no code with `fix_scope.py`" is a false disclosure | §5.3 |
| minor | `bug49354.py`'s third assertion does not test what its label claims | §2.3 |
| minor | rule-6 fence disclosure names 4 edits against 27 moved leaves | §6 m3 |
| minor | `NOTES.md` §10d quotes a pre-rebuild negatives log (claim re-verified true) | §6 m4 |
| minor | F47 drops "up to relocations" from `R4 ≡ R5`; `spec.md` and the proposed `.memory-php/` text keep it | §3.1 |
| minor | `r4_nozero`'s "no spec exists" — Verus names one | §3.3 |
| minor | `extra_spans[1]` pins a re-expressed span without saying so | §4.3 |
| minor | `provenance.py:836-837`'s *"adding a span cannot make the number go up"* is false — measured 75 % → 77 % | §6 m7 |
| minor | `gate.py:300`'s `provenance.py:841-843` citation went stale inside the change | §6 m8 |
| minor | claim (i)'s "byte-identical" holds for the default invocation only; `--no-tarball` moves one line on `ph03` | §4.1 |
| ~~process~~ | ~~the row is uncommitted while F47 is committed~~ — **WITHDRAWN, fixed mid-review**; the mechanism survives | §6 m5 |
| process | this report was committed at 1087 lines and acted on before it finished (rule 11) | top box |
| process | the gate hashes `controls/*.py` and never runs them | §6 m6 |

**Nothing here invalidates the rebuild.** The gate verdict, the ladder, the
`fixed-R4 bound`, the R1h decision and the corpus all survive. The two majors are
stale declarations, and the third is a handoff sentence that says more than the
row it came from.

---

# §10 SCRATCH, AND WHAT REGENERATES IT

`.temp/php22/` only. Generators kept; every `.rs` variant, `.bin` and callgrind
dump is derived and deleted.

| path | what it is |
|---|---|
| `msproof/gen_ms.py` | §1 — builds the memory-safety-only proofs by mechanical weakening, with the no-value-token audit |
| `msproof/gen_ms2.py` | §1.3 — the explicit no-read-past-`slen` postcondition, with the instrumentation audit |
| `msproof/RESULTS.log` | the 16-row verification matrix |
| `checksum_probe.py` / `.log` | §1.4 — does the gate's stage 2 separate the two configurations? |
| `r1h_rederive.py` | §2.1/2.2/2.4 — independent transcription of `mbfilter.c`, the terminator sweep, all 11 mblen_tables, the shipped-corpus census |
| `ladder_rederive.py` | §3.1 — the whole ladder from the record |
| `r4attack/attack.py` | §3.3/3.4 — three new R4 spellings, kernel-exclusive **and** whole-program |
| `rec_head.json` | the pre-rebuild measurement record, for M1 |
| `bug49354/` | §2.3 — phpt extraction + blob authentication, the real-C differential, five mutants, `run.sh` |
| `spansmf/mustfire.py` | §4.2 — eleven `extra_spans` must-fire controls on a scratch row of symlinks |
| `spansmf/provenance_old.py` | the pre-`extra_spans` validator, for the byte-identical check |
| `spans/mutate.py`, `spans/{old,new}tree/` | §4 — the 19-case control driver and the mirrored old/new validator trees |
| `spell/` | §3.2 working files, incl. `matcher_diff.py` |

Re-run: `python3 .temp/php22/msproof/gen_ms.py && python3 .temp/php22/msproof/gen_ms2.py`,
then `./verus_run.py .temp/php22/msproof/<f>.rs [--cfg slb_twin]`; the other
probes take no arguments.

---

**Running count: launched from 74.** This review refuted the sentence F47 leads
with — while confirming, by construction, the claim underneath it that the task
asked to be tested. It found two stale declarations inside hash-pinned files, one
of them the exact hole `PROTOCOL.md` rule 6 documents. It attacked the R4
endpoint with three further spellings and **failed to move it**, which makes the
row's strongest number stronger. And it says the manager deferred: **4.1-A is a
norm wearing an observation's clothes, and by the engineer's own argument for
holding 4.1-B, landing 4.1-A buys the row nothing it does not already have.**
