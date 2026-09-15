# ph96 — NOTES

**`spec.md`'s contract is the declaration. This file is the MEASUREMENTS**, and
it is gate-only: nothing here is in `contract_sha256`, so a claim in it costs a
re-gate to repair and not a 32-cell re-measure. That is why the arguments a
`c/*` comment may only POINT at live here (`PROTOCOL_PHP.md` §F6a).

> ⚠ **`contract_sha256` DISCLOSURE, `PROTOCOL.md` rule 6.** As FIRST written,
> before any measured cell existed:
>
> ```
> a2f4c7e4ebf430b834bebdd315bf04ef17e50409daec539b9baa0aa6a5dcb92c
> ```
>
> **It moved twice, both times before the first gate run and both times for a
> reason recorded here rather than quietly:**
>
> 1. ⛔ **`tier` went from `narrowed` to `modelled`** when
>    `harness-php/provenance.py` measured the kernel overlap at **14.63 %**
>    against the 25 % `narrowed` leads a reader to expect (§11 below).
>    → `0e8ec5f76d7c0ead839ce7124164dd8cb7a65cc59e9b6e351ae4ee4720e1bdc1`
> 2. ⛔ **one backticked span in `idiom.required[1].rust` PINNED NOTHING** —
>    `char *retval = NULL` is a C-language spelling inside a rust-keyed entry,
>    which is
>    item 100's class exactly. The gate's stage 0b reported it (*pins nothing —
>    0 of 4 rungs*) and it became prose.
>    → `5369b3cf318777f5eaff415f32a5398405e5317e513f3ebd4f39d0dabf3fe815`
> 3. ⛔⛔ **AND THE REPLACEMENT PROSE DID IT AGAIN, IN THE SENTENCE EXPLAINING
>    IT.** The new text read *"a pin on it inside a `rust`-keyed entry would pin
>    NOTHING"* — and the backticks round the word made `rust` a fifth pin, which
>    `controls/spellings.py` then reported as **4 of 72 obligations
>    unsatisfied**. ▶ **Item 100 is now at four instances in four tasks, and the
>    fourth is a document about item 100.** §13.
>    → `8bef92ba9cd15f926a55e3f3f66d8f4023bc9a7413bedd8ab1aad6a081471350`
>
> ⚠ **QUOTED AS AN EVENT, NEVER A STATE** (F119/M2): the third value is what the
> file hashed to when this line was written. Re-read it against
> `results-php/gate/ph96-outparam-unwritten.json`.

---

## §1 WHAT THE ROW IS, IN FIVE LINES OF UPSTREAM C

```
Zend/zend_execute_API.c
 592  /* we may return SUCCESS, and yet retval may be uninitialized,
 593   * if there was an exception...
 594   */
 595  *fci->retval_ptr_ptr = NULL;
 ...
 870  if (EG(exception)) { zend_throw_exception_internal(NULL TSRMLS_CC); }
 873  return SUCCESS;
 389  (*zval_ptr)->refcount--;                       /* _zval_ptr_dtor's FIRST */

Zend/zend_object_handlers.c
 509  zval *retval;
 512  zend_call_method_with_1_params(&object, ce, NULL, "offsetunset", &retval, offset);
 513  zval_ptr_dtor(&retval);
```

**All line citations verified exact against the pristine tarball**
(`sha256 5783e0c0…d6919`) on 2026-09-15, by this task.

⭐⭐ **THE STATUS IS TESTED AND THE OUT-PARAMETER IS NOT.**
`Zend/zend_interfaces.c:81-87` tests `result == FAILURE` and raises
`E_CORE_ERROR`, which does not return. `I12/O1` lists four things — *a NULL
return, sentinel, status code, **or NULL-able out-parameter*** — and it is the
last one nothing looks at. That is what separates this row from `ph60`
(*a fallible call's failure not tested*): **the call succeeds.**

---

## §2 ⭐⭐⭐ CRITERION 2, MEASURED — the four-handler matrix, RE-RUN

Recorded as an EVENT (`PROTOCOL_PHP.md` §A3a step 6): what was run, on which
binary, on which date, what came back.

**Date:** 2026-09-15.
**Binary:** `/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext`
— `-v` prints `PHP 5.0.0 (cli) (built: Aug  5 2026 09:26:33)`.
**Probe:** the committed `.tasks-php/probes/ph96_arrayaccess_matrix.sh`, which
builds its shim from the committed `.tasks-php/probes/segaddr.c`.

```
$ sh .tasks-php/probes/ph96_arrayaccess_matrix.sh
HANDLER        SITE   CONTRACT                   RC      FAULT
offsetGet      :384   output + GUARD :385        rc=255  none   ok
offsetSet      :413   NO-OUTPUT (NULL)           rc=255  none   ok
offsetExists   :427   output, UNGUARDED          rc=139  0x14   ok
offsetUnset    :512   output, UNGUARDED          rc=139  0x10   ok
benign(none)   --     nothing throws             rc=0    none   ok

MATRIX AS EXPECTED -- 2 guarded cells clean, 2 unguarded cells faulting at
DISTINCT offsets that match offsetof(zval,refcount)=0x10 and (zval,type)=0x14.
```

* **`rc=255` is PHP's OWN `Fatal error: Uncaught exception 'Exception' with
  message 'boom'`** — the CORRECT behaviour, not a silent wrong answer. The text
  was read, not inferred from the code.
* ⭐ **§A3a step 4, REPRODUCIBILITY: FIVE runs each of the two faulting
  scripts.** `offsetUnset` gave `rc=139 si_code=1 si_addr=0x10` **5/5**;
  `offsetExists` gave `rc=139 si_code=1 si_addr=0x14` **5/5**. ▶ This row is the
  strongest of §A3a's three categories: **a stable signal WITH a stable
  address** — unlike `ph75` (three different signals) and `ph79` (four `si_addr`
  values in four runs under ASLR).

### ⚠⚠ THE TWO CAUTIONS, REPEATED (a row that omits them has over-claimed)

1. **Name the build.** That binary is **php-in-safe-rust's oracle build**
   (mysql + webext), **not** a museum-default one. A fault address is a property
   of a build.
2. **A clean run would NOT have been evidence of absence** (`RECAP_PHP.md` F3).
   The converse is the half this programme long lacked: **a run that faults,
   executed, is evidence of PRESENCE.** `crashes_pristine_5_0_0 = True`,
   executed.

⚠⚠⚠ **AND ON THIS ROW CAUTION 2 IS NOT A FORMALITY — §6 MEASURES IT FIRING.**

---

## §3 ⭐⭐ THE C RUNG REPRODUCES IT **AT THE STRUCT OFFSET**, AND THAT IS ASSERTED AT BUILD TIME

```
$ LD_PRELOAD=<segaddr.so> <gcc -O1 -g R1> inputs/adversarial-unset.bin
[segaddr] SIG11 si_code=1 si_addr=0x10
EXIT=139
$ LD_PRELOAD=<segaddr.so> <gcc -O1 -g R1h> inputs/adversarial-unset.bin
15642763268152511488
EXIT=0
$ LD_PRELOAD=<segaddr.so> <gcc -O1 -g R1> inputs/small.bin
18106149370596871061
EXIT=0
```

**Byte for byte the string the PHP 5.0.0 CLI printed for `offsetUnset`.**

⭐⭐⭐ **AND THE ADDRESS IS A HARDER TARGET THAN `ph97`'s `(nil)`.** `0x10` is
`offsetof(zval, refcount)` and `0x14` is `offsetof(zval, type)`; both follow from
`Zend/zend.h:270-293` on LP64, because `zend_object_value` is
`{zend_object_handle handle; zend_object_handlers *handlers;}` and so the
`zvalue_value` union is 16 bytes. **`c/kernel.c` holds its own zval to exactly
those offsets with three negative-array-size assertions**, so the match is a
BUILD-TIME property of the extraction rather than a coincidence of one run.

`controls/fault_addr.py` proves those assertions are load-bearing rather than
decorative — a mutant that pads the zval so `refcount` moves off `0x10`
**fails to compile**:

```
A. N1 MUST-FIRE  a zval with refcount off 0x10 -> BUILD REFUSED (ok)
   error: size of array 'ph96_assert_refcount_10' is negative
```

and it re-runs both limbs on both compilers:

```
cell          limb                   rc  si_addr   want
c-gcc-R1      unset (:512-513)      139  0x10      0x10      ok
c-gcc-R1      exists (:427-429)     139  0x14      0x14      ok
c-gcc-R1h     unset (:512-513)        0  None      None      ok
c-gcc-R1h     exists (:427-429)     139  0x14      0x14      ok
c-clang-R1    unset (:512-513)      139  0x10      0x10      ok
c-clang-R1    exists (:427-429)     139  0x14      0x14      ok
c-clang-R1h   unset (:512-513)        0  None      None      ok
c-clang-R1h   exists (:427-429)     139  0x14      0x14      ok
```

⚠ **THE MATCH IS OF MECHANISM, NOT OF TOOLCHAIN.** The CLI half is the oracle
build; the kernel half above is `gcc -O1 -g`; §6's sweep is a third set again.
Same signal, same `si_code`, same addresses; different builds.

---

## §4 ⭐⭐ R1h IS A **BACKPORT**, AND THE WORD IS LOAD-BEARING

`controls/r1h_backport.py`, run on every invocation, verdicts taken **from the
bytes**:

| question | answer |
|---|---|
| **does the cached patch BIND?** | ✅ `From cf020f133487d36a8b1d9cfd16ec456f7f07952e`, filename `cf020f133487.patch` — **not** one of F115's three mis-bound patches |
| **does `git apply --check` place it on pristine 5.0.0?** | ⛔ **NO. `rc=1` at the default width, at `-C1`, at `-C0` and at `-3`** |
| why not | the pre-image carries `SEPARATE_ARG_IF_REF(offset);` and `zval_ptr_dtor(&offset);` — **two context lines 5.0.0 does not have**, read out of the patch rather than assumed |
| **does the three-line hand backport reproduce upstream's own diffstat?** | ✅ **`1 file changed, 1 insertion(+), 3 deletions(-)`**, against the commit header's `Zend/zend_object_handlers.c \| 4 +---` |
| **is that what `c/kernel_hardened.c` does?** | ✅ nine of the ten functions are **IDENTICAL** between the two C rungs; `ph96_unset_dimension` differs by exactly the local, the call and the dtor |
| `preimage_screen.py --row ph96 --verbose` | **`CANDIDATE`, 1 record, `0` NOT-THE-REPAIR exclusions.** ⚠ `CANDIDATE` is the screen's *positive* label and under `PROTOCOL_PHP.md` §C it says **nothing** either way — only `NOT-THE-REPAIR` is a proof. **Cite 0 exclusions, not 0** (F68/D11) |

⚠ **`ph55` NOTES §5's trap was designed for.** The scratch `git init` repo's
`rev-parse --show-toplevel` is asserted equal to the scratch directory, so the
outer repository's gitignore cannot reach it, and no verdict is read from an
exit status that could be `head`'s.

### §4.1 ⭐⭐⭐ `PROTOCOL_PHP.md` §A3a OBLIGATION 5, DISCHARGED ON REAL PHP

`controls/rebuild_hardened_php.sh` — a row-local adaptation of the committed
`.tasks-php/probes/rebuild_hardened_php.sh`, whose step 4 is pinned to `ph97`
and which is **not edited**:

```
sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
COLD_BUILD_WALL_SECONDS=30
  pristine offsetUnset  rc=139 (expect 139)
  pristine offsetExists rc=139 (expect 139)
  backport applied at :509/:512/:513          <- and the diff is printed
INCR_REBUILD_MS=611
  hardened offsetUnset  rc=255 (expect 255 -- PHP's own Uncaught exception fatal)
  hardened offsetExists rc=139 (expect 139 -- THE SECOND LIMB, UNREPAIRED)
```

**Thirty seconds and 611 ms, no sudo, no network, 60 MB deleted after** — the
costs `RECAP_PHP.md` F123 measured, reproduced. ⭐ **The fix's efficacy is
measured on the interpreter itself and not only on the kernel**, which is the
strongest evidence a row can carry about its own R1h.

⚠ The patch could not be applied with `patch -p1` for the reason in the table
above; the script performs the three-line edit in place and **prints the diff**,
so a reader can compare it with the commit.

---

## §5 ⛔⛔⛔ THE SECOND LIMB — `:427-429` — AND THE SCOPE OF WHAT THIS BOX CAN SAY

`zend_std_has_dimension` at `zend_object_handlers.c:427-429` calls the **same
helper** with the **same output contract** and guards nothing, dereferencing the
sentinel **twice**: `:428 i_zend_is_true(retval)` reads `op->type` at `0x14` and
`:429 zval_ptr_dtor(&retval)` writes `refcount` at `0x10`. **The catalogue's
`ph96` entry names only `:509`/`:512-513`.**

⭐⭐⭐ **`cf020f133487` DOES NOT TOUCH IT, AND THIS ROW MEASURES THAT RATHER THAN
ARGUING IT.** `controls/second_limb.py`, six rungs × four sentinel states:

```
cell            exists        unset         read          write
c-gcc        rc=139 0x14   rc=139 0x10    rc=0 ok      rc=0 ok
c-gcc-h      rc=139 0x14     rc=0 ok      rc=0 ok      rc=0 ok
safe_naive     rc=0 ok       rc=0 ok      rc=0 ok      rc=0 ok
safe_tuned     rc=0 ok       rc=0 ok      rc=0 ok      rc=0 ok
unsafe         rc=0 ok       rc=0 ok      rc=0 ok      rc=0 ok
verus          rc=0 ok       rc=0 ok      rc=0 ok      rc=0 ok

  unset_limb_repaired_by_cf020f133487          True
  exists_limb_repaired_by_cf020f133487         False
  exists_limb_faults_in_both_c_rungs           True
  no_rust_rung_faults_on_either_limb           True
```

and §4.1 reproduces it **on a rebuilt, patched PHP 5.0.0** (`hardened
offsetExists rc=139`).

⚠ `PROTOCOL_PHP.md` §C says it in terms: *"An upstream fix is not automatically
correct. The earlier attempt measured one that, backported, still left a
reachable wild write in the arm it does not guard. **That is a result, and one of
the strongest a row can carry. Report it; do not repair it.**"*

### ⚠⚠ THE SCOPE, STATED BEFORE THE CLAIM IS QUOTED ANYWHERE

`controls/second_limb.py` searches all **163** cached patches **by diff BODY**:

| limb | repair in the cache |
|---|---|
| `offsetunset` `:512-513` | **`cf020f133487`, uniquely** |
| `offsetexists` `:427-429` | ⛔ **NONE — 0 of 163** |

⛔⛔ **THAT IS A RESULT ABOUT THE 163-PATCH SCREENED CORPUS CACHE ON THIS BOX,
AND NOT A CLAIM ABOUT php-src's HISTORY.** There is no network here and the cache
is not upstream's log. *"No repair in the cache"* is a negative and a negative is
a result (F10); *"upstream never fixed it"* is a claim this box cannot support
and this row does not make.

⚠⚠ **TWO METHOD TRAPS, AVOIDED ON PURPOSE AND NAMED SO THE NEXT ROW AVOIDS
THEM TOO.** (a) The `@@ … @@` hunk-header label names the function the hunk
STARTS AFTER, **not** the function it touches — reading it as the latter made
`235e6c0afe1d` look like an `unset_dimension` repair when it is a
`call_user_call` one. (b) A **compound** `grep -a 'A\|B'` whose hit is attributed
to `A` when it matched `B`. ▶ The control searches the `+`/`-` lines only, one
token at a time, and never the subject line.

### ⛔⛔ WHY THERE IS NO `adversarial-exists.bin` IN `inputs/`

`harness/check.py` stage 7h **fails a row whose R1h fires a sanitizer on ANY
input, adversarial included** — *"R1h is the arm that carries the check, so it is
expected clean on EVERY input"*. An input carrying the `:427` sentinel faults in
R1h, so shipping one would make this row's gate record RED for a defect upstream
declined to repair rather than for anything the row got wrong.

▶ **The limb is therefore measured in `controls/` and is absent from `inputs/`,
deliberately.** ⚠ **That is a judgement and it is ROUTED TO THE MANAGER** — see
`.tasks-php/TASK_PHP_060_REPORT.md` §UNSURE. The alternative (ship the input,
accept a FAIL verdict, and publish the incompleteness through the gate record
itself) is defensible and I did not take it.

> ## ✅✅ RULED BY THE MANAGER, 2026-09-15 — **THE ACTION IS UPHELD, THE GROUND IS REPLACED, AND THE DEFECT WAS MINE**
>
> ⚠ **Ruled HERE, in the file that asked, and not only in a task report** —
> `_059` found a routed ruling request buried in a row's `NOTES.md` that the
> manager never answered and then contradicted in print. **An unanswered routed
> question is not neutral; it becomes a claim its author is free to contradict
> without noticing** (`F123`'s class). ⓘ The report's §13 item 1 carries a
> pointer to this ruling, not a second copy of it (`F131`: one home per fact).
>
> ✅ **THE ACTION STANDS: `adversarial-exists.bin` stays out of `inputs/`.**
>
> ⛔⛔⛔ **BUT NOT FOR THE STATED REASON, AND THE STATED REASON MUST NOT BE
> QUOTED.** *"A RED gate record misreports what the row got wrong"* is the wrong
> ground, because **stage 7h's own failure text refutes it in terms**: *"This is
> a real finding about the pattern, not a gate false alarm … **Report it; do not
> silence it.**"* ▶ **On the engineer's ground, withholding the input IS the
> silencing that sentence forbids.** A ruling that let that ground stand would
> have put this row in conflict with the stage it was avoiding.
>
> ⭐⭐⭐ **THE GROUND THAT ACTUALLY CARRIES IT: `:427` HAS NO R1h, SO IT CANNOT
> SHARE AN R1h COLUMN WITH `:512`.** Measured this round across all 163 cached
> patches by diff body: `:512-513` is repaired by `cf020f133487` uniquely and
> `:427-429` by **nothing**. The R1h column of a row is a claim about **the
> commit that repairs the cited site**. Putting `:427`'s adversarial input into
> **this** row's `inputs/` would make `ph96`'s R1h column assert coverage of a
> site it does not cover — ▶ **the objection is that the LABEL would be false,
> not that the VERDICT would be red.**
>
> ⛔⛔ **AND THE DEFECT IS THE MANAGER'S, IN `TASK_PHP_060.md` §2.5.** I ruled
> *"the row models the CONTRACT, not the site"* and in the same task file pinned
> an R1h that repairs **one of the two faulting shapes**. Those two instructions
> cannot both be honoured, and **the engineer hit the contradiction and routed it
> back rather than papering over it, which is the correct behaviour.** ⭐ The
> `§2.5` decision is not withdrawn — the four-shape kernel is the row's best
> evidence and the 2×2 is why this row is worth more than its catalogue entry —
> **but it was under-specified: it should have said *model all four shapes in the
> BENIGN domain; an ADVERSARIAL input may only exercise a shape the row's R1h
> repairs.*** That sentence is the repair, and it is now the rule.
>
> ▶ **`:427-429` IS ROUTED TO THE CATALOGUE AS A CANDIDATE ROW, NOT KEPT AS A
> LIMB OF THIS ONE** — same obligation (`I12/O1`), different site, **and no known
> upstream repair**, which under `PROTOCOL_PHP.md` §C makes it *unusual and worth
> cataloguing*, not unbuildable. ⚠ **Scope, and it binds every quote of this:**
> *no repair in the **163-patch cache*** is a cache result (`F10`); ***"upstream
> never fixed it"* is a claim this box cannot support.**
>
> ⛔ **THE THIRD OPTION IS REFUSED, ON A MEASURED COST AND NOT ON TASTE.** A
> `spec.md` field declaring an input on which R1h is *expected* to fire would
> require reading it in **stage 7h, which lives in `harness/check.py`** — frozen
> PAT infrastructure hashed into **all 33 PAT gate records** (`CLAUDE.md`,
> `PLAN_PHP.md` §2.1). ▶ **It is the MOST expensive of the three options, not the
> cheapest**, and it would encode the wrong model anyway: the right description
> of `:427` is *a different row*, not *a declared exception to this one*.
>
> ✅ **WHAT MAKES THE ROW HONEST, AND IT WAS CHECKED BEFORE RULING:** the row's
> **cited** defect does ship an adversarial input, and the R1-vs-R1h comparison
> works on it — `adversarial-unset.bin` reads `fired=true` on the vulnerable C
> rung and `fired=false` on R1h in the gate record. ▶ **7h passes because the
> repair really does repair the cited site, not because the hard input was
> withheld.**

---

## §6 ⛔⛔⛔ THE C FAILURE MODE IS **BUILD-DEPENDENT**, AND F3 FIRES LIVE

`controls/widened_domain.py`'s opt sweep, R1 on `inputs/adversarial-unset.bin`:

| compiler | `-O0` | `-O1` | `-O2` | `-O3` |
|---|---|---|---|---|
| **gcc** | SIGSEGV `0x10` | SIGSEGV `0x10` | SIGSEGV `0x10` | SIGSEGV `0x10` |
| **clang** | SIGSEGV `0x10` | SIGSEGV `0x10` | ⛔ **silent wrong answer** | ⛔ **silent wrong answer** |

The null dereference is UB; above `-O1` clang propagates *`retval` is non-NULL*
backwards from the dereference and the sentinel path compiles into something that
returns `18121308747923605504` where the correct answer is
`15642763268152511488`. **No crash, no diagnostic, a wrong checksum.**

⭐⭐ **THIS IS `RECAP_PHP.md` F3 — *a clean run is not evidence of absence* —
FIRING LIVE, on a row that also has a faulting run to compare it against.** A
reviewer who had tested only `clang -O3` would have concluded the defect was not
reachable.

⭐ **And `controls/rust_bug.py` finds the SAME SHAPE one language over** (§10):
unsafe Rust with the guard deleted aborts at `-O0` and returns a silent wrong
answer at `-O1` and above, while **safe Rust panics at every level**. ▶ *Safe
Rust's detection is build-independent; C's and unsafe Rust's are not.*

⚠ The gate's own `notes` says the narrower version of this by itself:
*"adversarial-unset.bin/c-clang: opt/mode variants of this rung disagree
(2 distinct behaviours)"*.

---

## §7 ⭐⭐⭐ THE TWO ATTESTED REPAIRS, PRICED AGAINST EACH OTHER

Every other row in this programme has ONE R1h. This one has **two strategies for
one obligation, both attested in the vulnerable file by the same author before
the bug was reported**:

| | strategy | C spelling | attested at |
|---|---|---|---|
| **noout** | REMOVE the output | pass `NULL`, delete the local and the dtor | `:413`, **and upstream's `cf020f133487`** |
| **guard** | TEST the output | `if (!retval)` before use | `:385` |

`controls/repair_price.py`, **A1 = `kernel_exclusive_ir` / calls**,
**`O3/isolated`**, base = **noout (upstream's own strategy)**, **BOTH C COLUMNS**:

```
compiler  variant                           input        A1 total   A1/call  W-share
gcc       noout (upstream cf020f133487)     small.bin     7184739   359.237   94.02%
gcc       guard (the :385 spelling)         small.bin     7184739   359.237   94.02%
gcc       noout                             large.bin     7299741  2919.896   96.40%
gcc       guard                             large.bin     7299741  2919.896   96.40%
clang     noout                             small.bin     8007990   400.399   94.63%
clang     guard                             small.bin     8007990   400.399   94.63%
clang     noout                             large.bin     8097819  3239.128   96.77%
clang     guard                             large.bin     8097819  3239.128   96.77%

  ⭐ c-gcc     small.bin    guard - noout = +0.0000 Ir/call  (+0.0000 %)
  ⭐ c-gcc     large.bin    guard - noout = +0.0000 Ir/call  (+0.0000 %)
  ⭐ c-clang   small.bin    guard - noout = +0.0000 Ir/call  (+0.0000 %)
  ⭐ c-clang   large.bin    guard - noout = +0.0000 Ir/call  (+0.0000 %)
```

**The two repairs cost exactly the same, in all four cells.** The checksums agree
on every input first, so the difference is a price and not a semantics change.

### §7.1 ⭐⭐ **THE MECHANISM, because a cost with no mechanism is an incomplete row** (§F8)

```
C. WHY. The two `kernel` symbols, compared instruction for instruction:
   c-gcc     identity_level=counts  insns 207 vs 207, bytes 705 vs 705
   c-clang   identity_level=exact   insns 280 vs 280, bytes 1070 vs 1070
```

⭐⭐⭐ **UNDER CLANG THE TWO ATTESTED REPAIRS ARE THE SAME PROGRAM — byte-identical
machine code.** Under gcc they are the same instruction count and the same byte
count with different bytes.

▶ **And the reason is structural rather than an optimiser accident: "removing the
output" does NOT delete the NULL test — it RELOCATES it into the shared helper.**
`zend_interfaces.c:88-93` disposes of the value behind its **own** `if (retval)`
at `:89`. Both configurations execute one NULL test and one conditional release;
only *where the test is written* differs, and inlining erases even that.

⚠ That is why **`:89` is the very test `:513` omits, written by the same hand in
the function being called** — and why `cf020f133487` is best read as *moving the
call site onto a contract whose test is already written* rather than as *deleting
a test*.

---

## §8 THE PROOF, AND WHAT IT RESTS ON

`verus.rs`: **36 verified / 0 errors**, and **40 / 0** under `--cfg slb_twin`
(four trusted accessors, therefore four twins; `load_input` and `emit` are I/O and
have none).

⭐⭐⭐ **THERE IS NO `#[verifier::rlimit]` ON THE ROW AND THAT IS A MEASUREMENT.**
`controls/rlimit_bisect.sh`: **1 suffices**, plain and twin, and every value
1..12 gives 36/0 and 40/0 — **monotone throughout**. ⚠ What to read a bisect for
is monotonicity, not a minimum: `ph97` before its `#[verifier::opaque]`
attributes went 10 pass / 30 FAIL / 60 pass, which is *a proof that is a coin
flip* rather than *a proof that is too big*. This row carries
`#[verifier::opaque]` on `s_step` and `s_fold_zval` for the same reason.

### §8.1 ⭐⭐⭐ THE MUTANTS — `controls/negatives.py`

```
mutant      must        verified  errors  first error
shipped     verify            36       0
r1          FAIL              35       1  error: precondition not satisfied
r1exists    FAIL              35       1  error: precondition not satisfied
status_ok   FAIL              33       3  error: postcondition not satisfied
```

* **`r1`** deletes the `:385` NULL test at the READ shape (upstream's own) →
  `opt_get`'s `requires t.is_some()` is unsatisfied. **`I12/O1` is load-bearing.**
* **`r1exists`** deletes the same test at the EXISTS shape — the one upstream
  does **not** have — with the same result. ▶ **The second limb, as a proof
  obligation.**
* ⭐⭐⭐ **`status_ok`** strengthens `call_method`'s postcondition to what the
  author of `:513` evidently assumed — *SUCCESS means the out-parameter was
  written* — and it fails with a **postcondition** error **inside the callee**.
  **The callee cannot promise it, because it really does return SUCCESS having
  written nothing.** ▶ *"The status answers a different question"* and *"the
  status's postcondition cannot discharge the release's precondition"* are the
  same sentence in two languages.

### §8.2 ⚠ WHICH OBLIGATIONS ARE THE ROW AND WHICH ARE ARITHMETIC

Four trusted accessors, and **only one of them is about PHP**:

| item | `requires` | is it the row? |
|---|---|---|
| `opt_get` | `t.is_some()` | ⭐⭐⭐ **YES — `I12/O1` word for word** |
| `sget` | `i < v@.len()` | no — a slice index bound |
| `wsub` | `o + n <= v@.len()` | no — a sub-slice bound |
| `ty_get` | `k < 4` | no — a four-entry table indexed by a residue |

▶ **An editor who deleted a NULL test would be removing the precondition of
exactly ONE of them**, which is what `controls/negatives.py --emit r1` shows.

### §10.1 SLB-TRUSTED-ARGUMENT — the per-item arguments the gate requires

Four trusted accessors, four arguments. Each answers the three things no stage of
the gate can judge: **(a)** is the twin's body the right checked stand-in for the
unchecked operation; **(b)** is the `ensures` COMPLETE with respect to every
unchecked operation the body performs; **(c)** does each clause mean the same
thing in the shipped configuration as in the twin's.

⚠ **(b) is `TASK_009_REVIEW`'s x4 and it is the one a contract pin cannot
catch:** a body that ALSO read `i + 1` satisfies the contract, the twin and the
`--cfg slb_twin` run unchanged. The defence on every item below is the same two
things — a body short enough to quote whole, and **Miri**, which this row
requires.

#### SLB-TRUSTED-ARGUMENT verus.rs opt_get

Body: `unsafe { t.unwrap_unchecked() }`. Twin: `t.unwrap()`.

**(a)** `unwrap` is *the* checked stand-in for `unwrap_unchecked`: same function,
same return, one adds the `None` arm. There is no third spelling to choose
between. **(b)** The body performs exactly one unchecked operation and its
definedness depends on exactly one thing — whether `t` is `Some`. `t` is the only
parameter, so the shape this stage exists to catch (an unconstrained parameter the
body then uses) **cannot arise**: the `requires` names the only quantity there is.
The `ensures` `*r == *t.unwrap()` names the WHOLE result, so a body that returned
some other `Zval` could not satisfy it. **(c)** Both clauses are over the same
`Option` value in both configurations; nothing is `cfg`-dependent.

⭐⭐ **WHERE THE PRECONDITION COMES FROM IS THE ROW.** Not from arithmetic, not
from the caller's convenience, and **NOT from the call's status** — whose
postcondition proves the opposite, that the output may be absent (§8.1's
`status_ok`). It comes from a NULL test at each of the two sites: `:385`, which
upstream wrote, and the same spelling at `:427`, which upstream did not (§5).

#### SLB-TRUSTED-ARGUMENT verus.rs sget

Body: `unsafe { *v.get_unchecked(i) }`. Twin: `v[i]`.

**(a)** `v[i]` is the checked form of the same read, character for character
otherwise. **(b)** One unchecked operation, one quantity that can make it
undefined — `i` against a length that is a RUN-TIME fact for a slice, which is
why the `requires` has to name it. The `ensures` `r == v@[i as int]` names the
whole result: a body that read `i + 1` and returned that could not satisfy it,
**but a body that read `i + 1` and DISCARDED it could** — that residue is (b)'s
x4 and Miri is what covers it. **(c)** `v@.len()` means the same in both
configurations. ⚠ The call sites bound `i` differently: inside the record decode
it is a literal under 16 and the caller's `b@.len() == REC` supplies the rest;
inside the value fold it is the loop's cursor plus `SOFF`, bounded by
`n <= STRMAX` and by `REC == SOFF + STRMAX` (which `controls/tables.py` asserts).

#### SLB-TRUSTED-ARGUMENT verus.rs wsub

Body: `unsafe { v.get_unchecked(o..o + n) }`. Twin: `&v[o..o + n]`.

**(a)** The safe slice expression is the same operation; the twin needs one ghost
`assert` to fire vstd's length axiom and nothing else. **(b)** The constrained
quantities are **both endpoints at once** — `o + n <= v@.len()` bounds the pair,
which is what a sub-slice needs and what an index bound would not give. The
`ensures` names the **subrange**, not merely its length, because a body that
returned a correctly-sized slice of the WRONG bytes would satisfy a length-only
contract and change every answer downstream. **(c)** Both clauses are over the
same slice view in both configurations.

#### SLB-TRUSTED-ARGUMENT verus.rs ty_get

Body: `unsafe { *TYTAB.get_unchecked(k) }`. Twin: `TYTAB[k]`.

**(a)** Same read, checked. **(b)** `k` is the only parameter and it IS
constrained, by `k < 4`; the array is a fixed-size `const` whose length is in its
TYPE, so there is nothing about it left for a `requires` to say. ⭐ **The
`ensures` is `r == s_tytab(k as int)`, where `s_tytab` is DEFINED AS THE CONSTANT
TABLE'S OWN VIEW** — so the contract asserts nothing about the table's four
bytes, which is why the verified twin can meet it with a bounds-checked index and
why those four bytes are **not in the TCB**. They are checked by
`controls/tables.py` instead, which diffs all six transcriptions. **(c)**
`s_tytab` is the same spec function in both configurations.

---

## §9 THE NUMBERS, AND WHAT RESOLVES THEM

**A1 = `kernel_exclusive_ir`**, `O3/isolated`, from
`results-php/ph96-outparam-unwritten.json`. `small.bin` makes 20 000 calls at
118 B/call (7 records); `large.bin` makes 2 500 at 1004 B/call (62 records).

| cell | A1/call `small.bin` | A1/call `large.bin` |
|---|---:|---:|
| `c-gcc` (R1) | 358.544 | 2913.352 |
| `c-clang` (R1) | 399.619 | 3232.625 |
| `c-gcc-h` (R1h) | 359.237 | 2919.896 |
| `c-clang-h` (R1h) | 400.399 | 3239.128 |
| `safe_naive` (R2) | 317.333 | 2527.951 |
| `safe_tuned` (R3) | 381.963 | 3035.456 |
| `unsafe` (R4) | **348.025** | **2798.873** |
| `verus` (R5) | **348.025** | **2798.873** |

⛔⛔ **EVERY PERCENTAGE BELOW CARRIES FIVE THINGS** (F108): STATISTIC **A1** ·
INPUT named · OPT/MODE **`O3/isolated`** · BASE named · and where the base is a C
cell, **BOTH C COLUMNS**.

### §9.1 R4 == R5, TO THE INSTRUCTION, ON BOTH INPUTS

`6 960 509` and `6 997 183`, identical. `asm.py::identity_level` on the gate's own
`O3/isolated` binaries is **`norel`**, 271 instructions and 978 bytes each; at
`O0` it is `norel` with 644 instructions and 3377 bytes each. **The proof costs
zero run-time instructions.**

### §9.2 ⚠ THE TWO C COLUMNS DISAGREE, ON IDENTICAL C

A1, `small.bin`, `O3/isolated`: `c-gcc` 358.544 vs `c-clang` 399.619 Ir/call —
**clang is +11.46 % over gcc on the same source**; on `large.bin`, +10.96 %.
⚠ **The sign is the opposite of `ph97`'s**, where gcc was +152.5 % over clang.
That is F108's rule firing in the direction that makes it a LABELLING rule rather
than a preference for either compiler.

### §9.3 R2 vs R3 — ⛔ THE "TUNED" RUNG IS SLOWER, AS ON `ph97`

A1, `small.bin`, `O3/isolated`, base `safe_naive`: R3 is **+20.37 %** (381.963 vs
317.333). On `large.bin`, **+20.08 %**. ▶ `get`-returning-`Option` accessors, an
iterator `fold` over the value bytes and a `match` on the shape cost *more* than
the indexed `while` loops and `if/else if` chain they replace, at `O3`.
⚠ **This is the second consecutive row on which the idiomatic rung is dearer than
the naive one**, and I am reporting it rather than re-tuning R3 until it wins:
the row's question is what an idiomatic port costs, not what the best port costs.
*(Unsure: I did not disassemble to name the mechanism — §12.)*

### §9.4 R2 vs R4 — the safe rung is CHEAPER than the unsafe one

A1, `small.bin`, `O3/isolated`, base `safe_naive`: R4 is **+9.67 %** (348.025 vs
317.333); on `large.bin`, **+10.72 %**. ⛔ **THE UNSAFE RUNG IS DEARER THAN THE
NAIVE SAFE ONE ON THIS ROW, ON BOTH INPUTS.** ⚠ I did not isolate why, and it is
the biggest unexplained number in this file (§12). The one thing that can be said
from the record is that it is **not** a bounds-check story in the obvious
direction: R4 removes checks R2 has and is still dearer.

### §9.5 ⭐⭐ `inside_share` PER CELL, AS A MATRIX, BEFORE THE STATISTIC IS CHOSEN

⚠⚠ **BOTH QUANTITIES THAT WEAR THE NAME ARE COMPUTED AND BOTH ARE LABELLED**
(`RECAP_PHP.md` F129). `controls/inside_share.py`, `O3/isolated`:

| cell | input | A1/call | **share `W`** | **share `F74`** |
|---|---|---:|---:|---:|
| `c-gcc` | small | 358.544 | 94.01 % | 94.85 % |
| `c-gcc` | large | 2913.352 | 96.40 % | 99.44 % |
| `c-clang` | small | 399.619 | 94.62 % | 95.84 % |
| `c-clang` | large | 3232.625 | 96.77 % | 99.57 % |
| `c-gcc-h` | small | 359.237 | 94.02 % | 94.83 % |
| `c-gcc-h` | large | 2919.896 | 96.40 % | 99.44 % |
| `c-clang-h` | small | 400.399 | 94.63 % | 95.92 % |
| `c-clang-h` | large | 3239.128 | 96.78 % | 99.57 % |
| `safe_naive` | small | 317.333 | 90.92 % | 94.53 % |
| `safe_naive` | large | 2527.951 | 93.37 % | 99.40 % |
| `safe_tuned` | small | 381.963 | 92.34 % | 95.10 % |
| `safe_tuned` | large | 3035.456 | 94.42 % | 99.50 % |
| `unsafe` | small | 348.025 | 91.66 % | 94.80 % |
| `unsafe` | large | 2798.873 | 93.98 % | 99.46 % |
| `verus` | small | 348.025 | 91.66 % | 94.80 % |
| `verus` | large | 2798.873 | 93.98 % | 99.46 % |

* **`W`** = kernel exclusive Ir ÷ callgrind's own summary total (needs a
  callgrind run). **`F74`** = `(A1 / n_iters) ÷ marginal_ir_per_call` (arithmetic
  over the two committed records). ▶ **Say which you mean, every time.**
* ⭐ **The gap between them is a MEASUREMENT and never a constant**: it runs
  **0.82 pp to 6.03 pp** across these sixteen cells, wider on `large.bin` than on
  `small.bin`. A third data point for F129 beside `ph29`'s 8.9 pp and `ph45`'s
  0.01 pp.
* **Sixteen independent per-cell ratios, NOT a comparison.**
* ⛔⛔ **A HIGH SHARE IS NOT A CERTIFICATE AND F74's TWO-CONDITION BAR IS NOT A
  GATE.** `TASK_PHP_059` settled it and four documents said so before: on `ph55`
  the bar ADMITS a pair whose A1 reads exactly `+0.0000 %` against a 66.14 Ir/call
  whole-program difference, and on `ph03` it REJECTS a pair whose true A1
  difference is known to be exactly 0. ▶ **Use the share to EXPLAIN a
  disagreement. Never to withhold a column.**
* **What it licenses here:** every difference §9 publishes is between cells at
  91–97 % `W`, and the two that matter most are **exactly zero** (§9.1's R4-vs-R5
  and §7's guard-vs-noout), which A1 resolves trivially because there is nothing
  to resolve. For the non-zero ones (§9.2, §9.3, §9.4) the share is high and
  **A1 is the resolving statistic for this row**, which is why the figures above
  are published in it.
* ⚠ **The whole-program column is in the record** (`main_exclusive_ir`, `O3`
  isolated, `small.bin`: `c-gcc` 280 053, `c-clang` 280 062, `unsafe` 280 279,
  `verus` 280 274) and is not quoted to more than 2 dp anywhere.

### §9.6 ⛔ NO FAMILY-B FIGURE IS PUBLISHED BY THIS ROW

Every number above is family A1 or a whole-program figure. **§B5's sweep is
therefore not owed by anything this file says**, and it has not been paid. ▶ **A
later task that quotes a `marginal_ir_per_call` difference out of this row's gate
record owes `php50_align_sweep.py` and TWO verdicts — *magnitude resolvable?* and
*sign stable?*** Recorded as a gap in `.tasks-php/TASK_PHP_060_REPORT.md` §12
rather than as a clearance.

---

## §10 THE LADDER'S *DOES THE DEFECT SURVIVE?* COLUMN, MEASURED

| | `adversarial-unset.bin` (the `:512` limb) | the `:427` limb |
|---|---|---|
| C R1, **gcc**, `-O0`..`-O3` | **SIGSEGV `si_addr=0x10`** | **SIGSEGV `si_addr=0x14`** |
| C R1, **clang**, `-O0`/`-O1` | **SIGSEGV `si_addr=0x10`** | SIGSEGV `0x14` |
| C R1, **clang**, `-O2`/`-O3` | ⛔ **silent wrong answer** | SIGSEGV `0x14` |
| C R1h (`cf020f133487`) | answers | ⛔ **SIGSEGV `si_addr=0x14`** |
| every shipped Rust rung R2–R5 | answers | answers |
| safe Rust + `unwrap`, guard deleted | **panic, exit 101 at every `-O`** | — |
| unsafe Rust + `unwrap_unchecked`, guard deleted | **SIGABRT at `-O0`, SILENT WRONG ANSWER at `-O1`+** | — |

⭐⭐ **THE SENTENCE THIS ROW ADDS TO THE CRASH COURSE:** *in C the bug is an
OMISSION — a test that is not written — and in Rust reproducing it takes a
COMMISSION, an `unwrap` a reviewer would ask about.* **And the shapes of the two
failures are the same: both are detected at low optimisation and both become
silent wrong answers above it. The only rung whose detection is
build-independent is the SAFE one.**

⚠ `controls/rust_bug.py` measures all of the Rust half; its `N0` must-not-fire
arm confirms the SHIPPED `unsafe.rs` answers at every `-O` on the same input.

---

## §11 ⛔⛔ THE TIER — THE ROW **REFUTES ITS OWN CATALOGUE LABEL**

`patterns-php/CATALOGUE.md` says `narrowed`. **This row declares `modelled`**,
and the ground is measured rather than argued. `harness-php/provenance.py`:

```
per-span overlap: span0 12% (1/8), span1 20% (5/25), span2 13% (5/39),
                  span3 20% (1/5), span4 0% (0/8), span5 38% (3/8),
                  span6 35% (9/26), span7 6% (1/18)
kernel overlap 15% (18/123 excerpt lines)   -- 14.63 % exactly
```

against the **25 %** `narrowed` leads a reader to expect. Three further
measurements, taken to see whether the heuristic is simply wrong about this row:

| restriction | overlap |
|---|---|
| all 8 cited spans, as shipped | **14.63 %** (18/123) |
| all 8 spans, `ph96_` prefix normalised away | 21.95 % (27/123) |
| the **5 LIFTED** spans only, prefix normalised | **24.73 %** (23/93) |
| the 3 CITED-FOR-PROVENANCE spans only (3, 4, 7) | 6.45 % (2/31) |

⭐ **So the heuristic is depressed by two things that say nothing about
fidelity** — this row's `ph96_` prefix convention, and three spans cited so a
reader can check the mechanism rather than because the kernel lifts them (`ph97`
recorded the same about its own `span4`). **But even fully corrected it lands at
24.73 %, one line short — exactly where `ph97` sat — so the heuristic is not
simply wrong.**

⛔⛔ **AND THE DECISIVE FACT IS NOT THE HEURISTIC.** `zend_call_function` is a
~300-line VM entry of which **THREE lines survive** (`:595`, `:870-872`, `:873`),
and what a call DOES arrives in the record as attacker data rather than being
computed. That is a mechanism **re-expressed**, not a wrapper removed. Two
behaviours are also **projected** (both non-returns: `E_CORE_ERROR` and the
`E_ERROR` arm).

⚠ **THE HONEST ALTERNATIVE IS `narrowed` AND A REVIEWER MAY PREFER IT.** The
defect site, all four consumer handlers, `zend_call_method`, `_zval_ptr_dtor` and
`i_zend_is_true` are upstream's bodies unchanged; only the executor is gone, and
`.memory-php/01-extraction.md` prices extraction at the DEFECT site. ▶ **I
declared the lower tier because a tier is a COST and never a FILTER
(`PROTOCOL_PHP.md` §A1), so the honest one is free, and because `ph56` set the
precedent for `modelled` where a mechanism is re-expressed.** This is the second
row after `ph55` to refute its own mining-wave label.

ⓘ **One unevaluable preprocessor condition**, `#ifndef PH96_KERNEL_H`, the
include guard. The residual is reported as a number rather than enumerated away.

---

## §12 ⚠ WHAT IS RECORDED HERE AND IS NOT ESTABLISHED

1. **§9.3 and §9.4 have costs and no disassembly.** R3 is +20 % over R2 and R4 is
   +9.7 % over R2, and `PROTOCOL_PHP.md` §F8 says *a cost with no mechanism is an
   incomplete row*. Both have hypotheses and neither has a disassembly behind it.
2. **The `:427` limb's absence from `inputs/` is a JUDGEMENT** (§5) and it is
   routed to the manager in the task report, not settled here.
3. **`uses_allocator: false` is DECLARED, never detected.** The kernel allocates
   nothing — the zval is a frame object, the type table is `static const`, no rung
   calls `emalloc`/`efree`/`malloc`/`free` — so `PROTOCOL_PHP.md` §B1a's
   precondition holds at ZERO allocations per call rather than at O(1), and this
   row's cross-language column carries **no allocator caveat at all**. The
   `c/emalloc_shim.h` symlink is carried anyway, because that rule is
   UNCONDITIONAL.
4. **`echoes: ["p42"]` is the catalogue's, carried across.** I did not re-derive
   whether `p42` really shares this mechanism; `echoes` is a cross-reference and
   never a filter.
5. **`fix_commit` is confirmed at the SITE and the DIRECTION, from the patch
   bytes** — not against the release tags. Whether `cf020f133487` is the FIRST
   commit to close the unset site, and whether a 5.0.x branch backport preceded
   it, is **UNVERIFIED** (`PROTOCOL_PHP.md` §F5(iii)).
6. **The `loud` section is non-empty and is not a defect** — 3
   `doc-citation-other` hits, all line citations into `build.py` that live in
   `common-php/emalloc_shim.h`, the shared allocator header this row symlinks.
   They are not this row's text and re-citing them by function costs a re-measure
   of every php row.

---

## §13 WHAT THE SPELLING AUDIT MOVED, BEFORE `spec.md` EXISTED

`controls/spellings.py` was run on the CANDIDATE `idiom` block before `spec.md`
was written — which is what `TASK_PHP_060` §3.4 asks for and what item 100's
three instances did not get. Every candidate pin HIT in every rung it scopes to,
and every `forbidden` spelling MISSED in all six, on the first draft.

⚠ **One pin still got through and the GATE caught it, which is worth recording**:
`idiom.required[1].rust` quoted `char *retval = NULL` — a **C-language** spelling in a
rust-keyed entry, so it pinned 0 of 4 rungs. Stage 0b reported it as *pins
nothing* and it became prose. ▶ **A candidate audit is not a substitute for the
gate's own: my first run checked that each spelling matched SOMEWHERE, and the
gate checks that it matches in the rungs its KEY scopes it to.**

⛔⛔ **AND THE REPLACEMENT PROSE CREATED A FIFTH PIN OUT OF THE WORD `rust`**,
because the sentence explaining the rule put the word in backticks. This time
`controls/spellings.py` caught it — **4 of 72 obligations unsatisfied** — which
is the same control doing the job the first draft's weaker question missed.

▶ ⭐ **THE FINDING FOR THE LAYER, AND IT IS THE FOURTH INSTANCE IN FOUR TASKS:
item 100's failure mode is not "an author forgot the rule". It is that the rule's
own PROSE is written in a field where backticks are pins**, so explaining the
rule inside an `idiom` entry creates an instance of it. ⚠ `ph97`'s entries all
carry the same warning sentence and all of them keep it backtick-free; that is
the discipline, and it is fragile because nothing but this control checks it.
