# p32 — free-list allocator / object pool with recycling: measurements

`spec.md` is the contract and `c/kernel.h` is the kernel in pseudocode. This file
is what was **measured**, and what was not.

**`p32` and `p33` of `.memory/06-catalogue.md` are ONE ROW with TWO ARMS** — one
C mechanism, one omitted conjunct, and the input picks the harm.

---

## 0. The contract hash, and a disclosure about WHEN it was recorded

`spec.md`'s `slb-contract` block, as `harness/check.py` hashes it:

```
contract_sha256  80059fefdd89a443f1393e5e5ae2cbc18ce969c13d3ad80e61fea091bb365f26
```

⚠⚠ **DISCLOSURE, and it is a deviation from `PROTOCOL.md`'s definition
of done item 6.** That rule asks for the hash to be recorded *"the moment you
first write it, before building any cell"*, so that *"no `required` or
`forbidden` entry moved after I measured"* is independently checkable in a
one-commit pattern. **On p32 it was not**: `spec.md` was written AFTER the six
non-Verus cells had been built and cross-checked against `model.py`, because the
`verus.obligations` and `identity` pins are census results that do not exist
before the rungs do. So this hash is the value at the END of `TASK_144`, not a
pre-measurement snapshot, and **it does not provide the check the rule exists
for.**

What a reviewer can check instead, and it is weaker: `spec.md` is generated in
one shot by `.temp/t144/spec/mkspec.py` and was edited **exactly once** after
first being written, for a reason the gate itself printed. ⚠ **The
disclosure has to name that edit or it would be the false-disclosure failure
`TASK_064_REVIEW` M3 caught on `p47`**, so:

* gate runs 1 and 2 recorded `contract sha256 68ea7c9f58ce...`;
* both runs SHOUTED `[idiom-forbidden]` **fourteen times** — every `forbidden`
  entry was a bare string with no backticks, so the enforced audit never ranged
  over any of them and the reported `0 hits` was **vacuous**, which is `p09`'s
  defect (`TASK_038_REVIEW`);
* the fix was to backtick all fourteen. The audit now ranges over **28
  spellings × rungs with 0 hits** and the shout is gone;
* gate run 3 onwards records `contract sha256 80059fefdd89...`.

**The diff between those two hashes is FOURTEEN SETS OF BACKTICKS AND NOTHING
ELSE** — `required`, `why`, the `verus` block, `driver`, `collapse`, `identity`
and `miri` are byte-identical across it, checked by regenerating the pre-edit
`spec.md` from `mkspec.py` and diffing the parsed JSON with `forbidden` removed.
⚠ **The first version of this paragraph said the diff ALSO contained an
added sentence in `why`, and that was false**: the edit was written but its
search string did not match the generator's line-wrapped literal, so it silently
did nothing. Caught by running the diff that this paragraph now cites, rather
than by trusting the edit. That is `TASK_064_REVIEW` M3's failure mode — a
disclosure a reviewer trusts INSTEAD of re-checking — caught inside one task.
The gate logs
are in `.temp/t144/`, which is gitignored, so a reviewer who wants the check must
re-run `harness/check.py p32` and compare against the value above.

---

## 1. Why this row exists, and it is not what a reader will guess

It exists because **the admission bar was corrected** (`CLAUDE.md` rule 6,
`.memory/02-bench-rules.md` *THE ADMISSION BAR IS C-SIDE ONLY*, RECAP findings 53
and 54). It was refused twice on the sentence

> *"safe slab == buggy C bit for bit"*

⚠⚠⚠ **That sentence is TRUE, it is reproduced below on a kernel written
from scratch for this task, and it is this row's HEADLINE rather than a defect.**
Nothing the Rust or Verus rungs do can shrink or retire the row. Where they land
on a zero, or on a gap, that is reported as a result — sections 6b and 8 are both
of that kind.

### 1b. The one deviation from the promoted demonstration, and it is measured

`TASK_143`'s admitted demonstration packed the handle into the **operand byte**:
`h = a & 7`, `g = a >> 3`, so the file named a `(slot, generation)` pair
directly. **The shipped rungs do not.** ALLOC issues the handle into a handle
REGISTER and the file names the register — `p29`'s corrected sentence, *a file
cannot name a pointer, but it CAN name an operation that saves one*.

The reason is not taste. `controls/arm_forgeable.c` is the file-supplied-handle
variant **with the hardened guard present**, and `controls/forgeable.py` runs it:

```
op0 ALLOC   -> slot 0  (handle 0 | gen 0)
op1 FREE  a=0x00 -> ACCEPTED: push slot 0, nx[0]=1, freehead=0
op2 FREE  a=0x08 -> ACCEPTED: push slot 0, nx[0]=0, freehead=0   <<< SELF-LOOP
op3 ALLOC   -> slot 0
op4 ALLOC   -> slot 0

free list simple: NO  <<< CYCLIC
two ALLOCs returned the same slot: YES <<< TWO LIVE HANDLES ALIAS ONE BLOCK
```

With a file-supplied handle the attacker can always spell the CURRENT
incarnation of a block that is already free, so `gen[h] == g` passes on a block
that is on the list and **the HARDENED kernel self-loops its own free list in
five operations**. That is not a harder version of this row; it is a broken R1h,
and admission question 1 requires the C kernel to be correct. The control exits
non-zero if the variant ever stops breaking, so this paragraph cannot go stale
quietly.

⚠ The second deviation is smaller and is in section 9.

---

## 2. Detector coverage — the two-cell storage experiment

`controls/storage_arms.py`. **One algorithm, storage the only variable**, every
run with `LD_PRELOAD` unset, every sanitiser log read whole, and the positive
control (a real double free of a real heap block) firing in all ten C builds.

```
input            arm    C arena           C malloc            safe Rust     malloc detector
                                                        forbid(unsafe_code)
benign           bug  72356755880000075  72356755880000075  72356755880000075   -
benign           fix  72356755880000075  72356755880000075  72356755880000075   -
adv-stale-read   bug              32521          NOT REPRO              32521   heap-use-after-free
adv-stale-read   fix              38535              38535              38535   -
adv-recycle      bug           29797947           29797947           29797947   -   (SILENT in BOTH)
adv-recycle      fix           30032431           30032431           30032431   -
adv-doublefree   bug        28444101123           rc = -6        28444101123   attempting double-free
adv-doublefree   fix        35593523088        35593523088        35593523088   -
adv-alias        bug       895071855618           rc = -6       895071855618   attempting double-free
adv-alias        fix      7765691657627      7765691657627      7765691657627   -
```

Three things at once, and each is a separate result:

1. ✅ **`#![forbid(unsafe_code)]` safe Rust reproduces the C ARENA rung EXACTLY
   on 10 of 10 (input, arm) cells**, buggy arm included — including the four
   where the answer is WRONG. The sentence that killed this row twice.
2. ✅ **The SAME C source with `malloc` storage ABORTS** on two of the three
   adversarial harms. Everything else is byte-identical: the free list, the
   generations, the handle registers, the fold and the safety line.
   `controls/arm_body.inc` is included twice inside that control, so its own two
   arms differ by the safety line alone.
3. ⚠⚠ **`adv-recycle` is bit-identical and silent in BOTH storage arms.**
   The use-after-RECYCLE harm is **storage-independent** and invisible to every
   allocation-shaped instrument. That is `p29`'s recycle class arriving on
   unrelated code, and it is `p33`'s arm of this row.

⚠ **`NOT REPRO` is not a missing number, it is the result.** The
`malloc` arm's `adv-stale-read` cell reads FREED HEAP, so its plain-build
checksum is a function of the allocator rather than of the input: measured in one
run of `storage_arms.py`, `malloc-plain` `33172`, `malloc-plain-clang` `33203`,
`malloc-ubsan` `34629`, and a different value again in the run before. The ARENA
arm is `32521` in all five of its builds and 1 distinct value in 20 runs. **No
number from that one cell is a fact; the detector verdict is.**

### 2a. What the gate's own instruments say about the SHIPPED storage

Stage 7 (ASan + UBSan, gcc and clang) and stage 8 (Miri on `unsafe.rs`), all
nine inputs:

```
                             ASan/UBSan   Miri     R1 vs R1h checksum
benign / degenerate            clean      no UB    identical
adversarial-stale-read         clean      no UB    DIVERGES
adversarial-recycle            clean      no UB    DIVERGES
adversarial-doublefree         clean      no UB    DIVERGES
adversarial-alias              clean      no UB    DIVERGES
adversarial-many               clean      no UB    DIVERGES
adversarial-stride3            clean      no UB    identical (0 kernel calls)
```

**Every detector is silent on every input, and four of the five adversarial
inputs return a wrong answer.** That is not an oversight and `model.py` does not
merely assert it: its simulation computes every index the BUGGY rung would
compute and records whether one escapes its array (`Pool._touch`), so
`sanitizer_expect` is a derivation. None escapes, and the reason is structural —
`regs[r]` is `NIL` or a real slot, `freehead` is `NIL` or a real slot, and `nx[]`
only ever holds values drawn from those two.

### 2b. Why the `malloc` arm does not null the freed pointer

Measured, both ways. With `blk[h] = NULL` after the `free`:

* the stale read becomes a **SIGSEGV** rather than a `heap-use-after-free` — a
  crash, a different bug class, `p27`'s and `p29`'s argument exactly;
* the double free becomes a no-op **`free(NULL)`**, and the first draft of the
  control therefore reported *"LeakSanitizer only"* where the real answer is
  `attempting double-free`.

Both are recorded here rather than quietly repaired. The shipped `regs[r]` is not
cleared for the same reason: clearing it would turn every stale use into the
`h == NIL` case, which folds `SENT` in BOTH rungs.

### 2c. The positive control, and why it has a `volatile` sink

`controls/arm_malloc.c`'s `k_ctl` is `malloc; free; free`. ⚠ **The first
spelling of that control at `TASK_143` did not fire under clang**, because clang
eliminates a `malloc`/`free` pair whose pointer never escapes — `p31`'s
malloc-elision artefact. `slb_sink` is a `volatile void *` that forces the
escape. `storage_arms.py` exits non-zero if any build's control is silent, and on
this run it fired in **10 of 10** C builds (gcc and clang × plain, ASan, UBSan,
and both storage arms).

### 2d. Reproducibility — and this row has a property neither built temporal row has

`controls/repro.py`, 20 runs per (input, cell), plain `-O3 isolated`:

| | R1 | R1h | R1 vs R1h |
|---|---|---|---|
| all five `adversarial-*` | **1 distinct** | 1 distinct | **DIVERGES** |
| `degenerate`, `small` | 1 distinct | 1 distinct | identical |

**Every cell is stable.** p32's storage is a local array, so no heap address
reaches the answer and R1's checksum is a pure function of the input bytes —
where `p29` ships **20 distinct values in 20 runs** on three of its inputs. p32's
adversarial rows are excluded from the gate's agreement set because they
*disagree*, not because they are unstable.

⚠ The contrast lives inside this pattern: the `malloc` arm's
`adv-stale-read` cell reads freed heap and is **not** stable — one run of
`storage_arms.py` gave `33172` / `33203` / `34629` across gcc-plain,
clang-plain and gcc-ubsan, and the run before gave different values again, while
the arena arm is `32521` in all five of its builds. So *"what the stale read
returns is not reproducible"* is a property of the STORAGE, not of the bug class,
and **p32 contains both cells**. ⚠ No count in `repro.json` is pinned
anywhere: `p23`'s lesson is that the distinct-value count of a nondeterministic
checksum is itself nondeterministic, so what is published is the invariant.

---

## 3. What safe Rust gives you here, and the answer is nothing

`p27` and `p29` both get **one half of their safety line written by the
language**: their records are `Option<Box<Rec>>`, `tab[i] = None` frees the
record and invalidates the slot in one operation, and the `Option` discriminant
IS the liveness bit.

**p32's pool is `[u8; 32]`.** No block is allocated, no block is dropped, and
`Option`, `Box`, borrowck, drop glue and Miri have nothing to attach to.

| rung | what the language writes | what the author writes |
|---|---|---|
| `safe_naive.rs` (R2) | nothing | `h == NIL` **and** `gen[h as usize] != g` |
| `safe_tuned.rs` (R3) | the `Some`/`None` discriminant, from `Option<(u8, u32)>` | `gen[h] != g` |
| `unsafe.rs` (R4) | nothing | both, through `arr_get_unchecked` |
| `verus.rs` (R5) | nothing | both, and see 6b |

R3 is the most idiomatic safe Rust available for this kernel and it still writes
the generation compare out by hand, because **nothing in the type system knows
that a live range of bytes has changed occupant**.

⚠ There is no epilogue in ANY rung — not even in the safe ones, which is
where `p27` and `p29` hand theirs to `Drop`. There is nothing to release.

---

## 4. The proof, and what it costs

```
verus.rs                       15 verified, 0 errors
verus.rs --cfg slb_twin        18 verified, 0 errors
```

`15 = 6 consts + run 1 + kernel 3 + main 5`, every function term measured one at
a time with `--verify-function <name> --verify-root`
(`.temp/t144/verus/obligations.log`). `kernel`'s 3 is the body plus two loop
bodies — the free-list initialisation and the op walk.

**TCB: FIVE items** — `buf_get_unchecked`, `arr_get_unchecked`,
`arr_set_unchecked`, `load_input`, `emit`. Three carry verified twins, which is
the `15 → 18` difference.

⚠⚠ **`p27` and `p29` ship SEVEN trusted items and owe FIVE twins.** The
two p32 does not have are `vstd::raw_ptr::allocate` and `deallocate` — **because
p32 does not allocate**. There is no `PointsTo`, no `Dealloc` token, no
`global layout` directive, no `Map<int, PointsTo<Rec>>` and no permission
threading anywhere in `verus.rs`. The proof is a plain functional refinement of
an abstract machine over five `Seq`s.

---

## 5. R4 vs R5 identity

```
unsafe vs verus  -O0  : norel   (md5_fn e21b58386386; raw equal False, padding 9/9 B)
unsafe vs verus  -O3  : exact   (md5_fn cf0875f0cafb; raw equal True,  padding 15/15 B)
```

⚠⚠ **Stronger than `p29`'s `norel`/`differ`, and the reason is the
pattern rather than the effort.** `p29`'s pair diverges at `-O0` because its
record write goes through vstd's `ptr_mut_write` on one side and a bare `*p = v`
on the other — six instructions apart at five sites. p32 has **no pointer write,
no allocation and no vstd call in the kernel at all**; its only trusted items are
three `#[inline(always)]` `get_unchecked` wrappers, identical between the two
files. There is nothing for the two rungs to spell differently. The `-O0` residue
is link layout: the crate names differ in length, so the pc-relative
displacements do.

---

## 6. What the R5 does, and — more interestingly — what it does not

### 6a. The obligation is FUNCTIONAL, not temporal, and that is structural

`p27` proves *at the moment of the read the record still exists*, and one linear
`PointsTo` carries the whole of it. `p29` proves that **and** *the record is
still the one FIND returned*, and its first conjunct is discharged by
`perms.tracked_borrow`'s precondition — so **the proof forces the line C forgot**:
delete `live[cur] = 0` after the free and the invariant cannot be re-established
at any price.

⚠⚠⚠ **Nothing of that kind happens on p32.** The safety line is
discharged as an ordinary functional postcondition: the loop must compute what
`run` says, and `run`'s handle-consuming arm folds `SENT` when the generation
does not match. **Linearity has nothing to say about this bug, because the bug
does not touch an allocation.** The invariant `verus.rs` actually needs —
`wf_ranges` — says only that every handle, every free-list link and the head are
`NIL` or a real slot. **That invariant holds in `c/kernel.c` too**, which is why
ASan says nothing about the shipped bug.

⚠⚠ **And the invariant that makes R1h correct AS AN ALLOCATOR is not
proved and is not needed**:

> for every handle register `r` with `regs[r] = h != NIL` and `regg[r] == gen[h]`,
> slot `h` is not on the free list

is what rules out the double push, the self-looping list and the two aliased
handles. It is argued in `c/kernel.h`, it appears **nowhere** in `verus.rs`, and
neither the memory-safety obligations nor the functional `ensures` require it —
the abstract machine models a self-looping list perfectly happily. `model.py`
carries a `list_is_simple()` walk over its successor map that decides the
property, and **no rung and no proof ever computes it.**

### 6b. The mutation battery, including an arm that MUST VERIFY

`controls/proof_mutants.py`, seven arms, **7 of 7 as expected**. Run with
`--rlimit 200`: ⚠ at the default limit a mutant whose real failure is a
precondition reports only `Resource limit (rlimit) exceeded` on the enclosing
loop, which cannot distinguish a memory-safety failure from a functional one —
measured on M3, and that distinction is what this whole section turns on.

| arm | kind | expected | got | the diagnostic |
|---|---|---|---|---|
| `M0-control` | control | verify | **verify** `15/0` | the shipped file |
| `M1-generation-conjunct` | **ATTACK** | fail | **fail** `14/1` | `assertion failed` at `st_out =~= step(st_in, c, a).0` — the refinement |
| `M2-constant-body` | **VACUITY** | fail | **fail** `12/1` | `postcondition not satisfied` |
| `M3-nil-test` | attack | fail | **fail** `14/1` | `precondition not satisfied`, `i < v@.len()` |
| `M4-spec-weaken` | **must-verify** | **verify** | **verify** `15/0` | — |
| `M5-freehead-range` | deletion | fail | **fail** `14/1` | `precondition not satisfied` |
| `M6-nx-init` | deletion | fail | **fail** `14/1` | `invariant not satisfied at end of loop body` |

* **`M1` is the ATTACK arm the bar asks for**: it deletes `gen[h] != g` from the
  exec code and nothing else, so what survives IS `c/kernel.c`. It fails.
* **`M2` is the VACUITY arm**: `return 0;`, which is `TASK_136`'s
  `fn arm_c() -> u8 { 9 }` in this file's terms. It fails.
* ⚠⚠⚠ **`M4` is the arm that is supposed to VERIFY, and it does,
  `15/0`.** It deletes the conjunct from the exec code AND from `step`, so the
  specification describes the buggy kernel and the two agree again. **That is the
  honest statement of what this R5 buys: the safety line is load-bearing against
  the SPECIFICATION and against nothing else.** Compare `p29`, whose
  `live[cur] = 0` cannot be deleted at any price. `p42` is the precedent for
  shipping a gap like this as the finding.
* **`M3` versus `M1` is the contrast worth reading.** `M3` disables `h == NIL`,
  so slot 255 is indexed into an 8-element array, and Verus reports a
  **precondition** failure — a memory-safety obligation. `M1` disables the
  generation test and Verus reports a **refinement** failure. **The two halves of
  one `if` fail for two different kinds of reason, and only one of them is what
  a memory-safety tool would ever have caught.**
* **`M6` is the sharpest deletion arm.** Delete the free-list initialisation and
  `nx` stays all-zero, so the list self-loops at slot 0 from the very first
  operation. What fails is the *loop invariant*, not memory safety — slot 0 is a
  real slot. **The free list's SHAPE is only ever a functional property here.**

---

## 7. What the safety line costs, and why this pattern publishes no cost headline

⚠⚠ **p32 SHIPS WITH NO COST AXIS. THE ABSENCE IS DECLARED, NOT A
MEASURED ZERO.** `p29` ships the same way, and `.memory/02-bench-rules.md`'s rule
is the reason: *a published spread cannot carry a safety number*, and a
rung-to-rung difference may only be published after searching BOTH rungs'
spellings and counting the levers on each side. **That search was not done**, on
either side, and five patterns in this project have published a headline wrong in
the flattering direction by skipping it.

What the gate records — and it is data, not a headline — is that the anti-collapse
stage measured marginal Ir per kernel call between **727 and 17349** across 64
cell/probe pairs, all above the derived floor, with the tightest margin **49.2×**.
`results/tables/p32-free-list-pool.md` renders the per-cell numbers. **No
rung-to-rung claim is made from them here or anywhere else in this pattern.**

The R2/R3 levers that were deliberately left unmeasured, so that a later task
knows where to look: the flat `[u8; 32]` pool versus `[[u8; 4]; 8]`, the
NIL-sentinel register pair versus `Option<(u8, u32)>`, re-widening `h as usize`
per use versus binding it once, and an `if` chain versus a `match`. R3 takes all
four; **which of them survive `-O3`, and at what price, is open.**

---

## 8. What was NOT done

* **No cost claim of any kind**, on any axis, for the reason in section 7.
* **The R5 does not prove the free-list well-formedness invariant** (section 6a).
  It could be stated — `model.py` computes it with a visited-set walk — and
  stating it would make p32 the first row here to prove a *structural* invariant
  about a data structure the safety line maintains. Not attempted; budget.
* **`sweep-*` bands are generated but nothing was measured on them.**
  `inputs/gen.py --sweep` writes an operation-count band and a free-fraction
  band; no law is published from either.
* **The `malloc` storage arm is a CONTROL, not a rung.** It is built at `-O1`
  with gcc and clang, plain / ASan / UBSan, and it is not in the ladder matrix,
  so no Ir or wall-clock number exists for it.
* **`arm_forgeable.c` is one input.** It demonstrates that the
  file-supplied-handle variant's hardened kernel breaks; it does not characterise
  how often or how badly.
* **No `-O0d` (debug-assertions) row.** All arithmetic is `wrapping_*` in the
  Rust rungs precisely so that row would be uninteresting; it was not run.

---

## 9. Two conventions this pattern does NOT follow, and why

### 9a. The two C rungs are written out in full, not `#include`d twice

`TASK_143`'s demonstration wrote ONE kernel body and `#include`d it twice with
`SLB_HARDEN` 0 and 1, so that R1 and R1h differ by the safety line **by
construction**. The task file asked for that construction to be kept. It is kept
— in `controls/arm_body.inc`, where the storage experiment uses it — and it is
**not** used for the rungs, for a gate reason rather than a stylistic one:

> `harness/check.py`'s `forbidden` audit reads the rung sources as TEXT
> (`rung_sources` → `exec_code` → `spelling_matches`), and a `forbidden` hit is
> one of the few things in stage 0b that can FAIL the gate. A kernel body moved
> into an `.inc` would be in neither C rung's text, so a forbidden spelling could
> sit there unseen — which is exactly the honest-refactor escape route
> `harness/check.py::forbidden_only_sources` names and closes for `c/kernel.h`.

`controls/safety_line.py` makes the same claim by **measurement** instead: it
preprocesses both shipped files with `cc -E -P` and diffs them.

```
preprocessed kernel.c          235 lines
preprocessed kernel_hardened.c 237 lines
diff  +2 / -0
    + } else if (gen[h] != g) {
    + v = 251;                        (`SENT` is a macro)
```

It **fails** if the diff stops being a pure addition, if an added line is outside
the safety line, or if `gen[h] != g` appears at other than exactly one site. That
is strictly stronger than the include-twice construction, which makes the
property true by fiat and therefore cannot fail.

⚠ **`+2 / −0`, not `TASK_143`'s `+9 / −0`.** The demonstration had three
handle-consuming sites; here FREE, READ and WRITE share the handle decode, so
they share the guard and **one omitted source line carries both bug classes** —
which is `p29`'s shipped shape and the stronger form of the claim.

### 9b. Slots ARE recycled, where `p27` and `p29` never recycle

`p27`'s and `p29`'s `ntab` only grows, which is what reduces their generation
counter to one bit. **Recycling is what a free-list allocator does**, so p32
recycles, and the incarnation counter is what replaces the bit. `p29`'s `spec.md`
records that a slab-and-freelist spelling would be *"wrong on both bug classes and
bit-identical to buggy C, which is verbatim p32/p33's already-refused result"* —
⚠ **that sentence is still accurate about `p29` and its second half is no
longer a refusal**; p32 is that spelling, built, and the bit-identity is section
2's headline.

---

## 10. SLB-TRUSTED-ARGUMENT sections

The gate requires one per trusted item and prints it in full on every run. Three
items here, against `p27`'s and `p29`'s seven; the four differences are that p32
has no allocation API to borrow and therefore no `rec_alloc`/`rec_free`, and that
`load_input`/`emit` are outside the twin regime.

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's is `v[i]` on the same
`&[u8]`, with the same parameters and character-identical clause text. `v[i]` is
the checked form of the identical operation — rustc emits the bounds test
`i < v.len()` that `get_unchecked` requires of the caller — so a `requires` too
weak to license the unchecked read is too weak to license the indexed one, and
`--cfg slb_twin` would reject it. This is the same item every unsafe rung in this
project ships and it is unchanged here.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
read of one element, and returns it; `r == v@[i as int]` names that element and
its value, and `v: &[u8]` is immutable so nothing can be modified. The
completeness question is TASK_009_REVIEW's x4 — a body that also read `i + 1`
would satisfy this contract — and the answer is that the body is the one line
above and contains no second access. On p32 the window read is the *only* thing
this item is used for: `off + p + 1 < buf@.len()` is established by
`off + len <= buf@.len()` and `p + 2 <= len`, both loop invariants, so the caller
discharges the precondition with no arithmetic the reader cannot check.

**(c) Does each clause mean the same in both configurations?** `i < v@.len()` and
`r == v@[i as int]` mention only `i`, `v` and `r`; `v@` for a slice is
`vstd::slice`'s view in both configurations, `spec_slice_len` is the same
function, and nothing in the clause text is `cfg`-dependent. The `#[cfg(slb_twin)]`
twin differs from the trusted item in its body and in nothing else — the gate's
`_check_twin_cfg_hygiene` checks that mechanically.

## SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[T; N]`; the twin's is `v[i]` on the same
`&[T; N]`, same parameters, same clause text. For a fixed-size array `v[i]` is the
checked form of the identical operation — rustc emits the bounds test `i < N` —
so a `requires` too weak to license the unchecked read is too weak to license the
indexed one. **It is generic over `T: Copy` and `N` on purpose**: p32 indexes
*five* arrays with it — the pool `[u8; 32]`, the free-list links `[u8; 8]`, the
generations `[u32; 8]` and both handle-register arrays — and one item is one
axiom instead of five. Genericity does not weaken the argument, because the body
is `T`-independent and `vstd::array`'s `array_len_matches_n` supplies
`v@.len() == N` for every `N`.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
read of one element, and returns it; `r == v@[i as int]` names that element and
its value, and `v` is `&[T; N]` so nothing can be modified. ⚠ **On p32 every
`T` is a plain integer** — `u8` or `u32` — so there is no provenance, no pointer
and no interior mutability for the clause to be silent about, which is the one
place where p29's version of this argument has to work harder (its `T` includes
`*mut Rec`, where "the value read" has to mean address *and* provenance). Here
`Seq<u8>`/`Seq<u32>` equality is equality of the integer, and that is the whole
of what a read can produce.

**(c) Does each clause mean the same in both configurations?** Both clauses
mention only `i`, `v` and `r`, and `v@` for `[T; N]` is `vstd::array`'s view in
both. `N` is a const generic instantiated identically at every call site in both
configurations. Nothing in the clause text is `cfg`-dependent, and the twin
differs only in its body.

## SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }` on a `&mut [T; N]`; the twin's is
`v[i] = x;` on the same `&mut [T; N]`, same parameters, same clause text. `v[i] = x`
is the checked form of the identical store and rustc emits the bounds test `i < N`
that `get_unchecked_mut` requires of the caller, so `--cfg slb_twin` rejects a
`requires` too weak for either.

**(b) Is the `ensures` complete?** `final(v)@ == old(v)@.update(i as int, x)` is
an equality over the WHOLE sequence, so it says both what changed and — element
by element — that nothing else did. A body that also wrote `i + 1` would violate
it, which is the direction TASK_009_REVIEW's x4 asks about, and the body is the
one line above. The parameter `x` is unconstrained by any `requires` and that is
the parameter-coverage false positive `.memory/04-verus.md` names: `x` is a pure
VALUE, stored into the array and never used as an address, an index or a length,
so every `T` is a legal thing to store in a `T` slot. `spec.md`'s
`verus.unsafe_justifications` carries the same argument in the hashed block.

**(c) Does each clause mean the same in both configurations?** `i < old(v)@.len()`
and the `update` equality mention only `i`, `v` and `x`; `old`/`final` and
`Seq::update` are Verus builtins with one meaning, and `v@` for `[T; N]` is
`vstd::array`'s view in both configurations. Nothing is `cfg`-dependent and the
twin differs only in its body.
