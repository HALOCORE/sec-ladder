# UPSTREAM_001 — the upstream repair survey for the batch `ph21 · ph16 · ph12 · ph29`

**Author: the manager.** Written **before** the batch's task files, because
`ph07` cost a whole task to the opposite order: `TASK_PHP_015` reported *"no
`fix_commit` exists"*, the manager had to overturn it against three tags (F34),
and `TASK_PHP_016` now carries the correction as a §2. **Finding the repair is
the expensive half of a row and it is not row-specific work — so the manager
does all four at once, and each row engineer starts from a located fix.**

⚠ **This is EVIDENCE, not a decision.** Nothing here has been through a
reviewer. `PROTOCOL.md` rule 9 keeps it out of `.memory-php/` until it has.
⚠ **It does not settle admission** either — the bar is C-side and per-row.

---

## §0 Method, and how to regenerate every byte

```sh
.temp/mgr/REFETCH.sh          # re-downloads everything cited below
```

Two sources, and **only** these two:

1. **5.0.0 = the pinned tarball** (`patterns-php/SOURCES.md`, sha256
   `5783e0c0…d6919`, re-checked at survey time). Every `file:line` below was
   read out of it, not out of GitHub.
2. **later tags = `raw.githubusercontent.com/php/php-src/<tag>/<path>`**, for
   `php-5.1.0 5.2.0 5.3.0 5.4.0 5.6.0`. ⚠ **A tag is not a commit.** This survey
   brackets each fix to a *release window*; **pinning the commit inside that
   window is the row engineer's job** (`PROTOCOL_PHP.md` §F item 5), and
   `https://github.com/php/php-src/commit/<sha>.patch` fetches while `git fetch`
   of a bare SHA is refused.

⚠⚠ **READ §5 BEFORE YOU GREP ANYTHING.** Two of these four rows live in a file
this box's `grep` reports as empty.

## §1 Citations — all four verified byte-exact against the pinned tarball

| row | catalogue says | at source | |
|---|---|---|---|
| `ph12` | `string.c:4786` | `if (len && offset >= s1_len) {` | ✅ |
| `ph16` | `streamsfuncs.c:541` | `FD_SET(this_fd, fds);` | ✅ |
| `ph21` | `string.c:4120 / :4144 / :4145` | `int result_len;` / the product / the guard | ✅ |
| `ph29` | `streamsfuncs.c:321` | `read_buf = emalloc(to_read + 1);` | ✅ |

✅ **`CATALOGUE.md`'s own `⚠ risk` note on `ph21` is confirmed**: cite
`:4120/:4144/:4145`; `ADJUDICATION_001.md` §0's `:4119/:4143/:4144` is off by one
on all three.

## §1b ⭐ THE COMMITS ARE PINNED AFTER ALL — and two of them are the wrong fix

⚠ **This section was added after §2–§4 were written, and it changes what §6
says is owed.** The corpus index has a **`fix_commit` column**
(`index.csv`, documented at `PLAN_PHP.md:109`) — **all 166 rows carry one**, and
`CRASH-115`'s cell is `f95c1df58349`, the sha `ph03` ships. ⚠ **That is not an
independent cross-check** — `ph03` took its sha from the same corpus's history
layer. **What it is: the one row where the corpus's identifier was confirmed by
MEASUREMENT** (`TASK_PHP_013` applied the patch over 12 600 documents).
All five relevant patches fetched and read (`RECAP_PHP.md` **F38**):

| row | `fix_commit` | date, author | verdict |
|---|---|---|---|
| `ph29` | **`445daac3ab1a`** | 2004-07-28 Ilia | ✅ **exact, minimal** — adds `if (to_read <= 0) … RETURN_FALSE;`, nothing else. **Use it.** |
| `ph16` | **`99e290f882c9`** | 2004-09-17 Wez | ✅ **right fix, big commit** — *"Bug #24189: possibly unsafe select(2) usage… by using poll(2)"*, 10 files / 27 KB; **it introduces `PHP_SAFE_FD_SET`** and applies it at the row's line. **Use it, and cite the hunk, not the commit.** |
| `ph12` | `896a5216d73d` | 2006-04-25 Tony | ❌ **LATER fix.** Its pre-image already reads `if ((offset + len) >= s1_len)` — **the `len &&` short-circuit is already gone.** Fixes bug #33605 instead. **R1h is the earlier change (§3); cite both.** |
| `ph21` | `c591f022f8ab` | 2015-05-10 Stas | ❌ **LATER fix, by nine years.** Adds `if (result_len > INT_MAX)` to a function that is already `size_t` + `safe_emalloc`. **R1h is the 5.2.0 change (§2); cite both.** |
| *(`ph07`)* | **`cb3cca21b345`** | 2005-12-15 Ilia | ⭐ *not this batch, but the same lookup:* *"Fixed possible memory corruption inside `mb_strcut()`"* — **in the CALLER, `ext/mbstring/mbstring.c`**, which is why `mbfl_strcut` never changed |

⚠⚠ **THE RULE THIS ESTABLISHES: the column names *a* fix for the row's function,
not necessarily the one that removes the 5.0.0 defect.** Both `ph12` and `ph21`
would have shipped a **wrong R1h with a plausible sha and a security-sounding
subject** if the column had been trusted alone. **The column and the tag bisect
below are complementary — the column gives you a real commit, the bisect tells
you whether it is yours.**

## §2 `ph21` — `str_repeat`, and upstream DELETED the guard

**5.0.0 and 5.1.0, identical** (`ext/standard/string.c`):

```c
int		result_len;                                      /* :4120 */
result_len = Z_STRLEN_PP(input_str) * Z_LVAL_PP(mult);   /* :4144  int × long, computed 64-bit, NARROWED BY THE STORE */
if (result_len < 1 || result_len > 2147483647) {         /* :4145  2nd disjunct provably dead: an int cannot exceed INT_MAX */
	php_error_docref(… "You may not create strings longer then 2147483647 bytes");
	RETURN_FALSE;
}
result = (char *)emalloc(result_len + 1);                /* :4149 */
```

**5.2.0 — three changes at once, and none of them is "tighten the guard":**

```c
size_t		result_len;                                            /* int -> size_t          */
result_len = Z_STRLEN_PP(input_str) * Z_LVAL_PP(mult);
                                                                   /* THE GUARD IS GONE      */
result = (char *)safe_emalloc(Z_STRLEN_PP(input_str), Z_LVAL_PP(mult), 1);  /* emalloc -> wrapper */
```

Stable in that form through 5.3.0 / 5.4.0 / 5.6.0 (5.3.0 additionally moves to
`zend_parse_parameters` and a plain `long mult`).

⭐ **The catalogue calls this *"a guard killed by the type of the variable it
tests"*. Upstream's repair was to change the type and delete the guard — the
maintainers' own fix is that reading, confirmed.**

- **fix window: 5.1.0 → 5.2.0.**
- **R1h candidate:** the 5.2.0 form. ⚠ It is a **three-part** change; the row
  must say whether R1h carries all three or only the one that restores the
  bound, **and justify it** — `ph03` set the precedent that a multi-hunk fix has
  hunks worth pricing separately.

## §3 `ph12` — `substr_compare`, the guard disabled by an optional argument

**5.0.0 and 5.1.0** (`:4786`):

```c
if (len && offset >= s1_len) {        /* omit the 4th argument -> len == 0 -> NO OFFSET CHECK AT ALL */
	php_error_docref(… "The start position cannot exceed initial string length.");
	RETURN_FALSE;
}
cmp_len = (uint) (len ? len : MAX(s2_len, (s1_len - offset)));   /* :4791 */
RETURN_LONG(zend_binary_strncmp(s1 + offset, (s1_len - offset), s2, s2_len, cmp_len));
```

**5.2.0 — the short-circuit is deleted:**

```c
if (ZEND_NUM_ARGS() >= 4 && len <= 0) { … RETURN_FALSE; }   /* new: reject a non-positive explicit length */
if (offset < 0) { offset = s1_len + offset; offset = (offset < 0) ? 0 : offset; }   /* new: clamp */
if ((offset + len) > s1_len) { … RETURN_FALSE; }            /* UNCONDITIONAL — no `len &&` */
```

**5.3.0** rewrites again to `if (offset >= s1_len)` **plus a clamp**
`if (len > s1_len - offset) { len = s1_len - offset; }`; **5.4.0 drops that clamp
again**, keeping only `offset >= s1_len`.

⚠ **Do not read 5.4.0's smaller guard as a regression before checking the sink.**
`zend_binary_strncmp(s1+offset, (s1_len-offset), s2, s2_len, cmp_len)` receives
*both* lengths and mins them internally, so the clamp is redundant there. **The
row should verify that at source rather than take this line's word for it.**

- **fix window: 5.1.0 → 5.2.0.**
- **R1h candidate:** 5.2.0's unconditional `(offset + len) > s1_len`.

## §4 `ph16` and `ph29` — both already fixed by 5.1.0

### `ph16` — the fix is not a check, it is a check **on one platform**

5.0.0 `streamsfuncs.c:541` is a bare `FD_SET(this_fd, fds);`. 5.1.0:

```c
if (SUCCESS == php_stream_cast(…, (void*)&this_fd, 1) && this_fd >= 0) {   /* new: reject a negative fd */
	PHP_SAFE_FD_SET(this_fd, fds);                                         /* new: the macro */
```

and `main/php_network.h:193-204` (5.1.0) is:

```c
#ifdef PHP_WIN32
/* it is safe to FD_SET too many fd's under win32; the macro will simply ignore
 * descriptors that go beyond the default FD_SETSIZE */
# define PHP_SAFE_FD_SET(fd, set)	FD_SET(fd, set)                                   /* NO CHECK */
#else
# define PHP_SAFE_FD_SET(fd, set)	do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)
#endif
```

⭐ **A macro named `PHP_SAFE_…` whose safety is `#ifdef`-conditional.** The
comment is *correct* — Win32's `fd_set` is a counted array of `SOCKET`s, not a
bitmap, so `FD_SET` really is bounded there — which makes this a clean example
of **a bound that lives in a platform's data structure rather than in the code**.
**R1h must state which branch it compiles** (we build POSIX → the guarded one).

- **fix window: 5.0.0 → 5.1.0.** Stable through 5.6.0 (5.4.0 changes the fd test
  from `>= 0` to `!= -1`).

### `ph29` — a TWO-STAGE repair

```
5.0.0   read_buf = emalloc(to_read + 1);                       long to_read, unchecked
5.1.0   if (to_read <= 0) { RETURN_FALSE; }   <-- stage 1      then emalloc(to_read + 1)
5.3.0   if (to_read <= 0) { RETURN_FALSE; }   then read_buf = safe_emalloc(1, to_read, 1);   <-- stage 2
```

- **fix window: 5.0.0 → 5.1.0** for the guard, **5.2.0 → 5.3.0** for the wrapper.
- ⚠ **So *"the fix"* is a choice the row must make and defend**, exactly as
  `ph03`'s two hunks were.

⚠⚠ **AND `ph29`'s CATALOGUED MECHANISM IS UNVERIFIED — SETTLE IT BEFORE
BUILDING.** `CATALOGUE.md` says *"`emalloc(n+1)` where the allocator truncates
n mod 2^32"*. But `to_read` is a `long` and 5.0.0's `emalloc` takes a `size_t`,
**which on this 64-bit box truncates nothing**. Either the truncation is
32-bit-only, or it happens somewhere else (`Z_STRLEN` is an `int`; the
`recvfrom` return is an `int recvd`), or the row is mis-catalogued.
**This is a C-side question, so unlike a Rust- or Verus-side one it CAN decide
admission** (`PLAN_PHP.md` §3) — but only after it is answered at source, and
*"the mechanism is 32-bit-only"* is a **narrowing**, not a kill.

## §5 ⚠⚠ BEFORE YOU GREP: two of these rows are in a file `grep` calls empty

`grep` in a `Bash` call is **a shell function that dispatches to `ugrep 7.8.4`**
(`/usr/bin/grep` is GNU 3.11 and is fine). On a file containing **one** non-UTF-8
byte the wrapper exits **1 with no stdout and no stderr** — identical to "not
found". `ext/standard/string.c` is such a file (`Stig S\xe6ther Bakken`, line
16), and it holds **`ph12` and `ph21`**.

```sh
grep         -n "PHP_FUNCTION(str_repeat)" …/string.c   # exit 1, SILENT
grep        -an "PHP_FUNCTION(str_repeat)" …/string.c   # 4115:PHP_FUNCTION(str_repeat)
/usr/bin/grep -n "PHP_FUNCTION(str_repeat)" …/string.c  # 4115:  (GNU grep is unaffected)
rg           -n "PHP_FUNCTION\(str_repeat\)" …/string.c # 4115:  (the Grep tool is rg-backed)
```

**Rule: `grep -a` on the corpus, always.**

⚠⚠ **And do not "check it with a script".** A shell function is not exported to
`sh`, so `sh probe.sh` runs GNU grep and **succeeds** on the file that fails when
you type the same line. Full census and the narrower decode hazard:
`RECAP_PHP.md` **F35**.

## §6 ⚠⚠ TWO OF THESE FOUR ROWS ARE MIS-TIERED, AND THE CATALOGUE STILL SAYS `verbatim`

`TASK_PHP_012` **M4** found that **12 of the 41 rows declaring `verbatim` sit
inside a `PHP_FUNCTION` / VM-handler / argument-parsing frame**, which
`PROTOCOL_PHP.md` §A1 defines as **`narrowed`** (*"a wrapper comes off (zval
unpacking, argument parsing)"*). ✅ **Re-run by the manager, reproduced exactly**
(`.temp/mgr/batch/tier_recheck.log`): the same 12 rows, and **all 12 still say
`verbatim` in `CATALOGUE.md`.**

| row | catalogue | enclosing frame at the defect site | correct tier |
|---|---|---|---|
| `ph21` | `verbatim` | `PHP_FUNCTION(str_repeat)` | ⚠ **`narrowed`** |
| `ph12` | `verbatim` | `PHP_FUNCTION(substr_compare)` | ⚠ **`narrowed`** |
| `ph16` | `verbatim` | `static int stream_array_to_fd_set(…)` — a helper | ✅ `verbatim` |
| `ph29` | `narrowed` | `PHP_FUNCTION(stream_socket_recvfrom)` | ✅ `narrowed` |

⚠ **This is a COST statement, never a filter** (`PLAN_PHP.md` §4) — **no row
gains or loses admission here.** But it is not cosmetic: `provenance.py` reports
kernel overlap **against the declared tier's expectation** (`verbatim` 50 %,
`narrowed` 25 %), and `TASK_PHP_008` demoted that from a floor to a report, which
put the judgement on a person. **A mis-declared `verbatim` row landing at 30 %
hands a reviewer a frightening number with no way to tell a wrong tier from a bad
extraction.** `TASK_PHP_012` said this must be fixed *before the first row*; it
was not, and `ph03` was unaffected — **`ph12` and `ph21` are where it finally
bites.**

**Landing is staged and mechanical**: `python3 .temp/mgr/land_m4.py --check |
--apply` edits Part A and Part B for all 12 and **refuses** unless every row has
exactly two occurrences. ⚠ **Blocked only because `TASK_PHP_016` is reading
`CATALOGUE.md`** (`PROTOCOL.md` rule 11).

⚠ **Also from `TASK_PHP_012` §6.2, and it stands**: `ph16` and `ph17` are a
legitimate C-side variation, **but their Rust and Verus halves are one row twice**
— *"index a fixed-size bitset with an unvalidated integer"* is a single
obligation. **`ph17` stays deferred**; do not pick it up as a fifth.

## §7 What this survey does NOT give you

1. ~~**No commit is pinned** — only tag windows.~~ ✅ **Superseded by §1b: all
   four are pinned from `index.csv`.** ⚠ **But two of the four name a LATER fix
   than the one that removes the 5.0.0 defect**, so the tag windows in §2–§4 are
   still the thing that decides R1h. **Cite both, and say which is which.**
2. **No admission decision.** All four are still subject to the C-side bar.
3. **No claim that a fix is complete.** `ph03` taught that a shipped fix can be
   **dead and incomplete at once** — measure both ends (`.memory-php/02`).
4. **No R1h is chosen.** Each row picks its own and justifies it; `ph21`
   (three-part) and `ph29` (two-stage) both force the choice.
