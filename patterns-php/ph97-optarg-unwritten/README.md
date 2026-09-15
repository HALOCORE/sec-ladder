# ph97 — the optional argument the parser never writes

**PHP 5.0.0, `ext/mbstring/mbstring.c:3209-3252`, corpus row CRASH-126, CWE-476,
tier `narrowed`, invariant `I12` / obligation `O3`.**

Read `spec.md` for the contract the gate enforces, `NOTES.md` for the
measurements, and this file for the shape of the row.

---

## The defect, in five lines of upstream

```c
3211  	char *typ = NULL;
3212  	int typ_len;
3215  	if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "|s", &typ, &typ_len) == FAILURE) {
3216  		RETURN_FALSE;
3219  	if (!strcasecmp("all", typ)) {
```

```c
Zend/zend_API.c
 485  			case '|':
 486  				min_num_args = max_num_args;      /* still ZERO */
 511  	if (num_args < min_num_args || num_args > max_num_args) {
 537  	while (num_args-- > 0) {                      /* runs ZERO times */
 548  	return SUCCESS;
```

`"|s"` puts the optional marker **first**, so the minimum argument count is set
from a maximum that is still zero. A call with no arguments passes the count
test, the loop that writes the out-parameters never runs, the parser reports
**SUCCESS**, and `typ` — the function's own `:3211` initialiser — goes into
libc.

## The claim, in one sentence

⭐⭐ **The guard is PRESENT and it PASSES, and it answers a different question
from the one the code needs answered.** `:3215` tests *were the supplied
arguments well-typed?*; `:3219` needs *was the optional argument supplied?*.

That is why this row is **not** *a fallible call's failure not tested*: nothing
fails. The catalogue's own risk note on `ph60` says so in terms, and it is why
CRASH-126 was split out of that row.

## Measured, not argued

A PHP 5.0.0 CLI on this box, under `.tasks-php/probes/segaddr.c`:

```
mb_get_info()                    -> SIG11 si_code=1 si_addr=(nil)   exit 139
mb_get_info("internal_encoding") -> string(10) "ISO-8859-1"         exit 0
mb_get_info(null)                -> bool(false)                     exit 0
mb_get_info(array(1,2))          -> Warning ... bool(false)         exit 0
mb_get_info("all", "x")          -> Warning ... bool(false)         exit 0
```

Same binary, same run. `c/kernel.c` reproduces the first line **at the same
address**, and ASan independently reports `SEGV on unknown address
0x000000000000` in `ph97_strcasecmp`. `NOTES.md` §1 and §2, with the two
cautions that travel with every such result.

⚠ **The null VALUE and the absent ARGUMENT are different states** and only the
second faults — `"|s"` carries no `!`, so `zend_API.c:302-308`'s `IS_NULL` arm
falls through and a supplied `null` becomes the empty string. That pair is what
makes *the guard answers the wrong question* a behavioural claim rather than a
reading of the source.

## The ladder

| rung | file | what it is |
|---|---|---|
| **R1** | `c/kernel.c` | PHP 5.0.0, narrowed. **The bug.** |
| **R1h** | `c/kernel_hardened.c` | + `f7326d627962`, **one line** |
| **R2** | `safe_naive.rs` | the mechanical safe port |
| **R3** | `safe_tuned.rs` | R2's three per-byte walks as iterator pipelines |
| **R4** | `unsafe.rs` | R3 with seven checks removed |
| **R5** | `verus.rs` | R4 plus the proof that licenses them |

⚠ **R2–R5 implement R1h's function**, because the 2005 fix is complete for this
defect. `NOTES.md` §7 says which safe behaviour was built and why, and
`controls/rust_bug.py` builds the alternatives — Rust rungs with the 2005 guard
deleted — rather than arguing about them in prose.

## What the row is about, and it is not a bounds check

⭐⭐ C spells *absent* as a NULL `char *`. Rust spells it `Option<&[u8; 21]>`,
which every Rust rung **asserts at compile time** occupies the same eight bytes,
because the discriminant lives in the reference's own null niche. So the safety
here is a **representation that costs nothing** plus a `match` the compiler will
not let you skip — not a test that costs instructions.

⚠⚠ **And the consequence is that no Rust rung reproduces the defect, which is a
FINDING and never a problem** (`CLAUDE.md` rule 6). In C the bug is an
**omission**; in Rust reproducing it takes a **commission** — and
`controls/rust_bug.py` commits it, twice, and measures that **neither
commission reproduces C either**: safe Rust turns it into a *panic*, and
`unwrap_unchecked` on `None` is UB the optimiser **exploits rather than lowers**
(abort at `-O0`, non-termination at `-O1` and above). `NOTES.md` §7.

## The R5 obligation

`opt_get`'s `requires` is `t.is_some()` — `I12/O3` word for word, with the
possibility in the type. It is discharged at all five compare sites from **one**
fact: the `typ.is_none() ||` disjunct that IS `f7326d627962`.

⛔ **It is not discharged from the parser's postcondition, and that is the
point.** `parse_va_args` returns SUCCESS with nothing written whenever the count
is zero, and its `ensures` says so — so the parser's contract *proves* the
pointer may be absent. `controls/negatives.py --emit r1` deletes the 2005 line
and the file stops verifying, on that precondition, at that site.

## Controls

| file | what it measures |
|---|---|
| `controls/r1h_backport.py` | the apply, the offset, the post-image bytes, and the gitignore trap |
| `controls/widened_domain.py` | R1 vs R1h on all seven inputs — the fix widens the benign domain |
| `controls/libc_compare.py` | the in-kernel compare against the platform's `strcasecmp`, with a must-fire control, and `inside_share` for both variants |
| `controls/tables.py` | the two constant tables, diffed across `c/kernel.c`, `verus.rs` and `model.py`; **and** the `strcasecmp` census — the clean negative, re-derived |
| `controls/rust_bug.py` | the two Rust variants that DO delete the 2005 guard, built and run — ⛔ **and neither reproduces C's fault**; see its docstring |
| `controls/negatives.py` | must-fire mutants of `verus.rs`, including the 2005 line's deletion |
| `controls/spellings.py` | every backticked span in `spec.md`'s `idiom`, matched against every rung it scopes to |
| `controls/rlimit_bisect.sh` | the proof budget, re-derived in both configurations |
