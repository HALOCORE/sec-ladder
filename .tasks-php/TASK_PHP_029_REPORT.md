# TASK_PHP_029_REPORT — the R1h hunt for `ph73` and `ph21`

**Role: research investigator. One agent, alone. Nothing was built.** No pattern
directory, no rung, no gate, no measurement, no C was written. Scratch is
`.temp/php29/`; every fetch is regenerable with `.temp/php29/fetch_tags.sh` and
`python3 .tasks-php/fixsurvey.py --offline`.

**Both rows came out SETTLED, with a named upstream artefact each. Neither
verdict is the commit the corpus column names.**

---

## §0 Headline, before the detail

| | |
|---|---|
| `ph73` | **NOT one R1h. FIVE corpus ids, FIVE DISTINCT `fix_commit`s, in ~~FOUR~~ FIVE files, spanning 2004-12-17 → 2008-10-26.** All five are located, all five pinned to a tag pair. ⚠ **`FOUR` corrected to `FIVE` by the manager, 2026-09-10 — see the addendum at the foot of this report.** |
| `ph21` | **The named commit is refuted by its own pre-image bytes.** R1h is `a4d2f0430723` (2006-08-10), decided by a **NEWS entry in `php-5.2.0`** and by the fact that the 5.1.0→5.2.0 diff of the function *is* its hunk and nothing else. |

⚠⚠ **Open item 45's premise needs correcting, and the correction is more useful
than the item.** The item reads *"`ph73`'s `fix_commit` DOES NOT TOUCH `ph73`'s
FUNCTION"*. That is true, and the reason is **not** that the column names a fix
in the wrong function. It is that **`ph73` has five corpus ids, each with its
own `fix_commit`, and `fixsurvey.py` reports the first one only** —
`fixsurvey.py:194` is a bare `break` with the comment *"one id per row is
enough"*. The commit it reports (`3d7b0bab28e7`) is **the correct and exact fix
for CRASH-052**, whose site is `Zend/zend_execute.c:1138`. The catalogue's
`c_file_line` header — `Zend/zend_object_handlers.c:520-592`,
`zend_std_call_user_call` — is **CRASH-051's** site, and CRASH-051's fix is
`235e6c0afe1d`. The two never had anything to do with each other.

⭐ **Neither the catalogue nor the column is wrong. The single-record output is.**
`CATALOGUE.md:868` lists all five sites and they map **1:1** onto the five ids
in the order the ids are listed. Nothing needs re-filing on that account.

---

## §1 Method, and what it is *not*

Per §4 of the task, for each row and each corpus id on a fat row:

1. defect pinned by reading the **pristine tarball** (`SOURCES.md` §2 recipe,
   `sha256 5783e0c0…d6919`, re-verified: `5595997` bytes);
2. the named commit's **patch bytes** read
   (`https://github.com/php/php-src/commit/<sha>.patch`, cached under
   `.temp/php29/patches/`);
3. bracketed against release tags via
   `raw.githubusercontent.com/php/php-src/<tag>/<path>` (`UPSTREAM_001.md` §0
   rule 2), **reporting the window, never a guess**;
4. R1h stated with the artefact that decides it.

⚠ **The §4 trap was live on both rows and I did not take it.** No replacement
was chosen for convenience. Every replacement below is decided by an **upstream
artefact** — a bug number in the commit subject, a regression test inside the
commit, a NEWS line in the release, or the commit's own pre-image refuting it —
and the artefact is named on every line. Where a claim rests on a fingerprint
rather than a proof of commit identity, it says so.

`grep -a` / `/usr/bin/grep` throughout (F35). `ext/standard/string.c` — `ph21`'s
file — is one of the 41.

---

## §2 `ph73` — five ids, five fixes

### The mechanical finding first

```
$ python3 .tasks-php/fixsurvey.py --offline
resolved: 101   same-file: 93   OTHER-FILE: 8   unfetched: 0   no-sha: 1   UNRESOLVED: 0
   ph73   3d7b0bab28e7    5 files  Fixed memory allocation bugs related to magic object handler
```

`fixsurvey.json` carries **one** record for `ph73`:

```
 "id": "CRASH-052",  "sha": "3d7b0bab28e7",  "defect_file": "Zend/zend_execute.c",
 "verdict": "same-file"
```

The verdict is **correct about CRASH-052** and is **silent about the other four
ids**, which the loop never reaches. Read from `index.csv` directly:

```
CRASH-052 → 3d7b0bab28e7    CRASH-051 → 235e6c0afe1d    CRASH-027 → d2018ef2c035
CRASH-032 → 30f4d3f9593d    CRASH-100 → 5d804d163ae9
```

⚠ **`fixsurvey.py`'s `same-file` verdict for `ph73` was never a claim about
`zend_object_handlers.c`.** It compares against **CRASH-052's own**
`c_file_line`, which is `Zend/zend_execute.c` — and `3d7b0bab28e7` does touch
that file. The task file's *"a same-file verdict is exactly what `fixsurvey.py`
reports for it, which is why a same-file verdict is a starting point and not an
answer"* is right, and the reason is sharper than expected: **the verdict is
about a different id than the one the row's `c_file_line` came from.**

### Per-id blocks

---

```
ph73 · CRASH-051 · Zend/zend_object_handlers.c:524 (+ :542, :587-588)   [THE ROW'S OWN CITED SPAN]
```

Pasted from the tarball (`tar -xzOf … php-5.0.0/Zend/zend_object_handlers.c | sed -n '520,592p'`):

```c
520  ZEND_API void zend_std_call_user_call(INTERNAL_FUNCTION_PARAMETERS)
524  	zval method_name, method_args, __call_name;
537  	method_name_ptr = &method_name;
541  	method_args_ptr = &method_args;
561  	call_args[0] = &method_name_ptr;
562  	call_args[1] = &method_args_ptr;
565  	call_result = call_user_function_ex(NULL, &this_ptr, &__call_name,
                                          &method_result_ptr, 2, call_args, 0, NULL TSRMLS_CC);
587  	zval_dtor(method_args_ptr);
588  	zval_dtor(method_name_ptr);
```

| | |
|---|---|
| named `fix_commit` (`3d7b0bab28e7`) touches the defect text? | **NO** — 0 occurrences of `call_user_call` in 296,077 patch bytes |
| the *id's own* `fix_commit` (`235e6c0afe1d`) touches it? | **YES, exactly** |
| first tag without the defect | **php-5.0.4** (present in php-5.0.3) → **window 5.0.3 → 5.0.4** |
| **R1h VERDICT** | **`235e6c0afe1d`**, Andi Gutmans, 2004-12-17, *"Fixed Bug #30562 Segmentation fault with `__call()`"* |
| artefact | **bug number #30562 in the commit subject** + the tag pair |

The commit's pre-image is a **later rewrite** of the function than 5.0.0's, so
it will not `git apply`. But the 5.0.0 → 5.0.4 diff of the function body is
**exactly the commit's four line-pairs and nothing else** — i.e. the PHP_5_0
branch received the identical repair against 5.0.0's shape:

```diff
-	zval method_name, method_args, __call_name;
+	zval __call_name;
-	method_name_ptr = &method_name;
+	ALLOC_ZVAL(method_name_ptr);
-	method_args_ptr = &method_args;
+	ALLOC_ZVAL(method_args_ptr);
-	zval_dtor(method_args_ptr);
-	zval_dtor(method_name_ptr);
+	zval_ptr_dtor(&method_args_ptr);
+	zval_ptr_dtor(&method_name_ptr);
```

⭐ **Note what the fix did NOT touch: `zval __call_name` survives.** It is the
*callee name*, passed as `&__call_name` to `call_user_function_ex` and never
published into `call_args`. Upstream heap-promoted the two zvals that reach
userland and left the one that does not — **the idiom is not the defect, the
publication is**, decided by upstream rather than by us.

**What a build task must do:** ship `235e6c0afe1d` as R1h, sha-pinned, and state
in `spec.md` that the commit does not apply as a patch to 5.0.0 and that the
four line-pairs above are the backport, with `php-5.0.4`'s body as the
witness. **Do not ship `3d7b0bab28e7` for this id.**

---

```
ph73 · CRASH-052 · Zend/zend_execute.c:1138 (declaration) / :1146-1149 (escape)
                   in zend_fetch_property_address_read
```

```c
1137  		zval *offset;
1138  		zval tmp;
1140  		offset = get_zval_ptr(op2, Ts, &EG(free_op2), BP_VAR_R);
1145  			case IS_VAR:
1146  				tmp = *offset;
1147  				zval_copy_ctor(&tmp);
1148  				convert_to_string(&tmp);
1149  				offset = &tmp;
1157  		*retval = Z_OBJ_HT_P(container)->read_property(container, offset, type TSRMLS_CC);
```

| | |
|---|---|
| named `fix_commit` (`3d7b0bab28e7`) touches the defect text? | **YES — and this is the id it was named for** |
| first tag without the defect | **php-5.0.5** (present in php-5.0.4) → **window 5.0.4 → 5.0.5** |
| **R1h VERDICT** | **`3d7b0bab28e7`**, Dmitry Stogov, 2005-06-03, *"Fixed memory allocation bugs related to magic object handlers"* |
| artefact | **a regression test inside the commit** (`Zend/tests/object_handlers.phpt`, 171 new lines) + the wrapper fingerprint below |

⚠ **The reason a function-name search misses it is CODE MOTION, not a wrong
commit.** Between 5.0.0 and 2005-06 the VM moved to a generator: at 5.0.0 the
function is `zend_execute.c:1111 zend_fetch_property_address_read`; at the
commit it is `zend_vm_def.h`'s `zend_fetch_property_address_read_helper`
(+ the generated `zend_vm_execute.h`). `zend_vm_def.h` **does not exist at any
5.0.x tag** — all three of my 5.0.x fetches returned `404`. This is F34's shape
with a third cause: *the guard moved because the file did.*

The patch's hunk against that helper deletes the identical block:

```diff
-		zval tmp;
-		switch (OP2_TYPE) {
-			case IS_CV:
-			case IS_VAR:
-				tmp = *offset;  zval_copy_ctor(&tmp);  convert_to_string(&tmp);  offset = &tmp;
+		if (IS_OP2_TMP_FREE()) {
+			MAKE_REAL_ZVAL_PTR(offset);
 		}
```

⭐ **The fingerprint that pins the backport.** `MAKE_REAL_ZVAL_PTR` is a macro
this commit *invents* (`+#define MAKE_REAL_ZVAL_PTR(val)`, 11 lines):

```
php-5.0.3  MAKE_REAL_ZVAL_PTR in zend_execute.c: 0
php-5.0.4  MAKE_REAL_ZVAL_PTR in zend_execute.c: 0
php-5.0.5  MAKE_REAL_ZVAL_PTR in zend_execute.c: 12
```

and php-5.0.5's definition is **byte-identical to the eleven lines the commit
adds**. ⚠ **This is a fingerprint, not a proof of commit identity** — I did not
resolve which sha landed on `PHP_5_0`. It is strong because the wrapper has no
prior existence anywhere in the tree.

⚠⚠ **R1h for CRASH-052 is TWO SITES IN TWO FILES, and a row that ships only one
half will be wrong.** The commit *moves* the non-string→string conversion out
of the caller and into the handler, and heap-promotes the handler's temp:

```diff
 zval *zend_std_read_property(...)
-	zval tmp_member;
+	zval *tmp_member = NULL;
-		tmp_member = *member;  zval_copy_ctor(&tmp_member);  convert_to_string(&tmp_member);  member = &tmp_member;
+ 		ALLOC_ZVAL(tmp_member);  *tmp_member = *member;  INIT_PZVAL(tmp_member);
+		zval_copy_ctor(tmp_member);  convert_to_string(tmp_member);  member = tmp_member;
```

Both halves are in `php-5.0.5` (`zend_std_read_property` line 4 reads
`zval *tmp_member = NULL;` there and `zval tmp_member;` at 5.0.4).

⭐⭐ **This independently confirms F58's best clean negative, from upstream's own
hand.** 5.0.0 has **five** `zval tmp_member` sites in `zend_object_handlers.c`
— `:267` `read_property`, `:318` `write_property`, `:441`
`get_property_ptr_ptr`, `:485` `unset_property`, `:858` `has_property`. At
5.0.5 exactly **two** are heap zvals and **three are still `zval tmp_member`**.
The two upstream fixed are the two that publish to userland. **F58's agent
predicted the split from the C; upstream drew it the same way.**

**What a build task must do:** ship `3d7b0bab28e7` as R1h for this id, cite the
**two** hunks (`zend_execute.c`-side and `zend_object_handlers.c`-side), state
that the 5.0.0 spelling lives in `zend_execute.c` where the commit's lives in
`zend_vm_def.h`, and use `php-5.0.5`'s `zend_execute.c` as the backport witness.

---

```
ph73 · CRASH-027 · Zend/zend_execute_API.c:881 + :917   (zend_lookup_class → __autoload)
```

```c
881  	zval class_name, *class_name_ptr = &class_name;
916  	INIT_PZVAL(class_name_ptr);
917  	ZVAL_STRINGL(class_name_ptr, name, name_length, 0);
919  	args[0] = &class_name_ptr;
923  	retval = call_user_function_ex(EG(function_table), NULL, &autoload_function, &retval_ptr, 1, args, 0, NULL TSRMLS_CC);
```

| | |
|---|---|
| named `fix_commit` (`3d7b0bab28e7`) touches the defect text? | **NO** — it does not touch `zend_execute_API.c` at all |
| the *id's own* `fix_commit` (`d2018ef2c035`) touches it? | **YES, exactly and minimally** |
| first tag without the defect | **php-5.0.5** (present in php-5.0.4) → **window 5.0.4 → 5.0.5** |
| **R1h VERDICT** | **`d2018ef2c035`**, Dmitry Stogov, 2005-05-26, *"Fixed bug #33116 (crash when assigning class name to global variable in `__autoload`)"* |
| artefact | **a regression test inside the commit** (`Zend/tests/bug33116.phpt`) + **`php-5.0.5/NEWS:76`** *"Fixed bug #33116 (crash when assigning class name to global variable in …"* + the tag pair |

The commit's pre-image line `zval class_name, *class_name_ptr = &class_name;` is
**byte-identical to 5.0.0:881**; the only context divergence is that HEAD had
replaced the `"__autoload"` literal with `ZEND_AUTOLOAD_FUNC_NAME`. ⭐ Note the
fix is **two changes, not one**: `ALLOC_ZVAL` *and* `dup 0 → 1`. The second
matters — 5.0.0's `dup=0` makes `class_name_ptr->value.str.val` alias the
caller's `name`, so even a heap zval would hand userland a non-owned pointer.
**A build task that ports only the `ALLOC_ZVAL` half has ported half a fix.**

---

```
ph73 · CRASH-032 · Zend/zend_objects.c:34   (destructor `$this` is a stack zval)
```

```c
34  		zval zobj, *obj = &zobj;
67  		zobj.type = IS_OBJECT;
68  		zobj.value.obj.handle = handle;
69  		zobj.value.obj.handlers = &std_object_handlers;
70  		INIT_PZVAL(obj);
```

| | |
|---|---|
| named `fix_commit` (`3d7b0bab28e7`) touches the defect text? | **NO** — it does not touch `zend_objects.c` at all |
| the *id's own* `fix_commit` (`30f4d3f9593d`) touches it? | **YES** |
| first tag without the defect | **php-5.2.0** (present in **php-5.1.0**) → **window 5.1.0 → 5.2.0** |
| **R1h VERDICT** | **`30f4d3f9593d`**, 2006-07-26, *"Fixed bug #38220 (Crash on some object operations)"* |
| artefact | **a regression test inside the commit** (`Zend/tests/bug38220.phpt`, 92 lines) + **`php-5.2.0/NEWS:310`** *"Fixed bug #38220 (Crash on some object operations). (Dmitry)"* + the tag pair |

⚠ **Backport cost is real here.** The commit's second hunk pre-image uses
`Z_TYPE(zobj)` / `Z_OBJ_HANDLE(zobj)` / `Z_OBJ_HT(zobj)`; 5.0.0 spells the same
three assignments as raw fields (`zobj.type`, `zobj.value.obj.handle`,
`zobj.value.obj.handlers`). The repair is unchanged; the **spelling** is not,
and that is a `divergences` ledger line (`kind: substitution`), not a silent
edit. ⚠ And the fix **adds a `zval_copy_ctor(obj)`** and **two** `zval_ptr_dtor`
sites (one on the already-active-exception path) — it is not a one-line
promotion. ⭐ **This id also shipped vulnerable for two years longer than the
other four in the same file** — through the whole 5.1 series.

---

```
ph73 · CRASH-100 · ext/standard/streamsfuncs.c:728 (and 735, 742)   (userland stream notifier)
```

```c
728  	zval zvs[6];
733  	for (i = 0; i < 6; i++) {
734  		INIT_ZVAL(zvs[i]);
735  		ps[i] = &zvs[i];
736  		ptps[i] = &ps[i];
742  		ZVAL_STRING(ps[2], xmsg, 0);
750  	if (FAILURE == call_user_function_ex(EG(function_table), NULL, callback, &retval, 6, ptps, 0, NULL TSRMLS_CC)) {
```

| | |
|---|---|
| named `fix_commit` (`3d7b0bab28e7`) touches the defect text? | **NO** — it does not touch `ext/` at all |
| the *id's own* `fix_commit` (`5d804d163ae9`) touches it? | **YES, and its pre-image is byte-identical to 5.0.0** |
| first tag without the defect | **php-5.2.7** (present in **php-5.2.6**) → **window 5.2.6 → 5.2.7** |
| **R1h VERDICT** | **`5d804d163ae9`**, Felipe Pena, 2008-10-26, *"MFH: Fixed bug #46388 (`stream_notification_callback` inside of object destroys object variables)"* |
| artefact | **`php-5.2.7/NEWS:83`** *"Fixed bug #46388 (stream_notification_callback inside of object destroys …"* + bug number in the subject + the tag pair |

⭐⭐ **This is the id that carries a real "the defect survived" finding.**
Present at 5.0.0, 5.1.0, 5.2.0 **and 5.2.6** — vulnerable from **2004-07-13 to
2008-05-01, over four years and three minor series.** ⚠ **The date selector
does not see it: 2008 < 2010.**

⚠ **A quirk worth stating in the row, because it looks like a mistake and is
not:** the fix keeps `zval zvs[6]` and keeps `ps[i] = &zvs[i]`, then
immediately overwrites `ps[i]` with `MAKE_STD_ZVAL(ps[i])`. The stack array
becomes dead storage. `ptps[i] = &ps[i]` holds the address of the **slot**, so
`*ptps[i]` reads the heap zval. **Do not "clean this up" in the backport** —
R1h is what upstream shipped.

### Do the five agree?

**No — and that is the answer to §6.2.**

| | CRASH-051 | CRASH-052 | CRASH-027 | CRASH-032 | CRASH-100 |
|---|---|---|---|---|---|
| file | `zend_object_handlers.c` | `zend_execute.c` (+`zend_object_handlers.c`) | `zend_execute_API.c` | `zend_objects.c` | `streamsfuncs.c` |
| fix | `235e6c0afe1d` | `3d7b0bab28e7` | `d2018ef2c035` | `30f4d3f9593d` | `5d804d163ae9` |
| date | 2004-12-17 | 2005-06-03 | 2005-05-26 | 2006-07-26 | 2008-10-26 |
| window | 5.0.3→5.0.4 | 5.0.4→5.0.5 | 5.0.4→5.0.5 | **5.1.0→5.2.0** | **5.2.6→5.2.7** |
| author | Gutmans | Stogov | Stogov | (bug #38220) | Pena |
| repair shape | `ALLOC_ZVAL` + `zval_ptr_dtor` | `MAKE_REAL_ZVAL_PTR` + `zval_ptr_dtor` | `ALLOC_ZVAL` + `dup 0→1` + `zval_ptr_dtor` | `MAKE_STD_ZVAL` + `zval_copy_ctor` + 2× `zval_ptr_dtor` | `MAKE_STD_ZVAL` + `dup 0→1` + `zval_ptr_dtor` |

⚠⚠ **REPORTED, NOT RE-FILED** — `CATALOGUE.md` is off-limits to this task and
the manager lands catalogue moves. §G1's two limbs, applied at the level of
description `CATALOGUE.md` itself uses (*"automatic storage published where user
code can retain it"*):

- ✅ **A DISTINCT fix is admitted as evidence for DIFFERENT.** Five distinct
  commits, four files, four authors, four non-overlapping tag windows spanning
  four years. On §G1's own terms that is **five pieces of DIFFERENT-evidence**,
  and it is the strongest such evidence any row in this corpus has produced.
- ⚠ **But the burden runs the other way** (§G: *one test, one burden — can I show
  these are the SAME?*), and there is a real SAME argument: the (a) unchecked
  predicate, (b) attacker quantity and (c) fault primitive are arguably
  identical across all five — *a zval with automatic storage duration is handed
  to userland, which stores it; the frame returns; the retained pointer is
  read*. Upstream repaired all five with **the same repair shape** (heap-promote
  the published zval, refcount it, drop it after the call), differing only in
  which allocator macro was idiomatic in that file.

⚠⚠⚠ **So §G returns BOTH answers on `ph73`, which is exactly the defect §G
already admits it has** (*"the verdict is a function of the description, not of
the C"*). **I am not breaking that tie.** What I can add, and it is the thing
the manager should weigh: the five ids' fixes are **temporally independent** —
upstream fixed them one at a time over four years, never noticing the class,
and the last one shipped **three and a half years after the first**. If the
five were one mechanism to upstream, the sweep that fixed one would have fixed
the rest. **No commit here fixes more than one of the five.**

⚠ **This has a concrete build consequence whichever way it is decided:** a
single `ph73` row **cannot ship a single sha-pinned `kernel_hardened.c`**.
`PROTOCOL_PHP.md` §F5's *"`kernel_hardened.c` = the real `fix_commit`,
sha-pinned"* has no spelling for five. Either the row splits, or it declares
one id as its subject and records the other four as siblings, or §F5 acquires
a multi-fix spelling. **That is a manager decision, and it should be made
before the build task starts, not inside it — which is the whole point of
open item 45.**

---

## §3 `ph21` — the column is eleven years late, and it is refuted by its own bytes

```
ph21 · CRASH-107 · ext/standard/string.c:4144   (PHP_FUNCTION(str_repeat))
```

Pasted from the tarball (`sed -n '4117,4153p'`):

```c
4117  	zval		**input_str;		/* Input string */
4118  	zval		**mult;			/* Multiplier */
4119  	char		*result;		/* Resulting string */
4120  	int		result_len;		/* Length of the resulting string */
4144  	result_len = Z_STRLEN_PP(input_str) * Z_LVAL_PP(mult);
4145  	if (result_len < 1 || result_len > 2147483647) {
4146  		php_error_docref(NULL TSRMLS_CC, E_WARNING, "You may not create strings longer then 2147483647 bytes");
4147  		RETURN_FALSE;
4148  	}
4149  	result = (char *)emalloc(result_len + 1);
4152  	if (Z_STRLEN_PP(input_str) == 1) {
4153  		memset(result, *(Z_STRVAL_PP(input_str)), Z_LVAL_PP(mult));
```

⭐ **The fault primitive, pinned, because the row will need it:** `:4144`
computes `int × long` in 64-bit `long` and **narrows it at the store** into
`int result_len`; the guard at `:4145` then tests the **narrowed** value and its
second disjunct is provably dead (an `int` cannot exceed `INT_MAX`). `:4149`
allocates from the narrowed value. `:4153` then `memset`s
**`Z_LVAL_PP(mult)`, the UN-narrowed `long`**, into that buffer. So the
overflow is not "allocate small, write `result_len`" — it is **allocate from
the truncated product and write from the untruncated multiplier**, and the two
quantities are different variables. (The `else` arm at `:4155-4166` uses
`result_len` consistently and does not over-write; it under-produces.)

| | |
|---|---|
| named `fix_commit` (`c591f022f8ab`, 2015-05-10) touches the defect text? | **NO** |
| first tag without the defect | **php-5.2.0** (present in **php-5.1.0**) → **window 5.1.0 → 5.2.0** |
| **R1h VERDICT** | **`a4d2f0430723`**, Ilia Alshanetsky, 2006-08-10, *"Fixed overflow on 64bit systems in `str_repeat()` and `wordwrap()`. … # Patches by Stefan E."* |
| artefact | **`php-5.2.0/NEWS:161`** — *"Fixed overflow on 64bit systems in str_repeat() and wordwrap(). (Stefan E.)"* |

### Why `c591f022f8ab` is refuted, and by what

**Not by a tag scan — by the commit's own pre-image.** Its only `str_repeat`
hunk is:

```diff
@@ -4949,6 +4949,10 @@ PHP_FUNCTION(str_repeat)
 	/* Initialize the result string */
 	result_len = input_len * mult;
+	if(result_len > INT_MAX) {
+		php_error_docref(NULL TSRMLS_CC, E_WARNING, "Result is too big, maximum %d allowed", INT_MAX);
+		RETURN_EMPTY_STRING();
+	}
 	result = (char *)safe_emalloc(input_len, mult, 1);
```

The **context lines it must match to apply** are `result_len = input_len * mult;`
and `safe_emalloc(input_len, mult, 1)` — i.e. **the post-5.2.0 form**. The 5.0.0
defect (`int result_len` narrowing the product, then `emalloc(result_len + 1)`)
is **already absent from the commit's own pre-image**. ⭐ **A commit cannot
remove a defect that is not in the code it is diffed against.** This is a
stronger refutation than a tag comparison and it needs no tags at all; F38's
hand-check of this row is confirmed and now has the byte evidence behind it.

### Why `a4d2f0430723` is the replacement, and by what

Three independent artefacts, none of them "a tag that suits":

1. **The NEWS entry** in the first release that lacks the defect:
   `php-5.2.0/NEWS:161`, naming the function *and* the defect class.
2. **The commit subject** names `str_repeat()` and *overflow*.
3. ⭐ **The window contains exactly one change to the function.** The
   5.1.0 → 5.2.0 diff of `PHP_FUNCTION(str_repeat)` is:

```diff
-	int		result_len;		/* Length of the resulting string */
+	size_t		result_len;		/* Length of the resulting string */
 	result_len = Z_STRLEN_PP(input_str) * Z_LVAL_PP(mult);
-	if (result_len < 1 || result_len > 2147483647) {
-		php_error_docref(… "You may not create strings longer then 2147483647 bytes");
-		RETURN_FALSE;
-	}
-	result = (char *)emalloc(result_len + 1);
+	result = (char *)safe_emalloc(Z_STRLEN_PP(input_str), Z_LVAL_PP(mult), 1);
```

   which is **`a4d2f0430723`'s `str_repeat` hunk, line for line**. There is no
   room in the window for a second candidate. ⚠ **This is the check that makes
   the answer a derivation rather than a selection** — the trap §4 warns about
   is *choosing among* tags; here the window admits one commit.

⚠ **Backport cost: one character.** The 5.0.0 → 5.1.0 diff of the function is
`empty_string` → `""` and nothing else, and the commit's pre-image differs from
5.0.0 only by the typo repair *"longer **than**"* vs 5.0.0's *"longer **then**"*
— **inside the line the fix deletes**, so it costs nothing.

⭐ **Bonus artefact, and it is a finding in its own right.** The dead guard
5.0.0 carries was itself introduced as a security fix: **`aab971825371`**, Ilia
Alshanetsky, **2003-04-02**, *"Fixed possible integer overflow in
`str_repeat()`."* — and the four lines it adds are exactly 5.0.0's `:4145-4148`.
**So the guard `ph21` is about is not an oversight; it is a fix that was already
wrong when it shipped, and stayed wrong for three years.** That is a sharper
version of the catalogue's *"a guard killed by the type of the variable it
tests"*, with a sha and a date on it.

### ⚠ Is `a4d2f0430723` complete? — one open sub-question, flagged not answered

`a4d2f0430723` makes `result_len` a `size_t` and moves the allocation to
`safe_emalloc`, which removes the truncation at the allocation site. But
`RETURN_STRINGL(result, result_len, 0)` still stores that `size_t` into a
zval's `int` length. **That is a plausible reading of what `c591f022f8ab`'s
`result_len > INT_MAX` guard is actually for** — i.e. the two commits are the
two halves of one story rather than unrelated.

⚠⚠ **I did not measure this and it is INFERENCE.** I did not build 5.2.0, did
not check whether `memory_limit` makes a > 2 GiB allocation unreachable first,
and did not read `zend_operators`/`ZVAL_STRINGL` at 5.2.0. **A build task should
settle it** — it decides whether `ph21`'s R1h is *complete*, which
`PROTOCOL_PHP.md` §C says is one of the strongest results a row can carry, and
`.memory-php/02-ladder.md` records two of three prior rows whose fix was not.
**Do not write the inference into a finding until it is measured.**

**What a build task must do:** ship `a4d2f0430723` as R1h, sha-pinned, cite
`c591f022f8ab` beside it and say which is which (§F5(iii)'s *"if it does not,
cite both"*), cite `aab971825371` as the provenance of the guard the row is
about, and measure the `INT_MAX` question above.

---

## §4 ⚠ The date selector: the test the manager asked for, and it does not survive it

§6.1 asked whether the *"31 rows dated 2010 or later"* selector is worth
anything, and told me to report the test rather than a promotion.

**On these two rows the selector scores 1 hit and 1 miss, and it is the miss
that is informative.**

| | `ph21` | `ph73` |
|---|---|---|
| named `fix_commit` date | **2015** | **2005** |
| selected by the date rule? | ✅ yes | ❌ no |
| was the column in fact wrong? | ✅ yes | ✅ yes (for the row as cited) |
| **verdict** | **true positive** | **FALSE NEGATIVE** |

⚠⚠ **And the two rows are wrong for reasons that have nothing in common.**

- `ph21` — **right id, right function, wrong era.** The column names a later
  hardening. *Date-visible.*
- `ph73` — **right id, right function for that id, wrong id for the row.** The
  column is correct about CRASH-052 and silent about four others.
  *Date-invisible, and its date is an ordinary 2005.*

⭐ **What n = 2 does support is a DIFFERENT and cheaper selector, and it is one
`csv` read with no network: does the row's own set of corpus ids agree about the
fix commit?** Measured (`.temp/php29/idspread.py`, two controls, both fire):

```
catalogue rows                       : 102
rows with an id on the Part A line   : 102
rows carrying MORE THAN ONE id       : 31
rows whose ids name DIFFERENT commits: 30

CONTROL 1 (must fire) -- ph73 is in the split list:  fires
CONTROL 2 (must NOT fire) -- a single-id row cannot be 'split':  silent
probe: PASS
```

**30 of 102 rows have corpus ids that disagree about the fix commit, and for
every one of them `fixsurvey.py` reports the first and never looks at the rest.**
The extremes are `ph82` (**9 ids, 9 distinct commits**), `ph78` (7/7), and
**four** rows at 5/5 (`ph61 ph73 ph77 ph79`). Cross-tabulated against the date
selector:

```
date selector  (fix_commit >= 2010) : 31 rows,  47 corpus ids
id-spread selector (ids disagree)   : 30 rows,  97 corpus ids
BOTH                                : 10  [ph04 ph39 ph41 ph63 ph65 ph67 ph72 ph75 ph80 ph83]
date only                           : 21
id-spread only                      : 20  [ph18 ph37 ph43 ph46 ph47 ph48 ph61 ph62 ph68
                                            ph70 ph71 ph73 ph76 ph77 ph78 ph79 ph81 ph82 ph86 ph87]
union                               : 51
```

⚠⚠ **The two selectors are nearly orthogonal — 10 rows shared out of 31 and 30
— and each of my two rows is caught by exactly one and missed by the other.**
That is as clean a demonstration as n = 2 can give that **the date is one
failure mode of two, and the corpus already knows about the other one for free.**

### Is the method worth running over the 31 date-selected rows?

**Yes, but not first, and not as the 31.** Costs, from what these two actually
took:

- **a single-id row** whose file is already located: **~15–25 min** — one
  tarball excerpt, one patch fetch, 2–4 tag fetches, one `diff` of the function
  across the window. `ph21` cost about that, and it had `UPSTREAM_001.md` §2's
  bracket already done; **without that head start budget ~30 min.**
- **a fat row**: linear in ids. `ph73`'s five cost about **45 min** — the tag
  fetches amortise across ids in the same file, the patch reads do not.
- **the 31 date-selected rows carry 47 corpus ids** → **≈ 12–16 h**, call it
  **2–3 tasks**.
- **the 30 id-spread rows carry 97 corpus ids** → **≈ 25–30 h**, **4–6 tasks**.
- **the union, 51 rows / 118 ids** → **6–8 tasks.**

⚠ **My recommendation, and it is a recommendation and not a finding.** Do
**neither sweep as a sweep**. The cheap, high-value, non-optional piece is a
**one-line change of shape in `fixsurvey.py`: drop the `break` at `:194` and
report every id's commit per row.** That is minutes of work, costs no network
for rows already cached, and converts 30 rows from *silently under-answered* to
*visibly disagreeing* — which is exactly open item 47's stated hazard (*"a
lookup that finds nothing … looks the same as a row with no fix"*) one level
down. ⚠ **`fixsurvey.py` is a validator under §H**, so that change lands with
must-fire negatives: `ph73` must go from 1 record to 5, and a genuinely
single-id row must stay at 1.

Then hunt R1h **per row, at the head of that row's build task**, on the ~2 rows
per batch that are actually going to be built — which is what this task did and
what `ph07` proved is cheaper than doing it inside the build.

⚠⚠⚠ **n = 2 IS NOT A VALIDATION AND I AM NOT CLAIMING ONE.** Two rows cannot
estimate a rate; F58 is the standing lesson (the ≥5-file selector *looked*
principled over 12 rows and carried no signal). What n = 2 supports is a
**disjunction** — *the date is not the only way the column goes wrong* — which
is a claim about the existence of a second failure mode, and one instance
establishes existence. **It supports nothing about how often either fires.**
⚠ And the id-spread selector's 30 rows are a count of *disagreement*, **not** a
count of *wrong columns*: a fat row whose ids genuinely have different fixes is
correctly described by all of them. **On `ph73` the disagreement was real; on
the other 29 nobody has looked.**

---

## §5 What I did NOT do, and what I am unsure of

1. ⚠ **I did not resolve which sha landed on the `PHP_5_0` branch** for any of
   the three 5.0.x-window fixes. The tag evidence shows the *repair* arrived;
   for CRASH-052 the `MAKE_REAL_ZVAL_PTR` fingerprint makes the identification
   near-certain; for CRASH-051 the 5.0.0→5.0.4 function diff equals the
   commit's edits exactly. **Neither is a proof of commit identity**, and a row
   citing these should say "this commit's repair, witnessed at tag X" rather
   than "this commit was applied at tag X".
2. ⚠ **I did not measure whether any R1h is COMPLETE.** §C says an incomplete
   upstream fix is one of the strongest results a row can carry, and
   `.memory-php/02-ladder.md` says two of three prior rows had one. The
   `ph21` `RETURN_STRINGL` question in §3 is **explicitly flagged as inference**
   and is the one I would attack first.
3. ⚠ **I did not adjudicate `ph73`.** §G returns both answers and I said so
   rather than picking. **No `CATALOGUE.md` edit, no re-filing** — the manager
   lands catalogue moves.
4. ⚠ **The five `ph73` ids' `crashes_pristine_5_0_0` flags differ**
   (CRASH-052 `False`, CRASH-051 `False`, CRASH-027 `True`, CRASH-032 `True`,
   CRASH-100 `True`) and CRASH-100 additionally `requires: network: an HTTP
   listener on 127.0.0.1:8599`. I did not run any reproducer. Per §B1 rule 1,
   `False` is not evidence of absence — recorded here so the build task is not
   surprised by it.
5. ⚠ **CRASH-052's CSV cell also claims `Zend/zend_object_handlers.c:277` is
   "a real sibling instance of the same idiom but is not reached by this
   trigger".** That is 5.0.0's `zend_std_read_property`, and
   `3d7b0bab28e7` fixes it in the same commit — so the corpus's own note and
   the upstream fix agree. I did not test reachability.
6. ⚠ **I did not touch `patterns-php/ph29*` or `.temp/php27/`** (the concurrent
   `ph29-recvfrom-alloc` build), and I did not investigate the **row** `ph29`.
   The only `ph29` string in this report is inside pasted `fixsurvey`/`idspread`
   output.
7. ⚠ **Everything I read was read-only** except `.temp/php29/` and this report
   file. No `git add`, no `git commit`, no history-mutating git; nothing written
   under `RECAP_PHP.md`, `.memory-php/`, `patterns-php/`, `.web/`, `harness/`,
   `common/`, `patterns/`, `results/`, `pilot/`.

### ⚠ One disagreement with my launch prompt, disclosed per rule 2

The resume message said *"`.temp/php29/` does not exist yet, so there is no
partial state of yours to reconcile"*. **That was false.** `.temp/php29/` had
already been created with the six patches, the six tarball excerpts and the
fetch script; I verified it with `ls -la` and continued rather than re-fetching.
No work was lost and nothing was double-fetched. **Recording it because a
manager premise stated as fact in a task or resume message is one an agent has
no reason to doubt** (`PROTOCOL.md` rule 14) — and here the cheap check was one
`ls`. The task file itself was authoritative and I followed it; nothing else in
the resume message contradicted it.

### Brackets (`PROTOCOL_PHP.md` §E1)

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ git status --porcelain
?? .tasks-php/TASK_PHP_029_REPORT.md          <- mine
?? patterns-php/ph29-recvfrom-alloc/          <- the CONCURRENT agent's, untouched by me
?? results-php/preflight/ph07.preflight.json  <- not mine; I ran no gate.py
```

⚠ **I deliberately did NOT run the php half, `gate.py --tool measure
--check-stale`, and this is a disclosed departure from §E1.** That command
appends to `results-php/preflight/_norow.preflight.json`, a **committed** file
(§E's *"not read-only"* row, `TASK_PHP_009` m5) — and this task produced no
record for it to check, while another agent is mid-build in `results-php/`.
Running it would dirty a committed file on behalf of a task that measured
nothing. **The PAT bracket above is the one that carries information here: it
proves the frozen tree is untouched.** ⚠ If the manager wants the php bracket
for the record, run it at the task boundary once `ph29-recvfrom-alloc` has
landed, not now.

---

## §6 Evidence index — everything under `.temp/php29/`

| path | what |
|---|---|
| `fetch_tags.sh` | re-fetches every tag snapshot cited above |
| `tags/` | `php-5.0.1/.3/.4/.5, 5.1.0, 5.2.0, 5.2.6, 5.2.7, 5.3.0` × the 6 relevant paths (`*.ABSENT` = 404, i.e. `zend_vm_def.h` before 5.1.0) |
| `patches/` | `3d7b0bab28e7 235e6c0afe1d d2018ef2c035 30f4d3f9593d 5d804d163ae9 c591f022f8ab a4d2f0430723 aab971825371` |
| `src/` | the six 5.0.0 tarball files, extracted with `SOURCES.md` §2's recipe |
| `c051_5.0.0.txt` / `c051_5.0.4.txt` | the `zend_std_call_user_call` bodies the §2 diff is taken between |
| `ph21_5.0.0.txt` / `ph21_5.1.0.txt` / `ph21_5.2.0.txt` | the `str_repeat` bodies the §3 diffs are taken between |
| `NEWS-5.0.4 / -5.0.5 / -5.2.0 / -5.2.7` | the four NEWS files the artefact citations come from |
| `idspread.py` + `idspread.log` | the §4 selector probe, two controls, `PASS` |
| `selectors.log` / `cost.log` | the §4 cross-tabulation and the per-row id counts |

⚠ Per `CLAUDE.md` rule 1 the fetched blobs are re-derivable and the generator
(`fetch_tags.sh`, `idspread.py`) is the evidence that stays; nothing here is a
binary and nothing needs deleting.

---

## ⚠ MANAGER ADDENDUM, 2026-09-10 — the headline says FOUR files and it is FIVE

`§0`'s summary row read *"FIVE corpus ids, FIVE DISTINCT `fix_commit`s, in **FOUR
files**"*. Re-derived twice from the corpus index, mechanically:

```
CRASH-052  Zend/zend_execute.c:1138            zend_fetch_property_address_read
CRASH-051  Zend/zend_object_handlers.c:524     zend_std_call_user_call
CRASH-027  Zend/zend_execute_API.c:881         zend_lookup_class
CRASH-032  Zend/zend_objects.c:34              zend_objects_destroy_object
CRASH-100  ext/standard/streamsfuncs.c:728     user_space_stream_notifier
```

**Five distinct files and five distinct functions.** (Enclosing functions
resolved against the pinned tarball by `.temp/mgr168/enclosing_fn.py`, whose
selftest calibrates on the `_safe_emalloc`/`_ecalloc` pair F7 caught the manager
confusing.)

✅ **NOTHING ELSE IN THIS REPORT MOVES.** The conclusion — *"a single `ph73` row
cannot ship a single sha-pinned `kernel_hardened.c`"* — is unaffected, and all
five per-id R1h verdicts and tag pins stand as written. ⭐ **The conclusion is in
fact slightly STRONGER at five files than at four.**

⚠ **This is `RECAP_PHP.md`'s oldest standing lesson landing on a report that is
otherwise exact: *the citation and the story about it are two separate claims,
and running the grep does not check the prose.*** The five citations were all
correct; only the count of them was wrong.

⭐ **And this report ANSWERED open item 48 from the other side, before the item
was decided.** *"A single row cannot ship a single `kernel_hardened.c`"* and
§F5's new spelling (*R1h is the fix of the id whose site the kernel extracts*)
are one statement seen from two directions: **a row pricing five sites cannot
have one R1h; a row extracting one always can.** See retired item 48 and F69.
