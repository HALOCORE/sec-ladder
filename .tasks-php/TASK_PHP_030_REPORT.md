# TASK_PHP_030_REPORT — the PRE-IMAGE SCREEN

**Role: research investigator. One agent, alone. NOTHING WAS BUILT.** No pattern
directory, no rung, no gate, no measurement, no C. Everything I wrote is under
`.temp/php30/` plus this file. No `git add`, no `git commit`. Nothing written to
`RECAP_PHP.md`, `.memory-php/`, `patterns-php/`, `.web/`, `harness/`, `common/`,
`patterns/`, `results/`, `pilot/`. I did not read or write `patterns-php/ph29*`,
`.temp/php27/` or `.temp/php29/`.

---

## §0 Headline

| | |
|---|---|
| **§4's four ground-truth cases** | ✅ **all four reproduce**, in both directions, and the four span all three outcomes so no constant answer passes |
| **the screen agrees with FIVE MORE hand-established verdicts** it was not built against — `ph03`, `ph29`, `ph16` (must-NOT-exclude), `ph12`, `ph22` | **9 for 9** |
| **records screened** | **170** — the 169 `fixsurvey.py` calls `resolved`, plus `ph36`'s no-sha record |
| **NOT-THE-REPAIR** | **43** (25 %), over **34 rows** |
| ⚠⚠ **of those 43, how many are an EXCLUSION rather than a shrug** | **33** carry positive evidence that the commit's window reaches the cited site; **10 do not and must be reported as *"does not touch the cited lines"*, not as an exclusion** |
| **INAPPLICABLE** | **18**, against the survey's **19** OTHER-FILE — **the one disagreement is a real corpus finding**, §4 below |
| **§7.3 — does it just re-derive the date selector?** | **No. 29 of 43 exclusions are dated before 2010**, and **12 exclusion rows are missed by the UNION of the date and id-spread selectors** |
| **§5 `ph95`** | **SETTLED, with an upstream artefact.** The corpus column `865739e5b196` is **excluded from the bytes**; R1h is **`db420cb6a141876b2f7d101051fb01934a28071a`** |
| **bonus** | **`ph22`'s R1h now has a sha** — `6d98fc38b53c0ce803bf5cc8de05e2083eb6cd41`, Stefan Esser, 2004-11-28. `FIXSURVEY_001.md` had only the 5.0.0→5.1.0 tag bracket |

⚠⚠ **The single most important thing in this report is not a count.** It is that
*"the cited text is absent from the pre-image"* has **two readings**, and the
screen as first written could not tell them apart. §3 is that finding.

---

## §1 What ships, and how to run it

| path | what |
|---|---|
| `.temp/php30/preimage_screen.py` | **the tool.** `--selftest` (§4's four + nine negatives), `--all`, `--row phNN`, `--id CRASH-NNN`, `--json OUT`, `--no-file-restrict` (a control), `--sha X --cell '<citation>'` (manual mode) |
| `.temp/php30/crosstab.py` | §6.3 / §7.3 — the cross-tabulations |
| `.temp/php30/audit_parser.py` | the diff-parser validity audit over **every** cached patch |
| `.temp/php30/mktable.py` | renders the deliverable table |
| `.temp/php30/01-selftest.log` … `06-table.md` | the run output pasted below |
| `.temp/php30/screen.json` | all 170 records, machine-readable |
| `.temp/php30/patches/` | **3 patches not in the shared cache** — `6d98fc38b53`, `db420cb6a14` (ph95, §5) and `56adfe1f3cf1`. Re-fetchable with the same `curl` `fixsurvey.py` uses |

```sh
python3 .temp/php30/preimage_screen.py --selftest        # 0.7 s, no network
python3 .temp/php30/preimage_screen.py --all             # 2.2 s, no network
python3 .temp/php30/crosstab.py
python3 .temp/php30/audit_parser.py
```

**The rule, restated exactly as implemented.** A unified diff applies only to a
tree whose text matches the hunk's context and `-` lines, so **the pre-image is
a partial snapshot of the tree the commit was diffed against**. Restricted to
hunks whose `diff --git a/…` names the defect's file, if the 5.0.0 text at the
cited site is **not** in that snapshot, the commit was written against a tree
that no longer has it.

**Three outcomes, per §3.4:**

- `INAPPLICABLE` — the patch has **no** hunk for the defect's file. The screen
  says **nothing** about such a commit.
- `NOT-THE-REPAIR` — it does touch the file, and none of the cited 5.0.0 lines
  are in its pre-image for that file.
- `CANDIDATE` — at least one is. ⚠ **CANDIDATE is not a verdict of
  correctness**; it means the screen could not exclude the commit, and
  `PROTOCOL_PHP.md` §F5(iii)'s tag check still owes an answer.

Plus three honest non-answers: `NO-SPAN` (2), `NO-SHA` (1, `ph36`), `NO-PATCH` (0).

### The traps, and what I did about each

1. ⚠⚠⚠ **Line numbers are never read** (§3.1). `@@` headers are used only to
   *enter* a hunk; the trailing **function-name text** of a header is read (it
   is text), the numbers are not. **Tested behaviourally, not by inspection**:
   selftest **N6** rewrites every `@@ -a,b +c,d @@` in all four ground-truth
   patches to `@@ -1,1 +1,1 @@` and asserts every verdict and every hit is
   unchanged. It is.
2. ⚠⚠ **Pre-image = context (` `) + removed (`-`), only in the defect file's
   hunks.** Selftest **N4** proves a `+` line cannot leak in. Selftest **N5**
   proves the file restriction is load-bearing — `ph07` moves
   `INAPPLICABLE → NOT-THE-REPAIR` without it, which is precisely the
   permissive error §3.4 warns of, in the other direction.
   ⭐ **And an external check the task did not ask for:** `@@ -a,b` *declares*
   the pre-image length. The parser never reads `b`, so counting its output
   against `b` is a genuine outside test — **1892 hunks across 476 file
   sections, 0 mismatches** (`05-audit.log`).
3. ⚠ **Normalisation, stated.** `norm_ws`: strip `\r`, collapse every run of
   whitespace (tabs included) to one space, strip the ends. `norm_code`: that,
   then delete complete `/*…*/`, `//…` and an unterminated `/*` tail. **Nothing
   is lowercased, no punctuation is removed, no identifier is renamed.**
   Selftest **N3** shows four pairs that must stay different
   (`a = b + c;` vs `a = b - c;`; `zval tmp;` vs `zval *tmp;`; `<` vs `<=`;
   argument order) and **one case it does change**: `"\t\tzval  tmp;\r"` vs
   `"    zval tmp;"` — raw unequal, normalised equal. It is load-bearing: PHP's
   tree re-indents a line whenever its enclosing block moves, and both `ph73`
   hits and the `ph21` refutation depend on it.
4. ⚠⚠ **INAPPLICABLE is a third outcome, not a non-match.** 18 records.
5. ⚠ **`c_file_line` may name the FAULT site, not the MECHANISM.** Handled
   *per record*: every verdict below carries its own cited lines, its own
   hits/misses and its own evidence. **I aggregate nothing I cannot defend per
   row**, and §3's tiering exists because one aggregate verdict would have been
   wrong for 10 of 43.
6. ⚠ **A probe whose setup encodes the answer.** §4's four span **all three**
   outcomes (N1: always-CANDIDATE scores 2/4, always-NOT-THE-REPAIR 1/4,
   always-INAPPLICABLE 1/4), so **no constant implementation passes**. N2 moves
   `ph73`/CRASH-051's span to a bogus one 220 lines away and requires the
   verdict to flip `CANDIDATE → NOT-THE-REPAIR`; it does.

---

## §2 §4's ground truth — all four, output pasted

```
==============================================================================
§4 GROUND TRUTH -- all four must reproduce, in BOTH directions
==============================================================================
✅ ph21  CRASH-107  c591f022f8ab  expect NOT-THE-REPAIR  got NOT-THE-REPAIR
     the patch touches ext/standard/string.c but NONE of its 1 cited 5.0.0 lines appear in that file's pre-image; and the commit's window PROVABLY REACHES the site (DECISIVE)
     (TASK_PHP_029 §3; the pre-image is already the post-5.2.0 form)
     misses: ['result_len = Z_STRLEN_PP(input_str) * Z_LVAL_PP(mult);']

✅ ph73  CRASH-052  3d7b0bab28e7  expect CANDIDATE       got CANDIDATE
     3/5 cited 5.0.0 lines are present in the pre-image of Zend/zend_execute.c
     (TASK_PHP_029 §2; exact fix, regression test in-commit)
     hits  : ['zval tmp;', 'zval_copy_ctor(&tmp);', 'convert_to_string(&tmp);']
     misses: ['tmp = *offset;', 'offset = &tmp;']
     ⚠ same text in ANOTHER file of the same patch: {'Zend/zend_vm_def.h': [1138, 1146, 1147, 1148, 1149], 'Zend/zend_vm_execute.h': [1138, 1146, 1147, 1148, 1149]}

✅ ph73  CRASH-051  235e6c0afe1d  expect CANDIDATE       got CANDIDATE
     3/4 cited 5.0.0 lines are present in the pre-image of Zend/zend_object_handlers.c
     (TASK_PHP_029 §2; bug #30562, 5.0.3->5.0.4)
     hits  : ['method_args_ptr = &method_args;', 'zval_dtor(method_args_ptr);', 'zval_dtor(method_name_ptr);']
     misses: ['zval method_name, method_args, __call_name;']

✅ ph07  CRASH-124  cb3cca21b345  expect INAPPLICABLE    got INAPPLICABLE
     the patch does not touch ext/mbstring/libmbfl/mbfl/mbfilter.c at all (it touches ext/mbstring/mbstring.c)
     (the fix is in the caller, ext/mbstring/mbstring.c)
```

Three things in that output are worth more than the four ticks.

⚠⚠ **`ph73`/CRASH-052 is a LUCKY PASS and I am reporting it as one.** The right
answer is CANDIDATE, and the screen gets it — **but not for `_029`'s reason.**
The two lines that actually pin CRASH-052's site, `tmp = *offset;` and
`offset = &tmp;`, are **absent from `zend_execute.c`'s pre-image and present in
`Zend/zend_vm_def.h`'s**, exactly as `_029` §2 says ("*the guard moved because
the file did*"). The three that hit in `zend_execute.c` are the **sibling
idiom** in `zend_assign_to_object`, a different function. **This is trap §3.5
firing on the one ground-truth case that could show it**, and it is why the
`elsewhere` column exists: it names, per record, which *other* file of the same
patch carries the cited 5.0.0 text.

⚠ **`ph73`/CRASH-051's one miss is informative and confirms `_029`.** The commit's
pre-image is `zval method_name, method_args;` — `__call_name` had already gone
by 2004-12. `_029` §2 quotes the **5.0.0 → 5.0.4** function diff (which does
carry `__call_name`), not the commit's own; both are right about different
trees, and the screen sees the commit's.

⭐ **`ph07`'s INAPPLICABLE is right, and the corpus cell already says so.**
`CRASH-124`'s cell is
`ext/mbstring/libmbfl/mbfl/mbfilter.c:1203 (OOB read site); missing guard at ext/mbstring/mbstring.c:1807`
— the *second* half names the file the fix touches. A future screen could
follow that; this one deliberately does not, because that would be a
`c_file_line`-prose heuristic and not a proof.

### Nine negatives, all run (`01-selftest.log`)

| | what it attacks | result |
|---|---|---|
| **N0** | regression: `ph73`/CRASH-100 — a **false exclusion I shipped and then found**, §7 | ✅ fires |
| **N1** | no constant answer passes §4 | ✅ 2/4, 1/4, 1/4 |
| **N2** | the verdict is keyed on the **cited text** — move the span, the verdict flips | ✅ fires |
| **N3** | the normaliser does not make different code equal (4 pairs) **and** is load-bearing (1 pair) | ✅ silent / ✅ fires |
| **N4** | `+` lines cannot leak into the pre-image | ✅ silent |
| **N5** | the defect-file restriction is load-bearing | ✅ 1 of 4 verdicts moves |
| **N6** | the verdict does not depend on the patch's **line numbers** (headers rewritten to `@@ -1,1 +1,1 @@`) | ✅ silent |
| **N7** | the pre-image parser against **hunk arithmetic** | ✅ 378 hunks, 0 mismatches (full sweep: 1892, 0) |
| **N8** | the **decisiveness** test — must fire on `ph21`, must not fire for a hunk in another function of the same file | ✅ fires / ✅ silent |
| **N9** | **five hand-established verdicts the screen was not built against**, three of them **must-NOT-exclude** | ✅ 5/5 |

**N9 in full, because it is the strongest evidence in this report:**

```
    ✅ ph03  CRASH-115  expect CANDIDATE       got CANDIDATE       decisive=None
       MUST-NOT-EXCLUDE. F38 half 1: TASK_PHP_013 APPLIED this patch and measured its
       effect over 12,600 documents. The only fix_commit in the corpus confirmed
       correct behaviourally.
    ✅ ph29  CRASH-097  expect CANDIDATE       got CANDIDATE       decisive=None
       MUST-NOT-EXCLUDE. F38 half 2: 'exact and minimal'.
    ✅ ph16  CRASH-098  expect CANDIDATE       got CANDIDATE       decisive=None
       MUST-NOT-EXCLUDE. F38 half 2: 'the right fix, inside a 10-file 27 KB change'
       -- also a size control.
    ✅ ph12  CRASH-108  expect NOT-THE-REPAIR  got NOT-THE-REPAIR  decisive=True
       F38 half 2 proved this is a LATER fix, by hand, from its pre-image.
    ✅ ph22  CRASH-014  expect NOT-THE-REPAIR  got NOT-THE-REPAIR  decisive=True
       FIXSURVEY_001 'ph22 was the standout': settled across EIGHT TAGS; R1h is
       INC_OUTPUTPOS's 5.1.0 arrival, not this 2025 commit.
```

⚠ `ph22` is the one I would point a reviewer at. `FIXSURVEY_001.md` settled it
**across eight tag snapshots**; the screen reaches the same verdict **from the
commit's own bytes, with no network and no tags**, and additionally says *which
function* (`PHP_FUNCTION(pack)`) and *what the tree has instead*
(`INC_OUTPUTPOS((arg + (arg % 2)) / 2,1)` where 5.0.0 has
`outputpos += (arg + 1) / 2;`).

---

## §3 ⚠⚠⚠ THE FINDING: *"absent from the pre-image"* HAS TWO READINGS, AND THE SCREEN AS FIRST WRITTEN COULD NOT TELL THEM APART

This is the part of the task I am least comfortable with §1's framing of, and
`PROTOCOL.md` rule 2 says to say so.

*"The pre-image does not contain the 5.0.0 text"* is consistent with **two**
states of the world:

- **(i)** the tree the commit was diffed against **no longer has** that text —
  a genuine proof of exclusion, which is `_029` §3's `ph21`; **or**
- **(ii)** the tree still has it and the hunk's **~3-line context window simply
  never reaches it** — in which case the absence proves *nothing at all*.

**And (ii) is not a corner case.** Measured (`05-audit.log`): behind the 43
exclusions the pre-image for the defect file is **min 7 lines, median 14, max
229**. A median of fourteen lines is one hunk with three lines of context each
side. *Most of a file is outside every window.*

**So a bare `NOT-THE-REPAIR` is NOT a proof of exclusion, and §1 of the task
overstates the rule.** The rule is sound only where the window demonstrably
reaches the site.

### What separates them, and both halves are TEXT

Two independent signals, neither reading a patch line number:

- **`same_function`** — a hunk header is
  `@@ -a,b +c,d @@ <enclosing function>`, and that trailing text is **git's own
  answer** to *which function is this hunk in*. Compare it against the
  enclosing header of the **cited 5.0.0 line**, computed by git's own default C
  `xfuncname` heuristic (nearest preceding line starting at column 0 with a
  letter, `_` or `$`). Equal ⇒ the commit edited **the same function the corpus
  cites**, so its window reaches the site.
  ⭐ This is what fires on `ph21`:
  `@@ -4949,6 +4949,10 @@ PHP_FUNCTION(str_repeat)` against 5.0.0's
  `PHP_FUNCTION(str_repeat)` at `:4115`, cited line `:4144`.
- **`bracketed`** — locate the hunk in 5.0.0 **by text**: a 5.0.0 line is an
  anchor if its normalised text is in that hunk's pre-image, is matchable, and
  occurs **exactly once** in the whole 5.0.0 file. If some hunk has an anchor
  before *and* after the cited line within 60 lines, the window spans the site.
  ⚠ **This was my first design and it does NOT fire on `ph21`** — that hunk's
  pre-image is 7 lines of which 2 are code and neither exists in 5.0.0, so
  there is nothing to anchor on. **A screen validated only on bracketing would
  have failed §4's one known-decisive case.** It fires alone on exactly one
  record (`ph77`/CRASH-050) and is kept because it is independent.

A third, weaker, **reported not decisive** signal: `nearest` — the closest
pre-image line by `difflib` ratio, printed beside every miss so a reader sees
*what the commit's tree has where 5.0.0 has the cited line*.

### The tiering, and it changes the answer for 10 records

| tier | evidence | count |
|---|---|---|
| **A+B** | window provably reaches the site **and** the pre-image carries a near-variant (≥ 0.60) of the cited line | **14** |
| **A** | window provably reaches the site | **12** |
| **B** | near-variant ≥ 0.60, but nothing shows the window reaches the site | **7** |
| **–** | **neither** | **10** |

**A ∪ B = 33 of 43.** ⚠ **The 10 in tier `–` should be reported as *"this
commit does not touch the cited lines"*, NOT as *"this commit is not the
repair"*** — they are consistent with the commit repairing a *different* defect
in the same file, and equally consistent with the window missing the site.

⚠ **0.60 is a REPORTING cutoff, not a verdict**, and the sensitivity is printed
rather than buried (`04-crosstab.log` §E): `≥0.4 → 29`, `≥0.5 → 25`,
`≥0.6 → 21`, `≥0.7 → 16`, `≥0.8 → 9` of 43. **Tier A does not move with it**,
which is the point of having two signals: `ph22`/`ph95` score only **0.37** on
similarity — `outputpos += (arg + 1) / 2;` vs
`INC_OUTPUTPOS((arg + (arg % 2)) / 2,1)` is the *same statement rewritten*, and
a character-ratio cannot see that — while `same_function` puts them squarely in
tier A. Conversely `ph61`/CRASH-117 scores **0.97** (one added `(char*)` cast)
and is tier B because the header context did not match.

---

## §4 §6.3 — INAPPLICABLE **18** against the survey's OTHER-FILE **19**

```
    fixsurvey OTHER-FILE : 19
    screen  INAPPLICABLE : 18
    OTHER-FILE not INAPPLICABLE : [('ph72', 'CRASH-112')]
    INAPPLICABLE not OTHER-FILE : []
      ('ph72', 'CRASH-112'): screen=NO-SPAN  cited lines [[0, 0]] are out of range
                             for ext/standard/uuencode.c (206 lines)
```

**The two numbers disagree by exactly one record, and it is a real finding
about the corpus, not about either tool.** `CRASH-112`'s cell is

```
ext/standard/uuencode.c:0|ext/standard/user_filters.c:140
```

**`:0` is a sentinel, not a line.** `fixsurvey.py:194` derives `defect_file` as
`c_file_line.split(":")[0]`, which takes `ext/standard/uuencode.c` and so
reports **OTHER-FILE** — but the row's real site is the *second* half,
`ext/standard/user_filters.c:140`, **which is exactly the file
`4c0970bec69b` touches**. So the survey's OTHER-FILE verdict for `ph72`/CRASH-112
is an artefact of the `split(":")[0]` parse, and the record is not an
`ph07`-shaped row at all.

⚠ I let the screen return `NO-SPAN` rather than silently ordering the
applicability check first — **had I checked applicability before the span, the
counts would have matched at 19/19 and this would never have surfaced.** That
is `PROTOCOL_PHP.md` §D's *"an out-of-range span used to PASS"* lesson one level
across.

⭐ **The `elsewhere` channel turns three more INAPPLICABLEs into something
better than a shrug** (`04-crosstab.log` §F). Where a bare INAPPLICABLE says
nothing, this says *the cited 5.0.0 text is in a different file of the same
patch* — i.e. **the code moved file and the commit may well be the repair**:

```
    ph27   CRASH-009  INAPPLICABLE    ext/standard/reg.c    ->  ['ext/ereg/ereg.c']
    ph54   CRASH-143  INAPPLICABLE    Zend/zend_execute.c   ->  ['Zend/zend_vm_def.h', 'Zend/zend_vm_execute.h']
    ph79   CRASH-069  INAPPLICABLE    Zend/zend_execute.c   ->  ['Zend/zend_vm_def.h', 'Zend/zend_vm_execute.h']
    ph46   CRASH-053  NOT-THE-REPAIR  Zend/zend_execute.c   ->  ['Zend/zend_vm_def.h', 'Zend/zend_vm_execute.h']
    ph02   CRASH-120  CANDIDATE       ext/standard/var_unserializer.c -> ['ext/standard/var_unserializer.re']
    ph65   CRASH-121  CANDIDATE       ext/standard/var_unserializer.c -> ['ext/standard/var_unserializer.re']
    ph73   CRASH-052  CANDIDATE       Zend/zend_execute.c   ->  ['Zend/zend_vm_def.h', 'Zend/zend_vm_execute.h']
    ph82   LOGIC-019  CANDIDATE       Zend/zend_execute_API.c -> ['Zend/zend_compile.c']
```

`ph27` is `FIXSURVEY_001.md`'s own *"the file was also moved
(`reg.c → ereg.c`), so both the function-name search and a path search fail on
it"* — now with the byte evidence that the 5.0.0 line `:337` is in the commit's
`ereg.c` pre-image. The four `zend_vm_def.h` rows are the **5.1 VM-generator
migration**, and `.re` → `.c` is **`re2c` generation**. ⚠ **`ph46`/CRASH-053 is
the one to look at**: it is currently classed `NOT-THE-REPAIR`, and its cited
5.0.0 line `:1632` *is* in the same patch's `zend_vm_def.h` pre-image — so the
commit is probably the repair, in the file the code moved to. It sits in tier
`–`, which is the correct place for it.

---

## §5 THE DELIVERABLE — every NOT-THE-REPAIR record, side by side

Full machine output: `.temp/php30/02-all.log` (each record with **all** its
cited lines) and `.temp/php30/06-table.md`. The `pre-image has` column is the
closest line in that commit's pre-image for that file — *what the commit's tree
carries where 5.0.0 carries the cited line*. Lines are shown normalised and
truncated to 76 chars.

| tier | row | corpus id | `fix_commit` | defect file | cited 5.0.0 line | the pre-image has, at that site | evidence |
|---|---|---|---|---|---|---|---|
| A+B | ph01 | CRASH-066 | `6a7cc8ff8582` | `ext/standard/var_unserializer.c` | `:390` `yy16: yych = *++YYCURSOR;` | `yych = *++YYCURSOR;` | same fn `PHPAPI int php_var_unserialize(UNS`; variant 0.86 |
| A+B | ph05 | CRASH-102 | `29b9d79c2ff6` | `ext/standard/string.c` | `:240` `if (((unsigned) start + (unsigned) len) > len1) {` | `if ((start + len) > len1) {` | same fn `static void php_spn_common_handler`; variant 0.71 |
| A+B | ph06 | CRASH-091 | `9d1986647629` | `ext/standard/html.c` | `:656` `unsigned char next2_char = str[pos+1];` | `unsigned char next2_char;` | same fn `inline static unsigned short get_n`; bracketed; variant 0.79 |
| A+B | ph21 | CRASH-107 | `c591f022f8ab` | `ext/standard/string.c` | `:4144` `result_len = Z_STRLEN_PP(input_str) * Z_LVAL_PP(mult);` | `result_len = input_len * mult;` | same fn `PHP_FUNCTION(str_repeat)`; variant 0.64 |
| A+B | ph30 | CRASH-133 | `17b39638d0a6` | `ext/bcmath/bcmath.c` | `:542` `BCG(bc_precision) = (Z_LVAL_PP(new_scale) < 0) ? 0 : Z_LVAL_PP(new_scale);` | `BCG(bc_precision) = (new_scale < 0) ? 0 : new_scale;` | same fn `PHP_FUNCTION(bcscale)`; variant 0.83 |
| A+B | ph43 | CRASH-079 | `2c36778e47b6` | `ext/standard/array.c` | `:2695` `*return_value = **array;` | `zval **array;` | same fn `PHP_FUNCTION(array_unique)`; variant 0.65 |
| A+B | ph46 | CRASH-056 | `3790227f9d36` | `Zend/zend_execute.c` | `:200` `if (!T(opline->op1.u.var).var.ptr_ptr) {` | `zval_ptr_dtor(&T(opline->op1.u.var).var.ptr);` | same fn `static inline void zend_switch_fre`; variant 0.71 |
| A+B | ph61 | CRASH-155 | `1aab36e3f22a` | `Zend/zend_builtin_functions.c` | `:615` `if (zend_lookup_class(Z_STRVAL_PP(class_name), Z_STRLEN_PP(class_name), &ce` | `if (zend_lookup_class_ex(Z_STRVAL_PP(class_name), Z_STRLEN_PP(class_name), (` | same fn `static void is_a_impl(INTERNAL_FUN`; variant 0.88 |
| A+B | ph74 | CRASH-139 | `9a98904ddd0e` | `Zend/zend_API.c` | `:1966` `value = Z_OBJ_HT_P(object)->read_property(object, &property, silent TSRMLS_C` | `value = Z_OBJ_HT_P(object)->read_property(object, property, silent TSRMLS_CC` | same fn `ZEND_API zval *zend_read_property(`; variant 0.99 |
| A+B | ph78 | CRASH-042 | `41ad9b4d1fdd` | `Zend/zend_object_handlers.c` | `:294` `zobj->in_get = 0;` | `guard->in_get = 0;` | same fn `zval *zend_std_read_property(zval `; variant 0.74 |
| A+B | ph82 | LOGIC-012 | `4d926b1fa37e` | `Zend/zend_builtin_functions.c` | `:994` `zval_copy_ctor(EG(user_error_handler));` | `zval *error_handler;` | same fn `ZEND_FUNCTION(set_error_handler)`; variant 0.61 |
| A+B | ph91 | CRASH-071 | `e8359d3f904c` | `Zend/zend.c` | `:955` `z_context->value.ht = EG(active_symbol_table);` | `Z_ARRVAL_P(z_context) = EG(active_symbol_table);` | same fn `ZEND_API void zend_error(int type,`; variant 0.77 |
| A+B | ph92 | CRASH-106 | `157ddd957731` | `ext/standard/string.c` | `:3593` `new_length = Z_STRLEN_PP(zstr) + repl_cnt * (sizeof("<br />") - 1);` | `new_length = str_len + repl_cnt * (sizeof("<br />") - 1);` | same fn `PHP_FUNCTION(nl2br)`; variant 0.85 |
| A+B | ph101 | LOGIC-018 | `0455ccb80552` | `Zend/zend_compile.c` | `:1900` `zend_hash_update(ce->static_members, child_info->name, child_info->name_leng` | `zend_hash_update(&ce->default_static_members, child_info->name, child_info->` | same fn `static zend_bool do_inherit_proper`; variant 0.96 |
| A | ph12 | CRASH-108 | `896a5216d73d` | `ext/standard/string.c` | `:4794` `RETURN_LONG(zend_binary_strncmp(s1 + offset, (s1_len - offset), s2, s2_len,` | `cmp_len = (uint) (len ? len : MAX(s2_len, (s1_len - offset)));` | same fn `PHP_FUNCTION(substr_compare)` |
| A | ph13 | CRASH-136 | `f002287eb39a` | `ext/exif/exif.c` | `:1047` `return (((uchar *)value)[1] << 8) \| ((uchar *)value)[0];` | *(nothing within 0.35)* | same fn `static void exif_process_TIFF_in_J` |
| A | ph22 | CRASH-014 | `865739e5b196` | `ext/standard/pack.c` | `:247` `outputpos += (arg + 1) / 2;` | `INC_OUTPUTPOS((arg + (arg % 2)) / 2,1)` | same fn `PHP_FUNCTION(pack)` |
| A | ph28 | CRASH-147 | `0ebe3a7690a7` | `Zend/zend_operators.c` | `:1168` `uint res_len = op1->value.str.len + op2->value.str.len;` | `uint res_len = Z_STRLEN_P(op1) + Z_STRLEN_P(op2);` | same fn `ZEND_API int concat_function(zval ` |
| A | ph43 | CRASH-111 | `30a015a92f68` | `ext/standard/url.c` | `:612` `zend_hash_internal_pointer_reset_ex(HASH_OF(stream->wrapperdata), &pos);` | *(nothing within 0.35)* | same fn `PHP_FUNCTION(get_headers)` |
| A | ph44 | CRASH-085 | `af1843f866a5` | `ext/standard/basic_functions.c` | `:2996` `add_next_index_zval(hash, element);` | `zval_copy_ctor(element);` | same fn `static void php_simple_ini_parser_` |
| A | ph53 | CRASH-158 | `be8daf1f47fa` | `Zend/zend_compile.c` | `:1951` `if (ce->interfaces[i] == entry) {` | `switch (interface_node.u.EA.type) {` | same fn `void zend_do_end_class_declaration` |
| A | ph76 | CRASH-078 | `96d755978cc8` | `ext/standard/array.c` | `:3273` `*return_value = **args[0];` | `RETVAL_ZVAL(*args[0], 1, 0);` | same fn `static void php_array_diff(INTERNA` |
| A | ph76 | CRASH-148 | `2a31dbbadfb9` | `Zend/zend_operators.c` | `:661` `object_and_properties_init(op, zend_standard_class_def, op->value.ht);` | `object_init(op);` | same fn `ZEND_API void convert_to_object(zv` |
| A | ph77 | CRASH-050 | `1b317f15264e` | `Zend/zend_execute.c` | `:3162` `zend_switch_free(brk_opline, EX(Ts) TSRMLS_CC);` | `zend_switch_free(&T(brk_opline->op1.u.var), brk_opline->op1.op_type, brk_opl` | bracketed `{cited 3162, before 3161, after 3164}` |
| A | ph80 | CRASH-114 | `77acc692fd9b` | `ext/standard/user_filters.c` | `:420` `if (append) {` | `} else {` | same fn `static void php_stream_bucket_atta` |
| A | ph95 | V5C-015 | `865739e5b196` | `ext/standard/pack.c` | `:247` `outputpos += (arg + 1) / 2;` | `INC_OUTPUTPOS((arg + (arg % 2)) / 2,1)` | same fn `PHP_FUNCTION(pack)` |
| B | ph39 | CRASH-036 | `d6505acbf5ff` | `Zend/zend_exceptions.c` | `:551` `zend_error_va(E_ERROR, Z_STRVAL_P(file), Z_LVAL_P(line), "Uncaught %s\n thro` | `zend_error_va(severity, Z_STRVAL_P(file), Z_LVAL_P(line), "Uncaught %s\n thr` | variant 0.92 |
| B | ph61 | CRASH-117 | `83ac79600e3a` | `ext/standard/var.c` | `:806` `php_error_docref(NULL TSRMLS_CC, E_NOTICE, "Error at offset %ld of %d bytes"` | *same, with `(char*)p` added* | variant 0.97 |
| B | ph63 | CRASH-002 | `fd5bd37ab129` | `ext/standard/array.c` | `:1062` `zend_hash_move_forward_ex(target_hash, &pos);` | `zv = zend_hash_get_current_data_ex(target_hash, &pos);` | variant 0.75 |
| B | ph65 | CRASH-118 | `630f9c33c236` | `ext/standard/var_unserializer.c` | `:181` `zend_hash_update(ht, Z_STRVAL_P(key), Z_STRLEN_P(key) + 1, &data, sizeof(dat` | `zend_hash_update(ht, Z_STRVAL_P(key), Z_STRLEN_P(key) + 1, &data,` | variant 0.86 |
| B | ph75 | LOGIC-027 | `40b8105cca1f` | `Zend/zend_compile.c` | `:2959` `zend_hash_next_index_insert(result->u.constant.value.ht, &element, sizeof(zv` | `zend_hash_next_index_insert(Z_ARRVAL_P(result), &expr, sizeof(zval *), NULL)` | variant 0.75 |
| B | ph77 | CRASH-057 | `8365e71cb92b` | `Zend/zend_execute.c` | `:535` `T(result->u.var).var.ptr_ptr = &value;` | `T(result->u.var).var = &T->str_offset.str;` | variant 0.65 |
| B | ph77 | CRASH-151 | `f5f8cba8e978` | `Zend/zend_execute.c` | `:380` `PZVAL_UNLOCK(value);` | `PZVAL_LOCK(EG(error_zval_ptr));` | variant 0.63 |
| **–** | ph18 | CRASH-011 | `f7d1d3ef445e` | `ext/standard/formatted_print.c` | `:211` `memcpy(&(*buffer)[*pos], add, copy_len + 1);` | *(nothing within 0.35)* | ⚠ none |
| **–** | ph32 | CRASH-089 | `bd2e99ee50ed` | `ext/standard/html.c` | `:108` `static entity_table_t ent_uni_338_402[] = {` | *(nothing within 0.35)* | ⚠ none |
| **–** | ph39 | CRASH-037 | `4d2278143a08` | `Zend/zend_exceptions.c` | `:339` `zend_hash_apply_with_arguments(Z_ARRVAL_P(trace), (apply_func_args_t)_build_` | *(nothing within 0.35)* | ⚠ none |
| **–** | ph46 | CRASH-053 | `ff5620524c94` | `Zend/zend_execute.c` | `:283` `if ((*object_ptr)->type == IS_NULL` | `case IS_NULL:` | ⚠ none — **but see §4: `:1632` is in this patch's `zend_vm_def.h`** |
| **–** | ph48 | LOGIC-014 | `b4dba12d3407` | `Zend/zend_builtin_functions.c` | `:1420` `SEPARATE_ZVAL_TO_MAKE_IS_REF(arg);` | *(nothing within 0.35)* | ⚠ none |
| **–** | ph63 | CRASH-022 | `18a0d46a1b44` | `ext/standard/array.c` | `:546` `args[0] = (zval **) f->pData;` | *(nothing within 0.35)* | ⚠ none |
| **–** | ph64 | CRASH-086 | `562f886ecb14` | `ext/standard/basic_functions.c` | `:2135` `tick_fe->calling = 0;` | `zval *func2 = tick_fe2->arguments[0];` | ⚠ none |
| **–** | ph71 | CRASH-067 | `8ce349b8e03c` | `Zend/zend_execute.c` | `:2243` `zval **value_ptr_ptr = get_zval_ptr_ptr(&opline->op2, EX(Ts), BP_VAR_W);` | `**EG(return_value_ptr_ptr) = *retval_ptr;` | ⚠ none |
| **–** | ph79 | CRASH-072 | `d5bb03b11a96` | `main/streams/streams.c` | `:1403` `zend_hash_copy(FG(stream_wrappers), &url_stream_wrappers_hash, NULL, &tmpwra` | `le_stream = zend_register_list_destructors_ex(stream_resource_regular_dtor,` | ⚠ none |
| **–** | ph80 | CRASH-141 | `e000da960b5c` | `Zend/zend_object_handlers.c` | `:75` `call_args[0] = &member;` | `tmp_member = *member;` | ⚠ none |

⭐ **One row of that table separates the corpus column from the catalogue's own
R1h, and the screen puts them on opposite sides.** `ph32`/CRASH-089's **corpus
column** is `bd2e99ee50ed` — excluded above. The **catalogue's** R1h, from
`TASK_PHP_023` §2.6 / F53, is **`56adfe1f3cf1`**. Run against the same corpus
cell (fetched for this check; three `curl`s total, §10.11):

```
$ python3 .temp/php30/preimage_screen.py --sha 56adfe1f3cf1 --label ph32 \
      --cell 'ext/standard/html.c:108 (undersized literal) + ext/standard/html.c:398 …'
 verdict: CANDIDATE
 hits   : [(108, 'static entity_table_t ent_uni_338_402[] = {')]     <- byte-identical to 5.0.0
 misses : [(398, …), (402, …), (900, …)]
```

**The column's commit is excluded; the catalogue's is not, and its pre-image
carries 5.0.0's `:108` verbatim.** ⚠ **But `ph32`'s exclusion is in tier `–`**,
so the screen's own evidence does not *prove* the negative half — the agreement
with F53 is corroboration, not proof, and I am not upgrading it. (F53 also says
`56adfe1f3cf1` repairs only **one of `ph32`'s three tables**; the screen has
nothing to say about the other two, whose sites are not in this cell.)

⚠ **`ph22` and `ph95` are the same commit against the same cited line** — `ph95`
resolves through `merged_members` to CRASH-014's corpus row, so the two records
are literally identical. See §6.

---

## §6 §5 — `ph95`, run on all three, and it comes out SETTLED

⚠ **First, a thing the task's framing does not say and a build task needs to
know.** `ph95`'s catalogue id is **`V5C-015`, one of the three ids `RECAP_PHP.md`
F38 records as resolving only through `merged_members`** — so
`fixsurvey.py::load_corpus` maps it onto **CRASH-014's row**, which is `ph22`'s.
The sweep's `ph95` record therefore carries `ph22`'s cell
(`ext/standard/pack.c:247`) and `ph22`'s sha. **The 169-record sweep says nothing
about `ph95`'s own sites `:212`, `:214`, `:262`.** I ran those separately, from
`CATALOGUE.md:473-478`, with the tool's manual mode — and the report says
`⚠ MANUAL citation, not the corpus's` on every such run.

5.0.0 text, from the tarball (`sha256 5783e0c0…d6919`, verified by the tool
before every run):

```
:212        currentarg += arg;
:214        if (currentarg > argc) {
:262        outputpos += arg * 2;   /* 16 bit per arg */
```

| candidate | date | screen | what its pre-image carries |
|---|---|---|---|
| `6d98fc38b53` Stefan Esser, *"Fixed: removed possible integer over-/underflows"* | 2004-11-28 | **CANDIDATE** | **`:262` byte-identical** (`outputpos += arg * 2;	/* 16 bit per arg */`). `:212` misses (nearest `outputpos += arg;`), `:214` misses |
| `db420cb6a14` Christoph M. Becker, *"Fix #78833: Integer overflow in pack causes out-of-bound access"* | 2019-11-19 | **CANDIDATE** | **`:212` byte-identical** (`currentarg += arg;`). `:214`'s nearest is **`if (currentarg > num_args) {`** — the same guard with `argc` renamed. `:262` gone (`INC_OUTPUTPOS` by then) |
| `865739e5b196` *"Fix GH-18976: pack with h or H format string overflow"* — **what the corpus column names** | 2025 | ⛔ **NOT-THE-REPAIR, DECISIVE** | **none of the three.** `same_function` fires: the hunk is in `PHP_FUNCTION(pack)`, so the window reaches the site and all three lines are absent from the tree it was diffed against |

### ⭐ VERDICT: `ph95`'s R1h is `db420cb6a141876b2f7d101051fb01934a28071a`

**Named upstream artefacts, per §C — not a tag that suits:**

1. **A bug number in the subject** — `#78833`, *"Integer overflow in pack causes
   out-of-bound access"*.
2. **A regression test INSIDE the commit** —
   `ext/standard/tests/strings/bug78833.phpt`, whose body is
   `var_dump(pack("E2E2147483647H*", 0x0, 0x0, 0x0));` expecting
   `Warning: pack(): Type E: too few arguments`. **That is `ph95`'s trigger
   shape**: a huge repeat count defeating the argument-count guard.
3. **A NEWS entry INSIDE the commit**.
4. **The guard it adds is `ph95`'s mechanism, exactly** — a *pre-overflow* test
   placed immediately before the wrapping add:

```diff
 				if (arg < 0) {
 					arg = num_args - currentarg;
 				}
-
+				if (currentarg > INT_MAX - arg) {
+					goto too_few_args;
+				}
 				currentarg += arg;
 
 				if (currentarg > num_args) {
+too_few_args:
```

   `CATALOGUE.md:474` predicted the shape without the sha: *"`db420cb6a14`
   (2019, bug #78833) adds `if (currentarg > INT_MAX - arg)` before `:212`"*.
   **Confirmed from the bytes, and the pre-image proves it is diffed against a
   tree that still has 5.0.0's `currentarg += arg;`.**

**And the catalogue's *"neither repairs the other"* is now byte-evidenced.**
`6d98fc38b53` touches `:262` and its pre-image does not carry `:212`/`:214`;
`db420cb6a14` touches `:212`/`:214` and its pre-image does not carry `:262`.
**Two disjoint repairs, fifteen years apart.**

⚠ **What I did NOT settle, and a build task owes it.** Is `db420cb6a14`
**complete** for `ph95`? It guards `currentarg += arg` and leaves `:262`
unguarded — which is `ph22`'s defect. So a `ph95` R1h that ships only this hunk
will still wrap at `:262` on a different input, and `CATALOGUE.md:478`'s
*"an extraction that lifts only `:262` has rebuilt ph22"* has a mirror image
here. **That is a §C *"the upstream fix is incomplete"* result if it holds, and
`PROTOCOL_PHP.md` §C says that is one of the strongest results a row can carry
— but I did not measure it and it is INFERENCE.** Also a backport detail: the
2019 hunk's `goto too_few_args;` targets a label inside `if (currentarg > argc)`,
and 5.0.0's arm has an extra `efree(argv);` the 2019 arm does not.

### ⭐ Bonus: `ph22`'s R1h now has a sha

`FIXSURVEY_001.md` settled `ph22` as *"the 5.1.0 arrival of `INC_OUTPUTPOS`"* and
had **no commit**. `6d98fc38b53c0ce803bf5cc8de05e2083eb6cd41` **is** that
arrival — it defines `INC_OUTPUTPOS` (`+#define INC_OUTPUTPOS(a,b)`, the exact
body `FIXSURVEY_001.md:120` quotes) and rewrites every `outputpos +=` in
`PHP_FUNCTION(pack)` to use it. Run against `ph22`'s own cell:

```
$ python3 .temp/php30/preimage_screen.py --sha 6d98fc38b53 --label ph22 \
      --cell 'ext/standard/pack.c:247'
 "verdict": "CANDIDATE",   "hits": [[247, "\t\t\t\toutputpos += (arg + 1) / 2;\t\t/* 4 bit per arg */"]],
 "misses": [],  "patch_files": ["ext/standard/pack.c", "main/php.h"]
```

**5.0.0's `:247` is in that commit's pre-image byte-identical.** ⚠ **This is a
fingerprint of the repair, not a proof of commit identity on `PHP_5_1`** — the
same bound `_029` §5.1 put on its own 5.0.x identifications.

---

## §7 ⚠ A FALSE EXCLUSION I SHIPPED, FOUND, AND GUARDED

`PROTOCOL.md` definition-of-done 5 asks for what went wrong.

**The first working version of the screen called `ph73`/CRASH-100 /
`5d804d163ae9` `NOT-THE-REPAIR`.** `TASK_PHP_029` §2 says of that exact commit:
*"the id's own `fix_commit` touches it? **YES, and its pre-image is
byte-identical to 5.0.0**"*. **A wrong exclusion — the one direction this screen
may not fail in.**

**Cause: the citation parser, not the matching rule.** The cell is

```
ext/standard/streamsfuncs.c:728 (and 735, 742)
```

and `735` / `742` have **no colon and no path**, so a `path:N` parse cannot see
them. Reading `:728` alone (`zval zvs[6];`, which the fix keeps) gave zero hits.
Both of the bare ones **are** in the pre-image:

```
 		INIT_ZVAL(zvs[i]);
 		ps[i] = &zvs[i];            <- 5.0.0 :735
 		ptps[i] = &ps[i];
+		MAKE_STD_ZVAL(ps[i]);
-		ZVAL_STRING(ps[2], xmsg, 0);   <- 5.0.0 :742
+		ZVAL_STRING(ps[2], xmsg, 1);
```

**The repair.** Every bare number in the cell that is a valid line of the defect
file is added to the search set and **flagged** as residual. ⚠ Some of those are
certainly not line numbers (`2014` from *"the 2014 fix commit's line numbers"*,
`5`/`0`/`0` from *"php-5.0.0"*, and `ph01` picks up the licence header at
`var_unserializer.c:16`). **That is the safe direction**: a spurious extra line
can only turn an exclusion into a CANDIDATE — it costs coverage, never
soundness. **Measured**: over 170 records the repair moved exactly **two**
verdicts, `ph73`/CRASH-100 and `ph51`/CRASH-087 (whose cell cites
*"`glob_t globbuf;` at 369 and GLOB_FLAGMASK at 164"*, and `164` hits). **So it
is precise, not a blunderbuss.**

**Guarded as selftest N0**, quoting `_029` §2 as its authority.

⚠ **The general lesson, and it is `PROTOCOL_PHP.md` §F6's *"ask about a FUNCTION,
not about text"* in a new place: a screen is only as good as its citation
parser, and the corpus's `c_file_line` is PROSE.** Only **58 of 166** cells are
a bare `path:N`; the rest carry secondary sites, faulting frames, corrections of
their own claimed line numbers, and commentary. **24 records still have digits
the parser reads as residual rather than as citations**, and they are listed in
`screen.json` per record (`residual_numbers`).

---

## §8 §7.3 — does this just re-derive the date selector? **NO**

```
    records with a fetched patch          : 169
    records dated 2010 or later           : 45
    NOT-THE-REPAIR records                : 43
    NOT-THE-REPAIR AND late               : 14
    NOT-THE-REPAIR AND NOT late           : 29   <- the coverage the date selector MISSES
    late AND CANDIDATE                    : 24   <- late records the screen could NOT exclude
```

**29 of 43 exclusions are dated before 2010** — 2004 (1), 2005 (4), 2006 (5),
2007 (7), 2008 (6), 2009 (6). **The date selector cannot see two thirds of what
the screen finds.** Conversely **24 late records survive the screen**: the date
says *suspect*, the bytes say *cannot rule out*.

Against the id-spread selector, per row:

```
    rows with >1 distinct fix_commit (id-spread) : 30
    rows with at least one exclusion             : 34
    exclusion AND id-spread                      : 16
    exclusion, NOT id-spread                     : 18
    id-spread, NO exclusion                      : 14

    exclusion rows the UNION of both selectors misses:
       ['ph05','ph06','ph12','ph13','ph28','ph32','ph44','ph53','ph64','ph74','ph91','ph101']
```

⚠⚠ **Twelve rows carry an exclusion and are invisible to BOTH selectors.**
`_029` measured the date and id-spread selectors as nearly orthogonal (overlap
10 of 31 and 30) and recommended **neither as a sweep**; this is a **third**
axis, largely orthogonal to both, and unlike them it is **a test rather than a
ranking**. ⭐ **Ten of those twelve are in tier A or A+B** — `ph05 ph06 ph12
ph13 ph28 ph44 ph53 ph74 ph91 ph101`; only `ph32` and `ph64` are in tier `–`.
**So the coverage the two selectors miss is not the weak part of the screen's
output.**

⚠ **What this does NOT say.** It does not say the 43 commits are wrong about
their rows. `PROTOCOL_PHP.md` §3.5's hazard — a **`c_file_line` that names the
FAULT site rather than the MECHANISM** — is live here, and `ph63` is in the list
**twice** (`CRASH-002` and `CRASH-022`), which is the standing example of that
shape. For any such record the screen looked in the right file at the wrong
concept. **Per record, and defensible per record only.**

---

## §9 §6.4 — should this run inside `fixsurvey.py`? **No. Keep it separate.**

**Argue the cost, as §6.4 asks.** Measured on this box:

| | |
|---|---|
| `python3 .tasks-php/fixsurvey.py --offline` | **0.1 s** |
| `python3 .temp/php30/preimage_screen.py --all` | **2.2 s** |
| `--selftest` | **0.7 s** |

**That is a 22× slowdown of a tool agents run mid-task**, and the cost is
structural rather than incidental: the screen must **sha256 and gunzip the
5.6 MB tarball** (`SOURCES.md` §1 pins it and refuses any other), which
`fixsurvey.py` neither needs nor knows about. Folding it in makes a
network-free, tarball-free, 0.1 s lookup depend on a 5.6 MB artefact under
**another project's gitignored `.temp/`** (`SOURCES.md` §1's own hazard) — so
`fixsurvey.py` would start *failing* on a box where the tarball has been
cleaned, for a question it was not asked. 2.2 s is not much in itself; **turning
a hard dependency-free tool into a soft-dependency one is.**

There is a second and better reason. `fixsurvey.py` answers **one crisp
mechanical question** — *does the fix commit touch the defect's file?* — and its
value is that its answer needs no interpretation. **The screen's answer needs
interpretation**: three outcomes, a decisiveness tier, and 10 of 43 exclusions
that a reader must be told not to treat as exclusions. Printing that inside a
routine preflight-adjacent lookup is how a nuanced result becomes a number
someone quotes.

**Recommendation:** promote the tool to `.tasks-php/preimage_screen.py`
(⚠ **the manager promotes it; I did not put it there**), keep it a separate
command, and add **one line** to `fixsurvey.py`'s output pointing at it —
`FIXSURVEY_001.md`'s *"a `same-file` verdict is a starting point, never a
licence"* is exactly where that pointer belongs. Under `PROTOCOL_PHP.md` §H the
tool is a validator, so it ships with its ten negatives, run, above.

---

## §10 ⚠ What I did NOT do, and what I am unsure of

1. ⚠⚠ **The task's §1 framing is stronger than what I can support, and §3 is
   the correction.** *"If the pre-image does not contain the 5.0.0 text, that
   commit is not the repair"* is **not** a proof of exclusion on its own,
   because the median pre-image behind an exclusion is 14 lines. **33 of 43
   carry positive evidence that the window reaches the site; 10 do not.** I
   report the 10 separately rather than counting them.
2. ⚠ **I did not verify a single exclusion against the release tags.** Every
   verdict here is derived from the commits' own bytes and the pristine
   tarball. `PROTOCOL_PHP.md` §F5(iii)'s tag check is a **different** question
   (*what removed the defect?*) and the screen does not answer it — it only
   removes wrong answers.
3. ⚠ **CANDIDATE means only *"could not exclude"*.** 106 records are CANDIDATE
   and **nobody has looked at 100 of them.** Do not read 106 as 106 confirmed
   fixes.
4. ⚠ **`ph95`'s completeness is INFERENCE** (§6). I did not build anything, did
   not run the trigger, and did not check whether `:262` is separately reachable
   after `db420cb6a14`'s guard. **Do not write it into a finding until it is
   measured.**
5. ⚠ **The `same_function` test rests on git's `xfuncname` heuristic**, which I
   re-implemented as *"nearest preceding line starting at column 0 with a
   letter, `_` or `$`"*. That is git's documented **default** C behaviour, but
   PHP's tree has no `.gitattributes` `diff=cpp` that I checked, and the
   evidence-carrying comparison is tolerant (prefix match either way) because
   git truncates long headers. **A mismatch would show as a missing tier-A
   record, never as a false exclusion** — the failure direction is safe, but it
   is a heuristic and I am naming it as one.
6. ⚠ **`bracketed`'s 60-line window and the 0.60 similarity cutoff are
   parameters.** The sensitivity of the second is printed (§3); the first fires
   alone on exactly one record, so nothing much rests on it.
7. ⚠ **2 records return `NO-SPAN` and I did not chase either**:
   `ph04`/CRASH-110 cites `ext/standard/url.c:132`, which at 5.0.0 is the `*/`
   closing a comment — nothing to match; and `ph72`/CRASH-112's `:0` sentinel
   (§4). **The first is a corpus citation that is one or two lines off** and is
   worth a manager's eye.
8. ⚠ **I did not adjudicate any row, edit any catalogue, or propose an R1h for
   anything but `ph95`** — which §5 asked for.
9. ⚠ **The screen has no opinion about `ph36`** (no sha) and cannot acquire one.
10. ⚠ **Files I wrote outside `.temp/php30/`**: exactly one —
    `.temp/mgr/batch/fixsurvey.json`, regenerated by
    `python3 .tasks-php/fixsurvey.py --offline`, which the task file §2
    instructs. It is gitignored scratch and its content is unchanged from the
    manager's own run (`resolved: 169 same-file: 150 OTHER-FILE: 19`). I also
    created `.temp/php30/patches/` with three patches not in the shared cache.
11. ⚠ **I fetched from the network for `ph95`.** The task says the sweep is
    network-free and it is — all 169 records ran from
    `.temp/mgr/batch/patches/`. §5's `6d98fc38b53` and `db420cb6a14` are not in
    that cache (nothing had ever needed them) and `56adfe1f3cf1` was fetched to
    check the `ph32` corroboration. Three `curl`s, same URL form as
    `fixsurvey.py::fetch`, cached under `.temp/php30/patches/`.

### One disagreement with the task file, disclosed per rule 2

**§6.2 asks for *"a table of every record the screen calls NOT-THE-REPAIR"* and
says *"that table is the deliverable; the counts are not"*. I have shipped the
table — and I think the counts in it are worth less than the task assumes and
the TIER is worth more.** A reader who takes "43 exclusions" away from this
report has taken away a number that is wrong by 10. §3 is the deliverable I
would defend; §5 is the artefact.

### Brackets (`PROTOCOL_PHP.md` §E1)

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ git status --porcelain
?? .tasks-php/TASK_PHP_029_REPORT.md            <- not mine
?? patterns-php/ph29-recvfrom-alloc/            <- the concurrent agent's, untouched
?? results-php/ph29-recvfrom-alloc.json         <- ditto
?? results-php/preflight/ph07.preflight.json    <- not mine; I ran no gate.py
?? results-php/preflight/ph29-recvfrom-alloc.preflight.json  <- ditto
```

⚠ **I deliberately did NOT run `gate.py --tool measure --check-stale`, the same
disclosed departure `_029` §5 made and for the same two reasons**: it appends to
`results-php/preflight/_norow.preflight.json`, a **committed** file (§E's *"not
read-only"* row), and another agent is mid-build in `results-php/` — the `??`
lines above are its work. **This task produced no record for it to check.** The
PAT bracket is the one that carries information here: it proves the frozen tree
is untouched.

---

## §11 Evidence index — everything under `.temp/php30/`

| path | what |
|---|---|
| `preimage_screen.py` | the tool, with `--selftest` |
| `crosstab.py`, `audit_parser.py`, `mktable.py` | the three analyses |
| `00-fixsurvey.log` | `fixsurvey.py --offline`, the 170 records' source |
| `01-selftest.log` | §4's four + N0–N9, the run pasted in §2 |
| `02-all.log` | the full sweep, every exclusion with **all** its cited lines |
| `03-ph95.log` | §5's three `ph95` candidates, plus the `ph32` / `56adfe1f3cf1` run appended at the end |
| `04-crosstab.log` | §6.3 / §7.3, the tiering and its sensitivity |
| `05-audit.log` | 1892 hunks vs `@@ -a,b`, 0 mismatches; pre-image sizes |
| `06-table.md` | §5's table, generated |
| `screen.json` | all 170 records, machine-readable |
| `patches/` | 3 patches, re-fetchable |

Per `CLAUDE.md` rule 1 nothing here is a binary; the generators are the evidence
and the `.json`/`.log`/`.md` are re-derivable from them in ~3 s.
