# TASK_PHP_054 — REPORT, agent A: **E2 · E3 · E4** (`ph65`–`ph76`, 12 rows)

**Role:** research investigator. **This is a ranked shortlist with evidence, not a
decision.** Scratch: `.temp/php54A/`. No `git add`/`commit`; nothing written
outside this file and `.temp/php54A/`.

---

## §0 ROW COUNT — printed and reconciled (§3.1's mandate)

```
sed -n '898,931p' patterns-php/CATALOGUE.md | grep -ac '^\*\*ph'   ->  4   (E2, ph65-ph68)
sed -n '932,961p' patterns-php/CATALOGUE.md | grep -ac '^\*\*ph'   ->  4   (E3, ph69-ph72)
sed -n '962,996p' patterns-php/CATALOGUE.md | grep -ac '^\*\*ph'   ->  4   (E4, ph73-ph76)
                                                             total  12

python3 .tasks-php/quota.py   ->  E2 4 · E3 4 · E4 4      ✅ RECONCILED, 12 of 12
```

Every row below was read from **its own Part B entry**. Nothing here comes from a
one-line summary, including the ones in the task file (§0's rule, §4 trap 2).

### What I actually did, so the report can be checked

* **Extracted 20 pristine files** from the pinned tarball (sha256 verified
  `5783e0c0…d6919`, matches) and **read every `file:line` the twelve entries
  cite — 58 citations, and all 58 resolve.** Re-derive with the one-liner in
  `.temp/php54A/NOTES.md`.
* **Read 13 of my 34 `fix_commit` records as patch bytes.** 12 from the
  manager's cache (`.temp/mgr/batch/patches/`); **1 FETCHED** (`4f161fe28997`,
  ph71, absent from the cache) into `.temp/php54A/patches/`. I also **re-fetched
  3 shas** to reproduce the defect in §7.8 — **I fetched, and I am saying so.**
* Ran `fixsurvey.py --offline` and `preimage_screen.py --row phNN --verbose` for
  **all 12 rows**, and wrote `.temp/php54A/dump_fixsurvey.py` because
  `fixsurvey.py` prints only the **top 12** spread rows (`spread[:12]`) — so a
  row with **2 ids → 2 distinct commits is invisible in its stdout**, and two of
  mine (`ph65`, `ph67`) are exactly that.
* **Computed `ph66`'s DJBX33A preimage**, which its entry says "was never
  computed" — `.temp/php54A/ph66_preimage.py`, selfcheck **PASS**, two controls.

---

## §1 STAGE 1 — all 12 rows, from their own entries

`needs` ticks: **Z**vals · **A**llocator · **H**ashTable · **X**=executor/VM ·
**U**serland re-entry · **G**=stack garbage · **P**recomputation/hash preimage ·
**F**ailure injection · **M**=more than one subsystem.

| row | tier | defect site (as the entry gives it) | harm | needs | determ.? | observable by | R1h (year·files·same?·ids→commits) |
|---|---|---|---|---|---|---|---|
| **ph65** | `modelled` | `ext/standard/var_unserializer.c:875-893`, `:176-186` | UAF-read then double-free (CWE-416) | **Z A H M** (4) | yes | ledger `(allocs,frees)` + checksum + ASan | 2013 ⚠late · 5f · same · **2→2** |
| **ph66** | `verbatim` | `Zend/zend_hash.c:464-465` | **silent wrong answer** — wrong element deleted | **H** (1) ⓘ + P, now discharged | **YES** | **checksum divergence alone** | **2006 · 1f · same · 1→1** |
| **ph67** | `verbatim`/`narrowed` per limb | `Zend/zend_hash.c:214-236` (+ `zend_variables.c:47-56`) | UAF-read/write through a dead payload still advertised | **Z A H U M** (5) | yes | ledger + checksum | 2014 ⚠late · 1f · same · **2→2** |
| **ph68** | `verbatim` | `Zend/zend_execute_API.c:617-626` | stale handle resolves to a **different live object** → wrong answer, then NULL/garbage deref at `:625` | **A** (1) ⓘ+Z | **YES** (LIFO free list) | checksum + NULL deref | 2007 · 2f (1 code) · same · **3→3** |
| **ph69** | `narrowed` | `ext/pcre/php_pcre.c:584-593` | refcount < holders → later double-free / UAF-write | **Z A H** (3) | **YES** | fold of `(refcount,payload)` + ledger | **2005 · 3f (1 code) · same · 1→1** |
| **ph70** | `narrowed` | `Zend/zend_object_handlers.c:392-395` + 3 more | over-decrement → premature free → UAF | **Z A U M** (4) | yes | refcount fold + ledger | 2006 · 3f · same · **4→4** |
| **ph71** | `modelled` | `Zend/zend_execute.c:220-278` | UAF-read of `value_ptr->is_ref`, then UAF-write | **Z A H X** (4) | yes | refcount/`is_ref` fold + ledger | 2005 · 3f (1 code) · same · **4→4** |
| **ph72** | `narrowed` | `ext/standard/array.c:993-1063` | **two** faults: (A) free of an **uninitialised** stack pointer, (B) **double** free | **Z A H U G(A only) M** (5) | **(B) yes · (A) NO** | ledger + ASan | 2012 ⚠late · 3f · same · **3→3** |
| **ph73** | `narrowed` | `Zend/zend_object_handlers.c:520-592` (+4 siblings) | automatic storage retained by userland → dangling stack zval + freed HashTable | **Z A H U G(part) M** (5) | **part** | ledger + checksum + ASan | 2005 · 5f · same · **5→5** |
| **ph74** | `narrowed` | `Zend/zend_API.c:1957`, `:1965-1966` | non-allocator pointer handed to the deallocator (CWE-590) | **Z A U G** (4) | **NO** — `refcount`/`is_ref` are stack garbage, **the entry says so** | ledger + abort | 2006 · 4f · same · **1→1**, and **⛔ NOT-THE-REPAIR** |
| **ph75** | `narrowed` | `Zend/zend_variables.c:139-153` | ownership taken, commit skipped → dangling `original_ht` / leak | **Z A H U F M** (6) | yes, *given* an injected failure | ledger + checksum | 2014 ⚠late · 1f · same · **4→4** ⚠ sha, §7.8 |
| **ph76** | `narrowed` | `ext/standard/array.c:2058-2061` | **`free()` of a non-allocator pointer** (CWE-590) → hard abort | **A H** (2) ⓘ | **YES**, and `crashes_pristine_5_0_0 = True` | **abort / ASan "not malloc()-ed"** + ledger | **2005 · 5f · same · 4→4, 2 of them decisively excluded** |

ⓘ **ph66** — I tick `H` only. `zend_hash` allocates a `Bucket` per insert, so a
kernel's allocations are **O(n) per call** and `§B1a` applies to its
cross-language column; but the **harm** is a pure checksum divergence with the
allocator, as the entry says, "entirely out of the picture". That is a
*labelling* cost, never a kill (`§B1a.1`), and `§B1a.4` leaves the
`fixed-R4 bound` untouched.
ⓘ **ph68** — `Z` is avoidable: the entry says "the handle table alone lifts…
Do not import the object model", and the class-entry deref becomes a payload
word. `A` is the store's `erealloc` on growth, amortised O(1).
ⓘ **ph76** — `Z` is avoidable: the mechanism needs a *tagged container*, not a
zval. No userland re-entry, no stack garbage, no precomputation, no failure
injection, one subsystem.

### The entries' own ⚠ risk lines, quoted

| row | the entry's ⚠ line, verbatim |
|---|---|
| ph65 | "⚠ risk: `modelled` — the parser is a re2c state machine over zvals. **The mechanism narrows cleanly** to a growable table of raw pointers to values the parser also frees; the re2c body need not come along. Say which was built." |
| ph66 | "⚠⚠ risk: **it produces no fault — a silent wrong answer.** ✅ That is a classification, not a kill (`CLAUDE.md` rule 6; `p29` shipped this shape) and it is the **best checksum-visible row in the corpus, with the allocator entirely out of the picture.** The DJBX33A preimage the fixture needs was never computed; compute it before building." |
| ph67 | "⚠ risk: `verbatim` for CRASH-160 (zend_hash alone); `narrowed` for CRASH-154 (needs the zval tag). Declare the tier per limb or the provenance overlap will disagree with the claim." |
| ph68 | "⚠ risk: the handle table alone lifts; the class-entry dereference becomes a payload-word read. Do not import the object model." |
| ph69 | "⚠ risk: **split from ph70 deliberately** (adjudication §2 item 6) — a **missing increment** breaks `I7` from the opposite direction to an **unmatched decrement**. Different C; two rows." |
| ph70 | "⚠ risk: the `u64` must carry the refcount, not just the payload — this row's harm is invisible in the payload until the free lands." |
| ph71 | "⚠ risk: `modelled` — the surrounding function is dense executor plumbing (`temp_variable`, `znode` operand kinds, `PZVAL_LOCK`). The mechanism re-expresses in a few lines; declare the deletions individually." |
| ph72 | "⚠ risk: the **uninitialised** first free and the **double** later free are two different faults from one line. Record which fired." |
| ph73 | "⚠ risk: **CRASH-139 is NOT in this idiom and is split out to ph74** (adjudication §2 item 6) — its CWE is 590, not 562." |
| ph74 | "⚠ risk: routed to ph76's provenance family, not ph73's. If it is built beside ph73, the `spec.md` must say which invariant each is about or the pair reads as one row twice." |
| ph75 | "⚠ risk: the failure injection is the row. Without a way to fail mid-copy from the blob, the kernel is correct and measures nothing." |
| ph76 | "⚠ risk: a struct with **one embedded container and one heap-allocated one**, and a function that frees \"the container\" without asking which kind it has. If the extraction heap-allocates both, there is no defect." |

### ⭐ `ids → commits`, RE-DERIVED — and the task file's list is incomplete

`fixsurvey.py`'s stdout prints only the top 12 spread rows. The task file's §2
named "**at least** ph70 ph71 ph73 ph75 ph76" in my set. The full per-record
walk (`.temp/php54A/fixsurvey_myrows.log`) adds **ph65 (2→2), ph67 (2→2),
ph68 (3→3), ph72 (3→3)**:

```
ph65 2->2   ph66 1->1   ph67 2->2   ph68 3->3
ph69 1->1   ph70 4->4   ph71 4->4   ph72 3->3
ph73 5->5   ph74 1->1   ph75 4->4   ph76 4->4
```

▶ **Exactly THREE rows in my set owe NO R1h decision: `ph66`, `ph69`, `ph74`.**
And `ph74`'s single commit is the one that is **provably excluded**.

### `preimage_screen.py` — every record, with the right label

Run per row with `--verbose` (the "every record" block needs it).

| row | records |
|---|---|
| ph65 | CRASH-121 **CANDIDATE** · CRASH-118 `INAPPLICABLE-SAME-FILE` (**⛔ says NOTHING**, F68/F95) |
| ph66 | LOGIC-001 **CANDIDATE** |
| ph67 | CRASH-160 **CANDIDATE** · CRASH-154 **CANDIDATE** |
| ph68 | all three **CANDIDATE** |
| ph69 | CRASH-131 **CANDIDATE** |
| ph70 | all four **CANDIDATE** |
| ph71 | CRASH-004 **CANDIDATE** · CRASH-003 `INAPPLICABLE` · CRASH-025 `INAPPLICABLE` · CRASH-067 `INAPPLICABLE-SAME-FILE` (⛔ none of these three is an exclusion) |
| ph72 | CRASH-074 **CANDIDATE** · CRASH-125 **CANDIDATE** · CRASH-112 `NO-SPAN` |
| ph73 | all five **CANDIDATE** |
| ph74 | CRASH-139 **⭐ `NOT-THE-REPAIR`** — the only decisive exclusion in my 12 |
| ph75 | CRASH-161 **CANDIDATE** · LOGIC-026 `INAPPLICABLE` · LOGIC-027 `INAPPLICABLE-SAME-FILE` · LOGIC-004 **CANDIDATE** |
| ph76 | CRASH-012 **CANDIDATE** · CRASH-026 **CANDIDATE** · CRASH-148 **`NOT-THE-REPAIR`** · CRASH-078 **`NOT-THE-REPAIR`** |

⚠ **`CANDIDATE` means only "could not exclude", and §3.2(c) is right that the
label is not the answer.** Three of my `CANDIDATE`s are **not repairs at all**,
and I found that only by reading the patch bytes — §7.

---

## §2 STAGE 2 — DEEP VERIFICATION: `ph66` (E2)

### (a) every cited line, quoted from the pristine tarball

`Zend/zend_hash.c:450-465`, pristine:

```c
450  ZEND_API int zend_hash_del_key_or_index(HashTable *ht, char *arKey, uint nKeyLength, ulong h, int flag)
...
457      if (flag == HASH_DEL_KEY) {
458          h = zend_inline_hash_func(arKey, nKeyLength);
459      }
460      nIndex = h & ht->nTableMask;
461
462      p = ht->arBuckets[nIndex];
463      while (p != NULL) {
464          if ((p->h == h) && ((p->nKeyLength == 0) || /* Numeric index */
465              ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength))))) {
```

✅ **The entry's quoted block is `:464-465` verbatim**, comment included. The
only difference from the catalogue's rendering is run-length of whitespace.

### (b) is the `▸ trigger` verified, plausible, or WRONG?

> `▸ trigger: a string key whose DJBX33A hash over len+1 equals a live integer index.`

▶ **VERIFIED (i) — traced to the cited site in the C, end to end:**

1. **`nKeyLength == 0` really does mark a numeric bucket** — `zend_hash.c:387`:
   `p->nKeyLength = 0;   /*  Numeric indices are marked by making the nKeyLength == 0 */`.
   So for such a bucket the left disjunct at `:464` is **true unconditionally**
   and the whole test collapses to `p->h == h`.
2. **Both keys land in the same chain** — `nIndex = h & nTableMask` at `:460`,
   and `h` is equal by construction, so the chain is the same at any table size.
   No rehash timing, no table-size dependence.
3. **PHP reaches it with `nKeyLength = strlen+1`** —
   `zend_execute.c:3673  zend_symtable_del(ht, offset->value.str.val, offset->value.str.len+1);`
   (the `unset($a["…"])` path) and `zend_execute.c:3612  zend_hash_del(target_symbol_table, varname->value.str.val, varname->value.str.len+1);`
   (the `unset($x)` path). `zend_hash.h:333-337`'s `zend_symtable_del` declines
   the `HANDLE_NUMERIC` fast path for a non-numeric string and falls through to
   `zend_hash_del` → `zend_hash_del_key_or_index(…, HASH_DEL_KEY)`.
4. **"over len+1" is right and it matters** — `zend_inline_hash_func`
   (`zend_hash.h:243-268`) hashes `nKeyLength` bytes, so **the terminating NUL
   is hashed.** `hash` is `ulong`, 64-bit here; there is no 32-bit reduction.

### ⭐ (b+) THE ENTRY'S ONE NAMED UNKNOWN IS NOW DISCHARGED

> "The DJBX33A preimage the fixture needs **was never computed**; compute it
> before building."

`.temp/php54A/ph66_preimage.py`, **selfcheck PASS**, two controls. **It is
arithmetic, not a search, in both directions:**

* **FORWARD, no search at all.** `H("x"+NUL) = 5863869`. A PHP array index is a
  `long`, so the victim's key is just that integer:

  ```php
  $a = array(); $a[5863869] = 'victim'; $a['other'] = 'live';
  unset($a['x']);        // 5.0.0 deletes $a[5863869]. The table never held 'x'.
  ```
* **PREIMAGE for ANY target index, solved not searched.** 33 is odd, hence
  invertible mod 2⁶⁴, so the bijective base-33 expansion of
  `(N − 5381·33ⁿ)·33⁻¹` *is* the key bytes. Demonstrated for
  `N = 0, 1, 2, 42, 1000, 65535`, each re-hashed and checked.
* **Controls.** must-NOT-fire: flipping one byte of the `N=42` key gives
  `299878227680151177 ≠ 42`. must-fire: `H('x'+NUL)=5863869` vs `H('x')=177693`
  differ — the detail a fixture gets wrong if it forgets the NUL.

▶ **The entry's cost line is real but it over-prices it.** Say "compute the
constant", not "compute a preimage".

### (c) the R1h, read as bytes

`b73349dbe4e9`, Zeev Suraski, **2006-02-01**, subject *"Fix possibility of a
wrong element being deleted by zend_hash_del() Thanks Stefan!"*.
**1 file · 1 hunk · 4 insertions, 2 deletions.** From the cache.

```
@@ -461,8 +461,10 @@ ZEND_API int zend_hash_del_key_or_index(HashTable *ht, char *arKey, uint nKeyLen
 	p = ht->arBuckets[nIndex];
 	while (p != NULL) {
-		if ((p->h == h) && ((p->nKeyLength == 0) || /* Numeric index */
-			((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength))))) {
+		if ((p->h == h)
+			 && (p->nKeyLength == nKeyLength)
+			 && ((p->nKeyLength == 0) /* Numeric index (short circuits the memcmp() check) */
+				 || !memcmp(p->arKey, arKey, nKeyLength))) {
```

▶ **The two deleted lines are 5.0.0's `:464-465` BYTE-FOR-BYTE**, and the hunk's
own `@@` context names the function. The screen's `CANDIDATE` is the weakest
true statement about this commit; **by hand it is the repair, and the repair of
exactly the cited lines.** `ids→commits = 1→1`, so **no R1h decision is owed.**

### (d) is the fix a CENSUS?

**No, and that is a positive result.** The patch touches **one** site. I checked
why: **`:464` is the only comparison in `zend_hash.c` written as a disjunct.**

```
:215  (p->h == h) && (p->nKeyLength == nKeyLength)       add_or_update          CORRECT
:280  (p->h == h) && (p->nKeyLength == nKeyLength)       quick_add_or_update    CORRECT
:356  (p->nKeyLength == 0) && (p->h == h)                index_update           CORRECT
:464  (p->h == h) && ((p->nKeyLength == 0) || …)         del_key_or_index       ⛔ THE DEFECT
:854  (p->h == h) && (p->nKeyLength == nKeyLength)       find                   CORRECT
:881  …                                                  quick_find             CORRECT
:906  …                                                  exists                 CORRECT
:932  …                                                  quick_exists           CORRECT
:955  (p->h == h) && (p->nKeyLength == 0)                index_find             CORRECT
:976  (p->h == h) && (p->nKeyLength == 0)                index_exists           CORRECT
```

⭐ **One wrong comparison against NINE right ones, all in the same file.** That
is `ph55`'s shape — *"the codebase gets it right at every site but the one"* —
and it means the contrast can live **inside the extracted kernel** rather than in
a comment. No sibling is owed.

---

## §3 STAGE 2 — DEEP VERIFICATION: `ph69` (E3)

### (a) cited lines, quoted

`ext/standard/php_pcre.c:583-593`, pristine:

```c
583      /* Add the match sets to the output array and clean up */
584      if (global && subpats_order == PREG_PATTERN_ORDER) {
585          for (i = 0; i < num_subpats; i++) {
586              if (subpat_names[i]) {
587                  zend_hash_update(Z_ARRVAL_P(subpats), subpat_names[i],
588                                   strlen(subpat_names[i])+1, &match_sets[i], sizeof(zval *), NULL);
589              }
590              zend_hash_next_index_insert(Z_ARRVAL_P(subpats), &match_sets[i], sizeof(zval *), NULL);
591          }
592          efree(match_sets);
593      }
```

✅ `:584-593`, `:587-588`, `:590` all exact, and **there is no `ZVAL_ADDREF`
between them.** The "refcount 1, one owner" claim is verified at `:457-462`:
`match_sets = safe_emalloc(...)`, then per element `ALLOC_ZVAL` + `array_init` +
`INIT_PZVAL` — refcount 1.

### (b) trigger: **VERIFIED, WITH A NECESSARY CORRECTION**

> `▸ trigger: any pattern with a named subpattern.`

**Reaching the cited site needs three things and the sentence states one:**

1. `global == 1` — i.e. **`preg_match_all`**, not `preg_match`
   (`php_pcre.c:612-615  PHP_FUNCTION(preg_match_all) { php_pcre_match(…, 1); }`).
   Under `preg_match` the whole block at `:584` is unreachable.
2. `subpats_order == PREG_PATTERN_ORDER` — satisfied by default
   (`:356 subpats_order = 0`, `:370 subpats_order = PREG_PATTERN_ORDER;` on the
   `global` path; `php_pcre.h:35 #define PREG_PATTERN_ORDER 1`). **No flag
   argument is needed.**
3. `subpat_names[i] != NULL` — the named-subpattern condition the sentence gives
   (`:449 subpat_names[name_idx] = name_table + 2;`).

**And the HARM needs one more step the sentence omits**: inside the call the
defect is only a *state* (two owning slots, count 1). The free lands when the
result array is destroyed while something else still names the inner zval.
Upstream's own regression test in the fix commit supplies it exactly:

```php
function func1(){ … preg_match_all('/(?P<word>the)/', $string, $matches);
                  return $matches['word']; }
$words = func1(); var_dump($words);
```

ⓘ For a *kernel* this is not a cost: the entry's `u64` already folds
`(refcount, payload)` per slot, so the **defective state itself** is
checksum-visible without staging the free.

▶ Classification: **(i) verified to reach the cited site**, with the sentence
corrected to *"any `preg_match_all` with a named subpattern"*, and with the
harm-path step named.

### (c) the R1h, read as bytes

`631da59b5032`, Dmitry Stogov, **2005-10-11**, *"Fixed bug #34790
(preg_match_all(), named capturing groups, variable assignment/return =>
crash)"*. **3 files, of which ONE is code; 1 line added.** From the cache.

```
@@ -620,6 +620,7 @@ static void php_pcre_match(INTERNAL_FUNCTION_PARAMETERS, int global)
 			if (subpat_names[i]) {
 				zend_hash_update(Z_ARRVAL_P(subpats), subpat_names[i],
 								 strlen(subpat_names[i])+1, &match_sets[i], sizeof(zval *), NULL);
+				ZVAL_ADDREF(match_sets[i]);
 			}
 			zend_hash_next_index_insert(Z_ARRVAL_P(subpats), &match_sets[i], sizeof(zval *), NULL);
```

▶ **The pre-image's four context lines are 5.0.0's `:586-590` byte-for-byte**
(only the line numbers drift, 620 vs 586). The repair is **the single missing
increment the entry names**. `ids→commits = 1→1`. **This is the smallest R1h in
my twelve and it comes with upstream's own `.phpt`.**

### (d) census?

**No.** One site in one code file; the other two files are `NEWS` and the test.
No named wrapper (F58's predictor is absent, correctly). No sibling owed.

---

## §4 STAGE 2 — DEEP VERIFICATION: `ph76` (E4)

### (a) cited lines, quoted

`ext/standard/array.c:2058-2061`, pristine — `PHP_FUNCTION(array_splice)`:

```c
2058     /* Replace input array's hashtable with the new one */
2059     zend_hash_destroy(Z_ARRVAL_P(array));
2060     efree(Z_ARRVAL_P(array));
2061     Z_ARRVAL_P(array) = new_hash;
```

✅ exact. The entry's **"`EG(symbol_table)` is a `HashTable` embedded in the
executor-globals struct — not an allocator return"** is verified in two places:

```
Zend/zend_globals.h:169    HashTable symbol_table;   /* main symbol table */      <- a MEMBER, not a pointer
Zend/zend_execute_API.c:153        globals->value.ht = &EG(symbol_table);
Zend/zend_execute_API.c:145        zend_hash_init(&EG(symbol_table), 50, NULL, ZVAL_PTR_DTOR, 0);
```

Both named siblings check out too: `zend_operators.c:661
object_and_properties_init(op, zend_standard_class_def, op->value.ht);` exact,
and `array.c:3272-3274`'s `*return_value = **args[0]; zval_copy_ctor(return_value);`
exact — with the **no-op** it depends on confirmed at
`zend_variables.c:146-147  if (zvalue->value.ht == &EG(symbol_table)) { return SUCCESS; }`.

### (b) trigger: **VERIFIED (i)**

> `▸ trigger: array_splice($GLOBALS, 0, 1);`

* `array_splice` is declared `first_arg_force_ref`
  (`ext/standard/basic_functions.c:767`), so `$GLOBALS` can be passed and
  modified.
* `Z_ARRVAL_P(array)` is then `&EG(symbol_table)` (the two lines above), so
  `:2060` is `efree(&EG(symbol_table))` — a `free()` of a pointer that is a
  **struct member**, never an allocator return.
* Corroborated independently: **`crashes_pristine_5_0_0 = True`** for CRASH-012,
  and the fix commit ships `ext/standard/tests/array/bug31158.phpt` doing exactly
  `array_splice($GLOBALS,0,count($GLOBALS));`.
  (⚠ `True` is corroboration; per F3 the *absence* of it would prove nothing.)

### (c) the R1h, read as bytes — and **it is a SUBSET of its fix commit**

`1d33a3e95e4e`, Dmitry Stogov, **2005-07-04**, *"Fixed bug #31158 (array_splice
on $GLOBALS crashes)"*. **5 files.** From the cache.

The `array_splice` hunk's pre-image is **byte-identical to 5.0.0's `:2059-2061`**:

```
 	zend_hash_destroy(Z_ARRVAL_P(array));
-	efree(Z_ARRVAL_P(array));
-	Z_ARRVAL_P(array) = new_hash;
+	if (Z_ARRVAL_P(array) == &EG(symbol_table)) {
+		zend_reset_all_cv(&EG(symbol_table) TSRMLS_CC);
+	}
+	*Z_ARRVAL_P(array) = *new_hash;
+	FREE_HASHTABLE(new_hash);
```

⛔⛔ **BUT TWO OF THE FIVE FILES CANNOT BE BACKPORTED TO 5.0.0, AND I CHECKED
RATHER THAN ASSUMED.** `Zend/zend_API.h` + `Zend/zend_execute_API.c` add
`zend_reset_all_cv()`, whose body reads `ex->CVs[i]` and
`ex->op_array->last_var`. Measured on the pristine tarball:

```
grep -an 'CVs|last_var'  Zend/zend_compile.h  Zend/zend_execute.h  Zend/zend.h   ->  NO HITS
grep -an 'zend_delete_global_variable'  Zend/zend_execute_API.c                  ->  NO HITS
```

**PHP 5.0.0 has no compiled variables at all**, so the CV-cache half of the
repair has nothing to repair — the commit is against a 5.1-dev tree. The
memory-safety repair *for 5.0.0* is the `array.c` change alone.

▶ **This is `PROTOCOL_PHP.md` §C's "⚠⚠ AND IT MAY BE TOO BIG" — the `ph07`
shape — and §C says it is OPEN at n = 1 and "a row that wants to do the same
brings it to the manager as a proposal".** It is an *easier* case than `ph07`'s:
the dropped hunks are **provably inexpressible** in 5.0.0 (the symbols do not
exist) rather than a judgement about benign behaviour. **But §C does not
self-apply, and this is the decision that must be made before dispatch.**

ⓘ On `ids→commits = 4→4`: **§C settles it cheaply.** CRASH-012's own
`c_file_line` is `ext/standard/array.c:2060` — *the catalogued defect site* — so
"the id whose `c_file_line` the kernel extracts" is CRASH-012 and R1h is
`1d33a3e95e4e`. The other three are sibling evidence, and **two of them
(CRASH-148, CRASH-078) are `NOT-THE-REPAIR`**, i.e. decisively excluded anyway.

### ⭐ (d) IS IT A CENSUS? **YES — three sites, two uncatalogued, and F58 called it**

The patch touches **three** sites in `ext/standard/array.c`, and all three
pre-images are present in 5.0.0:

| # | 5.0.0 site | function | catalogued in `ph76`? | live with `$GLOBALS`? |
|---|---|---|---|---|
| 1 | `array.c:1982-1984` | `array_unshift` | ❌ **no** | ✅ yes — `first_arg_force_ref`, `basic_functions.c:766` |
| 2 | `array.c:2059-2061` | `array_splice` | ✅ yes | ✅ yes |
| 3 | `array.c:2556-2558` | `array_pad` | ❌ **no** | ✅ **yes — see below** |

And the repair introduces a **named wrapper**, `zend_reset_all_cv` — **F58's one
measured positive predictor of a census, which names `zend_reset_all_cv`
explicitly.** F58 already scored `ph76` at **2** sibling sites; this is an
independent reproduction of that count from the patch bytes.

⭐ **Site 3 is live, and by COMPOSING the row's two named mechanisms** — I read
it rather than assumed it. `array_pad` is by value
(`basic_functions.c:776 PHP_FE(array_pad, NULL)`), so one would expect
`return_value` to be a fresh heap table. It is not:

```c
2528     /* Copy the original array */
2529     *return_value = **input;
2530     zval_copy_ctor(return_value);
...
2556     zend_hash_destroy(Z_ARRVAL_P(return_value));
2557     efree(Z_ARRVAL_P(return_value));
```

`:2529-2530` is the **byte-identical idiom** to the entry's own named sibling
`array.c:3272-3274`, and `zval_copy_ctor` **no-ops for the symbol table**
(`zend_variables.c:146-147`). So `array_pad($GLOBALS, 1000, 0)` — `do_pad` true,
`num_pads` under the `1048576` guard at `:2539` — reaches
`efree(&EG(symbol_table))` at `:2557`. ⚠ **Read, not run** (§8).

---

## §5 THE COST VERDICT — in §3.3's words

### E2 — **CHEAP**
Led by **`ph66`**: `verbatim`; **one** `needs` tick (HashTable); harm
deterministic and visible in a checksum with the allocator out of the picture;
R1h **1 file, same file, one commit, one hunk, pre-image byte-exact**; **no R1h
decision owed**; the one named unknown (the DJBX33A constant) **computed in this
task**; and a 1-against-9 sibling contrast inside the same file.
⚠ **The one thing that will cost a task and I am naming it:** `zend_hash`
allocates a `Bucket` per insert, so a kernel's allocations are **O(n) per call**
and `§B1a`'s cross-language label applies. `§B1a.1` makes that a finding, never a
kill, and `§B1a.4` leaves the `fixed-R4 bound` unaffected.
ⓘ **`ph68` is a genuinely cheap second** and the one-line table hides it: its
2007 fix adds **exactly** the missing `!object_buckets[handle].valid` guard, at
two sites in one code file, on a pre-image byte-identical to 5.0.0's `:617-620`
— and its harm (a stale handle resolving to a *different live object*) is
deterministic and checksum-visible with no zvals and no HashTable.
⛔ **`ph67` is BLOCKED-ON-A-DECISION** — see §7.2; the decision is *which limb*,
and it decides whether an R1h exists at all.

### E3 — **MEDIUM**
Led by **`ph69`**, whose R1h is **one added line** with an exact pre-image and
upstream's own `.phpt` — the best R1h *content* in my twelve.
**The specific thing that will cost a task:** every E3 row needs **three**
subsystems in the kernel — boxed values carrying a refcount, an owning
container, and the allocator ledger as part of the oracle, because `I7`'s harm
is invisible in the payload until the free lands (the entry says so for `ph70`
and it is equally true of `ph69`). That is a bigger kernel than `ph66`'s and a
bigger one than `ph76`'s.
ⓘ **`ph71` is much better than its one-line summary**: its R1h `4f161fe28997`
is a **zero-net-line MOVE** of six lines, on a byte-exact 5.0.0 pre-image, with
upstream's own `.phpt` — §7.5. It is `modelled` and 4→4, which is the real cost.
⛔ **`ph72` has NO KNOWN R1h** — §7.3.

### E4 — **MEDIUM**
Led by **`ph76`**, which is the *cheapest mechanism* in all twelve — two
`needs` ticks, no zvals required, no userland re-entry, no stack garbage, no
precomputation, no failure injection, one subsystem — with a **hard,
deterministic abort**, `crashes_pristine_5_0_0 = True`, upstream's `.phpt`, and a
**free, already-mined census of three sites**.
**The specific thing that will cost a task, and it is a manager decision:**
**the R1h is a SUBSET of its `fix_commit`** because 2 of its 5 files use symbols
that do not exist in 5.0.0 (`ex->CVs`, `op_array->last_var`,
`zend_delete_global_variable`). `PROTOCOL_PHP.md` §C leaves that **OPEN at
n = 1** and requires a proposal to the manager. **Until that is ruled on, `ph76`
cannot be dispatched with a clean R1h story.**
ⓘ **`ph73` is the strong second** and its R1h is the best *shape* in my set —
**2004 · 1 file · 9 lines** (`235e6c0afe1d`), because the catalogue's cited span
is CRASH-051's and `FIXSURVEY_001.md:56-63` already says so. ⚠ Its pre-image
differs from 5.0.0's declaration line, and the fix leaves 5.0.0's **third**
stack zval `__call_name` un-hoisted — §7.6.
⛔ **`ph74` is BLOCKED-ON-A-DECISION** — its only `fix_commit` is the one
`NOT-THE-REPAIR` in my set, confirmed by hand: §7.1.
`ph75` is **DEAR** — the entry is right that "the failure injection is the row",
and it carries the sha problem in §7.8.

⛔ **No row in my twelve fails the C-side bar of §0.** All twelve are correct on
benign inputs, all twelve exhibit their error on an adversarial input, and all
twelve have a C mechanism that lifts at a declarable tier. **There is no kill
here and I am not offering one.**

---

## §6 ⭐⭐ THE RANKING, AND WHICH FAMILY I WOULD ENTER FIRST

### My three families, best first

| # | family | the ONE sentence a build-task author needs |
|---|---|---|
| **1** | **E2** (via **`ph66`**) | *Lift `zend_hash_del_key_or_index` verbatim with its nine correctly-written siblings from the same file, drive it from an insert/delete key stream, and fold the surviving keys into the `u64`: the defect deletes the wrong element silently, the R1h is a one-hunk 2006 commit whose pre-image is 5.0.0's exact two lines, and the collision constant is `H("x"+NUL) = 5863869` (`.temp/php54A/ph66_preimage.py`).* |
| **2** | **E4** (via **`ph76`**) | *Model a struct holding one **embedded** container and one **heap** container plus an operation stream carrying an "embedded?" bit, and a splice that destroys-and-frees "the container" without asking which kind it has — the R1h is `1d33a3e95e4e`'s `array.c` hunks only, and **the manager must first rule on §C's "R1h is a subset of its fix commit", because two of that commit's five files use symbols 5.0.0 does not have**.* |
| **3** | **E3** (via **`ph69`**) | *Lift the `PREG_PATTERN_ORDER` tail — write one boxed value into a named slot and then into the next integer slot with no increment between — fold `(refcount, payload)` per slot plus `(allocs, frees)`, and backport the literal one-line `ZVAL_ADDREF(match_sets[i])` as R1h; the trigger is `preg_match_all` (not `preg_match`) with a named subpattern.* |

### ▶ WHICH FAMILY WOULD I ENTER FIRST? **E2, on `ph66`.**

Four reasons, each checkable above:

1. **It is the only row in my twelve that owes the manager nothing.**
   `1 id → 1 commit`; no limb choice; no R1h-subset question; no sha problem.
2. **Its R1h is the cleanest artefact I read in twelve patches** — one file, one
   hunk, 4+/2−, the deleted lines byte-identical to the cited ones, a commit
   message that names the harm.
3. **The harm is a pure checksum divergence.** No garbage determinism, no stack
   layout, no ASan dependence, no sanitizer blind spot to argue about — the
   thing `ph52` cost the programme (F105) and `ph55` cost it nothing.
4. **The one named unknown is now a constant**, computed and controlled in this
   task.

### ⭐ WHAT WOULD CHANGE MY MIND

* **A portfolio reason to want a *crashing* 11th row.** `ph66` produces a silent
  wrong answer. That is a **classification and never a kill** (`CLAUDE.md`
  rule 6; `p29` shipped it) — but if the manager wants the next row to abort
  hard, **`ph76` is the pick**, and it is not much dearer: deterministic abort,
  `crashes_pristine_5_0_0 = True`, upstream `.phpt`, a free three-site census.
  **My ranking flips E2↔E4 on that preference alone.**
* **A permissive ruling on §C's R1h-subset question.** If the manager rules
  that a fix whose extra hunks are *provably inexpressible* in 5.0.0 backports
  as a subset, `ph76` loses its only named cost and becomes as cheap as `ph66`
  **and** brings a hard crash and a census. Then E4 goes first.
* **A measurement of the allocation order I did not take.** I predicted
  `zend_hash`'s bucket allocator makes a `ph66` kernel O(n)-per-call from the C.
  I did not build one. If a kernel can be written at O(1) (a fixed bucket arena
  would be a `divergences` entry, not a free lunch), `ph66` gets cheaper still;
  if the O(n) label turns out to cost more on a `zend_hash` kernel than I priced,
  `ph68` — one subsystem, no HashTable — becomes E2's row instead of `ph66`.
* **Nothing on the Rust, Verus or ladder side.** No such consideration entered
  this ranking, and none may (`CLAUDE.md` rule 6).

---

## §7 ⭐ WHAT THE PATCH BYTES SAID THAT NO LABEL SAID

**Three of my rows have a `fix_commit` that does not repair their defect, and
the screen calls all three `CANDIDATE`.** That is §3.2(c)'s warning firing three
times in twelve rows.

### 7.1 ⛔ `ph74` — the only `NOT-THE-REPAIR`, and it is worse than the label

`9a98904ddd0e` (2006-07-21) — its pre-image at `zend_read_property` is:

```c
	MAKE_STD_ZVAL(property);
	ZVAL_STRINGL(property, name, name_length, 1);
	value = Z_OBJ_HT_P(object)->read_property(object, property, silent TSRMLS_CC);
	zval_ptr_dtor(&property);
```

5.0.0 (`zend_API.c:1957, :1965-1966`) is:

```c
	zval property, *value;
	...
	ZVAL_STRINGL(&property, name, name_length, 0);
	value = Z_OBJ_HT_P(object)->read_property(object, &property, silent TSRMLS_CC);
```

▶ **By 2006 the tree had already replaced the stack `zval property` with
`MAKE_STD_ZVAL`, flipped `dup` from `0` to `1` — which is `ph74`'s ENTIRE
mechanism — and added the matching `zval_ptr_dtor`.** What the commit itself
changes is `silent` → `silent?BP_VAR_IS:BP_VAR_R`, exactly its subject line
("wrong `type` argument to `read_property()`"). **It repairs a different defect.**
▶ `ph74` has **NO KNOWN R1h**, its one id is exhausted, and finding one costs a
bisect over 2004-07 … 2006-07. **BLOCKED-ON-A-DECISION: accept no R1h, or pay
for the bisect.**

### 7.2 ⛔ `ph67` — the "fix" is a **PURE REFACTOR**, and which limb you pick decides whether an R1h exists

`c3a317117ad8` (2014-03-20), *"Add helper function for updating bucket
contents"*, 32+/40−, one file. It extracts three copies of the update body into
`zend_hash_bucket_update()`. **The destructor is still called while the bucket
is linked and still advertises `p->pData`, and `UPDATE_DATA` still follows it.**
The moved text is:

```c
+	if (ht->pDestructor) {
+		ht->pDestructor(p->pData);
+	}
+	UPDATE_DATA(ht, p, pData, nDataSize);
```

— i.e. **`ph67`'s defect survives this commit unchanged.** (Its pre-image is not
5.0.0's either: the condition had already been flattened and given an
`p->arKey == arKey` fast path and a `ZEND_ASSERT`.) The screen says `CANDIDATE`
because those three lines *appear* — as moved text, not repaired text.

✅ **The other limb DOES have a real R1h.** `e88cdaa0143a` (2012-10-18, 2 files,
**one added line**) puts `Z_TYPE_P(zvalue) = IS_NULL;` **before**
`zend_hash_destroy` in `_zval_dtor_func`'s `IS_ARRAY` arm — and its pre-image
(`if (zvalue->value.ht && (zvalue->value.ht != &EG(symbol_table))) { zend_hash_destroy(…); FREE_HASHTABLE(…); }`)
is **byte-identical to 5.0.0's `zend_variables.c:51-54`**.

▶ **The decision the manager owes `ph67` is not a tier, it is a limb** — and the
entry's ⚠ line frames it as a tier question only.

### 7.3 ⛔ `ph72` — the fix repairs a **different variable in the same function**

`37d7df72a62e` (2012-03-02), bug #52719, has **six hunks in `array.c` and every
one is about `userdata`** — `zval **userdata` → `zval *userdata`,
`Z_ADDREF_PP` → `Z_ADDREF_P`, three `zval_ptr_dtor(userdata)` → `(&userdata)`.
The only `key` in the whole patch is the context line `args[1] = &key;`.

▶ **Nothing touches `zval *key;`'s declaration or the unconditional
`zval_ptr_dtor(&key)` — which is the defect the entry cites AND the one the
corpus's own `c_file_line` cites** (`ext/standard/array.c:1061 (the
unconditional …`). `ph72`'s R1h for its cited defect is **unfound**. ⚠ I did not
establish whether the `key` defect was still present in the 2012 tree (§8).

### 7.4 ✅ `ph68` — better than its summary: the fix adds **exactly the missing guard**

`d7b30e457a3d` (2007-05-18), 2 files (1 code + 1 `.phpt`), two hunks, 8 added
lines. Its pre-image at the first hunk —

```c
 		if (fci->object_pp) {
 			/* TBI!! new object handlers */
 			if (Z_TYPE_PP(fci->object_pp) == IS_OBJECT) {
 				if (!IS_ZEND_STD_OBJECT(**fci->object_pp)) {
```

— is **byte-identical to 5.0.0's `:617-620`**, and what it inserts is
`!EG(objects_store).object_buckets[Z_OBJ_HANDLE_PP(…)].valid → return FAILURE`:
**verbatim the guard the entry says is missing.** It also patches a second
`object_pp` path in the same function — a small, free census. And I confirmed
`IS_ZEND_STD_OBJECT` (`zend_object_handlers.h:137`) checks the *handler table*,
never the store's `valid` flag, so the entry's claim holds.

### 7.5 ✅ `ph71` — a **zero-net-line MOVE**, byte-exact, with upstream's test

`4f161fe28997` (2005-09-01, bug #34137) — **⚠ not in the cache; I FETCHED it**
into `.temp/php54A/patches/`. It moves the six lines

```c
		variable_ptr->refcount--;
		if (variable_ptr->refcount==0) {
			zendi_zval_dtor(*variable_ptr);
			FREE_ZVAL(variable_ptr);
		}
```

from **before** `if (!PZVAL_IS_REF(value_ptr))` to **after**
`*variable_ptr_ptr = value_ptr; value_ptr->refcount++;`. **Both the removed and
the added regions' contexts are byte-identical to 5.0.0's `:233-242` and
`:255-259`**; only the function signature in the `@@` context differs (5.0.0
carries `znode *result` and `temp_variable *Ts`, which the body never touches).
Upstream's `.phpt` gives a working trigger:
`$arr1 = array('a1' => array('alfa'=>'ok')); $arr1 =& $arr1['a1'];`

▶ The task file's `2005 · 3f · same` and the "4 ids → 4 commits" flag both make
`ph71` look worse than it is. The 4→4 is real, **but §C resolves it**: the
catalogue's cited span is CRASH-004's site (`c_file_line = Zend/zend_execute.c:242`),
so R1h is this commit, and the other three ids are sibling evidence — two of
which the screen can say nothing about (`INAPPLICABLE`).

### 7.6 ⚠ `ph73` — the best R1h *shape* in my set, with a named gap

`235e6c0afe1d` (Andi Gutmans, **2004-12-17**, **1 file, 4+/5−**) turns
`zval method_name, method_args;` into two `ALLOC_ZVAL`s and the two `zval_dtor`s
into `zval_ptr_dtor`s. **Its two deleted teardown lines are 5.0.0's `:587-588`
byte-for-byte.** But its pre-image declaration is `zval method_name, method_args;`
while 5.0.0 has **three** names — `zval method_name, method_args, __call_name;`
— plus `args`, `call_args[2]`, `i`, `call_result`. So the 2004 HEAD and the
5.0.0 branch had already diverged in this function.
▶ **Backported, the upstream fix hoists two of 5.0.0's three stack zvals and
leaves `__call_name` on the stack.** That is `PROTOCOL_PHP.md` §C's *"an upstream
fix is not automatically correct … that is a result, and one of the strongest a
row can carry"*. ⚠ **Plausible, not settled**: `__call_name` is passed as the
*function name*, not as an argument, so whether userland can retain it is a
question I did not answer (§8).
ⓘ And `FIXSURVEY_001.md:56-63` already records the mapping that makes
`235e6c0afe1d` the right R1h, so `ph73`'s `5 ids → 5 commits` costs far less
than it looks.

### 7.7 ⚠ `ph65` — the R1h is a 45-hunk commit against a rewritten unserializer

`1ac4d8f2c632` (2013-07-29) has **~45 hunks across `var_unserializer.c` AND
`var_unserializer.re`** — the generated file and its re2c source, which must be
kept in sync. Its pre-image already has `(*var_hashx)->last` and a
`var_push_dtor()`; **5.0.0 has neither** (`var_push` walks `var_hashx->first`,
`:35-56`, and there is no `var_push_dtor`). ▶ A real R1h exists but backporting
it is a task in itself. Combined with the `modelled` tier, `ph65` is the **most
expensive row in E2** and I rank it last there.

### 7.8 ⛔⛔ A DEFECT IN THE R1h EVIDENCE BASE ITSELF — **3 of 163 cached patches are under the wrong sha**

Found while reading `ph75`'s fix. `.temp/mgr/batch/patches/ed4c0245c7ca.patch`
begins `From 9dfa843a386b65b18353c510f032e322004d0bb7`. I swept the whole cache:

```
for p in *.patch; do  compare ${p%.patch} against `head -1 $p`  done
  MISMATCH 49bd45a2c175 -> bc9f2fb8dfadc1dba4264695ded28f673c54dc75     (ph79, agent B)
  MISMATCH abb09693ac4d -> 6a6c273893178bb9b59c117e31761fe0193d0c9f     (ph78, agent B)
  MISMATCH ed4c0245c7ca -> 9dfa843a386b65b18353c510f032e322004d0bb7     (ph75, MINE)
  total 163 cached, 3 mismatched
```

**Reproduced LIVE, so it is not a stale cache** — I re-fetched all three and each
returns **HTTP 200** from `github.com/php/php-src/commit/<sha>.patch` with a
`From:` header naming a *different* sha. (Most plausibly these are cherry-picked
branch commits and the API serves the equivalent object; **that is a hypothesis
and I did not confirm it** — §8.)

⚠ **`fixsurvey.py:168-172` validates only that the file starts with `b"From "`.
It never checks the sha.** So these three records' `same-file?` verdicts, and
`preimage_screen.py`'s verdicts on them, are computed from a patch that is not
the named commit. That is `TASK_PHP_012` M1's shape — *a checker that accepts
the artefact it is checking* — for the fifth time by F49's count.

ⓘ For `ph75` the *substance* is fine: the served patch plainly is the fix for
bug #68365 and it is a **one-line move** hoisting `zvalue->value.ht = tmp_ht;`
above `zend_hash_copy` — the exact repair the entry names, on defect lines
byte-identical to 5.0.0's `:151-152`. **But the sha a `spec.md` would pin is not
the sha of the patch anyone has read**, and that must be settled before `ph75`
is built.

---

## §8 ⭐ WHAT I AM UNSURE OF — named, not omitted

1. **I ran no PHP and executed no trigger.** Every verification here is a read of
   the pristine C, the corpus CSV, and patch bytes. Where I say "verified", I
   mean *verified by reading the C to the cited site* — §3.2(b)'s sense — not
   *executed*.
2. **`ph72`'s R1h.** I proved all six hunks of `37d7df72a62e` are about
   `userdata`. I did **not** establish whether the `key` defect was still present
   in the 2012 tree, and I did not find the commit that fixed it. "`ph72` has no
   known R1h" is a statement about *this* commit, not a proof that none exists.
3. **`ph73`'s backport gap.** That `235e6c0afe1d` leaves `__call_name` on the
   stack is read off the diff. Whether `__call_name` is *retainable* by userland
   (it is the function-name zval, not an argument) I did not determine. **The
   gap is real; whether it is exploitable is unverified.**
4. **`ph76`'s `array_pad` site.** Verified by reading `:2528-2530` + `:2556-2558`
   + `zend_variables.c:146-147`. **Not run.** The `do_pad` and
   `num_pads > 1048576` guards are satisfiable but I did not execute it.
5. **All `§B1a` allocation-order statements are predictions from the C**, not
   measurements. I built no kernel and counted no allocations.
6. **`ph65`'s fix.** I read the hunk headers (45 of them) and two hunks, not all
   of it. "The 2013 tree is substantially rewritten" rests on `var_push`'s
   signature and `var_push_dtor`'s existence, which is solid; the *size* of the
   backport is an estimate.
7. **The 3-sha mismatch cause.** Reproduced and its consequences are certain;
   the *reason* GitHub serves a different sha (cherry-pick vs branch alias) is a
   hypothesis I did not confirm.
8. **Patches I did not read** (**21 of the 34 records in my set**; I read 13):
   `630f9c33c236` (ph65), `ce23692663fe` `b8360c376b5d` (ph68),
   `41ae8de13666` `90f4590d87fe` `72c6d5cbafc9` (ph70),
   `b599e434add` `44325e647302` `8ce349b8e03c` (ph71),
   `09370413757a` `4c0970bec69b` (ph72),
   `3d7b0bab28e7` `d2018ef2c035` `30f4d3f9593d` `5d804d163ae9` (ph73),
   `99bf19c177e2` `40b8105cca1f` `c009a4f361fd` (ph75),
   `2a31dbbadfb9` `c447acf8632d` `96d755978cc8` (ph76).
   ⚠ **Given that 3 of the 13 I DID read turned out not to repair their defect,
   the unread ones should not be assumed sound.**
9. **`ph70` and `ph75` were not deep-verified**, only line-checked. Their
   `▸ trigger` lines are untested by me.
10. **My depth did not run out.** Every §5 deliverable is complete. Points 1–9
    are the boundary of what I chose to verify inside it, and I am naming them
    rather than letting the confident sentences stand alone.

---

## §9 SCORING THE MANAGER'S THREE REGISTERED PREDICTIONS

### P1 — "at least ONE of ph87, ph60, ph85, **ph66**, ph37 fails deep verification"

**Only `ph66` is in my scope, and it PASSES — comprehensively.**

* Cited lines `:464-465`: **byte-exact**, comment included.
* Trigger: **verified to the cited site in the C**, through three call paths.
* R1h: **1 id → 1 commit**, 1 file, 1 hunk, **pre-image byte-exact**.
* The entry's one named unknown: **computed, with a selfcheck and two controls.**
* Sibling census: **1 defect against 9 correct instances in the same file.**

▶ **P1 gets NO support from my scope.** ⚠ **But the phenomenon P1 is about is
alive at 3 of 12 in my set** — `ph67`, `ph72` and `ph74` all carry a
`fix_commit` that does not repair their defect, and `ph74`'s is the `ph32`
failure exactly (a commit whose *shape* is perfect). **P1 named the wrong rows,
not the wrong worry.**

### P2 — "row 11 is a TEMPORAL row"

Not mine to adjudicate (agent C is the control). From the E-side I can say:
**`ph66` is genuinely cheap on every axis I measured**, and **`ph68` and `ph76`
are close behind**, so **P2 is well-supported from my three families** and does
not rest on the mechanical shape alone. If an `S`/`T` family beats `ph66` on
agent C's evidence, nothing in my report contradicts that.

### P3 — "`▸ trigger` lines fail on roughly a third of rows deep-verified"

| deep check | verdict |
|---|---|
| **`ph66`** | ✅ **VERIFIED** — reaches the cited site; three call paths traced; concrete instance computed |
| **`ph69`** | ⚠ **VERIFIED WITH A CORRECTION** — reaches the cited site **only** under `preg_match_all` (`global = 1`) with the default `PREG_PATTERN_ORDER`; the sentence "any pattern with a named subpattern" also covers `preg_match`, where the block is unreachable. The **observable harm** needs one further step the sentence omits |
| **`ph76`** | ✅ **VERIFIED** — `array_splice($GLOBALS,0,1)` reaches `:2059-2060`; `first_arg_force_ref` at `basic_functions.c:767`; `Z_ARRVAL_P(array) == &EG(symbol_table)` from `zend_globals.h:169` + `zend_execute_API.c:153`; corroborated by `crashes_pristine_5_0_0 = True` and upstream's `.phpt` |

**0 of 3 WRONG · 1 of 3 needs a correction.**
▶ **Count it both ways and let the pooling decide**: at "needs a correction = a
failure" my rate is **1/3 = 33 %**, which **matches** F46/F49's 3-of-9; at
"WRONG only" it is **0/3**, which does not. My `ph69` correction is of the same
kind as F46's `ph29` note (the site is right, the stated approach reaches it only
under a condition the line omits) rather than F49's `ph98` (cannot be set up at
all).

ⓘ Two further triggers checked in passing, not deep: **`ph72`** —
`array_walk_recursive` does exist in 5.0.0 (`array.c:1106`,
`basic_functions.c:746`) and the two arms are as the entry describes, so the
trigger is sound; **`ph71`** — upstream's own `.phpt` uses
`$arr1 = array('a1'=>array('alfa'=>'ok')); $arr1 =& $arr1['a1'];`, the same shape
as the entry's `$a = array(1); $a = &$a[0];`.

---

## §10 CATALOGUE DEFECTS FOUND

⭐ First, the good news, because it is the larger fact: **I checked all 58
`file:line` citations across the twelve entries against the pristine tarball and
EVERY ONE RESOLVES** — most to the exact line, a few to a span containing it.
**Zero defect sites were wrong**, which is F46's 0-of-19 holding at 0-of-12 on
twelve rows nobody had checked. Three are unusually careful and deserve saying so:

* **`ph72`'s parenthetical is right and useful**: *"⚠ the span ends at the
  while-loop's brace; `php_array_walk` closes at `:1066`"* — `:1063` is the
  `while`'s brace and `:1066` is the function's. Exactly so.
* **`ph73` names five sites in four files and all five are byte-exact**:
  `:524`, `zend_execute.c:1138`, `zend_execute_API.c:881`, `zend_objects.c:34`,
  `streamsfuncs.c:728`.
* **`ph71`'s CRASH-003 triple is exact to the line** — `:629
  zendi_zval_dtor(*variable_ptr);`, `:634 safe_free_zval_ptr(variable_ptr);`,
  `:669 (*variable_ptr_ptr)->is_ref=0;` — a three-line citation in a
  4451-line file, all three right.

Now the defects.

1. **⛔ `ph67`'s cited `fix_commit` is a pure refactor, and the entry does not
   say so** (§7.2). Its ⚠ line frames the row's risk as a *tier* question; the
   real risk is that one of its two limbs **has no repair at all**.
2. **⛔ `ph72`'s cited `fix_commit` repairs a different variable** in the same
   function (§7.3). The entry cites it without qualification.
3. **⛔ `ph74`'s only `fix_commit` had already been overtaken** — the defect was
   gone from the tree before that commit (§7.1). The screen flags it; **the entry
   does not.**
4. **`ph76` under-names its own census.** Its `fix_commit` patches **three**
   sites in `ext/standard/array.c` and the entry names one:
   **`array.c:1982-1984` (`array_unshift`)** and **`array.c:2556-2558`
   (`array_pad`)** are uncatalogued. `array_pad`'s is reachable by **composing
   the row's two named mechanisms** (§4d). F58 already scored `ph76` at 2
   siblings; this reproduces that count from the patch bytes and locates both.
5. **Six ids whose site the row's entry never names** — a build task choosing an
   R1h under §C needs this mapping and must currently go to `index.csv` for it:
   `ph68`/CRASH-045 `zend_objects_API.c:144` and CRASH-044 `:54`;
   `ph71`/CRASH-025 `zend_execute.c:2243-2245` and CRASH-067 `:2243`;
   `ph75`/LOGIC-026 `zend_execute.c:3414`;
   `ph76`/CRASH-026 `zend_execute.c:371`.
   ⓘ **This may be deliberate** under §0.4's ~80–110-word micro-schema. Reported
   as a fact about what the entry does and does not carry, not as an error.
6. **`ph65`'s "a flat back-reference table"** is a **chained list of 1024-slot
   `var_entries` blocks** (`var_unserializer.c:29-56`), not flat. Immaterial —
   the row's own ⚠ line already narrows it to "a growable table" — but a builder
   reading "flat" will size the wrong structure.
7. **`ph69`'s `▸ trigger` under-specifies** (§3b): it needs `preg_match_all`
   (not `preg_match`) and, for the *harm*, retention across the array's
   destruction.
8. **⛔⛔ Not a catalogue defect but a TOOL one, and it touches this task's own
   method: 3 of 163 cached patches are stored under a sha the file does not
   carry**, `fixsurvey.py` cannot see it, and one of the three (`ed4c0245c7ca`,
   `ph75`) is in my set — the other two (`ph78`, `ph79`) are **agent B's**
   (§7.8). **I have not told agent B; the manager reconciles.**

---

## §11 EVIDENCE — what is in `.temp/php54A/`

| file | what |
|---|---|
| `NOTES.md` | the one-line `tar` command that re-derives every extracted `.c`, and what was deleted |
| `ph66_preimage.py` + `.log` | the DJBX33A construction, both directions, selfcheck **PASS**, 2 controls |
| `dump_fixsurvey.py` | per-ID walk of `fixsurvey.json`, because `fixsurvey.py`'s stdout truncates the spread list at 12 |
| `fixsurvey_myrows.log` | `ids → commits` for all 12 rows, with per-record sha/date/files/verdict |
| `fixsurvey_offline.log` | the full `--offline` run |
| `preimage_myrows.log` | `preimage_screen.py --row phNN --verbose` for all 12 |
| `corpus_ids.log` | `c_file_line` / `fix_commit` / `crashes_pristine_5_0_0` / `cwe` for all 34 ids in my set |
| `patches/` | `4f161fe28997.patch` (**fetched**, absent from the cache) and the three re-fetches for §7.8 |

⛔ The extracted `.c` blobs are **deleted** per `CLAUDE.md` "Don't" rule 1 — they
are re-derivable from the tarball by the command in `NOTES.md`.
