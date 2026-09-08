# `patterns-php/SOURCES.md` — the citation base

**Every `file:line` in the PHP programme resolves against the pristine PHP
5.0.0 museum tarball, and against nothing else.** This file is what makes that
checkable after the tarball is gone.

---

## 1. The corpus

```
php-5.0.0.tar.gz
sha256    5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
size      5595997 bytes
entries   3815          (.c and .h among them: 1170)
root      php-5.0.0/    (the single top-level directory)
origin    museum.php.net  -- https://museum.php.net/php5/php-5.0.0.tar.gz
found on this box at
          /home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
```

⚠⚠ **That path is under ANOTHER PROJECT'S gitignored `.temp/`, which that
project's own convention makes deletable at any time.** This is the hazard
`common/census/README.md` §1 already names — *"a census whose corpus cannot be
re-identified is a census nobody can check"* — and it is why
`php-5.0.0.manifest` is committed beside this file. If the tarball disappears,
re-fetch it from `museum.php.net`, check the sha256 above, and every citation
in `patterns-php/` still resolves.

Override the location with `PHP500_TARBALL=<path>`; `manifest.sh` and
`harness-php/provenance.py` both honour it and both refuse a tarball whose
sha256 is not the one above.

## 2. The read recipe

```sh
tar -xzOf <tarball> php-5.0.0/<path> | sed -n '<a>,<b>p'
```

`<path>` is **root-relative** — `Zend/zend_alloc.c`, not
`php-5.0.0/Zend/zend_alloc.c` — which is exactly the spelling
`php-5.0.0.manifest` uses, so a manifest line and a citation are the same
token. `sed -n 'a,bp'` is **1-based and inclusive**.

To confirm one file has not moved:

```sh
tar -xzOf <tarball> php-5.0.0/Zend/zend_alloc.c | sha256sum
grep 'Zend/zend_alloc\.c$' patterns-php/php-5.0.0.manifest
```

## 3. ⚠⚠⚠ THE RULE: NEVER CITE A BUILD TREE

**The rule stands. Everything this section previously gave as its reason was
wrong**, and the correction is `TASK_PHP_003` M3 → `TASK_PHP_004` §2.7. It said
*"every extracted PHP tree on this box is patched"* and named an allocator
patch *"which deletes the 32-bit truncation at `Zend/zend_alloc.c:135`"*.
Measured over **every** `php-5.0.0/Zend/zend_alloc.c` on this box
(`find`, 12 trees; hashes against the tarball's `fb4215f19dc2e68c…`):

| n | `zend_alloc.c` | tree(s) | what the patch does |
|--:|---|---|---|
| 3 | **pristine** | `.app-tests/.temp/oracle/build-5.0.0-mysql-webext{,-O3lto,-maxlto}/` | — (this row's table used to call these *"modern-gcc **and allocator**"* patched) |
| 3 | **pristine** | `.trash/temp-20260805-0920/build-5.0.0{,-mysql,-mysql-webext}/` | — |
| 2 | **pristine** | `.temp/san_tests/oracle/…-maxlto-asan`, `…-maxlto-hardened` | — |
| 2 | `d6245088682d2e00` | `.temp/san_tests/oracle/…-maxlto-nocache{,-asan}` | `ZEND_DISABLE_MEMORY_CACHE 0 → 1` at **`:40` and `:43`** — turns OFF the size-class cache. ⚠ **The consequential one**, and it was named nowhere: it is the control the 63.5 % figure is derived from |
| 1 | `74a20877c68d1ff4` | `.temp/san_tests/oracle/…-maxlto-nocache-detect-asan` | the cache patch **plus** `REAL_SIZE(size) → (size)` at **`:132`** |
| 1 | `b817edb91015b918` | `.temp/san_tests/oracle/…-maxlto-poison-asan` | `ASAN_{,UN}POISON_MEMORY_REGION` at `:35-41`, `:162`, `:284` |

**8 of 12 are byte-identical to the pristine tarball**, including all three
`.app-tests/` trees this table named as allocator-patched.

⚠⚠ **AND `REAL_SIZE(size) → (size)` DOES NOT DELETE THE TRUNCATION.**
`real_size` is still `unsigned int` (`:129`) and `real_size = REAL_SIZE(size)`
(`:135`) still truncates mod 2^32. All the patch removes is the round-up-to-8,
so ASan's redzone starts at the requested size. Measured
(`.temp/php4/real_size_probe.c`): for `emalloc_probe.c:61`'s 18.45 EB request
both spellings give `real_size = 2147483648`. ⚠ That equality is
**value-dependent** — at `SIZE_MAX` they give `0` and `4294967295`, still both
truncating.

⚠ **The tree count.** There are **12** `php-5.0.0` trees and **13**
`Zend/zend_alloc.c` files if you count `php-in-safe-rust/build/php-4.0.2/`,
which `DP-06` excludes and which cannot be byte-identical to a 5.0.0 tarball.
That, and nothing else, is the `7 of 12` / `8 of 13` disagreement between the
reviewer and the manager: the **8** and the **13** are each right about a
different set. Settled at `TASK_PHP_004`; enumeration in
`.temp/php4/trees_500.txt`.

✅ **So why the rule still holds:** a *some-trees-are-patched* corpus is one
where **you cannot tell by looking which tree you are in** — three of the four
patched trees sit beside eight pristine ones under sibling directory names
differing by one suffix — and the two `-nocache` trees model an allocator with
**no size-class cache at all**, which is a bigger lie about PHP than the patch
this section used to warn about. `php-in-safe-rust/build/php-4.0.2/` really is
modern-gcc patched, and is 4.0.2.

⚠ And the same rule one level up (`PLAN_PHP.md` §1): **the corpus CSV's
`c_file_line` is authoritative; the reproducer `.php` header comment is not.**
Six of those comments describe 4.0.2 code that no longer exists at 5.0.0, and
`CRASH-017.php`'s says so in its own text. A reproducer is an INPUT, not a
citation.

## 4. `php-5.0.0.manifest`

sha256 of **every `.c` and `.h`** in the tarball, root-relative, `LC_ALL=C`
sorted. Regenerate with:

```sh
sh patterns-php/manifest.sh          # READ-ONLY on the tarball
```

It refuses to write if the tarball's sha256, byte size or entry count is not
the one pinned above — so a manifest in this tree is always a manifest of
*that* corpus. `MANIFEST.sha256` is the digest-of-digests, so the manifest
itself can be checked with no corpus present.

**Size, judged against `.memory/00-environment.md`'s *"kilobytes, not
gigabytes"*, the way `common/census/README.md` does rather than silently:**

| | |
|---|---|
| files | **1170** |
| bytes | **109,405** (107 K) |

That is *kilobytes*, comfortably — an order of magnitude under the 506 K
`common/census/` already justifies, and 0.2 % of `.git`. It is sorted,
diffable, greppable ASCII, which is the shape the policy is *for*.
Root-relative paths rather than `php-5.0.0/`-prefixed save ~11 K at zero
information cost, since the root is one header line. **gzip was measured and
rejected on the same grounds `common/census/README.md` gives** — it halves the
file and stops it being greppable or diffable, and at 107 K there is nothing
to buy.

⚠ **What a green manifest does NOT buy.** It says the bytes are the ones the
programme measured. It says nothing about whether a row's `c_lines` span is
the right span — that is `provenance.extract_sha256`, and
`harness-php/provenance.py` is what checks it.

## 5. How a row cites this

Inside the hashed `slb-contract` block (`PLAN_PHP.md` §6):

```json
"provenance": {
  "php_version":    "5.0.0",
  "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
  "c_file":         "ext/standard/url.c",
  "c_lines":        [463, 489],
  "extract_cmd":    "tar -xzOf <tarball> php-5.0.0/ext/standard/url.c | sed -n '463,489p'",
  "extract_sha256": "<sha256 of exactly those bytes>",
  "tier":           "verbatim",
  "divergences":    [{"what": "TSRMLS_DC", "kind": "deletion", "where": "url.c:463", "why": "thread plumbing, no semantics"}],
  "root_cause_ids": ["…"], "cwe": "CWE-125", "fix_commit": "…",
  "invariant": "I1", "obligation": "O2", "echoes": ["p16"]
}
```

Check it with `python3 harness-php/provenance.py <row>`. The validator does
**not** `exec` `extract_cmd` — it derives the excerpt from `c_file`/`c_lines`
and separately requires `extract_cmd` to be the canonical spelling of those
fields, so the two can fail independently and the failures mean different
things.

⚠ **What it checks and what it does not** is itemised in `provenance.py`'s own
docstring and is worth reading before writing a `provenance` block. In short:
the tarball hash, the manifest membership, the span (non-empty, in range) and
its sha256, the canonical `extract_cmd`, and a **heuristic line overlap**
between the excerpt and the row's `c/kernel*.{c,h}` with a per-tier floor. It
does **not** validate `tier`, `divergences` (the ledger, `deletions` before
`TASK_PHP_015`), `cwe`, `fix_commit`, `invariant`,
`obligation` or `echoes` — those are declarations.
