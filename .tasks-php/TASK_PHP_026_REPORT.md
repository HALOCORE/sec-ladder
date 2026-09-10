# TASK_PHP_026_REPORT — is a fix commit a CENSUS of its defect's siblings?

**Role:** research miner. **Read-only on the tree.** No `git add`/`commit`, no
edits under `harness/ common/ patterns/ results/ pilot/ .web/`, nothing written
to `RECAP_PHP.md`, `.memory-php/` or `patterns-php/CATALOGUE.md`.
Scratch: `.temp/php26/`.

---

## §0 ⚠⚠ TWO DISCLOSURES, BOTH ADVERSE, BOTH BEFORE ANYTHING ELSE

### D1 — I READ §4 BEFORE WRITING MY TRIAGE. The control is compromised.

The task file says, in capitals, **"DO NOT READ §4 UNTIL YOURS IS WRITTEN."**
My launch prompt said to read `TASK_PHP_026.md` **in full** and follow it
exactly. I read it in full, in one `Read` call, top to bottom — so I had already
seen the manager's prediction (**"4 SWEEP, 6 REWRITE, 2 UNCLEAR … 5–15 sibling
sites … fewer than half survive as anything but `EXACT`"**) before writing a
word of my own.

⚠ **Treat §1's triage as ANCHORED.** The task file itself prices this: *"a
disclosed anchor is worth something, an undisclosed one makes the whole triage
unusable."* This is the disclosed kind. It is still worth less than a blind one.

⚠ **The instruction and the launch prompt conflict, and that is a process bug,
not an agent error.** A task whose §2 says *"do not read §4"* cannot be launched
with *"read it in full."* **If this control is to be run again, §4 must live in a
separate file the agent is told to open later** — the ordering cannot be enforced
inside one file that the bootstrap tells the agent to read whole.

### D2 — my message extractor leaked the DIFFSTAT.

`.temp/php26/msgonly.py` splits each cached patch at the first `diff --git`.
`git format-patch` puts the **diffstat** (file names + per-file line counts)
*before* that marker, so my "message only" view included, for every commit, the
list of files touched and how many lines moved in each.

That is strictly more than the message. It is **materially informative** for this
exact triage — a `zend_vm_execute.h  | 3799 ++++---` line reads as "generated VM
re-emission" without any hunk being seen.

**Repair, since I cannot unsee it:** every row in §1 is tagged with the signal I
actually used — `[MSG]` = subject/body text alone would have produced this
verdict, `[MSG+STAT]` = the diffstat contributed. **Four of twelve are
`[MSG+STAT]`.** ⚠ A future run of this control should split on the `---\n` that
precedes the diffstat, or fetch `.../commit/<sha>` message via the API instead.

---

## §1 THE TRIAGE — from the commit message, WRITTEN BEFORE ANY HUNK WAS READ

⚠ This section was written into this file **before** opening a single patch
body. Everything below §1 was written after. The rule I applied, stated in
advance so it can be attacked:

> **SWEEP** — the message describes *one* defect or defect-class and implies it
> is being repaired at *more than one place* (plural "bugs", an enumerated list
> of subjects, "all", "everywhere", or the introduction of a **wrapper/macro**
> whose whole purpose is to be applied at N call sites).
> **REWRITE** — the message describes *replacing or restructuring* a subsystem
> (reimplemented, removed support, swapped implementation, unified, optimised by
> changing the design). The defect's repair is incidental to a larger edit.
> **UNCLEAR** — a terse single-bug subject with no structural signal either way.

| # | row | files | my call | signal | the words I keyed on |
|---|---|---:|---|---|---|
| 1 | `ph48` | 17 | **REWRITE** | `[MSG]` | *"Fixed is_callable/call_user_func **mess** that had done **different things** for very similar arguments"* — unification of divergent behaviour, i.e. a redesign |
| 2 | `ph24` | 16 | **REWRITE** | `[MSG]` | *"**Reimplemented** date and gmdate with new timelib code. **Removed old** … implementations."* |
| 3 | `ph16` | 10 | **SWEEP** | `[MSG]` | *"possibly unsafe select(2) usage. We avoid the problem by using poll(2)"* + *"a couple of handy **wrapper functions** have been added to make this easier"* — a wrapper exists to be applied at N sites |
| 4 | `ph26` | 9 | **REWRITE** | `[MSG]` | *"**use BSD licensed implementation** of double-to-string utilities **instead of** LGPL one"* — wholesale replacement, licence-driven |
| 5 | `ph23` | 8 | **UNCLEAR** | `[MSG]` | *"is_numeric_string() **optimization**"* — five words. An optimisation that changes a helper and updates its call sites is sweep-*shaped* but is not a *defect* sweep; the message cannot tell me which |
| 6 | `ph83` | 8 | **REWRITE** | `[MSG+STAT]` | *"**Improved** ternary operator **performance** when returning arrays"* — performance redesign. ⚠ the `zend_vm_opcodes.h +2` / `zend_vm_execute.h +315` stat confirmed "new opcode + VM regeneration" for me |
| 7 | `ph39` | 5 | **SWEEP** | `[MSG]` | *"Just **convert everything** to the appropriate data type, like `Exception::__toString()` does"* — "everything" over the several overridable properties is the same repair at N places |
| 8 | `ph54` | 5 | **REWRITE** | `[MSG]` | *"foreach(…) **optimization**. **Removed** temorary array creation on each iteration."* — design change |
| 9 | `ph65` | 5 | **UNCLEAR** | `[MSG+STAT]` | *"fix bug #65481 (shutdown segfault due to serialize)"* — terse, one bug. ⚠ the stat showed `var_unserializer.c` + `.re` are a **generated/source pair** and two more files are NEWS + test, so "5 files" is really ~2 |
| 10 | `ph73` | 5 | **SWEEP** | `[MSG]` | *"Fixed memory allocation **bugs** (plural) related to magic object handlers (`__get()`, `__set()`, **…**)"* — plural defect + an explicitly elided list of subjects. This is the strongest sweep signal after `ph16` |
| 11 | `ph76` | 5 | **UNCLEAR** | `[MSG+STAT]` | *"Fixed bug #31158 (array_splice on \$GLOBALS crashes)"* — one bug, one name. ⚠ stat showed NEWS + test + a 2-line header, so "5 files" is really ~2.5 |
| 12 | `ph84` | 5 | **REWRITE** | `[MSG+STAT]` | *"**Removed support for** break/continue \$var syntax"* — a feature removal, not a defect repair at all. ⚠ stat's `zend_vm_execute.h −146` confirmed regeneration |

**My totals: 3 SWEEP · 6 REWRITE · 3 UNCLEAR.**
(The manager's, which I had already seen: 4 · 6 · 2.)

sha256 of this section as first written, before any patch body was opened:
recorded at `.temp/php26/triage.sha256`.

---

## §2 THE ANSWER, IN ONE TABLE

All 12 patches were already in `fixsurvey.py`'s cache
(`.temp/mgr/batch/patches/`, 89 patches, **zero network fetches needed**).
Every `file:line` below was resolved against the **pristine tarball**
(sha256 re-verified at survey time: `5783e0c0…d6919`, 5 595 997 B) extracted to
`.temp/php26/php-5.0.0/`, **not** against the commit's own pre-image — which for
these commits is a 2005–2013 tree, not 5.0.0.

| row | files | my triage | **uncatalogued sibling sites, in 5.0.0** | triage verdict |
|---|---:|---|---:|---|
| `ph16` | 10 | SWEEP | **3** | ✅ |
| `ph39` | 5 | SWEEP | **1** | ✅ |
| `ph73` | 5 | SWEEP | **3** (+1 already in the row) | ✅ |
| `ph23` | 8 | UNCLEAR | **2** | ⚠ was a sweep |
| `ph76` | 5 | UNCLEAR | **2** | ⚠ was a sweep |
| `ph65` | 5 | UNCLEAR | 0 | — |
| `ph26` | 9 | REWRITE | **1** | ❌ **wrong** |
| `ph48` | 17 | REWRITE | 0 | ✅ |
| `ph24` | 16 | REWRITE | 0 | ✅ |
| `ph83` | 8 | REWRITE | 0 | ✅ |
| `ph54` | 5 | REWRITE | 0 | ✅ |
| `ph84` | 5 | REWRITE | 0 | ✅ |

> ### **12 uncatalogued sibling sites, from 6 of the 12 commits.**
> **The channel is real and it is not a one-instance channel.**
> The manager's *"5–15 sibling sites"* band is **hit: 12.**

### 2.1 ⚠⚠ The triage is a good POSITIVE predictor and a BAD NEGATIVE one — so it is not safe as a filter

| | |
|---|---|
| SWEEP → yielded | **3 / 3 (100 %)** — **not one false positive** |
| REWRITE → yielded nothing | **5 / 6 (83 %)** — `ph26` broke it |
| UNCLEAR → yielded | **2 / 3** |
| **false negatives** (called REWRITE/UNCLEAR, was a sweep) | ⚠ **3 of 12** |

**Answer to §2.3: the message predicts the patch in one direction only.** If it
says SWEEP, it is a sweep. If it says anything else, it is a coin flip — and the
three misses account for **5 of the 12 sibling sites (42 %)**. ⚠ **Triaging by
message and then skipping the non-SWEEPs would have lost nearly half the yield.**

**Answer to §5.2 — you asked whether the triage is ceremony. Partly yes, and I
would drop it as a FILTER but keep it as a CONTROL.** Reading the patch is
cheap: the cache made it free, and the discriminating grep is one line per row
(*"which lines does this patch add that match the row's own repair?"*). The
triage bought exactly one thing, and it was worth having: **a measured
false-negative rate.** Without it the temptation to prune the ≥5-file list by
message would have looked safe. It is not.

### 2.2 ⚠⚠⚠ AND THE SELECTOR THAT PRODUCED THIS LIST OF 12 CARRIES ZERO SIGNAL

`FIXSURVEY_001.md:64`'s heading selects on **≥ 5 files touched**. Measured over
the 12:

```
files >= 8 : n=6  siblings=6  per-row=1.00
files == 5 : n=6  siblings=6  per-row=1.00
the two BIGGEST commits (17f, 16f) yielded 0
TOTAL uncatalogued sibling sites = 12
```

**Identical density.** ⚠ **The two largest commits in the corpus yielded
nothing at all**, and three 5-file commits yielded six sites between them. The
file count is what made `ph16` *look* like a cost; it is **not** what makes a
commit a census. **What actually predicts a census is a repair expressed as a
NAMED WRAPPER** — `PHP_SAFE_FD_SET` (`ph16`), `MAKE_REAL_ZVAL_PTR` (`ph73`),
`zend_reset_all_cv` (`ph76`) — because a wrapper exists in order to be applied
N times. All three highest-yield rows introduced one. ⭐ **That is a better
selector than the file count and it is greppable: `^\+.*#define [A-Z_]+\(` or a
new `ZEND_API`/`PHPAPI` function in the same commit as the row's own hunk.**

---

## §3 THE 12 SITES, WITH THE C AND THE PRIMITIVE NAMED

⚠⚠⚠ **I DO NOT ADJUDICATE ANY OF THESE.** Per `PROTOCOL_PHP.md` §G1: a
**shared** upstream fix is **not** evidence for SAME. Every entry below is a
*candidate with evidence*; the SAME/DIFFERENT question is a separate burden on
separate evidence, and nothing here discharges it.

### 3.1 `ph16` — `99e290f882c9` · 3 sites · ✅ the manager's n = 1, independently re-derived

Repair signature: `FD_SET(fd,set)` → `PHP_SAFE_FD_SET(fd,set)`, whose POSIX
branch is `do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)`.
**Exactly 4 call sites take the macro**, and all four resolve byte-exact:

```
ext/standard/streamsfuncs.c:541: 			FD_SET(this_fd, fds);                   <- ph16 itself
ext/standard/streamsfuncs.c:577: 			if (FD_ISSET(this_fd, fds)) {
ext/sockets/sockets.c:536: 		FD_SET(php_sock->bsd_socket, fds);
ext/sockets/sockets.c:563: 		if (FD_ISSET(php_sock->bsd_socket, fds)) {
```

| site | primitive | catalogued? |
|---|---|---|
| `ext/standard/streamsfuncs.c:577` | OOB **read** of an on-stack `fd_set` | ❌ |
| `ext/sockets/sockets.c:536` | OOB **write** | ❌ |
| `ext/sockets/sockets.c:563` | OOB **read** | ❌ |

✅ **`.temp/mgr166/NOTES.md` §2 is confirmed in full, including the line
numbers.** Nothing in it needed correcting.

#### ⭐ But the note is INCOMPLETE, and the omission is the interesting half

`99e290f882c9` contains **two different repairs for one defect class**, and the
note records only the first:

- **Repair A — guard the index.** The `PHP_SAFE_FD_*` macro, 4 sites (above).
- **Repair B — delete the `fd_set`.** `php_pollfd_for(...)` / `poll(2)`
  replaces `select(2)` outright. Measured: the commit removes **24** bare
  `FD_SET`/`FD_ISSET` calls; 4 become the macro, and the other **20** are
  deleted along with their `fd_set` objects. Sample hunk (`main/streams/xp_socket.c`):

  ```diff
  -			fd_set fdw, tfdw;
  -			FD_ZERO(&fdw);
  -			FD_SET(sock->socket, &fdw);
  -			retval = select(sock->socket + 1, NULL, &tfdw, NULL, ptimeout);
  +			retval = php_pollfd_for(sock->socket, POLLOUT, ptimeout);
  ```

  **19 of those resolve into pristine 5.0.0**, in five files the commit touches:
  `ext/ftp/ftp.c:1249,1299,1339,1366,1393` · `ext/openssl/xp_ssl.c:264,525,527` ·
  `ext/soap/php_http.c:46,49` · `main/network.c:330,331,339,698,706` ·
  `main/streams/xp_socket.c:87,165,247,249`.

⚠ **I am deliberately NOT counting these 19 in the headline 12.** They share
`ph16`'s **unchecked predicate** (`fd < FD_SETSIZE`) and its **fault primitive**,
but the **attacker-controlled quantity differs**: `ph16`'s index arrives in a
userland array, whereas these are single descriptors the process itself opened,
reachable only under fd exhaustion. That is §G limb (b), it is exactly the limb
the checklist gives no level of abstraction for, **and it is the manager's call,
not mine.** I record them so the decision is made on the evidence rather than on
whether anyone happened to notice them.

### 3.2 `ph26` — `4d44a5b71dd7` · 1 site · ⭐⭐ THE SHARPEST FIND, AND IT REFUTES MY OWN TRIAGE

`main/snprintf.c` carries a **near-verbatim clone** of `ph26`'s defective
function, and the same commit deletes both. Compare, from the tarball:

```c
/* ph26's own site — ext/standard/formatted_print.c:65,73,95-96 */
static char *php_convert_to_decimal(double arg, int ndigits, int *decpt, int *sign, int eflag)
	static char cvt_buf[NDIG];                                  /* :73  BSS   */
			mvl = NDIG - ndigits;                                   /* :95        */
			memmove(&cvt_buf[mvl], &cvt_buf[0], NDIG-mvl-1);        /* :96        */

/* THE SIBLING — main/snprintf.c:296,323-324 */
char * ap_php_cvt(double arg, int ndigits, int *decpt, int *sign, int eflag, char *buf)
			mvl = NDIG - ndigits;                                   /* :323       */
			memmove(&buf[mvl], &buf[0], NDIG-mvl-1);                /* :324       */
```

Both files `#define NDIG 80` independently (`formatted_print.c:37`,
`snprintf.c:161`). The clamp is upper-only in both, so `mvl` goes negative and
`memmove` writes **before** the object and reads past it.
**Primitive: OOB write + OOB read.** **Catalogued: ❌** — `grep -a -o
'snprintf\.c:[0-9-]*' patterns-php/CATALOGUE.md` returns **nothing**; the
catalogue has no `main/snprintf.c` row of any kind.

⭐ **The variation is the storage class, and it matters for this project
specifically.** `ph26`'s buffer is `static` (BSS) — its own `⚠ risk` line says
*"no allocator at all — static BSS. A row built with an `emalloc` fixture
measures nothing."* The sibling's buffer is `char buf1[NDIG]` **on the caller's
stack** (`snprintf.c:177`, `:408`). **Same arithmetic, different memory region,
different oracle** — and a stack version is exactly what `ph16` needed a canary
for.

⚠⚠ **This is the entry that kills the cheap triage.** `ph26`'s message is
*"use BSD licensed implementation … instead of LGPL one"* — an unambiguous
wholesale-replacement message, which I called REWRITE and the manager's own
prediction would also have called REWRITE. **The rewrite was a deletion sweep:
it removed every copy of a duplicated function at once.** *"A REWRITE yields
nothing"* is false, and it is false for a structural reason — **a rewrite that
replaces a subsystem necessarily visits every clone of it.**

### 3.3 `ph73` — `3d7b0bab28e7` · 3 new sites (+1 re-derived) · a wrapper sweep

The commit introduces **`MAKE_REAL_ZVAL_PTR`** (`Zend/zend_execute.c`) — heap-
allocate before publishing — and applies it at **160 call sites**. The row's
mechanism is *"automatic storage published where user code can retain it"*.

⚠⚠ **157 of those 160 DO NOT EXIST IN 5.0.0.** They are in `Zend/zend_vm_def.h`
(11) and `Zend/zend_vm_execute.h` (146), and **5.0.0 has neither file** — the VM
specialiser arrived in 5.1. Verified: `zend_vm_def.h`, `zend_vm_execute.h`,
`zend_vm_gen.php`, `zend_vm_opcodes.h` are all **ABSENT** from the tarball.
**Only the 3 in `zend_execute.c` are resolvable**, plus the two hand-edited
`zend_object_handlers.c` functions.

| # | 5.0.0 site | the C | published to | catalogued? |
|---|---|---|---|---|
| 1 | `Zend/zend_object_handlers.c:267` (`zend_std_read_property`) | `zval tmp_member; … member = &tmp_member;` | `zend_std_call_getter` → `call_args[0] = &member` → userland **`__get($name)`** | ⚠ **function yes, defect no** — `ph78` cites `:264-296` for a *different* mechanism (a latched raw pointer) |
| 2 | `Zend/zend_object_handlers.c:318` (`zend_std_write_property`) | identical idiom | `zend_std_call_setter` → userland **`__set`** | ❌ |
| 3 | `Zend/zend_execute.c:419` (`zend_assign_to_object`, `ZEND_ASSIGN_OBJ`) | `zval tmp; … property_name = &tmp;` then `Z_OBJ_HT_P(object)->write_property(object, property_name, value)` | userland **`__set`** | ❌ |
| 4 | `Zend/zend_execute.c:1138` | `zval tmp` → `__get` | — | ✅ **already in `ph73`'s member list** |

✅ **#4 is the channel validating itself**: the census independently re-derives a
sibling the catalogue found by hand. **Primitive on all four: dangling pointer
into a dead stack frame (CWE-562), i.e. `ph73`'s.**

#### ⚠⚠ AND `ph73`'s OWN CITED SITE IS NOT TOUCHED BY ITS OWN `fix_commit`

`grep -a -c 'call_user_call' 3d7b0bab28e7.patch` → **0**. The commit never
mentions `zend_std_call_user_call`, which is `ph73`'s cited defect site
(`:520-592`). FIXSURVEY's `same`-file verdict is correct and, exactly as
`FIXSURVEY_001.md:13-18` warns, **not a licence**. This is `.memory-php/02-ladder.md`'s
*"the column names **a** fix for the row's function, not necessarily the one that
removes the 5.0.0 defect"* firing on a row nobody had checked. **`ph73` needs an
R1h hunt of its own before it is built.**

### 3.4 `ph76` — `1d33a3e95e4e` · 2 sites · a wrapper sweep behind a one-bug subject

Repair signature: `efree(Z_ARRVAL_P(x)); Z_ARRVAL_P(x) = new_hash;` →
`if (Z_ARRVAL_P(x) == &EG(symbol_table)) zend_reset_all_cv(…); *Z_ARRVAL_P(x) = *new_hash; FREE_HASHTABLE(new_hash);`
Applied at **three** `PHP_FUNCTION`s; the row is one of them.

```c
/* ph76 itself — ext/standard/array.c:2059-2061, PHP_FUNCTION(array_splice) */
	zend_hash_destroy(Z_ARRVAL_P(array));
	efree(Z_ARRVAL_P(array));
	Z_ARRVAL_P(array) = new_hash;

/* SIBLING 1 — ext/standard/array.c:1983-1984, PHP_FUNCTION(array_unshift) */
	zend_hash_destroy(Z_ARRVAL_P(stack));
	efree(Z_ARRVAL_P(stack));
	Z_ARRVAL_P(stack) = new_hash;

/* SIBLING 2 — ext/standard/array.c:2557-2558, PHP_FUNCTION(array_pad) */
	zend_hash_destroy(Z_ARRVAL_P(return_value));
	efree(Z_ARRVAL_P(return_value));
	Z_ARRVAL_P(return_value) = new_hash;
```

**Primitive on all three: `efree` of `&EG(symbol_table)`** — a `HashTable`
embedded in the executor-globals struct, never an allocator return.
**Catalogued: ❌ both** (catalogue has `array.c:2058-2061`, `:3272-3274`,
`:1884-1894`, `:2688-2695` … and neither `:1983` nor `:2557`).

⚠⚠ **`array_pad` looked like a false positive and I checked instead of
assuming.** Its `return_value` is built by `*return_value = **input;
zval_copy_ctor(return_value);` (`array.c:2529-2530`), which reads like a real
copy. It is not — **measured at source**, `Zend/zend_variables.c:146-148`:

```c
		case IS_ARRAY:
				if (zvalue->value.ht == &EG(symbol_table)) {
					return SUCCESS; /* do nothing */
				}
```

So `array_pad($GLOBALS, …)` leaves `Z_ARRVAL_P(return_value) == &EG(symbol_table)`
and `:2557` `efree`s it. ⭐ **This is `ph76`'s own `⚠ risk` note — *"`array.c:3272-3274`'s
`zval_copy_ctor` no-ops for it so the 'copy' aliases it"* — turning up
independently at a fourth site.**

### 3.5 `ph23` — `ff9d0fcc783c` · 2 sites · the sweep hiding inside an "optimization"

`ph23`'s own repair is a **one-character constant bump** buried in an 8-file
performance commit — `PROTOCOL_PHP.md` §G1's *"one commit routinely repairs
unrelated errors"*, verbatim:

```diff
-		s_tmp = emalloc(Z_STRLEN_PP(file) + MAX_LENGTH_OF_LONG + 2 + 1);
+		s_tmp = emalloc(Z_STRLEN_PP(file) + MAX_LENGTH_OF_LONG + 4 + 1);
```

The same commit makes the **same class** of repair — *the `emalloc` budget is
short for the `sprintf` that follows* — at two more sites:

```c
/* SIBLING 1 — Zend/zend.c:209-210, zend_make_printable_zval, case IS_RESOURCE */
	expr_copy->value.str.val = (char *) emalloc(sizeof("Resource id #")-1 + MAX_LENGTH_OF_LONG);
	expr_copy->value.str.len = sprintf(expr_copy->value.str.val, "Resource id #%ld", expr->value.lval);

/* SIBLING 2 — Zend/zend_operators.c:532-533, _convert_to_string, case IS_RESOURCE */
	op->value.str.val = (char *) emalloc(sizeof("Resource id #")-1 + MAX_LENGTH_OF_LONG);
	op->value.str.len = sprintf(op->value.str.val, "Resource id #%ld", tmp);
```

**Primitive: 1-byte heap over-write (the NUL). Catalogued: ❌ both.**

⚠ **I measured the arithmetic rather than asserting it, and swept the constant
so the verdict could move** (`.temp/php26/ph23_budget.c`):

```
sizeof("Resource id #") = 14   MAX_LENGTH_OF_LONG = 20   (Zend/zend_operators.h:37)
budget 5.0.0 = 33   budget fixed = 34   sizeof(long) = 8

                 value     need    5.0.0    fixed
                     0       15       ok       ok
                 12345       19       ok       ok
            2147483647       24       ok       ok
   9223372036854775807       33       ok       ok
  -9223372036854775808       34 OVERFLOW       ok
```

⚠⚠ **The verdict flips only at `LONG_MIN`** — the minus sign is the 20th
character. The defect is real and the fix is exactly right, but **reachability
is not established**: PHP resource ids are small sequential positives, so I
found **no route** to a 20-character `%ld`. **I report this as evidence, not as
a kill** (`CLAUDE.md` rule 6). It is the one item in §3 whose admission I would
expect to fail on `PLAN_PHP.md` §3 criterion 2, and it should fail *there*, on
the C, after somebody tries — not here.

### 3.6 `ph39` — `d6505acbf5ff` · 1 site

Repair: coerce the untagged zval before reading it. Two hunks, one file, same
repair; the second is `ph39`'s own (`:551`), the first is the sibling.

```c
/* SIBLING — Zend/zend_exceptions.c:538-539 read, :544 consumed */
				file = zend_read_property(default_exception_ce, EG(exception), "file", …);
				line = zend_read_property(default_exception_ce, EG(exception), "line", …);
			}
			zend_error_va(E_WARNING, file ? Z_STRVAL_P(file) : NULL, line ? Z_LVAL_P(line) : 0, …);
```

`Z_STRVAL_P` expands to `.value.str.val` and **consults no tag**; `file ?` is a
**NULL-pointer** test, not a type test, so a `file` property set to a `long`
from userland is dereferenced as a `char *`. **Primitive: type-confused pointer
read.** **Catalogued: ❌** — the catalogue holds `zend_exceptions.c:293`,
`:310-311`, `:339`, `:519`, `:551`, and neither `:538` nor `:544`.

---

## §4 CLEAN NEGATIVES — named attacks that did NOT land

1. ⭐ **`ph48` (17 files, the largest fix in the corpus) yields ZERO.** The repair
   signature across the whole 17-file patch is **one line**:
   `awk '/^diff --git/{f=$3} /^[+-].*(is_ref|SEPARATE_ZVAL)/' ` →
   `Zend/zend_execute_API.c :: -			SEPARATE_ZVAL_IF_NOT_REF(tmp_object_ptr);`.
   A 261-line restructure of `zend_call_function` around a single deleted line.
2. ⭐ **`ph24` (16 files) yields ZERO, and cleanly.** `ext/standard/datetime.c`:
   **411 lines removed, 1 added.** Pure deletion, no repair to imitate.
3. **`ph84` yields ZERO.** One hunk in `zend_execute.c`, deleting the
   `zval tmp` conversion in `zend_brk_cont` outright because the syntax is gone.
4. **`ph54` and `ph83` yield ZERO, for a reason worth recording separately.**
   Neither fix touches the row's own file, and **3 of `ph83`'s 8 files and 2 of
   `ph54`'s 5 do not exist in 5.0.0** (`zend_vm_def.h`, `zend_vm_execute.h`,
   `zend_vm_opcodes.h`). FIXSURVEY's `OTHER-FILE` flag already predicted this.
5. **`ph65` yields ZERO, and its "5 files" is really ~2.** The repair
   (`zval_ptr_dtor(rval)` → `var_push_dtor_no_addref(…)`) appears twice, and I
   checked which two: patch line 461 is in `var_unserializer.c`, line 585 in
   `var_unserializer.re` — **the generated file and its source, one logical
   site.** Its other repair (`BG(serialize_lock) = 1` → `++`, 3 sites) has **no
   5.0.0 counterpart at all**: `grep -arn 'serialize_lock'` over the tarball
   returns **0**, against a control (`var_push` → 2) proving the grep works.
6. **`ph39`'s `zend_exceptions.c:530` is NOT a sibling.** It also does
   `Z_STRVAL_P(str)`, but `:527` guards it with an explicit
   `if (Z_TYPE_P(str) != IS_STRING)`. A real tag check — excluded.
7. ⚠ **Three of `ph73`'s five 5.0.0 `zval tmp_member` sites are NOT siblings**,
   and this is the negative I most expected to get wrong. `:441`
   (`zend_std_get_property_ptr_ptr`), `:485` (`zend_std_unset_property`) and
   `:858` (`zend_std_has_property`) use the **byte-identical four-line idiom** —
   `tmp_member = *member; zval_copy_ctor(&tmp_member); convert_to_string(&tmp_member); member = &tmp_member;`
   — but the address never leaves the engine: it reaches only
   `zend_get_property_info` and `zend_hash_*`. **No userland call, no retention,
   no defect.** `get_property_ptr_ptr` even returns `NULL` explicitly *because*
   a getter exists. ⭐ **The idiom is not the defect; the publication is** — and
   a grep for the idiom would have produced three false candidates.
8. **`ext/sockets/`'s zero rows are NOT a build artefact.** See §5.
9. **No new-row build, no catalogue edit, no `.memory-php/` write, no
   `git add`/`commit`, nothing under `harness/ common/ patterns/ results/
   pilot/ .web/`.** `git status` was read-only throughout.

---

## §5 §5.1 ANSWERED — `ext/sockets/` WAS BUILT. THE ZERO IS THE **CORPUS's**, NOT THE CENSUS's.

You asked me to check whether `ext/sockets/` was in the ASan census's built
configuration, because *"if it was not, that explains its zero rows completely
and innocently."* **It was. The innocent explanation is refuted.** Three
measurements, in increasing order of decisiveness:

1. **It is configured in.** `build-php-5.0.0-san.sh:124` →
   `--enable-sockets` (alongside `--enable-ftp --enable-exif --enable-mbstring`).
2. **It is built and loaded.** `ext/sockets/sockets.o` exists in the asan build
   tree, and the census binary's `php -m` lists **`sockets`** among 15 modules.
3. ⭐ **But the corpus never sampled it, and neither did the workload.**

   | | |
   |---|---:|
   | corpus `index.csv` rows citing `sockets.c` | **0** |
   | corpus rows citing `streamsfuncs.c` | **6** |
   | ASan logs (of **2 534**) naming `ext/sockets` | **0** |

> ✅ **So: a finding about the CORPUS's coverage.** The catalogue has zero
> `sockets.c` rows because the corpus has zero, and the corpus has zero because
> the 18 web apps it was mined from use streams and `fsockopen`, never the raw
> `sockets` extension. **Nothing is wrong with the catalogue, the census build,
> or the mining.** ⚠ **And that is precisely what makes the census channel worth
> having: it reaches a file no corpus row points at.** `ext/sockets/sockets.c`
> is in the pinned tarball, so it clears `SOURCES.md`; the C-side bar is
> unaffected.

## §5.3 ANSWERED — *"nobody looked"* for 10 of 12, and the two exceptions are the interesting ones

You asked me to distinguish *"nobody has looked at this"* from *"someone looked
and said no"*. Searched `.tasks-php/` including `TASK_PHP_001_MINE/`:

- **10 of the 12 sites: never mentioned anywhere.** `zend_exceptions.c:538/:544`,
  `zend_object_handlers.c:318`, `array.c:1983`, `array.c:2557`, `snprintf.c` /
  `ap_php_cvt`, `"Resource id #"` — **all zero hits.** Nothing was mined and
  killed; nobody looked.
- `sockets.c:536/:563` and `streamsfuncs.c:577` appear **only** in
  `TASK_PHP_025*` and `TASK_PHP_026.md` — i.e. downstream of
  `.temp/mgr166/NOTES.md`, not in the mining wave.
- ⭐ **Two sites are in functions the mining wave DID examine, for OTHER
  mechanisms** — the more interesting outcome, and it argues the channel is
  complementary rather than duplicative:
  - `zend_execute.c:419` — `TASK_PHP_001_MINE/temporal/candidates.json` reaches
    `zend_assign_to_object` at **`:380`**, the *double `PZVAL_UNLOCK`* in the
    non-object error arm (CRASH-151 → `ph77`). **Different defect, 39 lines up.**
  - `zend_object_handlers.c:267` — examined twice, for the **latched `zobj`
    pointer** (→ `ph78`) and for the **getter's unowned return zval**
    (`TASK_PHP_019_REPORT.md:540`). **Neither is the `zval tmp_member`
    publication.**

> ⚠ **So the honest headline is: the catalogue's unit is the MECHANISM, and a
> function can be catalogued three times over while a fourth defect in it has
> never been read.** ✅ **`ADJUDICATION_001.md` did not already cover this
> ground** — none of the 17 reversed kills is any of these sites.

---

## §6 §2.4's COST QUESTION — what a full sweep over all ~91 resolved fixes would cost

**I did not run it.** Priced from what these 12 actually took:

| | |
|---|---|
| network | ⭐ **zero** — 89 patches already cached; `--offline` covers all but `ph36` |
| per row | ~5 shell commands: locate the defect site in Part B → grep the patch for the row's repair signature → resolve each hit in the tarball → `grep -a` the catalogue → quote the C |
| this task | 12 rows, ~35 tool calls, one session |
| **91 rows** | **≈ 250–300 tool calls — one full agent task, two if the C is read carefully** |
| ⚠ **not prunable** | §2.2 measured the file-count selector at **zero signal**, and §2.1 measured the message triage's **false-negative rate at 3/12**. **Neither is safe as a filter, so the sweep is all-or-nothing.** |

⚠ **Two coverage gaps to budget for, neither of which is mine to close:**

1. **`FIXSURVEY_001.md` covers 91 rows; the catalogue is now 102.** Missing:
   `ph92 ph93 ph94 ph95 ph96 ph97 ph98 ph99 ph100 ph101 ph102` (landed by
   `_019`/`_020`/`_023`). A full sweep should re-run `fixsurvey.py` first.
2. **`ph36` has no sha** (`bison-regeneration`), so 90 are actually resolvable.

**My recommendation, and it is a recommendation and not a finding:** the yield
here was **1.0 sibling per commit across all twelve, evenly distributed**, and
6 of 12 commits paid. If that density holds, 90 fixes is on the order of **~50–90
candidate sites** — far too many to adjudicate as a side-effect of anything else.
⭐ **The cheap version is to sweep only for the WRAPPER signature first** (a
`#define`/`ZEND_API`/`PHPAPI` introduced in the same commit as the row's hunk),
which found all three of the highest-yield rows here and is one `grep` per patch.

---

## §7 WHAT I AM LEAST SURE OF

1. ⚠⚠⚠ **The §4 anchor (§0 D1).** My triage came out 3/6/3 against the
   manager's 4/6/2, and two of my three UNCLEARs turned out to be sweeps — so
   the numbers are close to a prediction I had already read. **I cannot certify
   that my SWEEP/REWRITE calls are independent of it.** What I would trust
   instead: the *rule* is stated in §1 before the table and each row names the
   words it keyed on, so a reader can re-run the classification themselves.
   **If this control matters, re-run it blind with a different agent and §4 in a
   separate file.**
2. ⚠⚠ **The diffstat leak (§0 D2)** — 4 of 12 rows are `[MSG+STAT]`. Note that
   **`ph26`, the row that refutes the triage, is `[MSG]`** — the leak did not
   manufacture the headline result, and if anything it made me *more* confident
   in wrong REWRITE calls.
3. ⚠ **"The same repair" has no more stated level of abstraction than §G's
   (a)(b)(c) do**, and I hit it head-on at `ph16`: repair A (the macro) gives 4
   sites, repair A+B (macro + poll conversion) gives 23. **I chose the narrow
   reading for the headline and reported the wide one separately.** A different
   reading gives a different count, and the count is not the finding.
4. ⚠ **`ph23`'s two siblings are of doubtful reachability** — I could not
   construct a 20-character resource id (§3.5). The C is short by one byte;
   whether an adversarial input exists is open, and `PLAN_PHP.md` §3 criterion 2
   demands a **detector firing**, which I did not attempt.
5. ⚠ **I did not check whether any of the 12 sites duplicates another
   `patterns-php/` row's mechanism**, deliberately — that is the §G burden and
   §3.1 of my task file forbids me to discharge it. **In particular I have not
   asked whether `sockets.c:536` is `EXACT` against `ph16`**, which
   `.temp/mgr166/NOTES.md` §"What I am NOT claiming" flags as the sharp case.
6. ⚠ **I resolved sibling sites by content match, not by mechanical patch
   application.** For commits whose pre-image is 2005–2013, `@@ -a,b @@` line
   numbers are meaningless against 5.0.0, so every line number above was found
   by grepping the tarball for the code. Each is quoted with its C so it can be
   re-checked; but a site whose *code changed between 5.0.0 and the fix* could
   in principle have been missed by my search string.
7. ⚠ **`ph73`'s R1h problem (§3.3) is a by-product, not something I was asked
   to find, and it is unreviewed.** I am confident in the measurement
   (`grep -a -c 'call_user_call'` → 0) and much less confident about what it
   implies for building the row.
8. ⚠ **I did not widen past the 12**, per §3.4. **But two of the biggest yields
   came from 5-file commits, and §2.2 shows the file count is not a selector —
   so the 2-, 3- and 4-file fixes are NOT a lower-yield tail, they are simply
   unexamined.** Do not read "the 12 are where the density is highest" as
   measured; it is not, and this task's own data mildly contradicts it.

---

## §8 REGENERATION

Everything is under `.temp/php26/`, blobs deleted per `CLAUDE.md` constraint 1:

```sh
sh .temp/php26/REFETCH.sh      # tarball pin check -> extract -> patches -> both probes
```

Kept (evidence): `REFETCH.sh`, `msgonly.py` (message extractor — ⚠ **splits at
`diff --git` and therefore LEAKS THE DIFFSTAT; split at the preceding `---` if
you re-run the blind control**), `resolve.py` (snippet → 5.0.0 `file:line`),
`ph23_budget.c` (the budget probe), `triage.sha256`.
Deleted (re-derivable): `php-5.0.0/` (37 MB, from the pinned tarball),
`ph23_budget` (binary).

**Triage pin:** `c87093df6368134a94b23092dd0fa57daf9d550ec6f84ee9c2e2be31c13a36df`
— sha256 of this file at the moment §1 was complete and **before any patch body
was opened**, `2026-09-10T02:47:05+00:00`. Reconstructible: truncate this file
at the `---` closing §1.
