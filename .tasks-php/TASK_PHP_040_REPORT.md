# TASK_PHP_040 — REPORT · the R1h hunt for `ph52` and `ph53`, and the build brief for ROW 7

**Role:** research engineer, alone. **Bracket:** `66/0` and `14/0` first and last
(§8). **Scope:** one file changed outside `.temp/` — `.tasks-php/preimage_screen.py`
(§4, §3-sanctioned, in no digest; `git status` in §8).

---

## §0 THE ANSWER IN ONE TABLE

| | `ph52` · LOGIC-007 | `ph53` · CRASH-158 |
|---|---|---|
| corpus `fix_commit` | `7412202c43e7` (2006-05-11) | `be8daf1f47fa` (2008-03-12) |
| screen label | **`CANDIDATE`** (1/1 cited line in the pre-image) | **`NOT-THE-REPAIR`** (0/2) |
| §F5(iii) tag comparison | ✅ **CONFIRMS** — present at `php-5.1.6`, gone at `php-5.2.0` | ⛔ **REFUTES** — the cited line was already gone at `php-5.0.5`, **2 years 9 months before this commit** |
| **R1h verdict** | ⭐ **FOUND, at the corpus sha.** Delete `Zend/zend.c:243` | ⭐⭐ **FOUND, at a DIFFERENT sha: `d09cdd9f71f3`** (2005-06-08, *"Fixed valgrind errors"*). The corpus sha is **excluded**. |
| does the R1h `patch -p1` onto pristine 5.0.0? | ❌ **NO** — context drifted; R1h is a *hand* backport of one deleted line | ✅ **YES** — `Hunk #1 succeeded at 2568 (offset -14 lines)`, zero fuzz, exit 0 |
| does R1h remove the fault? | ✅ **completely** (the type byte is written after the switch, `zend.c:263`) | ⚠⚠ **NO — it makes it DETERMINISTIC.** `memset` turns a wild-pointer deref into a **NULL** deref; the consumers get no guard at 5.0.5 |
| R1h cost on the **benign** path | ⚠ **predicted 0.00 %** — it changes only an error arm the benign corpus never executes | ⭐ **an O(n) `memset` on every class declaration** — a real, attributable number |
| corpus fidelity anchor (§A4) | `crashes_pristine_5_0_0 = n/a (non-crash class)`, `uninit-read-silent` | `True`, `build = asan`, `wild-pointer-deref`, CWE-824 |

▶ **ROW 7 RECOMMENDATION: `ph53`.** §2 gives the reason and §5 the brief.
▶ **§3's third label `INAPPLICABLE-SAME-FILE` is LANDED** with six negatives,
`--selftest PASS`, corpus repartitioned **43 → 26 + 17**. **`ph53` does not
exercise it today and WOULD under a repair I found and did not land** (§4.3).

---

## §1 EXPECTATIONS, DECLARED BEFORE EITHER PATCH WAS FETCHED (§7.6)

Written to `.temp/php40/00-EXPECTATIONS-PRE-FETCH.md` **before** the first
`curl`; `.temp/php40/01-pre-fetch-state.log` records `patches/` empty at that
moment. Verbatim summary and the outcome:

| # | what I predicted | held? |
|---|---|---|
| 1 | `ph52` screen = `CANDIDATE`, confidence HIGH | ✅ |
| 2 | `ph52`'s repair is a **one-line deletion** and **complete**, because `expr_copy->type = IS_STRING` sits at `zend.c:263` *after* the switch — derived from the tarball, before fetching | ✅ **exactly.** 1 file, 1 deletion, nothing else |
| 3 | `ph52` §F5(iii) confirms | ✅ |
| 4 | *risk:* the 2006 tree may have restructured past the cited line (~20 %) | ❌ did not happen — but **the context HAD drifted**, which is why the patch does not apply (§0). I predicted the risk in the wrong place: the line survived, its neighbours did not |
| 5 | `ph53` screen = `NOT-THE-REPAIR`, **and probably the NON-DECISIVE kind** | ⚠ **HALF WRONG.** `NOT-THE-REPAIR` ✅, but it comes out `decisive=True` — and **that decisiveness is a FALSE POSITIVE** (§4.3). My instinct that the hunk is in a different function was **right**; the screen disagreed with me and the screen was wrong |
| 6 | `ph53` outcome 2 — the fusion **does not close the window** | ✅ **and for a reason better than mine**: there was no window left to close. It had been closed in 2005 |
| 7 | `ph53`'s R1h is `NOT FOUND`; the real repair is a 5.1-era restructuring; *"I will NOT go tag-bisecting for it"* | ❌ **WRONG, and I did.** The bisection cost four `curl`s and one API query and **found the commit** — `d09cdd9f71f3`. My "5.1-era" guess was also wrong: **5.0.5** |
| 8 | *named bias:* outcome 1 is the one I want, ~25 % | ✅ flagged in advance and it did **not** fire. The repair is *"zero the storage"*, not *"delete the second pass"* |
| 9 | `ph53` exercises the new label, `ph52` does not | ⚠ **not today** (§5 above); **yes** under the §4.3 repair |
| 10 | recommendation = `ph52` | ❌ **WRONG.** Both R1h survived, §7.2's tie-break applies, and two things I measured afterwards point the same way |

⭐ **The prediction that was worth writing down is #7**, because it is the one
the task file warned about from the other side: `NOT FOUND` is valued, and I was
ready to file it. The answer is better than `NOT FOUND`, and the reason is that
`preimage_screen.py` handed me an exclusion at 2008 and the tag walk handed me a
**bracket** — `php-5.0.4` has the line, `php-5.0.5` does not — and a one-release
bracket is a searchable interval.

---

## §2 THE TWO R1h, SETTLED

### 2.1 `ph52` — `7412202c43e7` · **CONFIRMED** · `CANDIDATE` · one line

`.temp/php40/patches/7412202c43e7.patch`, sha256
`32e8526ebfe684d9…`, 746 B, HTTP 200, **byte-identical to
`.temp/mgr/batch/patches/7412202c43e7.patch`** (the cache was already warm; I
fetched anyway and diffed — a free integrity check on the shared cache).

> Antony Dovgal, 2006-05-11, *"no need to destroy the zval here"* · **1 file, 1
> deletion, 0 insertions**, and the deleted line is
> `zval_dtor(expr_copy);` in `zend_make_printable_zval`.

**Screen:** `CANDIDATE`, `1/1 cited 5.0.0 lines are present in the pre-image of
Zend/zend.c`, `n_dropped = 0`, `patch_files = ['Zend/zend.c']`.
`zval_dtor(expr_copy)` occurs **exactly once** in the whole of 5.0.0's
`Zend/zend.c` (grepped `-a`), so the match is not an accident of a common line.

**§F5(iii), the tag comparison** (`.temp/php40/03-tagcheck.log`, refs fetched
from `raw.githubusercontent.com`, each blob's sha256 in the log):

| ref | `zval_dtor(expr_copy)` |
|---|---|
| `php-5.0.0` | **present** at `:243` |
| `7412202c43e7^` | **present** at `:251` |
| `7412202c43e7` | ⛔ **gone** |
| `php-5.1.6` (2006-08-24, **after** the commit) | ⚠ **STILL PRESENT** at `:256` |
| `php-5.2.0` | ⛔ gone |
| `php-5.2.1` | ⛔ gone |

▶ **The commit is the removal event, and it was never merged back to `PHP_5_1`**
— `php-5.1.6` ships three months later still carrying it. First release that
carries the fix: **`php-5.2.0`**; kept thereafter. **It removes the 5.0.0 defect
at the cited site: YES.**

⚠ **Two things the fetch showed that the corpus column does not, and the brief
would have to carry:**

1. **The patch does NOT apply to pristine 5.0.0** (`.temp/php40/13-backport-apply.log`:
   `Hunk #1 FAILED at 248`). By 2006 the guard had changed — 5.0.0 has
   `if (EG(exception)) {` above the line, the 2006 tree has an unconditional
   `zend_error(EG(exception) ? E_ERROR : E_RECOVERABLE_ERROR, …)`, and
   `empty_string` had become `STR_EMPTY_ALLOC()`. With `--fuzz=3 --batch` `patch`
   *reverse*-applies it, i.e. **the only line that matches is the `-` line
   itself**. So `kernel_hardened.c` would be a hand backport: delete one line.
   Defensible under §C (*"backported and sha-pinned"*), but it is a
   reconstruction and it owes an argument.
2. ⭐ **In the 2006 tree the defect is WIDER than in 5.0.0** — the arm runs on
   *any* failed `__toString`, not only on a pending exception. 5.0.0's defect is
   a **subset**, so the deletion removes it in both trees. That is a clean
   argument *for* the backport and it is worth stating rather than eliding.

### 2.2 `ph53` — the corpus sha is **REFUTED**, twice, independently

`.temp/php40/patches/be8daf1f47fa.patch`, sha256 `42190b44ad8068c3…`, 7397 B,
HTTP 200, byte-identical to the shared cache. Dmitry Stogov, 2008-03-12,
*"Optimized ZEND_FETCH_CLASS + ZEND_ADD_INTERFACE into single ZEND_ADD_INTERFACE
opcode"*, 4 files (`NEWS`, `zend_compile.c`, `zend_vm_def.h`, `zend_vm_execute.h`).

**(a) Screen:** `NOT-THE-REPAIR`. Neither cited line is in the pre-image of
`Zend/zend_compile.c`:

```
5.0.0 :2571  ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces, sizeof(zend_class_entry *)*ce->num_interfaces);
5.0.0 :1951  if (ce->interfaces[i] == entry) {
```

**(b) §F5(iii), the tag walk — and this is the decisive half.** The `erealloc`
line's *enclosing function* is tracked across seven refs
(`.temp/php40/03-tagcheck.log`, `04-narrow-5.0.x.log`):

| ref | `zend_do_end_class_declaration`'s interface block |
|---|---|
| `php-5.0.0` | `erealloc(ce->interfaces, …*ce->num_interfaces)` — **the defect** |
| `php-5.0.1` `5.0.2` `5.0.3` `php-5.0.4` | **defect present, unchanged** |
| ⭐ `php-5.0.5` | `emalloc(…)` **+ `memset(ce->interfaces, 0, …)`** — **repaired** |
| `php-5.1.0` | same as 5.0.5 |
| `php-5.2.0` | restructured again: `ce->interfaces = NULL; ce->num_interfaces = 0;`, and `zend_do_implement_interface` now grows the array **one slot at a time at runtime** (`erealloc(…, ++current_iface_num)`; `ce->interfaces[ce->num_interfaces++] = iface`) — **the invariant `num_interfaces == slots written` restored by construction** |
| `be8daf1f47fa^` | identical to 5.2.0's shape at these lines |
| `be8daf1f47fa` | changes only `opline->extended_value = CG(…)->num_interfaces++;` → `CG(…)->num_interfaces++;` |

▶ **The 2008 commit removes the compile-time index coupling, and by then there
was no window left to close.** §2's outcome list: this is **outcome 2** (*"it does
not close the window"*) reached **via outcome 3** (*"the screen excludes it"*), and
the task's outcome-1 prize — *"the upstream repair is 'delete the second pass'"* —
**does not apply to this commit.** It applies, loosely, to **`php-5.2.0`'s**
restructuring, which is not a single commit I have identified and is not R1h.

### 2.3 ⭐⭐ `ph53`'s REAL R1h: `d09cdd9f71f34deab4b99f4e63523fb94164a724`

Found by: the one-release bracket above → GitHub API,
`commits?sha=php-5.0.5&path=Zend/zend_compile.c&since=2005-03-25&until=2005-09-10`
→ 15 commits, of which `d09cdd9f71f3` 2005-06-08 Dmitry Stogov **"Fixed valgrind
errors"** is the only plausible subject for an uninitialised-read repair. Fetched:
`.temp/php40/patches/d09cdd9f71f3.patch`, sha256 `4f97b625fc9772d6…`, 1026 B,
HTTP 200. **1 file, 1 hunk, 2 insertions, 1 deletion:**

```diff
@@ -2582,7 +2582,8 @@ void zend_do_end_class_declaration(znode *class_token, znode *parent_token TSRML
 	/* Inherit interfaces */
 	if (ce->num_interfaces > 0) {
-		ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces, sizeof(zend_class_entry *)*ce->num_interfaces);
+		ce->interfaces = (zend_class_entry **) emalloc(sizeof(zend_class_entry *)*ce->num_interfaces);
+		memset(ce->interfaces, 0, sizeof(zend_class_entry *)*ce->num_interfaces);
 	}
```

**The three-part confirmation:**

- **(i)** not from the column — the column is refuted. Cited **as well as** the
  column, per §F5(iii)'s *"cite both and say which is which"*.
- **(ii)** fetched, above.
- **(iii)** **tag comparison:** the removed line is **byte-identical to 5.0.0's
  `:2571`**; present at `php-5.0.4`, absent at `php-5.0.5`; the commit is
  reachable from `php-5.0.5` (the API query was rooted at that tag). ✅
- **screen:** `CANDIDATE`, and the hit is on the **primary** cited line
  (`.temp/php40/12-screen-d09cdd9f.log`):
  `1/2 cited 5.0.0 lines are present in the pre-image`, hit = `:2571`, miss =
  `:1951` (the secondary compare-only read, in a different function, correctly
  not touched).
- ⭐⭐ **It applies mechanically to the citation base**:
  `patch -p1 --dry-run` on the pristine tarball's `Zend/zend_compile.c` →
  `Hunk #1 succeeded at 2568 (offset -14 lines)`, **zero fuzz, exit 0**
  (`.temp/php40/applytest.sh`, `13-backport-apply.log`). And `memset` is already
  used three times in 5.0.0's `zend_compile.c` (`:250`, `:2190`, `:2191`), so the
  backport needs no new include. **`kernel_hardened.c` is `git apply` + nothing.**

### 2.4 ⚠⚠ AND R1h DOES NOT REMOVE THE FAULT — IT MAKES IT DETERMINISTIC

Checked, because §C says an upstream fix is not automatically correct. At
`php-5.0.5` the **consumers are unchanged**:

- `Zend/zend_operators.c:1566-1567` (5.0.5) still reads
  `instanceof_function(instance_ce->interfaces[i], ce)` with **no NULL guard**,
  and `instanceof_function` at `:1585` is `return instanceof_function_ex(instance_ce, ce, 0)`
  → `NULL->num_interfaces` → **SEGV**.
- `Zend/zend_compile.c:1980` (5.0.5) still `if (ce->interfaces[i] == entry)` — a
  compare, which on NULL is **defined and correct**.

▶ **So the 2005 repair converts a CWE-824 indeterminate-pointer dereference into
a deterministic NULL dereference at the deref sink, and into a correct answer at
the compare-only sink. The same one-hunk fix lands at TWO different severities on
the row's two consumers.** ⭐ That is `PROTOCOL_PHP.md` §C's *"Report it; do not
repair it"* case, it is the strongest thing this row can carry, and **no built row
carries it.** It is also why §5's kernel ships **both** consumers.

### 2.5 ▶ THE RECOMMENDATION FOR ROW 7 — `ph53`, and it does not rest on the tie-break alone

§7.2's rule applies as written: **both R1h survive, so recommend `verbatim` over
`narrowed` → `ph53`.** ⚠ **But I do not want that to be the whole reason, because
I think both declared tiers are optimistic** (§5.1), and a recommendation resting
on a label I am about to dispute is not a recommendation. **Three things I
measured point the same way:**

1. ⭐ **`ph53`'s R1h applies mechanically to the citation base; `ph52`'s does
   not.** `kernel_hardened.c` for `ph53` is a `patch -p1`; for `ph52` it is a
   hand reconstruction that owes an argument (§2.1).
2. ⭐⭐ **`ph52`'s R1h is predicted to be a 0.00 % column.** It deletes a line on
   an arm the benign corpus never executes, so R1-vs-R1h has **nothing to
   measure** on the measured path. `ph53`'s R1h is an **O(n) `memset` on every
   benign class declaration** — an attributable cost, on a benchmark whose whole
   subject is the cost of safety. (Labelled: this is a **prediction**, §5.6.)
3. ⭐ **`ph53` has a fidelity anchor and `ph52` does not.** The corpus records
   `crashes_pristine_5_0_0 = True`, `build = asan`, `wild-pointer-deref` for
   CRASH-158; for LOGIC-007 it records `n/a (non-crash class)` and
   `uninit-read-silent`. §A4 asks the row to reproduce the **recorded** crash
   category — `ph53` has one to reproduce.

⛔ **This is NOT a kill on `ph52`, and nothing here refuses it.** Admission is
C-side only and `ph52` passes it: correct benignly, exhibits the target error
adversarially, and its C mechanism — *a tag-dispatched teardown over a tag byte
the caller never wrote* — is distinct from every built row's. It stays catalogued,
its R1h is now **settled and confirmed at the corpus sha** (which is a permanent
saving for whoever builds it), and ⭐ **its predicted 0.00 % R1h column is itself a
finding worth publishing**: *an upstream memory-safety fix that costs nothing
because it only shortens an error path.* It is the strongest fallback in the
family and it is now cheaper than it was this morning.

---

## §3 WHAT I SPOT-CHECKED IN THE TASK FILE'S §1 (rule 14)

The task file said I was not being asked to re-verify §1 and invited a report of
any discrepancy. I checked all of it against the pristine tarball
(`sha256 5783e0c0ba94f165633a…`, read with `tar -xzOf … | awk`, never an
extracted tree). **Every claim holds, verbatim, including the ones doing the most
work.** Specifically:

- `zend_compile.c:2571` erealloc, no zeroing ✅ · `:2591`
  `opline->extended_value = CG(active_class_entry)->num_interfaces++;` ✅ ·
  `:1951` compare bounded by `ce_num` ✅ · `zend_operators.c:1534-1535` loop to
  `num_interfaces` and deref ✅.
- `:3747 ce->num_interfaces = 0;` — ✅ **and `:3748 ce->interfaces = NULL;` right
  below it**, which the task file infers and does not quote. So
  `erealloc(NULL, n)` is a plain `malloc` and the **whole** array is
  indeterminate, exactly as §1 claims.
- `ph52`'s path condition ✅ — `:233` `get`-handler guard, `:234-238` the
  recursive call which **does** write `expr_copy` and `return`s at `:238`, so
  every path reaching `:243` leaves `expr_copy` unwritten.
- ⭐ **One thing §1 does not say and the brief needs**: `expr_copy->type = IS_STRING;`
  is at **`zend.c:263`, after the switch**. That is what makes `ph52`'s R1h a
  complete repair rather than a partial one, and I predicted the patch's shape
  from it before fetching (§1 #2).
- **Two corrections to `CATALOGUE.md`, both in the `▸` lines F46 already flagged
  as the unreliable part:**
  - `ph52`'s block cites `Zend/zend.c:242-247`; the **corpus** cell is
    `Zend/zend.c:243 (caller stack zval: Zend/zend_operators.c:1148)`. Not wrong,
    but the provenance block must use `:243` (or a span containing it) or
    `provenance.py`'s `c_lines` will not match the corpus citation.
  - ⛔ **`ph53`'s `▸ benign` line says `u64 = fold of the interface pointers
    read`. That cannot be the `u64`: it is address-dependent and will not
    reproduce across rungs or runs.** §5.5 replaces it.

---

## §4 §3's THIRD LABEL — `INAPPLICABLE-SAME-FILE` · LANDED WITH SIX NEGATIVES

### 4.1 What changed in `.tasks-php/preimage_screen.py`

sha256 after the edit: `97ee5bc53edfad9e32f99f4b3aa4551efe6c617241d09cd08c4005fc5a2b045e`.
**The file is in no digest** — `grep -arn 'preimage_screen' harness/*.py
harness-php/*.py common/*.py common-php/*.py` → 0 hits — so this costs no re-gate.

1. **The verdict branch.** `not hits and file_restrict and not decisive` →
   `INAPPLICABLE-SAME-FILE`, with a `why` that names `bracketed` and
   `same_function` and ends *"⛔ THIS IS NOT AN EXCLUSION"*. `NOT-THE-REPAIR` now
   means exactly *decisive exclusion*.
   ⚠ **Gated on `file_restrict` on purpose**: `--no-file-restrict` is N5's
   **control** and never computes `decisive` at all, so under that flag the old
   label stands and the control still measures one thing. N10f asserts it.
2. **The docstring.** `THREE OUTCOMES, NOT TWO` → `FOUR OUTCOMES, AND ONLY ONE OF
   THEM IS A PROOF`, **and `THE RULE`'s unqualified *"That is a PROOF OF
   EXCLUSION"* at line 18 is qualified in place** — F68 asked for that *"in the
   same edit"* and it is the sentence a reader meets first.
3. **The `.phpt` prohibition is written into the docstring**, with its measured
   53 %/46 %/45 % numbers, so the next reader who has the idea meets the
   refutation rather than re-running it (D11's own forbidden move).
4. **Reporting.** `main()` counts the new label, prints it in its own section
   headed *"⛔ NOT exclusions"*, and prints
   `⭐ CITE 26 EXCLUSIONS, NOT 43` so the figure F64/F68 kept getting wrong is
   emitted by the tool instead of remembered.
5. **Six header/arithmetic rots I created were repaired** (`PROTOCOL.md` rule 13):
   adding a fifth ground-truth record left N0/N5/N6/N9 saying *"four"* over
   five-element loops and N5 printing `{moved} of 4`. Now computed from
   `len(GROUND_TRUTH)`.

### 4.2 The negatives (§H) — `--selftest` **PASS**, `.temp/php40/10-selftest-FINAL.log`

| | | result |
|---|---|---|
| **§4 ground truth** | extended to **five** records spanning **all four** outcomes; the new one is `ph64 CRASH-086 562f886ecb14 → INAPPLICABLE-SAME-FILE`, which `TASK_PHP_031` §7.1 established **by hand before the label existed** | 5/5 ✅ |
| **N10a MUST-FIRE** | `ph64` must LEAVE `NOT-THE-REPAIR` — F68's confirmed false exclusion | ✅ `INAPPLICABLE-SAME-FILE`, `decisive=False` |
| **N10b MUST-NOT-FIRE** | `ph21 CRASH-107` must STAY `NOT-THE-REPAIR` (§H's own decisive case) | ✅ silent |
| **N10c MUST-NOT-FIRE** | `ph07 CRASH-124` must STAY `INAPPLICABLE` — the file- and function-granularity labels must not merge | ✅ silent |
| **N10d MUST-NOT-FIRE** | the three F38-corroborated MUST-NOT-EXCLUDE records stay `CANDIDATE` | ✅ ×3 |
| **N10e MUST-FIRE** | the **corpus-wide partition invariant**, not five records: `NOT-THE-REPAIR ⇒ decisive is True ∧ file touched`; `INAPPLICABLE-SAME-FILE ⇒ decisive is False ∧ file touched ∧ zero hits`; `INAPPLICABLE ⇒ file NOT touched`; **and the two must sum to the 43 the single label carried** — a refinement must **repartition**, not reclassify. Also fails if `isf == 0`, so the label cannot land unexercised | ✅ `170 records · 26 + 17 = 43 · CANDIDATE 106 · INAPPLICABLE 18`, **0 violations**, and 26/17 **is F68's own measured split** |
| **N10f MUST-NOT-FIRE** | zero records carry the new label under `--no-file-restrict` | ✅ `0` |
| **N1 strengthened** | the best constant answer now scores **2/5** (was 2/4 over three outcomes) | ✅ |
| **N2 WIDENED, deliberately, with the reason in a comment** | its assertion was `r1 == "NOT-THE-REPAIR"` and **my change would have broken it**: the bogus span `[[300,340]]` is `bracketed=False, same_function=False`, hence the new label. N2 tests *"the verdict is keyed on the cited text"*, so the assertion it wants is **"moved out of `CANDIDATE`"** | ✅ `CANDIDATE → INAPPLICABLE-SAME-FILE` |
| N0, N3, N4, N5, N6, N7, N8, N9 | unchanged, re-run | ✅ all |

⚠ **I found N2 by measuring the change's impact before making it**
(`.temp/php40/07-label-impact.log`), not by running the suite afterwards and
retuning it. The 17 records that move are **exactly** `TASK_PHP_031` §7.1's list
— `ph18 ph32 ph39×2 ph46 ph48 ph61 ph63×2 ph64 ph65 ph71 ph75 ph77×2 ph79 ph80`
— which is an independent reproduction of that census.

### 4.3 ⚠⚠ DOES EITHER OF MY ROWS EXERCISE IT? — and the answer exposed a defect in `same_function`

**`ph52`: no.** It is a `CANDIDATE` and never reaches the branch (N10d's class).

**`ph53`: NO TODAY — AND IT SHOULD.** It comes out `NOT-THE-REPAIR` with
`decisive=True`, and **that decisiveness is a false positive.**

> `same_function()` trusts the trailing text of `@@ -a,b +c,d @@ <ctx>` as *"the
> function this hunk is in"*. git's `xfuncname` picks `<ctx>` by scanning
> **backwards from the hunk's FIRST line**. `be8daf1f47fa`'s hunk header is
> `@@ -3261,35 +3261,25 @@ void zend_do_end_class_declaration(…)`, and measured in
> the commit's parent tree (fetched, sha256 `1dc76c81013f6067`):
> `zend_do_end_class_declaration` is **3215–3259**, `zend_do_implements_interface`
> is **3262–3293**, the hunk's pre-image is **3261–3295**, and **line 3261 is
> blank**. ▶ **The hunk contains ZERO lines of the function it is labelled with —
> not one context line — and all 16 of its removals are in the next function.**

So the screen printed *"the commit's window PROVABLY REACHES the site
(DECISIVE)"* about a hunk that never comes near it. **The conclusion was right and
the stated reason was not, and I only know the conclusion is right because the tag
walk in §2.2 settled it independently.** A false *promotion* of an exclusion to a
proof is the one direction this screen may not fail in.

**Measured, with negatives:** `.temp/php40/samefunc_probe.py`, `probe: PASS`,
`.temp/php40/06-samefunc-probe.log`. Text-only detector (the screen's own
constraint): *a hunk whose pre-image contains a function-definition header, with
zero removals before it and some after, is labelled with a function it does not
edit.*

| | |
|---|---|
| P1 MUST-FIRE | `ph53` flags: `crossed_into: void zend_do_implements_interface(…)`, `-before=0`, `-after=16` ✅ |
| P2 MUST-NOT-FIRE | `ph21 CRASH-107` — the sound case — silent ✅ |
| P3 MUST-NOT-FIRE ×2 | synthetic hunks either side of a boundary, both directions ✅ |
| **P4 REACH** | **25 records use `same_function`; 1 is flagged; it is `ph53`** — and its `decisive` rests on `same_function` **alone** (`bracketed=False`), so the flag has no second support |

▶ **So `NOT-THE-REPAIR` is 25 proofs plus one known misfiling, and under the
repair `ph53` becomes the 18th `INAPPLICABLE-SAME-FILE`** — which is the honest
thing for a text-only screen to say about a commit whose hunks are in a different
function. **That is the answer to §3's question: `ph53` exercises the third label,
and the reason it does not yet is a second defect one layer down.**

⛔ **I did NOT land the repair.** §6 scopes my validator edit to §3's label; the
fix moves a corpus-wide soundness flag and belongs to the manager. **The
recommended repair, one line of intent:** require the matched hunk's pre-image to
contain **no** function-definition header before its first edited line — i.e.
confirm the label describes the edited region, not the hunk's first byte. The
detector, its four negatives and its reach are already written and passing in
`.temp/php40/samefunc_probe.py`; the docstring now carries the defect, its reach
and a pointer, so nobody cites 26 as 26 unqualified. ⭐ **And note it is
`INAPPLICABLE-SAME-FILE`'s arrival that makes this repair safe to make** — before
today, demoting `ph53` would have moved it from one wrong label to another.

---

## §5 THE BUILD BRIEF — `ph53` · storage grown to the COUNT, tail never written

⚠ **Everything in §5.6 is a PREDICTION, labelled as one so the build task can be
measured against it** (§4 of the task file). Everything before §5.6 is measured
or cited.

### 5.1 Tier — ⚠ **declare `narrowed`, not the catalogue's `verbatim`**, and itemise

Under `CATALOGUE.md` §0.1 the provenance block names the **defect** site, and the
defect span **does** lift byte-identically — that is exactly why R1h `patch`es
onto it. But the *mechanism* needs three frames in two files, and two of them do
not lift:

| frame | site | lifts? |
|---|---|---|
| **defect** | `Zend/zend_compile.c:2569-2572` (`zend_do_end_class_declaration`) | ✅ **byte-identical** |
| the count advance | `Zend/zend_compile.c:2584-2592` (`zend_do_implements_interface`) | ⚠ the `num_interfaces++` lifts; `get_next_op`, `zend_op`, `CG()`, `opline->extended_value` do not → **`projection`** |
| **faulting** consumer | `Zend/zend_operators.c:1530-1538` (`instanceof_function_ex`) | ⚠ the loop lifts; `instanceof_function`'s class-tree walk and `TSRMLS` do not → **`narrowed`** |
| **compare-only** consumer | `Zend/zend_compile.c:1947-1953` (`zend_do_inherit_interfaces`) | ✅ the compare loop lifts |

⚠ **This weakens §7.2's tie-break and I am saying so rather than letting it
stand** — on *"how much real PHP text is in the kernel"* the two candidates are
close, and §2.5's three measured reasons are what the recommendation actually
rests on. A tier is a **cost, never a filter** (§A1, `CATALOGUE.md` §0.2), so
declaring `narrowed` refuses nothing.

**`provenance` block:**

```
c_file        Zend/zend_compile.c
c_lines       2569-2572
extract_cmd   tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '2569,2572p'
tier          narrowed
cwe           CWE-824
fix_commit    d09cdd9f71f34deab4b99f4e63523fb94164a724   ⚠ NOT the corpus column
              (the column is be8daf1f47fa and it is EXCLUDED — cite both, §F5(iii))
uses_allocator  true
echoes        ["p27"]          (and cross-reference ph32 — sized to the LITERAL, excess PAST the end)
```

### 5.2 The divergence ledger — itemise at least these

| `what` | `kind` | `where` | `why` |
|---|---|---|---|
| `TSRMLS_DC` / `TSRMLS_CC` | `deletion` | `zend_compile.c:2542`, `zend_operators.c:1530` | thread plumbing, no semantics |
| `zend_op` / `get_next_op` / `CG(active_op_array)` | `projection` | `zend_compile.c:2586-2590` | the opcode array's only role is to carry `extended_value` from phase 1 to phase 2; the blob's op stream carries it instead. No semantics |
| `instanceof_function`'s parent-chain walk | `narrowed` | `zend_operators.c:1539-1546` | the row prices the **slot read**, not the class-tree walk; the walk is replaced by pointer identity. ⚠ Reachable-domain argument owed |
| `zend_verify_abstract_class` / `do_verify_abstract_class` | `deletion` | `zend_compile.c:2573-2579` | inside the extracted span's `if`, does not touch `interfaces`, no semantics |
| `erealloc` → the shim's `erealloc` | — | — | **not** a divergence: §B requires the shim |

### 5.3 The kernel's C shape — and **do not reach for the executor**

`ph49`'s warning applies verbatim here: *an extraction that reaches for the
executor has built a different row.* **The blob IS the opcode stream.** Three
phases in one `kernel()` call:

```c
/* phase 1 — zend_do_implements_interface :2591, n times, one per `implements` */
for (k = 0; k < n_decl; k++) idx[k] = ce->num_interfaces++;   /* NO slot written */

/* phase 2 — zend_do_end_class_declaration :2569-2572, VERBATIM, the defect */
if (ce->num_interfaces > 0) {
    ce->interfaces = (iface_t **) erealloc(ce->interfaces,
                     sizeof(iface_t *) * ce->num_interfaces);   /* no zeroing */
}

/* phase 3 — the op stream: FILL writes one slot, QUERY reads them all */
```

`ce->interfaces = NULL; ce->num_interfaces = 0;` at init (`:3747-3748`), so the
`erealloc` is a plain `malloc` and **every** slot is indeterminate.

**Both consumers ship**, because §2.4 shows one hunk lands at two severities:

```c
/* QUERY_DEREF  — zend_operators.c:1534-1535, the FAULTING consumer */
for (i = 0; i < ce->num_interfaces; i++)
    if (ce->interfaces[i] == target || ce->interfaces[i]->id == target->id) return 1;
/* QUERY_CMP    — zend_compile.c:1951, the COMPARE-ONLY consumer */
for (i = 0; i < ce_num; i++) if (ce->interfaces[i] == entry) break;
```

**Allocator (§B):** link `common-php/emalloc_shim.h`; `c/emalloc_shim.h` symlink
**unconditional**; `php_shim_reset()` at the top of every kernel call (§B1.3);
fold `php_shim_tally()` into the `u64` (§B1.2).
⭐ **§B1a's precondition HOLDS: allocations per call are O(1)** — one `erealloc`
per class declaration, and `FILL`/`QUERY` allocate nothing. **So `ph53` is the
exception §B1a says is worth remarking on, and its cross-language column needs no
allocator caveat** — unlike `ph64`'s `2n+2`. **Declare the order in `spec.md`
anyway** (§B1a.2).

### 5.4 Blob format

```
u32  n_decl          number of `implements` clauses  (phase 1 count target)
u32  n_pool          size of the interface pool
u32  n_ops
n_pool × { u64 id }                      the pool; `id` is what the u64 folds
n_ops  × { u8 op; u32 a; u32 b }
        op=0 FILL(a=decl index, b=pool index)   ce->interfaces[idx[a]] = &pool[b]
        op=1 QUERY_DEREF(a=pool index)          the faulting consumer
        op=2 QUERY_CMP(a=pool index)            the compare-only consumer
```

### 5.5 Benign corpus, the `u64`, and the adversarial input

**Benign** = every `FILL` precedes every `QUERY`, and `n_decl` `FILL`s cover
`0..n_decl-1` exactly once. Ordinary class declarations.

⛔ **The `u64` is NOT "a fold of the interface pointers read"** — the catalogue's
`▸ benign` line says that and it is address-dependent, so it will not reproduce
across rungs or runs (§3). **The `u64` is:**

```
fold over each op, in order, of:
   QUERY_DEREF : (u64) retval, then the matched pool `id` (0 if no match), then i_examined
   QUERY_CMP   : (u64) retval, then the matched decl INDEX (n if no match)
   FILL        : the decl index
finally: php_shim_tally()
```

Every term is an **index, an id or a count** — no address ever enters it.

**`inputs/gen.py` must ASSERT its own coverage (§A2a rule 1)**, because the
defect's own branch is `if (ce->num_interfaces > 0)` at `:2570` — **two arms**:

1. classes with `n_decl == 0` **and** `n_decl > 0` — both arms of `:2570`;
2. the query loop's arms: **0 iterations** (`n_decl == 0`), **match on the
   first** slot, **match on the last**, and **no match** (the full-scan path);
3. **both** consumers exercised.

⚠ `_check_arms()` must **re-derive this from the bytes it just wrote** and refuse
a corpus that misses an arm — an intention in a comment is what `ph03` had, and
it was wrong for a task. Keep `n_decl` constant per cell so `work_per_call` is
constant.

**`model.py::selfcheck` must construct its own domain (§A2a rule 2)** — sweep
`n_decl = 0..32` × op orderings, not the six `.bin` files. Two implementations,
must-fire and must-NOT-fire controls.

**Adversarial input** = any blob where a `QUERY` precedes the last `FILL`; the
minimum is `n_decl=2`, `FILL(0)`, `QUERY_DEREF`. What it triggers, per rung:

| rung | on the adversarial blob |
|---|---|
| R1 / R4 | `QUERY_DEREF` dereferences slot 1, which holds whatever `malloc` returned → **CWE-824 wild read**, ASan `heap-buffer-overflow`/SEGV. `QUERY_CMP` compares an indeterminate pointer — **the graded half** |
| **R1h** | slot 1 is NULL → `QUERY_DEREF` **SEGV (deterministic)**; `QUERY_CMP` returns a **correct** no-match. **§2.4's result, measured** |
| R2 / R3 | **cannot be written**; see §5.6 |

⚠ **Determinism of the control:** the shim's size-class cache (§B1.1) hands a
freed block straight back to the next same-class request, so a `controls/` probe
should **prime** the allocator — write chosen bytes into a block of the same size
class, free it, then let the `erealloc` pick it up. That makes the wild pointer
**chosen rather than observed**, which is what a control needs.

**Fidelity (§A4):** reproduce `wild-pointer-deref` under `build = asan` with the
same binaries clean on the benign corpus. ⚠ A different signal (a plain SEGV
where the corpus says otherwise) is **a finding to state**, not a failure.

### 5.6 ⭐ §4's LABELLED PREDICTION for the five rungs — *this is a prediction, not a result*

**R2 (safe Rust, naive) — the mechanism is INEXPRESSIBLE and the program must
change.** A safe `Vec` cannot have length *n* with uninitialised elements. So R2
becomes `vec![None; n]` / `Vec<Option<&Iface>>` and the query becomes
`if let Some(x) = slot`. ⭐⭐ **PREDICTION, AND IT IS THE FINDING THIS ROW EXISTS
FOR: R2 is PHP 5.2.0's upstream repair, reinvented by the type system** — the same
*"the count never exceeds the slots written"* invariant, obtained from
`Option`/`push` rather than from a `memset`. Predicted cost: with niche
optimisation `Option<&Iface>` is one word and the guard is a `test/jz`, so **R2 ≈
R1h and cheaper than a naive bounds-checked scan**.

**R3 (safe Rust, tuned).** Grow by `push` as each interface arrives —
`Vec<&Iface>`, no `Option`, no separate zeroing pass, no window at all. That is
5.2.0's `zend_do_implement_interface` exactly. ⭐ **PREDICTION: R3 is the cheapest
rung on the row** — the safe restructuring is also the fastest, because it deletes
both the discriminant check and the zeroing. **If that holds it is the row's
headline; if it fails, the reason is the `push` reallocation schedule and that is
the number to report.**

**R4 (unsafe Rust).** `Vec<MaybeUninit<*const Iface>>` + `assume_init_read` at
the query reproduces the C including the defect.
⚠⚠ **SEARCHED, in the PINNED `~/tools/verus/vstd/` and in `std_specs/`
specifically, and the result constrains the design** (`.temp/php40/15-vstd-r5-search.log`):

| spelling | in the pinned vstd? |
|---|---|
| `MaybeUninit::{new, uninit, assume_init, assume_init_ref, assume_init_mut}` | ✅ **`vstd/std_specs/maybe_uninit.rs`** — `assume_specification`, all five |
| `MaybeUninit::write`, `assume_init_read`, `as_ptr`, `as_mut_ptr` | ⛔ **no spec** — 0 hits anywhere under `vstd/` |
| `Vec::set_len`, `Vec::spare_capacity_mut` | ⛔ **no spec** in `std_specs/vec.rs` |

▶ **So R4's most natural shape — `with_capacity(n)` + `set_len(n)` +
`spare_capacity_mut()` — is unverifiable at R5, and R4/R5 must instead
materialise `MaybeUninit::uninit()` elements** (which *is* specified), and
**initialise by assigning `MaybeUninit::new(x)`, not by `slot.write(x)`.**
⭐ **PREDICTION: LLVM elides the `MaybeUninit::uninit()` fill entirely and R4's
inner loop is byte-identical to R1's. If it does NOT elide, R4 pays an O(n) write
pass the C rung skips and lands near R1h** — which would make R4 *dearer* than
the C it models, a result worth the row on its own.

**R5 (unsafe + Verus) — the obligation is STATABLE and vstd already spells it.**
`vstd/std_specs/maybe_uninit.rs` gives `MaybeUninit::mem_contents() -> MemContents<T>`
with `uninit()` ensuring `MemContents::Uninit` and all three `assume_init*`
carrying `requires m.mem_contents().is_init()`.

> **The obligation is literally the vstd `requires`:**
> `forall|i| 0 <= i < ce.num_interfaces ==> v[i].mem_contents().is_init()`
> as a loop invariant on the query, discharged by phase 2's `FILL`s.

⭐⭐ **PREDICTION, and note it CONTRADICTS the guess I would have made**: R5 needs
**no hand-rolled ghost `Seq<bool>`** — `mem_contents()` *is* the ghost state and
`MemContents::{is_init, value}` (`vstd/raw_ptr.rs:250,264`) are its accessors.
▶ **So R5's real burden is proving the `FILL`s cover `0..num_interfaces`, which is
a coverage property of the blob, not a memory property** — i.e. **R5 proves
exactly the invariant PHP 5.2.0 restored by construction and PHP 5.0.5 papered
over with a `memset`.** ⚠ Residual risk to check first: whether the `FILL`
assignment `v[i] = MaybeUninit::new(x)` through `Vec`'s `index_mut` carries a
value-level `ensures` in `std_specs/slice.rs` (it does for `Range<usize>`, per
`CLAUDE.md`'s TASK_089 note — **grep the inherent spelling as well as the free
one**). **Trusted base to report:** every `assume_init*` site, and any
`external_body` wrapper the `Vec` indexing needs.

**`ph52` at R5, for contrast** (it is not the recommended row): its obligation is
about a **tag byte driving a switch**, which in Rust is an enum discriminant, so
R4 is `MaybeUninit<Zval>` and R5 lands on the **same** `mem_contents().is_init()`
spelling. ⭐ **So the two rows are not redundant at R5 in the obligation's
*spelling* — they differ in the fault primitive (indeterminate pointer vs
indeterminate discriminant selecting a teardown path), which is the C-side
distinction admission turns on.**

---

## §6 WHAT I DID NOT DO, AND WHAT I AM UNSURE ABOUT (`PROTOCOL.md` DoD 5)

1. ⛔ **No row was built.** No `spec.md`, no gate run, no `harness-php/gate.py
   --tool build`. As instructed.
2. ⛔ **I did not land the `same_function` repair** (§4.3) — out of scope, and it
   moves a corpus-wide flag. The detector and its four negatives are written and
   passing; the decision is the manager's.
3. ⚠ **I did not identify a commit for PHP 5.2.0's restructuring** (§2.2's last
   row) — the `interfaces = NULL; num_interfaces = 0` + per-slot-growth rewrite.
   It is **not** R1h (R1h is the 2005 commit that removes 5.0.0's cited line) and
   the row does not need it, but it is the *structural* repair and someone may
   want it. Bracket: after `php-5.1.0`, at or before `php-5.2.0`.
4. ⚠ **`d09cdd9f71f3`'s reachability from `php-5.0.5` rests on the GitHub API
   query being rooted at that tag** (`?sha=php-5.0.5`), not on a local `git
   merge-base`. The tag bracket (`5.0.4` has the line, `5.0.5` does not) and the
   patch's own `-` line are two further independent supports, so I am confident;
   but it is one inference and not three.
5. ⚠ **Everything in §5.6 is a prediction.** In particular *"R3 is the cheapest
   rung"* and *"LLVM elides the `MaybeUninit::uninit()` fill"* are the two most
   likely to be wrong, and the R5 `index_mut` question in §5.6's last paragraph
   is **unresolved** — I named where to grep rather than claiming an answer,
   because `CLAUDE.md` records that exact false-negative twice.
6. ⚠ **§5.1's tier disagreement with `CATALOGUE.md` is a judgement, not a
   measurement.** I have not extracted the kernel, so *"the consumers do not
   lift"* is an assessment from reading the tarball. It refuses nothing either
   way (§A1: a tier is a cost).
7. ✅ **Clean negative worth recording**: both corpus patches were **already in
   `.temp/mgr/batch/patches/`** and my fresh fetches are **byte-identical** to
   them. The shared cache has not drifted from what GitHub serves.
8. ⚠ `d09cdd9f71f3.patch` is in `.temp/php40/patches/` and **not** in
   `preimage_screen.py`'s `PATCH_DIRS`. I screened it by extending `PATCH_DIRS`
   **in a driver script**, so the validator keeps no pointer into `.temp/`
   (open item 65). If the manager wants that sha in the standing survey, the
   patch should go to the shared cache rather than the list gaining a fourth
   gitignored path.

---

## §7 EVIDENCE — every artefact, with what it proves

`.temp/php40/` is **gitignored**, so the numbers and shas are in this file and
the paths are for re-derivation, not for citation (open item 65).

| path | what it is |
|---|---|
| `00-EXPECTATIONS-PRE-FETCH.md` | §1's predictions, written before the first `curl` |
| `01-pre-fetch-state.log` | `patches/` empty; cache status; the **baseline** `--selftest PASS` |
| `patches/7412202c43e7.patch` | sha256 `32e8526ebfe684d9…`, 746 B — **evidence, stays** |
| `patches/be8daf1f47fa.patch` | sha256 `42190b44ad8068c3…`, 7397 B — **evidence, stays** |
| `patches/d09cdd9f71f3.patch` | sha256 `4f97b625fc9772d6…`, 1026 B — ⭐ **`ph53`'s R1h, stays** |
| `tagcheck.py` + `03-tagcheck.log` | the §F5(iii) tag walk, 13 blobs across 9 refs, each with its sha256. **Generator kept, blobs deleted** (`--clean`) |
| `narrow.sh` + `04-narrow-5.0.x.log` | the `5.0.1`–`5.0.4` narrowing that produced the one-release bracket |
| `05-all-BEFORE.{json,log}` / `09-all-AFTER.{json,log}` | the corpus screen either side of §4: `43/106/18` → `26/17/106/18` |
| `06-samefunc-probe.log` + `samefunc_probe.py` | §4.3's defect: 4 negatives, `PASS`, reach **1 of 170** |
| `07-label-impact.log` | the 17 movers, measured **before** the edit — this is what caught N2 |
| `08-selftest-AFTER.log`, `10-selftest-FINAL.log` | `--selftest PASS`, both runs |
| `11-final-screens.log`, `12-screen-d09cdd9f.log`, `02*-screen-ph52*.log` | the per-row screens |
| `applytest.sh` + `13-backport-apply.log` | do the R1h patches apply to pristine 5.0.0? `ph53` yes, `ph52` no. **Generator kept, tree deleted** |
| `14-brief-premises.log` | `:3747-3748`, `zend_do_implements_interface`'s span, the vstd `MaybeUninit` grep |
| `15-vstd-r5-search.log` | §5.6's searched negatives on `write` / `assume_init_read` / `set_len` |

---

## §8 BRACKET AND SCOPE

```
FIRST   python3 harness/measure.py --check-stale               -> 66 record(s) examined, 0 STALE
        python3 harness-php/gate.py --tool measure --check-stale -> 14 record(s) examined, 0 STALE
LAST    python3 harness/measure.py --check-stale               -> 66 record(s) examined, 0 STALE
        python3 harness-php/gate.py --tool measure --check-stale -> 14 record(s) examined, 0 STALE

git status --porcelain
 M .tasks-php/preimage_screen.py
```

One tracked file changed, and it is the one §6 of the task file permits.
`grep -arn 'preimage_screen' harness/*.py harness-php/*.py common/*.py
common-php/*.py` → **0 hits**, so the edit is in **no digest** and costs no
re-gate. Nothing under `harness/`, `common/`, `common-php/`, `patterns/`,
`patterns-php/`, `results/`, `results-php/`, `pilot/`, `.web/`, `RECAP_PHP.md` or
`.memory-php/` was touched. No `git add`, no `git commit`. No `/tmp` file. Every
corpus and tarball `grep` used `-a`.
