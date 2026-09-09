# UPSTREAM_002 — `ph07`'s R1h: **PHP DELETED HALF ITS OWN SECURITY FIX, AND OUR GATE HAD ALREADY SAID WHY**

**Author: the manager**, between `TASK_PHP_017` and `TASK_PHP_018`.
⚠⚠ **UNREVIEWED MANAGER WORK.** `PROTOCOL.md` rule 3 — I may not clear my own
design. `TASK_PHP_018` builds on this; the review after it must attack it.
Generator: `.temp/mgr165/REFETCH.sh` (the `.c` blobs are re-derivable and get
deleted; the script and the `.patch` are the evidence).

---

## §0 Why this exists

`TASK_PHP_017` §4 refused to land the §A2a clause `ph07` proposed, and gave a
reason that was **not** a reason about fixtures:

> *"An R1h of hunk (a) alone is memory-safety-complete, is byte-for-byte what
> PHP shipped at 5.2.17 / 5.3.2 / 5.3.3 / 5.3.29, changes no benign output,
> passes stage 7h on an unrestricted corpus, and needs no protocol clause at
> all."*

It verified the **fact** (hunk (b) is absent at those tags) and stopped. **I
went looking for the commit that removed it.** The answer is better than the
fact, and it inverts open item 24.

## §1 The measurement — `PHP_FUNCTION(mb_strcut)`, brace-matched, by body sha256

⚠ **Ask about a FUNCTION, not about text** (F35). A `grep` for the hunk's own
source line **misses 5.3.0**, which respells the same two guards as
`(unsigned int)from` / `string.len`. That is this project's own trap, and it
fired on me while I was writing this document.

| tag | body | sha256/16 | hunk (a) `from > len → FALSE` | hunk (b) `from+len > len → clamp len` |
|---|---:|---|:---:|:---:|
| `php-5.1.2` … `php-5.2.6` | 1931 B | `a971fe526e8b8803` | ✅ | ✅ |
| `php-5.2.7` … **`php-5.2.11`** | 1923 B | `ec8b60b77f5d7e8e` | ✅ | ✅ |
| **`php-5.2.12`** … `php-5.2.17` | 1823 B | **`26e2099e33433c74`** | ✅ | ❌ **GONE** |
| `php-5.3.0`, `php-5.3.1` | 1449 B | `08719ef48d57d502` | ✅ | ✅ *(respelled)* |
| **`php-5.3.2`** … `php-5.3.29` | 1356 B | **`49ad3ab2796d63e4`** | ✅ | ❌ **GONE** |

*(The 5.2.6→5.2.7 move is `MBSTRG(current_language)` → `MBSTRG(language)` — one
token, unrelated. The 5.2→5.3 size drop is the surrounding rewrite, not the
guards.)*

**So hunk (b) is continuously present from the 2005 security commit through
5.2.11 and 5.3.1, and is removed on both branches within five months.**

## §2 ⭐⭐ THE REMOVAL COMMIT, AND IT IS NOT A CLEANUP

`c2471b495009` — **Moriyoshi Koizumi, 2009-09-23**, on `PHP-5.2`. The only
non-cosmetic commit on that file in the window (the other is a copyright-year
`sed`). Its diff of `mbstring.c` is **exactly hunk (b) and nothing else**:

```diff
 	if (from > Z_STRLEN_PP(arg1)) {
 		RETURN_FALSE;
 	}
-	if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) {
-		len = Z_STRLEN_PP(arg1) - from;
-	}
 
 	ret = mbfl_strcut(&string, &result, from, len);
```

**Subject:** *"Fixed bug #49354 (`mb_strcut()` cuts wrong length when offset is
within a multibyte character)."* It adds `ext/mbstring/tests/bug49354.phpt`, a
**regression test** whose `--EXPECT--` block pins six answers that hunk (b) got
wrong. ⭐ **And the commit message contains a rebuke:**

> *"(This bug was introduced by the commit by r202895. Please double-check the
> specification of the function you are going to \*fix\*.)"*

⚠ **NOT VERIFIED: that `r202895` resolves to `cb3cca21b345`.** The 2005 commit
is CVS-era and the revision is an SVN number, so the identification needs a
mapping I have not done. **What is measured is the code, not the blame** — and
the code says the lines removed in 2009 are the lines added in 2005. Whoever
reviews this should either resolve `r202895` or delete the sentence.

## §3 What this does to open item 24 — **it inverts it**

The row's position was: *stage 7h refuses R1h because the upstream fix changes
benign output on 13.5 % of calls, so the fixture must keep the fix's guards
dead, and protocol should say so.* Set the three facts side by side:

| | |
|---|---|
| `ph07`'s own `fix_scope.py` | hunk (b) **removes none** of the reads past `val[slen]`; hunk (a) alone closes **all** of them |
| `ph07`'s own `fix_scope.py` | hunk (b) **changes the answer on 15 870 of 117 612** benign calls (13.5 %); hunk (a) changes none |
| **upstream, 2009** | **deleted hunk (b) as a correctness bug, with a regression test** |

⚠⚠⚠ **So `check.py` stage 7h was not a harness limitation getting in the way of
a real fix. It detected the same defect PHP's own maintainers detected — four
years later, from a bug report — and it detected it in the first hour the row
existed.** The engineer read a true refusal as an obstacle and proposed
protocol to route around it; `TASK_PHP_017` declined the protocol on other
grounds and was right for a stronger reason than it gave.

⭐ **This is `ph03`'s finding reached from the opposite direction.** There, a
stated obligation caught in 2026 what a patch missed for ten years — the fix was
**incomplete**. Here the fix was **too big**, and the part that was too big was
not merely dead: it was **wrong**, and upstream removed it. **Two rows, two
shipped security fixes, neither minimal nor sufficient as shipped.** That is a
result about security patches, and it is now n = 2 rather than an anecdote.

## §4 The decision I am making, and its cost

**`ph07`'s R1h becomes the guard configuration upstream CONVERGED on — hunk (a)
alone — pinned as `php-5.2.12 … php-5.2.17`, `PHP_FUNCTION(mb_strcut)` body
sha256 `26e2099e33433c74`.** The two-hunk commit and the removal commit both
stay in `controls/` as the evidence for why.

**What it buys:**

1. ✅ **The invented §A2a clause is not needed.** Item 24 closes by **deletion**,
   not by a rule — the best outcome available for a rule invented on n = 1.
2. ✅ **`inputs/gen.py`'s corpus restriction goes away**, so the ladder is
   measured over the **whole** benign domain instead of the 86.5 % of it on
   which the shipped fix happened to agree with 5.0.0.
3. ⭐ **F41's *"the fix costs a CONSTANT"* is re-measured on ONE comparison
   instead of two** — a cleaner number for a cleaner claim.
4. ⭐ **R1h stops being a choice the row has to defend and becomes a citation.**

**What it costs — and this is a REBUILD of row 2, not an edit:**

- `c/kernel_hardened.c`, `spec.md`'s `idiom.required[4]` (which pins R1h as
  *"`cb3cca21b345` and NOTHING ELSE"* — inside the hashed block, so this is a
  **re-gate**), `inputs/gen.py` and therefore **every `.bin`**, therefore **every
  measured number on the row**, therefore F41 and `.memory-php/`.
- ⚠⚠ **And the Rust rungs.** F41 says R2–R5 *are ports of R1h*. If they carry
  hunk (b)'s clamp, then on the newly-admitted 13.5 % they will disagree with
  R1 — **the identity stages will fail, and that failure is correct.** The
  engineer must check this first and say what it found.
- ⚠ `TASK_PHP_017`'s `v1` number (**+2.62 %**) was measured on the **restricted**
  corpus and must be **re-derived**, not carried over.

⚠ **The honest risk, stated because it is mine:** a subset of a commit is not a
commit, and `PROTOCOL_PHP.md` §C says R1h is *the real upstream `fix_commit`*.
**My answer is that a tagged upstream configuration is a stronger citation than
a commit, not a weaker one** — it is what the project *shipped and kept*, it is
pinnable by `(tag, function, sha256)`, and four tags carry it byte-for-byte.
**But that is a protocol extension and it is unreviewed.** → `TASK_PHP_018`
proposes the §C wording; **nobody lands it before a reviewer has attacked it**
(rule 9). ⚠ **It is exactly the shape of thing this programme keeps getting
wrong: a rule invented to make one row work.** The difference I am claiming — and
it is the thing to attack — is that the §A2a clause narrowed the *evidence* to
fit the *artefact*, and this widens the *artefact* to fit the *evidence*.
