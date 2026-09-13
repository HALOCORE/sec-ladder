# TASK_PHP_045 — BUILD **ROW 8 = `ph52`**: an unconstructed caller slot destructed on an early exit, and the defect is **silent on a clean stack**

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_045_REPORT.md` — **write the FILE** (rule 10).

✅ **THE THREE CONDITIONALS THIS BRIEF CARRIED ARE NOW SETTLED BY `TASK_PHP_043`.**
**F94 is UPHELD-NARROWED** — ⭐ **and its narrowing does NOT touch `ph52`**: what
was withdrawn is the *screen* route for excluding `ph53`'s wrong sha, while
`ph52`'s R1h was confirmed on a different route (a `CANDIDATE` verdict on a
**unique** cited line) and `_040` recorded that `ph52` *"never reaches the
branch"* the repair changed. ✅ **Re-verified: the new `MIN_LEADING_CONTEXT` guard
has measured reach `0` on the whole corpus.** So **§2.1 stands and no R1h hunt is
in scope.** **F98 is UPHELD-NARROWED** with four qualifiers (§2.9 restates them).
⚠⚠ **F97 IS STILL UNREVIEWED**, so §2.9's prediction rests partly on a finding
whose cycle is open — **it is a prediction either way, and that is said there.**

⚠⚠⚠ **EVERYTHING IN §2.3–§2.5 AND §2.9 IS THE MANAGER'S ANALYSIS, FROM READING
THE PRISTINE C AND TWO MEASUREMENTS ON THIS BOX. NONE OF IT HAS BEEN COMPILED.**
▶ **It is handed over as stated hypotheses WITH the measurements that produced
them, and the engineer's first job is to break them.** ⭐ **Saying *"the
manager's §2.4 is wrong and here is the disassembly"* is the most valuable thing
this task can return** — `_040` did exactly that to my recommendation and was
right.

---

## §1 Why this row

1. **It is `T3`'s last owed row.** `quota.py`: `T3 5 1 OWES 1`, and `ph53` is the
   one built. Building it **closes a family**.
2. ⭐⭐ **It carries a live falsifiable prediction: item 76 says the R1h column is
   `0.00 %`.** The fix deletes one `zval_dtor` from an arm the benign corpus never
   runs. ⛔⛔ **A `0.00 %` R1h column is a FINDING, NOT A DISQUALIFICATION** —
   `CLAUDE.md` rule 6 and finding 53: *"no column moves"* is never a kill. ⭐ **What
   it says is publishable: the upstream fix for a whole CLASS of defect — the
   unreached error path — is FREE, and the ladder can put a number on it.**
3. ⚠ **Item 81 predicts your `controls/spellings.py` will find a FIFTH defect in
   the shared machinery.** The law is monotone in suite size: 54 cases missed two,
   75 missed one, 128 found one, 161 found the fourth. ▶ **You are cloning
   `ph53`'s control, which is the most-repaired in the tree and still carried a
   path-sensitive `kernel_fingerprint`. Write NEW negatives, not inherited ones.**
4. ⛔ **"Cheapest candidate" is WITHDRAWN from the START HERE box.** `_040` §7.2
   ranked this row **below** `ph53` on three measured grounds and I did not carry
   two of them forward. **The honest phrasing is *lowest-risk R1h, highest-risk
   adversarial input*, and §2.3 is why.**

---

## §2 The manager's decisions

### 2.1 ⚠ THE R1h IS `7412202c43e7` — settled, but it is a **HAND RECONSTRUCTION** and it owes an argument

`_040` §2.1: **CONFIRMED**, screen = `CANDIDATE` confidence HIGH, §F5(iii)
confirms, **a one-line deletion**, and **complete** — because
`expr_copy->type = IS_STRING` sits at **`zend.c:263`, *after* the switch**, so
deleting the `zval_dtor(expr_copy)` at `:243` leaves no path that tears down an
unconstructed slot.

⛔⛔ **BUT: `ph53`'s `kernel_hardened.c` is a `patch -p1`; THIS ONE IS NOT.**
`_040` `13-backport-apply.log`: **`ph53` applies to pristine 5.0.0, `ph52` does
not.** ▶ **So §C's *"R1h is the real upstream fix"* is satisfied by a HAND
RECONSTRUCTION here, and §C requires the argument in writing.** **Deliver: the
diff of the two C kernels, beside the upstream hunk, with every token that
differs accounted for** — `ph53`'s `why` is the model (*"the only tokens that
differ from the tarball's own line are the narrowed type name and the shim's
allocator prefix"*).

### 2.2 TIER — **declare what you measure**, not the catalogue's label

`CATALOGUE.md:146` declares **`narrowed`**. `_040` §5.1 judged **both** row-7
candidates' tiers optimistic and judged `ph52`'s optimistic too; open item 75
asks whether the whole catalogue is optimistic **in the same direction** (2 of 2
examined so far). ⓘ **A tier is a COST STATEMENT, NEVER A FILTER** — declaring a
worse tier refuses nothing. ▶ **Declare what the extraction actually needs and
itemise why**, as `ph53` did. ⭐ **And you are the THIRD data point for item 75;
say which direction you land.**

### 2.3 ⛔⛔⛔ DELIVERABLE #0 — **STACK DETERMINISM.** THIS ROW'S UNINITIALISED MEMORY IS ON THE **STACK**, AND EVERY MECHANISM THIS TREE HAS FOR UNINITIALISED MEMORY IS AN **ALLOCATOR** SHIM

**The C, from the pristine tarball** (`5783e0c0ba94f165…`):
`Zend/zend_operators.c:1146` `concat_function` declares **`zval op1_copy,
op2_copy;`** — bare locals, **no `= {0}`, no `INIT_ZVAL`, no `memset`** — and
passes `&op1_copy` to `zend_make_printable_zval`, which writes
`expr_copy->value.str.*` on every arm and `expr_copy->type` **once, at `:263`,
after the switch**. The faulting arm is `:242-247`:
```c
if (EG(exception)) { zval_dtor(expr_copy); … break; }
```

**MEASURED ON THIS BOX** (⭐ **`.tasks-php/asan_fill_byte.c`, COMMITTED** — its
rebuild line is in its header, and it is committed rather than left in `.temp/`
for open item 86's reason; `~/tools/llvm/bin/clang -O1 -fsanitize=address`):

| | fresh `malloc(64)` | un-initialised `stack[64]` |
|---|---|---|
| **with ASan** | `be be be be be be be be` | **`00 00 00 00 00 00 00 00`** |
| **without** | `00 00 …` | **`00 00 …`** |

**AND FROM THE PRISTINE C** — `Zend/zend.h:387-392`: **`IS_NULL 0`**,
`IS_STRING 3`, `IS_ARRAY 4`, `IS_OBJECT 5`; `Zend/zend_variables.c:36-57`
`_zval_dtor` switches on `zvalue->type & ~IS_CONSTANT_INDEX` over **`IS_STRING`,
`IS_CONSTANT`, `IS_ARRAY`, `IS_CONSTANT_ARRAY`, `IS_OBJECT`** and has **no
`case IS_NULL`**.

> ⛔⛔⛔ **THEREFORE: A CLEAN STACK SLOT READS ZERO, ZERO IS `IS_NULL`, AND
> `zval_dtor` IS A NO-OP ON IT. ⭐ THE DEFECT IS SILENT ON A FRESH STACK.**
> ▶ **It fires only when a prior frame left a freeing tag at that offset, and
> `ph53`'s `0xbe` determinism came from ASan's malloc fill — ⭐ **and it is a
> RUNTIME OPTION DEFAULT, not even a compile-time property: the same binary under
> `ASAN_OPTIONS=malloc_fill_byte=0` returns zeros** (`_044` §7.1, re-measured by
> me) — a mechanism that
> does not exist for the stack.**

⭐⭐⭐ **THE MANAGER'S HYPOTHESIS FOR HOW TO GET DETERMINISM, AND IT IS FREE IF
IT HOLDS — ATTACK IT FIRST.** The pinned driver loop calls
`kernel(buf, k*stride, stride)` **`n_iters` times**. ▶ **So iteration 2's
`op1_copy` sits at the same stack offset as iteration 1's, which wrote
`type = IS_STRING` at `:263` and a heap pointer into `value.str.val`.** Under
that reading:

* **iteration 1** — clean stack, `IS_NULL`, `zval_dtor` no-ops, **no fault**;
* **iteration 2+** — reads the previous iteration's `IS_STRING` and **frees the
  previous iteration's already-freed pointer** → **a double free / UAF**;
* ⭐ **and it is FAITHFUL** — real PHP calls `concat_function` repeatedly, which
  is exactly why this bug was reachable at all.

⚠⚠ **FOUR WAYS THAT HYPOTHESIS CAN FAIL, AND YOU MUST CHECK ALL FOUR BECAUSE
THIS ROW IS MEASURED AT `{gcc,clang} × {O0,O3}`:**

1. **The compiler may keep `op1_copy` in registers**, in which case there is no
   stack slot and no garbage. ⓘ It is passed **by address** to a callee, so it
   must be addressable — **unless the callee inlines.**
2. ⭐⭐ **AND THAT MAKES THE TRANSLATION-UNIT BOUNDARY LOAD-BEARING.** The harness
   measures **`isolated` AND `whole`**. In `isolated` the callee is a separate TU
   and cannot inline; in `whole` it can. ▶ **PREDICTION, REGISTERED: the defect may
   be PRESENT in `isolated` and OPTIMISED AWAY in `whole`.** ⭐ **If that holds it
   is a row property no built row has — a memory-safety defect whose existence
   depends on the TU boundary — and it is a finding either way.**
3. **Stack reuse may not be exact** — a different frame layout between
   iterations, or a `-O3` frame the compiler re-orders. **Verify the offset, do
   not assume it.**
4. ⛔ **`-ftrivial-auto-var-init`, stack poisoning, or any `-fsanitize` stack
   mode DELETES the defect.** ▶ **The catalogue's trap — *"an extraction that
   zero-initialises the slot for tidiness deletes it"* — applies to the COMPILER,
   not only to the author. Record the exact flags, and if a sanitizer run needs a
   flag that kills it, say so rather than changing the kernel.**

**FALLBACKS, in order, decided here so they are not improvised mid-build:**
* **(a)** the driver-loop reuse above, verified on all four cells;
* **(b)** an explicit prior call inside the kernel that writes a chosen tag at the
  same depth — **more robust, slightly less faithful, and it must be declared in
  the divergence ledger**;
* **(c)** accept the nondeterminism, pin the benign path, and put the adversarial
  demonstration in **`controls/`** — ⭐ **this is F31's prescription and exactly
  what `ph53` had to do for a different reason** (item 77). **It is a legitimate
  outcome, not a failure.**
* ⛔⛔ **(d) NOT AVAILABLE: moving the slot to the heap so the shim applies.**
  That is infidelity to the one declaration the row exists to extract.

### 2.4 ⭐ A PIN THE CATALOGUE DOES NOT ASK FOR: **THE WRITE ORDER**

The defect lives in the fact that `expr_copy->type` is written **last**. ▶ **Any
kernel that writes the tag early — the natural, tidy ordering — deletes the
defect while keeping every line that looks load-bearing.** ⭐ **So
*value-first, tag-last* is a PINNED ORDERING and belongs in `idiom.required`
with that reason attached.** ⚠ This is `ph53`'s `required[1]` lesson exactly
(*"it is a whole statement away from the second, which is why the kernel keeps it
as its own loop"*).

### 2.4a ⛔⛔ ITEM 83 IS RULED, AND IT BINDS EVERY `required` ENTRY YOU WRITE

`.memory-php/02-ladder.md`, landed 2026-09-13: **a backticked span in
`idiom.required` pins the REPRESENTATION; the entry's ENGLISH decides which rungs
it scopes to; and the mechanical presence report decides NOTHING.** ⭐ **The
clause that does the work is the LEADING APPOSITIVE** — on `ph53` it was *"THE
ONE-BYTE-PER-SLOT WITNESS"*, and that is what excluded a cheaper `u32` bitmask.
▶ **So when you write an entry: the appositive is the pin's definition and
everything after it is commentary. Write it deliberately.**
⚠⚠ **`ph53` cost a published headline because its appositive and its summary
disagreed about what was pinned.** ⭐ **You are writing these from scratch, which
is the cheapest moment in the row's life to get them right — `ph53`'s repair is
costing a whole re-gate.**
⛔ **And `required` CANNOT FAIL THE GATE.** `harness/check.py::idiom_audit`
measures the naive every-span-in-every-rung reading at **41 misses of 158
obligations, all 41 non-defects, 17 of them ANTI-signal** (an entry may quote a
span **in order to say it is ABSENT**). ▶ **So do not write an entry expecting the
gate to enforce it; write it so a READER can.**

### 2.5 ⚠⚠ THE HARM IS A TAG-DISPATCHED **FREE**, NOT A READ — AND A KERNEL THAT ONLY BRANCHES HAS BUILT A WEAKER ROW

`_zval_dtor`'s `IS_STRING`/`IS_ARRAY`/`IS_OBJECT` arms **release a pointer read
out of the same uninitialised slot**. ▶ **So the demonstration needs the free.**
ⓘ The row still belongs in **T3** — the *cause* is an uninitialised read — but a
kernel whose teardown merely selects an arm has dropped the consequence.

⭐⭐ **AND THE ROW CAN PUBLISH SOMETHING NO BUILT ROW CAN: THE HARM IS
CONDITIONAL ON THE GARBAGE VALUE, AND THE CONDITION IS COUNTABLE.** Five named
cases out of a byte, widened by the `& ~IS_CONSTANT_INDEX` mask. ▶ **A
`controls/` sweep over the tag byte `0..255` counting which values free is the
whole control, and it is cheap.** ⭐ **That number is the answer to *why do
uninitialised-read bugs survive for years in shipped code* — which is exactly what
a reader of this ladder needs.** ⚠ **UNTESTED: read off the `switch` and the
mask, not compiled. Measure it; do not quote my five.**

### 2.6 §A4 — **THERE IS NO CRASH ANCHOR, AND THE REASON IS THE MECHANISM**

⚠ **ATTRIBUTION, because F87's defect was exactly this.** `uninit-read-silent`
I verified **directly**, in
`.tasks-php/TASK_PHP_001_MINE/type/NOTES.md:398` (*"corpus `vuln_class =
uninit-read-silent`"*). **`n/a (non-crash class)` I did NOT** — it is
`TASK_PHP_040_REPORT.md:221` quoting `index.csv`, and **`index.csv` is not in
this repository**. ▶ **Re-read it from the corpus before you rest anything on
it.** For contrast, CRASH-158 gave `ph53`
`crashes_pristine_5_0_0 = True` / `asan` / `wild-pointer-deref`.
ⓘ And `FIXSURVEY_001.md:242` dates `7412202c43e7` to **2006** — *"no need to
destroy the zval here"*, 1 file — **so the fix is in no 5.0.x release at all**,
which is consistent with §2.1's patch not applying to pristine 5.0.0.
§A4 asks for the **recorded** category, and *"reproducing a DIFFERENT signal is a
finding to state, not a failure to hide."*

⭐ **§2.3 explains WHY it is recorded silent rather than merely noting that it
is:** most garbage is zero or is not one of the freeing tags, so in the wild the
teardown usually no-ops. ▶ **Deliver that as the §A4 answer**, and **expect ASan
to fire on the double free where the corpus says silent** — state the divergence,
with the exact diagnostic.

### 2.7 §B1a — declare the allocation order, and this row probably satisfies the precondition

`PROTOCOL_PHP.md` §B1a.2 requires the allocation order **declared in
`idiom.required`**, and §B1.2's cancellation is free only at **O(1) allocations
per kernel call**. ⓘ The benign path `estrndup`/`emalloc`s the printable string
and the teardown frees it, so **O(1) per call looks right** — ▶ **but count it,
declare it, and if it is not O(1), §B1a tells you exactly what to do instead**
(label the cross-language figures; it is **not** a refusal). ⭐ **`ph53` is the
declared exception that made §B1a's precondition hold; this row is the second
test of it.**

### 2.8 ⭐⭐⭐ WHICH STATISTIC — **MEASURE `inside_share` FIRST AND LET IT DECIDE. DO NOT ASSUME `A1`.**

⛔⛔ **THIS IS NEW AND IT REPLACES THE RULE THE LAST THREE ROWS WERE GIVEN.**
`TASK_PHP_043` §3 settled open item 78 and **refuted BOTH earlier candidate
axes** — *same-language vs cross-language* (F91's, refuted on its own table: all
nine of its cells are same-language and separate by `|Δ|`) and *does the callee
work diverge* (refuted because **a sign flip ENTAILS callee divergence, so the
variable does not vary**).

> ⭐ **THE RULE, now in `.memory-php/03-numbers.md`: family A resolves a code
> difference exactly to the extent the difference lands INSIDE THE KERNEL SYMBOL,
> and the measure of that is `inside_share` — which is ALREADY COMPUTED FOR EVERY
> CELL IN EVERY RECORD.**

▶ **So: compute `inside_share` for this row's cells, THEN choose the headline
column, and say which and why.** **`ph45` at 9.5 % published in W1; `ph53` at
89.5 % published in A1; both were right.** ⚠ **Your row's kernel inlines a
`zval_dtor`-shaped teardown, so do not guess which side of that you land on —
measure it.**
⚠⚠ **AND A ROW'S SPREAD OVER RESPELLINGS IS A FACT ABOUT ITS VARIANTS, NOT ABOUT
THE STATISTIC** (item 82): `ph45`'s A1 spread is `0.000000` pp over nine variants
and `ph53`'s is `39.9`/`45.3` pp over 20. ⛔ **Do not quote either as evidence
about family A.**
▶ **Quote BOTH columns, labelled, always**, and ⛔ **never a percentage without
saying which input, which statistic, which level, and what it is measured
against** — **F98 shipped missing all four** (item 84, `_043` §5.2).

### 2.9 ⭐⭐ TWO PREDICTIONS, REGISTERED BEFORE ANY RUNG EXISTS

⚠ **F98's figure, with the four qualifiers `_043` §5.2 found it owed**: the
witness costs **`+21.775 %`** in **W1**, on **`small.bin`**, at **`O3/isolated`**,
**against `controls/r4_nowitness.rs` — a RUST control, NOT against the C** — and
**only ~44 % of it is the witness** (`+101.59` of `+228.87` `Ir`/call; the rest is
the array being in memory at all). ▶ **Quote it that way or not at all.**
⚠⚠ **And F97 is UNREVIEWED**, so the *"jointly unsatisfiable"* claim beneath this
prediction has not had a reviewer. **Treat it as the strongest available guess,
not as settled.**

1. **F97/F98 RECUR, HARDER.** The uninitialised datum here is a **discriminant**.
   **R2/R3 cannot reproduce it at all** — Rust has no uninitialised `enum` tag
   that is safe to name (ⓘ **a FINDING, never a kill**). **R4/R5**: reading an
   uninitialised discriminant is UB when the value is *produced*, not when it is
   *matched*, so `MaybeUninit::<Tag>::assume_init` needs `is_init()`, which is a
   property of the **failure flag** — attacker data — exactly as on `ph53`.
   ▶ **Predicted: the faithful R4 is again a `controls/` program and not a rung,
   and the shipped R4 again carries a witness the C does not.**
2. ⭐⭐ **AND A WAY IT SHOULD DIFFER, WHICH IS WHAT MAKES (1) FALSIFIABLE RATHER
   THAN SAFE.** `ph53`'s witness is **per-slot** — `n` bits, and F98 priced it at
   **`+21.8 %`**. `ph52`'s is **one slot, one bit**: `constructed: bool`.
   ▶ **Predicted: the witness is ~FREE here.** ⭐ **If it is free on `ph52` and
   dear on `ph53`, then the cost of a safety witness is O(the number of slots) and
   not a constant — a better statement than either row gives alone, and the first
   two-row law on the `T3` axis.**

---

## §3 Traps

1. ⚠⚠⚠ **`grep -a` ALWAYS** (F35): 41 corpus files exit 1 silently under plain
   `grep`, and a probe script does not reproduce it. ⭐ **And a line-based grep
   cannot find a prose phrase that WRAPS.**
2. ⛔ **Never publish a percentage without WHICH INPUT and WHICH STATISTIC**
   (`check.py`'s own *DO NOT MAX IT OVER INPUT*).
3. ⚠ **A magnitude floor with every sign claim.** An outlier test in this
   programme once fired at `0.00 pp`.
4. ⚠ **`controls/*.py` is a VALIDATOR and §H binds**: it lands with its must-fire
   **and** must-NOT-fire negatives, or it does not land. ⭐ **`ph45`'s bar was 128
   cases; `ph53`'s 161 found the fourth shared defect. Item 81 predicts yours
   finds a fifth — write NEW negatives.**
5. ⚠ **Know which digest every edit touches.** `inputs/gen.py`, the `.rs` rungs
   and `c/*` are in the **MEASUREMENT** digest (an edit costs a 32-cell
   re-measure); `spec.md`, `NOTES.md` and `controls/*` are **gate-only** (one
   re-gate). ▶ **Say which side of that line each edit is on.**
6. ⛔⛔ **`PROTOCOL_PHP.md` §F6: `spec.md` and `NOTES.md` must not cite `.temp/`.**
   Commit the probe under `controls/` or restate the claim without the pointer.
   **`python3 .tasks-php/citecheck.py` is how you check you are done.**
7. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match; no
   `until … sleep` poller loops.
8. ⚠ **`.temp/` is gitignored** — numbers go in your report, not behind a pointer.
9. ⚠ **A truncated `ls`/`head` is not evidence of absence.**
10. ⓘ **`verus_checked` and `problems` are NOT gate-record fields.** They live in
    `controls/spellings.json`; `problems` is also a preflight field. **Name the
    file any field came from** (F99).
11. ⚠⚠⚠ **ADMISSION IS C-SIDE ONLY.** *"Safe Rust can't express it"*, *"no column
    moves"*, *"Miri doesn't see it"*, *"the R5 can't state the obligation"* are
    **ALL FINDINGS, NEVER KILLS** (`CLAUDE.md` rule 6, finding 53). ⭐ **This row
    will test it twice — at §2.9(1) and at item 76's `0.00 %` column.**

**Scope:** ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **No edits under `harness/`, `common/`, `common-php/`, `patterns/`,
`results/`, `pilot/`, or any `patterns-php/` row other than the new one.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`. Scratch under `.temp/`.
**Brackets**: `harness/measure.py --check-stale` → `66/0` and
`harness-php/gate.py --tool measure --check-stale` → `16/0` **first**; the php
figure **rises by 2** when the row's records land and **nothing else moves**.

---

## §4 Definition of done

1. ⭐ **DELIVERABLE #0 FIRST AND IN WRITING: stack determinism, on all four C
   cells, with the fallback you took and why** (§2.3). ⛔ **Do not start the Rust
   rungs before this is settled** — every later number depends on it.
2. **The row built and gated**: `spec.md`, `model.py` with its independent second
   implementation **and its mutant sweep** (§A2a rule 2), `inputs/gen.py` +
   blobs, `c/{kernel,kernel_hardened,main}.c`, four rungs, `controls/`,
   `NOTES.md`, `README.md`. **Quote `verdict`, `failures`, `complete_run`, the
   `identity` levels and `contract_sha256` AS FIELDS.**
3. **§2.1's R1h argument**, token by token, since it is a hand reconstruction.
4. **Item 76 TESTED**: is the R1h column `0.00 %`? ⭐ **Either answer is a result**
   — and if it is not `0.00 %`, say where the cost came from.
5. **§2.9's two predictions tested**, each UPHELD or REFUTED with the evidence.
6. **§2.5's tag sweep** as a `controls/` program with its own negatives, and the
   measured count of freeing tag values.
7. **§2.2's tier**, declared with its itemisation, and **your direction on item
   75**.
8. ⚠ **WHAT YOU ARE UNSURE OF, in its own section.** ⭐ **`UNTESTED` and *"I could
   not tell"* are VALUED ANSWERS** — `_039` shipped a negative's failure, `_040`
   shipped a defect it could not fix, `_041` reported 15 uncertainties and found
   its own citation defect. **All three were the right call.**
9. ⭐ **EVERY `§2.3`–`§2.5`/`§2.9` HYPOTHESIS OF MINE THAT YOU BROKE, named.**
   **I have not compiled any of it.**
