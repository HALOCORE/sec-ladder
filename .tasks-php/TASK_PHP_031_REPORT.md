# TASK_PHP_031_REPORT — `ph64`'s R1h, and the build brief

**Role: research engineer. One agent, alone. NOTHING WAS BUILT.** No
`patterns-php/` directory, no rung, no gate, no measurement, no row source. The
only files I created are this report and `.temp/php31/`. Per the task file I did
**not** run either staleness bracket (`TASK_PHP_028` is re-gating `ph16`/`ph29`/
`ph03` concurrently); `git status` is in §8.

---

## §0 Headline, before the detail

| | |
|---|---|
| **R1h** | ⭐ **SETTLED. `562f886ecb14`, and the corpus's column is RIGHT for once** — Antony Dovgal, 2007-04-10, *"MFH: fix #41037 (unregister_tick_function() inside the tick function crash PHP)"*. Bracketed **php-5.2.1 → php-5.2.2**, and the window admits **exactly one** change to the function. **It applies to the pristine 5.0.0 tarball with `patch -p1`, rc=0, and the result is byte-identical to php-5.2.2's function.** Backport cost: **zero**. |
| **the repair is at a THIRD site** | It patches **neither** L (`zend_llist.c:190`) **nor** C (`basic_functions.c:2135`). It patches `user_tick_function_compare` (`basic_functions.c:2146-2161`) so that `unregister_tick_function` **refuses to free an element that is currently executing**. |
| **is it correct?** | ⭐ **On the tick list, YES — and this is the FIRST of five hunted rows whose upstream fix I could not fault.** The guard's invariant is exact (§4.2). ⚠ **One incompleteness candidate, INFERENCE not measured**: the refusal path calls `php_error_docref(E_WARNING)`, which reaches a userland error handler **from inside `zend_llist_del_element`'s own walk** — a new re-entry point the fix itself introduces (§4.3). |
| **§3 — one row or two?** | ⭐⭐ **ONE ROW, and the manager's "I lean two" is refuted — not on §G's limbs but on R1h.** `562f886ecb14`'s predicate **is site C's own state variable**, set at `:2109` and cleared at `:2135`. **A row built at L alone cannot state R1h at all**, and §C forbids inventing one. Full argument in §5. |
| **§3.1 — which site?** | `c_file`/`c_lines` = **`Zend/zend_llist.c` [186,193]** (L, the defect site, the 8 lines the row is named for), with **C and the R1h frame as `extra_spans`** — `ph07`'s shape, open item 25's lesson applied at build time instead of two tasks late. |
| **is the kernel extractable?** | ⭐ **YES, measured, PASS on gcc/clang × -O0/-O3.** `.temp/php31/oracle_probe.c`, 8 scenarios, 3 must-NOT-fire, all expectations met. |
| ⚠⚠ **the manager premise that is WRONG** | **§2(b)'s explanation.** The pre-image screen did **not** miss because the file drifted. It missed because **the commit does not contain the cited statement at any line number, in any hunk** — the repair is in a different *function*. §7.1, and it generalises to **17 of the screen's 43 exclusions**. |
| ⚠ **the manager premise that is INCOMPLETE** | **§2(e)'s chain is FIVE frames, not four**, and the frame it omits is a **second** non-`next`-caching walk (`php_ticks.c:71`). §7.2. |

Everything in §2 of the task file was re-derived. **(a), (c) and (d) hold
exactly** — including `fce26e38389ba9fb…` over `Zend/zend_llist.c:186-193`, the
317-line file, `30/102`, and `21/31 = 68 %` of the temporal axis.

---

## §1 Method, and what it is *not*

Per `PROTOCOL_PHP.md` §C and §F5, in this order and no other:

1. the defect pinned by reading the **pinned tarball** (`SOURCES.md` §2 recipe;
   sha256 re-verified `5783e0c0…d6919`, 5 595 997 B; every span cross-checked
   against `patterns-php/php-5.0.0.manifest`);
2. the named commit's **patch bytes** read
   (`github.com/php/php-src/commit/562f886ecb14.patch`, cached);
3. **then** bracketed against release tags
   (`raw.githubusercontent.com/php/php-src/<tag>/<path>`, 21 tags × 2 paths),
   reporting the window;
4. R1h stated with the artefact that decides it.

⚠ **§5.1's "scan tags until one suits" trap was live and I did not take it.**
The verdict is decided by the commit's own artefacts — a bug number in the
subject, a **NEWS entry inside the commit**, and a **regression test inside the
commit** — and the tags only *confirm* it. The confirmation is a **derivation,
not a selection**: the 5.2.1→5.2.2 diff of the function **is** the commit's
hunk, line for line (§4.1), so the window admits no second candidate.

⚠ `grep -a` / `/usr/bin/grep` / `rg` throughout (F35). ⭐ And I asked about
**functions, not text** — `.temp/php31/fnbody.py` is a brace-matching extractor
with **12 declared controls including 4 must-NOT-fire**, `--selftest` PASS.
⚠⚠ **Its first version reported `(no definition in this file)` for
`user_tick_function_{call,compare}` at php-5.3.0 … master, where both functions
are plainly present** — php-src ≥ 5.3 writes `f(...) /* {{{ */` before the
brace and the naive skip stopped at the comment. **That is F35's shape inside my
own tool, it reported ABSENCE, and one line of `grep -ac user_tick` (24 hits) is
what caught it.** Fixed, and the case is now `SELFTEST` case M so it cannot
recur silently.

---

## §2 The chain, verified frame by frame in the pinned tarball

```
main/php_ticks.c:71       php_run_ticks
                            -> zend_llist_apply_with_argument(&PG(tick_functions),
                                   php_tick_iterator, &count)        <- WALK 1, no next-cache
main/php_ticks.c:59-65    php_tick_iterator  ->  func(*(int*)arg)
basic_functions.c:2139-2144 run_user_tick_functions
                            -> zend_llist_apply(BG(user_tick_functions),
                                   user_tick_function_call)          <- the call is at :2143
zend_llist.c:190          for (element=l->head; element; element=element->next)   <- WALK 2
zend_llist.c:191              func(element->data)                    <- RUNS USERLAND PHP
basic_functions.c:2109          tick_fe->calling = 1
basic_functions.c:2111-2116     call_user_function(...)   ==> userland
basic_functions.c:2860              unregister_tick_function()
zend_llist.c:98-99                    compare(current->data, key) -> DEL_LLIST_ELEMENT
zend_llist.c:85                         l->dtor(current->data)   [efree(arguments), zval_ptr_dtor]
zend_llist.c:87                         pefree(current)          <== THE FREE
basic_functions.c:2135          tick_fe->calling = 0;              <== SITE C  WRITE-AFTER-FREE
zend_llist.c:190          element = element->next                  <== SITE L  READ-AFTER-FREE
zend_llist.c:191              func(element->data)                  <== and then it FOLLOWS it
```

**Trap §5.5 discharged — `unregister_tick_function` really does free the element
the loop holds, and I asked about the FUNCTION.** `PHP_FUNCTION(unregister_tick_function)`
(`:2840-2862`) calls `zend_llist_del_element(BG(user_tick_functions), &tick_fe,
user_tick_function_compare)` at `:2860`; `zend_llist_del_element` (`:91-104`)
expands `DEL_LLIST_ELEMENT` (`:73-88`), whose last two statements are
`pefree((current), (l)->persistent)` and `--l->count`. `l->persistent` is **0**
(`register_tick_function:2824` passes `0` to `zend_llist_init`), so `pefree` is
`efree`. `l->dtor` is `user_tick_function_dtor` (`:2074-2082`), which
`zval_ptr_dtor`s every argument and `efree`s the `arguments` array — so the
chain produces **three** dangling references, not two: `element` (site L),
`element->data` / `tick_fe` (site C), and `tick_fe->arguments[0]`, which the
comparator reads on any subsequent walk.

### ⭐ Why L is *the defect*, argued C-side, from the same file

`.temp/php31/logs/walkcensus.log` — the six callback-driven walks in
`Zend/zend_llist.c`:

```
  zend_llist_del_element     :91-104   caches_next=YES  callback=compare(current->data, element)
  zend_llist_destroy         :107-121  caches_next=YES  callback=l->dtor(current->data)
  zend_llist_apply_with_del  :171-183  caches_next=YES  callback=func(element->data)
  zend_llist_apply           :186-193  caches_next=no   callback=func(element->data)
  zend_llist_apply_with_argument  :229-236  caches_next=no
  zend_llist_apply_with_arguments :239-249  caches_next=no
```

⭐⭐ **`zend_llist_apply_with_del` is FIFTEEN LINES ABOVE `zend_llist_apply`,
takes the same caller-supplied `func`, and caches `next = element->next` at
`:177` BEFORE calling it.** The same file, the same authors, the same walk
written safely — and the three `apply*` members that advance in the `for`
header are the three that do not. **That is the C-side "why", it needs no Rust
and no ladder, and it is the strongest form the argument can take: upstream had
the defence in hand, in the same translation unit, and did not apply it here.**
(§6 records what that buys the row as a *control*, not as R1h.)

---

## §3 R1h — the verdict, `_029`'s shape

```
ph64 · CRASH-086 · ext/standard/basic_functions.c:2135  (cited)
                   Zend/zend_llist.c:186-193            (defect, per CATALOGUE.md)
                   ext/standard/basic_functions.c:2146-2161  (WHERE THE REPAIR LANDS)
```

| | |
|---|---|
| named `fix_commit` | **`562f886ecb14`** — Antony Dovgal `<tony2001@php.net>`, **2007-04-10 09:37:09 +0000** |
| subject | *"MFH: fix #41037 (unregister_tick_function() inside the tick function crash PHP)"* |
| does it touch the **cited** line's statement? | ❌ **NO.** `grep -ac 'calling = 0'` over the 86-line patch → **0**. The statement survives unchanged at php-5.2.2 (1 occurrence, untouched) |
| does it touch the **defect** (`zend_llist_apply`)? | ❌ **NO.** The commit touches 3 files and none is `Zend/zend_llist.c` |
| does it **remove the defect**? | ✅ **YES — by making the free unreachable.** It is a real repair (§4) |
| first tag with the guard | **php-5.2.2** (absent in php-5.2.1) → **window php-5.2.1 → php-5.2.2**, and the commit's date sits inside it (5.2.1 = 2007-02-08, 5.2.2 = 2007-05-03) |
| **R1h VERDICT** | ⭐ **`562f886ecb14`, whole, unmodified, one hunk, 7 added / 2 deleted lines in one function** |
| artefacts, all three **inside the commit** | **(1)** bug number **#41037** in the subject; **(2)** a **NEWS entry** the commit itself adds — `+- Fixed bug #41037 (unregister_tick_function() inside the tick function crash PHP). (Tony)`; **(3)** a **regression test** the commit itself adds — `ext/standard/tests/general_functions/bug41037.phpt`, 23 lines, whose `--EXPECTF--` is three `Unable to delete tick function executed at the moment` warnings |
| **plus the derivation** | the php-5.2.1 → php-5.2.2 diff of `user_tick_function_compare` **is this commit's hunk, line for line** (below). **The window admits one candidate; nothing was selected.** |

### The hunk

```diff
 static int user_tick_function_compare(user_tick_function_entry * tick_fe1, user_tick_function_entry * tick_fe2)
 {
 	zval *func1 = tick_fe1->arguments[0];
 	zval *func2 = tick_fe2->arguments[0];
+	int ret;
 	TSRMLS_FETCH();

 	if (Z_TYPE_P(func1) == IS_STRING && Z_TYPE_P(func2) == IS_STRING) {
-		return (zend_binary_zval_strcmp(func1, func2) == 0);
+		ret = (zend_binary_zval_strcmp(func1, func2) == 0);
 	} else if (Z_TYPE_P(func1) == IS_ARRAY && Z_TYPE_P(func2) == IS_ARRAY) {
 		zval result;
 		zend_compare_arrays(&result, func1, func2 TSRMLS_CC);
-		return (Z_LVAL(result) == 0);
+		ret = (Z_LVAL(result) == 0);
 	} else {
+		ret = 0;
+	}
+
+	if (ret && tick_fe1->calling) {
+		php_error_docref(NULL TSRMLS_CC, E_WARNING, "Unable to delete tick function executed at the moment");
 		return 0;
 	}
+	return ret;
 }
```

### The tag bracket (`.temp/php31/fetch.sh`, `fnbody.py`)

Function bodies, hashed. **`user_tick_function_compare`:**

```
php-5.0.0  :2146  16 L  418a53cb63037006   guard ABSENT
php-5.0.5  :2160  16 L  418a53cb63037006   guard ABSENT   <- byte-identical to 5.0.0
php-5.1.0  :2310  16 L  418a53cb63037006   guard ABSENT
php-5.1.6  :2344  16 L  418a53cb63037006   guard ABSENT
php-5.2.0  :5288  16 L  418a53cb63037006   guard ABSENT
php-5.2.1  :5312  16 L  418a53cb63037006   guard ABSENT   <- LAST tag without it
php-5.2.2  :5323  23 L  4ae3d1c82072e782   guard PRESENT  <- FIRST tag with it
php-5.2.17 :5403  23 L  4ae3d1c82072e782   guard PRESENT
php-5.3.0  :5002  27 L  edbd5d31d7d3ce34   guard PRESENT
php-7.0.0  :4977  22 L  e80f621bed775bfb   guard PRESENT
php-8.3.0  :1665  22 L  28b37495a158f036   guard PRESENT
master     :1636  10 L  a8baef304c3f80ba   guard PRESENT
```

⭐ **The guard survives into `master`, and upstream STRENGTHENED it**:
`php_error_docref(E_WARNING)` became `zend_throw_error(NULL, "Registered tick
function cannot be unregistered while it is being executed")`. **That is an
independent upstream artefact that this is the accepted repair** — 18 years,
never reverted, and upgraded. (It is also a partial answer to §4.3: a thrown
`Error` cannot run userland; a warning can.)

### The backport, and it costs nothing

```
$ patch -p1 --dry-run < bf.patch          # only the basic_functions.c file-diff
checking file ext/standard/basic_functions.c
Hunk #1 succeeded at 2147 with fuzz 1 (offset -3170 lines).
rc=0
$ python3 fnbody.py <patched 5.0.0> user_tick_function_compare
### first_line=2146  lines=23  sha256=4ae3d1c82072e782     <- == php-5.2.2's, byte for byte
```

⚠ **The `fuzz 1` is ONE line of trailing context, OUTSIDE the function, and the
patch neither adds nor deletes it**: the commit's tree has `void
php_call_shutdown_functions(TSRMLS_D)` where 5.0.0 has `…(void)`. Everything
inside `user_tick_function_compare` matches exactly, because **5.0.0's function
is byte-identical to php-5.2.1's** (`diff logs/cmp_5.0.0.txt logs/cmp_5.2.1.txt`
→ IDENTICAL). **The whole-file diff after the apply is exactly the commit's 7
added and 2 deleted lines and nothing else.**

⭐ **This is the cleanest R1h backport in the programme so far** — cleaner than
any of `_029`'s five, all of which needed a witness tag because the commit's
pre-image was a later rewrite. Here the pre-image *is* 5.0.0.

### And `zend_llist_apply` is NEVER repaired — ever

```
zend_llist_apply body, sha256 over the 8 lines:
php-5.0.0 … php-5.6.0   b6de446154e2ed86   (12 tags, byte-identical)
php-7.0.0               a5ed671fb22ca47e   TSRMLS removal ONLY
php-8.3.0, master       a5ed671fb22ca47e   TSRMLS removal ONLY
```

⚠⚠ **The loop at `:190` is unchanged in php-src master, 21 years on.** So *"does
`zend_llist_apply` ITSELF ever get repaired upstream?"* — task file §4.2's
starred question — is answered: **NO, and this is a proof, not a search.** The
only change is `TSRMLS_DC`/`TSRMLS_CC` deletion. **A row built at L therefore
has no R1h of its own**, which is §5's whole argument.

⚠ And there is a reason it was never repaired: at 5.0.0 the tick list is the
**only** userland-reentrant caller of `zend_llist_apply` — all 8 call sites,
`grep`ed as a function:

```
ext/standard/basic_functions.c:2143   user_tick_function_call     <- runs USERLAND
main/php_ini.c:549, :550              php_load_*_extension_cb
sapi/{cgi,cli}/…:1515, :934           php_register_command_line_global_vars
Zend/zend_execute_API.c:158, :208     zend_extension_{activator,deactivator}
Zend/zend_extensions.c:166            zend_extension_shutdown
```

**Seven of eight cannot re-enter userland. Fixing the one caller closes the one
exposure** — which is why a container-level fix was never owed, and it is also
the clean negative against reading the missing `next`-cache as an unexploited
hole elsewhere.

---

## §4 Is the fix CORRECT, and is it COMPLETE?

⚠⚠ Task file §5.2: *"in four built rows the fix has been incomplete or wrong
FOUR TIMES — there is no run here, and no prior you may lean on."* I attacked it
and here is what I found, split into what I measured and what I did not.

### 4.1 It is the right fix, and it is minimal

Not a rewrite, not an optimisation (§5.3's trap): one hunk, one function, 7
added / 2 deleted lines, and every added line is either the `int ret` the
refactor needs or the guard itself. The refactor of the three `return`s into
`ret` exists **only** so a single exit point can carry the guard. Nothing else
in the commit touches C.

### 4.2 ⭐ Its invariant is EXACT on the tick list — argued, and probed

The guard's claim is *"never free an element that a live walk's cursor points
at"*. It enforces it via `tick_fe1->calling`, and **that is exactly the right
predicate**, because:

- `zend_llist_apply` advances **only after `func` returns** (`:190`, the `for`
  header runs after the body);
- `user_tick_function_call` sets `calling = 1` at `:2109` and clears it at
  `:2135`, i.e. **for precisely the duration of the userland call**;
- so **every element that any live `zend_llist_apply` frame's `element`
  variable points at has `calling == 1`**, including under nested tick dispatch
  (`php_run_ticks` has no re-entrancy guard, so the walk *can* nest — and each
  nesting level's cursor is protected by its own entry's flag);
- and the elements the guard does **not** protect need no protection:
  `DEL_LLIST_ELEMENT` repairs both neighbours' links, so deleting a
  non-executing element leaves every live cursor valid.

⚠ `tick_fe1` is `current->data`, the **list** element, not the search key —
verified against `zend_llist_del_element:98`'s `compare(current->data, element)`.
That matters, because `PHP_FUNCTION(unregister_tick_function)` builds its key
with **`calling` uninitialised** (`:2843-2859` set only `arguments` and
`arg_count`). Had the guard read `tick_fe2->calling` it would have been a read
of an indeterminate stack `int`. **It reads the right one.**

Three of these limbs are **measured**, not argued —
`.temp/php31/logs/oracle_probe.log`, scenarios S3 (delete the entry *ahead*),
S3b (delete the entry *behind*) and S4 (delete nothing): all three must-NOT-fire
and all three are silent, at both rungs, `fold`/`tally`/`count` identical.

### 4.3 ⚠⚠ ONE incompleteness candidate — INFERENCE, NOT MEASURED

**The fix's refusal path runs arbitrary userland code from inside
`zend_llist_del_element`'s own walk, and that walk holds two raw element
pointers.** Chain, every link read at source:

```
php_error_docref  ==  php_error_docref0            (main/php.h:324)
                  ->  php_verror                   (main/main.c:431)
                  ->  php_error(type, "%s", message)   [php_verror's last statement]
                  ->  zend_error                   (Zend/zend.c:866)
   zend_error, `default:` arm:  if EG(user_error_handler) is set and
   EG(user_error_handler_error_reporting) & E_WARNING, it does
       call_user_function_ex(CG(function_table), NULL, orig_user_error_handler, ...)
   -- verified at 5.0.0 (Zend/zend.c:866-1014) AND at php-5.2.2, the tag the
   fix shipped in (`set_error_handler` -> arbitrary PHP runs here).
```

Now the reachability, with `set_error_handler` installed and the list
`[A(executing), B(idle)]`:

```
userland A: unregister_tick_function('a')
  zend_llist_del_element:  current = A;  next = A->next = B        (:97)
  compare(A, 'a') -> ret=1, A->calling=1
      -> php_error_docref(E_WARNING)  -> user error handler runs
             handler: unregister_tick_function('b')
                nested del_element -> DEL_LLIST_ELEMENT(B) -> pefree(B)   <== B FREED
      -> compare returns 0
  current = next = B  (FREED)                                      (:102)
  while (current) -> true
  next = current->next          <== READ-AFTER-FREE                (:97)
  compare(current->data, 'a')   <== reads tick_fe1->arguments[0], and `arguments`
                                    was efree'd and its zval zval_ptr_dtor'd
                                    by the dtor -- TWO more dereferences of freed
                                    memory, one of them through a freed pointer
```

⚠⚠⚠ **If this holds, `562f886ecb14` closes one instance of the class and opens
another instance of the same class, in the function next door.** Before the
fix, `user_tick_function_compare` had no unconditional path to userland; after
it, the refusal path always has one.

⚠⚠ **I DID NOT MEASURE THIS AND IT IS INFERENCE.** I did not build 5.2.2, did
not run PHP, and did not check whether `zend_error`'s `EG(user_error_handler) =
NULL` window or `EG(error_handling) == EH_THROW` blocks the specific nesting.
**The probe cannot speak to it either, and that is deliberate and stated in the
probe's own header**: it projects `php_error_docref` to a counter, and *that
projection is exactly what hides this defect*.

⭐ **The test is one PHP file and it is cheap.** A build task should run, on a
5.2.2 ASan build:

```php
<?php
set_error_handler(function($n,$s){ unregister_tick_function('b'); return true; });
function a(){ unregister_tick_function('a'); }
function b(){ }
declare(ticks=1);
register_tick_function('a');
register_tick_function('b');
$x=1; $y=2; $z=$x+$y;
```

**Do not write this into a finding until it is measured** (`_029` §3's
discipline, and `PROTOCOL.md` rule 9's conclusion/mechanism split: the
*conclusion* "R1h introduces a userland re-entry inside the deleter's walk" is
static and verified at source; the *mechanism reaching a fault* is open).

### 4.4 ⭐ A clean negative worth as much as the finding

**R1h changes NOTHING on the benign domain.** Measured, both rungs, four benign
scenarios (S0, S3, S3b, S4): `fold`, shim `tally` **and** `l->count` all
identical between R1 and R1h. **It differs only on the adversarial input.**

⚠⚠ **That is `check.py` stage 7h's exact concern, and this row passes it where
`ph07` cost two tasks and a §A2a rule-refusal to get there** (F43/F47, open item
24). A build task should expect stage 7h green on the first attempt — and if it
is not, the hypothesis is about the row, not the gate.

---

## §5 ⭐⭐ §3 answered: ONE ROW, at L, with C in `extra_spans`

### 5.1 Are L and C one row or two? — **ONE**, and here is the argument the task file did not have

The manager's §6.1 says *"I lean two, and I am aware that 'the manager leans' is
how ph03/ph07 ended up as one family nobody noticed. Attack it."* Attacked, and
it does not survive. Three arguments, strongest first.

**(1) ⭐⭐ R1h BINDS THEM, and this is decisive on its own.**
`562f886ecb14`'s guard is `if (ret && tick_fe1->calling)`. The `calling` field
is declared at `basic_functions.c:157`, **set at `:2109` and cleared at `:2135`
— and `:2135` IS SITE C**. So:

- **A row built at L alone has no `calling` field, therefore no predicate,
  therefore no R1h.** It would have to invent a hardening — and
  `PROTOCOL_PHP.md` §C is *"`c/kernel_hardened.c` is the `fix_commit` patch
  backported and sha-pinned… here we do not [argue our hand-written hardening
  is fair]."* **An L-only row breaks §C.**
- **A row built at C alone has no cursor, therefore nothing for the guard to
  protect**, and its `spec.md` would have to explain why an upstream fix to a
  *comparator* is the fix for a *write* — a story that only makes sense with the
  loop in front of you.

So the two candidate single-site rows are not two faithful extractions. They are
**one chain with a different half amputated**, and each amputation destroys the
row's ability to state its own R1h.

**(2) They are not independently triggerable.** There is **one** trigger — a
tick function that unregisters itself — and it produces **both** dereferences,
always, in a fixed order. Measured: ASan on plain malloc/free reports the
**WRITE at site C first** (§6.2), and the read at L follows in the same
statement's continuation. You cannot construct an input that fires L without C
or C without L. Under §G limb (b), the attacker-controlled quantity is
**identical** and there is only one of it.

**(3) ⭐ The two candidate hardenings fix DIFFERENT halves, and only a joint row
can measure that.** Upstream's comparator guard prevents the free, so it fixes
**both** L and C. The `next`-caching idiom `zend_llist_apply_with_del:177`
already uses fifteen lines above (§2) fixes **L only** — site C still writes
into the freed block. **A row carrying both sites gets to price that asymmetry
against the real fix; a single-site row cannot see it.** That is the row's best
finding and it is unavailable if you split.

### 5.2 ⚠ Where §G lands, stated honestly, and why I am not deciding on it

At the level of description `CATALOGUE.md` itself uses — *"the callee unlinks
and frees the very element the loop holds"* — §G's three limbs give:

| limb | L vs C | evidence for |
|---|---|---|
| (a) unchecked predicate | **SAME** — *`element`, and therefore `element->data`, outlives `func`*. There is exactly one lifetime fact in question and one `pefree` that falsifies it | same |
| (b) attacker-controlled quantity | **SAME** — the callback's self-unregistration. There is no second input | same |
| (c) fault primitive | **DIFFERENT** — read of a link field at block+0, then *followed*; vs write of a payload field at block+28 | different |

⚠⚠ **So §G's letter says "two rows"** (kill only on all three; anything else is
a row) **and I am not using it, for a stated reason: §G is a rule for admitting
a CANDIDATE against a BUILT OR CATALOGUED row, and its burden is deliberately
placed so that doubt produces MORE rows.** Pointed at *"should this one
catalogued row become two?"* the same asymmetry splits on doubt, which is not
obviously the safe direction and is not what §G was argued for.
`PLAN_PHP.md` §3.1 makes "two rows" **available** — it is not wrong, and a later
task may still take it. **What decides it here is §5.1(1): only the joint row
can ship a sha-pinned upstream R1h**, and that is a property of the fix, not of
the description level. ⚠ **I am reporting §G's disagreement rather than hiding
it** — the same thing `_029` §2 did on `ph73`.

### 5.3 ⚠ §3.1's premise, corrected

The task file offers: *"L is the standalone container (F1's shape, 8 lines, no
PHP machinery) and is my prior; C needs the tick-function registry and a
zval."* **Half of that is right and the half that is wrong changes the answer.**

- ✅ `Zend/zend_llist.c` **is** standalone — no zvals, no executor, no hash
  table, and only `TSRMLS_*` plumbing to remove. 317 lines, and the row needs
  ~70 of them.
- ❌ ⚠⚠ **But the 8 lines are not a row on their own, and §6.3 predicted this
  correctly.** The read-after-free at `:190` requires **something to free
  `element` during `func`**, and the only thing in PHP that does is
  `zend_llist_del_element` driven by a comparator — so an L-sited row carries
  `DEL_LLIST_ELEMENT`, `del_element`, the entry struct, a comparator, **and the
  `calling` flag**, the last three of which live in `basic_functions.c`.
  **Measured**: `.temp/php31/oracle_probe.c`'s faithful chain is ~140 lines of
  transcribed C, not 8.
- ⭐ **So §3.1's cost comparison is between the wrong two options.** The real
  choice is *"one row citing both files"* versus *"two rows each citing both
  files and each unable to state R1h"*. The first is strictly cheaper.

### 5.4 Which span is PRIMARY, and what `provenance.py` does with it

`harness-php/provenance.py:172-176` — the kernel overlap is computed **over the
UNION of every cited span**, and every `extra_spans` entry is checked exactly as
the primary is. So the primary choice is about which **claim** is primary, not
about coverage.

**Primary = `Zend/zend_llist.c` [186,193].** Three reasons:
`.memory-php/01-extraction.md` says `provenance.c_file`/`c_lines` name the
**defect** site and the other two sites go in the row's notes; `CATALOGUE.md`'s
own Part A/B header names L; and F1 is precisely that
`c_file_line` names the **faulting frame**. ⚠ **And here F1 is subtler than
usual, so say it in `spec.md` rather than repeating the slogan: `:2135` is not a
mis-citation. It is the FIRST faulting access in the chain** — ASan on plain
malloc/free reports it as the initial `heap-use-after-free`, a `WRITE of size 4`
— **and the corpus's own history record says exactly that** (`c_function:
user_tick_function_call`, then *"and the apply loop then reads element->next"*).
So on this row the cited line is the faulting frame *and* the first fault, and
the defect is still one call up.

---

## §6 THE BUILD BRIEF

### 6.1 `provenance` — ready to paste, every `extra_sha256` computed

Canonical `extract_sha256` = sha256 of the bytes
`tar -xzOf <tarball> php-5.0.0/<path> | sed -n 'a,bp'` prints
(`.temp/php31/spans.sh` regenerates the whole table).

**PRIMARY**

| field | value |
|---|---|
| `c_file` | `Zend/zend_llist.c` |
| `c_lines` | `[186, 193]` |
| `extract_cmd` | `tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.c \| sed -n '186,193p'` |
| `extract_sha256` | `fce26e38389ba9fb7909f94c7fcfaed8a48f7960ba92c6d132812a958c40e917` |

**`extra_spans` — MUST cite (the kernel lifts them, or R1h occupies them)**

| `c_file` | `c_lines` | L | `extract_sha256` | `why` (in one line — write it out properly) |
|---|---|--:|---|---|
| `Zend/zend_llist.h` | `[25, 29]` | 5 | `c171e9616068985524cbc37f9d9523ba9f36208db3c0e7a5d685e8a94582a03b` | `zend_llist_element` — `next` is at **offset 0**, so site L's read-after-free is the freed block's first word. Load-bearing for the oracle |
| `Zend/zend_llist.h` | `[37, 45]` | 9 | `c0e8e19b6f9a810a104b3d606abd104367b32f7bf3a3ad2c3a38b7224d3e2ef1` | `zend_llist` — `head`/`tail`/`count`; `count` is half the R1-vs-R1h oracle |
| `Zend/zend_llist.c` | `[26, 34]` | 9 | `fbbb2fb69b643cd4b4eee95861f1f72119c24f4090a7bc92715e35c33b9ae31c` | `zend_llist_init` — sets `persistent = 0`, i.e. `pefree` == `efree` |
| `Zend/zend_llist.c` | `[37, 52]` | 16 | `6b80ae8a75f7586252791e888218a4547ffb8514c52203d2a2322b987813c461` | `zend_llist_add_element` — the `sizeof(elem)+size-1` request that decides the size class |
| `Zend/zend_llist.c` | `[73, 104]` | 32 | `b714ec3184afe1e0a68d30997c480c5d5b5810a3d454aacfbcb915e268146493` | `DEL_LLIST_ELEMENT` + `zend_llist_del_element` — **THE FREE SITE**, and the walk §4.3's candidate lives in. (Split as `[73,88]` = `39c2eb4c…477a` and `[91,104]` = `cf34ef8e…81fc` if two claims are wanted) |
| `ext/standard/basic_functions.c` | `[154, 158]` | 5 | `b5f23b9dc0b83a10b09fa6266b9fd980528afe5a6a06108d1afb1634496f8941` | `user_tick_function_entry` — declares **`calling`**, which is site C's target *and* R1h's predicate |
| `ext/standard/basic_functions.c` | `[2102, 2137]` | 36 | `bacb13c0332f3ec4b51e2446c5ff586c3c44e7fb0fcf43c8e2dd6f35bca5a247` | **SITE C.** `user_tick_function_call`; the write-after-free is `:2135`, and `:2109`/`:2135` are the two lines that make R1h's predicate true |
| `ext/standard/basic_functions.c` | `[2146, 2161]` | 16 | `a429912167dab97bb93e08c6864a3666afb1d90b0513917bb38ca72fc49622f7` | ⭐ **WHERE R1h LANDS.** `user_tick_function_compare`. Open item 25's whole lesson: cite the frame the fix goes in, or the overlap number certifies a span containing neither the fix nor its frame |
| `ext/standard/basic_functions.c` | `[2074, 2082]` | 9 | `a84dcb7e67109c37532329ac3b3598dda80c4fbaa0b08c1208e1f43e55c9e81f` | `user_tick_function_dtor` — what the free destroys besides the element: `arguments` and its zvals, i.e. the chain's third dangling reference |

**`extra_spans` — SHOULD cite (only if the kernel lifts them)**

| `c_file` | `c_lines` | L | `extract_sha256` | what |
|---|---|--:|---|---|
| `ext/standard/basic_functions.c` | `[2139, 2144]` | 6 | `d64eae1b992514d19098b45efbe692573dc02b165d059609090abc19811e73db` | `run_user_tick_functions`, the bridge; the `zend_llist_apply` call is at **`:2143`** |
| `ext/standard/basic_functions.c` | `[2840, 2862]` | 23 | `ef14ca8cae07f307be5c95bdaffcaa2dafed36b61cb15f48da59a8c1f07f5b8d` | `PHP_FUNCTION(unregister_tick_function)` — the trigger's entry point; `narrowed` (zval unpack comes off) |
| `ext/standard/basic_functions.c` | `[2799, 2835]` | 37 | `a002a982f92b9262ee0ea8f1cb11d2e6a13715dbce96a5ab847a497b9204a3c0` | `PHP_FUNCTION(register_tick_function)` — sets `calling = 0` at `:2804` |

⚠ **Do NOT cite `[2135,2135]` as a span.** It is one line, it would score ~0 on
overlap, and `provenance.py` wants a span the kernel actually lifts. Cite
`[2102,2137]` and name `:2135` in the `why`.

### 6.2 Tier — **`narrowed`**, and here is the argument

⚠ **Not `verbatim`, and `CATALOGUE.md:170`'s Part A cell says `verbatim`.** That
cell is right about `Zend/zend_llist.c` and wrong about the row, because the row
must lift `basic_functions.c` too:

- `Zend/zend_llist.{c,h}` lifts **`verbatim`** — only `TSRMLS_DC`/`TSRMLS_CC`
  come off, and `pemalloc`/`pefree` redirect to `php_shim_emalloc`/`efree`
  (a `substitution` under §A1's clause: PHP's own `pemalloc` with
  `persistent == 0` *is* `emalloc`, so the `why` genuinely ends in "no
  semantics").
- `basic_functions.c:2102-2137` needs a **wrapper removal**: `zval **arguments`
  becomes an opaque block and `call_user_function(EG(function_table), NULL,
  function, &retval, argc-1, args+1)` becomes a function-pointer call. That is
  §A1's definition of `narrowed` — *"a wrapper comes off (zval unpacking,
  argument parsing); the body is unchanged"* — and the body (the `calling`
  guard, the two flag writes, the error arms) **is** unchanged.
- `basic_functions.c:2146-2161` likewise: `zend_binary_zval_strcmp` /
  `zend_compare_arrays` become an id comparison, and the `Z_TYPE_P` dispatch
  is a projection to the reachable arm.

⚠⚠ **A tier is a COST, never a filter** (§A1, `.memory-php/01-extraction.md`).
`narrowed` costs the row a 25 % overlap expectation instead of 50 %
(`provenance.py`, reported not enforced since `TASK_PHP_008` §2) — and with 9
spans in the union that number will be low and **should be read and commented
on in `NOTES.md`, per §F9.** ⭐ **This is the first `verbatim`-or-`narrowed`
multi-span php row and §F9 says the first one is where the demotion stops being
free.** Say what you think of the number.

**`divergences` the row owes, at minimum** (one entry each, §A2):
`TSRMLS_DC`/`TSRMLS_CC` (`deletion`, ×5 sites); `pemalloc`/`pefree` →
`php_shim_emalloc`/`efree` (`substitution`, `zend_llist.c:39,87,116,147`, with
the `persistent == 0` demonstration); `zval **arguments` → opaque block
(`narrowing`/`projection`, `basic_functions.c:155`); `call_user_function` →
function pointer (`projection`, `:2111-2116`); the three `php_error_docref`
error arms (`projection`, `:2122-2132`); ⚠⚠ **and `php_error_docref` on R1h's
refusal path (`projection`, the R1h hunk) — and that entry's `why` CANNOT end in
"no semantics", because §4.3 is exactly the semantics it removes. Say so
explicitly; it is the row's most interesting divergence.**

### 6.3 The trigger, the fixture, and §A2a's two rules

**Trigger:** a registration/unregistration stream in which one entry's callback
unregisters **itself**, plus one same-size-class allocation inside that
callback. Precisely: a tick function that calls `unregister_tick_function` on
its own name and then allocates ~33-40 bytes.

⚠ **§A2a rule 1 — the fixture must reach every arm of the branch the defect
lives on, and `inputs/gen.py` must ASSERT it.** The branch here is
`DEL_LLIST_ELEMENT`'s **four** arms (`prev` / no `prev` × `next` / no `next`),
and they are *not* interchangeable — the probe's S2/S5/S6 are the mid, head and
tail cases and all three fault, but by different routes (S6's `element->next`
was `NULL`, so the reuse *creates* a successor where the loop would have ended).
**A corpus that only ever unregisters a middle element misses two arms.**
`gen.py` must re-derive, from what it just emitted, that all four arms are
reached, in the shape of `ph03`'s `_check_span`.

⚠ **§A2a rule 2 — `model.py::selfcheck` must sweep a domain it constructs.**
`.temp/php31/oracle_probe.c`'s 8-scenario table is the shape: list length ×
which position self-unregisters × reuse on/off, with the must-NOT-fire controls
in the same table. That is milliseconds and needs no `.bin`.

### 6.4 ⭐⭐ THE ORACLE — measured, and it is the thing that would have stalled a build task

`.temp/php31/logs/oracle_probe.log`. **8 scenarios × 2 rungs, forked so a SEGV
is a reported outcome, all declared expectations met, PASS on gcc/clang ×
-O0/-O3** (`logs/sweep.log`).

The layout arithmetic first, because everything follows from it:

```
sizeof(zend_llist_element) = 24     offsetof(element, next) = 0    <- SITE L reads THIS word
sizeof(user_tick_function_entry) = 16   offsetof(element, data) = 16
add_element request        = 39     `calling` at element+28        <- SITE C writes HERE
REAL_SIZE(39)              = 40     (zend_alloc.c:132, :135)
cache_index = 40>>3        = 5      (MAX_CACHED_MEMORY 11, zend_alloc.h:63)
=> a freed element is CACHED: NOT returned to malloc, PAYLOAD UNTOUCHED
```

| | R1 | R1h | R1 vs R1h |
|---|---|---|---|
| **S0** benign, no unreg | visits 3, fold `1000008000018`, count 3, tally `147772514` | identical | fold **NO**, tally **NO**, count **NO** |
| ⭐ **S1** SELF-unreg, **no reuse** — *the corpus trigger* | visits **3**, fold `1000008000018`, count **2**, dtors 1, tally `147869856` | visits 3, fold **the same**, count **3**, dtors 0, refusals 1, tally `147772514` | fold **NO**, tally **YES**, count **YES** |
| ⭐ **S2** SELF-unreg **+ same-class reuse** | **SIGSEGV** | visits 3, clean | one rung faulted |
| **S3** unreg the entry AHEAD | visits 2, fold `1000005` | identical | NO / NO / NO |
| **S3b** unreg the entry BEHIND | visits 3, count 2 | identical | NO / NO / NO |
| **S4** *no unreg* + same-class reuse (**the §5.4 control**) | visits 3, fold `1000008000018`, sentinel **clean** | identical | NO / NO / NO |
| **S5** SELF-unreg at the **head** + reuse | **SIGSEGV** | clean | one rung faulted |
| **S6** SELF-unreg at the **tail** + reuse | **SIGSEGV** | clean | one rung faulted |

⚠⚠⚠ **READ S1 FIRST, BECAUSE IT IS THE TRAP A BUILD TASK WOULD FALL INTO.**
On the corpus's own trigger, with the faithful allocator and no reuse, the
read-after-free at site L is **LATENT: the visit fold is BIT-IDENTICAL between
R1 and R1h.** The 40-byte block goes into `cache[5]`, is not returned to
`malloc`, and nothing scribbles the payload — so `element->next` still reads the
true successor and the walk visits every remaining node exactly once. **This is
what `crashes_pristine_5_0_0 = False` is, and it is `PROTOCOL_PHP.md` §B1 rule 1
firing on this row.** A row whose only oracle is *"which elements got visited"*
— which is exactly what `CATALOGUE.md:795` proposes — **would gate green with
R1 and R1h agreeing and would measure nothing.**

**Two oracles work, and the row should ship BOTH:**

1. ⭐ **The cheap one, no modelling risk: `php_shim_tally()` folded into the
   `u64`, plus `l->count`.** Measured on S1: tally `147869856` vs `147772514`,
   count 2 vs 3, dtors 1 vs 0. This is §B1 rule 2 doing exactly its job — the
   defect lands in the checksum the gate compares across rungs and not only in a
   sanitizer. **No injected allocation, no extra modelling, and it is
   deterministic.** ⚠ Note it is a *free-count* oracle, so it is evidence that
   the fix fired, not evidence that the fault was harmful.
2. ⭐ **The sharp one: make the reuse happen, faithfully.** One
   `emalloc(sizeof(element)+size-1)` inside the driver's userland callback after
   the self-unregistration — which is what any PHP tick function body does with
   any small allocation — LIFO-pops the just-freed element and R1 **faults** at
   all three `DEL_LLIST_ELEMENT` arms while R1h is clean.
   ⚠⚠ **This is the shape §5.4 warns about, so the row must ship S4 as a
   `controls/` must-NOT-fire: the SAME injected allocation with NO free leaves
   `fold`, `tally` and `count` all identical.** Without S4 the divergence could
   be the allocation and not the free, and nothing in the number says which.
   ⚠ A row cannot *measure* a faulting cell (the driver loop dies), so oracle 2
   belongs in `controls/`, and oracle 1 in the measured `u64`.

**§A4 fidelity — and the answer is a finding, not a match:**

| build | S1 (corpus trigger, no reuse) | ASan verdict |
|---|---|---|
| faithful shim, no sanitizer | **silent**, fold identical to R1h | — |
| faithful shim **+ ASan** | **silent on S1**; the reuse scenarios give `SEGV on unknown address`, `READ`, at the callee's payload read | ⚠ **not** `heap-use-after-free` |
| plain `malloc`/`free` + ASan | **faults on S1 too** | ✅ **`heap-use-after-free`, `WRITE of size 4`, frame #0 = SITE C** |

⚠⚠ **So the corpus's recorded `asan_kind: heap-use-after-free` is reproducible
on plain `malloc`/`free` and NOT reproducible on the faithful cached allocator.**
For ASan to report *use-after-free* the block must have reached `free()`, and a
39-byte `zend_llist_element` never does — `cache_index 5 < MAX_CACHED_MEMORY
11`, on both 32- and 64-bit builds. **The corpus's ASan confirmation therefore
came from a build whose allocator is not the pristine cached one**;
`SOURCES.md` §3 enumerates three such trees on this box (two
`ZEND_DISABLE_MEMORY_CACHE 0→1`, one `-poison-asan`). ⭐ **A build task must not
read its shim-based row's silence as a failure to reproduce.** §A2a/§A4 are
explicit: *"reproducing a DIFFERENT signal is a finding to state, not a failure
to hide."* State it, and cite the plain-`malloc` control as the artefact that
the recorded category is real.

⭐ And note what the ASan frame says: the **first** faulting access is the
`WRITE of size 4` at site C. **The corpus's `c_file_line` is the first fault,
not a mis-citation** — §5.4.

### 6.5 R1h — exactly what to ship

`c/kernel_hardened.c` = the row's `c/kernel.c` **plus `562f886ecb14`'s hunk and
nothing else**: an `int ret`, three assignments in place of three `return`s, and

```c
if (ret && tick_fe1->calling) {
    /* PHP: php_error_docref(NULL TSRMLS_CC, E_WARNING,
     *      "Unable to delete tick function executed at the moment");
     * PROJECTED to <the row's refusal counter>.  ⚠ THIS PROJECTION REMOVES A
     * USERLAND RE-ENTRY -- see TASK_PHP_031_REPORT §4.3.  It is a divergence
     * whose `why` CANNOT end in "no semantics". */
    return 0;
}
return ret;
```

`spec.md`'s hashed block records: `fix_commit: "562f886ecb14"`, the author and
date, the tag window **php-5.2.1 → php-5.2.2**, the three in-commit artefacts
(#41037, the NEWS line, `bug41037.phpt`), that the patch applies to pristine
5.0.0 with `patch -p1` rc=0 and yields php-5.2.2's function byte-identically,
and ⚠ **that R1h is in a DIFFERENT FUNCTION from both the cited line and the
defect** — the fix prevents the free rather than making either dereference safe.

**Two things to put under `controls/`, not in `spec.md`:**

- ⭐ `controls/next_cache.py` (or `.c`) — the **counterfactual hardening**
  `zend_llist_apply_with_del:177` already uses in the same file: cache `next`
  before the callback. **It fixes site L and leaves site C standing.** Measuring
  the two hardenings side by side is this row's best result, and it is only
  available because L and C are one row (§5.1(3)). ⚠ **It is NOT R1h** — §C is
  the real upstream fix, full stop.
- `controls/bug41037.phpt` — upstream's own regression test, replayed the way
  `ph07`'s `controls/bug49354.py` replays `c2471b495009`'s.

### 6.6 Mechanical items a build task will otherwise trip on

- `ln -s ../../../common-php/emalloc_shim.h patterns-php/ph64-*/c/emalloc_shim.h`
  — **unconditional** (§B2), and this row *does* allocate so `uses_allocator:
  true` with a reason.
- `php_shim_reset()` at the top of every kernel call (§B1 rule 3) — the LIFO
  cache is the oracle's mechanism, so a cache that survives across driver
  iterations makes call *N* depend on call *N−1* and destroys the marginal-`Ir`
  subtraction.
- Only `c/`, `inputs/`, `controls/` (§B3a / `ROW_DIRS`). Nine cited spans across
  three tarball files → **flatten** (`c/zend__zend_llist.h`) or flat-symlink
  beside; do not create `<row>/extract/`.
- Six commands, in order, ~28 min (§E) — steps 4→6 are the `gate → report →
  gate` chain and the first gate **must** fail on tables.
- `idiom.why`'s mandatory 11,003-byte named-spelling tail (§E), and
  `contract_sha256` computed with `check.py::read_contract`'s regex, which keeps
  the newline before the closing fence.

---

## §7 ⚠ Where the task file is wrong

### 7.1 ⚠⚠⚠ §2(b)'s explanation is WRONG, and the pre-image screen has a 17-row false-exclusion class

The task file says:

> *"The file drifted so far between 5.0.0 and `562f886ecb14` that line 2135 is a
> different statement — the drift case (open item 49), **not** an exclusion."*

**The bottom line is right — inconclusive, not negative — and the mechanism is
wrong.** The screen output is reproduced exactly
(`logs/preimage_ph64.log`); here is why it says what it says:

```
$ grep -ac 'calling = 0' .temp/php31/patches/562f886ecb14.patch      -> 0
$ grep -an 'calling'     .temp/php31/patches/562f886ecb14.patch
  24: - Fixed bug #41026 (segfault when calling "self::method()" in shutdown functions).
  50:+	if (ret && tick_fe1->calling) {
      ^ two hits: one unrelated NEWS *context* line that happens to contain the
        English word, and the ADDED guard.  No `-` line and no context line
        anywhere in the patch mentions the field.
$ grep -a '^diff --git'  .temp/php31/patches/562f886ecb14.patch      -> NEWS, basic_functions.c, bug41037.phpt
$ grep -acn 'tick_fe->calling = 0;' tags/php-5.2.2--ext_standard_basic_functions.c -> 1  (UNTOUCHED)
```

⚠ **The cited statement is not in the patch at ANY line number, and it is not in
the patch because the commit patches a DIFFERENT FUNCTION.** Line numbers are
irrelevant — `preimage_screen.py`'s own docstring says *"It never looks at a LINE
NUMBER in the patch… Matching is TEXT-ONLY."* **There is no drift case here.**
The record's `same_function=False` is the screen reporting exactly this, and it
is **correct**.

⚠⚠ **And the deeper problem is with the screen, not with `ph64`.** Its stated
rule is *"if the cited 5.0.0 line is nowhere in the pre-image, the commit is NOT
the repair of that site"*, and it labels that outcome `NOT-THE-REPAIR`, which
the docstring calls **"a PROOF OF EXCLUSION, not a ranking."**

> ⭐⭐ **`562f886ecb14` IS the repair AND removes no line at either site, at any
> version, ever. `zend_llist.c:190` and `basic_functions.c:2135` are
> byte-identical from 5.0.0 to master. NO LINE-LEVEL PRE-IMAGE SCREEN CAN EVER
> FIND A FIX OF THIS SHAPE** — a fix that closes a use-after-free by making the
> **free** unreachable from a third site.

**Measured, corpus-wide** (`logs/preimage_all.{log,json}`, 170 records):

```
NOT-THE-REPAIR   43        of which  decisive=True   26     <- the sound exclusions
CANDIDATE       106                  decisive=False  17     <- ph64's class
INAPPLICABLE     18
```

⚠⚠ **17 of 43 exclusions (40 %) carry `decisive=False`** — the screen prints a
label its own docstring calls a proof over a record whose own soundness flag
says it has proved nothing. **And the 17 are uniform in mechanism: I read the
git hunk contexts for all 17 and every one has a same-file hunk in a DIFFERENT
function from the cited line** (`ph18 ph32 ph39×2 ph46 ph48 ph61 ph63×2 ph64
ph65 ph71 ph75 ph77×2 ph79 ph80`). That is the `INAPPLICABLE` mechanism the
docstring already describes — *"the patch has no pre-image hunk for the defect's
file at all (the `ph07` shape: the fix is in the caller, in another file). The
screen says NOTHING about such a commit"* — **one granularity down: same file,
different function.** §F6's *"ask about a FUNCTION, not about text"* firing on
the manager's own tool.

⚠ **I verified ONE of the 17.** So the claim is *existence*, not a rate of
wrongness: the class is 17 rows and it contains **at least one confirmed false
exclusion**. ⚠ Two others look suspicious on their face — `ph63 CRASH-002`'s
commit patches `php_array_walk`, which is the very caller `CATALOGUE.md`'s ph63
block names, and `ph80 CRASH-141`'s patches `zend_std_read_property`/
`zend_std_write_property` — **but I did not check them and nobody should act on
that sentence without doing so.**

⭐ **Recommendation, and the ingredients already exist.** `NOT-THE-REPAIR` with
`same_function == False and bracketed == False` should print under a **third
label** — `INAPPLICABLE-SAME-FILE` — because its mechanism is `INAPPLICABLE`'s
and only a file-granularity coincidence separates them. **The screen already
computes everything needed; only the label is wrong**, and the honest reading of
today's output is *"the screen's exclusions are the 26, not the 43."*
⚠⚠ `preimage_screen.py` is a validator under §H, so that change lands with its
must-fire negatives: **`ph64` must leave `NOT-THE-REPAIR`; `ph21 CRASH-107` must
stay in it** (it is the `decisive=True, same_function=True` case §H was written
around); and a genuinely `INAPPLICABLE` row must not move.

⚠ **What this does NOT do: it does not touch F64's headline.** *"The screen
excludes"* is still true of the 26. What changes is which 26.

### 7.2 ⚠ §2(e)'s chain is FIVE frames, not four

The chain in §2(e) starts at `basic_functions.c:2139
run_user_tick_functions`. **There is a frame above it and it matters**:

```
main/php_ticks.c:67-72   php_run_ticks
   -> zend_llist_apply_with_argument(&PG(tick_functions), php_tick_iterator, &count)
                                                       ^^^^ zend_llist.c:229-236
main/php_ticks.c:59-65   php_tick_iterator -> func(*(int*)arg) -> run_user_tick_functions
```

⭐ **The omitted frame is a SECOND non-`next`-caching `zend_llist_apply*` walk**
(`zend_llist.c:233`, `caches_next=no`), over a *different* list
(`PG(tick_functions)`, C function pointers, `persistent = 1`). It does not fault
on this trigger — nothing userland-reachable calls `php_remove_tick_function`
(grepped as a function; `register_tick_function:2825` is the only caller of
`php_add_tick_function` in `ext/standard`) — **so this is a clean negative, not
a second defect.** Worth having in `spec.md` because it is the obvious question
a reader asks.

⚠ Also, minor: the `zend_llist_apply` call is at **`:2143`**, not `:2139`;
`:2139` is `run_user_tick_functions`'s signature. §2(e)'s layout implies this
but a `provenance` span written from it would be wrong.

### 7.3 ⚠ Where §3.1's premise breaks — see §5.3

*"L is the standalone container (8 lines, no PHP machinery)"* is right about the
FILE and wrong about the ROW: the 8 lines cannot fault without a free, the free
needs the deleter and a comparator, and the comparator's predicate is site C's
flag. **Measured**: the faithful chain is ~140 lines, not 8. §6.3 of the task
file predicted exactly this and it was right.

### 7.4 ✅ What held, exactly as written

- **(a)** re-derived (`idspread31.py`, 3 controls, PASS): 102 catalogued rows,
  **31** with >1 corpus id, **30** whose ids name different commits; temporal
  **21 of 31 = 68 %**; `ph64` has **one** id (`CRASH-086`) and **one**
  `fix_commit` (`562f886ecb14`) and is **not** in the split list. So it does not
  owe open item 48. ⓘ Control 3 flagged `V5C-015/116/173` as absent from
  `index.csv`'s id columns — the documented F51 / open item 39 case, not new.
- **(c)** confirmed: the enclosing function of `basic_functions.c:2135` is
  `user_tick_function_call` (`:2102-2137`), the callee. F1 landing where F1
  predicted — with §5.4's refinement that it is also the *first* fault.
- **(d)** confirmed **byte-exactly**: `Zend/zend_llist.c` is **317 lines**
  (`wc -l`), manifest sha `fd73a78aa1666a61…`, and
  `sed -n '186,193p' | sha256sum` = **`fce26e38389ba9fb7909f94c7fcfaed8a48f7960ba92c6d132812a958c40e917`**.
- **(b)**'s bottom line — *inconclusive, not negative* — confirmed. Only its
  mechanism is wrong (§7.1).
- **§6.2** — `ph64` needed no hunt-substitute and **`ph73` is not needed**.
  `ph64`'s R1h is settled with better artefacts than any of `ph73`'s five, and
  it is the cheaper row. **The manager's call stands.**

---

## §8 What I did NOT do, and what I am unsure of

1. ⚠⚠ **I did not measure §4.3**, the one incompleteness candidate. It is a
   static reachability argument over C I read line by line — `php_error_docref`
   → `php_verror` → `php_error` → `zend_error`'s user-handler arm, verified at
   5.0.0 **and** at php-5.2.2 — but I did not build PHP, did not run the script
   in §4.3, and did not check whether `zend_error`'s
   `EG(user_error_handler) = NULL` window or `EG(error_handling) == EH_THROW`
   blocks the specific nesting. **Conclusion landed, mechanism OPEN**
   (`PROTOCOL.md` rule 9).
2. ⚠ **I did not verify 16 of the 17 non-decisive `NOT-THE-REPAIR` records.**
   The uniform *mechanism* (same file, different function) is measured for all
   17; whether each commit is or is not the repair is checked for `ph64` only.
   §7.1's recommendation stands on the label being unsound, not on a wrongness
   rate.
3. ⚠ **I did not resolve which sha landed on any release branch.** The tag
   evidence shows the guard arrived between php-5.2.1 and php-5.2.2 and the
   window's only change to that function is this commit's hunk. That is a
   derivation, not a proof of commit identity; `spec.md` should say *"this
   commit's repair, witnessed at php-5.2.2"*.
4. ⚠ **I ran no PHP reproducer.** `CRASH-086.php` and
   `history/ext/stdext-finds/GIT-562f886ecb14.php` are read and quoted; neither
   was executed. ⓘ Both files' header comments describe **site L**
   (*"the apply loop dereferences element->next on the freed node"*) while the
   CSV's `c_file_line` names **site C** — the corpus's own two artefacts point
   at the two different primitives, which is worth knowing and is **not** a
   citation (`.memory-php/00-corpus.md`: a reproducer comment is never
   authoritative).
5. ⚠ **`crashes_pristine_5_0_0 = False` is not evidence of absence** (§B1 rule
   1) and I did not treat it as such. §6.4 explains it mechanically instead. But
   I did not resolve **which** ASan build the corpus's `heap-use-after-free`
   came from — only that it cannot have been a pristine cached allocator.
6. ⚠ **I did not run either staleness bracket**, per the task file's explicit
   instruction (`TASK_PHP_028` is mid-re-gate). A hunt changes no measured
   artefact. `git status --porcelain` at the end of the task:

   ```
   $ git status --porcelain
    M patterns-php/ph16-fdset-index/NOTES.md               <- TASK_PHP_028's
    M patterns-php/ph16-fdset-index/README.md              <- TASK_PHP_028's
    M results-php/gate/ph16-fdset-index.json               <- TASK_PHP_028's
    M results-php/preflight/ph16-fdset-index.preflight.json <- TASK_PHP_028's
   ?? .tasks-php/TASK_PHP_028_REPORT.md                    <- TASK_PHP_028's
   ?? .tasks-php/TASK_PHP_031_REPORT.md                    <- MINE, the only one
   ?? patterns-php/ph16-fdset-index/controls/spellings.json <- TASK_PHP_028's
   ?? patterns-php/ph16-fdset-index/controls/spellings.py   <- TASK_PHP_028's
   ?? results-php/preflight/ph07.preflight.json             <- not mine; I ran no gate.py
   ?? results-php/preflight/ph29.preflight.json             <- not mine; I ran no gate.py
   ```
   ⓘ `.temp/` is gitignored, so `.temp/php31/` does not appear. **Exactly one
   line is mine.**
7. ⚠ **Touched nothing** under `patterns-php/`, `RECAP_PHP.md`, `.memory-php/`,
   `.web/`, `harness/`, `common/`, `patterns/`, `results/`, `pilot/`,
   `results-php/`, `CATALOGUE.md`. No `git add`, no `git commit`. I did **not**
   read `patterns-php/ph16*`, `ph29*` or `ph03*` for anything quoted here;
   conventions come from `ph07-strcut-cursor/spec.md` and
   `harness-php/provenance.py`'s docstring. **I ran no `gate.py`**, so
   `results-php/preflight/` is untouched by me.
8. ⚠ **Two probe bugs of my own, both caught by declared expectations, both kept
   as artefacts** — `logs/oracle_probe-v1-WRONG.log` (the probe measured a
   *different scenario* from the one it declared: `userland()` was shared by
   every entry, so "entry 2 unregisters itself" ran as "entry 1 unregisters
   entry 2") and `logs/oracle_probe-v2-S2MISS.log` (my S2 expectation was
   *"clobbered, no crash"*; R1 SIGSEGVs). ⭐ **Both are §5.4's shape in my own
   probe, and neither would have been visible from the output alone.** The
   expectations, and only the expectations, are what caught them.
9. ⚠ **The probe's `visit_cap` is a probe-only bound.** PHP has none; a diverged
   walk in PHP is unbounded. Reported as `runaway` and never as a verdict.
10. ⚠ `clang` is not on `PATH` in this sandbox; `sweep.sh` uses
    `harness/build.py:53`'s `~/tools/llvm/bin/clang`. All four cells PASS. I did
    **not** run the probe under `-Ofast`/`-march=native` (no floating point
    here, so `ph03`'s reason to does not apply).

---

## §9 Evidence index — everything under `.temp/php31/`

| path | what |
|---|---|
| `NOTES.md` | how to regenerate every byte; what was deleted and why |
| `fetch.sh` | the commit patch + 21 tag snapshots × 2 paths (`*.ABSENT` = 404) |
| `spans.sh` + `logs/spans.log` | **every span's canonical `extract_sha256`** — §6.1's table |
| `fnbody.py` | brace-matching function extractor, **12 controls incl. 4 must-NOT-fire**, `--selftest` PASS; case **M** is the comment-before-brace bug it reported ABSENCE on |
| `walkcensus.py` + `logs/walkcensus.log` | the `caches_next` census over `zend_llist.c`'s six callback walks — §2's C-side "why" |
| `oracle_probe.c` + `run.sh` + `logs/oracle_probe.log` | **the oracle**: 8 scenarios × 2 rungs, forked, 3 must-NOT-fire, PASS |
| `logs/oracle_probe-v1-WRONG.log`, `-v2-S2MISS.log` | the two times the probe was wrong, kept on purpose |
| `sweep.sh` + `logs/sweep.log` | the same probe over gcc/clang × -O0/-O3, 4 × PASS |
| `logs/asan-shim.log`, `logs/asan-plain.log` | §6.4's fidelity table — `SEGV` under the faithful shim, `heap-use-after-free` (`WRITE`, frame #0 = site C) under plain `malloc`/`free` |
| `idspread31.py` + `logs/idspread31.log` | §2(a) re-derived, 3 controls, PASS |
| `logs/preimage_ph64.log`, `preimage_all.{log,json}` | §7.1's 43/26/17 split |
| `patches/562f886ecb14.patch` | the commit, 86 lines |
| `applytest/bf.patch` + `applytest/a/…` | the backport: `patch -p1` rc=0, result == php-5.2.2's function |
| `tags/` | `php-5.0.0 .1 .2 .3 .4 .5, 5.1.0, 5.1.6, 5.2.0-.5, 5.2.17, 5.3.0, 5.4.0, 5.6.0, 7.0.0, 8.3.0, master` × `Zend/zend_llist.c`, `ext/standard/basic_functions.c` (+ 5.2.2's `Zend/zend.c`, `main/main.c`) |
| `src/` | the six 5.0.0 tarball files, `SOURCES.md` §2 recipe |
| `logs/cmp_5.0.0.txt`, `cmp_5.2.1.txt`, `cmp_5.2.2.txt` | the three `user_tick_function_compare` bodies §3's diffs are taken between |
| `logs/llist_apply_500.txt` | the 8 lines, and the `fce26e38…` that hashes them |

⚠ Per `CLAUDE.md` rule 1 every binary is deleted (`*.bin`, `__pycache__/`) and
the whole `full/` tarball extraction with it; `fetch.sh`, `spans.sh`, `run.sh`,
`sweep.sh` and the four `.py` files re-derive all of it. Nothing left here needs
deleting.
