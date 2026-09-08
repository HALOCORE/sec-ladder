# FIXSURVEY_001 — every catalogued row's upstream fix, surveyed once

**Author: the manager.** `ph07` cost a whole task to the question *"where is the
upstream fix?"* (F34), and the answer turned out to be **a different file**
(F38). **That question is now answered mechanically for the whole catalogue**, so
no row engineer repeats it.

```sh
python3 .tasks-php/fixsurvey.py            # fetch what is missing, report
python3 .tasks-php/fixsurvey.py --offline  # from the patch cache only
```

⚠⚠ **WHAT THIS ANSWERS AND WHAT IT DOES NOT.** It answers *"does the corpus's
`fix_commit` touch the same FILE as the defect's `c_file_line`?"* — **it does
NOT answer *"is this the commit that removes the 5.0.0 defect?"***. F38 half 2
showed **2 of the 4 commits actually checked are LATER fixes**, and only a tag
comparison settles that. **A `same` verdict is a starting point, never a licence.**

## Summary

| | |
|---|---|
| catalogued rows with a parseable corpus id | **84** of 91 |
| unmapped (a limit of the parse, not the corpus) | 7 — `ph48 ph52 ph66 ph82 ph83 ph84 ph85` |
| resolved (patch fetched and read) | **83** · ⚠ **zero fetch failures** |
| fix touches the **same file** as the defect | **77** |
| ⚠ fix is in **another file** — the `ph07` shape | **6** |
| ⚠⚠ **no sha exists** | **1** — `ph36`, cell reads `(bison-regeneration; no single commit)` |

### ⚠ The 6 rows a function-name search cannot find

| row | id | sha | defect file | fix touches | subject |
|---|---|---|---|---|---|
| `ph07` | CRASH-124 | `cb3cca21b345` | `libmbfl/mbfl/mbfilter.c` | `ext/mbstring/mbstring.c` | Fixed possible memory corruption inside mb_strcut() |
| `ph27` | CRASH-009 | `21452a5401e9` | `ext/standard/reg.c` | `ext/ereg/ereg.c` | ⚠ **the file was also MOVED** — bug #73284, 2016 |
| `ph54` | CRASH-143 | `fc96c7f7fa18` | `Zend/zend_execute.c` | `zend_compile.c`, `.h`, `zend_language_parser.y`… | a **compiler**-side fix for an **executor** defect |
| `ph88` | CRASH-062 | `2e1a2438b5e6` | `Zend/zend_execute_API.c` | `Zend/zend.c` | bug #35634 |
| `ph89` | CRASH-034 | `e0b0ae9ce7c5` | `Zend/zend_execute_API.c` | `Zend/zend.c` | bug #25922 |
| `ph90` | CRASH-029 | `32c2e664a6ec` | `ext/standard/array.c` | `Zend/zend_execute_API.c` | bug #30266 |

⭐ **Four of the six cross a subsystem boundary** (ext ↔ Zend, executor ↔
compiler). **`R1h` for these rows is a guard that does not live in the kernel's
own translation unit**, which is a real fidelity question each must state — the
one `ph07` is answering now.

### ⚠ 9 fixes touch ≥ 5 files (F34's "inside a rewrite" shape)

```
ph24  e155585e6e13   16 files  Reimplemented date and gmdate with new timelib code
ph16  99e290f882c9   10 files  Bug #24189: unsafe select(2) usage -- avoided by using poll(2)
ph26  4d44a5b71dd7    9 files  MFH: use BSD licensed implementation of double-to-string
ph23  ff9d0fcc783c    8 files  is_numeric_string() optimization
ph39  d6505acbf5ff    5 files  Fixed bug #64821 Custom Exceptions crash when internal
ph54  fc96c7f7fa18    5 files  foreach($a as $key => $val) optimization
ph65  1ac4d8f2c632    5 files  fix bug #65481 (shutdown segfault due to serialize)
ph73  3d7b0bab28e7    5 files  Fixed memory allocation bugs related to magic object handlers
ph76  1d33a3e95e4e    5 files  Fixed bug #31158 (array_splice on $GLOBALS crashes)
```

⚠ **`ph24` and `ph26` are also `history_status: fixed-by-rewrite`** — the corpus
and this survey agree, from independent fields.

### ⭐ How long PHP shipped these — and why 31 % of the corpus needs the tag check

Fix year, over the 83 resolved:

```
2004:9 2005:19 2006:7 2007:10 2008:5 2009:7 2010:1 2011:2 2012:2 2013:5 2014:6 2015:2 2016:5 2017:1 2018:1 2025:1 —:1
```

**26 of 83 (31 %) were fixed in 2010 or later**, against a 5.0.0 release of
**2004-07-13**. ⚠⚠ **Each of those is one of two very different findings and
this survey cannot tell them apart:**

- **(a) the defect really survived 6–21 years** — a headline for the crash
  course; or
- **(b) the named commit is a LATER hardening** and the real removal happened
  earlier — **exactly what `ph21`'s 2015 commit turned out to be** (F38).

**Only the tag comparison distinguishes them, and it must be run per row.**

### ✅ `ph22` was the standout, and settling it produced case (b)

This file first said: *"`ph22` (`pack`, `pack.c:247`) — `865739e5b196`, 2025 …
if that is the same defect, PHP shipped it for 21 years"*, flagged unverified.
**Settled across eight tags. It is case (b), and the 21 years is withdrawn:**

```
5.0.0   outputpos += (arg + 1) / 2;                  <-- ph22's defect, NO CHECK
5.1.0   INC_OUTPUTPOS((arg + 1) / 2, 1)              <-- the checking macro ARRIVES
5.2.0   INC_OUTPUTPOS((arg + (arg % 2)) / 2, 1)      <-- +1 over-counted for even arg
5.3.0 … 8.4.0   unchanged, ~15 years
2025    INC_OUTPUTPOS((arg / 2) + (arg % 2), 1)      <-- 865739e5b196, the CSV's cell
```

**R1h for `ph22` is the 5.1.0 arrival of `INC_OUTPUTPOS`**, whose body is
`if ((a) < 0 || ((INT_MAX - outputpos)/(b)) < (a)) { … RETURN_FALSE; }`.
**The third confirmed instance of F38 half 2** — on the row picked as most
likely to be the exception.

⭐ **The 2025 commit is still a finding, and a better one.** What survived
5.1.0 → 2025 is signed-overflow UB **in the macro's ARGUMENT**:
`(arg + (arg % 2))` overflows at `arg == INT_MAX` *before* the guard runs, so an
explicitly overflow-checking macro receives an already-wrapped value. ⚠⚠ **That
is `ph20`'s catalogued shape in a second function** — *"the wrap collapsed inside
`safe_emalloc`'s first argument, so the wrapper is present and bypassed"* — and
here it lasted nineteen years **inside the guard meant to prevent it.**

⚠ **`ph49` and `ph50` resolve to the SAME corpus id and the same commit**
(CRASH-153 / `86434be9462c`). Two catalogue rows from one corpus row is not
necessarily wrong — the catalogue splits by *mechanism* — **but nobody has
checked that these two are distinct C mechanisms.** Flagged, not judged.

## The full table

⚠ `year` is the **commit** year, not a release. `⚠late` = ≥ 2010. `⚠Nf` = the
fix touches N ≥ 5 files.

| row | id | `fix_commit` | year | files | verdict | subject |
|---|---|---|---|---:|---|---|
| ph01 | CRASH-066 | `6a7cc8ff8582` | **2016** ⚠late | 4 | same | Fix bug #73052 - Memory Corruption in During |
| ph02 | CRASH-120 | `16b3003ffc63` | **2016** ⚠late | 3 | same | Fix bug #73825 - Heap out of bounds read on unserialize in |
| ph03 | CRASH-115 | `f95c1df58349` | **2004** | 1 | same | Fixed bug #29821 (Fixed possible crashes in |
| ph04 | CRASH-110 | `e1ba58f068f4` | **2015** ⚠late | 1 | same | Fix bug #70480 (php_url_parse_ex() buffer overflow read) |
| ph05 | CRASH-102 | `29b9d79c2ff6` | **2007** | 1 | same | Fix chunk_split fix - avoid using floats Fix money_format  |
| ph06 | CRASH-091 | `9d1986647629` | **2009** | 2 | same | - Fixed bug #49785 (insufficient input string validation o |
| ph07 | CRASH-124 | `cb3cca21b345` | **2005** | 1 | ⚠ **OTHER-FILE** | Fixed possible memory corruption inside mb_strcut(). |
| ph08 | CRASH-016 | `091b7642c2d8` | **2014** ⚠late | 2 | same | Fix bug #67249: printf out-of-bounds read |
| ph09 | CRASH-033 | `9966587aafae` | **2005** | 2 | same | Fixed bug #29015 (Incorrect behavior of member vars(non |
| ph10 | CRASH-094 | `3e9cb6a4a550` | **2014** ⚠late | 3 | same | Fix bug #67250 (iptcparse out-of-bounds read) |
| ph11 | CRASH-145 | `0eaa26fc3153` | **2004** | 1 | same | String offset starts with 0, fix isset($str[$len]) |
| ph12 | CRASH-108 | `896a5216d73d` | **2006** | 3 | same | fix possible substr_compare() crash add new tests |
| ph13 | CRASH-136 | `f002287eb39a` | **2009** | 3 | same | - MFH: #48378, exif_read_data() segfaults on certain |
| ph14 | CRASH-134 | `dbccc8c112e0` | **2011** ⚠late | 4 | same | - fix bug #54002, exif_read_data crashes on crafted tags |
| ph15 | CRASH-096 | `c933634253b4` | **2005** | 3 | same | Fixed crash inside stream_get_line() when length parameter |
| ph16 | CRASH-098 | `99e290f882c9` | **2004** | 10 | same ⚠10f | Fix for Bug #24189: possibly unsafe select(2) usage. We av |
| ph17 | CRASH-127 | `4e68b2c52b1f` | **2017** ⚠late | 1 | same | Patch from the upstream git |
| ph18 | CRASH-001 | `085af567107d` | **2008** | 1 | same | fix integer overflow in length calculation |
| ph19 | CRASH-006 | `4c968c6ddd2d` | **2016** ⚠late | 2 | same | Fix bug #72138 - Integer Overflow in Length of String-type |
| ph20 | CRASH-007 | `9282d4add60b` | **2007** | 3 | same | Fixed an interger overflow inside chunk_split(), identifie |
| ph21 | CRASH-107 | `c591f022f8ab` | **2015** ⚠late | 3 | same | Fix bug #69403 and other int overflows |
| ph22 | CRASH-014 | `865739e5b196` | **2025** ⚠late | 3 | same | Fix GH-18976: pack with h or H format string overflow. |
| ph23 | CRASH-157 | `ff9d0fcc783c` | **2006** | 8 | same ⚠8f | is_numeric_string() optimization |
| ph24 | CRASH-008 | `e155585e6e13` | **2005** | 16 | same ⚠16f | - Reimplemented date and gmdate with new timelib code. - |
| ph25 | CRASH-095 | `a9f5ad7e8772` | **2008** | 2 | same | MFB: Fixed bug #44242 (metaphone('CMXFXM') crashes PHP) |
| ph26 | CRASH-149 | `4d44a5b71dd7` | **2006** | 9 | same ⚠9f | MFH: use BSD licensed implementation of double-to-string |
| ph27 | CRASH-009 | `21452a5401e9` | **2016** ⚠late | 1 | ⚠ **OTHER-FILE** | Fix bug #73284 - heap overflow in php_ereg_replace functio |
| ph28 | CRASH-147 | `0ebe3a7690a7` | **2009** | 1 | same | Extend the previously added large string concatenation |
| ph29 | CRASH-097 | `445daac3ab1a` | **2004** | 1 | same | Fixed possible crash in stream_socket_recvfrom() when leng |
| ph30 | CRASH-133 | `17b39638d0a6` | **2011** ⚠late | 3 | same | - Fixed bug #60337 bcscale related crashed on 64bits |
| ph31 | CRASH-135 | `f13d9c0e033e` | **2010** ⚠late | 3 | same | - Fixed bug #53574 (Integer overflow in SdnToJulian, |
| ph32 | CRASH-089 | `bd2e99ee50ed` | **2005** | 1 | same | - Fixed bug #29119 (html_decode_entities handling of |
| ph33 | CRASH-128 | `b7259b71b430` | **2016** ⚠late | 3 | same | Fix #72994: mbc_to_code() out of bounds read |
| ph34 | CRASH-122 | `9daaedc12526` | **2005** | 2 | same | Fixed bug #34645 (ctype corrupts memory when validating la |
| ph35 | CRASH-130 | `ae57857ebac7` | **2009** | 2 | same | fix bug #47662: support more than 127 named subpatterns |
| ph36 | CRASH-005 | `(bison-regen` | **—** | — | ⚠⚠ **NO SHA** | — |
| ph37 | CRASH-018 | `7d109bc62761` | **2006** | 1 | same | fix #38322 (reading past array in sscanf() leads to arbita |
| ph38 | CRASH-077 | `ff1687731dee` | **2005** | 2 | same | - Fixed bug #32021: Crash caused by range('', 'z') |
| ph39 | CRASH-036 | `d6505acbf5ff` | **2013** ⚠late | 5 | same ⚠5f | Fixed bug #64821 Custom Exceptions crash when internal |
| ph40 | CRASH-093 | `84f9fe0fdcc6` | **2014** ⚠late | 2 | same | Fix bug #67498 - phpinfo() Type Confusion Information Leak |
| ph41 | CRASH-039 | `a11606b18fd2` | **2012** ⚠late | 3 | same | Fix Bug #63762 Sigsegv when Exception::$trace is changed b |
| ph42 | CRASH-144 | `c3dbe168fb46` | **2004** | 1 | same | Fix for 30457 |
| ph43 | CRASH-079 | `2c36778e47b6` | **2007** | 3 | same | MFH: fix #40191 (use of array_unique() with objects trigge |
| ph44 | CRASH-085 | `af1843f866a5` | **2007** | 3 | same | MFH: fix #40752 (parse_ini_file() segfaults when a scalar |
| ph45 | CRASH-123 | `e8901dc17087` | **2005** | 2 | same | - Fix bug #30573 (compiler warning due to invalid type cas |
| ph46 | CRASH-053 | `ff5620524c94` | **2009** | 4 | same | Fixed bug #47704 (crashes on some "bad" operations with |
| ph47 | CRASH-104 | `cd32b4e2bb54` | **2007** | 3 | same | Fixed bug #42208 (substr_replace() crashes when the same |
| ph49 | CRASH-153 | `86434be9462c` | **2013** ⚠late | 3 | same | Fix bug #65051: count() off by one inside unset() |
| ph50 | CRASH-153 | `86434be9462c` | **2013** ⚠late | 3 | same | Fix bug #65051: count() off by one inside unset() |
| ph51 | CRASH-087 | `8ab99847073d` | **2007** | 2 | same | MFH:- Fixed bug #42365 (glob() crashes with invalid flags) |
| ph53 | CRASH-158 | `be8daf1f47fa` | **2008** | 4 | same | Optimized ZEND_FETCH_CLASS + ZEND_ADD_INTERFACE into singl |
| ph54 | CRASH-143 | `fc96c7f7fa18` | **2005** | 5 | ⚠ **OTHER-FILE** ⚠5f | foreash($a as $key => $val) optimization Removed temorary |
| ph55 | CRASH-023 | `4f68f3774c34` | **2004** | 1 | same | fix crash #29893 |
| ph56 | CRASH-041 | `1e708a5aeb30` | **2004** | 1 | same | Bugfix #29882 isset crashes on arrays |
| ph57 | CRASH-028 | `536260f2c52a` | **2013** ⚠late | 4 | same | Fix bug #65821: By-ref foreach on property access of strin |
| ph58 | CRASH-055 | `35b38598ccb5` | **2005** | 2 | same | Fixed bug #29944 (Function defined in switch, crashes). |
| ph59 | CRASH-082 | `f046cdf3fa15` | **2005** | 3 | same | fix #35821 (array_map() segfaults when exception is throwe |
| ph60 | CRASH-088 | `60fc9c050a44` | **2004** | 1 | same | Fixed bug #29678 (opendir() with ftp:// wrapper segfaults  |
| ph61 | CRASH-155 | `1aab36e3f22a` | **2007** | 3 | same | Fixed bug #42009 (is_a() and is_subclass_of() should NOT c |
| ph62 | CRASH-046 | `4e2c0bc9050c` | **2009** | 1 | same | MFH: fix bug #47353 (crash when creating a lot of objects  |
| ph63 | CRASH-002 | `fd5bd37ab129` | **2018** ⚠late | 2 | same | Revert "Fixed bug #75961 (Strange references behavior)" |
| ph64 | CRASH-086 | `562f886ecb14` | **2007** | 3 | same | MFH: fix #41037 (unregister_tick_function() inside the tic |
| ph65 | CRASH-121 | `1ac4d8f2c632` | **2013** ⚠late | 5 | same ⚠5f | fix bug #65481 (shutdown segfault due to serialize) |
| ph67 | CRASH-160 | `c3a317117ad8` | **2014** ⚠late | 1 | same | Add helper function for updating bucket contents |
| ph68 | CRASH-030 | `d7b30e457a3d` | **2007** | 2 | same | MFH: fix #41421 (Uncaught exception from a stream wrapper |
| ph69 | CRASH-131 | `631da59b5032` | **2005** | 3 | same | Fixed bug #34790 (preg_match_all(), named capturing groups |
| ph70 | CRASH-047 | `41ae8de13666` | **2006** | 3 | same | Fixed bug #39297 (Memory corryption because of indirect |
| ph71 | CRASH-004 | `4f161fe28997` | **2005** | 3 | same | Fixed bug #34137 (assigning array element by reference cau |
| ph72 | CRASH-074 | `37d7df72a62e` | **2012** ⚠late | 3 | same | Fix bug #52719: array_walk_recursive crashes if third para |
| ph73 | CRASH-052 | `3d7b0bab28e7` | **2005** | 5 | same ⚠5f | Fixed memory allocation bugs related to magic object handl |
| ph74 | CRASH-139 | `9a98904ddd0e` | **2006** | 4 | same | Fixed wrong "type" argument to read_property() handler |
| ph75 | CRASH-161 | `ed4c0245c7ca` | **2014** ⚠late | 1 | same | Partial fix for bug #68365 (zend_mm_heap corrupted after |
| ph76 | CRASH-012 | `1d33a3e95e4e` | **2005** | 5 | same ⚠5f | Fixed bug #31158 (array_splice on $GLOBALS crashes) |
| ph77 | CRASH-151 | `f5f8cba8e978` | **2008** | 4 | same | Fixed bug #44660 (Indexed and reference assignment to prop |
| ph78 | CRASH-042 | `41ad9b4d1fdd` | **2008** | 2 | same | Fixed bug #46308 (Invalid write when changing property fro |
| ph79 | CRASH-038 | `6319efa013ec` | **2005** | 3 | same | Fixed bug #34260 (Segfault with callbacks (array_map) + |
| ph80 | CRASH-084 | `336b5f59b6c4` | **2014** ⚠late | 2 | same | Fixed bug #67399 (putenv with empty variable may lead to |
| ph81 | CRASH-142 | `8df40bdb313d` | **2006** | 2 | same | Keeping consistent arg_stack during arguments freeing |
| ph86 | CRASH-065 | `89e53d5ab231` | **2005** | 2 | same | Fixed bug #30080 (Passing array or non array of objects) |
| ph87 | CRASH-068 | `1ea22c90046b` | **2004** | 1 | same | Bugfix #29116 Zend constant warning uses memory after free |
| ph88 | CRASH-062 | `2e1a2438b5e6` | **2007** | 3 | ⚠ **OTHER-FILE** | Fixed bug #35634 (Erroneous "Class declarations may not be |
| ph89 | CRASH-034 | `e0b0ae9ce7c5` | **2005** | 2 | ⚠ **OTHER-FILE** | Fixed bug #25922 (In error handler, modifying 5th arg |
| ph90 | CRASH-029 | `32c2e664a6ec` | **2005** | 1 | ⚠ **OTHER-FILE** | - Fix all incarnations of bug #30266 # most probably we |
| ph91 | CRASH-071 | `e8359d3f904c` | **2009** | 2 | same | - Fixed bug #49142 (crash when exception thrown from |
