# ph64-callback-frees-cursor — notes

## §0 Rule 6 disclosure, and the one declaration the measurement corrected

**`contract_sha256` as first written, before any cell was built:**

```
a971e810d8ab9a2d5d2a8e58e3c84e762d4c31b04edeb5c669fd6a43fd9d65dc
```

⚠⚠ **IT MOVED TWICE AND BOTH MOVES ARE DISCLOSED HERE RATHER THAN LEFT TO BE
NOTICED**, because `.tasks/PROTOCOL.md` rule 6's documented hole is a frozen
declaration that measurement has since falsified, and `ph07` carried eleven
pre-rebuild numerals for six tasks with a matching hash (`TASK_PHP_024`).

| # | sha256 | what changed, and why |
|---|---|---|
| 1 | `a971e810d8ab9a2d…` | as first written, **before any cell was built** |
| 2 | `3288f7acc1b1cc63…` | ⚠ **the `identity` entry was WRONG and the measurement said so.** It was written as `O3: "norel"` on the structural argument that a kernel calling out to the allocator cannot be `exact`. Measured: `unsafe` is **385 instructions / 1747 bytes** and `verus` is **384 / 1740**, so `md5_fn_norel` differs too and only `differ` is available. The entry now carries the measured numbers and the one-instruction diff that explains them (§11) |
| 3 | `66941e87db0c65cc…` | the `idiom` block: `forbidden[0]` and `forbidden[2]` quoted `zend_llist_apply`, `l->count`, `DEL_LLIST_ELEMENT` and `--l->count` **in their prose**, and the named-spelling standard makes a backticked token in a `forbidden` entry a spelling that must be ABSENT — so the row's own C rungs violated the row's own contract, **8 hits, and the gate failed exactly as it should have**. The entries were narrowed to the spellings actually meant, and `required[3]`/`required[4]` (which say "NO BACKTICKED SPELLING IN THIS ENTRY") had their backticks removed so they mean what they say |
| 4 | `a45c15891ee66bc8…` | `verus.twin_obligations` 46 → 47 when a twin was added for the tenth trusted item — the gate refused a trusted item with no verified twin, correctly |
| 5 | `7ec3fc87b30975c5…` | ⚠ **the gate refused the twin too**, because `slb_twin_slice_subrange`'s body called `vstd::slice::slice_subrange` and step 5c-twin matches by IDENTIFIER: a twin that names the trusted item re-uses the axiom instead of re-deriving it. The row's own item is now called **`subwin`**, so the twin's call to vstd's checked `&slice[i..j]` really is a re-derivation. ⭐ **And in the same pass all three `#[verifier::rlimit]` overrides came OUT** (§10a). **This is the sha the shipped tree carries** |

⚠ **`git show HEAD:… | diff -` is VACUOUS on a new row and this row does not
cite it.** A pattern lands in one commit, so on a clean tree the command always
prints nothing and always looks like it passed (`TASK_070_REVIEW`). The hash
above is the only evidence, which is why it is written down before anything was
built.

⚠ **`spec.md` is GENERATED**, by `.temp/php32/mkspec.py` — rule 6's
artefact-vs-generator note. The 11 003-byte named-spelling tail is lifted from
`ph07`'s `why` rather than retyped, and `verus.items` is read out of `verus.rs`
with the gate's own `harness/vparse.py`, so neither can drift by transcription.
**If `spec.md` is edited by hand, fix the generator too.**

---

## §1 What the row is

```
Zend/zend_llist.c:190      for (element=l->head; element; element=element->next)   <- SITE L
Zend/zend_llist.c:191          func(element->data);
basic_functions.c:2109             tick_fe->calling = 1
basic_functions.c:2111-2116        call_user_function(...)        ==> USERLAND PHP
basic_functions.c:2860                 unregister_tick_function()
Zend/zend_llist.c:98-99                  compare(current->data, key) -> DEL_LLIST_ELEMENT
Zend/zend_llist.c:85                       l->dtor(current->data)   [efree(arguments)]
Zend/zend_llist.c:87                       pefree(current)          <== THE FREE
basic_functions.c:2135             tick_fe->calling = 0             <== SITE C  WRITE-AFTER-FREE
Zend/zend_llist.c:190      element = element->next                  <== SITE L  READ-AFTER-FREE
```

**One trigger, two dereferences, and the corpus cites the second one first.**
`index.csv`'s `c_file_line` for CRASH-086 is `basic_functions.c:2135`, which is
the WRITE — and it is right to: on plain `malloc`/`free` under ASan that is the
FIRST faulting access, a `WRITE of size 4` (§6). The DEFECT is one call up, in
the loop that advances its cursor after handing control to a callback, and that
is what `provenance.c_file`/`c_lines` names (`.memory-php/01-extraction.md` F1).

There is a **third** dangling reference and the row cites it too:
`user_tick_function_dtor` `efree`s the entry's `arguments` block, which the
comparator reads on any later walk (`extra_spans[7]`).

---

## §2 The fixture, and what it asserts about itself

A window is `[u32 nent][u32 trig][u32 mode][u32 post]` then one 4-byte slot per
registered tick function; entry `i`'s name is `[u32 le i][slot i]`, so **names
are unique BY CONSTRUCTION** and "unregister my own name" cannot silently mean
somebody else's. That is exactly how `TASK_PHP_031`'s own first oracle probe was
wrong (its report §8.8), and it is closed here by construction rather than by an
assertion.

`inputs/gen.py::_check_span` refuses to write a corpus that misses any of:

- ⭐ any of `DEL_LLIST_ELEMENT`'s **four** arms — `mid`, `head`, `tail`, `only`
  (`PROTOCOL_PHP.md` §A2a rule 1). They are not interchangeable: the `tail`
  arm's `element->next` is NULL, so a recycled block CREATES a successor where
  the loop would have ended, and the `only` arm needs a ONE-ENTRY list;
- a deletion during the walk **and** one at top level;
- a deletion of the entry AHEAD of the cursor, and one BEHIND it;
- a `post` that names an entry the walk already removed (so `del_element`
  scans the whole list and matches nothing);
- the reuse allocation both ON and OFF;
- `trigger == 0` (a walk in which no callback touches the list);
- `n == 1` and `n == nmax`.

⚠ **One fixture parameter had to change its spelling and the assertion is what
caught it.** The `n == 1` profiles were written as `0.01 × nmax`, which is 1 at
`nmax = 134` and **10** at `nmax = 1014` — so the `only` arm was reached on
`small.bin` and missed on `large.bin`. A parameter that means one thing at one
stride and another at another is not a parameter; it is now spelled `0.00`,
meaning `n == 1` exactly.

⚠⚠ **What the measured corpus may NOT contain, and why it is not the `ph07`
situation.** `mode == SELF` with a live trigger is the row's own trigger and the
ONE shape on which R1 and R1h return different `u64`s, so it lives in
`adversarial-*.bin`. That is an exclusion of the ADVERSARIAL shape, not of a
region of the benign domain: `562f886ecb14`'s guard is `ret && tick_fe1->calling`
and outside a self-unregistration that flag is 0 at every element the comparator
ever sees. `ph07` restricted **13.5 % of its benign domain** to keep a withdrawn
guard dead, and `TASK_PHP_018` had to undo it; nothing of that kind is happening
here, and `model.py::selfcheck` check 2 asserts positively that the corpus DOES
delete elements rather than merely avoiding the trigger.

---

## §3 Provenance, and the overlap number (`PROTOCOL_PHP.md` §F9)

**Fourteen spans across three files.** The primary is the DEFECT
(`Zend/zend_llist.c:186-193`); `index.csv`'s own cited line
(`basic_functions.c:2102-2137`) is `extra_spans[8]`; and **the frame R1h occupies
(`basic_functions.c:2146-2161`) is `extra_spans[10]`**, cited from the first
commit rather than two tasks late — which is open item 25's whole lesson.

```
kernel overlap 50% (69/139 excerpt lines in kernel.c, kernel.h, kernel_hardened.c)
tier=narrowed is expected to clear 25% -- REPORTED, NOT ENFORCED
per-span: span0 50% span1 100% span2 100% span3 86% span4 91% span5 95%
          span6 89% span7 80% span8 20% span9 17% span10 0% span11 17%
          span12 9% span13 29%
1 preprocessor condition the heuristic cannot evaluate: ['#ifndef PH64_KERNEL_H']
```

⚠⚠ **§F9 says read this number and say what I think of it, so: 50 % over the
union is TWICE the `narrowed` expectation and it is still the WRONG SHAPE to
read as a quality signal, for a reason this row makes unusually visible.** Look
at the per-span column, not the union:

- the six `Zend/zend_llist.{c,h}` spans score **86–100 %**. They lift `verbatim`
  and the number says so;
- the seven `ext/standard/basic_functions.c` spans score **0–29 %**. They are
  `narrowed` — the zval unpack, `call_user_function`, `zend_binary_zval_strcmp`
  and three `php_error_docref` arms all come off — and the number says that too;
- ⭐ **`span10` scores 0 % (0 of 3), and `span10` is `user_tick_function_compare`
  — THE FRAME R1h LANDS IN.** The overlap tool reads `c/kernel*.{c,h}`, and this
  row's comparator is a 3-line span whose surviving text after narrowing is a
  byte loop that shares no line with the original. **A row that used the union
  as its quality signal would be certifying 50 % while the fix's own frame scored
  zero.** That is open item 25's failure mode one level in, and it is why the
  per-span column matters more than the union on a 14-span row.

⚠ **The union also moves the wrong way when you add a span**, which open item
37(a) already measured: adding a well-lifted span raises it and adding a heavily
narrowed one lowers it, so the number tracks the MIX of tiers among the cited
spans and not the fidelity of any of them. It is reported, it is not tuned, and
this row's real fidelity evidence is `controls/differential.py` (the SHIPPED C
against the model over 2 592 windows) and §6's ASan table.

---

## §4 R1h — `562f886ecb14`, and where it is not

| | |
|---|---|
| commit | **`562f886ecb14`**, Antony Dovgal `<tony2001@php.net>`, 2007-04-10 09:37:09 +0000 |
| subject | *"MFH: fix #41037 (unregister_tick_function() inside the tick function crash PHP)"* |
| shape | ONE hunk, 7 added / 2 deleted lines, in ONE function |
| artefacts INSIDE the commit | bug #41037 in the subject; a NEWS line it adds; `ext/standard/tests/general_functions/bug41037.phpt`, 23 lines, which it adds |
| window | guard ABSENT at php-5.2.1 (body sha256 `418a53cb63037006`), PRESENT at php-5.2.2 (`4ae3d1c82072e782`); the php-5.2.1 → php-5.2.2 diff of the function **is this commit's hunk, line for line** |
| backport cost | **zero.** 5.0.0's `user_tick_function_compare` is byte-identical to php-5.2.1's, so the commit's pre-image IS 5.0.0: `patch -p1` rc = 0 and the result is byte-identical to php-5.2.2's function |
| where it lands | ⚠⚠ **NEITHER SITE.** Not `zend_llist.c:190` and not `basic_functions.c:2135`. `grep -ac 'calling = 0'` over the 86-line patch is **0** |

**`zend_llist_apply` is never repaired, at any tag.** Its body's sha256 is
identical at twelve tags from php-5.0.0 to php-5.6.0 (`b6de446154e2ed86`) and
differs at php-7.0.0 and master (`a5ed671fb22ca47e`) **only** by the
`TSRMLS_DC`/`TSRMLS_CC` deletion. So a row built at the loop alone would have no
R1h at all — which is why this row carries both sites (`TASK_PHP_031_REPORT` §5).

⭐ **And upstream STRENGTHENED the guard rather than reverting it**: it survives
into master, 18 years on, with `php_error_docref(E_WARNING)` upgraded to
`zend_throw_error(NULL, "Registered tick function cannot be unregistered while
it is being executed")`.

⚠ **Why the one exposure was closed instead of the container.** Of
`zend_llist_apply`'s eight 5.0.0 call sites, **seven cannot re-enter userland**
(`php_ini.c:549,:550`, the two SAPI `php_register_command_line_global_vars`,
`zend_execute_API.c:158,:208`, `zend_extensions.c:166`) and the eighth is
`user_tick_function_call`. Fixing the one caller closes the one exposure — the
clean negative against reading the missing `next`-cache as an unexploited hole
elsewhere.

⚠ **The pre-image screen calls this commit `NOT-THE-REPAIR` and it is right to,
in the narrow sense that its own soundness flag admits.**
`.tasks-php/preimage_screen.py` labels it `NOT-THE-REPAIR` with
`decisive=False`, because no line-level pre-image screen can find a fix that
closes a use-after-free by making the FREE unreachable from a third function.
`TASK_PHP_031_REPORT` §7.1 measured that class at **17 of the screen's 43
exclusions** and recommends a third label; ph64 is the one instance of the 17
that has been checked by hand.

### §4a Is the fix correct? — yes on the tick list, and here is the invariant

`zend_llist_apply` advances only after `func` returns; `user_tick_function_call`
sets `calling = 1` at `:2109` and clears it at `:2135`, i.e. for exactly the
duration of the userland call. **So every element that any live
`zend_llist_apply` frame's `element` variable points at has `calling == 1`** —
including under nested tick dispatch, because each nesting level's cursor is
protected by its own entry's flag. And the elements the guard does NOT protect
need no protection: `DEL_LLIST_ELEMENT` repairs both neighbours' links.

`controls/predicate.py` E4 measures the invariant rather than arguing it: over
2 336 windows the shipped guard refuses **exactly once on a live SELF trigger
and never otherwise**.

### §4b It is one word from being a no-op

`zend_llist_del_element:98` calls `compare(current->data, element)`, so
`tick_fe1` is the **LIST ELEMENT** and `tick_fe2` is the **SEARCH KEY** — and
`PHP_FUNCTION(unregister_tick_function)` (`:2843-2861`) sets only `arguments`
and `arg_count`, leaving the key's `calling` an indeterminate stack `int`.
`controls/predicate.py` builds the `tick_fe2` spelling and measures it:
**189 of 189 trigger windows revert to R1's exact `u64`, and 189 of 189 reuse
windows still go wild.** The fix's soundness is entirely in which argument it
reads.

### §4c What was chosen against — and it is NOT weaker in one direction only

`zend_llist_apply_with_del` (`:171-183`) is fifteen lines above the defect,
takes the same caller-supplied `func`, and caches `next = element->next` at
`:177` before calling it. `controls/next_cache.py` builds that counterfactual:

| | |
|---|---|
| E1 | caching `next` removes **every** wild walk on the SELF shape — **189/189**. SITE L is fixed |
| E2 | ... and SITE C still writes into the recycled block — **189/189**. SITE C is not |
| E3 | ... and the `u64` still differs from R1h's on the latent shape — **189/189**. The answer is not restored either |
| E5 | ⚠⚠ **... and it ADDS a use-after-free the plain walk does not have — 196/196.** Where the callback frees the cursor's own SUCCESSOR (`mode == AHEAD`), plain `zend_llist_apply` re-reads `element->next` AFTER the callback and `DEL_LLIST_ELEMENT`'s repaired link makes it skip correctly; the cached-`next` rung follows a pointer it read BEFORE the free and **visits the freed element** |

⚠ **E5 was not predicted.** The control's first version declared "identical
wherever nothing is freed under the cursor" and missed on 196 of 1958, all
`mode == AHEAD`. The expectation was wrong, not the measurement, and the miss is
recorded in the control's own header rather than rewritten. ⭐ **What it buys is
the point: the two hardenings are NOT ordered by strength.** Upstream picked the
one that dominates, and this row can say so only because it carries both sites —
which is `TASK_PHP_031_REPORT` §5.1(3)'s argument, measured.

### §4d ⚠⚠ THE OPEN ITEM — R1h's refusal path runs userland from inside the deleter's walk

**Conclusion, verified at source; mechanism, OPEN** (`.tasks/PROTOCOL.md` rule 9's
split). `562f886ecb14`'s refusal path calls
`php_error_docref(NULL TSRMLS_CC, E_WARNING, "Unable to delete tick function
executed at the moment")`, and that chain is

```
php_error_docref == php_error_docref0   (main/php.h:324)
                -> php_verror           (main/main.c:431)
                -> php_error(type, "%s", message)
                -> zend_error           (Zend/zend.c:866)
   zend_error's `default:` arm, with set_error_handler installed:
       call_user_function_ex(CG(function_table), NULL, orig_user_error_handler, ...)
```

i.e. **arbitrary userland, reached from inside `zend_llist_del_element`'s own
`while` loop, which holds `current` and `next`.** Verified by reading the source
at 5.0.0 **and** at php-5.2.2, the tag the fix shipped in.

⚠⚠ **IT IS NOT MEASURED AND IT IS NOT A FINDING.** No PHP was built, the
one-file reproducer in `TASK_PHP_031_REPORT` §4.3 was not run, and nobody has
checked whether `zend_error`'s `EG(user_error_handler) = NULL` window or
`EG(error_handling) == EH_THROW` blocks the specific nesting. **This row cannot
speak to it either, and that is deliberate and stated in `spec.md`'s
`divergences[5]`**: the row PROJECTS the warning to a counter, and that
projection is exactly what hides it. It is the one divergence whose `why` does
not end in "no semantics".

⭐ **Upstream is itself a partial answer**: master replaced the warning with
`zend_throw_error`, which cannot run userland.

---

## §5 The C-side asymmetry — this row's argument needs no Rust

`Zend/zend_llist.c` has **six** callback-driven walks
(`TASK_PHP_031_REPORT` §2, `.temp/php31/logs/walkcensus.log`):

```
zend_llist_del_element          :91-104   caches_next=YES
zend_llist_destroy              :107-121  caches_next=YES
zend_llist_apply_with_del       :171-183  caches_next=YES   <- FIFTEEN LINES ABOVE
zend_llist_apply                :186-193  caches_next=no    <- THE DEFECT
zend_llist_apply_with_argument  :229-236  caches_next=no
zend_llist_apply_with_arguments :239-249  caches_next=no
```

**Three cache the successor, three advance in the `for` header, and the three
that do not are exactly the three this defect can reach.** One file, one author,
one idiom written both ways. That is the strongest form the argument can take:
upstream had the defence in hand, in the same translation unit, and did not apply
it here — and §4c is what that is worth as a hardening.

---

## §6 The oracle, and the fidelity answer (`PROTOCOL_PHP.md` §A4)

### §6a The obvious oracle measures nothing

```
sizeof(zend_llist_element) = 24     offsetof(element, next) = 0    <- SITE L reads THIS
sizeof(user_tick_function_entry) = 16   offsetof(element, data) = 16
add_element request = 24 + 16 - 1 = 39      `calling` at element+28  <- SITE C writes HERE
REAL_SIZE(39) = 40                  cache_index = 40>>3 = 5 < MAX_CACHED_MEMORY 11
=> a freed element is CACHED: NOT returned to malloc, PAYLOAD UNTOUCHED
```

All five numbers are asserted **at compile time** by `c/kernel.c`'s
`ph64_layout_assert`, which is stronger than anything `model.py` could parse.

`CATALOGUE.md:795` proposes this row's `u64` be a fold of the ids the walk
invoked. `controls/oracle.py` E2a measures that on the corpus's own trigger:
**the visit fold is BIT-IDENTICAL between R1 and R1h on 213 of 213 windows.**
The block never reaches `malloc`, nothing scribbles the payload,
`element->next` still reads the true successor, and the walk visits every
remaining node exactly once. **That is what `crashes_pristine_5_0_0 = False`
is**, and a row built on that oracle would gate green with R1 and R1h agreeing
and would measure nothing.

### §6b What the row folds instead, and it moves on 213 of 213

`acc = fold ⊕ l->count ⊕ dtors ⊕ visits ⊕ refusals ⊕ n`, then `^ php_shim_tally()`
(`n_alloc`, `n_free`, `n_cache_hit`, `bytes_mallocked`). On the latent trigger R1
freed an element R1h refuses to free, so `count`, `dtors` and all four allocator
counters move. `controls/oracle.py`: **E1 2166/2166 must-NOT-diverge, E2 213/213
must-diverge, E3 213/213 wild on reuse, E4 2379/2379 nothing else wild.**
`controls/differential.py` checks the same against the **shipped C** over 2 592
windows, three spellings to one number: **E1 2592/2592, E2 213/213, E3 2166/2166,
E4 213/213 SIGNAL, E5 2379/2379, E6 all four arms.**

### §6c ⚠ The fidelity answer is a FINDING, not a match — and the row reproduces the recorded category anyway

`controls/asan_fidelity.sh`, four builds × three windows:

| build | corpus trigger (no reuse) | trigger + reuse | control (no free) |
|---|---|---|---|
| faithful shim, no sanitizer | returns the `u64` | **SIGSEGV** | returns |
| faithful shim + ASan/UBSan | **SILENT** | UBSan `member access within misaligned address 0x1000000000004 for type 'struct zend_llist_element'` then `DEADLYSIGNAL` | silent |
| plain `malloc`/`free`, no sanitizer | **SIGSEGV** | SIGSEGV | returns |
| plain `malloc`/`free` + ASan | ⭐ **`heap-use-after-free`, `WRITE of size 4`, `#0 user_tick_function_call kernel.c:431`, `#1 zend_llist_apply kernel.c:265`** | same | silent |

⭐⭐ **The bottom-left cell is the artefact that the corpus's recorded
`heap-use-after-free` is real**: same kernel, same chain, one allocator swapped,
and frame #0 is SITE C — `basic_functions.c:2135`, the line `index.csv` cites —
with `zend_llist_apply` (SITE L's frame) directly above it.

⚠⚠ **And the top-right cell is `PROTOCOL_PHP.md` §B1 rule 1 firing on this row:
a C kernel on plain `malloc`/`free` reproduces MORE of this than pristine PHP
does.** For ASan to say *use-after-free* the block must have reached `free()`,
and a 39-byte `zend_llist_element` never does. So the row measures under the
faithful allocator, fires the sanitizer only where the block is handed back out
inside the same callback, and states the difference rather than hiding it.

⚠ **One declared expectation in that control was wrong and is recorded as such**:
I predicted `SEGV on unknown address` for the shim+ASan reuse cell and got
UBSan's misaligned-access diagnostic instead. The CATEGORY claim — not
`heap-use-after-free`, because the block never reached `free()` — is what the
expectation was for and it holds.

### §6d The gate agrees, and stage 7h was green first try

```
sanitizer          : fires on the 4 reuse inputs, clean on the other 4  -- matches model.py
sanitizer_hardened : CLEAN ON ALL EIGHT, adversarial included
```

⭐ **`check.py` stage 7h passed on the first attempt, which was a falsifiable
prediction and not a hope.** `TASK_PHP_031_REPORT` §4.4 measured R1h as changing
nothing on the benign domain and the task file said so in terms: *"if 7h fails,
something in §6 is wrong — stop and report it."* It did not fail.
⚠ `ph07` cost two tasks and a §A2a rule-refusal to reach the same place (F43/F47,
open item 24) because its upstream fix changed benign output on 13.5 % of calls.
**The difference is a property of `562f886ecb14`, not of this row's cleverness.**

---

## §7 The allocator, and why it is the mechanism here rather than the background

Every row links `common-php/emalloc_shim.h`; on this row the size-class cache
**is the defect's mechanism twice over**: it is what makes the freed element
survive with its payload intact (§6a) and it is what hands that element straight
back to the next same-class request, which is how the latent read becomes a
fault. The truncations T1/T2/T3 do **not** fire — every request is 8 or 39 bytes
— so ph64 exercises the CACHE half of the shim and none of the overflow half.

`php_shim_reset()` at the top of every kernel call is `PROTOCOL_PHP.md` §B1
rule 3 and is not optional here: the cache is the oracle, so a cache surviving
across driver iterations would make call *N*'s reuse depend on call *N−1*'s
frees. ⚠ **It also has a price this row is the first to pay, and §8 is where it
lands.**

---

## §8 The numbers — and ⚠⚠ WHICH STATISTIC THEY ARE IN

**`marginal_ir_per_call`, `O3 / isolated`** — the whole-program slope, which is
symbol-independent (`report.py`'s own preamble; `p11-nul-scan` §3 and
`p08-overlap-move` §2b are the precedents this row follows):

| rung | `small.bin` (552 B, mean n≈73) | `large.bin` (4074 B, mean n≈558) |
|---|---:|---:|
| `c-gcc` (R1) | 42,585.22 | 342,010.56 |
| `c-gcc-h` (R1h) | 42,601.20 | 342,027.51 |
| `c-clang` (R1) | 41,428.27 | 333,033.90 |
| `c-clang-h` (R1h) | 41,446.61 | 333,052.23 |
| `safe_naive` (R2) | 12,407.88 | 88,218.50 |
| `safe_tuned` (R3) | 9,351.56 | 70,330.15 |
| `unsafe` (R4) | 7,987.14 | 60,959.59 |
| `verus` (R5) | 8,180.50 | 60,930.82 |

### §8a ⭐⭐ The one clean like-for-like number: what `562f886ecb14` costs

| | `small.bin` | `large.bin` |
|---|---:|---:|
| gcc, R1h − R1 | **+15.98 Ir/call** (+0.037 %) | **+16.95 Ir/call** (+0.005 %) |
| clang, R1h − R1 | **+18.34 Ir/call** (+0.044 %) | **+18.33 Ir/call** (+0.006 %) |

**FLAT in `n`, to within 1 Ir across a 7.6× change in list length.** The
mechanism is exactly what the source says: the guard is `if (ret && tick_fe1->
calling)`, `ret` is true at most once per `zend_llist_del_element` call, and a
window makes at most two such calls — so the extra load, test and branch execute
a bounded number of times per kernel call however long the list is. **The
upstream fix for a use-after-free costs sixteen instructions per tick round.**

⚠⚠ **AND IT IS INVISIBLE IN THE PUBLISHED TABLE'S OWN COLUMN.**
`kernel_exclusive_ir` is **identical to the instruction** for `c-gcc` and
`c-gcc-h` (20,036,795 / 19,704,793 both), and `md5_fn_norel` is identical too —
because gcc keeps `ph64_unregister_tick_function` OUT OF LINE, and that is the
symbol the guard lives in. Reading the table's `Ir` column alone would support
the sentence *"R1h costs zero"*, which is false. §8c is the general form.

### §8b The Rust ladder, and one number that goes the other way from `ph16`/`ph29`

| | `small.bin` | `large.bin` |
|---|---:|---:|
| `fixed-R4 bound` = R3ship − R4ship | **+17.08 %** | **+15.37 %** |
| R2 − R4 | +55.35 % | +44.72 % |
| ⭐ R3 − R2 | **−24.63 %** | **−20.28 %** |
| R5 − R4 | +2.42 % | −0.05 % |

⚠⚠ **THE `fixed-R4 bound` IS POSITIVE HERE, AND IT IS THE THIRD PHP ROW ON THAT
QUESTION.** `.memory-php/02-ladder.md` records `ph16` at **−1.22 %** and `ph29`
at **−6.06 %** — safe-tuned CHEAPER than unsafe — and calls two rows with the
same sign "materially harder to explain as a per-row spelling artefact".
**ph64 is +15 to +17 % and breaks that pair.** ⚠ It is a bound over an
**UNSEARCHED** R4 endpoint and over one R3 spelling: `controls/spellings.py` was
NOT built (§13), so this figure is the cost of *these* spellings and the row is
unbounded in both directions exactly as `ph03` and `ph29` are.

⭐ **R3 is 20–25 % cheaper than R2 and the mechanism is named**, per
`PROTOCOL_PHP.md` §F8. Two things and both are visible in `callgrind_annotate`:

- R2 spends **3,261,108 Ir (16.5 % of its whole program)** in a symbol called
  `safe_naive::name_of` — building `[u8; 8]` byte by byte keeps the helper OUT
  OF LINE. R3's `name_of` returns the `u64` the comparison actually is and
  inlines to nothing;
- R2 spends **503,412 Ir in `realloc`**, because `Vec::new()` grows by doubling.
  R3's `Vec::with_capacity(n)` does not reallocate.

### §8c ⚠⚠⚠ THE COLUMN THIS ROW BREAKS, AND IT BREAKS IT IN BOTH DIRECTIONS

`report.py`'s own preamble warns that the `isolated` kernel-exclusive figure "is
right only when every rung does its own work inside its own symbol", and names
`p08` and `p11` as the two PAT rows where it reverses a real comparison.
**ph64 is a third, and a worse one.** Whole-program attribution,
`O3 / isolated / small.bin`:

```
c-gcc      total 66,070,064   kernel 20,036,795 (30.3%)
                              libc malloc/free and friends 39,803,304 (60.2%)
                              user_tick_function_dtor 2,988,765 (4.5%)
                              ph64_unregister_tick_function 693,416 (1.0%)
unsafe     total 12,795,571   unsafe::kernel 11,330,956 (88.6%)
                              <unsafe::Ticks>::unregister 605,264 (4.7%)
safe_naive total 19,759,221   safe_naive::kernel 12,936,157 (65.5%)
                              safe_naive::name_of 3,261,108 (16.5%)
                              realloc 503,412 (2.5%)
```

Two consequences, and both are the row's, not the harness's:

1. **The kernel-exclusive column REVERSES R2 vs R3.** It reads R3 **+2.9 %
   dearer** than R2 (13,310,049 vs 12,936,157); the marginal reads R3 **24.6 %
   cheaper**. The 16.5 % R2 spends in `name_of` is in no column of the published
   table. **Only the marginal is comparable across rungs on this row**, and that
   is the convention every number in §8 is quoted in.
2. ⚠⚠ **THE C-vs-RUST COLUMN IS NOT A SAFETY COMPARISON ON THIS ROW AND MUST
   NOT BE QUOTED AS ONE.** `PROTOCOL_PHP.md` §B forbids a Rust rung from linking
   the shim, so the four Rust rungs reproduce `php_shim_tally()` ARITHMETICALLY —
   which is exactly right for the CHECKSUM and exactly wrong for the COST. **The
   C rung allocates; the Rust rungs count.** On `ph07` that was one `emalloc` +
   one `efree` per call and it was noise. Here it is `2n + 2` per call with `n`
   up to 1014, `php_shim_reset()` empties the cache at the top of every call (§7,
   §B1 rule 3), and the result is **60 % of the C's instructions in libc**. The
   4.3–4.6× "C vs unsafe Rust" ratio in the table above is that, and nothing
   else.

   ⭐ **The general form, and it is worth more than this row: `PROTOCOL_PHP.md`
   §B2's "the Rust rungs reproduce the tally arithmetically" is free only while a
   row makes O(1) allocations per kernel call.** ph64 is the first php row where
   it is O(n), and it is the first where the C-vs-Rust column stops meaning what
   the other rows' means. A row in that position should either say so — as this
   one does — or give its Rust rungs the same allocation traffic, which for an
   index arena would be a design chosen to fit a metric.

### §8d O0, and why it is not quoted

At `O0` the ordering inverts twice over (`c-gcc` 74,113 Ir/call small vs
`unsafe` 32,432): nothing is inlined, so the C's shim calls are real calls and
Rust's accessors are too. `.memory/02-bench-rules.md` forbids resting a perf
claim on an `O0` row and this row does not.

---

## §9 ⭐⭐ The ladder result: what safe Rust buys here is a REPRESENTATION, not a check

`zend_llist_element *next` is a raw pointer. Safe Rust cannot express that list
without `Rc`, `RefCell` or raw pointers, so the faithful safe port is an
**index arena**: `next` becomes a `u32` into a `Vec<Node>` the kernel owns, and
"free" becomes "unlink".

⚠⚠ **A dangling index is then an ORDINARY IN-BOUNDS READ of a slot that is
still there — which is, to the byte, what PHP 5.0.0's size-class cache does with
the real block (§6a).** So on this row:

- **safe Rust does not turn the defect into a panic. It turns it into a WRONG
  ANSWER.** *"Safe Rust reproduces the bug"* is a FINDING and never a kill
  (`CLAUDE.md` Don't 6), and here it is the row's sharpest result;
- **what removes the defect is `562f886ecb14`'s guard, which is a LOGICAL
  invariant and not a bounds check.** R2–R5 all carry it, and they carry it for
  the answer rather than for safety;
- ⚠⚠ **`verus.rs`'s `wf` — the invariant that licenses all eight unchecked
  accessors AND every `decreases` — HOLDS WITH THE GUARD DELETED.** Memory
  safety and the upstream fix are **orthogonal** on this row. Only the value
  postcondition can see the difference, and §10 is what that cost.

⚠ **What the arena does change, declared rather than left to be noticed**
(`spec.md` `divergences[9]`): `zend_llist_add_element` appends at the TAIL, so
arena indices ASCEND along the list and stay ascending under `DEL_LLIST_ELEMENT`
(which only short-circuits `prev -> next`, and `prev < c < next`). The C's
element ADDRESSES have no such order — the cache hands blocks back LIFO. The
visit sequence, the fold and the allocator tally are identical either way
(`controls/differential.py`, 2 592 windows against the shipped C); what the arena
buys is the termination measure R5 needs.

---

## §10 The proof — what it says, and what it cost to make it say it

```
requires  off + len <= buf@.len(),  24 <= len,  len <= 268435456
ensures   r == llist_fold(buf@, off as int, len as int)
39 verified / 0 errors        47 verified / 0 errors under --cfg slb_twin
```

**`llist_fold` in `verus.rs` is a step-by-step recursion over the SAME arena the
exec code mutates** (`s_reg` / `s_del` / `s_visit` / `s_apply` / `s_destroy`,
fuel-bounded); **`llist_fold` in `model.py` is a CLOSED FORM** with no list, no
cursor and no event replay; and `model.py`'s other implementation is a
structural doubly-linked-list simulation driven at BOTH rungs. Three spellings,
one number, and the gate drives the first against the third.

⚠ **The spec walks are FUEL-bounded** because a `Seq<Node>` carries no ordering
fact by itself. The exec loops keep `fuel >= arena.len() - cur`, which `wf`
makes true, so the fuel never runs out on a reachable state. A fuel that COULD
run out would make the postcondition weaker than it looks, so the invariant is
stated and not assumed.

### §10a What made it verify, in the order it mattered

⭐ **The structural fixes came first and the budget second**, which is the right
order and is recorded because the wrong order is the tempting one:

1. **`register_all` split out of `kernel`** — the registration loop's invariants
   and the walk's are independent, and Z3's budget is not;
2. **`kernel` split into decode + `run`** — the same, one level up;
3. **`run_spec` marked `#[verifier::opaque]` and revealed once inside `run`** —
   this is the one that mattered. Without it `kernel`'s one-line body (decode,
   then call `run`) blew the budget at `rlimit(600)`: Z3 unfolds `llist_fold`
   into the whole composition, unfolds four recursive spec functions inside it
   once each by default fuel, and then tries to match that term tree against the
   same tree with differently-spelled arguments. Opaque, the match is six
   arguments and `kernel` verifies in seconds;
4. two vstd division lemmas (`lemma_div_decreases`, `lemma_div_is_ordered`) for
   the `((len - HEAD) / SLOT) as u32` cast, and `vstd::slice::group_slice_axioms`
   / `lemma_u128_shr_is_div` / `lemma_mul_inequality` in a `broadcast use` for
   the driver loop.

⚠⚠⚠ **AND THEN EVERY `#[verifier::rlimit]` CAME OUT, WHICH IS THE RESULT THIS
SECTION IS REALLY ABOUT.** The file carried `rlimit(600)` on `kernel`,
`rlimit(400)` on `run` and `rlimit(120)` on `main` while the structural fixes
were being found. Once (1)–(3) were in place they were bisected at 60 / 30 / 20 /
10 and **every one of them gives `39 verified, 0 errors`** — so they were deleted
rather than kept for reassurance, along with the `#[verifier::spinoff_prover]`
attributes. **The whole file verifies at the DEFAULT budget in ~5 s, plain and
twin.** ⭐ **Raising the budget was tried FIRST and did nothing**: `kernel` would
not verify at 600 as one function and verifies at 10 as two. A budget is not a
proof strategy, and this row is the measurement that says so.

⚠⚠ **AND ONE VERUS BEHAVIOUR COST AN HOUR AND IS WORTH WRITING DOWN.**
`del_element` originally used `return;` from inside its `while` loop, and its
postcondition failed **at that exit** while an `assert` of the *identical
proposition* placed immediately before the `return` PASSED. The repair is the C's
own spelling: `zend_llist_del_element:101` uses `break`, and with `break` the
loop needs `invariant_except_break` for the clauses that are false at the break
(the "remaining computation" equality and the arena snapshot), `invariant` for
the ones that hold at both exits, and `ensures` for what the two exits have to
agree on. **An early `return` from inside a `while` in a `&mut self` function is
where to look if a postcondition fails at an exit whose facts are all provable.**

### §10b The trusted base

**Ten `external_body` items**, eight of which have `ensures` and therefore
twins: `nnext`, `nprev`, `nname`, `ncalling` (readers), `set_next`, `set_prev`,
`set_calling` (writers), `subwin`; plus `load_input` and `emit`, which state no
`ensures` at all.

⚠ **`subwin` is called `subwin` and not `slice_subrange` for a reason the gate
found**: step 5c-twin refuses a twin whose body CALLS the trusted item, it
matches by IDENTIFIER, and a twin calling `vstd::slice::slice_subrange` reads as
calling a trusted `slice_subrange` when the row's own item shares that name.

⚠ **Eight is more than any other row in this programme carries** (`ph07` has
three, `ph29` six) and the reason is structural rather than sloppy: the arena's
element is a STRUCT, so an unchecked accessor is needed per FIELD, and the two
halves of `DEL_LLIST_ELEMENT`'s unlink are two different neighbour writes. A
whole-node read/write pair would be two items instead of seven — and would make
R4 copy 24 bytes where it now touches four, which is a design chosen to shrink a
tally rather than to be the unsafe rung.

---

## §11 Identity — `differ` at both levels, and the reason is one instruction

`results-php/ph64-callback-frees-cursor.json`, `O3 / isolated`: `unsafe` is
**385 instructions / 1747 bytes**, `verus` is **384 / 1740**. `md5_fn` and
`md5_fn_norel` both differ, so no `norel` claim is available and the pin is
`differ`.

⭐ **The difference is scheduling and not semantics.** Normalised (addresses and
symbol names masked) the two disassemblies differ in exactly two hunks: R4 emits
`incq <mem>` where R5 emits `inc %rbx ; mov %rbx,<mem>`, and one padding NOP
differs (`data16 cs nopw` vs `nopl`).

**And the run-time cost of the proof is not a cost.** `kernel_exclusive_ir` on
`small.bin` is 11,330,956 (R4) against 11,330,192 (R5) — R5 **764 Ir cheaper
over 1 500 calls, −0.007 %**. The marginal disagrees in sign between bands
(+193.36 Ir/call on `small`, −28.77 on `large`), and solving the two gives
**+227 Ir/call flat and −0.46 Ir per registered entry** — the per-entry term is
the size of the one scheduling difference in the walk, and ⚠ **the flat term I
did not isolate and do not explain.** The honest summary is that the proof is
free at run time and the two rungs differ by one instruction whose measured
direction depends on which statistic and which band you read.

⚠ At `O0` the two differ for the ordinary reason — 441/2406 against 485/2786 —
because nothing is inlined and R5's eight trusted accessors and its `run` helper
survive as real calls.

---

## §12 Controls

| file | what it decides | result |
|---|---|---|
| `562f886ecb14.patch` | the commit's 86 bytes-for-bytes | sha256 `2719dc3f143456d5…` |
| `bug41037.phpt` | upstream's own regression test, sliced out of the patch | 3 `hello`, 3 warnings |
| `bug41037.py` | replays it against both rungs | E1 3/3/0/1 · E2 R1 visits **1** · E3 both rungs identical |
| `oracle.py` | is the divergence where it must be and nowhere else | E1 2166/2166 · E2 213/213 · **E2a 213/213 (the fold is EQUAL)** · E3 213/213 · E4 2379/2379 |
| `differential.py` | the SHIPPED C against both model implementations | E1 2592/2592 · E2 213/213 · E3 2166/2166 · E4 213/213 · E5 2379/2379 · E6 four arms |
| `next_cache.py` | the counterfactual hardening | E1 189 · E2 189 · E3 189 · E4 1762 · **E5 196 (the hazard it ADDS)** |
| `predicate.py` | which `calling` the guard reads | E1 189 · E2 189 · E3 1958 · E4 2336 |
| `asan_fidelity.sh` + `.py` + `plain_alloc.h` | §A4 fidelity, four allocator × sanitizer builds | §6c |
| `dump.c` | the C half of `differential.py` and `asan_fidelity.sh` | — |

⚠ **`harness-php/gate.py` HASHES `controls/*.py` AND NEVER RUNS THEM**
(`TASK_PHP_022` m6). Every one of them ships must-fire **and** must-NOT-fire
cases, and two of them recorded a MISS of my own declared expectation rather
than rewriting it (`next_cache.py` E5, `asan_fidelity.sh` E2).

---

## §13 What this row does NOT have

1. ⚠⚠ **No `controls/spellings.py`.** The `fixed-R4 bound` in §8b is over an
   **unsearched** R4 endpoint and one R3 spelling. `.memory-php/02-ladder.md`
   already carries `ph03` and `ph29` in that state and calls it "the largest
   standing threat to the programme's headline quantity"; ph64 joins them.
   `TASK_PHP_025` shipped `ph16` with the debt declared rather than carrying it
   silently, and this row does the same — **the debt is declared here, in the
   report, and it needs its own task.**
2. ⚠ **§4d is not measured.** No PHP was built and no reproducer was run.
3. ⚠ **The `.memory-php/02-ladder.md` fix-completeness question is answered only
   for the tick list.** `562f886ecb14` is correct and minimal THERE (§4a); what
   §4d asks is whether it opens a second instance of the same class next door,
   and that is open.
4. ⚠ **`zend_llist_apply_with_argument` and `_with_arguments` are cited as a
   census (§5) and not built.** `main/php_ticks.c:71`'s walk over
   `PG(tick_functions)` is a SECOND non-`next`-caching walk on the same trigger's
   path; nothing userland-reachable calls `php_remove_tick_function`, so it is a
   clean negative rather than a second defect (`TASK_PHP_031_REPORT` §7.2).

---

SLB-TRUSTED-ARGUMENT verus.rs nnext

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `v.get_unchecked(i).next`; the twin's body is `v[i].next`. The
standard library documents `get_unchecked(i)` as `index(i)` with the bounds
check removed, so it is the same field of the same element of the same `Vec`,
and Verus checks the bound `v[i]` needs against the same `requires`. A defensive
twin — `if i < v.len() { v[i].next } else { NIL }` — cannot satisfy the
`ensures` and fails the stage rather than passing it.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes as the body stands: one expression, one unchecked read, one
field of element `i`, and `ensures r == v@[i as int].next` names that field, that
index and that `Vec`. ⚠ Nothing mechanical enforces it: a second unchecked read
the `ensures` never mentions is invisible to 5a, 5c, 5c-req and 5c-twin alike.

(c) **What is the backstop?** ⚠⚠ **Weaker here than on `ph03`, and that is
worth saying rather than copying `ph03`'s paragraph.** `ph03` leans on an
`exact` O3 identity pin: an extra read in `verus.rs` alone moves `md5_fn` and
stage 3c fails. **ph64's pin is `differ` at both levels (§11)**, so identity
compares nothing here. What remains is (i) the instruction and byte counts, both
recorded, which an added `movzbl` would move; (ii) **Miri**, which is required on
this row and which reaches this accessor on every input, because the walk calls
it once per visited element on `small.bin`'s 32 windows; and (iii) the value
postcondition itself — `llist_fold` names the fold of the names the walk
visited, so an accessor that returned a different `next` would not verify.

SLB-TRUSTED-ARGUMENT verus.rs nprev

(a) Yes — `v.get_unchecked(i).prev` against the twin's `v[i].prev`, same
argument as `nnext`.

(b) Yes as the body stands, same argument as `nnext`. ⭐ `nprev` is read at
exactly one site: `DEL_LLIST_ELEMENT`'s first arm, `if ((current)->prev)`. Its
`requires` is discharged from `wf`'s `arena[c].prev == NIL || prev < c` together
with `c < arena.len()`, which is the same fact that makes the unlink sound.

(c) Same backstops as `nnext`. ⚠ **`nprev` is the accessor whose precondition
the C does not have**: `zend_llist.c:74` dereferences `current->prev` with no
claim that `current` is still a live element, and that is the difference between
the two rungs stated as a proof obligation.

SLB-TRUSTED-ARGUMENT verus.rs nname

(a) Yes — `v.get_unchecked(i).name` against `v[i].name`.

(b) Yes as the body stands. ⭐ **`nname` carries a fact `wf` needs and the other
readers do not**: `wf` asserts `1 <= (arena[i].name as u32) <= n` for every
element, which is what lets `userland` call `unregister` with an id in range.
That fact is established at `register` by `lemma_name_id` — a one-line
`by (bit_vector)` proof that the low half of `(id as u64) | ((hi as u64) << 32)`
is `id` — and is preserved by every other operation because names are never
written after `push`.

(c) Same backstops. ⚠ An `nname` that returned the wrong element's name would
change the visit fold and fail the value postcondition, which is a stronger
backstop than this row's identity pin provides.

SLB-TRUSTED-ARGUMENT verus.rs ncalling

(a) Yes — `v.get_unchecked(i).calling` against `v[i].calling`.

(b) Yes as the body stands.

(c) Same backstops. ⭐⭐ **This is the accessor the row is about.** `ncalling` is
read at two sites: `zend_llist_apply`'s reentrancy guard (`basic_functions.c:2108`)
and `562f886ecb14`'s own predicate. In C the second of those reads
`tick_fe1->calling` through a pointer the callback may have freed — and
`controls/predicate.py` measures that reading the OTHER argument's flag instead
makes the whole fix a no-op on 189 of 189 trigger windows. Here the read is an
in-bounds arena access whose precondition `wf` discharges, which is §9's point in
one line: **the representation change removes the memory-safety question and
leaves the logical one exactly where it was.**

SLB-TRUSTED-ARGUMENT verus.rs set_next

(a) **Is the twin's body the right checked stand-in?** Yes, and it is longer
than the readers' for a reason. The unchecked operation is
`v.get_unchecked_mut(i).next = x`, which writes ONE field; `Vec::set` writes a
whole element, so the twin reads the other three fields back and writes them
unchanged — `v.set(i, Node { next: x, prev: p, name: nm, calling: c })`. That is
the same post-state, and it is exactly what the `ensures` says.

(b) **Is the `ensures` complete?** Yes, and this is the row where it matters
most. `ensures final(v)@ == old(v)@.update(i as int, Node { next: x,
..old(v)@[i as int] })` names the WHOLE post-state, so a body that also moved a
NEIGHBOUR's link could not satisfy it. ⚠⚠ **`DEL_LLIST_ELEMENT` IS A PAIR OF
NEIGHBOUR WRITES** — `(current)->prev->next = (current)->next` and
`(current)->next->prev = (current)->prev` — so an `ensures` naming only
`v@[i].next == x` would let a body that clobbered `v[i+1]` through every Verus
stage. That is precisely the completeness failure `.memory/04-verus.md` records
for `p02`'s `copy_bytes`, one data structure over.

(c) **What is the backstop?** ⚠ The identity pin is `differ`, so Miri is the
real one — and `spec.md`'s `miri.required` is `true` for exactly this reason.
`x: u32` is a PURE VALUE and needs no precondition: every one of the 2^32 values
is a legal `u32` store into a field that `Vec::push` initialised before any link
pointed at it.

SLB-TRUSTED-ARGUMENT verus.rs set_prev

(a) Yes — the mirror of `set_next`, writing the `prev` field, with the same
read-back twin.

(b) Yes, and for the same reason: these two wrappers ARE the two halves of
`DEL_LLIST_ELEMENT`'s unlink, and each writes a neighbour rather than the node
the caller's own cursor names. The whole-post-state `ensures` is what makes that
checkable.

(c) Same backstop as `set_next`: Miri, plus the value postcondition, plus the
recorded instruction and byte counts. `x: u32` is a pure value.

SLB-TRUSTED-ARGUMENT verus.rs set_calling

(a) Yes — `v.get_unchecked_mut(i).calling = x` against a read-back `Vec::set`.

(b) Yes. `x: bool` has two inhabitants and both are legal.

(c) ⭐⭐ **This wrapper is `basic_functions.c:2109` and `:2135`, and `:2135` IS
SITE C — the write R1 makes into a freed block.** The difference between the
rungs is exactly this item's precondition: here `i < old(v)@.len()` must be
DISCHARGED, and after the callback has run it is `wf` that discharges it; in C
nothing is asked and nothing is checked. Backstops as above.

SLB-TRUSTED-ARGUMENT verus.rs subwin

(a) **Is the twin's body the right checked stand-in?** Yes, and it is not
hand-written: the twin calls `vstd::slice::slice_subrange`, vstd's own checked
`&slice[i..j]` with the identical contract. The trusted body is `&v[i..j]`,
which is the same operation. ⚠ **The row's own item is called `subwin`
precisely so that this twin is a re-derivation and not a re-use**: step 5c-twin
matches the called identifier, and it refused the twin outright while the two
shared the name `slice_subrange`.

(b) **Is the `ensures` complete?** Yes. `r@ == v@.subrange(i as int, j as int)`
names the whole view of the returned slice, and a slice reference performs no
other operation.

(c) **What is the backstop?** ⚠ This item is `external_body` only because Verus
needs the view equation stated; the operation itself is a safe Rust slice index
and would panic rather than misbehave if the `requires` were wrong. It is
counted in the TCB anyway, because **every `external_body` item is TCB, not just
the interesting ones** (`.memory/04-verus.md`). Its `requires`
`i <= j <= v@.len()` is discharged in `kernel` from the row's own structural
precondition `off + len <= buf@.len()` plus
`buf@.len() == vstd::slice::spec_slice_len(buf)`.
