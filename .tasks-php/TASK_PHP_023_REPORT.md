# TASK_PHP_023 — REPORT · review the nine new rows, then land them

**Role:** research **reviewer**, alone. **Scope obeyed:** the only files written
are this report, `patterns-php/CATALOGUE.md` (via `land_019_020.py --apply`, as
tasked) and `.temp/php23/`. No `.memory-php/`, no `RECAP_PHP.md`, no
`PROTOCOL_PHP.md`/`PLAN_PHP.md`, nothing under `harness/`, `common/`,
`patterns/`, `results/`, `pilot/`, no `patterns-php/ph07-strcut-cursor/`, no
`.web/`. No `git add`, no `git commit`. `grep -a` / `/usr/bin/grep` / Python
throughout. `git status` at close: `M patterns-php/CATALOGUE.md`, nothing else.

---

# §0 ⚠⚠⚠ TWO SENTENCES IN THE LANDED TEXT ARE MEASURED FALSE. FIX BEFORE THE COMMIT.

**The nine rows are ADMISSIBLE and the landing is applied** (§3). But two of the
45 anchors carry claims I have refuted with re-runnable measurements, and
**`PROTOCOL.md` rule 4 says corrections a report asks for get landed before the
commit, not after.** Both are one paragraph. Exact replacement text: §5.

| # | where | the claim | status |
|---|---|---|---|
| **B1** | `ph94` Part B, `▸ trigger` + `⚠⚠ risk` | *"on THIS BOX IT PRODUCES NO OUT-OF-BOUNDS READ … the wild read is a codegen accident, not a property of the C"* | ⚠⚠⚠ **REFUTED.** The padding is never written at all; `TASK_PHP_021`'s probe was reading **its own `memset`**, which PHP does not do. With a faithful zval the read is **WILD at `-O0`, `-O1`, `-O2` and `-O3`** |
| **B2** | `ph32` Part B, `⚠⚠ risk` + `R1h` | *"All three are repaired by ONE commit — `56adfe1f3cf1` — which is why they are one row"*, and *"R1h = `56adfe1f3cf1` + `85afcb802dc1`"* | ⚠⚠⚠ **REFUTED.** `56adfe1f3cf1` repairs **one** of the three. `ent_uni_spacing` and `ent_uni_8592_9002` were already `ok` **two months earlier**, at `b9ff04703f16` (2005-01-11) |

⚠ **Neither refutation removes a row.** B1 makes `ph94` **stronger** — it
restores the mechanism `TASK_PHP_019` originally claimed and `TASK_PHP_021`
withdrew. B2 is inside an *existing* row's risk text; `ent_uni_spacing` and
`ent_uni_8592_9002` are in **no corpus row**, so no `phNN` is added or removed —
but the row's **R1h is wrong for two of the three tables it now claims**, which
`PLAN_PHP.md` §4.4 and `PROTOCOL_PHP.md` §F5(iii) make a build-blocking error.

---

# §1 Why this exists — and what the stop actually bought

`TASK_PHP_021` stopped the landing on a trigger-failure count. **The stop was
right and its stated reason was not the reason** (§4.2). What the extra task
bought is exactly what task §1 said was missing — *"NOBODY HAS REVIEWED the nine
rows"* — and it bought two refutations that no trigger count could have found,
one of them of `TASK_PHP_021`'s own headline measurement.

---

# §2 The review — all nine rows

## 2.0 Method, stated before the verdicts so it can be attacked

Every `file:line` below was opened in the **pinned tarball** (sha256
`5783e0c0…d6919`, re-verified this run by `.temp/php23/extract.sh`) with
`.temp/php23/cite.py`, which **prints `FAIL` and exits non-zero** on a missing
file or a past-EOF span rather than printing nothing. **≈70 line citations
across 15 files** were opened, including every one `TASK_PHP_019` called
*correct* — task §2.3's instruction, and F21/F37's rule.

⚠⚠ **The bar applied is C-side only.** No row was graded on Rust, Verus, Miri,
cost, ladder shape or mechanism *quality*. Duplication with `patterns/` was not
considered at all. **Nothing below is a kill and I removed no row.**

## 2.1 Verdicts

| row | citations | does the C support the admission? | **verdict** |
|---|---|---|---|
| `ph94` V5C-173 | ✅ 9/9 exact | ✅ **and stronger than the landed text says** (§2.2) | **ADMIT** |
| `ph95` V5C-015 | ✅ 8/8 exact | ✅ the `:214` guard-defeat is real and `ph22` provably cannot reach `:212` | **ADMIT** |
| `ph96` CRASH-061 | ✅ 6/6 exact | ✅ `:873` returns SUCCESS unconditionally with `EG(exception)` set | **ADMIT** |
| `ph97` CRASH-126 | ✅ 6/6 exact | ✅ `min_num_args = 0`, write loop runs zero times, `typ` keeps `NULL` | **ADMIT** |
| `ph98` CRASH-163 | ✅ 8/8 exact | ✅ save/clear at `:1074-1075`, fault on the tested FAILURE branch | **ADMIT** (⚠ one rider, §2.5) |
| `ph99` LOGIC-003 | ✅ 9/9 exact | ✅ `:1279 incdec_op(z)` with **no** separator; the sibling separates at `:1220` | **ADMIT** |
| `ph100` LOGIC-008 | ✅ 7/7 exact | ✅ **and stronger**: `zend_execute_API.c:450 INIT_PZVAL(p)` clears `is_ref` even when `SEPARATE_ZVAL` no-ops | **ADMIT** |
| `ph101` LOGIC-018 | ✅ 6/6 exact | ✅ `:1900`'s destroy-then-realias, with `:1891-1897` the live trap | **ADMIT** |
| `ph102` CRASH-090 | ✅ 4/4 exact | ✅ **independently re-derived from the patch bytes** (§2.6) | **ADMIT** |

**All nine clear the bar. I would overturn none of `TASK_PHP_019`'s nine
reversals.** The two defects in §0 are in *prose about codegen and upstream
history* — the two kinds of claim in this batch that are **not** C-reading, and
they are where 100 % of the failures are.

## 2.2 ⭐ `ph94` — task §2.4's starred question, and the answer is the opposite of `_021`'s

> *"`_021` measured that gcc narrows the 16-byte return through `mov %esi,%eax`
> at every `-O` level, zeroing the padding the row is about … If that is right,
> is `ph94` still admissible at all, and on what?"*

**It is not right.** `TASK_PHP_021` §2.1's probe
(`.temp/php21/ph94_probe2.c`) opens each trial with

```c
zval arg;
memset(&arg, 0, sizeof arg);            /* labelled "zend_API.c:692" */
arg.type = 5 /* IS_OBJECT */;
arg.value.obj = zend_objects_new(&obj, (void *)1);   /* zend_API.c:710 */
```

⚠⚠ **There is no such `memset` in PHP, and `zend_API.c:692` is the function's
signature line, not a statement.** ✅ Verified at source: the zval reaches
`_object_and_properties_init` from `zend_execute.c:3245 ALLOC_ZVAL(...)` —
i.e. `emalloc`, contents unspecified — and `:3246 object_init_ex(...)` is the
very next statement. `zend_API.c:708` writes only `arg->type`. **Nothing zeroes
`value`.** So probe2 could not distinguish *"the store wrote a zeroed high
half"* from *"the store never touched the padding and I am reading my own
`memset`"*.

**`.temp/php23/ph94_probe3.c` is probe2 with the `memset` replaced by a 0xAA
poison and the zval taken from `malloc` — nothing else changed.** All four
optimisation levels, gcc 13.3.0 (`.temp/php23/ph94_probe3.log`):

```
t0 handle=1 padding=0xaaaaaaaa lval=-6148914694099828735  :4033 guard PASSED -> s[lval] WILD
...
padding ever non-zero = YES  -> the struct assignment is MEMBER-WISE
wild read observed    = YES
```

**And the disassembly settles the mechanism**, `-O0`, the store at
`zend_API.c:710`:

```
call   <zend_objects_new>
mov    %eax,%ecx          ; handle
mov    %rdx,%rax          ; handlers
mov    %ecx,(%rbx)        ; 4 BYTES at offset 0
mov    %rax,0x8(%rbx)     ; 8 bytes at offset 8
```

⚠⚠⚠ **Bytes 4–7 are never written.** `_021`'s `mov %esi,%eax` is in the
*callee's* return sequence and is irrelevant, because **the caller never stores
RAX's high half into the zval at all.** `lval` is `handle | (residue << 32)`,
`offset->value.lval <= Z_STRLEN_PP(container)` is trivially true for a negative
`long`, and `:4033` reads at a wild displacement.

**Consequences, and they run in three directions:**

1. ✅ **`ph94`'s original claim is restored.** *"The index is uninitialised
   memory, not a program value"* is **true**, and the corpus's own valgrind
   *"Use of uninitialised value of size 8"* at `:4033` with a SEGV is now
   **corroborated** rather than contradicted.
2. ⚠ **The landed `▸ trigger` and `⚠⚠ risk` are false and must be replaced**
   (§5, B1). The risk line's *"even a producer that genuinely never writes those
   4 bytes does not deliver garbage on this toolchain"* is **exactly backwards**:
   a producer that never writes them delivers exactly the residue.
3. ⭐ **Taking the padding from the blob is still the right build advice — for a
   different reason.** Not *"because a faithful producer gives you zeros"*
   (false) but *"because a faithful producer gives you whatever `emalloc` left,
   which is not reproducible and not measurable"*. That is a `projection` in
   `PROTOCOL_PHP.md` §A2's sense — *"a behaviour outside the extracted span
   modelled by a narrower one"* — and it must be **declared in the divergence
   ledger with that `kind`**, not slipped in as a convenience. So: a faithful
   extraction, provided it is declared as a projection. ⚠ **And the row must
   then say what stops it becoming `ph11`**: the blob supplies the *padding*,
   the tag stream still decides whether the payload is read as an index at all;
   if a kernel lets the blob choose the index directly it has rebuilt `ph11`.

⚠ **What this does NOT establish.** One toolchain, one allocator. `0xAA` is as
arbitrary as `_021`'s zeros — the load-bearing result is not *"the padding is
0xAA"* but ✅ **"the padding is never written"**, which the disassembly shows
directly and which is toolchain-independent for a member-wise struct copy.

## 2.3 `ph98` and `ph101` — the other two corrected triggers

**`ph98` — the correction is right and I could not break it.** Every link
verifies: `zend_builtin_functions.c:1038` does refuse a non-callable at
registration; `:1060-1061`'s `zval_copy_ctor` on an array copies the
`HashTable` and shares element zvals; `zend_execute_API.c:678-680` returns
FAILURE on a non-`IS_STRING` `function_name`; `zend.c:1074-1075` clears the
global and `:1083` reads it back; `zend_exceptions.c:519`'s first statement is
`Z_OBJCE_P(exception)` → `zend_API.c:204 Z_OBJ_HT_P(NULL)`. ✅ **Clean.**

**`ph101` — the correction is right, and I checked the arithmetic it turns on.**
`:1891-1897` raises `E_COMPILE_ERROR` only when *both* defaults are non-NULL, so
`class B extends A { public static $x; }` (child NULL) reaches `:1899`; `:1990`'s
`zend_hash_merge(..., inherit_static_prop, ...)` has already set `is_ref = 1` on
the parent's zval, so `B::$x = "W"` writes through the alias and `A::get()`
returns `"W"`. The second clause (`class C { protected static $y; }` /
`class D extends C { public static $y = "CHILDVAL"; }` → NULL) is the mirror
case and also holds. ✅ **Clean**, and the `⚠ zend_hash_update`'s
destroy-then-replace is load-bearing* rider the landing added is correct.

## 2.4 Attacking the two "kill stands" verdicts (task §2.3: check what it called correct)

- **`LOGIC-014` → `ph48` (EXACT).** ✅ Upheld, and **more strongly than
  `TASK_PHP_019` argued.** The report says the two macros agree *"in the defect
  case"*. Expanded against `zend.h:568-577` and `zend_execute_API.c:608-610`
  they agree in **every** case: `is_ref==1` → both no-op; `is_ref==0` → both
  separate-if-shared and set the flag. There is no input that separates them.
  ⚠ **The one attack that has some force**, and I record it as a rule problem
  rather than a row problem: under test (b) the *attacker-controlled quantity*
  is a by-value **function argument on `EG(argument_stack)`** at `:1420` and a
  **callable-array element** at `:608-610`. Whether that is "the same quantity"
  is a question about how coarsely you are allowed to describe it — see §4.3.
- **`CRASH-037` → `ph39` (EXACT).** ✅ Upheld. `:338`/`:339` and `:551` verify;
  `Z_ARRVAL_P` → `HashTable*` vs `Z_STRVAL_P` → `char*` on an attacker-chosen
  `long` is the only difference.
- **`CRASH-101` → `ph41` (target corrected).** ✅ Upheld. `:917`'s `"ra"` really
  does type-check the container, `:816`/`:817` really do pass the unchecked
  element, `:775` really does read it as a `HashTable*`, and `:778` really does
  apply the identical test one level down. `ph41`'s pre-existing *"Do not fold
  into ph39"* line was right and `C.1` had ignored it.

## 2.5 Riders found on the way (none is a kill; none blocks the landing)

1. ⚠ **`ph98`'s corrected trigger has an unstated dependence on an
   uninitialised union member — the same defect class as `ph94`, at a third
   site.** `zend_builtin_functions.c:1054` is
   `if (Z_STRLEN_PP(exception_handler)==0) { … unset the handler; RETURN_TRUE; }`
   — and for the trigger's `array($o,'m')` that reads `value.str.len` at offset
   8 of a zval whose `_array_init` (`zend_API.c:644-651`) writes only
   `value.ht` (offset 0–7) and `type`. **If the residue is 0 the handler is
   silently never stored and the trigger no-ops.** A build task should know.
2. ⚠ **A citation off by one, landed.** `ph32`'s new block says
   *"(`int j, k;` at `:877`)"*. `html.c:877` is `int retlen;`; `int j, k;` is
   **`:878`**. This is inside `TASK_PHP_019`'s *"Citations: 13/13 resolve …
   No `F23` repeat"* claim, so that claim is **13/13 minus one** — F23's exact
   shape, once more, in the sentence denying it.
3. ⚠ `ph32`'s new block cites the spacing run as *"one miscounted run
   (`:132-133`)"*; `:132-133` are the twenty `NULL`s and the marker
   `/* 711 - 731 */` is at **`:131`**. Cosmetic.
4. ✅ `ph100` is **understated**: `zend_execute_API.c:450 INIT_PZVAL(p)` clears
   `is_ref` and `:451` restores only `refcount`, so the binding is broken even
   on the path where `SEPARATE_ZVAL` no-ops. Additive; the row is right as
   landed.
5. ✅ **`TASK_PHP_020`'s additive one-liners spot-checked 4/4**: `php_url_parse`
   has no `_ex` spelling in the tarball; `zend_llist.c` is **317** lines;
   `php_array_walk` opens at `:993` and closes at **`:1066`**; `exif.c:3004` is
   `NumDirEntries = php_ifd_get16u(dir_start, …)`.

## 2.6 ⚠⚠⚠ `ph32` / `ph102` — the `html.c` split, re-derived from the patch bytes

**`ph102`'s admission SURVIVES the attack and is now on firmer evidence than
`TASK_PHP_019` had.** But the same paragraph's account of `ph32` is false, and
the two facts come from one measurement.

`TASK_PHP_019` §10.5 rests `ph32`-vs-`ph102` on its rule's second disjunct, and
asserts (§10.3, §10.5, §10.6) that `56adfe1f3cf1` (2005-03-09, bug #28067)
repairs **all three** of `ent_uni_338_402`, `ent_uni_spacing` and
`ent_uni_8592_9002`. It quotes, as proof, a `56adfe1f3cf1` hunk

```diff
-	/* 711 - 731 */   ...20 NULLs...   /* 732 */   "tilde",
+	/* 711 - 730 */   ...20 NULLs...   /* 731 - 732 */   NULL, "tilde"
```

⚠⚠⚠ **That hunk is not in `56adfe1f3cf1`.** The patch is 113 lines and its
`html.c` diff is five hunks: the file-header URL, `ent_uni_338_402`,
`ent_uni_greek`'s two *name* typos, and three content hunks in
`ent_uni_8592_9002`. **`ent_uni_spacing` appears once, as trailing context.**
✅ Checked against `.temp/php19/patches/56adfe1f3cf1.patch`, whose sha256 I
re-fetched and matched (`bb9e3dc7…fa47`) — the artefact is authentic; the
reading of it was wrong.

**The real chain, measured with the C compiler at each commit**
(`.temp/php19/entcount.py`; log: `.temp/php23/entcount-by-commit.log`;
re-fetch: `.temp/php23/refetch.sh`):

| `ext/standard/html.c` at | `338_402` | `spacing` | `punct` | `8592_9002` |
|---|---|---|---|---|
| **php-5.0.0** | 63/65 | 22/23 | 66/67 | 410/411 |
| php-5.0.3 (2004-12-15) | 63/65 | 22/23 | ok | 410/411 |
| **`b9ff04703f16` (2005-01-11)** | **63/65** | **ok** | ok | **ok** |
| `d74acc15ccdf` (2005-03-06) | 63/65 | ok | ok | ok |
| **`56adfe1f3cf1` (2005-03-09)** | **41/65** | ok | ok | ok |
| `bd07142b9128` (2005-03-10) | 41/65 | ok | ok | ok |
| php-5.0.4 | 41/65 | ok | ok | ok |
| php-5.0.5 | ok | ok | ok | ok |

**So the 5.0.0 shortfalls are removed by four different commits, not one:**

| table | the commit that removes the **5.0.0** shortfall |
|---|---|
| `ent_uni_punct` | `35e43dabe16b`/`46bc2c5ae2ae`, 2004-07-19, bug #29199 — **punct only** |
| `ent_uni_8592_9002` | **`52adad71e750`**, 2005-01-11 (the `8840…9002` tail rewrite) |
| `ent_uni_spacing` | **`52adad71e750`** (range `732`→`731`) then **`b9ff04703f16`** (the `NULL`, range restored) |
| `ent_uni_338_402` | `56adfe1f3cf1`, 2005-03-09 — **and broken to 41 in the same hunk**; restored by `85afcb802dc1`, 2005-05-11 |

⚠ **Completeness**: the GitHub API listing of `ext/standard/html.c` on branch
`PHP-5.0` for 2004-12-01…2005-05-20 returns **9 commits**; I fetched and read
all of them. `cf68478f8e43`, `d74acc15ccdf`, `0f8e76468579` and
`feb4c902225f` touch no `ent_uni_*` table. **There is no other candidate.**

**What this does and does not change:**

- ✅ **`ph102` stands, and its argument improves.** At `b9ff04703f16`, `punct`
  is `ok` while `338_402` is still `63/65` — so *"two upstream fixes, neither
  repairing the other"* is now measured **at a commit** rather than inferred
  from tags, and `56adfe1f3cf1` genuinely does not touch `ent_uni_punct`
  (verified: context line only).
- ❌ **`ph32`'s *"all three … which is why they are one row"* is false**, and so
  is the reason the three are merged. Under `TASK_PHP_019`'s **own** second
  disjunct the three tables have **two** distinct upstream fixes and would
  split. **No `phNN` moves** — `spacing` and `8592_9002` are in no corpus row —
  but the block must stop citing a shared fix it does not have.
- ❌ **`ph32`'s R1h is wrong for two of its three tables.** `R1h =
  `56adfe1f3cf1` + `85afcb802dc1`` repairs `ent_uni_338_402` (= CRASH-089, the
  row's only corpus id) and leaves `spacing` and `8592_9002` short. A build that
  takes the block at its word ships an R1h that is *still defective on two of
  the tables the same block says the row covers* — `PROTOCOL_PHP.md` §F5(iii),
  *"confirm against the release tags that this commit removes YOUR defect"*,
  precisely.
- ⭐ **The §10.4 finding it was in service of is UNHARMED and is the best thing
  in `TASK_PHP_019`**: `56adfe1f3cf1` really does leave `/* 376 (0x0178)`
  unterminated, the array really does compile to **41**, `bd07142b9128` really
  does silence GCC while keeping the defect, and php-5.0.4 really does ship at
  41 with no diagnostic. ✅ All four re-measured above. *A defect made invisible
  by the commit that fixed its warning* survives intact.

---

# §3 The landing — APPLIED, and verified

```
$ python3 .tasks-php/land_019_020.py --check
rows in Part A before: 93
  (45 anchors: 40 replacements + 5 insertions, every one at occurrences: 1)
rows in Part A after : 102   Part B blocks after: 102
--check only, nothing written. All anchors resolve exactly once.

$ python3 .tasks-php/land_019_020.py --apply --to .temp/php23/CATALOGUE.after.md
applied                                    # scratch copy first

$ python3 .tasks-php/land_019_020.py --apply
applied to /home/apt/repos_common/sec-ladder/patterns-php/CATALOGUE.md

$ diff .temp/php23/CATALOGUE.after.md patterns-php/CATALOGUE.md
                                           # identical to the verified scratch copy
$ python3 .tasks-php/land_019_020.py --check
⚠ REFUSED — 26 anchor(s) did not resolve exactly once     # re-application refused ✅
```

**Task §3's verification list, item by item:**

| asked | measured |
|---|---|
| 102 rows in Part A **and** 102 blocks in Part B | ✅ `102` / `102`, no duplicate id, no Part A row without a Part B block |
| the three section headings sum to 102 | ✅ `Spatial (42)` + `Type / initialisation (29)` + `Temporal (31)` = **102**, and heading == section membership == axis cell for all three. `ph92`/`ph93` moved out of `Temporal` into `Spatial` as designed |
| `coverage.py` still **166/166** | ✅ `accounted for : 166 / 166`, `MISSING : 0`. `Part A distinct corpus ids` 163 → **167** (the four Part-C-only `LOGIC` ids becoming Part A ids), the three known non-corpus `merged_members` ids still flagged, the three known double-claims (`CRASH-153`, `LOGIC-011`, `LOGIC-022`) unchanged |
| every withdrawn `C.1` kill still present, in place, marked | ✅ **8** `KILL(S) WITHDRAWN` markers in `C.1`, each quoting its original note **in full**, struck through, with its new row. **Nothing was deleted**, including `CRASH-090`, which `TASK_PHP_019` §10.6 had proposed to delete |
| say what `coverage.py` prints | ⚠ `catalogue rows in Part A : 99  (ids ph01..ph91, gaps: none)` and `Part B blocks : 99` — **F49 exactly as predicted**. Its `166/166` path is unaffected. ✅ **Not repaired** (task instruction); `C.7` now pastes the true `102`/`102` with `⚠ coverage.py prints 99; see below` beside it and a paragraph explaining why the `gaps:` set cannot report its own blindness |

Logs: `.temp/php23/coverage_before.log`, `.temp/php23/coverage_after.log`.

**⚠ What I did NOT hold, and why.** Task §3 permits holding a row. I held none:
**all nine admissions clear §2**, and the two defects in §0 are in prose, not in
an admission. Holding `ph94` alone is also not mechanically available —
`B-ph94` is an *insertion*, so skipping it leaves `ph94` in Part A with no Part B
block and the script (correctly) refuses the whole landing. The choice was
binary: land all 45 anchors or none. **I landed, and §0/§5 is the disclosure.**
⚠ If the manager would rather have had the stop, that is a fair criticism of this
call and I say so; the deciding argument was that not landing leaves
`TASK_PHP_021`'s refuted measurement standing with **no** correction recorded
anywhere in the tree.

---

# §4 The three things the manager asked to have attacked

## 4.1 Is nine rows a reviewable unit? — **Yes for admission; no for the derived claims**

✅ **The C-side admission test is cheap once the tarball is open**: 5–10 minutes
a row, and it is the same motion every time — open both sites, name the
unchecked predicate, the attacker quantity and the primitive. All nine fit
comfortably in one task and I would not split it.

⚠ **What does not fit is everything that is not a C read.** Both §0 defects, and
every minute I spent finding them, are in the two claims that leave the tarball:
a **codegen** claim (`ph94`) and an **upstream-history** claim (`ph32`). Those
cost ~60 % of this task between them, they need a compiler and a network, and
they are exactly where `TASK_PHP_019` and `TASK_PHP_021` each put their headline
result. ⭐ **The reusable rule: batch the C-side reviews, but price a codegen or
fix-archaeology claim as its own unit of work, because it is not a reading and
it fails differently.**

## 4.2 ⚠⚠ Should `ph101` have counted as a failed trigger? — **The stop was right. The rule that fired was wrong.**

**On the narrow question: no, `ph101` should not have been scored a failure —
and it does not matter, because `ph94` alone should have stopped the landing.**

`ph101`'s trigger *fires*: it reaches `:1899-1900`, it aliases the slots, the
harm occurs. What is wrong is the **witness** — clause 1 needs an accessor
because `A::$x` is `protected`, clause 2 names an undeclared `class C`. Neither
is a claim about the C, and `TASK_PHP_021` says so itself. Under its own bar
(*"could an engineer run it and see the stated harm?"*) the verdict is
defensible; under the question the stop condition was **for** (*"does this batch
need a review cycle?"*) it is noise, and `_021` disclosed exactly that.

⚠⚠ **The real defect is that the stop condition counts heterogeneous things.**
The three "failures" were:

| row | what was wrong | material to admission? |
|---|---|---|
| `ph94` | the row is about something **other than what it says** | ⚠⚠⚠ **yes** — and, as it turns out, the *correction* was the error |
| `ph98` | the trigger **cannot be set up** — the engine refuses it | ⚠ yes, an engineer loses an hour |
| `ph101` | the **witness** is incomplete; the harm happens | ❌ no, a one-line fix |

**A rule keyed on the count fires on three typos and stays silent on one
`ph94`.** It is over-powered in one direction and under-powered in the other.
⭐ **Recalibration, and it costs nothing: stop on KIND, not on COUNT — *if any
correction changes what the row CLAIMS, stop, even if it is the only one*.**
Under that rule `ph94` stops the batch on its own, `ph101` never enters the
count, and the stop happens for the reason that was actually true.

⚠ **And one more thing the count could not see: `TASK_PHP_021` had already
folded all three corrected triggers into the landing script's text**, so at the
moment the rule fired there was nothing left to correct. **The stop bought a
review, not a repair** — which is what task §1 says was missing, and which is
why the stop was right on the merits and wrong in its stated reason.

## 4.3 ⚠⚠ Attacking the `EXACT` / `SLIGHT VARIATION` / `DIFFERENT MECHANISM` rule

> **EXACT** ⇔ the two sites agree on (a) the unchecked predicate, (b) the
> attacker-controlled quantity, (c) the fault primitive.
> **SLIGHT VARIATION** ⇔ exactly one differs → §3.1 admits it.
> **DIFFERENT MECHANISM** ⇔ two or more differ, **or** the two defects have
> different upstream fixes each of which leaves the other standing.

**1. ⚠ It has three names and two outcomes.** §3.1 admits a slight variation, so
`SLIGHT VARIATION` and `DIFFERENT MECHANISM` produce **the same result**: a new
row. The rule is binary — *kill* iff all three match — and the three-valued
presentation makes it look more discriminating than it is. It also invites an
argument that cannot change anything: `TASK_PHP_019` graded `CRASH-061` and
`V5C-015` as `SLIGHT VARIATION` *"at the minimum the evidence carries"*, a
distinction with no consequence. ✅ **The half that is real is the burden**: kill
only on a proof of *same*. That is the correct inversion of the corpus's
`merged_members` predicate and §3 of that report demolishes the old citation
properly.

**2. ⚠⚠ (a)(b)(c) have no stated level of abstraction, so the verdict is a
function of the description, not of the C.** Any pair can be made `EXACT` by
describing coarsely and `DIFFERENT` by describing finely. The report knows this
— §7 concedes the rule returns **both answers** on `CRASH-090` — and resolves it
not from the rule but from an external *"consistency with how the catalogue
already reads"* argument. Worked examples from this batch:

- (c) as *"an OOB read"* → `ph102` merges into `ph32`; as *"an OOB read past
  `ent_uni_punct`"* → it does not.
- (b) for `LOGIC-014` vs `ph48` is *"a by-value argument on
  `EG(argument_stack)`"* vs *"a callable array's element 0"* — different at one
  zoom, *"a live by-value zval the caller still holds"* at the next.
- `ph94` vs `ph11`: (c) as *"an OOB read of a string"* merges them; as *"a read
  at an index taken from an unspecified union member"* does not.

**This is not fatal — it is what makes the rule a checklist and not a decision
procedure. It must be quoted as one.**

**3. ⚠⚠⚠ The second disjunct is the weakest part and it is the one that decided
the hardest case — and it just failed a measurement.** *"Different upstream
fixes, each leaving the other standing"* is **not a C-side test**. It is:

- **contingent** — on what a maintainer happened to notice, and in what batch;
- **often counterfactual** — §10.5 admits *"one direction is counterfactual"*
  for `punct`, because it was already fixed;
- ⚠⚠ **easy to get wrong, and it was got wrong here.** `.memory-php/02-ladder.md`
  already warns that the `fix_commit` column *"names **a** fix for the row's
  function, NOT necessarily the one that removes the 5.0.0 defect"*. §2.6 is
  that warning firing on a hand-bisected chain: **the disjunct fired correctly
  for `ph102` and incorrectly for `ph32`'s three tables, in the same
  paragraph.**
- ⚠ **and it is asymmetric in a way the rule does not say.** A *distinct* fix is
  decent evidence of a distinct defect. A *shared* fix is very weak evidence of
  a shared mechanism — one commit routinely repairs unrelated errors in one
  file: `56adfe1f3cf1` fixes `ent_uni_338_402`'s **count** and, in the same
  patch, two pure **name** typos in a correctly-sized table.
  **Absence of a distinguishing fix is not presence of a shared mechanism** —
  and that is precisely the inference the `ph32` block made.
- ⚠ **It is silent on a large part of the corpus.** `PROTOCOL_PHP.md` §F5:
  `ph36` has no sha at all, 17 rows are `fixed-by-rewrite`, 31 % of fixes are
  2010 or later. For those pairs the disjunct cannot fire in either direction.

⭐ **Recommended restatement, and it keeps everything that worked:**

> **One test, one burden: *can I show these are the SAME?*** — (a) unchecked
> predicate, (b) attacker-controlled quantity, (c) fault primitive, **each
> described at the level the catalogue already uses**, stated in the note so it
> can be attacked. **A distinct upstream fix is admitted as evidence for
> DIFFERENT. A shared upstream fix is NOT evidence for SAME** — and any
> fix-commit claim must be verified at the commit, not at the column
> (`PROTOCOL_PHP.md` §F5(iii)).

⚠ **And the manager's own use of it survives, for a reason the rule states
badly.** `CRASH-090` → `ph102` is **right** — I re-derived it from the patch
bytes and from `entcount.py` at `b9ff04703f16` — but *"the rule got the answer
right"* and *"the rule is sound"* are different claims, and the same disjunct in
the same section produced §0's B2.

---

# §5 The two corrections — exact replacement text

⚠ **I do not edit these in** (the reviewer reports; it does not fix). Both are
single-paragraph replacements. ⚠ **They need to go into `CATALOGUE.md`
*and* into `land_019_020.py`'s corresponding anchor**, or the script's text
stays a cited artefact carrying a refuted claim.

## B1 — `ph94`, Part B: replace the `▸ trigger` line and the `⚠⚠ risk` line

**Replace**

```
▸ trigger: `$s = "abcdefgh"; $o = new stdClass; empty($s[$o]);` — ⚠⚠ **this REACHES `:4033` but on THIS BOX IT PRODUCES NO OUT-OF-BOUNDS READ.** ✅ Measured (`.temp/php21/ph94_probe2.c`, `zend_objects.c:93-104` and `zend_API.c:708-710` replicated statement for statement): gcc 13.3.0 returns the 16-byte `zend_object_value` in `RAX:RDX` and narrows through `mov %esi,%eax`, **zeroing the padding at `-O0`, `-O1`, `-O2` and `-O3`**, so `lval == handle` (1, 2, 3 …) and `:4033` indexes **inside** the string. What the trigger does demonstrate is the type confusion and an 8-byte read of a 4-byte-initialised member — which the corpus's own valgrind run reports as *"Use of uninitialised value of size 8"* at `:4033`. **The wild read is a codegen accident, not a property of the C** (`TASK_PHP_021` §2).
```

**with**

```
▸ trigger: `$s = "abcdefgh"; $o = new stdClass; empty($s[$o]);` — ✅ **Measured, and it DOES read out of bounds** (`.temp/php23/ph94_probe3.c`, gcc 13.3.0, identical at `-O0`, `-O1`, `-O2`, `-O3`): with the zval taken from the allocator the way `zend_execute.c:3245 ALLOC_ZVAL` really takes it, `lval` is `handle | (residue << 32)`, the guard `offset->value.lval <= Z_STRLEN_PP(container)` is trivially true for a negative `long`, and `:4033` reads at a wild displacement. **The `-O0` disassembly of `zend_API.c:710` is the mechanism**: `mov %ecx,(%rbx)` writes the 4-byte handle and `mov %rax,0x8(%rbx)` the handlers — **bytes 4–7 are never written by anything.** ⚠⚠ **`TASK_PHP_021` §2.1 reported the opposite** (*"no out-of-bounds read at any `-O`"*); its probe opened each trial with a `memset(&arg, 0, sizeof arg)` labelled `zend_API.c:692`, and **PHP does no such memset** — `:692` is the function's signature and `zend_API.c:708` writes only `arg->type`. It was reading its own zeroes. Retracted at `TASK_PHP_023` §2.2. The corpus's valgrind *"Use of uninitialised value of size 8"* at `:4033` is corroborated, not contradicted.
```

**Replace**

```
⚠⚠ risk: **the kernel must take the un-written half from the BLOB, not from a real `zend_objects_new`** — the measurement above is the reason, and it is stronger than *"a memset'd model deletes the mechanism"*: even a producer that genuinely never writes those 4 bytes does not deliver garbage on this toolchain. **Criterion 2 must therefore be discharged against the blob-driven kernel, and the row must report what the faithful producer does.**
```

**with**

```
⚠⚠ risk: **the kernel must take the un-written half from the BLOB** — not because a faithful producer gives zeros (it does not; §2.2) but because it gives whatever `emalloc` left, which is neither reproducible nor measurable. ⚠ **Declare it in the divergence ledger as `kind: projection`** (`PROTOCOL_PHP.md` §A2) — *"a behaviour outside the extracted span modelled by a narrower one"* — and never as a convenience. ⚠⚠ **And say what stops the row becoming ph11**: the blob supplies the **padding**, while the `(tag, payload)` stream still decides whether the payload is read as an index at all. A kernel that lets the blob choose the index directly has rebuilt ph11. **Criterion 2 is discharged against the blob-driven kernel, with the faithful producer's behaviour reported beside it.**
```

## B2 — `ph32`, Part B: replace the `⚠⚠ risk` paragraph and the `R1h` paragraph

**Replace** (from *"All three are repaired by ONE commit"* to the end of the
`R1h` paragraph) **with**

```
⚠⚠ risk: **the corpus records ONE short table for this row; there are THREE.** ✅ Measured with the C compiler (`.temp/php19/entcount.py`, `sizeof/sizeof[0]` over all 24 map rows) and re-measured independently (`.temp/mgr165/count_ent.py`, comment-aware, 17 tables · 4 short · 0 unevaluated): `ent_uni_338_402` **63 for 65**, `ent_uni_spacing` **22 for 23**, `ent_uni_8592_9002` **410 for 411**. **A build fixing only CRASH-089 is still defective on two tables.** ⚠ The *kinds* differ and the mechanism does not: two miscounted NULL runs (`:115-117`, `:121-123`), one miscounted run (marker at `:131`, NULLs at `:132-133`), and a compensating drift that nets to −1 (`crarr`, index 36). ⚠ Index citation: `int j, k;` is at `:878`, not `:877`.
⚠⚠⚠ **THE THREE TABLES DO NOT SHARE A FIX, AND AN EARLIER VERSION OF THIS BLOCK SAID THEY DID.** ✅ Measured at the commit (`.temp/php23/entcount-by-commit.log`, `refetch.sh`): at **`b9ff04703f16` (2005-01-11)** `ent_uni_spacing` and `ent_uni_8592_9002` are **already `ok`** while `ent_uni_338_402` is still **63 for 65**. `ent_uni_8592_9002` is repaired by **`52adad71e750`** (2005-01-11, the `8840…9002` tail rewrite); `ent_uni_spacing` by `52adad71e750` (range `732`→`731`) and then properly by **`b9ff04703f16`**; **`56adfe1f3cf1` (2005-03-09, bug #28067) touches neither** — its five `html.c` hunks are the file header, `ent_uni_338_402`, two *name* typos in `ent_uni_greek`, and three count-neutral hunks in `ent_uni_8592_9002`. All nine PHP-5.0 commits touching this file between 5.0.3 and 5.0.4 were fetched and read. **They are one row because the operation is one operation, NOT because the fix is one fix** (`TASK_PHP_023` §2.6).
⚠⚠ **R1h, AND IT IS FOUR COMMITS, NOT TWO.** For **CRASH-089 / `ent_uni_338_402`** — the row's only corpus id — R1h is `56adfe1f3cf1` **+ `85afcb802dc1`**, and ⭐ **the first one is invisibly incomplete**: it rewrites the table to the correct 65-element layout **and leaves `/* 376 (0x0178)` unterminated in the same hunk**, so it compiles to **41**; `bd07142b9128` (2005-03-10) then *"fixes the `/*`-within-comment warning"* by closing the comment **after** the swallowed block — **silencing GCC while keeping the defect**, which is how php-5.0.4 shipped at 41 with no diagnostic (✅ measured). Only `85afcb802dc1` / `bd2e99ee50ed` (2005-05-11, bug #29119) un-swallows the 24. ⚠ **If the row is built over all three tables its R1h must ALSO carry `52adad71e750` + `b9ff04703f16`**, or two of the three stay short. **Stopping at `56adfe1f3cf1` passes every syntactic check and is wrong twice over** (`ph03`'s two-hunk finding, second instance; `TASK_PHP_019` §10.4 as corrected by `TASK_PHP_023` §2.6).
```

⚠ `ph102`'s block needs **no** change: its *"`56adfe1f3cf1` … does not touch
this one"* and *"still short at php-5.0.1, 5.0.2 and 5.0.3"* are both ✅ correct,
and `C.1`'s withdrawn-`CRASH-090` note is ✅ correct as landed.

---

# §6 Clean negatives — named attacks that did NOT land

`PROTOCOL.md` rule 6: these are worth as much as findings and stop the next
agent re-running them.

1. ✅ **`TASK_PHP_019` §3's demolition of *"merged by the corpus itself"* is
   sound.** All three `verdicts.json` quotes verify **verbatim** (*"distinct
   missing guards"*, *"keep :212 as the distinguishing member"*, *"genuinely two
   distinct source-level mistakes"*), and both `validation/REPORT.md` quotes
   verify verbatim (*"root-cause dedup, decided by reading the C defect, never
   the fix commit or crash frame"*; *"Dedup burden of proof was set on
   'distinct', not 'same'"*). This is the strongest section in that report.
2. ✅ **The `C.4` enumeration is exactly right.** Independently rebuilt from
   `index.csv`: **14** rows with `category == null-deref` / `cwe == CWE-476`,
   and they are precisely the 14 `TASK_PHP_019` §6 lists, with the same
   `c_file_line`s. **No hidden seventh set member.** The `CRASH-061` cell really
   does correct `:479` → `:513` in the corpus itself.
3. ✅ **`ph102`'s separation from `ph32` survived a deliberate attempt to break
   it** — and came back stronger (§2.6).
4. ✅ **`LOGIC-014` → `ph48` `EXACT` survived** an attack on the macro
   expansions; the two are behaviourally identical in **all** cases, not only in
   the defect case (§2.4).
5. ✅ **`ph22` really cannot reach `pack.c:212`** — `H` is in the *"always uses
   one arg"* arm at `:174-191`, which does a bare `currentarg++`. `ph95`'s
   distinctness holds at source.
6. ✅ **`SEPARATE_ZVAL` really is a no-op at `refcount == 1`** (`zend.h:558`),
   which is the single fact the `ph99`/`ph100`/`ph101` three-way split rests on.
7. ✅ **`TASK_PHP_020`'s additive one-liners spot-checked 4/4** (§2.5.5).
8. ❌ **I did not find a fourth trigger defect.** `ph95`, `ph96`, `ph97`, `ph99`,
   `ph100`, `ph102` all trace end to end at source exactly as landed.

---

# §7 What I am least sure of, and what this report does NOT establish

1. ⚠⚠ **The decision to apply rather than hold** (§3). I judged the unit to be
   *the admission*, and every admission clears. A manager who judges the unit to
   be *the landed text* would have held, and would be applying a defensible
   reading of §3's own bullet. **The two corrections in §5 must land before the
   commit either way**; if they do, the two readings converge.
2. ⚠⚠ **`ph94`'s refutation is one toolchain and one poison value.** The
   load-bearing half is *"bytes 4–7 are never written"*, which the disassembly
   shows directly and which follows from a member-wise struct copy on any
   conforming compiler. **The half I would not bet on is what `emalloc` actually
   leaves there in a real PHP run** — that is the shim's territory
   (`PLAN_PHP.md` §4.3) and it is a build-task measurement, not mine. It is
   entirely possible that in practice the residue is often zero and the row is
   flaky rather than reliable; **that would be a finding, not a kill.**
3. ⚠ **I did not run PHP.** Every verdict is source-reading against the pinned
   tarball plus one compiled probe and one disassembly. Where I say "reaches", I
   mean the control flow and the types permit it, traced line by line.
4. ⚠ **Criterion 2 is demonstrated for none of the nine** and none was expected;
   it is discharged at build, as for all 93 pre-existing rows.
5. ⚠ **I did not re-adjudicate the `inv/obl` or `echoes` labels.** They landed
   marked `†` derived, with the legend, exactly as task §2.5 asked — **not
   upgraded by fiat and not demanded of.** `TASK_PHP_021` §7's private doubt
   about `p48` on `ph94` is still unresolved and still not a filter.
6. ⚠ **`ph32`'s `ent_uni_8592_9002` shortfall is attributed to `52adad71e750`
   by elimination plus a count**, not by reading its tail rewrite element by
   element. The elimination is tight — nine commits in the window, all fetched,
   only two touch any `ent_uni_*` table — but it is elimination.
7. ⚠ **I did not verify `35e43dabe16b`'s existence on the `PHP-5.0` branch.**
   I verified `46bc2c5ae2ae` (the HEAD sha) from the patch bytes in
   `.temp/php19/patches/`, and its *punct-only* scope. The MFH pairing is
   `TASK_PHP_019` §10.4's rider and I inherited it.
8. ⚠ **I did not repair `coverage.py`** (task instruction) and did not touch
   `.temp/php11/`, `.temp/php19/`, `.temp/php20/` or `.temp/php21/`.
9. ⚠ **`.memory-php/00-corpus.md` still says the catalogue holds 93.** It is 102
   as of this landing. Manager-only; flagged, not edited — as `TASK_PHP_021`
   §6.3 also flagged.

---

# §8 Scratch — `.temp/php23/`

**Kept (generators and evidence):** `extract.sh`, `refetch.sh`, `cite.py`,
`NOTES.md`, `ph94_probe3.c` + `.log`, `entcount-by-commit.log`,
`coverage_before.log`, `coverage_after.log`, `patches/` (5 upstream commits).
**Deleted (re-derivable, every rebuild command in `NOTES.md`):** `src/`, the
eight fetched `html*.c` snapshots, `hist.json`, three tarball spot-check files,
three compiled binaries, and the two `CATALOGUE.*.md` scratch copies.

**Files written by this task, in total:** `.tasks-php/TASK_PHP_023_REPORT.md`,
`patterns-php/CATALOGUE.md` (by `land_019_020.py --apply`), and `.temp/php23/*`.
Nothing else.
