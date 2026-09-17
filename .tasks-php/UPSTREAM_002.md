# UPSTREAM_002 — the upstream repair survey for the `E3` batch: **`ph70` · `ph69`**

**Author: the manager.** ⚠ **This is EVIDENCE, not a decision.** Nothing here
has been through a reviewer; `PROTOCOL.md` rule 9 keeps it out of `.memory-php/`
until it has. ⚠ It does **not** settle admission — the bar is C-side and per-row,
and `ROW14_001.md` §2 already measured both rows against it.

▶ **What it discharges:** `ROW14_001.md` §7 item 1 — *"pin the commit inside the
5.0.0→5.1.0 window for both rows"*. `UPSTREAM_001` bracketed fixes to a **release
window** and said in terms that **a tag is not a commit**; this survey closes that
gap for the `E3` pair. **Finding the repair is the expensive half of a row and it
is not row-specific work, so the manager does both at once** (`UPSTREAM_001` §0's
own precedent).

---

## §0 Method, and how to regenerate every byte

```sh
# 1. the 5.0.0 pre-image -- the PINNED TARBALL, never GitHub
TB=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
tar -xzOf "$TB" php-5.0.0/ext/standard/array.c
tar -xzOf "$TB" php-5.0.0/ext/pcre/php_pcre.c

# 2. the candidate commits, by PATH and DATE WINDOW (5.0.0 .. 5.1.0)
curl -sS "https://api.github.com/repos/php/php-src/commits?path=ext/standard/array.c&since=2004-07-01T00:00:00Z&until=2005-12-01T00:00:00Z&per_page=100"
curl -sS "https://api.github.com/repos/php/php-src/commits?path=ext/pcre/php_pcre.c&since=2004-07-01T00:00:00Z&until=2005-12-01T00:00:00Z&per_page=100"

# 3. each candidate's patch, and the fix commit's PARENT blob
curl -sSL "https://github.com/php/php-src/commit/<sha>.patch"
curl -sSL "https://raw.githubusercontent.com/php/php-src/<parent-sha>/ext/standard/array.c"
```

⛔ **Nothing fetched here is committed.** Patches and blobs are re-derivable from
the four commands above; this document is the evidence (`CLAUDE.md` Don't #1,
and `F150` — *keep the generator where a checkout can see it*).

⚠⚠ **A COMMIT MESSAGE IS NOT EVIDENCE.** Both rows had a plausible candidate
named in its subject line, and for `ph70` the plausible one is **not** the fix.
Every claim below is settled by **diffing the function**, not by reading the log.

---

## §1 `ph70` — ROW 14. `ext/standard/array.c`, `array_reduce`

### 1.1 ✅ PINNED: **`72c6d5cbafc9`** (2005-06-08)

> *"Fixed memory allocation bugs in array_reduce() with initial value
> (#22463 & #24980)"*

Inside the window (5.0.0 = 2004-07-13, 5.1.0 = 2005-11-24). Its first hunk is
**byte-identical** to the 5.1.0 text `ROW14_001.md` §3 quoted.

⚠ **The decoy, and it is the one a log-reader picks:** `dbc0bb7514a0`
(2004-11-28) — *"fix #29954 (array_reduce segfaults when initial value is
array)"*. It names the right function and the right symptom. **It adds
`convert_to_long_ex(initial);` and nothing else**, leaving `result = *initial;`
untouched — and `72c6d5cbafc9` **deletes that line again**. ▶ **It is not the
repair.**

### 1.2 ⛔⛔ THE FIX IS **TWO HUNKS**, AND `ROW14_001.md` §3 QUOTED ONE

```c
@@ PHP_FUNCTION(array_reduce)
 	if (ZEND_NUM_ARGS() > 2) {
-		convert_to_long_ex(initial);
-		result = *initial;
+		ALLOC_ZVAL(result);
+		*result = **initial;
+		zval_copy_ctor(result);
+		convert_to_long(result);
+		INIT_PZVAL(result);
 	} else {
@@ the EMPTY-ARRAY early return
 	if (zend_hash_num_elements(htbl) == 0) {
 		if (result) {
-			RETVAL_ZVAL(result, 1, 0);
+			RETVAL_ZVAL(result, 1, 1);
 		}
```

⭐⭐⭐ **AND THE TWO HUNKS ARE A MATCHED PAIR — EACH IS HARMFUL ALONE.**
Hunk 1 makes `result` **owned** (a deep copy); hunk 2 makes the empty-array
early return **free** that owned copy.

| applied | consequence |
|---|---|
| **both** | correct |
| **hunk 1 only** | ⚠ **LEAK** on the empty-input path — an owned copy nobody frees |
| **hunk 2 only** | ⛔ **DOUBLE FREE** — destroys the caller's zval, which hunk 1 was what stopped aliasing |

▶ **I have not seen this programme record an R1h with that property before**, and
it is a reason to carry both sites in the kernel rather than the cited line only.
⚠ `ROW14_001.md` §2.1's probe exercises the **loop** path; **an empty-input cell
is owed** before the build brief ships.

### 1.3 ⛔⛔⛔ THE PRE-IMAGE DOES **NOT** MATCH 5.0.0 — SO `ph70` NEEDS A **BACKPORT**

Measured by diffing `array_reduce` between the pinned 5.0.0 tarball and
`cf5a6f81e3af` (the fix commit's parent). ✅ **Exactly three differences, and
all three are benign for this defect:**

| # | 5.0.0 | fix commit's parent | verdict |
|---|---|---|---|
| 1 | *(absent)* | `convert_to_long_ex(initial);` | added by the decoy `dbc0bb7514a0`; **a type coercion, not an ownership change** |
| 2 | `*return_value = *result; zval_copy_ctor(return_value);` | `RETVAL_ZVAL(result, 1, 0)` | ✅ **semantically identical** — `copy=1, dtor=0`, a macro refactor |
| 3 | `*return_value = *result; zval_copy_ctor(return_value); zval_ptr_dtor(&result);` | `RETVAL_ZVAL(result, 0, 1)` | ⚠ **not identical**: copy+free became a **move**. Same outcome, one fewer copy |

⭐ **`result = *initial;` — the defect — is untouched across all three.** So
`72c6d5cbafc9` **does** repair 5.0.0's actual defect, and `ph70` joins
`ph55`/`ph56`/`ph96`/`ph97` as a backported R1h. ⚠ **This is `F44`'s caution
firing on a second row** (*"`bd2e99ee50ed`'s pre-image does not match 5.0.0 — so
it is *a* fix, not demonstrably *the* fix"*) — ▶ **and here it is answered by
measurement rather than left as a caveat.**

`RETVAL_ZVAL`'s semantics were read out of 5.1.0's `Zend/zend_API.h:441-470`,
not assumed: `*(z)=*(zv); if(copy) zval_copy_ctor(z); if(dtor){ if(!copy)
ZVAL_NULL(zv); zval_ptr_dtor(&zv); }`.

### 1.4 ▶ THE BACKPORT, IN 5.0.0 SPELLING

```c
 	if (ZEND_NUM_ARGS() > 2) {
-		result = *initial;                      /* :3804 */
+		ALLOC_ZVAL(result);
+		*result = **initial;
+		zval_copy_ctor(result);
+		INIT_PZVAL(result);
 	} else {
 ...
 	if (zend_hash_num_elements(htbl) == 0) {
 		if (result) {
 			*return_value = *result;
 			zval_copy_ctor(return_value);
+			zval_ptr_dtor(&result);
 		}
 		return;
```

⛔⛔ **NOTE WHAT IS DELIBERATELY ABSENT: `convert_to_long(result);`.** Upstream's
hunk 1 carries it as the *replacement* for `convert_to_long_ex(initial)` — a line
**5.0.0 does not have**. Including it would make `array_reduce($a, $f, "x")`
return `0` where 5.0.0 returns a string result: **a behaviour change smuggled in
with a memory fix.**

▶ **An R1h repairs the cited defect and nothing else.** `UPSTREAM_001` says
*"cite the hunk, not the commit"*; this is the same rule one level finer —
**cite the LINES, not the hunk.** ⚠ **The engineer must not silently drop it
either: `controls/r1h_backport.py` states the choice and checks it**, as
`ph55`/`ph56`/`ph96`/`ph97` do.

✅ The normal-exit path needs **no** change: 5.0.0 already does
`zval_ptr_dtor(&result)` there, which is correct once `result` is owned.

### 1.5 ✅ The citation is byte-exact

`ext/standard/array.c:3804` is `result = *initial;` in the pinned tarball —
`PHP_FUNCTION(array_reduce)` opens at `:3774`, the in-loop
`zval_ptr_dtor(&result)` is at `:3843`, the normal-exit one at `:3859`.
**No off-by-one** (`F56`'s shape, checked because it has happened).

---

## §2 `ph69` — ROW 15. `ext/pcre/php_pcre.c`, `php_pcre_match`

### 2.1 ✅ PINNED: **`631da59b5032`** (2005-10-11)

> *"Fixed bug #34790 (preg_match_all(), named capturing groups, variable
> assignment/return => crash)"*

**One line**, exactly as `ROW14_001.md` §3 recorded:

```c
 			zend_hash_update(Z_ARRVAL_P(subpats), subpat_names[i],
 							 strlen(subpat_names[i])+1, &match_sets[i], sizeof(zval *), NULL);
+			ZVAL_ADDREF(match_sets[i]);
 		}
 		zend_hash_next_index_insert(Z_ARRVAL_P(subpats), &match_sets[i], sizeof(zval *), NULL);
```

### 2.2 ✅✅ THE PRE-IMAGE MATCHES 5.0.0 **BYTE-FOR-BYTE** — NO BACKPORT

5.0.0 `:587-590` and 5.1.0 `:620-626` are **the same seven lines**, differing
only in offset. ⭐ **So the two rows in this batch sit on opposite sides of the
backport question, and that asymmetry was not predictable from the window** —
which is the argument for pinning commits rather than quoting tags.

### 2.3 ⭐ IT SHIPS ITS OWN TRIGGER

The commit adds `ext/pcre/tests/bug34790.phpt` — 23 lines, a named-capture
`preg_match_all` returned out of a function, with the expected output inline.
▶ **§A3a obligation 5 wants a trigger to re-run after rebuilding with the R1h,
and upstream has provided one.** `ph64` already carries a
`controls/bug41037.phpt`, so the precedent for landing it exists.

⚠⚠ **DO NOT WRITE THE BRIEF'S §A3a SECTION YET.** That obligation's wording is
`F141`, it is **UNREVIEWED**, and `_063` §4 may overturn it (`ROW14_001.md` §7
item 2). This note records that the *input* exists, not that the obligation
stands.

---

## §3 WHAT THIS SURVEY DID **NOT** SETTLE

1. ⛔ **The `.patch` files are not produced.** §0's commands re-derive them; a
   row's `controls/<sha>.patch` is landed by the row's own task, because it is
   hashed into `source_sha256`.
2. ⛔ **`ph70`'s backport is specified, not verified.** Nobody has applied it to
   5.0.0 and rebuilt. **`controls/r1h_backport.py` is where that check lives**,
   and §1.4's deliberate omission is the first thing it must assert.
3. ⛔ **The empty-input cell for `ph70`'s probe is owed** (§1.2), and it is the
   path hunk 2 exists for.
4. ⚠ **Neither row's R1h has been run against its trigger.** Blocked on `F141`
   (§2.3).

⭐ **Everything above is reproducible from §0 in about five minutes**, which is
the standard this programme has been failing at law 11 — and the reason this
document exists instead of a scratch note.
