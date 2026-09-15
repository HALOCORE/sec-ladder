# ph03-uudecode-bound — notes

`php_uudecode`, PHP 5.0.0, `ext/standard/uuencode.c:126-171`. Corpus row
CRASH-115 (merged with V5C-116). Tier `verbatim`. Built at `TASK_PHP_013`,
reviewed at `TASK_PHP_014`, **corrected and re-measured at `TASK_PHP_015`**.

**This is the PHP programme's first real row.** Twelve prior tasks produced
infrastructure, mining, a catalogue and reviews; none produced a row. Several of
the notes below are therefore about the *pipeline* rather than about uudecode,
and they are marked ⚠⚠ where a reader should carry them to the next row.

⚠⚠ **WHAT `TASK_PHP_015` CHANGED, BECAUSE EVERY NUMBER BELOW MOVED.** The row's
findings all survived review; its **fixture** did not. `inputs/gen.py` emitted
length byte **45 and nothing else**, so the benign corpus never once took the
`floor()` arm of `uuencode.c:141` — the arm the whole row is named for — and
`45 ≡ 0 (mod 3)` is exactly the case in which a line emits as many bytes as it
declares. That hid a real defect in `model.py` for a task (§13). The generator
now emits a **short final line** (which is also what `php_uuencode` really
emits), so the strides moved 498 → **556** and 4032 → **4090**, a fifth
adversarial input was added, and the row was rebuilt and re-measured. **§6, §7
and §8 are all new numbers; nothing in §1–§5 depends on the fixture and none of
it moved.**

---

## 0. `PROTOCOL.md` rule 6 — the declaration, as first written

```
contract_sha256  875387e901b85b5eb969ab5be8b9d86e45f779d87456bbeb0ade3f833ab822dd   AS FIRST WRITTEN
contract_sha256  bb2eb51917d2aabcafde52b3693ee9e2659e0442c99be5939bbc08761d3f2746   after gate run 1
contract_sha256  0302248bc9868121ae74260e3b4ec4987fde5437e5c0a366ca8bef78d0f140df   as shipped at TASK_PHP_013
contract_sha256  2fcd6802b9042dd2982a37636fda972cb649711ddb20bad61b2ae2893099bbc7   AS SHIPPED (TASK_PHP_015)
```

⚠⚠ **IT MOVED A THIRD TIME AT `TASK_PHP_015`, and unlike the first two this one
is NOT a gate finding — it is a review finding, so `PROTOCOL.md` rule 6's
disclosure is owed differently.** The `0302248b…` line is what `TASK_PHP_013`
committed and what the reviewer verified independently; `2fcd6802…` is this
tree. **Four edits inside the fenced block, all of them landing corrections that
`TASK_PHP_014` measured:**

1. **`note` (M1).** It claimed `model.py::uu_fold` mirrors `verus.rs`'s walk.
   **It did not** — it folded every emitted byte where `verus.rs` folds the
   first `total_len`, which is a different function for 42 of the 63 length
   bytes. ⚠ The claim was *inside the hashed contract*, so the false sentence
   was pinned. Now corrected, and the correction names the synthetic sweep that
   makes it checkable. §13.
2. **`provenance.deletions` → `provenance.divergences`**, with a `kind` on each
   entry. **Three of the four entries are not deletions** (two substitutions and
   one projection). `PROTOCOL_PHP.md` §A2 renamed to match; nothing reads the
   key, and `provenance.py` never did.
3. **`collapse.note`, `miri.blocked_reason`, `uses_allocator_why`** — the window
   sizes and `cap` bound, which the fixture change moved (498/4032 → 556/4090,
   `cap` ≤ 3025 → ≤ 3069).
4. **`idiom.why`** — two sentences: the dead hunk 1 (§5e), and a marker saying
   that `sanitizer_hardened`'s four `expect: clean, fired: false` rows are **not**
   evidence the fix is complete. That second one is `TASK_PHP_014` m6, and it
   goes in `why` **because `why` is the only part of the contract the gate record
   echoes** — `provenance`, including `fix_commit_note`, is not in the record at
   all (checked: `'fix_commit_note' in json.dumps(record)` is `False`).

⚠ **The `git show <commit>: | diff` test is available for this move and was
not needed**: every edit above is itemised and the before-hash is recorded, so a
reviewer can reproduce `0302248b…` from `git show HEAD:patterns-php/…/spec.md`
directly. That is what a second-and-later move is supposed to look like, and it
is the check §0's original text could not offer.

⚠⚠ **IT MOVED TWICE, AND HERE IS EXACTLY WHY — `PROTOCOL.md` rule 6: *"If the
hash changes later, say so and say why."*** Both moves are gate findings, not
second thoughts. The **first gate run refuted two declarations**, and both
corrections are inside the fenced block:

1. **`identity` at O0 was pinned `norel` and the measured level is `differ`.**
   I had taken `norel` from p01/p16 and from a hand build that showed only a
   size difference. The gate disassembles: 335 vs 352 instructions, 1906 vs
   2042 bytes — a real codegen difference, not relocations. **The pin was too
   strong and the gate caught it**, which is the direction that pin exists for.
   `identity.why` now carries the record's own `md5_fn` and the mechanism.
2. **`verus.unsafe_justifications["verus.rs"]["vset_unchecked"]` did not
   exist.** Stage `tcb-unsafe` requires a written justification when a trusted
   item's `requires` leaves a parameter its body uses unconstrained — here the
   value `x`. That is a *new* obligation for this row because `vset_unchecked`
   is the project's first **writing** trusted accessor; a read wrapper has no
   value parameter and never triggers it.

The **second gate run** then shouted `[idiom-forbidden]` three times:
**every one of my `forbidden` entries carried its spelling in plain prose with
no backticks, so the enforced audit ranged over none of them** and the
`0 forbidden hits` line above it was vacuous. ⚠ **That is the p09 shape — five
entries, zero audited spellings — and it is the exact defect `TASK_038_REVIEW`
named.** The three entries now carry exactly one backticked spelling each and
the audit reports `3 spelling(s), 0 hit(s), 0 entry/entries with NO backticked
spelling`. The `required` entries were tidied in the same pass: two are now
per-language `{c: ...}` objects (they quote C expressions no Rust rung can
contain, and a plain string is matched against every rung), and two carry no
backticks at all with a sentence saying why — they pin an ALGORITHM CHOICE and
an OPERATION, neither of which a single token decides.

⚠ **Neither correction touches a measured number.** `spec.md` is not in
`measure.py::measurement_sources` (that is `harness/{build,asm,measure}.py`,
`common/{driver.*,slb.py}` and the row's `*.rs` / `c/*`), so the measurement
record is unaffected and was not re-taken; the cost was `report.py` + a second
gate run, which the six-command chain already budgets.

**The first hash above was written before any measurement**, and computed the way
`check.py::read_contract` computes it —
`re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)`, whose capture **keeps
the newline before the closing fence**. The obvious spelling
`` ```slb-contract\n(.*?)\n``` `` gives `db3f258b08c1807c…` for this file, which
is a different number and is not what any record carries
(`PROTOCOL_PHP.md` §E).

⚠ **The `git show HEAD: | diff` test is VACUOUS on a new row and is not run
here.** ph03 lands in one commit, so on a clean tree that command always prints
nothing and always looks like it passed (`PROTOCOL.md` rule 6). **The hash above
is the only evidence**, which is why it is written down before any cell was
built through `harness/build.py`.

⚠ **Honest disclosure of what "before any cell" means here.** Sixteen C builds
(8 cells x {`kernel.c`, `kernel_hardened.c`}), twelve Rust builds (R2/R3/R4 x
{O0,O3} x {isolated,whole}) and two Verus builds were compiled **by hand into
`.temp/php13/bin/`** while the row was being written, before `spec.md` existed
at all — that is how the `-lm` finding (§9), the read-vs-write finding (§4) and
the R4/R5 identity figure in `spec.md`'s `identity.why` were obtained. None of
them went through `harness/build.py`, none produced a record, and no number in
`spec.md` was chosen after seeing a measurement record. The `identity` pin is
the one place a hand-measurement fed a declaration, and it says so in its own
`why`.

---

## 1. Reachability, settled against the kernel before any rung existed

`PROTOCOL_PHP.md` §A3 makes this deliverable #1. It was answered with an
instrumented interpreter of the verbatim function — offsets, not pointers, so it
can record every read and write without executing any of them —
`.temp/php13/02-reach.c`, output `.temp/php13/02-reach.log`.

Over **12 600** single-line documents (`src_len` 1..200 × declared `len` 1..63):

```
Q2 verbatim, 200*63 = 12600 single-line documents:
   read  past src end : 3608
   write past emalloc : 3352
   either             : 3608   (len values seen: 1..63)
   :158 tail entered  : 0   <- 0 means the tail block is DEAD
```

**The over-read is a superset of the over-write** — 3608 ⊇ 3352 — which is the
first half of §4's finding: on an exactly-sized source the read always leaves
the allocation first, and the write is only *separately* observable when the
source has slack.

The `len` values that trigger span the whole domain 1..63, so this is not a
property of the `len == 45` special case.

---

## 2. Fidelity evidence — the corpus's recorded category, reproduced

`PROTOCOL_PHP.md` §A4. `index.csv` records CRASH-115 as
`heap-buffer-overflow`; its history layer's note reads *"run5.py:
heap-buffer-overflow at uuencode.c:144 in php_uudecode, faults_5.0.0=true"*.

Built exactly as `check.py::_san_build` builds it (gcc, `-O1 -g
-fsanitize=address,undefined -fstrict-aliasing -static-libasan
-static-libubsan -DSLB_ISOLATED`), run with `env -u LD_PRELOAD`
(`PLAN_PHP.md` §7 rule 14). Re-run over the `TASK_PHP_015` corpus,
`.temp/php15/12-asan.log` and `.temp/php15/22-asan-lines.log`
(the original is `.temp/php13/06-asan.log`):

| input | `c/kernel.c` (R1) | `c/kernel_hardened.c` (R1h) |
|---|---|---|
| `small.bin` | clean, `5115966432339535952` | clean, same |
| `large.bin` | clean, `5544170072369974633` | clean, same |
| `adversarial-read.bin` | **heap-buffer-overflow READ of size 1**, `php_uudecode` `kernel.c:143` = `uuencode.c:144` | clean, `9832046297558006400` |
| `adversarial-write.bin` | **heap-buffer-overflow WRITE of size 1**, `kernel.c:145` = `uuencode.c:146` | clean, same |
| `adversarial-shortsrc.bin` | **heap-buffer-overflow READ of size 1**, `kernel.c:145` = `uuencode.c:146` | clean, `10969280517312833152` |
| `adversarial-floor.bin` | **heap-buffer-overflow READ of size 1**, `kernel.c:143` = `uuencode.c:144`, 0 bytes after a 45-byte region | clean, `10286939257659585152` |
| `adversarial-nowin.bin` | clean, `0` | clean, `0` |

⚠ **The three adversarial checksums did not move when the corpus was
regenerated, and that is not luck.** A refused window returns
`0xFFFFFFFF ^ tally(cap)`, which depends only on `cap` and therefore only on the
window's LENGTH — so those rows pin the guard that fired and the size that was
allocated, and nothing about the random bytes. `small`/`large` moved because
their windows decode.

⚠ **`adversarial-floor.bin` is `TASK_PHP_015`'s.** It is the first adversarial
cell whose length byte is **not 45**, so it is the first one that reaches
`uuencode.c:141`'s `floor()` arm: `len = 40`, `fl = (int) floor(40 * 1.33) = 53`
against a true end 44 characters away. Hunk 1 (`len > src_len`) does **not**
fire, so it is also the only adversarial input that isolates hunk 2 — the one
guard of the 2004 fix that decides anything (§5e).

✅ **Same category, same function, and `uuencode.c:144` is the exact line the
corpus names.** `TASK_PHP_012`'s probe reported a **WRITE** at `:144` where this
row reports a **READ** at `:144` and a **WRITE** at `:146` — §4 is why, and it is
a property of that probe's stack buffer, not a disagreement about the defect.

The must-fire control for the detector itself is
`controls/fix_incomplete.c control` (§5): it fires, so ASan silence on the
benign rows means something.

---

## 3. Admission, against `PLAN_PHP.md` §3

1. ✅ **correct on benign input** — `small`/`large` round-trip and all six rungs
   agree to the bit (§6 table).
2. ✅ **exhibits the target error on an adversarial input, with a detector
   firing and a must-fire control** — the table above plus
   `controls/fix_incomplete.c control`.
3. ✅ **kernel shape** — flat blob in, `u64` out, the shared driver loop.
4. ✅ **`kernel_hardened.c` differs by the safety lines and nothing else**, and
   here they are the real `fix_commit`.

---

## 4. ⚠⚠ WHICH LIMB THE ORACLE SEES IS DECIDED BY THE SOURCE BUFFER

The catalogue's ⚠ risk field for `ph03` says *"the row's `cwe` is CWE-125 but the
**write** fires first under ASan on most inputs. The oracle must record which,
not pick one silently."* **Both halves of that turn out to be about the harness
rather than about the defect, and the row ships the experiment.**

`adversarial-read.bin` and `adversarial-write.bin` carry the **same 71-byte
window** — one well-formed line, then a length byte claiming 45 with 8
characters behind it — and differ in exactly one thing: the second has **60
bytes of slack after the window inside the blob**. `nwin = n_blob / stride` is
1 in both, so the driver picks the same window either way.

```
adversarial-read   stride=71  n_blob=71   -> READ  at uuencode.c:144
adversarial-write  stride=71  n_blob=131  -> WRITE at uuencode.c:146
```

**Mechanism.** The inner loop reads four source bytes and writes three
destination bytes per iteration. The source pointer runs away from `e` at 4
bytes per iteration while `p` runs away from `cap` at 3, and it starts closer:
`cap = ceil(0.75·src_len) + 1` is *three quarters* of the source, so the write
has ~25 % more headroom. **On an exactly-sized source the read always leaves the
allocation first.** §1's 3608 ⊇ 3352 is the same fact counted.

⚠ **So the over-write is not independently reachable on an exact buffer — it is
downstream of the over-read.** The corpus recorded the write because *PHP always
has slack*: `zend_parse_parameters "s"` hands over a NUL-terminated zval string
and `emalloc` rounds the allocation up to a multiple of 8. `TASK_PHP_012`'s
probe saw the write for the same reason — a `char enc[16]` holding 9 live bytes.

**Consequence for the corpus, and it is a correction rather than a complaint.**
`TASK_PHP_012` m8 proposed re-labelling this row `CWE-787`. That is adopted:
`provenance.cwe` is `CWE-787` and `provenance.cwe_note` records the
disagreement and both runs. But *"the write fires first"* is only true of a
source with slack, and a reader who took it as a property of the code would
build the wrong adversarial input and get a green gate on a silent over-read.

⚠⚠ **Carry this to the next row: an oracle built on "which sanitizer message
appears" is measuring the allocator's rounding as much as the defect.** Where
two limbs share a bound, ship both blobs.

---

## 5. ⚠⚠⚠ THE HEADLINE — OF A TWO-HUNK FIX, ONE HUNK IS DEAD AND THE OTHER IS INCOMPLETE

`PROTOCOL_PHP.md` §C: *"An upstream fix is not automatically correct … That is a
result, and one of the strongest a row can carry. Report it; do not repair it."*

`c/kernel_hardened.c` is `f95c1df583490814b0501c56f59671193a57507b` (Ilia
Alshanetsky, 2004-08-24, bug #29821), all three hunks, patch bytes at
`controls/f95c1df58349.patch`, sha256 `fc3ef3c50488d0…`. Its two guards are
`if (len > src_len) goto err;` (**hunk 1**) and `if (ee > e) goto err;`
(**hunk 2**). Both halves of the headline are measured, and each is measured
from both sides:

| | claim | C side | Verus side |
|---|---|---|---|
| **hunk 2** | **incomplete** — bounds where the inner loop *tests*, while the body reads `*(s+3)` | 144 of 12 600 documents still read past the source (§5a) | deleting the 2014 fix makes `i < v@.len()` fail (§5b) |
| **hunk 1** | ⚠ **dead — it decides nothing** | of its 1 953 firings, hunk 2 would have refused **1 953** (§5e) | deleting it still gives `25 verified, 0 errors` (§5e) |

**Hunk 2 is incomplete because `ee` bounds where the inner loop TESTS and the
body reads `*(s+3)`**, so the loop overshoots `ee` by up to three bytes whenever
`ee - s` is not a multiple of 4 — which is every `len` except 45 and the
minority whose `(int) floor(len * 1.33)` happens to be divisible by 4.

⚠ **§5e was added at `TASK_PHP_015` from `TASK_PHP_014` M5. It is not a
correction — it is a result this row missed**, and it sharpens the headline
rather than softening it: *the patch that missed the real bug for ten years also
shipped a check that never decided anything.*

### 5a. The C side, with a must-fire control

`.temp/php13/02-reach.log` Q3, the same 12 600 documents as §1, with the 2004
fix applied:

```
Q3 with f95c1df58349 applied, same 12600 documents:
   goto err taken     : 3464
   read  past src end : 144   <- >0 means the fix is INCOMPLETE
   write past emalloc : 0
   :158 tail entered  : 0

Q3 smallest surviving over-reads (src_len, len, fl, read up to, src end, past by):
   src_len=2   len=1  fl=1  rd_max=4   e=2   past=3  wr_max=2   cap=3
   src_len=3   len=1  fl=1  rd_max=4   e=3   past=2  wr_max=2   cap=4
   src_len=4   len=3  fl=3  rd_max=4   e=4   past=1  wr_max=3   cap=4
```

**The write is closed; a read is left.** Run under ASan by
`controls/fix_incomplete.c`, `.temp/php13/11-fixctl.log`:

```
----- control     (the detector must be live)
CONTROL  reading b[8] of an 8-byte malloc
==1440994==ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 1
    #0 ... in main .../controls/fix_incomplete.c:126

----- benign      (must be silent)
BENIGN   src_len=63 -> total_len=45 (expect 45)

----- fixed       (2004 fix APPLIED -- the finding)
fixed     src_len=2, len byte declares 1, fl=1, ee == e (2014 fix ABSENT)
==1441005==ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 1
    #0 ... in php_uudecode .../controls/fix_incomplete.c:88     <- uuencode.c:144

----- fixed2014   (2014 fix APPLIED -- silent)
fixed2014 src_len=2, len byte declares 1, fl=1, ee == e (2014 fix APPLIED)
fixed2014 returned -1 -- no detector fired
```

⚠⚠⚠ **AND THE CONCLUSION THAT MECHANISM IMPLIES, WHICH THIS SECTION USED TO
STATE ONLY HALF OF** (`TASK_PHP_014` M6). The source buffer above is `malloc`ed
at **exactly** `src_len` bytes. **PHP's is not.** `zend_parse_parameters "s"`
hands `php_uudecode` a zval string, which is `emalloc(len + 1)`, and `emalloc`
rounds to a multiple of 8 (`PHP_SHIM_REAL_SIZE(size) = ((size)+7) & ~7`,
`common-php/emalloc_shim.h:217`, projecting `Zend/zend_alloc.c:135`). Measured,
same decoder, same input, three source allocations, with a must-fire control
(`.temp/php14/07-zval-slack.c`, re-run at `.temp/php15/21-zval-slack.log`):

```
----- control   CONTROL reading b[8] of an 8-byte malloc
                ==1801732==ERROR: AddressSanitizer: heap-buffer-overflow
----- exact     src_len=2, allocation 2 bytes, slack 0
                ==1801741==ERROR: AddressSanitizer: heap-buffer-overflow
----- zvalraw   src_len=2, allocation 3 bytes, slack 1   (USE_ZEND_ALLOC=0)
                ==1801749==ERROR: AddressSanitizer: heap-buffer-overflow
----- zvalmm    src_len=2, allocation 8 bytes, slack 6   (real emalloc)
                zvalmm returned 1 -- NO DETECTOR FIRED
```

**So the honest statement is *"a detector fires under this allocator"*, not
*"PHP faults"*.** The 2014 residual reaches `src_len + 2` while `emalloc` gives
`ALIGN8(src_len + 1) - src_len ∈ {1..8}` of slack, so it is **invisible for 6 of
the 8 residue classes of `src_len` mod 8** — and *a fortiori* on a stock build,
where `_emalloc` also puts a `zend_mem_header` and an end magic inside the same
libc block. It IS visible on a `USE_ZEND_ALLOC=0`-style build (`zvalraw`, which
still fires), which is how PHP is sanitizer-tested and plausibly how #67252 was
found.

⚠⚠ **This does NOT weaken the headline, and the reason is worth stating rather
than assumed.** Of §5's three proofs, **two are allocator-independent**: §1's
interpreter uses offsets and no allocator at all, and §5b's `i < v@.len()` is a
property of the *source slice*, not of any allocation. Only this one is
harness-conditional. ⚠ **And the finding is STRONGER for it** — *this residual
is not ASan-observable on a stock PHP build at all, which is part of why it
survived ten years.* §4's lesson one level down: an oracle built on "which
sanitizer message appears" is measuring the allocator as much as the defect.

### 5b. The Verus side: the proof refuses the shipped fix

`controls/negatives.py --emit no2014` deletes **only** the four lines of the 2014
check from `verus.rs` and leaves the algorithm `c/kernel_hardened.c` implements.
`.temp/php13/10-verus-negctl.log`:

```
error: precondition not satisfied
   --> ...verus_no2014_tmp.rs:673:26
    |
382 |         i < v@.len(),
    |         ------------ failed precondition
...
673 |             let b1: u8 = get_unchecked(buf, s + 1);

verification results:: 24 verified, 1 errors
```

⚠ **Read the second error, not the first.** `i < v@.len()` on
`get_unchecked(buf, s + 1)` **is** the over-read — the same byte ASan reports at
`uuencode.c:144` in 5a. A verifier in 2026 refuses, in one line, the patch PHP
shipped in 2004 and did not complete until 2014.

⚠⚠ **AND WHY THE FIRST ERROR IS NOT ITSELF A FINDING, because as written a
reader could report a write overflow that does not exist** (`TASK_PHP_014` m7).
The first error is `lemma_store_in_bounds`'s `s + 4 <= off + len`, i.e. the
**write** bound. §5a says the 2004 fix *closes* the write, and it does — but
**with zero slack**, so the proof has none either. Measured over **170 226**
multi-line documents under the 2004 fix (`TASK_PHP_014` N8, re-run at
`.temp/php15/20-hunk-rerun.log`):

```
   documents swept    : 170226
   write past emalloc : 0     <- >0 would REFUTE 'the write is closed'
   read  past src end : 1008
   tightest write margin (cap-1 - wr_max) : 0 at K=0 L=1 src_len=2
```

**The tightest margin is exactly 0.** No write escapes, and there is no room to
prove that it does not without the 2014 check. The first error is therefore a
proof-slack artefact and the second is the live defect — which is why they must
be read in that order and not by exit code.

### 5c. PHP's own second fix, and its reproducer

```
commit  1e2818b143760a79a0887861bd6221b158355073
author  Stanislav Malyshev <stas@php.net>, 2014-05-11
subject Fix bug #67252: convert_uudecode out-of-bounds read
        while (s < ee) {
    +           if(s+4 > e) {
    +                   goto err;
    +           }
```

Its `.phpt` is `"M" + 60 chars + "\n" + "a."`, and `PHP_UU_DEC('a') == 1`, so
`fl == 1` and `ee == e` — the same shape §5a's `src_len=2, len=1` row found
independently. Patch at `controls/1e2818b14376.patch`, sha256
`97975e658d67aaad…`.

**It is deliberately NOT in `c/kernel_hardened.c`.** R1h is `fix_commit`, and
`fix_commit` for CRASH-115 is the 2004 commit. R2–R5 carry it, and *have to*:
see `safe_naive.rs`'s header.

### 5d. ⚠⚠⚠ AND THE GATE CANNOT HOLD THIS RESULT

`harness/check.py::check_sanitizers_hardened` (stage `7h`) hard-fails the gate on
**any** ASan/UBSan diagnostic from the R1h arm on **any** input:

> *"R1h is the rung that does NOT have the bug, so the expectation is `clean` on
> **EVERY** input, adversarial included — that is what R1h *means*, and a
> per-input declaration here would let a pattern declare its way out of the only
> thing this stage asks."*

That is right for a PAT row, whose R1h is hand-written. It is **wrong for a php
row**, whose R1h is whatever upstream shipped — and `PROTOCOL_PHP.md` §C calls
"upstream got it wrong" the strongest available result. **The two documents are
in direct tension and the first real row hit it.** A blob demonstrating 5a
cannot live under `inputs/`; it lives in `controls/` and is run by hand.
`model.py::selfcheck` asserts no shipped input reaches the 2014-only class, so
the constraint is enforced rather than remembered. Reported to the manager as a
finding; **the fix is not this row's to make.**


### 5e. ⚠⚠⚠ THE OTHER HALF OF THE 2004 FIX IS DEAD — HUNK 1 DECIDES NOTHING

`TASK_PHP_014` M5, and it is a **result the build missed**, not a defect the
review found. Two sides, both re-run at `TASK_PHP_015`.

**C.** `.temp/php14/06-hunk.c` decomposes `goto err` by hunk over the same
12 600 documents as §1 (`.temp/php15/20-hunk-rerun.log`):

```
   hunk 1 (`len > src_len`) fired : 1953
   hunk 2 (`ee > e`)        fired : 1511
   of hunk-1 firings, hunk 2 would ALSO have refused : 1953
   of hunk-1 firings, hunk 2 would NOT have refused  : 0  <- 0 means HUNK 1 IS REDUNDANT
```

**Verus.** `controls/negatives.py` now emits two must-**PASS** mutants, and
`.temp/php15/19-negatives.log` runs all three controls against their declared
expectations in one pass:

```
no2014         expect REFUSE got REFUSE  verification results:: 24 verified, 1 errors ok
no2004a        expect VERIFY got VERIFY  verification results:: 25 verified, 0 errors ok
no2004a_both   expect VERIFY got VERIFY  verification results:: 25 verified, 0 errors ok
```

⚠ **`no2004a` is the decisive one and the argument is short.** It deletes hunk 1
from the **exec** and leaves `uu_walk`'s matching branch in the **spec**, so the
spec still refuses every `ln > src_len`. An exec that has lost hunk 1 can only
satisfy that postcondition if some other branch refuses exactly the same inputs
— and hunk 2 does. `no2004a_both` says the same thing from the spec side.

**The mechanism is one line.** `line_len(ln) >= ln` for every `ln ∈ 1..63`, and
after `s++` we have `e - s <= src_len - 1`; so `ln > src_len` forces
`fl > e - s`, which is hunk 2's condition.

⚠⚠ **This is the first control in either programme whose declared expectation is
that the mutant STILL VERIFIES**, and `controls/negatives.py`'s docstring says
plainly why that is a weaker instrument than a must-FAIL one and what guards it:
the anchor-uniqueness check refuses to emit a no-op, and `no2014` shares the
emit path and is must-FAIL, so a `negatives.py` that had stopped mutating
anything would be caught there rather than here.

⚠ **`inputs/adversarial-shortsrc.bin` stays** even though the guard it reaches
is the dead one. It pins **which** guard R1h reaches first, which is what a
reader of `kernel_hardened.c` asks; `inputs/adversarial-floor.bin`
(`TASK_PHP_015`) is the cell for hunk 2 with a non-45 length byte.

---

## 6. Cross-rung agreement, and the one rung that diverges

All six rungs, `-O3 isolated`, on every input
(`.temp/php15/11-crossrung.log`; the original is `.temp/php13/05-crun.log`):

| input | R1 | R1h | R2 | R3 | R4 | R5 | `model.py` |
|---|---|---|---|---|---|---|---|
| `small` | `5115966432339535952` | = | = | = | = | = | = |
| `large` | `5544170072369974633` | = | = | = | = | = | = |
| `adversarial-read` | **abort** | `9832046297558006400` | = | = | = | = | = |
| `adversarial-write` | **abort** | `9832046297558006400` | = | = | = | = | = |
| `adversarial-shortsrc` | **abort** | `10969280517312833152` | = | = | = | = | = |
| `adversarial-floor` | **`15053435816339650688`** | `10286939257659585152` | = | = | = | = | = |
| `adversarial-nowin` | `0` | `0` | = | = | = | = | = |

R1's "abort" without a sanitizer is glibc's own
`malloc(): invalid size (unsorted)` at exit 134 — the heap metadata it corrupted
is detected on the next allocation, on all eight C cells.

⚠⚠ **`adversarial-floor` is the row's first input on which R1 EXITS 0 WITH A
WRONG ANSWER**, and it is worth a sentence because it is the shape a reader
under-weights. The other three adversarial inputs make R1 corrupt heap metadata
badly enough that glibc notices on the next allocation; here the over-read runs
off a 45-byte window into live heap and the over-write stays inside the
allocator's rounding, so **nothing complains and the program prints a number**.
Only ASan sees it (§2). *"The rung aborted"* is not the defect and *"the rung
returned"* is not safety — `check.py`'s adversarial stage records per-rung
behaviour rather than requiring agreement, which is exactly why it can hold
this row.

**`uuencode.c:158` is dead on every window of every input**, re-derived per input
by `model.py::selfcheck` (§1's 0/12600 is the general statement; the model
checks the ones that ship). ⚠ It stays dead under the `TASK_PHP_015` corpus for
a reason the short line makes non-obvious: a line emits `3*ceil(fl/4)` bytes and
declares `ln`, and `lemma_emit_covers_declared` proves `ln <= 3*ceil(fl/4)` for
every `ln`, so `total_len > (p - *dest)` is false by the row's own Verus lemma
and not by the corpus's accident.

---

## 7. ⚠ The allocator, and one asymmetry a reviewer should attack

`c/emalloc_shim.h` is symlinked (unconditional, `PROTOCOL_PHP.md` §B2), and this
row genuinely uses it: `php_shim_reset()` at the top of every kernel call
(§B1.3), one `php_shim_emalloc(cap)`, one `php_shim_efree`, and
`php_shim_tally()` xored into the returned `u64` (§B1.2).

✅ **`emalloc_dependent: false` is CONFIRMED.** `cap = ceil(0.75·src_len) + 1`
is 418 for `small`, 3069 for `large`, 55, 16 and 35 for the adversarial windows.
Truncations T1 (32-bit `real_size`), T2 (31-bit recorded size) and T3
(`_ecalloc`, never called) all sit ~2⁴⁰ below their moduli. **The shim is
exercised, digested and executed on the first real row without its semantics
being the finding**, which is what `TASK_PHP_012` §7.3 said this row was for.

⚠⚠ **THE ASYMMETRY, STATED PLAINLY BECAUSE IT IS THE THING TO ATTACK.**
`PROTOCOL_PHP.md` §B1.2 says *"fold `php_shim_tally()` into the kernel's `u64`"*.
That is a C-side instruction. **The Rust rungs do not link the shim**; they
compute the same value arithmetically:

```rust
fn tally(cap: usize) -> u64 {
    let real_size: u64 = ((cap + 7) & !7) as u64;
    1000003u64 ^ 1000033u64 ^ real_size.wrapping_mul(1000039)
}
```

`n_alloc = n_free = 1` and `n_cache_hit = 0` because `php_shim_reset()` empties
the size-class cache at the top of every call, so the closed form is exact — and
it was checked against the C before either was pinned: predicted
`10969280517312833152` for `adversarial-shortsrc` and `9832046297558006400` for
`adversarial-read`, both matching the C runs to the bit. ⚠ **Both of those
survived the `TASK_PHP_015` regeneration unchanged**, and that is a property
rather than luck: a refused window returns `0xFFFFFFFF ^ tally(cap)`, so its
checksum depends on the window's LENGTH and on nothing else in it.

**What it buys:** the allocation SIZE is a pinned cross-rung quantity — a rung
that sized its destination differently could not agree by accident, and sizing
is *half of this defect*.

⚠⚠ **AND THE PRECISE CONDITION UNDER WHICH THAT ARGUMENT WORKS, because
"does not carry to `ph29`" without a criterion is not a rule the next row can
apply** (`TASK_PHP_014` §4.4). `cap` depends only on `stride`, which is fixed by
the payload header, so `php_shim_tally()` is a **per-input CONSTANT** — measured,
one distinct value per input across every call. A constant XORed into every
per-call result before the driver's Horner fold cannot mask a *per-call* wrong
answer: to cancel, a rung would have to be wrong the same way on every call,
which means it computed a different `cap`, which is the one thing the XOR is
there to catch. **The technique is sound exactly while the tally is
input-constant.** On `ph29` the tally VARIES with the input, because the
truncation *is* the defect — and a varying mixed-in term is one that can cancel
a per-call error. That is the criterion, and it is checkable before a row is
started rather than after.
**What it does NOT buy, and must not be read as:** it is not evidence that any
Rust rung ran PHP's allocator, and a truncation-dependent row could not be
modelled this way at all. ⚠ **`ph29` is the row where the shim's semantics ARE
the defect; this technique does not carry over to it**, and a reviewer should
check that the next builder does not copy it.

⚠ A second, smaller asymmetry: `php_shim_reset()` walks 11 size classes per
call on the C side and the Rust rungs have no analogue. It is a fixed per-call
term inside both C cells, so it cancels in R1-vs-R1h and does **not** cancel in
C-vs-Rust. §8's decomposition is where that lands.

---

## 8. Measurement — the numbers and the mechanism

From `results-php/ph03-uudecode-bound.json`; the full matrix is
`results-php/tables/ph03-uudecode-bound.md`. **`-O3 isolated`,
kernel-exclusive `Ir`.** `small` makes 25 000 calls over a 556-byte window
(8 full lines × 15 groups + a short final line × 14 = 134 groups), `large`
20 000 calls over 4090 bytes (65 × 15 + 14 = 989 groups).

| cell | `Ir`/call, small | `Ir`/call, large | **`Ir`/group** | fixed `Ir`/call |
|---|--:|--:|--:|--:|
| `c-gcc` (R1) | 7 369.7 | 52 913.9 | **53.27** | 231.8 |
| `c-gcc-h` (R1h) | 7 338.7 | 52 711.9 | **53.07** | 227.6 |
| `c-clang` (R1) | 6 244.7 | 45 050.9 | **45.39** | 162.8 |
| `c-clang-h` (R1h) | 6 272.7 | 45 249.9 | **45.59** | 164.0 |
| `safe_naive` (R2) | 9 363.7 | 68 632.9 | **69.32** | 74.7 |
| `safe_tuned` (R3) | 7 648.3 | 55 973.9 | **56.52** | 74.5 |
| `unsafe` (R4) | 6 817.4 | 49 897.9 | **50.39** | 65.6 |
| `verus` (R5) | 6 817.4 | 49 897.9 | **50.39** | 65.6 |

`Ir`/group is the marginal `(large − small) / 855`; "fixed" is
`small − 134 × marginal`, i.e. the per-call term that does not scale with the
window. ⚠ **855 is still the divisor after the fixture change, and not by
accident**: both windows gained exactly one 14-group short line, so the
difference is exactly 57 FULL lines × 15 groups. The `Ir`/group column is
therefore "per group of a full line" in both corpora, which is what makes the
two directly comparable.

⚠⚠⚠ **AND THAT COMPARISON IS THE STRONGEST THING IN THIS SECTION: EVERY
MARGINAL FIGURE REPRODUCED TO TWO DECIMAL PLACES ACROSS A COMPLETELY DIFFERENT
FIXTURE.** `TASK_PHP_015` moved both strides, changed every benign byte, added a
seventh input and rebuilt all 32 cells, and 53.27 / 53.07 / 45.39 / 45.59 /
69.32 / 56.52 / 50.39 / 50.39 came back **identical**. Nobody planned that as a
replication and it is worth more than one that was: the marginal is a slope, and
a slope that survives a change of both endpoints is a slope and not a fit.
⚠ **The FIXED column is the half that moved** (Rust ≈ 85 → ≈ 75/66, C ≈ 234 →
≈ 232), and it moved for the reason `TASK_PHP_013` §12.8 already flagged: it is
a two-point extrapolation, `small − 134 × marginal`, and the short line's groups
cost slightly less than a full line's (its Horner fold covers `total_len ∈
{40,41,42}` rather than the 42 bytes it emits). **The ordering — C carrying
~150 `Ir`/call more fixed cost than Rust — is robust and mechanism-backed; the
exact values are not, and never were.**

⚠ `RECAP_PHP.md` open item 9 / F14: **no php `Ir` is comparable to any
PAT `Ir`**, and none of these is put next to a `pNN` number anywhere.

### 8a. The deltas, and the mechanism for each

⚠ `PROTOCOL_PHP.md` §F item 8: *a cost with no mechanism is an incomplete row.*
Every number below is read off `objdump -d` of the shipped `-O3 isolated`
binaries.

**R2 − R4 = +18.93 `Ir`/group — one `cmp`/`jae` pair per checked access.**
R4's group body goes straight from the trip test to four `movzbl` loads. R2's
emits, immediately before them:

```
lea    -0x1(%r14),%rbx
cmp    %rsi,%rbx  ; jae <panic>      <- buf[s]
cmp    %rsi,%r14  ; jae <panic>      <- buf[s+1]
cmp    %r12,%r10  ; jae <panic>      <- dest[p]
```

There are ten checked accesses per group in R2 — four source reads, three
destination writes, and the three fold reads the group's bytes will later
receive — and ~1.9 `Ir` each is exactly a `cmp` + a not-taken `jae`.

**R3 − R4 = +6.13 `Ir`/group, so the reslice recovers 68 % of it — and the
residual is NOT a bounds check.** R3's body reads:

```
lea    0x3(%rdx),%r15 ; cmp %rsi,%r15 ; ja  <panic>   <- ONE check for buf[s..s+4]
cmp    $0xfffffffffffffffc,%rax ; ja <panic>          <- p + 3 must not WRAP
lea    0x3(%rax),%rbp ; cmp %rbx,%rbp ; ...           <- ONE check for dest[p..p+3]
```

Four source checks collapse into one and three destination checks into one —
**and `&mut dest[p..p + 3]` adds an overflow test on `p + 3` that R2's
`dest[p]`, `dest[p+1]`, `dest[p+2]` never needed**, because a range expression
must prove its own endpoint does not wrap. ⚠ **That is the interesting half:
R3's residual over R4 is not the check R2 was paying, it is a check R2 did not
have.**

**R4 == R5 exactly.** `md5_fn 338505795ee18db952aafcdaec522df4`, 708 bytes, 200
instructions, both cells. The proof is free *including the writes*.

**R4 − `c-gcc` = −2.88 `Ir`/group, R4 − `c-clang` = +5.00.** ⚠ **Unsafe Rust
beats gcc C on this kernel and loses to clang C**, and the clang column is why
that must be stated as two numbers: rustc 1.97.1 and clang 22.1.6 share LLVM
22.1.6 exactly (`TOOLCHAIN.md`), so the R4-vs-clang gap is language and ABI,
while the R4-vs-gcc gap is two different compilers. `.memory/03-measurement.md`
rule 2 — *every C-vs-Rust claim needs the clang column* — decides the sign here.

**The C rungs carry ~150 `Ir`/call more FIXED cost than the Rust ones**
(232 / 163 vs 75 / 66). That is `php_shim_reset()`: it walks 11 size classes
every call (`PROTOCOL_PHP.md` §B1.3 requires it) where the Rust rungs only
allocate a `Vec`. It cancels in R1-vs-R1h and does **not** cancel in C-vs-Rust,
so it is subtracted out of the `Ir`/group column above and named here rather
than buried in it.

### 8b. ⭐ THE 2004 SAFETY CHECK HAS A NEGATIVE COST ON gcc, AND THE SIGN FLIPS ON clang

Per **line** (57 more lines on `large` than on `small`), the R1h−R1 delta is

```
gcc    (52712 - 7339) - (52914 - 7370) = -171  over 57 lines  =  -3.0 Ir/line
clang  (45250 - 6273) - (45051 - 6245) = +171  over 57 lines  =  +3.0 Ir/line
```

⚠ **Exactly ∓171, which is a coincidence of magnitude and not of mechanism.**
⚠⚠ **And it is ∓171 again after `TASK_PHP_015` changed both corpora** — the
figures above are new numbers over a new fixture and they land on the same two.

### ⚠⚠⚠ THE COMPLETE ACCOUNT: THE EPILOGUE SAVES **9**, THE NEW CHECKS COST **6**, NET **−3**

`TASK_PHP_014` M4: *"the arithmetic is right and I reproduce it two independent
ways, but the account is partial — only 5 of the 9 are named and the cost side
is never mentioned."* **Correct, and here is the whole of it.** It is done with
callgrind's **per-instruction** counts rather than by hand-tracing basic blocks,
because hand-tracing is what produced the partial account
(`.temp/php15/26-attribute.py`, `27-band.py`; alignment table in
`.temp/php15/28-alignment.md`).

The stable classifier is **execution frequency**, not instruction text: R1 and
R1h allocate registers differently, so a text diff shows dozens of
full-magnitude differences that cancel. On `small.bin` each call runs 9 line
iterations and 134 group iterations, so every instruction sits in exactly one
band:

```
band                               R1 Ir/line  R1h Ir/line     delta
inner loop (~14.9/line)               773.526      773.526    +0.000
per line  (~1/line)                    44.667       41.667    -3.000
per call  (~0.111/line)                15.556       15.111    -0.444
TOTAL                                 833.748      830.304    -3.444
```

⚠ **The inner loop cancels to +0.000** — 27 instructions in both
(`.temp/php15/25-loopcount.log`) — so the entire effect is the per-line band,
and it is **exactly −3.000**, not −3.0-ish. (`−3.444 × 9 = −31.0 Ir/call`, the
record's own `small` delta; the extra −0.444 is a per-call constant that does
not scale with lines and so does not appear in the marginal.)

**R1h ADDS 6 instructions per line** — three two-instruction tests:

```
cmp %edi,%r12d ; jl      <- HUNK 1, `len > src_len`
cmp %rsi,%r9   ; jb      <- HUNK 2, `ee > e`
cmp %rsi,%r8   ; jae     <- the inner loop's entry test, now UNCONDITIONAL
```

⚠ The third is the one a reader misses: R1 emits an entry test too, but only on
the non-45 path; R1h emits it on every line.

**R1h DROPS 9 instructions per line**, of which `NOTES.md` named five:

```
lea 0x2(%rbx),%rax ; cmp %rax,%rsi   <- the PREDICATE itself, computed and tested
setae %dl                             <- ) the five this section
test %dl,%dl ; cmove %r12,%rcx        <- ) already named:
test %dl,%dl ; cmove %rbp,%rax        <- ) select s += 4n / p += 3n, or neither
mov %r9,(%rsp) ; mov (%rsp),%r9       <- a SPILL/RELOAD pair R1h does not need
```

and two address computations **swap shape and cancel**: R1's single
`lea 0x3d(%rbx),%rsi` becomes `mov $0x3c,%esi ; add %r8,%rsi` (+1), while R1's
`lea 0x0(,%rax,4),%rcx ; add %rcx,%r8` folds into one `lea (%r8,%rsi,4),%r8`
(−1). **−9 + 6 + 1 − 1 = −3.**

⚠⚠ **SO THE CLAIM IS NOT "three instructions removed, −3.0 `Ir`", AND THAT
READING IS ARITHMETICALLY SEDUCTIVE AND WRONG.** It is a **9-instruction
structural saving partly refunded by a 6-instruction check** — a safety check
paying for itself by more than its own cost, which is a much stronger and much
more interesting claim than the coincidence it looks like. The same warning this
section already gives about ∓171 is owed to the 3-for-3 reading.

**Why the 9 go.** Without `ee > e`, gcc cannot prove the inner loop is entered
at all, so it must *select* the trip count rather than compute it — hence the
predicate, the `setae`, the two `test`/`cmove` pairs, and the extra live value
that forces the spill. With the check, the count is `(ee − s + 3)/4`
unconditionally and gcc emits straight-line arithmetic:

```
mov %r14,%rax ; sub %rbp,%rax ; add %rax,%rsi ; shr $0x2,%rsi ; add $0x1,%rsi
lea (%rsi,%rsi,2),%rax ; lea (%r8,%rsi,4),%r8 ; add %rax,%r10
```

`.temp/php13/14-mechanism.sh` (re-run byte-identically at
`.temp/php15/24-mechanism.log`) reports `setae+cmove count: 0` for R1h against
`3` for R1, and confirms the float survives to machine code in every C cell
(23 fp instructions in gcc's kernel, 20 in clang's).

⚠⚠ **The safety check paid for itself by handing the optimiser a fact it
otherwise had to branch around.** clang does not take that route and keeps the
check as a plain compare, which is the +3.0. **So "what does the upstream fix
cost?" has no single answer on this row: it is −3.0 `Ir`/line on gcc and +3.0 on
clang, and reporting either alone would be reporting a compiler.**

### 8c. What these numbers are NOT

- **not a bounds-check tax.** The kernel does four separable things per call —
  allocate, decode, fold, free — and only the middle two carry a check R4
  removes. §8a's `Ir`/group column is the decode+fold half; the fixed column is
  the other.
- **not a searched comparison.** §12 owes a `controls/spellings.py`. One
  spelling per rung is not a search of either endpoint (`PLAN_PHP.md` §5.3, the
  trap that has fired seven times), so **no ratio here is *the* cost of safety
  on this kernel.**
- **not wall-clock evidence.** `-O3 isolated` medians are 18.19 ms (`small`) and
  97.98 ms (`large`) for `c-gcc` at 30 reps on a shared box; the spreads are
  1.2 % and 6.4 %. They are recorded and are secondary
  (`.memory/03-measurement.md` rule 6). ⚠ The `large` spread is worse than the
  `small` one on every rung, which is what an 8.0 MiB working set on a shared
  box looks like; it is a reason to read `Ir` and not the clock, not a reason to
  re-run.

⚠ **`RECAP_PHP.md` open item 9 / F14: no php `Ir` is comparable to any PAT `Ir`,
and no two php runs are comparable to each other unless the env block matches.**
Nothing below is put next to a `pNN` number, in a table or in prose.

⚠ **This kernel is not a pure decode loop and its marginal `Ir` must not be read
as one.** Per call it does four separable things:

1. an allocation of `cap` bytes (C: `php_shim_emalloc` + the cache walk in
   `php_shim_reset`; Rust: `vec![0u8; cap]`, which also **zeroes** where
   `emalloc` does not);
2. the decode walk — the part the bound is about;
3. a Horner fold over `total_len` bytes;
4. a free.

(2) and (3) scale with the window; (1) and (4) do not. `work_per_call` is the
window, which is the only scalar `check.py::check_marginal_ir` can use and is a
strict over-estimate of the bytes touched.

---

## 9. ⚠⚠ THE FLOAT: A `harness/` LIMITATION FOUND BY THE FIRST ROW

`uuencode.c:141` is `(int) floor(len * 1.33)` and `:131` is
`ceil(src_len * 0.75) + 1`. Both are libm.

**`harness/build.py::build_c` links no `-lm`, and `build.py` is frozen** —
editing it costs a 33-pattern re-measure (`PLAN_PHP.md` §2.1). Measured,
`.temp/php13/01b-floor-runtime.log`:

```
gcc   -O0 -DSLB_ISOLATED   FAILED: undefined reference to `floor'
gcc   -O0 -flto            FAILED: undefined reference to `floor'
gcc   -O3 -DSLB_ISOLATED   built
gcc   -O3 -flto            built
clang -O0 -DSLB_ISOLATED   FAILED: undefined reference to `floor'
clang -O0 -flto            FAILED: ld.lld: undefined symbol: floor
clang -O3 -DSLB_ISOLATED   FAILED: undefined reference to `ceil'
clang -O3 -flto            FAILED: ld.lld: undefined symbol: ceil
```

**6 of 8 cells cannot link a verbatim libm call**, and the two that can are the
two where gcc happens to fold both. ⚠ **This is not specific to uudecode**: any
php kernel touching `math.h` hits it, and `ext/standard/math.c`,
`ext/standard/formatted_print.c` and the `pack`/`unpack` family all do.

**What this row does about it**, and it is a declared `provenance.deletions`
entry: `c/kernel.c` and `c/kernel_hardened.c` define

```c
static double php_uu_floor(double x) { double t = (double)(long)x; return t > x ? t - 1.0 : t; }
static double php_uu_ceil (double x) { double t = (double)(long)x; return t < x ? t + 1.0 : t; }
#define floor(x) php_uu_floor(x)
#define ceil(x)  php_uu_ceil(x)
```

They take and return `double` and are applied to the same `double` expressions,
so `len * 1.33` is still evaluated in binary64 and still truncated by `(int)`.
Only the rounding instruction's provenance changes. **Differential with a
must-fire control** (`.temp/php13/02-reach.log` Q1):

```
Q1 floor: php_uu_floor vs libm floor, len 0..63 : 0 disagreements
Q1 ceil : php_uu_ceil  vs libm ceil,  n 0..1e6  : 0 disagreements
Q1 CONTROL (trunc vs round-half-up), must be > 0 : 38 disagreements
```

`len` cannot leave 0..63 (`PHP_UU_DEC` masks with `077`) and `src_len` is the
window, so those two ranges are the whole reachable domain.
`PROTOCOL_PHP.md` §B2's rule — *"modelled by an equivalent builtin is a claim
that needs a DIFFERENTIAL TEST, not a comment"* — is why this paragraph carries
numbers.

**`TASK_PHP_013` §7.3 asked whether the float is reproducible across the eight
build cells. It is**: all eight C cells give byte-identical checksums on `small`
and `large` (`.temp/php13/05-crun.log`), the gate's own stage 2 agrees over all
32 cells, and the `floor` table hashes to `a422642e99c46107` on every cell that
links.

⚠ **And the claim is BOUNDED beyond `build.py`'s flag set rather than merely
asserted** — `.temp/php13/16-flagscope.sh`, output
`.temp/php13/16-flagscope.log`. `-ffast-math`, `-march=native`,
`-funsafe-math-optimizations` and `-Ofast`, on **both** compilers, all give the
same two hashes (`floor a422642e99c46107`, `cap cfbb5c674d75f9e6`) and **0**
disagreements against libm. ⚠ `-mfpmath=387 -m32` **was NOT measured**: this box
has no 32-bit target and the probe does not build. None of the five is in
`build.py`'s set, so **no flag scope needs stating** — but the one that could
have moved it is the one that was not run, and that is said here rather than
rounded off.

⚠⚠ **Verus has no `f64` arithmetic at all.** The float therefore cannot reach
R5 under any spelling, and R2–R5 use `(ln * 133) / 100`, exhaustively equal over
the domain. **The ladder's own tooling is what forces the substitution, not a
preference** — that is the reportable half.

---

## 10. TCB tally — five trusted items, counted individually

`.memory/04-verus.md`: every `external_body` item is TCB, not just the
interesting one. `grep -n 'assume\|external_body\|external\b\|assume_specification' verus.rs`
finds exactly these five, each justified in a comment above it:

| # | item | `ensures` | why it is trusted |
|---|---|---|---|
| 1 | `get_unchecked(v: &[u8], i)` | `r == v@[i]` | vstd ships no spec for `<[T]>::get_unchecked`. **Half the security argument**: five call sites — the length byte, and `buf[s..s+3]`. |
| 2 | `vget_unchecked(v: &Vec<u8>, i)` | `r == v@[i]` | the destination read in the final fold. |
| 3 | `vset_unchecked(v: &mut Vec<u8>, i, x)` | `final(v)@ == old(v)@.update(i, x)` | **the other half.** The `ensures` is the WHOLE post-state, not `v@[i] == x`: a wrapper naming only the written element would let a body that also clobbered `v[i+1]` through every Verus stage (`.memory/04-verus.md`'s most dangerous vacuity mode). |
| 4 | `load_input()` | none | file I/O. An `ensures` here would be an axiom about a file's contents. |
| 5 | `emit(acc)` | none | `println!` is not verifiable. |

Three of the five carry an `unsafe` body or a non-empty `ensures`, so three get
**verified twins** (`slb_twin_get_unchecked`, `slb_twin_vget_unchecked`,
`slb_twin_vset_unchecked`), which is why `twin_obligations` is 28 against 25.

**Obligation counts, run:** `25 verified, 0 errors`; `--cfg slb_twin`:
`28 verified, 0 errors`.

⚠ **What the twins buy here, honestly.** `get_unchecked`'s twin is the same
single-clause `i < v@.len()` p01, p02 and p16 ship, so its passing is not
evidence that anything hard was checked. **`vset_unchecked`'s twin is the new
one**: `v.set(i, x)` in checked code is what forces the `update` `ensures` to be
the whole post-state rather than a point assertion, and it is the first
*writing* trusted accessor in either programme.

---

## 10a. Trusted items — the arguments no oracle can make

`harness/check.py` stage `5c-twin` requires one written argument per trusted
item, for the three things no stage of the gate can judge. It prints them and
fails without them; **only a human can judge them.**

SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)`; the twin's body is `v[i]`. The standard
library documents `get_unchecked(i)` as `index(i)` with the bounds check
removed, so it is the same operation on the same slice at the same index, and
Verus checks the bound `v[i]` needs against the same `requires`. A defensive
twin — `if i < v.len() { v[i] } else { 0 }` — cannot satisfy the `ensures` and
fails the stage rather than passing it.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes *as the body stands*: one expression, one unchecked read,
at index `i` of slice `v`, and `ensures r == v@[i as int]` names that index and
that slice. ⚠ **Nothing mechanical enforces it.** A second unchecked read the
`ensures` never mentions — `let _peek = *v.get_unchecked(i + 1);` — is invisible
to 5a, 5c, 5c-req and 5c-twin alike. Two backstops, both tests rather than
proofs: stage 3c identity catches it if the extra read is added to `verus.rs`
alone (the O3 pin is `exact`), and Miri catches it if it is added to
`unsafe.rs` too — **but only on an input that reaches the boundary.** ⚠ On ph03
that input is `adversarial-read.bin`, whose whole point is that the walk runs
off the end; the boundary is reached on every one of its 8 calls. Read the body,
every time.

(c) **Does the clause mean the same in both configurations?** Yes. `i < v@.len()`
mentions only `i`, `v` and vstd's `@`/`len()`, and `v: &[u8]` / `i: usize` are
concrete types with no generic or associated item that a `#[cfg]` could
redefine. The gate additionally forbids the token `slb_twin` anywhere in the
file except each twin's own `#[cfg(slb_twin)]`.

SLB-TRUSTED-ARGUMENT verus.rs vget_unchecked

(a) Yes, and it is `get_unchecked`'s argument with `&Vec<u8>` in place of
`&[u8]`: the unchecked operation is `*v.get_unchecked(i)` reached through
`Vec`'s `Deref<Target = [T]>`, and the twin is `v[i]`, which is `Vec`'s
`Index` — documented as the slice index. ⚠ **It is a separate item rather than a
reuse of item 1 for a real reason**: `dest` is a `Vec` the kernel owns and
`buf` is a borrowed slice, and passing `dest.as_slice()` to item 1 would put a
`Deref` call between the proof and the store loop that R4 does not have, which
would break the `exact` identity pin.

(b) Yes as the body stands — one expression, one unchecked read at `i`, and the
`ensures` names it. Same residual and same two backstops as item 1.
⚠⚠ **THIS PARAGRAPH USED TO SAY `total_len == p` ON EVERY BENIGN WINDOW AND
`TASK_PHP_015` MADE THAT FALSE — deliberately, and it is the whole point of the
fixture change.** Under the short-final-line corpus `total_len < p` on **22 of
32** `small` windows and **1 367 of 2 050** `large` ones (`inputs/gen.py`'s
`_check_span` prints the counts on every run), so the final fold now stops
*short* of the highest byte the decoder wrote on most windows. **The backstop is
weaker for it and that is worth saying rather than papering over**: the last
`vget_unchecked` of a benign call reads `dest[total_len - 1]`, not
`dest[p - 1]`. What still reaches the accessor's real boundary is the equality
case, which `_check_span` REFUSES to let the corpus lose — 10 `small` windows
and 683 `large` ones — plus `adversarial-*`, where the fold runs to a
`total_len` the decoder never wrote. ⚠ **That is the fixture rule paying for
itself in the other direction**: the same assertion that forces the strict case
in is what stops the equality case being dropped.

(c) Yes; identical reasoning to item 1.

SLB-TRUSTED-ARGUMENT verus.rs vset_unchecked

⚠⚠ **This is the project's first WRITING trusted accessor, in either
programme, and its three answers are not item 1's with the word "write"
substituted.**

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked_mut(i) = x`; the twin's body is `v.set(i, x)`,
vstd's checked `Vec` store, whose own `requires` is `i < old(v)@.len()` — the
same bound, checked. ⚠ **The wrong stand-in here would be `v.push(x)`**: it
satisfies no `update` postcondition and would fail, which is what the stage is
for.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** ⚠⚠ **This is where a write wrapper is harder than a read
wrapper, and it is why the `ensures` is the shape it is.** For a read, an
incomplete `ensures` under-describes the *result*; for a write it
under-describes the *heap*. `ensures v@[i as int] == x` — the obvious spelling —
says nothing about `v@[i + 1]`, so a body that also clobbered the next byte
would satisfy it, satisfy the twin, and pass every Verus stage. The shipped
clause is therefore the **whole post-state**:

```
ensures final(v)@ == old(v)@.update(i as int, x)
```

which pins every element of `v`, not one, and forces the twin to perform exactly
one store at exactly `i`. **That closes (b) mechanically for the extra-write
case** — the case item 1 can only mitigate with tests. It does **not** close the
extra-*read* case: a body that also read `v[i + 1]` before storing would still
satisfy this postcondition, and the same two backstops (identity `exact`, Miri
on a boundary-reaching input) are all there is. Read the body.

(c) **Does the clause mean the same in both configurations?** Yes.
`i < old(v)@.len()` and `final(v)@ == old(v)@.update(i as int, x)` mention only
`i`, `v`, `x`, `old`, `final` and vstd's `@`/`len()`/`update`; `v: &mut Vec<u8>`,
`i: usize` and `x: u8` are concrete. ⚠ `old`/`final` are the pinned Verus's
required spelling for a `&mut` parameter in a postcondition (writing `v@` alone
is a hard error at this version), and they mean the same thing under
`--cfg slb_twin` because the twin has the same signature.

⚠ **On `x` being unconstrained**, which stage `tcb-unsafe` requires a
declaration for: see `verus.unsafe_justifications` in `spec.md`. Short form:
`x` is a pure value, every `u8` is a legal byte to store, the *indexing*
parameter `i` **is** constrained, and the `update` postcondition is what makes
leaving the value free safe.

SLB-TRUSTED-ARGUMENT verus.rs load_input

(a) There is no twin and none is required: `load_input` is `external_body` with
**no `ensures` and no `unsafe`**, so it falls outside the trusted-item regime,
which `.memory/04-verus.md` keys on `external_body` + (a non-empty `ensures`
**or** `unsafe`). That is the correct boundary rather than a loophole — an item
that asserts nothing cannot axiomatise a falsehood.
(b) Vacuously complete: there is no `ensures` to be incomplete. ⚠ **The price is
real and is stated rather than hidden**: every fact the proof needs about the
input is re-derived at run time inside verified code from `bytes.len()`, which
is why the driver's window bound is proved and not assumed.
(c) No clauses, nothing to differ.

SLB-TRUSTED-ARGUMENT verus.rs emit

(a) No twin required, for the same reason as `load_input`: `external_body`, no
`ensures`, no `unsafe`. `println!` is not verifiable at this Verus.
(b) Vacuously complete.
(c) No clauses. ⚠ It is still TCB and is still counted in §10 — the pilot was
published as *"one 3-line wrapper"* when the true tally was three items, one of
which was `main`.

---

## 11. ⚠⚠ `TASK_PHP_013` §7.1 — WHICH `spec.md` PINS MEAN SOMETHING DIFFERENT FOR AN EXTRACTED KERNEL

The manager named this as the call it was least sure of: *"`spec.md`'s
machine-readable pins were designed for INVENTED PAT kernels. Some may be
meaningless for a row whose C came out of a tarball. Tell me which, rather than
inventing a value."* Item by item, and **none of them turned out to be
meaningless — but three change what they MEAN**:

| pin | verdict for an extracted row |
|---|---|
| `requires` / `ensures` | ✅ **unchanged.** The precondition is structural and the postcondition is a value; neither cares where the C came from. |
| `verus.obligations` / `items` | ⚠ **unchanged, and NOT a measure of spec strength.** 25/28 here, and the count pins the SHAPE of the file, not the proof. `TASK_PHP_014` §1.3 measured that **`25 verified, 0 errors` survives deleting the entire functional postcondition AND its consumer**, so a reader who takes 25 as evidence for *"a full functional postcondition"* is reading a coincidence. What pins the strength is `verus.items.verus.rs.kernel.ensures`, which carries the clause text — and what DEMONSTRATES it is mutation: 19 mutants, 17 killed, every byte-level one (shift, mask, source index, destination index, capacity ±1, Horner multiplier, step size, `total_len`). It happens to be a full functional postcondition; **not because of the 25**. |
| `driver.canonical` | ✅ **unchanged.** The driver is ours in both programmes. |
| `collapse` | ✅ **unchanged.** |
| `identity` | ✅ **unchanged** — and it is a *result* here: **`exact` at O3 and `differ` at O0**. ⚠⚠ **The shipped pin at O0 is `differ`, NOT `norel`, and it was NOT measured before it was declared** — this cell said both of those things until `TASK_PHP_015` (`TASK_PHP_014` M3) while §0 of this same file, in bold, says `norel` was pinned from a hand build and **the gate refuted it**. `PROTOCOL.md` rule 13 exactly: the detail got maintained and the summary 700 lines below it did not. Re-confirmed against the `TASK_PHP_015` record: O3 both cells `md5_fn 338505795ee1…`, 200 instructions, 708 bytes; O0 **335 vs 352 instructions, 1906 vs 2042 bytes**, `md5_fn_norel` `d1d6e3b49ff2…` vs `75ad2b1a5964…`. |
| `miri` | ✅ **unchanged**, and *more* load-bearing than on p16 because this row has a **writing** trusted accessor. |
| ⚠ `idiom.required` | **CHANGES MEANING.** On a PAT row it says *"this is the spelling we chose and every rung must keep it"*. Here it also says *"**this is what the tarball said**"* — `(int) floor(len * 1.33)` is `required` not because it is a good idea but because it is what `:141` contains, and the row would be a different program without it. A reviewer must read these as **provenance assertions**, checkable against `extract_sha256`, and not only as style. |
| ⚠⚠ `idiom.forbidden` | **CHANGES MEANING, AND IS THE SHARP ONE.** Every entry here forbids something that would be an *improvement* in any other row: `len = total_len - (p - *dest)` **fixes** a precedence bug; `(3 * src_len + 3) / 4` is the arithmetic the comment itself calls the obvious form. On a PAT row `forbidden` excludes a cheat; here it excludes a **repair**, and a reviewer who applies PAT's reflex will read the list backwards. |
| ⚠⚠ `model.py` | **CHANGES MEANING, AND THIS ROW HAS NOW PAID FOR IT TWICE.** On a PAT row the model is an independent implementation of a spec both it and the kernel are written from. Here **there is no spec** — the C is the spec — so `model.py` is an independent *reading of the tarball*, and its two implementations disagreeing means one of them mis-read PHP, not that one has a bug. That is why `selfcheck()` also re-derives `line_len` **from the float** and re-checks `:158`'s deadness per window: those are readings, not choices. ⚠⚠⚠ **AND IT IS WHY THE DOMAIN THE READINGS ARE COMPARED OVER IS PART OF THE PIN.** Both of this row's modelling errors — the `ee + 1` resume point and the `total_len` prefix (§13) — were *mis-readings of PHP* that the shipped corpus agreed with, and neither was findable from `inputs/`. `selfcheck()` now builds 896 synthetic windows spanning `ln = 0..63` and `inputs/gen.py` asserts the corpus reaches both arms of `:141`. **On an extracted row, "two independent implementations" is worth exactly as much as the domain you run them over.** |
| ⚠ `sanitizer_expect` | **NARROWER THAN IT LOOKS**, see §5d. It is per-input for R1 and structurally `clean` for R1h, which forbids a php row from shipping the evidence that its `fix_commit` is incomplete. |

**Nothing had to be invented to fill a field.** The two fields that could have
been are `cwe` (the corpus disagrees with itself — §4 records both and picks the
one the write supports, with the reason) and `uses_allocator` (declared `true`,
with the confirmation that no truncation fires — §7).

---

## 12. What is NOT here

- **No `controls/spellings.py`.** `PLAN_PHP.md` §5.3 asks for a re-derivable
  search of both endpoints before a rung difference is published. This row
  ships one alternate spelling per Rust rung by construction (R2 indexes, R3
  reslices, R4 unchecks) and **has not searched either endpoint further**. No
  R2-vs-R4 figure in §8 should be quoted as *the* cost of safety on this kernel
  until that search exists. Named as owed.
- **No `sweep-*` band.** `work_per_call` moves between `small` and `large` (556
  vs 4090, different residues mod 4/8/16), which is what
  `check.py::check_marginal_ir` needs, but there is no length sweep and
  therefore no law in `nlines` or in `cap`. ⚠ **`TASK_PHP_015` is as close as
  this row has come to one and it is not a substitute**: re-measuring over a
  second, differently shaped corpus reproduced every marginal to two decimals
  (§8), which is a *replication at two points*, not a curve through many.
- ✅ **`c/kernel.c`'s `harness/build.py:161-165` line citation is FIXED**, and
  the way it was fixed is the point. `TASK_PHP_013` left it deliberately: the
  gate shouts it (`doc-citation-other`) and explicitly does not fail it, and
  `c/kernel.c` is measurement-hashed, so re-citing cost a re-measure the row did
  not otherwise owe. The shout's own advice is *"cite the FUNCTION when one of
  these files is next re-measured anyway"* — and `TASK_PHP_015` re-measured
  anyway, so it now reads `harness/build.py::build_c` at no marginal cost.
  ⚠ **That is `PROTOCOL.md` rule 6's "batch every rung-source doc fix into ONE
  pass" working as designed**, and the same pass carried `verus.rs`'s
  "Four call sites" over a list of five and `c/kernel_hardened.c`'s two wrong
  hunk spans. ⚠ The shout also names three pre-existing line citations inside
  `common-php/emalloc_shim.h`, which are not this row's.
- **No claim about `php_uuencode`.** `:68-124` is in the same file and is not
  extracted; `inputs/gen.py` re-implements the encoder in Python instead, so the
  blobs are genuine uuencodings and the benign case is a real round trip.
  ⚠ Since `TASK_PHP_015` the re-implementation includes the **padding case**
  (`:110-115`), which is what a short final line needs and which the earlier
  version called *"dropped"*.
- ⚠⚠ **`provenance.c_lines` PINS ONE SPAN AND THIS ROW LIFTS TWO** — the only
  `TASK_PHP_014` finding left unlanded, and it is left deliberately.
  `harness-php/provenance.py:711-714` requires `c_lines` to be `[a, b]`
  integers, so `extract_sha256` covers `uuencode.c:126-171` and **not**
  `PHP_UU_DEC` at `uuencode.c:66`, which both C rungs also lift
  (`c/kernel.c:122`, `c/kernel_hardened.c:110`). It is byte-correct — checked by
  hand against the tarball, twice — but the check that exists to make *"those
  lines of that tarball hash to this"* a **one-command fact** cannot see it, and
  it is not in the overlap denominator either. ⚠ **This is a schema limit that
  ninety rows will meet**: most extracted kernels need a macro, a struct or a
  constant from outside their function.
  **The fix the reviewer proposes is right** — let `c_lines` be a list of
  `[a, b]` spans and hash their concatenation, backward-compatibly. **It was not
  taken here**, and the reason is that it changes the ENFORCED half of the only
  provenance check there is (`PROTOCOL_PHP.md` §D: *"`c_file` in the manifest,
  the span in range, `extract_sha256` — those are not heuristics"*), on the row
  whose provenance claim is load-bearing, inside a task already carrying a
  fixture change and a re-measure. **A schema decision for 90 rows deserves its
  own task and its own reviewer.** Named as owed with the design attached, not
  quietly dropped.
- ⚠ **The gate record still carries no `provenance` and no marker on
  `sanitizer_hardened`.** `TASK_PHP_014` m6: a machine consumer reading the
  record's four `expect: clean, fired: false` adversarial rows, and nothing
  else, would conclude the 2004 fix is complete. A human cannot — `idiom.why` is
  echoed and rendered and now says so in terms (§0) — but closing it properly
  needs `check.py` to echo `provenance` or to carry a per-row note beside
  `sanitizer_hardened`, and that is a `harness/` edit and a 33-pattern re-gate.
  **Named as owed, not fixed.**

---

## 13. ⚠⚠⚠ THE FIXTURE WAS A MONOCULTURE, AND IT HID A REAL DEFECT FOR A TASK

**This is the finding `TASK_PHP_015` exists for, and it is a SHAPE defect: it is
about how a row is built, not about uudecode.** `TASK_PHP_014` M1 found it.

### What was wrong

`spec.md`'s `note` — **inside the hashed contract** — said `model.py::uu_fold`
mirrors `verus.rs`'s `uu_walk`/`fold_line`. It did not:

| | folds |
|---|---|
| `verus.rs:215-223` | `fold_bytes(w.0, w.1, 0)` — the **first `total_len`** emitted bytes |
| `model.py` (as shipped at `TASK_PHP_013`) | **every** emitted byte |

Those are the same sequence only when `total_len == p`. The row's own
`lemma_emit_covers_declared` proves `ln <= 3·⌈line_len(ln)/4⌉` and `verus.rs:47`
records that equality holds **only at multiples of 3** — so the row's own Verus
lemma documents that its model's stated justification was false, and the
inequality is **strict for 42 of the 63 length bytes**.

⚠ **It passed for exactly one reason.** `inputs/gen.py` emitted `LINE_LEN = 45`
on every line of every blob and called the padding case *"dropped"*, and
`45 ≡ 0 (mod 3)` is the equality case. So `harness/check.py`'s
`ensures re-derived independently on N sampled calls` — the green line that is
supposed to tie the gate to R5's postcondition — **was re-deriving a different
postcondition**, correctly, on a corpus that could not tell the difference.

⚠⚠ **And the mechanism was already named in this row's own build report, eleven
lines above a second instance of it.** `TASK_PHP_013_REPORT.md` §6 records a
*different* modelling error in the *same function* — a walk resuming at `ee + 1`
— found "by writing the Verus termination argument, not by any test", and says
why no test could find it: *"it agrees with the simulation on every input this
row ships, because every shipped line declares 45."* **The diagnosis was right
and the repair was local.**

### What was done, and why it is two repairs and not one

1. **`model.py::uu_fold` now folds `out[:total_len]`**, mirroring `verus.rs`.
   Verified against an independent transcription of `verus.rs`'s three spec
   functions over `ln = 1..63`: **0 of 63 disagree**, where the shipped version
   gave **42 of 63** (`.temp/php15/01-prefix-divergence.log`,
   `04-postfix-divergence.log`). And against the *binaries*: on a window
   declaring `ln = 1`, `_window`, `uu_fold` and all five shipped rungs now agree
   on `152010033`, where `uu_fold` alone used to say `154280600`
   (`.temp/php15/05-real-divergence-postfix.log`).
2. **`model.py::selfcheck` builds its own domain.** 896 synthetic windows in
   three families spanning `ln = 0..63` — a single line with slack, a line at
   the buffer's edge (both refusal paths), and `45 → ln` chains (the only shape
   in which the resume point is exercised at all). **Must-fire and
   must-NOT-fire controls, `.temp/php15/03-sweep-mustfire.log`:**

   ```
   SHIPPED    (control)       MUST NOT fire  -> silent     0/896   ok
   all_bytes  (the M1 bug)    MUST fire      -> FIRED    294/896   ok
   nofold                     MUST fire      -> FIRED    440/896   ok
   resume_ee                  MUST fire      -> FIRED     65/896   ok
   srclen_e                   MUST NOT fire  -> silent     0/896   ok
   ```

   ⚠ It kills **both** of this row's modelling errors, including the one
   `TASK_PHP_013` could only find by writing a termination proof.
3. **`inputs/gen.py` emits a short final line** — which is also what
   `php_uuencode` really emits, so the monoculture was *unfaithful* as well as
   blind — and **asserts the span it exists to provide**. `_check_span`
   re-decodes what it generated and refuses to write a corpus missing the
   `floor()` arm, the strict case `declared < emitted`, or the equality case
   `declared == emitted`:

   ```
   span ok: small.bin   windows=32    floor()-arm lines=32    declared<emitted=22    declared==emitted=10
   span ok: large.bin   windows=2050  floor()-arm lines=2050  declared<emitted=1367  declared==emitted=683
   ```

⚠⚠ **(3) IS LOAD-BEARING AND NOT MERELY TIDIER, AND THAT WAS MEASURED**
(`.temp/php15/08-fixture-mustfire.log`). Re-installing the pre-fix `uu_fold` and
running **only** the corpus half of `selfcheck`:

```
                          OLD corpus (45-only)   NEW small.bin   NEW large.bin
PRE-FIX uu_fold                 silent               FIRES           FIRES
SHIPPED uu_fold                 silent               silent          silent
```

**The old corpus could not see the defect; the new one catches it without the
synthetic sweep at all.**

### ⚠⚠⚠ The rule, and it is `PROTOCOL_PHP.md` §A2a now

> **1. The fixture must REACH every arm of the branch the defect lives on, and
> `inputs/gen.py` must ASSERT that it does** — in the shape `_check_residues`
> already had. An intention in a comment is what this row had.
>
> **2. `model.py::selfcheck` must drive its two implementations over a domain it
> CONSTRUCTS, not only over the calls the corpus makes.** A second
> implementation is only as strong as the domain it is exercised over, and
> `inputs/` is not a domain — it is seven files.

⚠ **Neither subsumes the other.** (1) is bounded by what a window of fixed
stride can carry — a corpus cannot span `ln = 1..63` and keep `work_per_call`
constant — so it buys *reachability*, not coverage. (2) buys coverage and buys
it free, but it checks the **model** and cannot see a *measurement* taken down a
path nothing executes.

⚠ **The manager's first phrasing was *"the generator must span the parameter
that selects the code path"*, and it does not quite generalise**: "span" is not
achievable inside a fixed stride, and it names the fixture as the only repair
when the cheaper and stronger one is in the model. Checked against `ph07` before
being written down — `mbfl_strcut` walks `p += mbtab[*p]`, so its arms are the
lead-byte classes and an all-ASCII benign corpus takes exactly one of them,
which is this defect with a different name. The rule carries; the word
*parameter* did not.

## 14. ⭐⭐ `inside_share` PER CELL — MEASURED, NOT ASSUMED

`TASK_PHP_058`. This row published an `A1` headline with **no
`inside_share` measured anywhere in it** (`RECAP_PHP.md` **F127**: five built
rows had none, three of them publishing `A1`). `controls/inside_share.py` —
byte-identical to the copies in `ph16`, `ph29` and `ph97`, pinned, seven
must-fire arms — measures every cell. `n_iters` is **read from each input's own
header** (`common-php/slb.py`): 25000 on `small.bin`, 20000 on `large.bin`.

    inside_share = 100 x A1 / W,  W = callgrind's own `summary:` total, same run

⚠⚠ **A SECOND QUANTITY WEARS THIS NAME.** `F74`'s is
`(kernel_exclusive_ir / n_iters) / marginal_ir_per_call` — a slope, not a run —
and it is the one every figure in `RECAP_PHP.md` and `.memory-php/02-ladder.md`
quotes. The two differ; `.tasks-php/php58_record_share.py` computes the F74 one
for this row from the committed records. **Say which you mean.**

| cell | `small.bin` A1/call | share | `large.bin` A1/call | share |
|---|---:|---:|---:|---:|
| `c-gcc` | 7369.72 | **97.93 %** | 52913.94 | **99.18 %** |
| `c-clang` | 6244.69 | **97.63 %** | 45050.94 | **99.05 %** |
| `c-gcc-h` | 7338.72 | **97.92 %** | 52711.94 | **99.18 %** |
| `c-clang-h` | 6272.69 | **97.64 %** | 45249.94 | **99.06 %** |
| `safe_naive` | 9363.69 | **95.12 %** | 68632.94 | **95.03 %** |
| `safe_tuned` | 7648.34 | **94.09 %** | 55973.94 | **93.97 %** |
| `unsafe` | 6817.38 | **93.41 %** | 49897.94 | **93.29 %** |
| `verus` | 6817.38 | **90.13 %** | 49897.94 | **93.34 %** |

⚠ **EIGHT INDEPENDENT PER-CELL RATIOS, NOT A COMPARISON.** Both C columns are
present so that no reader takes it for one.
⚠ `whole` cells are absent because the ratio is **undefined** there, not 100 %:
at `O3`/`whole` the kernel is inlined into `main`, and this row's own
measurement record carries `kernel_exclusive_ir: null` for all eight of those
cells on both inputs — 16 entries, measured, not assumed.

⭐ **THE ONE CELL THAT MOVES, AND IT IS A KNOWN RESULT ARRIVING BY A NEW ROUTE.**
`verus`/`small.bin` reads **90.13 %** against `unsafe`'s **93.41 %** while their
`A1/call` is **identical to the digit** (6817.38) and `spec.md` pins the two
kernels byte-identical. The difference is entirely in the denominator: the
`verus` binary's whole-run total is **182 455 030 → 189 103 077 Ir, +3.64 %**.
That is `F74`'s family-B null, whose corpus maximum is *"`+3.652 %`
(`ph03`/`small`)"* — **this cell** — reproduced here from the run total instead
of from the marginal. ▶ **A1's null on that pair is `0.000 %` and the
whole-program column's is 3.6 pp: the share matrix shows WHY, on the row that
owns the corpus maximum.**

⛔ **A HIGH SHARE IS NOT A CERTIFICATE** (`RECAP_PHP.md` F109): `ph55`'s C cells
sit at 74–83 % and A1 still read `0.000 %` on that row's own defect site,
because the defect lived in an uninlinable callee. What decides a statistic is
whether **the DIFFERENCE** lands inside the symbol, not the level. ▶ Applied to
this row under `F74`'s two-condition rule (`.memory-php/02-ladder.md`;
(ii) `|Δinside_share| ≤ 0.02`), at `O3/isolated`, both inputs:

> ⛔⛔ **READ THE QUANTITY, AND READ WHAT *"PASS"* MEANS — BOTH WERE CORRECTED
> AT `TASK_PHP_059`.** The Δ column below is **`F74`'s** share
> ((`kernel_exclusive_ir`/`n_iters`) / `marginal_ir_per_call`), **not** the `W`
> one this row's `controls/inside_share.py` computes; two quantities wear the
> name and they differ by **8.9 pp on `ph29`** and **0.01 pp on `ph45`**
> (`F129`). ⛔ **And *"PASS"* IS NOT *"LICENSED"*: `F74`'s two conditions are
> NOT A GATE** — `.memory-php/02-ladder.md` says *"NO FUNCTION OF THE SHARES CAN
> CERTIFY A AT ANY THRESHOLD"*, and `_059` measured the conjunction **admitting**
> `ph55` `c-gcc` vs `c-gcc-h` where A1 reads `+0.0000 %` against 66.14 `Ir`/call.
> ▶ **Read a PASS as *"A1 and the whole-program column are in the regime where
> they are expected to AGREE"*, never as permission to publish one alone.**

| pair | `small.bin` Δshare (**`F74`'s**) | `large.bin` Δshare (**`F74`'s**) | rule (ii) |
|---|---:|---:|---|
| §8b's headline, `c-gcc` vs `c-gcc-h` | 0.0001 | 0.0000 | **PASS** |
| `c-clang` vs `c-clang-h` | 0.0001 | 0.0000 | **PASS** |
| `safe_tuned` vs `unsafe` (the `fixed-R4 bound`) | 0.0066 | 0.0067 | **PASS** |
| `safe_naive` vs `safe_tuned` | 0.0100 | 0.0104 | **PASS** |
| `unsafe` vs `verus` (the null) | **0.0330** | 0.0005 | **FAIL** (small) |
| `c-gcc` vs `safe_naive` | 0.0277 | 0.0417 | **FAIL** |
| `c-clang` vs `safe_naive` | 0.0248 | 0.0406 | **FAIL** |

✅ **This row's own R1-vs-R1h headline and its `fixed-R4 bound` both PASS**, and
they are same-language pairs, which is where `PROTOCOL_PHP.md` §B1a and F89 both
say the confounds cancel. ⛔ **Its CROSS-LANGUAGE pairs FAIL (ii) on both C
columns and both inputs** — so an `A1` C-vs-Rust figure from this row needs the
same qualification `ph29` §15 gives its own.
⚠⚠ **AND THE NULL PAIR FAILING ON `small.bin` IS A FACT ABOUT THE RULE, NOT
ABOUT THE ROW:** `unsafe` vs `verus` is the one comparison whose true A1
difference is **known to be exactly 0**, and (ii) rejects it — because the
+3.64 % sits in the denominator. ~~**Reported, not repaired: whether F74's rule
should exempt an `identity`-pinned pair is the manager's to rule on.**~~

> ✅✅ **RULED AT `TASK_PHP_059`, AND THIS PARAGRAPH WAS RIGHT ABOUT SOMETHING
> BIGGER THAN IT CLAIMED. NO EXEMPTION IS NEEDED, BECAUSE THE RULE WAS NEVER A
> GATE.** A condition that rejects a pair whose true A1 difference is *known to
> be exactly zero* is not a filter that needs an escape hatch — **it is a filter
> being read as something it is not.** ⭐ The two conditions describe **when A1
> and the whole-program column are expected to agree**; they never licensed or
> forbade a publication, and `.memory-php/02-ladder.md` has said so all along
> (*"NO FUNCTION OF THE SHARES CAN CERTIFY A AT ANY THRESHOLD"*).
>
> ⛔⛔⛔ **AND THE MANAGER OWES THIS PARAGRAPH AN APOLOGY IT CANNOT READ.** It was
> written here, addressed to the manager, and **routed to him for a ruling** —
> and he did not rule. He then published, in `F129`, that a `ph29` comparison was
> ***"INADMISSIBLE on the row's own written bar"***, which is exactly the
> gate-reading this paragraph is a counterexample to. ⭐⭐ **`TASK_PHP_059`
> refuted that with a `ph55` pair; THIS ROW HAD AN INDEPENDENT COUNTEREXAMPLE ON
> FILE FIRST, AND IT WAS SITTING IN THE MANAGER'S OWN INBOX.**
> ▶ **A question routed to the manager and never answered is not neutral — it
> becomes a claim he is free to contradict without noticing.** (`F123`'s law:
> an engineer's own uncertainty may be DEFERRED but not DOWNGRADED.)
