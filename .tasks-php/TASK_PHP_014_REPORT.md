# TASK_PHP_014_REPORT — adversarial review of `ph03`, the template row

**Role:** research reviewer. **Under review:** `patterns-php/ph03-uudecode-bound/`
(all six rungs, `spec.md`, `model.py`, `controls/`, records),
`.tasks-php/TASK_PHP_013_REPORT.md`, and `RECAP_PHP.md` F29–F32.

**Verdict in one line: the row is real work and its headline survives every
attack I could mount — but its *oracle* is checking a different function from
the one R5 proves, and `RECAP_PHP.md` has landed one false refutation as a
finding. Neither invalidates a published number; both get copied.**

Scratch: `.temp/php14/`. Nothing outside it was written; `git status` is clean at
the end and at every plant/restore boundary.

---

## §0 The bracket

**Open** (first two commands of the task):

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/gate/ph03-uudecode-bound.json      33 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)
FRESH       results/ph03-uudecode-bound.json           19 source(s) + 6 input(s)
4 record(s) examined, 0 STALE
```

**Close** (last two commands): identical — `66 record(s) examined, 0 STALE` and
`4 record(s) examined, 0 STALE`.

```
$ git status --porcelain
$                                  # empty: clean
$ sha256sum patterns-php/ph03-uudecode-bound/{verus.rs,model.py,spec.md,NOTES.md}
844f1c6374a1…  verus.rs      5199c69876323…  model.py
80f42258d40d…  spec.md       a19502401684…  NOTES.md
```

⚠ **`TASK_PHP_013_REPORT.md` §12.3b said *"the closing bracket itself dirties the
tree"* (+59 lines to `results-php/preflight/_norow.preflight.json`). It did
not.** I ran the php bracket **twice** and the tree stayed clean. The mechanism
is `PROTOCOL_PHP.md` §E's *"identical runs collapse on **content**"*: a run whose
`harness_php_sha256` + manifest hash + flags match a recorded entry adds nothing.
`TASK_PHP_013`'s runs dirtied it because the harness content was moving under it.
**The bracket is read-only on a settled tree** — see m5.

I **did not** run a full `gate.py <row>` (~24 min). It rewrites
`results-php/gate/<row>.json` and `results-php/tables/`, both committed, under a
review whose whole point is that the manager is not committing. The committed
gate record reads `verdict: PASS, failures: 0` and both `--check-stale` brackets
say every source still matches it, which is the evidence available without
writing.

---

## §1 PRIMARY TARGET — is R5's postcondition actually strong? **YES.**

### 1.1 What the `ensures` constrains, clause by clause

There is exactly one, `verus.rs:545-546`:

```rust
requires  off + len <= buf@.len()
ensures   r == uu_fold(buf@, off as int, len as int)
```

`uu_fold` (`verus.rs:215-223`) is **not** a length assertion and **not** a
no-panic assertion. Unfolded:

| layer | what it pins |
|---|---|
| `uu_walk` (`:162`) | the *whole line chain*: which byte is read as `ln`, the `ln == 0` stop, both 2004 refusals, where the walk resumes (`s + 1 + 4*nsteps(fl) + 1`, **not** `ee + 1`), and the `ln < 45` / `s_end >= e` stops |
| `fold_line` (`:136`) | the 4-character group loop **including the 2014 refusal** `e - s < 4` |
| `grp` (`:114`) | the three emitted bytes, **shift by shift and mask by mask** |
| `fold_bytes` (`:204`) | Horner-31 over the first `total_len` emitted bytes |
| `tally_of` (`:108`) | the allocation size, as `(cap+7) & ~7` |
| `cap_of` (`:96`) | `n - n/4 + 1` |

So the postcondition **pins the decoded bytes**, not the length. The report's
phrase *"a full functional postcondition"* is **earned**, and I could not break
it. Evidence below.

### 1.2 Mutation testing — 19 mutants, 17 killed, both survivors explained

`.temp/php14/mutate.py`, `mutate2.py`, `mutate3.py`; logs `01-mutants.log`,
`02-mutants2.log`. Every mutant is written into the row directory (Verus's
crate-name rules need it there), run, and deleted in a `finally:`; the harness
prints `verus.rs`'s sha256 before and after and `git status --porcelain
patterns-php/` at the end. Baseline first:

```
$ ./verus_run.py .temp/php-root/patterns/ph03-uudecode-bound/verus.rs
verification results:: 25 verified, 0 errors
```

```
verus.rs sha256 BEFORE  844f1c6374a122166c4f59a573a22b003e6580aab9783c306ac3758334cfea91
mutant        result                                    what it breaks
shift1        24 verified, 1 errors  assertion failed   dec(b0) << 2  ->  << 3
shift3        24 verified, 1 errors  assertion failed   drop b3 from the group's last byte
mask          24 verified, 1 errors  postcondition      PHP_UU_DEC's 077 -> 0177
srcidx        24 verified, 1 errors  invariant          read b1 twice instead of b2
storeidx      24 verified, 1 errors  assertion failed   second store aliases the third
linelen       24 verified, 1 errors  postcondition      (ln*133)/100 -> (ln*134)/100
step          24 verified, 1 errors  invariant+overflow s += 4 -> s += 5
horner        24 verified, 1 errors  rlimit             Horner 31 -> 33
totallen      24 verified, 1 errors  loop invariant     total_len += ln + 1
cap           24 verified, 1 errors  postcondition ×2   capacity() one byte SHORT
cap3          24 verified, 1 errors  postcondition      capacity() four bytes SHORT
no2014        24 verified, 1 errors  precondition ×2    delete 1e2818b14376
extra_read    24 verified, 1 errors  precondition       add get_unchecked(buf, s+4)
fold_p        24 verified, 1 errors  invariant          fold p bytes not total_len
inv_tl        24 verified, 1 errors  loop invariant     drop `total_len <= p`
noensures     24 verified, 1 errors  assertion failed   delete the ensures (main's assert breaks)
no2004b       24 verified, 1 errors  overflow+invariant delete 2004 hunk 2 `ee > e`
-- SURVIVORS --
no2004a       25 verified, 0 errors                     delete 2004 hunk 1 `ln > src_len`
no2004a_both  25 verified, 0 errors                     neutralise hunk 1 in the SPEC too
noassert      25 verified, 0 errors                     delete main's assert (row says so)
verus.rs sha256 AFTER   844f1c6374a122166c4f59a573a22b003e6580aab9783c306ac3758334cfea91
git status --porcelain patterns-php/ : (clean)
```

**Every byte-level mutation is killed.** A shift, a mask, an index, an
off-by-one in the allocation, a wrong Horner multiplier — all refused. This is
not a memory-safety-only spec and the "25/0 is what a vacuous spec looks like
from outside" worry does not apply here.

`noassert` surviving is exactly what `verus.rs:814-818` says: the assert in
`main` is what *consumes* the postcondition, and deleting it still verifies —
which is why mutation testing and not the assert is the defence.

### 1.3 Is the safety half independent of the `ensures`? **Yes — the row's own claim, confirmed.**

`verus.rs:18-29` and `spec.md:181-190` claim the memory safety rests entirely on
the discharged `requires` of the three trusted accessors, not on the `ensures`.
Tested by deleting **both** the postcondition and `main`'s assert
(`.temp/php14/mutate3.py`):

```
### safety_only2: delete BOTH kernel's ensures and main's assert
     verification results:: 25 verified, 0 errors
```

Confirmed. ⚠ **And it is the sharpest available demonstration that
`spec.md`'s `verus.obligations: 25` is NOT a measure of spec strength** — see m4.

### 1.4 Is the `requires` reachable? **Yes, and it is discharged, not assumed.**

`off + len <= buf@.len()` is discharged at `verus.rs:801-812` from
`k < nwin`, `nwin == n_blob / stride` and `stride <= n_blob` — two nonlinear
steps, both proved. Nothing is assumed about the file. `c/main.c` and the four
`.rs` drivers pass `kernel(buf, k*stride, stride)` with the same guard
(`stride_w >= 1 && stride_w <= n_blob`), and `harness/check.py`'s `proof-rule1`
stage evaluates it on **every** call of every input (the record shows
`requires` holding on all calls). Not vacuous.

### 1.5 `R4 ≡ R5 byte-identical at O3` — verified by hand, and what it is worth

```
$ objdump -d --no-show-raw-insn .temp/php-scratch/build/ph03/{unsafe,verus}-O3-isolated
  | awk '/^[0-9a-f]+ <.*kernel>:$/{f=1;next} f&&/^$/{exit} f'    # normalised
R4 == R5 at O3: IDENTICAL instruction stream, 212 instructions
```

and the record agrees (`md5_fn 338505795ee18db952aafcdaec522df4`, 200 `n_fn`,
708 bytes, both cells).

**Is it evidence?** Partly. It is *not* a discovery that ghost code erases —
that is Verus's design guarantee. What it does show, and what the row is right
to record, is that **R5's exec text needed no restructuring to be provable**: no
extra guard, no reshaped loop, no defensive early return. That is a real result
and it is the one worth stating. Both files independently define the same
`#[inline(always)]` wrappers, so "the same MIR" is close to the mechanism — the
content is that the *proof did not force a different program*.

The O0 half is a genuine result and I confirm the row was right to correct
`norel` → `differ`:

```
unsafe O0: 349 insns    verus O0: 358 insns
< sub    $0x1b8,%rsp        > sub    $0x208,%rsp
```

Different frame sizes and different instruction counts — codegen, not
relocation. `md5_fn_norel` also differs (`d1d6e3b4…` vs `75ad2b1a…`).

---

## §2 The headline — I attacked all three proofs. **All three hold. One limb is weaker than stated, and the whole claim is UNDERSTATED.**

### 2a. The interpreter (144 of 12 600) — **faithful, and I proved it rather than diffing it**

The task asked me to diff the interpreter's control flow against
`c/kernel_hardened.c`. I did that (they match statement for statement), but eye
diffing is what `TASK_PHP_013` already did, so I ran a **differential against the
row's own shipped C instead** (`.temp/php14/09-interp-vs-real.c`,
`10-interp-vs-real-h.c` — they `#include` `c/kernel.c` and
`c/kernel_hardened.c` unmodified and compare a Horner fold of `(total_len,
decoded bytes, tally)` document by document, skipping only the documents where
the real kernel would be UB):

```
R1  c/kernel.c vs .temp/php13/02-reach.c's interpreter, 12600 documents:
    compared 8992  (skipped 3608 the real kernel cannot run: they are OOB)
    DISAGREEMENTS: 0   <- 0 means the interpreter models the shipped C
    CONTROL  interp=13199814 real=13199814  equal=1

R1h c/kernel_hardened.c vs the same interpreter, 12600 documents:
    compared 12456  (skipped 144 the real kernel cannot run: they are OOB)
    DISAGREEMENTS: 0
    CONTROL  interp=13199814 real=13199814  equal=1
```

⚠ **Note the skip counts: 3608 and 144.** They are *independently* the row's own
Q2 and Q3 figures, and they fall out of a differential that never read the
interpreter's counters. **Clean negative — this is the strongest corroboration
of 3a available and it is stronger than what the row shipped.** I also re-ran
`.temp/php13/02-reach.c` unmodified: byte-identical to the recorded log.

### 2b. ASan — **the task's suspicion is correct, and the row states the mechanism but not the conclusion.** (major, M6)

`controls/fix_incomplete.c` reproduces exactly as `NOTES.md` §5a records (all
four arms run, `env -u LD_PRELOAD`, grepping `AddressSanitizer`):

```
----- control     CONTROL reading b[8] of an 8-byte malloc
                  ==1490474==ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 1
----- benign      BENIGN src_len=63 -> total_len=45 (expect 45)          [silent]
----- fixed       ==1490489==ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 1
                  #0 in php_uudecode .../controls/fix_incomplete.c:88    <- uuencode.c:144
----- fixed2014   fixed2014 returned -1 -- no detector fired             [silent]
```

`NOTES.md:255-258` discloses that the source is `malloc`ed at exactly `src_len`
and that "an over-allocated buffer gives the over-read slack to land in". **It
never draws the conclusion, and the conclusion is the answer to the question.**
Measured (`.temp/php14/07-zval-slack.c`, same decoder, same input, three source
allocations, must-fire control):

```
----- control   ==1491181==ERROR: AddressSanitizer: heap-buffer-overflow
----- exact     src_len=2, alloc = 2 bytes, slack 0   ==1491186==ERROR: heap-buffer-overflow
----- zvalraw   src_len=2, alloc = 3 bytes, slack 1   ==1491191==ERROR: heap-buffer-overflow
----- zvalmm    src_len=2, alloc = 8 bytes, slack 6   NO DETECTOR FIRED
```

`zvalmm` is a real PHP 5.0.0 zval string: `zend_parse_parameters "s"` gives
`emalloc(len+1)`, and `emalloc` rounds to a multiple of 8
(`PHP_SHIM_REAL_SIZE(size) = ((size)+7) & ~7`, `common-php/emalloc_shim.h:217`,
projecting `Zend/zend_alloc.c:135`). Slack is
`ALIGN8(src_len+1) - src_len ∈ {1..8}`; the 2014 residual reaches `src_len+2`,
so it is **hidden for 6 of the 8 residue classes of `src_len` mod 8**, and
hidden *a fortiori* on a stock build where `_emalloc` also carries a
`zend_mem_header` and an end magic inside the same libc block.

**So, plainly: a real PHP zval string does have that slack, and limb 2 of F29's
"three independent proofs" does not transfer to a stock PHP 5.0.0 build.** It
transfers to a `USE_ZEND_ALLOC=0`-style build (`zvalraw`, which still fires) —
which is how PHP is sanitizer-tested, and plausibly how #67252 was found.

⚠ **This does not weaken the headline**, because limbs 1 and 3 are
allocator-independent: the interpreter uses offsets and no allocator at all, and
Verus's `i < v@.len()` is a property of the *source slice*, not of any
allocation. Plus a fourth corroboration nobody has to trust us for: **PHP shipped
`1e2818b14376` with its own reproducer.** What needs fixing is the framing —
`NOTES.md` §5 is headed "MEASURED, TWICE, TWO WAYS" and one of the two ways is
harness-conditional.

### 2c. `negatives.py --emit no2014` — **deletes ONLY the 2014 check.** Clean negative.

```
$ diff -u verus.rs <(python3 controls/negatives.py --emit no2014)
@@ -666,10 +666,4 @@
             decreases e - s,
         {
-            if e - s < 4 {
-                err = true;
-                break;
-            }
             proof {
```

Four lines, nothing else. The *spec* half (`fold_line`'s `else if e - s < 4`,
`verus.rs:141`) is correctly **retained** — which is what makes the failure
mean "the exec no longer implements the algorithm the spec describes", i.e. the
2004-only decoder. Reproduced: `24 verified, 1 errors`, two unsatisfied
preconditions, exactly as `negatives.py:33-49` records.

⚠ **One nuance `NOTES.md` §5b under-explains.** It says *"Read the SECOND error,
not the first"* — the first is `lemma_store_in_bounds`'s `s + 4 <= off + len`,
i.e. the **write** bound — but never says *why* the first is not itself a
finding. It is not, and here is the reason, measured: the 2004 fix really does
close the write, but **with zero slack**, so the proof cannot close it either.
See N8. Worth one sentence, because a reader who takes the first error at face
value would report a write overflow that does not exist.

### 2d. The 2014 commit — **fetched and byte-identical.** Clean negative.

```
--- 1e2818b14376 fetched: 2063 bytes sha256 97975e658d67aaade1c24f6f4fb6cfc567abc2516f166cd3126f920e2dab5fff
    committed:     2063 bytes sha256 97975e658d67aaade1c24f6f4fb6cfc567abc2516f166cd3126f920e2dab5fff   IDENTICAL
--- f95c1df58349 fetched: 1433 bytes sha256 fc3ef3c50488d0047b04629fabecb2d89aaa95d5b6f9b0085e6b61703ac31a7f
    committed:     1433 bytes sha256 fc3ef3c50488d0047b04629fabecb2d89aaa95d5b6f9b0085e6b61703ac31a7f   IDENTICAL
```

Both are what the row says they are: Stanislav Malyshev 2014-05-11 bug #67252
adding `if(s+4 > e) { goto err; }` inside `while (s < ee)`, and Ilia
Alshanetsky 2004-08-24 bug #29821 adding three hunks plus the caller's
`if (dst_len < 0)` arm. I applied the 2004 patch to the pinned tarball and
confirmed all four hunks land where `c/kernel_hardened.c` puts them (one line
citation is off — m1).

---

## §3 Fidelity — the `verbatim` claim and the `-lm` substitution

### 3.1 The diff against the tarball, in full, not summarised

```
$ tar -xzOf <pinned tarball> php-5.0.0/ext/standard/uuencode.c | sed -n '126,171p'
  -> 939 bytes, sha256 9f68d3cfb639cb62a3ec7b685da1a8e4cec828085791e200c23ffa8eb12778fe
     (exactly what provenance.extract_sha256 declares)

$ diff -u <excerpt> <(sed -n '125,170p' c/kernel.c)
-PHPAPI int php_uudecode(char *src, int src_len, char **dest)
+static int php_uudecode(char *src, int src_len, char **dest)
```

**That is the entire difference.** One token, declared in the ledger
(`spec.md:601-604`). `c/kernel_hardened.c` differs by the same token plus
exactly the four blocks of `f95c1df58349` and their two marker comments. Every
`uuencode.c:NNN` citation in the row resolves: `:66` (`PHP_UU_DEC`), `:131`,
`:133`, `:135`, `:141`, `:143-148`, `:144`, `:146`, `:158`, `:160`, `:162`,
`:168`, `:202`. `harness-php/provenance.py ph03-uudecode-bound` →
`1 row(s) checked, 0 FAILED`, overlap **95 % (18/19)**, one unevaluable
conditional (`#ifndef PH03_KERNEL_H`, benign).

### 3.2 Is the substitution in the ledger? **Yes**, `spec.md:596-599`, with a
line citation, the reason (`build.py` links no `-lm` and is frozen), the
differential (0 disagreements over the whole reachable domain) and a must-fire
control at 38. I re-ran `.temp/php13/16-flagscope.sh` unmodified — byte-identical
output, `0 disagreements` on both compilers across `-ffast-math`,
`-march=native`, `-funsafe-math-optimizations` and `-Ofast`.

### 3.3 Verdict on the tier: **`verbatim` survives, and the TIER DEFINITION is what needs the one-word fix, not the row.**

The task asked me to decide this and to say so if the definition is what is
wrong. It is.

`PROTOCOL_PHP.md` §A1 defines `verbatim` purely by **removal** — *"the function
lifts as-is; only `TSRMLS_*` / macro plumbing is **removed**"*. ph03 does not
remove `floor`/`ceil`; it **adds** two `static double` definitions and two
`#define`s that redirect them. §A1's vocabulary has no word for that, so a
builder reading §A1 alone would conclude a substitution forces `modelled`.

§A2 already carries the *right* test — *"a deletion that CHANGES BEHAVIOUR is not
a deletion, it is a `modelled` tier … if you cannot write a `why` that ends in
'no semantics', you are in the wrong tier"* — and ph03 passes it with a
differential rather than an assertion. **The repair is to say in §A1 that
`verbatim` admits substitutions demonstrated behaviour-preserving over the
reachable domain and itemised individually in the ledger**, which is exactly what
this row did.

⚠ Two smaller shape points that ninety rows will copy:

- **The ledger is named `deletions` and 3 of ph03's 4 entries are not
  deletions** (two substitutions and one projection of the shim's NULL arm).
  Same mismatch one level down; rename it or say in §A2 that it holds
  substitutions too.
- **`provenance.c_lines` pins exactly ONE span** (`provenance.py:709-712`,
  `c_lines must be [a, b] integers`), and this row lifts a **second**: the
  `PHP_UU_DEC` macro at `uuencode.c:66`, copied into `c/kernel.c:122` and
  `c/kernel_hardened.c:110`. It is covered by **no `extract_sha256`** and is not
  in the overlap denominator. I checked it by hand and it is byte-correct — but
  the check that exists to make *"those lines of that tarball hash to this"* a
  one-command fact cannot see it. See m3.

---

## §4 The oracle, the controls, and what gets copied

### 4.1 ⚠⚠⚠ **M1 (major) — `model.py::uu_fold` is NOT `verus.rs::uu_fold`. 42 of 63 possible length bytes disagree. It passes only because every shipped line declares 45.**

`spec.md:215` — **inside the hashed contract block** — says:

> *"`uu_fold` is model.py's SECOND, independent implementation — a recursive walk
> over the line chain **mirroring verus.rs's `uu_walk`/`fold_line`** … `selfcheck()`
> runs the two against each other."*

and `model.py:38-40` repeats it. **It does not mirror it.**

- `verus.rs:215-223`: `uu_fold` = `fold_bytes(w.0, w.1, 0) * 31 + w.1` — Horner
  over the **first `total_len`** emitted bytes.
- `model.py:245-255`: `_fold_line` threads `acc` and folds **every** emitted
  byte, all `p` of them.

Those are the same sequence only when `total_len == p`. The row's own
`lemma_emit_covers_declared` (`verus.rs:357-365`) proves `ln <= 3*ceil(fl/4)` and
`verus.rs:47-48` says the bound is **equality only at multiples of 3** — so it is
**strict for 42 of the 63 length bytes**, and `model.py:294-298`'s stated
justification (*"the same sequence only because `total_len` never exceeds the
number of bytes emitted"*) names the wrong condition: sameness needs `==`, not
`<=`. **The row's own Verus lemma documents that its model's justification is
false.**

Measured (`.temp/php14/04-uufold-divergence.py`, a faithful transcription of
`verus.rs`'s three spec fns against the shipped `model.Model.uu_fold`):

```
ln  fl  nsteps emitted total_len   model.uu_fold        verus uu_fold      agree
  1   1     1        3        1              154280600            152010033  **DIFFER**
  2   2     1        3        2              154280601            151950586  **DIFFER**
  3   3     1        3        3              154280606            154280606  OK
  4   5     2        6        4           119554762606            241426375  **DIFFER**
 ...
42 of 63 single-line windows DISAGREE (len 1..63, one line, 200 bytes of payload)
```

**Which side is wrong: `model.py`.** Decisive — I built a window whose line
declares `ln = 1` and ran the *shipped binaries*
(`.temp/php14/05-real-divergence.py`, input `.temp/php14/ln1.bin`):

```
model _window result (folds out[:total_len]) : 152010033
model uu_fold  (the ENSURES helper)          : 154280600
model expected_stdout (whole driver)         : 4679476855872
model.selfcheck: ['simulated result 152010033 != uu_fold() 154280600 at off=0']

c-gcc-h-O3-isolated        exit=0 out='4679476855872'
safe_naive-O3-isolated     exit=0 out='4679476855872'
safe_tuned-O3-isolated     exit=0 out='4679476855872'
unsafe-O3-isolated         exit=0 out='4679476855872'
verus-O3-isolated          exit=0 out='4679476855872'
```

All five rungs, the C, and `model.py`'s own simulation agree on `152010033`.
`model.py::uu_fold` alone says `154280600`.

**Concrete failure scenario.** `harness/check.py:7599-7611` evaluates the derived
`ensures` — `result == uu_fold(buf, off, len)` — using `mod.helpers`, i.e. this
function, and prints
`ensures re-derived independently on N sampled calls`. **That green line is
re-deriving a different postcondition from the one R5 proves.** It passes on the
shipped corpus for one reason only: `inputs/gen.py:66` emits `LINE_LEN = 45`
exclusively, and `45 ≡ 0 (mod 3)` — the equality case. The moment anyone adds an
input with a line of any other length — and `NOTES.md` §12 already names a
`sweep-*` band as **owed** — `model.selfcheck()` returns a problem,
`check.py:2861` turns it into `rep.fail("model", …)`, and the gate goes **RED**
on a row whose kernel is correct. A reader would blame the kernel.

⚠⚠ **Why this is the finding worth the whole review.** `TASK_PHP_013_REPORT.md`
§6 already reports *the same class of defect in the same function*:

> *"My first `uu_walk` resumed the outer walk at `ee + 1` … **it agrees with the
> simulation on every input this row ships**, because every shipped line declares
> 45 and `60 % 4 == 0`. It was found by writing the Verus termination argument,
> not by any test."*

The engineer named the mechanism — **a monochrome input corpus makes the model's
second implementation untestable off the diagonal** — fixed one instance, and
left a second instance eleven lines below it. **That mechanism is the thing to
carry to the next ninety rows**, and it has a cheap fix: `model.py::selfcheck()`
should drive `uu_fold` against `_window` on **synthetic windows it constructs
itself** over the whole `ln ∈ 1..63` domain, not only on the windows the shipped
`.bin` files happen to contain. That is ~6 lines and it kills the entire class.

**Severity.** I considered `blocker` and settled on `major`: no published number
moves (checksums, `Ir`, `md5_fn`, the identity pins and the Verus result are all
unaffected, and the `ensures` check passes *correctly* on the six shipped
inputs). But the claim it falsifies is inside `contract_sha256`, so the repair
costs a `contract_sha256` move plus `gate → report → gate`.

### 4.2 Is `model.py` independent, or written from `kernel.c`? **Independent enough, and its independence is what caught this.**

`_window` and `_uu_walk`/`_fold_line` are genuinely two implementations with
different shapes (imperative + bytearray vs recursive + threaded accumulator).
`selfcheck()` really does run them against each other, and it **did** catch M1
the moment I fed it an off-diagonal window. The defect is not that the model is
derived from the kernel; it is that **the corpus it is exercised on is
monochrome**. `NOTES.md:799` gets the *meaning* right for an extracted row
("there is no spec — the C is the spec — so `model.py` is an independent
*reading of the tarball*") and that reading is what makes M1 a mis-read of PHP
rather than a bug, which is exactly what that paragraph predicts.

### 4.3 The controls — **all of them run; must-fire fires, must-not-fire is silent.** Clean negative.

| control | expectation | result |
|---|---|---|
| `negatives.py --list` | lists `no2014` | ✓ |
| `negatives.py --emit no2014` | **must NOT verify** | `24 verified, 1 errors` ✓ (and the anchor guard fires correctly — it refuses if the anchor is not unique) |
| `fix_incomplete.c control` | must fire | `AddressSanitizer: heap-buffer-overflow ... READ of size 1` ✓ |
| `fix_incomplete.c benign` | must be silent | silent, `total_len=45` ✓ |
| `fix_incomplete.c fixed` | fires (the finding) | fires at `:88` = `uuencode.c:144` ✓ |
| `fix_incomplete.c fixed2014` | must be silent | silent, returns −1 ✓ |
| `provenance.py <row>` | validates | `0 FAILED`, overlap 95 % ✓ |
| `.temp/php13/02-reach.c` | re-run unmodified | byte-identical log ✓ |
| `.temp/php13/14-mechanism.sh` | re-run unmodified | byte-identical log ✓ |
| `.temp/php13/16-flagscope.sh` | re-run unmodified | byte-identical log ✓ |
| input `.bin` files | match the record | 6 inputs, 0 mismatched ✓ |
| `contract_sha256` (gate's regex) | = NOTES §0 "AS SHIPPED" = record | `0302248bc9868121ae74260e3b4ec4987fde5437e5c0a366ca8bef78d0f140df` ✓ |

⚠ **The one control that does not exist and should**: `no2004a`. See M5.

### 4.4 The `(allocs, frees)` tally in the checksum — **it cannot hide a wrong answer on this row, and the reason is stronger than the one `NOTES.md` gives.**

The worry is real in general. For **this** row it is closed structurally: `cap`
depends only on `stride`, which is fixed by the payload header, so
`php_shim_tally()` is a **per-input constant**:

```
  adversarial-nowin.bin      stride=   65 nwin=    0 cap=[]      distinct tally values = 0
  adversarial-read.bin       stride=   71 nwin=    1 cap=[55]    distinct tally values = 1
  adversarial-shortsrc.bin   stride=   20 nwin=    1 cap=[16]    distinct tally values = 1
  adversarial-write.bin      stride=   71 nwin=    1 cap=[55]    distinct tally values = 1
  large.bin                  stride= 4032 nwin= 2050 cap=[3025]  distinct tally values = 1
  small.bin                  stride=  498 nwin=   32 cap=[375]   distinct tally values = 1
```

A constant XORed into every per-call result before the driver's Horner fold
cannot mask a *per-call* wrong answer — it would have to be wrong the same way
on every call, which is a rung that computed a different `cap`, which is what the
XOR is there to catch. `NOTES.md:380-382`'s claim (*"a rung that sized its
destination differently could not agree by accident"*) is **true as written**,
because each Rust rung derives both `vec![0u8; cap]` and `tally(cap)` from the
same variable.

⚠ **The flip side, and it is the sentence the next builder needs:** because the
tally is constant, it carries exactly **one scalar** of information (`cap`) and
**no allocator behaviour at all**. `NOTES.md:385-387` already says the technique
does not carry to `ph29`; the reason it does not is that on `ph29` the tally
**varies with the input**, which is precisely when a mixed checksum stops being a
constant offset and starts being able to cancel. Worth stating that way, because
"does not carry" without the criterion is not a rule the next row can apply.

### 4.5 `spec.md`'s pins — the §7.1 answer. **Nothing was invented; one cell is wrong.**

`NOTES.md` §11's table is a good answer and I agree with nine of its eleven
rows, including the two sharp ones (`idiom.forbidden` here excludes a *repair*,
not a cheat; `idiom.required` doubles as a provenance assertion). Two problems:

- **M3 (major): `NOTES.md:795` states a refuted value as the shipped one.**
  ```
  | `identity` | ✅ unchanged — and it is a *result* here (`exact` at O3, `norel` at O0),
                 measured before it was declared. |
  shipped identity pin: {'a': 'unsafe', 'b': 'verus', 'O0': 'differ', 'O3': 'exact'}
  ```
  The shipped pin is **`differ`**, and `NOTES.md:26-31` — the *same file* — says
  in bold that `norel` was the pin, that it was wrong, and that the gate refuted
  it. Both halves of that cell are false: the O0 level is `differ`, and it was
  **not** "measured before it was declared" (§0 says it came from a hand build
  and the gate corrected it). **This is `PROTOCOL.md` rule 13 exactly** — the
  detail (§0) got maintained and the summary table 770 lines later did not.
  Failure scenario: a builder copying ph03 reads §11 for "what does `identity`
  mean on a php row", pins `norel`, and burns a gate run rediscovering §0.

- **m4 (minor):** the same table calls `verus.obligations` *"unchanged, and
  load-bearing. 25/28 here."* §1.3 measures that **25/0 survives deleting the
  entire functional postcondition**. The count pins the *shape* of the file, not
  the strength of the proof. What actually pins the strength is
  `verus.items.verus.rs.kernel.ensures`, which carries the clause text. Say that,
  because `TASK_PHP_013_REPORT.md:359` pairs "**25 verified, 0 errors**" with
  "**A full functional postcondition**" in one heading, and a reader will take
  the number as evidence for the adjective. (It happens to be a full functional
  postcondition — §1 proves it — but *not because of the 25*.)

---

## §5 The measurement — the numbers reproduce; the **mechanism is a partial account**

### 5.1 M4 (major) — §8b's attribution names 5 of a 9-instruction saving and omits a 6-instruction cost

The arithmetic is right and I reproduce it two independent ways.

From the record: `c-gcc` 53.27 vs `c-gcc-h` 53.07 `Ir`/group → **−0.20 ×
15 groups/line = −3.0 `Ir`/line**. And by hand-counting the outer-loop body of
the shipped `-O3 isolated` binaries on the `len == 45` path
(`.temp/php14/r1.gcc.asm`, `r1h.gcc.asm`; the inner loop is **27 instructions in
both**, so it cancels exactly):

| | R1 (`c-gcc`) | R1h (`c-gcc-h`) | Δ |
|---|--:|--:|--:|
| prologue + inner-loop entry | 12 | 18 | **+6** |
| per-line epilogue | 22 | 13 | **−9** |
| **per line, excluding the inner loop** | **34** | **31** | **−3** |

**−3 exactly.** Two derivations agreeing is strong, and the finding is real.

But `NOTES.md:503-508` says only *"**The `setae` and both `cmove`s are gone** —
counted, not eyeballed … `setae+cmove count: 0` for R1h against `3` for R1"*, and
never mentions the cost side. The named instructions are **5** of the epilogue's
9 (`setae`, two `test %dl,%dl`, two `cmove`); the other 4 are a spill/reload pair
(`mov %r9,(%rsp)` / `mov (%rsp),%r9`, which R1 needs and R1h does not) plus two
address computations gcc folds into `lea`s once the trip count is
unconditional. Against that, **R1h pays +6**: hunk 1's `cmp %edi,%r12d; jl`,
hunk 2's `cmp %rsi,%r9; jb`, and an **unconditional** inner-loop entry test
`cmp %rsi,%r8; jae` that R1 emits only on the non-45 path.

**Failure scenario, and it is the one §5 of the task predicted:** "three
instructions removed, −3.0 `Ir`" is arithmetically seductive and wrong. A reader
who takes it will believe the saving is small and local; it is a **9-instruction
structural saving partly refunded by a 6-instruction check**, and *that* is the
interesting claim — a safety check paying for itself by more than its own cost.
`NOTES.md:483` already warns that ∓171 is "a coincidence of magnitude"; the same
warning is owed to the 3-instructions-for-3-`Ir` reading.

The rest of §8a I could not fault: the inner loop being identical in R1 and R1h
is what makes `Ir`/group nearly equal (53.27 vs 53.07), R2/R3 index vs reslice as
described, R2 is a fair naive port (not pessimised), R3 genuinely reslices, and
the C rung is idiomatic because it is verbatim upstream C.

### 5.2 Open item 9 — **no `phNN` figure is quoted against any `pNN` figure.** Clean negative.

I grepped every `.md`, `.rs`, `.c`, `.h` and `.py` in the row plus
`TASK_PHP_013_REPORT.md` for `\bp[0-9]{2}\b`. **21 hits, every one
methodological** — `p16`'s defect shape, `p01/p16`'s `norel` pin, `p09`'s
backtick-less-`forbidden` shape, `p02`'s exit 7, `p01`'s stride residues. **Zero
adjacent to an `Ir` number, in prose or in a table.**

---

## Findings, ranked

### major

**M1 — `model.py::uu_fold` is not `verus.rs::uu_fold`; the gate's `ensures`
re-derivation checks a different function.**
`patterns-php/ph03-uudecode-bound/model.py:245-255` vs `verus.rs:215-223`;
claimed equivalent at `spec.md:215` (hashed) and `model.py:38-40`; wrong
justification at `model.py:294-298`. 42 of 63 length bytes disagree; passes only
because `inputs/gen.py:66` emits `LINE_LEN = 45` exclusively and `45 ≡ 0 (mod
3)`. Full evidence in §4.1. **Repair: fold `w.0[:total_len]` in
`uu_fold`, and make `selfcheck()` drive the two implementations over synthetic
`ln ∈ 1..63` windows rather than only over shipped inputs.** Cost: a
`contract_sha256` move + `gate → report → gate`.

**M2 — `RECAP_PHP.md` F32 is a FALSE refutation, and it re-opens something
measured and settled at `TASK_PHP_005`.**
`RECAP_PHP.md:786-793` and `.tasks-php/TASK_PHP_013_REPORT.md:172-177` (B4) and
`:653-656` (refutation 3) say `PROTOCOL_PHP.md` §E's **11 003** is wrong and the
tail is **11 004**, citing *"`check.py`'s own `NAMED_SPELLING_LEN`"* as the
authority. **The constant says 11 003:**

```
harness/check.py:1908  NAMED_SPELLING_SHA256 = "59748cce2db5c57258677242cd59ff7e9766817bb659e7a874038d21f7150a7d"
harness/check.py:1910  NAMED_SPELLING_LEN = 11003
harness/check.py:1915  # (measured: 11003 bytes, all ASCII, no `"` and no backslash)

$ measured from ph03/spec.md, check.py's own span (BEGIN .. END+19):
  BEGIN..END inclusive : 11003 bytes, sha256 59748cce2db5
$ measured to end of the `why` string:
  ph03 named-spelling tail : 11004 bytes, sha256 0e7c1c8f99c0
```

`PROTOCOL_PHP.md:576` pairs its 11 003 **with sha256 `59748cce2db5…`**, which is
unambiguously `check.py`'s span. §E is **correct**. And this was already
adjudicated:

```
.tasks-php/TASK_PHP_005_REPORT.md:487  ✅ The manager's withdrawal is right and the mechanism is a single full stop.
:488  11 003 is `check.py`'s pinned slice (BEGIN -> end of the END marker); 11 004 is
:489  BEGIN -> end of string; the difference is the '.' that closes the sentence.
:490  Both are correct about different cuts
```

**Failure scenario, and it is live:** `RECAP_PHP.md` now **contradicts itself** —
line 14 says *"the gate mandates an 11 003-byte shared block"*, line 788 says
11 003 is wrong. Line 37 already points at the settlement that F32 reverses. A
corrections task acting on F32 would edit a **correct** number in
`PROTOCOL_PHP.md` into an incorrect one and break its pairing with
`NAMED_SPELLING_SHA256`. **Withdraw F32 and B4; the ironic framing ("the document
warning that this number is contested was itself carrying a wrong one") applies
to F32, not to §E.**

**M3 — `NOTES.md:795` asserts the `identity` pin is `norel` at O0 and "measured
before it was declared".** The shipped pin is `differ` (`spec.md:563`) and
`NOTES.md:26-31` says the gate refuted `norel`. Self-contradiction in the file a
builder consults to learn what the pins mean. Details in §4.5. Cost to fix: a
gate re-run (`NOTES.md` is gate-hashed only).

**M4 — `NOTES.md` §8b's mechanism is a partial account of a correct number.**
`NOTES.md:503-508`. The epilogue saves **9** instructions and the two new checks
plus an unconditional loop-entry test cost **6**; net −3. Only 5 of the 9 are
named and the cost side is not mentioned. Hand count and reconciliation in §5.1.
⚠ `c/kernel.c` and `c/kernel_hardened.c` are measurement-hashed but `NOTES.md`
is not, so this fix is a gate re-run.

**M5 — the headline is UNDERSTATED: `f95c1df58349`'s **first** hunk is
provably redundant.** Not a defect — a result the row missed. Two-sided:

*Verus.* Deleting `if ln > src_len { err = true; break; }` from R5's **exec**
still gives `25 verified, 0 errors`; neutralising the corresponding branch in the
**spec** (`uu_walk`'s `else if ln > src_len`) while keeping the exec also gives
`25 verified, 0 errors`. So Verus proves the two programs are the same program.

*C.* `.temp/php14/06-hunk.c`, the interpreter with `goto err` decomposed by hunk
over the same 12 600 documents:

```
A. f95c1df58349 `goto err` decomposed, 200*63 = 12600 documents:
   hunk 1 (`len > src_len`) fired : 1953
   hunk 2 (`ee > e`)        fired : 1511
   of hunk-1 firings, hunk 2 would ALSO have refused : 1953
   of hunk-1 firings, hunk 2 would NOT have refused  : 0  <- 0 means HUNK 1 IS REDUNDANT
```

The mechanism is one line: `line_len(ln) >= ln` for every `ln ∈ 1..63`, and
after `s++` we have `e - s <= src_len - 1`, so `ln > src_len` forces
`fl > e - s`. **So the 2004 commit is not merely incomplete — half of it is dead
on arrival.** That sharpens F29 considerably: *the patch that missed the real
bug for ten years also shipped a check that never decides anything.*
⚠ **Recommend `controls/negatives.py` gain a `no2004a` mutant declared
must-**PASS**** — it is the only mechanical way to keep this claim re-derivable,
and it is the first control in either programme whose expectation is "still
verifies".

**M6 — the ASan limb of F29 is harness-conditional and the row states the
mechanism without the conclusion.** `NOTES.md:255-258`,
`controls/fix_incomplete.c:47-50`. Measured in §2b: with a source allocated as
PHP 5.0.0's `emalloc` allocates a zval string, **ASan is silent**. Limbs 1 and 3
are allocator-independent so F29 stands, but `NOTES.md` §5's heading "MEASURED,
TWICE, TWO WAYS" over-promises about limb 2. **One sentence fixes it:** *"and on
a stock PHP build this residual is not ASan-observable at all — `emalloc` rounds
to 8 — which is part of why it survived ten years."* That sentence makes the
finding **stronger**, not weaker.

### minor

**m1 — `c/kernel_hardened.c:23` cites 2004 hunk 2 at `:145-148`; it is
`:147-150`.** Applied the pinned patch to the pinned tarball
(`.temp/php14/patchtest/`): hunk 1 → `:139-142` ✓, hunk 2 → **`:147-150`** (the
file says `:145-148`), hunk 3 → `:180-183` (`:180-184` includes the closing
brace, defensible), hunk 3′ → `:215-218` ✓. `c/kernel_hardened.c` is
measurement-hashed, so this costs a re-measure — **batch it**, do not pay it
alone.

**m2 — `verus.rs:375` says "Four call sites" and then lists five.** There are
five (`verus.rs:602, 676, 677, 678, 679`). `NOTES.md:633` says five and is
right. Measurement-hashed; batch with m1.

**m3 — `provenance.c_lines` pins one span, and this row lifts two.**
`harness-php/provenance.py:709-712`. `PHP_UU_DEC` at `uuencode.c:66` is in both C
rungs (`c/kernel.c:122`, `c/kernel_hardened.c:110`), is correct (I checked), and
is covered by no `extract_sha256` and not in the overlap denominator. **This is a
schema limit that ninety rows will meet** — most extracted kernels need a macro
or a struct from outside their function. Cheapest fix: let `c_lines` be a list of
`[a, b]` spans and hash their concatenation.

**m4 — `verus.obligations: 25` is insensitive to spec strength** and
`NOTES.md:792` calls it "load-bearing". §1.3: 25/0 survives deleting the whole
`ensures`. The strength pin is `verus.items…kernel.ensures`, not the count.

**m5 — `TASK_PHP_013_REPORT.md` §12.3b's *"the closing bracket itself dirties the
tree"* does not reproduce.** Four bracket runs, tree clean throughout. It is
conditional on the run's content being new (`PROTOCOL_PHP.md` §E: "identical runs
collapse on **content**"). Worth correcting because the next agent will otherwise
expect a dirty tree and not investigate one.

**m6 — F31's §7.3 worry ("would a reader of the gate record conclude the fix is
complete?"): the manager's call HOLDS for the published table and is thin for the
record.** `results-php/gate/ph03-uudecode-bound.json` carries `idiom.why`, which
says in terms *"R1h IS THE REAL UPSTREAM FIX … and IT IS INCOMPLETE: … 144 of
those 12 600 documents still read past the source"*, and `report.py` renders it
verbatim into `results-php/tables/ph03-uudecode-bound.md:44`. So a reader of
either artefact cannot conclude the fix is complete. **But the record's
`sanitizer_hardened` block reads `"expect": "clean", "fired": false` on all four
adversarial inputs and carries no marker that a firing input is
structurally unshippable**, and `provenance` (which holds the sha-pinned
`fix_commit_note` naming `1e2818b14376`) is **not echoed into the gate record at
all** — I checked: `'fix_commit_note' in json.dumps(record)` is `False`. A
machine consumer sees four clean rows. No harness edit needed; a
`sanitizer_hardened_note` inside the hashed block would close it.

**m7 — `NOTES.md:280` says "Read the second error, not the first" without saying
why the first is not itself a finding.** It is not (see N8), but as written a
reader could report a write overflow that does not exist.

---

## Clean negatives — attacked, did not land

Named so nobody re-runs them.

**N1.** `c/kernel.c` is byte-identical to the pinned tarball's `126-171` except
`PHPAPI` → `static`. Full diff in §3.1. `extract_sha256` reproduces exactly.
Every one of the row's thirteen `uuencode.c:NNN` citations resolves.

**N2.** Both committed patches are byte-identical to freshly fetched
`https://github.com/php/php-src/commit/<sha>.patch`, and `f95c1df58349` applies
cleanly to the pinned tarball producing exactly `c/kernel_hardened.c`'s four
blocks.

**N3.** `negatives.py --emit no2014` deletes exactly four lines, exactly the 2014
check, keeps the spec half, and its anchor-uniqueness guard is correct.

**N4.** **The instrumented interpreter is faithful to the shipped C** — 0
disagreements over 8992 (R1) and 12 456 (R1h) documents against the row's own
`c/kernel.c` and `c/kernel_hardened.c`, with a must-fire control, and the
skipped sets are independently exactly 3608 and 144. §2a.

**N5.** R5's `ensures` is strong: 17 of 19 mutants killed, including every
byte-level one (shift, mask, source index, destination index, capacity ±1,
Horner multiplier, step size, `total_len`). §1.2.

**N6.** The row's claim that the safety half does not rest on the `ensures` is
exactly right: `25 verified, 0 errors` with both the postcondition and its
consumer deleted.

**N7.** `R4 ≡ R5` at O3 verified by hand from the binaries (212 identical
instruction lines); `differ` at O0 verified (349 vs 358 insns, `0x1b8` vs
`0x208` frames, `md5_fn_norel` differs). The correction from `norel` was right.

**N8.** **"The 2004 fix closes the write" survives an extension of the row's own
sweep.** The row measured single-line documents only; I swept **170 226**
multi-line documents (`K` full 45-lines + a final line declaring `L`, `src_len`
swept) through the same interpreter:

```
B. MULTI-LINE documents under f95c1df58349:
   documents swept : 170226
   write past emalloc : 0   <- >0 would REFUTE 'the write is closed'
   read  past src end : 1008
   tightest write margin (cap-1 - wr_max) : 0 at K=0 L=1 src_len=2
```

⚠ **The tightest margin is exactly 0**, which is *why* R5's `no2014` run also
fails `lemma_store_in_bounds`'s `s + 4 <= off + len`: the write bound is tight to
the byte, so the proof has no slack to close it without the 2014 check even
though no write actually escapes. That is a proof-slack artefact, not a live
overflow — the explanation `NOTES.md` §5b owes (m7).

**N9.** `TASK_PHP_013_REPORT.md` §12.7's own worry — *"the C wrapper reads
`dest[0 .. total_len)` on an adversarial input where `total_len > cap`, i.e. a
second out-of-bounds site the wrapper adds"* — **is closed by the same sweeps.**
`total_len > cap` implies the terminator write at `dest[total_len]` is past
`cap`, which is counted as a write past emalloc; there are **0** under the 2004
fix across 182 826 documents, and under R1 the decoder itself faults first on
every document where it would matter (I ran the real R1 kernel on all 8992
non-OOB documents — no fault, no disagreement). The wrapper adds no reachable
site.

**N10.** The tally cannot mask a wrong answer here: it is a **per-input
constant**, one distinct value across every call. §4.4.

**N11.** `contract_sha256` computed the gate's way is
`0302248bc9868121ae74260e3b4ec4987fde5437e5c0a366ca8bef78d0f140df` — matching
`NOTES.md`'s §0 "AS SHIPPED" line **and** the committed gate record. The
`PROTOCOL.md` rule 6 disclosure is verifiable, and its two documented moves are
both gate findings, correctly described.

**N12.** Open item 9: no `phNN` figure is quoted against any `pNN` figure
anywhere in the row or in `TASK_PHP_013_REPORT.md`. §5.2.

**N13.** All three `.temp/php13/` harnesses re-run unmodified give byte-identical
output (`02-reach.c`, `14-mechanism.sh`, `16-flagscope.sh`). The 6 input `.bin`
files match the measurement record's `input_sha256` exactly.

**N14.** The rungs are semantically equivalent and none is rigged: R2 indexes,
R3 reslices, R4/R5 uncheck; identical driver loops between the markers; the R1
rung is idiomatic C because it *is* upstream C; the `Ir` claims rest on `-O3`
rows and the C-vs-Rust claim carries the clang column (`NOTES.md:460-465`).

---

## What I did NOT do

1. **No full `gate.py ph03-uudecode-bound` run.** It writes two committed
   artefacts under a review; §0 says what I used instead. If the manager wants
   the gate re-confirmed independently it is ~24 min and should be run **after**
   M1/M3/M4 land, since all three cost a re-gate anyway.
2. **No `controls/spellings.py`.** Still owed (`NOTES.md` §12), still means no
   ratio in §8 is *the* cost of safety. I did not attempt the search.
3. **I did not test `NOTES.md` §10a(b)'s residual** — an extra unchecked read
   added *inside* a trusted wrapper's `external_body` body. Verus cannot see it
   by construction, so there is nothing to run; the row's two named backstops
   (identity `exact`, Miri on a boundary-reaching input) are the honest answer
   and it says so. I did confirm the *analogous* mutation in verified code is
   caught (`extra_read`: `get_unchecked(buf, s+4)` → precondition not satisfied).
4. **I did not re-measure `Ir`.** §5.1's numbers are the record's, cross-checked
   against a hand instruction count; I did not re-run callgrind.
5. **Unsure: M1's severity.** I ranked it `major` because no published number
   moves. If the manager reads *"the gate's functional oracle is a different
   function from the proved one"* as invalidating the `proof-rule3` result
   itself, it is a `blocker`. I would not argue.
6. **Unsure: whether M5 should change F29's wording.** "The fix is incomplete"
   is true; "and one of its two checks is dead" is also true and I measured it
   both ways. Whether that belongs in F29 or as a separate finding is a manager
   call, and reconciliation of the running count is the manager's job.

---

**Running count: launched from 61. This review adds 6 major and 7 minor findings
and 14 named clean negatives.** The two that matter most are shape defects, not
row defects: **M1** (a monochrome input corpus makes a model's second
implementation untestable, and the row's own report names that mechanism eleven
lines above the second instance of it) and **M2** (an unreviewed refutation
landed in the authoritative layer, reversing a settled measurement and making
`RECAP_PHP.md` contradict itself). **Reconciliation is the manager's job.**
