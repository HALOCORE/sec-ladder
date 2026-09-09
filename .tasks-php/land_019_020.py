#!/usr/bin/env python3
"""Land TASK_PHP_019 (§4, §5, §10) and TASK_PHP_020 (§4, §7) on
`patterns-php/CATALOGUE.md`: 93 -> 102 rows.

    python3 .tasks-php/land_019_020.py --check           # touch nothing
    python3 .tasks-php/land_019_020.py --check --to FILE  # check another copy
    python3 .tasks-php/land_019_020.py --apply
    python3 .tasks-php/land_019_020.py --apply --to FILE  # write a scratch copy

⚠⚠⚠ **THIS SCRIPT WAS NOT APPLIED BY `TASK_PHP_021`.** Its §2 trigger test found
**3 of the 9 new rows had a `▸ trigger` that would cost an engineer time**
(`ph94`, `ph98`, `ph101`), and `TASK_PHP_021`'s own stop condition is *"if the
trigger test fails on more than two of the nine, STOP the landing and report"*.
The script is left `--check`-clean so the landing is one command once the batch
has had the review cycle that condition asks for. **The three corrected triggers
are already folded into the text below** (`TASK_PHP_021_REPORT.md` §2).

Following `.tasks-php/land_m4.py`'s precedent: every anchor must be present
**exactly once** or the script refuses and writes nothing. A landing that
silently half-applies is worse than one that stops.

The tier is a COST STATEMENT, never a filter (`PLAN_PHP.md` §4, `CATALOGUE.md`
§0.2) -- no row gains or loses admission here.
"""
import re
import sys

CAT = "/home/apt/repos_common/sec-ladder/patterns-php/CATALOGUE.md"

# ---------------------------------------------------------------------------
# 1. REPLACEMENTS -- (name, old, new).  `old` must occur exactly once.
# ---------------------------------------------------------------------------

REPLACE = []


def R(name, old, new):
    REPLACE.append((name, old, new))


# --- the file header: recount from the table, not from the old line ---------
# Measured by TASK_PHP_021: Part A holds 93 rows; by AXIS CELL they are
# spatial 40 / type 22 / temporal 31, and the three section headings read
# 38 / 22 / 31 because ph92 and ph93 (both `spatial`) sit under the Temporal
# heading.  This landing moves those two into the Spatial section, so heading
# == section == axis for all three afterwards.
R("header-counts",
  """**91 rows catalogued** — 38 spatial · 22 type/initialisation · 31 temporal, one
of them (`ph91`) **unresolved** — over the 166-row corpus at""",
  """**102 rows catalogued** — 42 spatial · 29 type/initialisation · 31 temporal, two
of them (`ph15`, `ph91`) **unresolved** — over the 166-row corpus at""")

R("header-merges",
  """**1 kill on criterion 3** (`CRASH-017`), **1 soft kill on criterion 2**
(`CRASH-021`, pending a run I did not take), and **12 exact-duplication merges**
that survive inside a catalogued row.""",
  """**1 kill on criterion 3** (`CRASH-017`), **1 soft kill on criterion 2**
(`CRASH-021`, pending a run I did not take), and **3 exact-duplication merges**
that survive inside a catalogued row — ⚠ **down from 12 at `TASK_PHP_019`**,
which ran the mechanism test on all 13 of `C.1` and reversed 10 of them.""")

# --- Part A section headings ----------------------------------------------
R("head-spatial", "### Spatial (38)", "### Spatial (42)")
R("head-type", "### Type / initialisation (22)", "### Type / initialisation (29)")

# --- Part A: `corpus rows` MOVES (they move, they never duplicate) ---------
R("A-ph11",
  "| ph11 | spatial | one-sided compare on a signed index, no lower bound | narrowed | I1/O1 | CRASH-145, V5C-173 | p02 | catalogued |",
  "| ph11 | spatial | one-sided compare on a signed index, no lower bound | narrowed | I1/O1 | CRASH-145 | p02 | catalogued |")

R("A-ph22",
  "| ph22 | spatial | two passes over one format string apply different clamps | narrowed | I11/O1 | CRASH-014, V5C-015 | p13 | catalogued |",
  "| ph22 | spatial | two passes over one format string apply different clamps | narrowed | I11/O1 | CRASH-014 | p13 | catalogued |")

R("A-ph32",
  "| ph32 | spatial | a range declared in one place, a table literal sized in another | verbatim | I1/O2 | CRASH-089, CRASH-090 | p27 | catalogued |",
  "| ph32 | spatial | a range declared in one place, a table literal sized in another | verbatim | I1/O2 | CRASH-089 | p27 | catalogued |")

R("A-ph39",
  "| ph39 | type | union member read with no tag check of any kind | narrowed | I4/O1 | CRASH-036, CRASH-037, CRASH-101 | p35 | catalogued |",
  "| ph39 | type | union member read with no tag check of any kind | narrowed | I4/O1 | CRASH-036, CRASH-037 | p35 | catalogued |")

R("A-ph41",
  "| ph41 | type | container checked, elements not | narrowed | I4/O1 | CRASH-039 | p35 | catalogued |",
  "| ph41 | type | container checked, elements not | narrowed | I4/O1 | CRASH-039, CRASH-101 | p35 | catalogued |")

R("A-ph48",
  "| ph48 | type | the same helper used to FORCE the shared flag ON | narrowed | I4/O2 | LOGIC-017 | p49 | catalogued |",
  "| ph48 | type | the same helper used to FORCE the shared flag ON | narrowed | I4/O2 | LOGIC-017, LOGIC-014 | p49 | catalogued |")

R("A-ph60",
  "| ph60 | type | a fallible call's failure not tested before its result is used | verbatim | I12/O1, I16 | CRASH-088, CRASH-061, CRASH-126, CRASH-163 | — | catalogued |",
  "| ph60 | type | a fallible call's failure not tested before its result is used | verbatim | I12/O1, I16 | CRASH-088 | — | catalogued |")

# --- Part A: ph92/ph93 move out of the Temporal section into Spatial -------
# (`TASK_PHP_020` §7.2 also rewrites ph93's mechanism cell; the moved line
#  carries the new wording.)
R("A-move-out-92-93",
  """| ph92 | spatial | `base + count*CONST` in `int`: one attacker degree of freedom | narrowed | I11/O2 | CRASH-106 | p13 | catalogued |
| ph93 | spatial | buffer regrown mid-emit; the growth arithmetic is unchecked `int` | narrowed | I11/O2 | CRASH-109 | — | catalogued |
""",
  "")

R("A-spatial-tail",
  "| ph38 | spatial | in-place increment of an operand that aliases a shared literal | narrowed | I1/O4 | CRASH-077 | p49 | catalogued |",
  """| ph38 | spatial | in-place increment of an operand that aliases a shared literal | narrowed | I1/O4 | CRASH-077 | p49 | catalogued |
| ph92 | spatial | `base + count*CONST` in `int`: one attacker degree of freedom | narrowed | I11/O2 | CRASH-106 | p13 | catalogued |
| ph93 | spatial | buffer regrown mid-emit, by a term an attacker `linelength` divides | narrowed | I11/O2 | CRASH-109 | — | catalogued |
| ph95 | spatial | an argument-count guard defeated by the wrap of its own operand | narrowed | I11/O1 † | V5C-015 | p05 † | catalogued |
| ph102 | spatial | one omitted element in the only entity table with no run comments | verbatim | I1/O2 † | CRASH-090 | p27 † | catalogued |""")

R("A-type-tail",
  "| ph60 | type | a fallible call's failure not tested before its result is used | verbatim | I12/O1, I16 | CRASH-088 | — | catalogued |",
  """| ph60 | type | a fallible call's failure not tested before its result is used | verbatim | I12/O1, I16 | CRASH-088 | — | catalogued |
| ph94 | type | untyped offset: the union's `obj` member read as a byte index | narrowed | I4/O1, I3/O2 † | V5C-173 | p35, p48 † | catalogued |
| ph96 | type | SUCCESS does not mean the out-parameter was written | narrowed | I12/O1, I16/O2 † | CRASH-061 | p42 † | catalogued |
| ph97 | type | an optional argument never written; the guard tests a different question | narrowed | I12/O3 † | CRASH-126 | — | catalogued |
| ph98 | type | a global cleared by the caller, read back on the error path | narrowed | I16/O4, I12/O2 † | CRASH-163 | — | catalogued |
| ph99 | type | a read handler's result mutated in place on the read-WRITE path | narrowed | I9/O2 † | LOGIC-003 | p49 † | catalogued |
| ph100 | type | the separator fires where it must not, and clears the binding | narrowed | I8/O2, I9/O5 † | LOGIC-008 | p49 † | catalogued |
| ph101 | type | two dictionary slots aliased by an update that destroys one | narrowed | I9/O1, I8/O1 † | LOGIC-018 | p49 † | catalogued |""")

# The `†` marker needs a legend beside the one that already explains the column.
R("A-inv-obl-legend",
  """`inv/obl` are the corpus's own blind-labelled invariant/obligation
(`paper/invariants-list.md`), carried across unmodified.""",
  """`inv/obl` are the corpus's own blind-labelled invariant/obligation
(`paper/invariants-list.md`), carried across unmodified.
⚠ **`†` marks a DERIVED cell, not a carried one.** The corpus has no blind
label for `ph94`–`ph102`, so `TASK_PHP_019` §5 read the `inv/obl` off the
obligation texts in `paper/invariants-list.md` and the `echoes` off the PAT
rows' mechanisms; each is justified in the row's Part B prose and **none is the
corpus's**. `echoes` is a reading throughout this file (§0.3, §9.4) — for the
`†` rows it is one nobody has checked against the `pNN` row.""")

# --- TASK_PHP_020 §7.1: ph21 -----------------------------------------------
R("B-ph21-harm",
  """*A guard killed by the type of the variable it tests*, which is not ph19's wrap-in-an-expression.
▸ trigger: `str_repeat($s, 2^32/strlen($s))`.""",
  """*A guard killed by the type of the variable it tests*, which is not ph19's wrap-in-an-expression.
⚠⚠ **AND THE HARM IS ON ONE ARM ONLY.** The general emit path (`:4155-4166`) bounds itself with `ee = result + result_len` — the **narrowed** length — so it writes exactly what was allocated and overflows nothing. The overflow is the `Z_STRLEN_PP(input_str) == 1` fast path at `:4153`, `memset(result, *(Z_STRVAL_PP(input_str)), Z_LVAL_PP(mult))`, which passes the **un-narrowed 64-bit multiplier** straight to `memset`. Second, much smaller limb: for `Z_STRLEN > 1` with `result_len < Z_STRLEN` — `strlen = 3, mult = 2863311531` gives `result_len = 1` — `:4157`'s `memcpy(result, …, Z_STRLEN_PP(input_str))` overflows the `result_len + 1` block. (`TASK_PHP_020` §3.B.)
▸ trigger: ⚠ **`str_repeat("A", 4294967297)` (= 2^32 + 1) — NOT `str_repeat($s, 2^32/strlen($s))`, which CANNOT FIRE**: at exactly `2^32/strlen` the stored `result_len` is **0** (or negative when `strlen` does not divide 2^32) and the guard's **surviving first** disjunct `result_len < 1` refuses it. The narrowed value must land in `[1, INT_MAX]`. (`TASK_PHP_020` §3.B.)""")

# --- TASK_PHP_020 §7.2: ph93 ----------------------------------------------
R("B-ph93-type",
  """**whose growth arithmetic is itself unchecked `int` AND DIVIDES BY AN ATTACKER-CONTROLLED `linelength`.**""",
  """whose growth term **DIVIDES BY AN ATTACKER-CONTROLLED `linelength`** — the one thing no other row has. ⚠ **Type, corrected the way `ph92`'s was**: `current` and `linelength` are `long` (`:636-637`), so `((textlen - current + 1)/linelength + 1) * breakcharlen` is computed in **64-bit** and is **truncated by the explicit `(int)` cast**; only the `alloced +=` accumulation is native `int`. *"The growth arithmetic is unchecked `int`"* is the same loose phrasing `TASK_PHP_017` §2.2 corrected on `ph92`. ⚠⚠ **AND THE HARM LIMB IS OPEN.** `TASK_PHP_020` reached `:692` on the stated arm and measured **no overflow there**: firing `chk <= 0` costs `textlen/linelength + 1` decrements, each consuming ≥ `min(linelength, breakcharlen)` input bytes, which bounds the growth term at fire time at roughly `textlen`. **No input was found that both reaches `:692` and wraps its accumulation, and none was shown not to exist.** The row's demonstrable overflow on this arm is the *sizing* line `:679` (`chk * breakcharlen` in `int`, e.g. `textlen = 10^6, linelength = 1, breakcharlen = 3000`) — which is the shape the block says is NOT the distinctness. **A build task must settle this before writing a rung.**""")

R("B-ph93-trigger",
  """▸ trigger: `linelength > 0` with `chk = textlen/linelength + 1` driven to 0 mid-loop — reached at iteration 2 with `linelength = 2e9, breakcharlen = 2`.""",
  """▸ trigger: ⚠ **two, and they are not the same claim.** (a) *Reaching* `:692` on the `linelength > 0` arm: `linelength = 2e9, breakcharlen = 2`, text beginning with the break string — `chk` starts at 1, one `chk--` at `:705` on iteration 0, `:691` fires at `current = 2`. ⚠ **This grows `alloced` by 3 and overflows nothing.** (b) A *demonstrated* overflow on the same arm: `:679`'s `chk * breakcharlen` in `int`. (`TASK_PHP_020` §7.2.)""")

# --- TASK_PHP_020 §7.3: the additive one-liners ---------------------------
R("B-ph04-name",
  "**ph04 · `php_url_parse_ex`: peeks and a desynced length**",
  "**ph04 · `php_url_parse`: peeks and a desynced length**")

R("B-ph04-name-note",
  "⚠ risk: **do not split this into two rows** — one extraction, two triggers; two rows double-count a ladder cost paid once.",
  "⚠ risk: **do not split this into two rows** — one extraction, two triggers; two rows double-count a ladder cost paid once. ⚠ **The function is `php_url_parse`, not `php_url_parse_ex`** — 5.0.0 has no `_ex` spelling anywhere in the tarball, and a reader searching for the name in an earlier version of this line found nothing (`TASK_PHP_020` §7.3; `.memory-php/00` *\"ask about a FUNCTION\"*).")

R("B-ph13-fault",
  "⚠ risk: pricing the extraction at `exif_process_IFD_in_JPEG` rather than at `:3071-3079` is the error that killed this row once (Part C, F8).",
  "⚠ risk: pricing the extraction at `exif_process_IFD_in_JPEG` rather than at `:3071-3079` is the error that killed this row once (Part C, F8). ⚠ **FAULT: `exif.c:3004`** — `NumDirEntries = php_ifd_get16u(dir_start, …)`, the callee's **first** statement, which is what makes *\"none of the mutual recursion is needed\"* true (`TASK_PHP_020` §7.3).")

R("B-ph22-clamps",
  "`outputpos += (arg + 1) / 2;` in the sizing pass wraps `int`; `output = emalloc(outputsize + 1);` at `:304` then allocates the wrapped amount and the emit loop from `:309` writes the unwrapped one.",
  "`outputpos += (arg + 1) / 2;` in the sizing pass wraps `int`; `output = emalloc(outputsize + 1);` at `:304` then allocates the wrapped amount, and the emit pass **clamps `arg` to `Z_STRLEN_PP(val)` at `:335`**, so it writes `ceil(strlen/2)` bytes into the wrapped allocation — **the two passes' different clamps are the mechanism**, and the adversarial cell is cheap, not 2 GB (`TASK_PHP_020` §7.3).")

R("B-ph42-gate",
  "The only row labelled both `I4` and `I3`; report both limbs or the row understates itself.",
  "The only row labelled both `I4` and `I3`; report both limbs or the row understates itself. ⚠ `:1196` gates on `str.len == sizeof(\"__clone\")-1 == 7` **before** `:1197` dereferences `str.val`, so the blob must supply that uninitialised word (`TASK_PHP_020` §2.1).")

R("B-ph74-initpzval",
  "The harm is not the stack escape — it is that userland's argument stack later **frees a pointer that was never an allocator return**.",
  "The harm is not the stack escape — it is that userland's argument stack later **frees a pointer that was never an allocator return**. ⭐ And `zend_read_property` **never calls `INIT_PZVAL(&property)`** — compare `zend_object_handlers.c:72-73`, which does — so `property.refcount` / `is_ref` are stack garbage before the zval reaches userland's argument stack (`TASK_PHP_020` §7.3).")

R("B-ph88-chain",
  "`zend_destroy_rsrc_list` runs before `Zend/zend.c:822`'s `shutdown_compiler`, so one subsystem is torn down while another still names its storage.",
  "`zend_destroy_rsrc_list` runs before `Zend/zend.c:822`'s `shutdown_compiler`, so one subsystem is torn down while another still names its storage. ⭐ **The chain, traced** (`TASK_PHP_020` §2.1): `shutdown_compiler` (`zend_compile.c:159-176`) ends at `:169 zend_llist_destroy(&CG(open_files))`, whose destructor `zend_file_handle_dtor` (`zend_language_scanner.c:2988`) takes its `ZEND_HANDLE_STREAM` arm at `:2997` and calls `fh->handle.stream.closer(fh->handle.stream.handle)` — on a `php_stream` that lived in `EG(regular_list)` and was **already destroyed** at `zend_execute_API.c:282`.")

R("B-ph12-onesided",
  "⚠ risk: the declaration block is `:4776-4780` and the miner's quote omits `zend_bool cs=0;` at `:4779` — copy from the tarball, not from the report.",
  "⚠ risk: the declaration block is `:4776-4780` and the miner's quote omits `zend_bool cs=0;` at `:4779` — copy from the tarball, not from the report. ⭐ **The guard is also ONE-SIDED**: with an explicit non-zero `$length`, `len && offset >= s1_len` still passes for **any negative offset** — `substr_compare(\"abc\",\"x\",-1000000,5)` reads at `s1-1000000` — which is why upstream's 5.2.0 fix added a negative-offset clamp **as well as** the unconditional `(offset+len) > s1_len` bound (`TASK_PHP_020` §3.A).")

R("B-ph64-lines",
  "⚠ risk: `zend_llist` is ~200 lines with an inline `char data[1]` payload and `zend_llist_apply` is eight lines.",
  "⚠ risk: `zend_llist.c` is **317** lines with an inline `char data[1]` payload and `zend_llist_apply` is eight lines (`:186-193`).")

R("B-ph72-span",
  "**ph72 · allocated on one arm, released on every arm** — `ext/standard/array.c:993-1063`",
  "**ph72 · allocated on one arm, released on every arm** — `ext/standard/array.c:993-1063` (⚠ the span ends at the while-loop's brace; `php_array_walk` closes at `:1066`)")

# --- TASK_PHP_020 §4: the three strengthenings to ph29 ---------------------
R("B-ph29-trigger",
  "▸ trigger: `stream_socket_recvfrom($s, PHP_INT_MAX)`.",
  "▸ trigger: `stream_socket_recvfrom($s, 4294967295)` — any `to_read` with `to_read + 1 ≡ 0 (mod 2^32)`. ⚠ **Prefer this to `PHP_INT_MAX`**, whose `to_read + 1` is signed-overflow **UB** the compiler may fold, so a kernel built to it can behave differently at `-O3` than at `-O0` *for a reason that is not the pattern*. `to_read = -1` also works (`size = 0`) and is exactly what upstream's 5.1.0 `if (to_read <= 0)` refuses. (`TASK_PHP_020` §4, measured: `.temp/php20/ph29_probe.c`.)")

R("B-ph29-risk",
  "This row **must** link `common-php/emalloc_shim.h` and say so.",
  """This row **must** link `common-php/emalloc_shim.h` and say so. ⭐ **Three strengthenings, measured on this box** (`TASK_PHP_020` §4): (1) the truncation **also defeats the memory limit** — `CHECK_MEMORY_LIMIT(size, SIZE)` at `zend_alloc.c:177` accumulates `SIZE` = `real_size` = **0**, so `--enable-memory-limit` does not stop it; (2) it reaches a **second** of the three truncations, `p->size = size` at `:167`/`:201` into `zend_alloc.h:53`'s `unsigned int size:31`, which is what `efree` later uses to pick a cache slot — it does **not** reach the third (`_ecalloc`'s `int final_size` at `:295`); (3) ⚠ **the mechanism is 64-BIT-ONLY** — on a 32-bit build `long`, `size_t` and `unsigned int` are all 32 bits, `REAL_SIZE` truncates nothing, and `malloc(~2 GiB)` fails into `zend_alloc.c:189-194`'s `exit(1)`. We build 64-bit, so criterion 2 holds in our environment.""")

# --- TASK_PHP_019 §4: the sentence owed to ph03 ----------------------------
R("B-ph03-v5c116",
  "⚠ risk: the row's `cwe` is CWE-125 but the **write** fires first under ASan on most inputs. The oracle must record which, not pick one silently (spatial `NOTES.md` §5.6).",
  """⚠⚠ **`V5C-116` is a SECOND defect in this loop, not a duplicate of the first, and this row already carries both.** `:141`'s bound can be wrong (`ee > e`); independently, `:143`'s test is at 1-byte granularity while `:144-147`'s body consumes 4, so the group over-runs even a **correct** bound — V5C-116's trigger has `ee == e` exactly. Two upstream fixes, `f95c1df58349` (2004) and `1e2818b14376` (2014); **measured, the 2004 fix leaves 144 of 12 600 documents still reading past the source** (`spec.md`, `.temp/php13/02-reach.log` Q3), which is why `R2–R5` carry the 2014 check and `verus.rs` cannot verify without it. No second row: one extraction, two defects — splitting would double-count a ladder cost paid once (ph04's rule). `C.1`'s old note said *"same loop, same bound"*; **the bound is the one thing they do not share** (`TASK_PHP_019` §2.2).
⚠ risk: the row's `cwe` is CWE-125 but the **write** fires first under ASan on most inputs. The oracle must record which, not pick one silently (spatial `NOTES.md` §5.6).""")

# --- TASK_PHP_019 §10.6: ph32 rewritten (three tables, ONE fix, TWO commits)
R("B-ph32",
  """**ph32 · `entity_map`: a range declared here, a table sized there** — `ext/standard/html.c:398`, `:401`, `:896` · CRASH-089, CRASH-090 · `verbatim` · I1/O2 · echoes p27
Each `entity_map` row pairs a `char **` table with a `basechar`/`endchar` codepoint range declared **in a completely different place** from the table literal. The decode loop walks `k` from `basechar` to `endchar` inclusive and indexes `table[k - basechar]` at `:900` and `:905`, with no compiler or runtime relation between the count and the extent.
▸ trigger: any input reaching the top of a short table's range.
▸ benign: ordinary entity decoding; `u64` = fold of the decoded entities.
▸ blob: the text + a charset selector.
⚠⚠ risk: **the corpus records two short tables; there are four.** `ent_uni_spacing` (22 for 23) and `ent_uni_8592_9002` (410 for 411) are also short and are in no corpus row. A build fixing only CRASH-089/090 would still be defective. Cross-reference **ph53**: same C shape, storage sized from the other number, different vulnerability class.""",
  """**ph32 · `entity_map`: a range declared here, a table sized there** — `ext/standard/html.c:398`, `:401`, `:896`, `:900` · CRASH-089 · `verbatim` · I1/O2 · echoes p27
Each `entity_map` row pairs a `char **` table with a `basechar`/`endchar` range declared **in a completely different place** from the table literal. `:896`'s loop walks `k` from `basechar` to `endchar` **inclusive** and indexes `table[k - basechar]` at `:900`, `:905` **and `:906`**, with no compiler or runtime relation between the count and the extent (`int j, k;` at `:877`).
▸ trigger: any input reaching the top of a short table's range.
▸ benign: ordinary entity decoding; `u64` = fold of the decoded entities.
▸ blob: the text + a charset selector.
⚠⚠ risk: **the corpus records ONE short table for this row; there are THREE.** ✅ Measured with the C compiler (`.temp/php19/entcount.py`, `sizeof/sizeof[0]` over all 24 map rows) and re-measured independently (`.temp/mgr165/count_ent.py`, comment-aware, 17 tables · 4 short · 0 unevaluated): `ent_uni_338_402` **63 for 65**, `ent_uni_spacing` **22 for 23**, `ent_uni_8592_9002` **410 for 411**. **A build fixing only CRASH-089 is still defective on two tables.** ⚠ The *kinds* differ and the mechanism does not: two miscounted NULL runs (`:115-117`, `:121-123`), one miscounted run (marker at `:131`, NULLs at `:132-133`), and a compensating drift that nets to −1 (`crarr`, index 36). ⚠ Index citation: `int j, k;` is at `:878`, not `:877`.
⚠⚠⚠ **THE THREE TABLES DO NOT SHARE A FIX, AND AN EARLIER VERSION OF THIS BLOCK SAID THEY DID.** ✅ Measured at the commit (`.temp/php23/entcount-by-commit.log`, `refetch.sh`): at **`b9ff04703f16` (2005-01-11)** `ent_uni_spacing` and `ent_uni_8592_9002` are **already `ok`** while `ent_uni_338_402` is still **63 for 65**. `ent_uni_8592_9002` is repaired by **`52adad71e750`** (2005-01-11, the `8840…9002` tail rewrite); `ent_uni_spacing` by `52adad71e750` (range `732`→`731`) and then properly by **`b9ff04703f16`**; **`56adfe1f3cf1` (2005-03-09, bug #28067) touches neither** — its five `html.c` hunks are the file header, `ent_uni_338_402`, two *name* typos in `ent_uni_greek`, and three count-neutral hunks in `ent_uni_8592_9002`. All nine PHP-5.0 commits touching this file between 5.0.3 and 5.0.4 were fetched and read. **They are one row because the operation is one operation, NOT because the fix is one fix** (`TASK_PHP_023` §2.6).
⚠⚠ **R1h, AND IT IS FOUR COMMITS, NOT TWO.** For **CRASH-089 / `ent_uni_338_402`** — the row's only corpus id — R1h is `56adfe1f3cf1` **+ `85afcb802dc1`**, and ⭐ **the first one is invisibly incomplete**: it rewrites the table to the correct 65-element layout **and leaves `/* 376 (0x0178)` unterminated in the same hunk**, so it compiles to **41**; `bd07142b9128` (2005-03-10) then *"fixes the `/*`-within-comment warning"* by closing the comment **after** the swallowed block — **silencing GCC while keeping the defect**, which is how php-5.0.4 shipped at 41 with no diagnostic (✅ measured). Only `85afcb802dc1` / `bd2e99ee50ed` (2005-05-11, bug #29119) un-swallows the 24. ⚠ **If the row is built over all three tables its R1h must ALSO carry `52adad71e750` + `b9ff04703f16`**, or two of the three stay short. **Stopping at `56adfe1f3cf1` passes every syntactic check and is wrong twice over** (`ph03`'s two-hunk finding, second instance; `TASK_PHP_019` §10.4 as corrected by `TASK_PHP_023` §2.6).
⚠ Cross-reference **ph53**: same C shape, storage sized from the other number, different vulnerability class. And **ph102**, the fourth short table, which is a separate row because it has a separate fix.""")

# --- TASK_PHP_019 §4: riders on the three kills that stand -----------------
R("B-ph39-rider",
  "⚠ risk: the property table can be a fixed-slot array — a real `HashTable` is not needed and importing one buries the mechanism.",
  "⚠ risk: the property table can be a fixed-slot array — a real `HashTable` is not needed and importing one buries the mechanism. ⚠ **`CRASH-037` (`:339`) is this mechanism at a second site and the kill stands** (`TASK_PHP_019` §2.5): same unchecked predicate, same attacker quantity (a property set from userland via `unserialize`), same primitive. **Only the static type imposed on the attacker's `long` differs** — `Z_ARRVAL_P` → `HashTable*` at `:339` vs `Z_STRVAL_P` → `char*` at `:551`. ⚠⚠ **`CRASH-101` was folded in here and has MOVED to ph41** — this row's heading is *\"no tag check of any kind\"*, and `streamsfuncs.c:817`'s container **is** checked.")

R("B-ph41-rider",
  "⚠ risk: the container/element split is the mechanism. Do not fold into ph39.",
  "⚠ risk: the container/element split is the mechanism. Do not fold into ph39. ⚠ **`CRASH-101` (`streamsfuncs.c:817`) moved here from `ph39` at `TASK_PHP_019` §2.6**, which is what this line had already asked for: `params` **is** type-checked by `zend_parse_parameters(…, \"ra\", …)` at `:917`, the **element** `*tmp` is not, and `:775 Z_ARRVAL_P(options)` reads it as a `HashTable*`. Reproducer: `stream_context_set_params($ctx, array(\"options\" => 1));`. ⚠ Rider: there the identical tag test is **present at depth 2** (`:778 Z_TYPE_PP(wval) == IS_ARRAY`) and absent at depth 1 — graded as context, not mechanism, and it is the closest call in the \"stands\" column.")

R("B-ph48-rider",
  "⚠ risk: `crashes_pristine_5_0_0 = n/a (non-crash class)` — the harm is a silently broken CoW separation, visible in the checksum, not in a sanitizer. Fold `(is_ref, refcount)` into the `u64` or the row measures nothing.",
  "⚠ risk: `crashes_pristine_5_0_0 = n/a (non-crash class)` — the harm is a silently broken CoW separation, visible in the checksum, not in a sanitizer. Fold `(is_ref, refcount)` into the `u64` or the row measures nothing. ⚠ **`LOGIC-014` (`zend_builtin_functions.c:1420`) moved here from `C.1`'s ph47 fold at `TASK_PHP_019` §2.10-2.13**: `SEPARATE_ZVAL_TO_MAKE_IS_REF(arg)` (`zend.h:573-577`) expands to `if (!is_ref) { if (refcount>1) {clone}; is_ref = 1; }` and this row's `:608-610` to `if (!is_ref) { if (refcount>1) {clone} }; is_ref = 1;` — **identical in the defect case (`is_ref==0, refcount==1`), where `SEPARATE_ZVAL` is a NO-OP and both stamp the flag on the caller's live by-value slot.** Same predicate, same attacker quantity, same primitive.")

R("B-ph60-reversals",
  "⚠ risk: the wave killed all four as *\"ordinary null-deref\"*. That is a **quality** judgement, which the bar does not carry; the correct application is one family row plus three duplication kills.",
  "⚠⚠ risk: ⚠⚠ **THE THREE MERGES ARE GONE — `CRASH-061` → `ph96`, `CRASH-126` → `ph97`, `CRASH-163` → `ph98` (`TASK_PHP_019` §2.7-2.9).** In `ph96` the call returns **SUCCESS** and NULLs the out-parameter on purpose (`zend_execute_API.c:592-595`); in `ph97` the failure **is** tested and the call does **not** fail (`|` makes the argument optional); in `ph98` the failure is tested and it is the **error branch** that faults, on a global this function itself cleared. *\"Failure not tested\"* is false at all three, so this row is `CRASH-088` alone. ⚠ The wave killed all four as *\"ordinary null-deref\"*: that is a **quality** judgement, which the bar does not carry.")

# --- Part C: C.1, rewritten.  No row is DELETED (TASK_PHP_012 M1). ---------
R("C1-table",
  """| CRASH-090 `html.c:155/:401` | **ph32** | literally the same defect on a different table; folded into ph32's `corpus rows` |
| V5C-116 | **ph03** | same loop, same bound, merged by the corpus itself |
| V5C-173 | **ph11** | same one-sided compare, merged by the corpus itself |
| V5C-015 | **ph22** | same two-pass sizing mismatch, merged by the corpus itself |
| CRASH-037, CRASH-101 | **ph39** | same missing-tag-guard read; carried inside ph39's `corpus rows` |
| CRASH-061, CRASH-126, CRASH-163 | **ph60** | same \"fallible call's failure not tested\"; carried inside ph60's `corpus rows` |
| LOGIC-003, LOGIC-008, LOGIC-014, LOGIC-018 | **ph47** | all family E — `is_ref` stamped on, or not separated from, a live shared slot; LOGIC-017 was **kept** as ph48 because it forces the flag rather than failing to clear it |

⚠ These are the only kills in this catalogue that rest on §3.1, and every one of
them is a **merge** — the row survives inside another row's `corpus rows`, which
is how the temporal miner applied the rule and is the right shape.""",
  """| ~~CRASH-090 `html.c:155/:401`~~ | ⚠ **KILL WITHDRAWN → `ph102`** | the note **in full**: *\"literally the same defect on a different table; folded into ph32's `corpus rows`\"*. ⚠⚠ **The operation is the same; the FIX is not.** `ent_uni_punct` is repaired by `35e43dabe16b` / `46bc2c5ae2ae` (2004-07-19, bug #29199), which leaves ph32's three tables short **through php-5.0.3 — measured, tag by tag** — and ph32's own fix `56adfe1f3cf1` (2005-03-09, bug #28067) does not touch `ent_uni_punct`. Two upstream fixes, neither repairing the other (`TASK_PHP_019` §10). ⚠ The corpus's own round-2 adversarial verifier had already broken this merge (`dedup2-verify.json`, `M6-html-tables`, `merge_holds: false`) |
| ~~V5C-116 `uuencode.c:145`~~ | ⚠ **KILL WITHDRAWN, NO NEW ROW → stays in `ph03`** | the note **in full**: *\"same loop, same bound, merged by the corpus itself\"*. ⚠⚠ **The bound is the one thing the two triggers do not share**: `ph03`/V5C-115's `ee` is *wrong* (`ee > e`); V5C-116's `ee == e` is *right* and the loop still over-runs, because `:143` tests at 1-byte granularity while `:144-147` consumes 4. Two upstream fixes, and this project has **measured** that the 2004 one leaves 144 of 12 600 documents still reading past the source. **No new row** — `ph03` already extracts the whole function and carries both defects (`TASK_PHP_019` §2.2) |
| ~~V5C-173 `zend_execute.c:4033`~~ | ⚠ **KILL WITHDRAWN → `ph94`** | the note **in full**: *\"same one-sided compare, merged by the corpus itself\"*. ⚠⚠ **Same line, different defect.** `ph11`/V5C-145 is the *range* check on a well-typed signed index (CWE-125); this is the *tag* check (CWE-843), and the corpus's own V5C-173 validator wrote *\"genuinely two distinct source-level mistakes on one line\"* before the merge (`TASK_PHP_019` §2.3) |
| ~~V5C-015 `pack.c:212`~~ | ⚠ **KILL WITHDRAWN → `ph95`** | the note **in full**: *\"same two-pass sizing mismatch, merged by the corpus itself\"*. ✅ True of the sizing, and the sizing is not the whole defect: `ph22`'s `H` arm **cannot reach `:212`** (it is in *\"always uses one arg\"*, which does a bare `currentarg++`), while V5C-015 chains `:212`'s wrap into a **guard defeated by the wrap of its own operand** at `:214`. The corpus's own validator asked for exactly this split — *\"keep :212 as the distinguishing member\"* (`TASK_PHP_019` §2.4) |
| CRASH-037 `zend_exceptions.c:339` | **ph39** | **Mechanism, not cost**: same unchecked predicate (the `type` tag, before a `Z_*VAL_P` macro that consults none), same attacker quantity (the type of a property set from userland via `unserialize`), same primitive (an attacker-chosen `long` dereferenced as a pointer). Only the static type imposed on that pointer differs — `Z_ARRVAL_P` → `HashTable*` at `:339` vs `Z_STRVAL_P` → `char*` at `:551`. ✅ **Kill stands**; carried inside ph39's `corpus rows`, with the type difference a rider on ph39's block |
| CRASH-101 `streamsfuncs.c:817` | **ph41** ⚠ **(was ph39 — corrected)** | **Mechanism, not cost**, and the target was wrong. `params` **is** type-checked, by `zend_parse_parameters(…, \"ra\", …)` at `:917`; the **element** `*tmp` is not, and `:775 Z_ARRVAL_P(options)` reads it as a `HashTable*`. That is **ph41 — *container checked, elements not*** on all three tests, and ⚠ **ph39's heading is *\"no tag check OF ANY KIND\"*, which this site does not satisfy** — ph41's own `⚠ risk` line already said *\"the container/element split is the mechanism. Do not fold into ph39.\"* ✅ **Kill stands; moved to ph41's `corpus rows`** |
| LOGIC-014 `zend_builtin_functions.c:1420` | **ph48** ⚠ **(was ph47 — corrected)** | **Mechanism, not family**, and the target was wrong. `SEPARATE_ZVAL_TO_MAKE_IS_REF(arg)` (`zend.h:573-577`) expands to `if (!is_ref) { if (refcount>1) {clone}; is_ref = 1; }`; ph48's `zend_execute_API.c:608-610` expands to `if (!is_ref) { if (refcount>1) {clone} }; is_ref = 1;`. **In the defect case (`is_ref==0, refcount==1`) `SEPARATE_ZVAL` is a NO-OP and both stamp the flag on the caller's live by-value slot.** ph48 is the row this table's own sentence said was **kept** for forcing the flag; this is that mechanism at a second site. ✅ **Kill stands; moved to ph48's `corpus rows`.** ⚠ `TASK_PHP_012` M2 reached this C and still filed the row as non-exact; that half of M2 is retracted |
| ~~CRASH-061, CRASH-126, CRASH-163~~ | ⚠ **KILLS WITHDRAWN → `ph96`, `ph97`, `ph98`** | the note **in full**: *\"same 'fallible call's failure not tested'; carried inside ph60's `corpus rows`\"*. ⚠⚠ **False at all three.** CRASH-061: the call returns **SUCCESS** and NULLs the out-parameter deliberately (`zend_execute_API.c:592-595`, comment quoted verbatim in ph96). CRASH-126: the failure **is** tested at `mbstring.c:3215` and the call **succeeds** — `|` makes the argument optional. CRASH-163: the failure is tested at `zend.c:1078` and the **error branch** is the one that faults, on a global `:1075` cleared itself. ⚠ **Three ids killed TWICE — once inside `C.4`'s six-member set, then again inside this one-sentence three-id row — so neither kill ever acquired a row-level entry to attack** (`TASK_PHP_019` §6) |
| ~~LOGIC-003, LOGIC-008, LOGIC-018~~ | ⚠ **KILLS WITHDRAWN → `ph99`, `ph100`, `ph101`** | the note **in full**: *\"all family E — `is_ref` stamped on, or not separated from, a live shared slot; LOGIC-017 was **kept** as ph48 because it forces the flag rather than failing to clear it\"*. ⚠⚠ **`SEPARATE_ZVAL` is a NO-OP at `refcount == 1`, and that one fact splits the four.** LOGIC-003: **no separator is called at all** on the `__get` read-write path, and the harm is in-place *mutation* seen by another holder, not in-place *retype*. LOGIC-008: a separator that **fires where it must not**, unconditionally, tearing a deliberate reference set apart on a plain read — the exact opposite of ph47. LOGIC-018: **two dictionary slots aliased by a hash update that also destroys what it replaces**, with no separation and no `is_ref` on that path. **LOGIC-014 is the one that IS exact — against ph48, not ph47** (row above) (`TASK_PHP_019` §2.10-2.13) |

⚠⚠ **This table shrank from 12 merges to 3 at `TASK_PHP_019`, which ran the test
`ADJUDICATION_002` never ran: *does the C support the mechanism claim?*** Ten of
the thirteen failed it. **Every withdrawn kill stays in place above with its
original note quoted in full** — `TASK_PHP_012` M1: *a kill that vanishes is
worse than a kill that was wrong.* ⚠ And the three that stand now state a
**mechanism** reason, because the old notes stated a family or a cost reason
even where the verdict was right.

⚠⚠⚠ **`\"merged by the corpus itself\"` DOES NOT MEAN WHAT THIS TABLE USED IT TO
MEAN, and it was the WEAKEST evidence here, not the strongest.** The corpus's
`merged_members` field is *root-cause dedup with the burden of proof set on
**distinct***  (`validation/REPORT.md`, \"Method\"); `PLAN_PHP.md` §3.1's bar is
*exact C mechanism with the burden on **same***. Citing one to support the other
is citing a `not-proven-distinct` as a `proven-same`. ⚠ And **all three** of the
merges cited that way — V5C-116, V5C-015, V5C-173 — had been flagged by the
corpus's **own per-case validators**, in writing, in `verdicts.json`, as covering
two separately-fixed defects, *before* the merge was made.""")

# --- Part C: C.4's last row now points at the three new rows ---------------
R("C4-nullderef",
  "| **CRASH-082, CRASH-088, CRASH-061, CRASH-126, CRASH-163, CRASH-021** | *\"the 'ordinary null-deref' set — mechanism-quality judgement on the C, which the bar permits\"* | ⚠ **the bar does not permit mechanism quality.** `PLAN_PHP.md` §3 has four criteria and `CLAUDE.md` rule 6 names three C-side tests, of which the only comparative one is **distinctness**. Six rows were removed by a fifth, unwritten criterion. CRASH-082 is not even in the family — `!f(x) == SUCCESS` is a **precedence** defect in a guard that runs | **ph59** + **ph60** (one family row, three merges under C.1) + CRASH-021 under C.2 |",
  """| **CRASH-082, CRASH-088, CRASH-061, CRASH-126, CRASH-163, CRASH-021** | *\"the 'ordinary null-deref' set — mechanism-quality judgement on the C, which the bar permits\"* | ⚠ **the bar does not permit mechanism quality.** `PLAN_PHP.md` §3 has four criteria and `CLAUDE.md` rule 6 names three C-side tests, of which the only comparative one is **distinctness**. Six rows were removed by a fifth, unwritten criterion. CRASH-082 is not even in the family — `!f(x) == SUCCESS` is a **precedence** defect in a guard that runs | **ph59**, **ph60**, **ph96**, **ph97**, **ph98** + CRASH-021 under C.2 |

⚠⚠ **`C.4` REVERSED a set kill and the reversal put three of its members
straight into a SECOND set kill** — `C.1`'s one-sentence, three-id `ph60` row —
so `CRASH-061`, `CRASH-126` and `CRASH-163` were killed twice and **never
acquired an individual entry that row-level review could reach.** All three
reverse at source and are now `ph96`, `ph97`, `ph98` (`TASK_PHP_019` §6).
**The rule F22 needs as a rider: when you reverse a set-shaped kill, its members
must land as individual entries — reversing a set into a set is not a
reversal.** ✅ Enumerated against `index.csv`, not against the prose: the corpus
has **14** `CWE-476` rows, the set named **6**, and there is **no hidden
seventh** — the other eight were never inside it and are all catalogued
(`ph15`, `ph46`, `ph54`, `ph55`, `ph56`, `ph57`, `ph90`, `ph91`). That is a
clean negative and it is worth recording as one.""")

# --- Part C: C.7's pasted coverage output, refreshed ----------------------
# ⚠ The pasted block was ALREADY stale before this landing (it says 91 rows /
# 161 ids; the file held 93 / 163 when TASK_PHP_021 measured it).  It is not
# re-pasted verbatim here, because `coverage.py`'s own row-count line is WRONG
# on a 102-row file -- see the warning folded into the replacement.
R("C7-output",
  """```
corpus rows in index.csv : 166
Part A distinct corpus ids : 161
Part C kill-table ids      : 30

accounted for              : 166 / 166
MISSING (in corpus, not in catalogue) : 0
ids the catalogue names that the corpus does not have : 3  ['V5C-015', 'V5C-116', 'V5C-173']

ids claimed by MORE THAN ONE catalogue row : 3
   CRASH-153   ['ph49', 'ph50']
   LOGIC-011   ['ph77', 'ph83']
   LOGIC-022   ['ph77', 'ph83']

catalogue rows in Part A : 91  (ids ph01..ph91, gaps: none)
Part B blocks            : 91  (in Part A but not Part B: none)
```

**91 catalogued rows carry 161 of the 166 corpus ids.**""",
  """```
corpus rows in index.csv : 166
Part A distinct corpus ids : 167
Part C kill-table ids      : 30

accounted for              : 166 / 166
MISSING (in corpus, not in catalogue) : 0
ids the catalogue names that the corpus does not have : 3  ['V5C-015', 'V5C-116', 'V5C-173']

ids claimed by MORE THAN ONE catalogue row : 3
   CRASH-153   ['ph49', 'ph50']
   LOGIC-011   ['ph77', 'ph83']
   LOGIC-022   ['ph77', 'ph83']

catalogue rows in Part A : 102          <- ⚠ coverage.py prints 99; see below
Part B blocks            : 102          <- ⚠ coverage.py prints 99; see below
```

⚠⚠ **`coverage.py`'s ROW-COUNT LINE IS BLIND TO THREE-DIGIT ROW IDS, AND IT
CANNOT REPORT THAT IT IS.** Its last two checks use `^\\| (ph\\d\\d) \\|` and
`^\\*\\*(ph\\d\\d) ` — **exactly two digits** — so `ph100`, `ph101` and `ph102`
are invisible to them; and the `gaps:` set is built as `ph01..ph<number it
found>`, i.e. **from its own hit count**, so a file three rows short of its own
view still prints `gaps: none`. ✅ Measured at `TASK_PHP_021`: 99 seen, 102
present, `['ph100','ph101','ph102']` missing, `gaps: none` printed. The two
numbers above are the true ones. ⚠ **The `166 / 166` accounting is NOT affected**
— that path scans `line.startswith("| ph")` and does see them — but the row
count must be fixed before it is pasted here again.

⚠⚠ **AND `166 / 166` IS NECESSARY, NOT SUFFICIENT.** `coverage.py` counts a
mention **in the kill table** as coverage, and it cannot detect an id merged
into the **wrong** row: an id sitting in the wrong `corpus rows` cell is
invisible to it by construction. `TASK_PHP_019` found **two** such mis-merges
(`CRASH-101` under ph39, `LOGIC-014` under ph47) that this check reported green
throughout. **Nothing here certifies the moves; only the mechanism test does.**

**102 catalogued rows carry 167 of the 166 corpus ids** (167 because
`V5C-015`, `V5C-116` and `V5C-173` are `merged_members`, not `input_id`s — see
the note below — and `CRASH-153`, `LOGIC-011`, `LOGIC-022` are each claimed by
two rows on purpose).""")

# --- §9: the derived labels ------------------------------------------------
R("S9-derived",
  """5. **`inv/obl` is the corpus's blind labelling, carried across unmodified.** It
   was produced by analysts forbidden to read the Rust port, which is why it is
   worth carrying — but this task did not re-derive a single label.""",
  """5. **`inv/obl` is the corpus's blind labelling, carried across unmodified** —
   ⚠ **except on the nine rows marked `†` in Part A (`ph94`–`ph102`), where it
   is DERIVED.** The corpus has no label for those, so `TASK_PHP_019` §5 read
   them off the obligation texts in `paper/invariants-list.md`. The carried
   labels were produced by analysts forbidden to read the Rust port, which is
   why they are worth carrying; the derived ones carry no such warrant and were
   not blind. **`echoes` on those rows is likewise a reading nobody has checked
   against the `pNN` row** (§0.3, and `TASK_PHP_019` §9.3 names `p48` on `ph94`
   and `p05` on `ph95` as the two it is least sure of).
6. **Criterion 2 is not demonstrated for `ph94`–`ph102`** — no detector was run
   and no positive control was built. Neither was it for the other 93; it is
   discharged at build (`ADJUDICATION_002` §2's rule, applied unchanged).
7. ⚠⚠ **Three of the nine new rows had their `▸ trigger` corrected before
   landing, and one of those corrections is a MEASUREMENT that narrows the
   row** (`TASK_PHP_021` §2). `ph94`'s trigger reaches the cited line and, on
   this box's toolchain, **produces no out-of-bounds read at any optimisation
   level**; `ph98`'s original trigger is refused by a registration-time guard;
   `ph101`'s could not be observed as written. The other six were clean.""")

# ---------------------------------------------------------------------------
# 2. INSERTIONS -- (name, anchor, text).  Inserted BEFORE `anchor`, which must
#    occur exactly once.  The new Part B blocks.
# ---------------------------------------------------------------------------

INSERT = []


def I(name, anchor, text):
    INSERT.append((name, anchor, text))


I("B-ph95", "### S4 — declared extent ≠ realised extent",
  """**ph95 · `pack`: the argument-count guard defeated by its own wrap** — `ext/standard/pack.c:212`, `:214`, `:262` · V5C-015 · `narrowed` · I11/O1 † · echoes p05 †
The *"use as many args as specified"* arm does `:212 currentarg += arg;` and then `:214 if (currentarg > argc) RETURN_FALSE;` — **the guard exists, runs, and is false**, because with `arg = INT_MAX` its own operand has already wrapped `currentarg` to `INT_MIN`. Only then does `:262 outputpos += arg * 2;` wrap to `-2`, leaving `outputsize` at 0 and `:304 emalloc(1)`; the emit arm at `:388-391` then writes 2 bytes per iteration for `arg` iterations and walks `argv` past its `argc` entries. ⚠ **`ph22` cannot reach `:212`**: `H` is in the *"always uses one arg"* arm (`:174-191`), which does a bare `currentarg++`. Two upstream fixes: `6d98fc38b53` (2004) repairs `:262`, `db420cb6a14` (2019, bug #78833) adds `if (currentarg > INT_MAX - arg)` before `:212`; neither repairs the other.
▸ trigger: `pack("s2147483647", 1)`. ✅ **Measured** (`.temp/php21/ph95_probe.c`, the declarations lifted verbatim): the guard at `:214` is defeated identically at `-O0`, `-O3` and `-O3 -fwrapv` on gcc 13.3.0 — `currentarg = -2147483648`, `outputpos = -2`, `emalloc(1)` — while the neighbours `arg = INT_MAX-1` and `arg = 2147483645` are **REFUSED**, which is the control showing the guard is defeated *by the wrap* and by nothing else.
▸ benign: ordinary count-based formats; `u64` = the packed bytes' checksum.
▸ blob: the format codes + the argument count + the arguments.
⚠ risk: **the row's claim is `:212`, not the sizing** — an extraction that lifts only `:262` has rebuilt ph22. ⚠⚠ **THE WRAP AT `:212` IS SIGNED-INTEGER OVERFLOW, i.e. UNDEFINED BEHAVIOUR, AND UNLIKE `ph29` THERE IS NO UB-FREE TRIGGER** — `arg` cannot be negative (`:208-210` rewrites any negative `arg`, and the digit scanner at `:152-158` admits no sign), so the only way past `:214` is the wrap, and upstream's own fix is a *pre-overflow test*. `harness/build.py` is frozen and passes neither `-fwrapv` nor `-fno-strict-overflow`; the measurement above says the three builds agree today, and a kernel must re-run it rather than assume (`TASK_PHP_021` §2). ⚠ Re-adjudicated out of `C.1` at `TASK_PHP_019`; the corpus's own V5C-015 validator asked for exactly this split (*"keep :212 as the distinguishing member"*).

""")

I("B-ph102", "### S5 — two passes compute one index differently",
  """**ph102 · `ent_uni_punct`: the table with no run comments, and the element nobody counted** — `ext/standard/html.c:155`, `:401`, `:900` · CRASH-090 · `verbatim` · I1/O2 † · echoes p27 †
`:401 { cs_utf_8, 8194, 8260, ent_uni_punct }` declares **67** slots; the literal at `:155-166` has **66**. Same read site as ph32, **different defect and different fix.** ⭐ **It is the only `cs_utf_8` table written as a flat dense list with no `/* codepoint */` run markers**, so nothing in the source states any entry's intended value — and the defect is a single omitted `NULL` placeholder for U+201F, immediately before `"dagger"` at `:161`. ✅ Localised from the source text alone (`.temp/php19/entdrift.py`, HTML4 entity names as the oracle): correct through `bdquo` (index 28 → U+201E), then uniformly **−1** — `dagger`→U+201F, `Dagger`→U+2020, `bull`→U+2021, `hellip`→U+2025, `permil`→U+202F, `prime`→U+2031, `oline`→U+203D, `frasl`→U+2043. Reproduces the corpus verifier's eight control-binary values exactly, with no binary.
▸ trigger: `html_entity_decode('&frasl;', ENT_QUOTES, 'UTF-8')` — anything reaching the top of 8194..8260. ✅ **Reachability re-checked at `TASK_PHP_021`**: `PHP_FUNCTION(html_entity_decode)` passes `all = 1` **unconditionally** (`:1219`), so `:890 if (all)` is always taken and the walk covers every `cs_utf_8` row; at `k = 8260` `:900` indexes `table[66]` of a 66-element literal. The count is measured by two independent tools that agree (`.temp/php19/entcount.py`, with the C compiler; `.temp/mgr165/count_ent.py`, comment-aware — 17 tables · 4 short · 0 unevaluated).
▸ benign: punctuation entities decode; `u64` = fold of the decoded code points.
▸ blob: the text + a charset selector.
⚠ risk: **R1h is `35e43dabe16b` (PHP-5.0) / `46bc2c5ae2ae` (HEAD), 2004-07-19, bug #29199** — it inserts the missing `NULL` **and adds the `/* 8216 */` and `/* 8242 */` markers that were absent**, which is the row's whole point: the scaffolding that would have made the miscount visible was not there. ⚠ **Do not merge into ph32**: ph32's three tables are repaired by `56adfe1f3cf1` (2005-03-09), which does not touch this one, and this fix left all three of ph32's standing — **measured: they are still short at php-5.0.1, 5.0.2 and 5.0.3.** Two fixes, neither repairing the other → `PLAN_PHP.md` §3.1. ⚠ Before the OOB read at `k = 8260`, the whole tail from U+2020 up **decodes to the wrong code point** — a silent correctness defect the corpus's `global-buffer-overflow` label does not name.

""")

I("B-ph94", "### T2 — a type-changing write through a value that was not separated",
  """**ph94 · the offset's TYPE is never checked, so the index is struct padding** — `Zend/zend_execute.c:4033` with `Zend/zend.h:270-284` · V5C-173 · `narrowed` · I4/O1 + I3/O2 † · echoes p35, p48 †
`:4025-4037` reads `offset->value.lval` as a byte index with **no type test and no `convert_to_long` anywhere in the arm**. For an `IS_OBJECT` offset the union's active member is `value.obj` = `{ zend_object_handle handle; zend_object_handlers *handlers; }` (`zend.h:270-273`), so on LP64 `lval` is **`[4 defined handle bytes | 4 bytes of struct padding that `zend_objects_new`'s stack-returned value never writes]`** — ✅ confirmed at `TASK_PHP_021` from the `-O0` disassembly: `zend_objects.c:99` stores only `%eax` into the 8-byte slot. `I4/O1` ("must not read `value.obj` from a zval whose tag does not select that member") composed with `I3/O2` ("must not use a value read from such a slot as … a size, or length").
▸ trigger: `$s = "abcdefgh"; $o = new stdClass; empty($s[$o]);` — ✅ **Measured, and it DOES read out of bounds** (`.temp/php23/ph94_probe3.c`, gcc 13.3.0, identical at `-O0`, `-O1`, `-O2`, `-O3`): with the zval taken from the allocator the way `zend_execute.c:3245 ALLOC_ZVAL` really takes it, `lval` is `handle | (residue << 32)`, the guard `offset->value.lval <= Z_STRLEN_PP(container)` is trivially true for a negative `long`, and `:4033` reads at a wild displacement. **The `-O0` disassembly of `zend_API.c:710` is the mechanism**: `mov %ecx,(%rbx)` writes the 4-byte handle and `mov %rax,0x8(%rbx)` the handlers — **bytes 4–7 are never written by anything.** ⚠⚠ **`TASK_PHP_021` §2.1 reported the opposite** (*"no out-of-bounds read at any `-O`"*); its probe opened each trial with a `memset(&arg, 0, sizeof arg)` labelled `zend_API.c:692`, and **PHP does no such memset** — `:692` is the function's signature and `zend_API.c:708` writes only `arg->type`. It was reading its own zeroes. Retracted at `TASK_PHP_023` §2.2. The corpus's valgrind *"Use of uninitialised value of size 8"* at `:4033` is corroborated, not contradicted.
▸ benign: `IS_LONG` offsets answer correctly; `u64` = fold of the boolean answers.
▸ blob: a string + a `(tag, payload)` offset stream, one payload deliberately left unwritten.
⚠⚠ risk: **the kernel must take the un-written half from the BLOB** — not because a faithful producer gives zeros (it does not; §2.2) but because it gives whatever `emalloc` left, which is neither reproducible nor measurable. ⚠ **Declare it in the divergence ledger as `kind: projection`** (`PROTOCOL_PHP.md` §A2) — *"a behaviour outside the extracted span modelled by a narrower one"* — and never as a convenience. ⚠⚠ **And say what stops the row becoming ph11**: the blob supplies the **padding**, while the `(tag, payload)` stream still decides whether the payload is read as an index at all. A kernel that lets the blob choose the index directly has rebuilt ph11. **Criterion 2 is discharged against the blob-driven kernel, with the faithful producer's behaviour reported beside it.** ⚠ **Do not fold into ph11** — ph11 is the *range* check on a well-typed signed index (CWE-125); this is the *tag* check (CWE-843), and the corpus's own V5C-173 validator calls them *"genuinely two distinct source-level mistakes on one line"*. ⚠ Re-adjudicated out of `C.1` at `TASK_PHP_019` §2.3.

""")

I("B-T2-new", "### T3 — initialised before read",
  """**ph99 · a read handler's result mutated in place on the read-WRITE path** — `Zend/zend_object_handlers.c:296-300`, `:311` with `Zend/zend_execute.c:1266`, `:1277-1281` · LOGIC-003 · `narrowed` · I9/O2 † · echoes p49 †
`zend_std_read_property`'s `__get` arm does `rv = zend_std_call_getter(…); if (rv) { retval = &rv; }` and `:311 return *retval;` — **the getter's zval is returned unseparated even for `BP_VAR_RW`**. The consumer `zend_post_incdec_property` then does `:1266 read_property(object, property, BP_VAR_RW)`, `:1277 *retval = *z;`, **`:1279 incdec_op(z)` with no separator at all**, `:1281 write_property(…, z)`. ⚠ **Not ph47**: ph47's separator *runs and no-ops* because `is_ref == 1`; here none is called. The sibling `zend_pre_incdec_property` **does** separate, at `:1220`. `I9/O2`: *"a value handed out for read-write access must be either exclusively owned by the writer or a reference the program itself wrote."*
▸ trigger: `class O { public $q = 3; function __get($n){ return $this->q; } } $o = new O; $o->virt++;` → `$o->q` is 4. ✅ **Chain re-traced at `TASK_PHP_021`**: `zend_std_get_property_ptr_ptr` returns NULL when a `__get` exists (`:470-473`), so `have_get_ptr == 0` and `:1266` runs; `ZEND_RETURN`'s by-value arm hands back the **live** zval (`zend_execute.c:2883-2886`, `*EG(return_value_ptr_ptr) = retval_ptr; retval_ptr->refcount++`), not a copy.
▸ benign: declared properties increment without touching anything else; `u64` = fold of every slot's value after each op.
▸ blob: a slot stream + an op stream, with a `via_handler` bit per op.
⚠ risk: **a boolean `shared` bit is enough** — importing refcounts adds ph69/ph70's mechanism to a row that is not about them (ph47's rule). ⭐ **And the blast radius is larger than the trigger says**: `zend_API.c:716` populates an object's properties with `zend_hash_copy(…, zval_add_ref, …)`, so `$o->q`'s zval **is** `ce->default_properties["q"]` — the in-place increment moves the *class default*, and a later `new O` starts at 4. ⚠ Re-adjudicated out of `C.1`'s four-`LOGIC` set kill at `TASK_PHP_019` §2.10-2.13.

**ph100 · the separator fires where it must not, and clears the binding** — `Zend/zend_object_handlers.c:797` with `Zend/zend_execute_API.c:430`, `:458` and `Zend/zend.h:554-566` · LOGIC-008 · `narrowed` · I8/O2 + I9/O5 † · echoes p49 †
`inherit_static_prop` (`zend_compile.c:1967-1971`, run from `zend_do_inheritance`'s `:1990 zend_hash_merge`) binds a child's static slot to the parent's zval — `refcount++; is_ref = 1;`. Every access then runs `:797 zval_update_constant(retval, 1)`, whose `IS_CONSTANT` (`:430`) and `IS_CONSTANT_ARRAY` (`:458`) arms call **`SEPARATE_ZVAL(pp)` unconditionally** — and `zend.h:558-564` separates on `refcount>1` **regardless of `is_ref`**, then sets `is_ref = 0`. ⭐ **A deliberate reference set is torn apart by a plain READ.** ⚠ **The opposite of ph47** — a separator that acts where it must not, where ph47's no-ops where it must act. `I8/O2`: *"must not clear or lose a binding the program did write."*
▸ trigger: `define('K',5); class A { public static $p = K; } class B extends A {} B::$p = 7;` → `A::$p` is still 5. ✅ **Re-traced at `TASK_PHP_021`**: `public static $p = K;` really does compile to an `IS_CONSTANT` zval (`zend_do_fetch_constant`, `zend_compile.c:2835-2843`, `ZEND_CT` arm), and the **write** path reaches `:797` too — `zend_fetch_var_address_helper` calls `zend_std_get_static_property` at `zend_execute.c:753` for **every** `BP_VAR_*`, not only reads.
▸ benign: a plain-literal static default keeps the binding; `u64` = fold of every slot's `(value, is_ref, refcount)`.
▸ blob: a slot stream with a per-slot `needs_resolution` bit and a bound-pairs list.
⚠ risk: **the constant-resolution step is the trigger, not the mechanism** — model it as one bit, not as a constant table. `crashes_pristine_5_0_0` is `n/a` (non-crash class), like every other refcount-logic row including ph48; criterion 2 is discharged at build. ⚠ Re-adjudicated out of `C.1`'s four-`LOGIC` set kill at `TASK_PHP_019` §2.10-2.13.

**ph101 · two dictionary slots aliased by an update that destroys one** — `Zend/zend_compile.c:1899-1900` with `:1967-1971` · LOGIC-018 · `narrowed` · I9/O1 + I8/O1 † · echoes p49 †
When a child redeclares a parent's `protected static` as `public static`, `do_inherit_property_access_check` does `:1899 (*prop)->refcount++;` — `prop` is the **parent's** zval — then `:1900 zend_hash_update(ce->static_members, child_info->name, …, (void**)prop, sizeof(zval*), NULL);`. **The child's own freshly-compiled default zval is destroyed by the table's destructor and the slot is re-pointed at the parent's**, with no separation; `:1901` then deletes the child's inherited mangled copy. The enabling helper `:1967-1971 inherit_static_prop` has already stamped `is_ref = 1` on the general merge path. ⚠ **Neither ph47 (no separator no-ops here) nor ph48 (no `is_ref` on this path)**: the defect is the aliasing update itself.
▸ trigger: ⚠ **`A::$x` is `protected`, so it cannot be read from global scope** (`zend_object_handlers.c:783-784` raises E_ERROR) and the second half needs its parent declared — the runnable form is `class A { protected static $x = "PARENT"; static function get(){ return A::$x; } } class B extends A { public static $x; } B::$x = "W"; var_dump(A::get());` → `"W"`; and `class C { protected static $y; } class D extends C { public static $y = "CHILDVAL"; } var_dump(D::$y);` → **NULL**, the child's declared default destroyed by `:1900`. ⚠ **The child's slot must be left uninitialised**: `:1891-1897` raises `E_COMPILE_ERROR` when *both* defaults are non-NULL, so `public static $x = "..."` under a non-NULL parent default never reaches `:1899` (`TASK_PHP_021` §2).
▸ benign: an ordinary override gets its own storage; `u64` = fold of every slot's `(value, identity)` after inheritance.
▸ blob: a class/slot declaration stream + a write stream.
⚠ risk: ⚠ **cite `:1899-1900`, the primary site.** `TASK_PHP_012` M2 priced `:1967-1971` (the helper) and reached the right verdict from the wrong frame. `crashes_pristine_5_0_0` is `n/a` (non-crash class). ⚠ **`zend_hash_update`'s destroy-then-replace is load-bearing** — a dictionary without a value destructor deletes half the mechanism. ⚠ Re-adjudicated out of `C.1`'s four-`LOGIC` set kill at `TASK_PHP_019` §2.10-2.13.

""")

I("B-T6-new", "## TEMPORAL",
  """**ph96 · SUCCESS does not mean the out-parameter was written** — `Zend/zend_object_handlers.c:509`, `:512-513` with `Zend/zend_execute_API.c:592-595` · CRASH-061 · `narrowed` · I12/O1 + I16/O2 † · echoes p42 †
`zval *retval;` then `:512 zend_call_method_with_1_params(…, &retval, offset); :513 zval_ptr_dtor(&retval);` — **no test of any kind**, and testing the status would not help: `zend_call_function` writes `*fci->retval_ptr_ptr = NULL` at `:595` under its own comment *"we may return SUCCESS, and yet retval may be uninitialized, if there was an exception"*, and returns `SUCCESS` unconditionally at `:873` even when `EG(exception)` is set (`:870-872`). Two outputs whose relationship is non-trivial, where ph60 has one. `I12/O1` names the case verbatim — *"a NULL return, sentinel, status code, **or NULL-able out-parameter** must be tested"* — and `I16/O2` is *"the outputs of an aborted call must not be … destroyed"*.
▸ trigger: `class C implements ArrayAccess { … function offsetUnset($o){ throw new Exception("boom"); } } $c = new C; unset($c[0]);` → `_zval_ptr_dtor` (`zend_execute_API.c:389`) derefs NULL. ✅ **Traced end to end at `TASK_PHP_021`**; `:511` requires the class to implement `ArrayAccess`, which the trigger must therefore say.
▸ benign: ordinary `offsetUnset` returns and its result is released once; `u64` = fold of `(status, out!=NULL)` per call.
▸ blob: a call-outcome stream carrying `(status, wrote_out)` **independently**.
⚠ risk: **the two flags must be independent in the blob** — a kernel that derives `wrote_out` from `status` has deleted the mechanism and rebuilt ph60. ⚠ Re-adjudicated out of `C.1` at `TASK_PHP_019` §2.7; ph60's *"failure not tested"* is false here, the call succeeds.

**ph97 · the optional argument the parser never writes** — `ext/mbstring/mbstring.c:3211`, `:3215`, `:3219` · CRASH-126 · `narrowed` · I12/O3 † · echoes —
`char *typ = NULL;` at `:3211`; `:3215 zend_parse_parameters(…, "|s", &typ, &typ_len)` — **the `|` makes it optional, so zero arguments returns SUCCESS and `typ` is never written**; `:3219 strcasecmp("all", typ)` hands the caller's own NULL to libc. ⚠ **The failure IS tested and the call does NOT fail.** The guard answers *"were the supplied arguments well-typed?"*; the code reads it as *"was the optional argument supplied?"* — a **different proposition**, whose real test is `ZEND_NUM_ARGS()` or `typ != NULL`. `I12/O3`: *"a possibly-NULL pointer must not be passed to a callee — including libc — that dereferences it without testing it."*
▸ trigger: `mb_get_info()` — zero arguments. ✅ **Verified at source at `TASK_PHP_021`**: `zend_parse_va_args` computes `min_num_args = 0` from the `|` (`zend_API.c:485-487`), passes the count test at `:511`, and its write loop `:537 while (num_args-- > 0)` runs **zero** times before `return SUCCESS`. The cheapest and most reliable trigger of the nine.
▸ benign: `mb_get_info("internal_encoding")` and friends answer; `u64` = the selected settings' checksum.
▸ blob: an argument-presence bitmap + the argument bytes.
⚠ risk: `zend_parse_parameters` must be **modelled with an optional spec**, not stubbed to always-write — the optionality is the defect. ⚠ Re-adjudicated out of `C.1` at `TASK_PHP_019` §2.8 (`ADJUDICATION_002` §5 found it first).

**ph98 · the global the caller cleared, read back on the error path** — `Zend/zend.c:1074-1075`, `:1078`, `:1083` · CRASH-163 · `narrowed` · I16/O4 + I12/O2 † · echoes —
`:1074 old_exception = EG(exception); :1075 EG(exception) = NULL;` — **this function moves the exception out itself** — then `:1078 if (call_user_function_ex(…) == SUCCESS) {…} else { :1083 zend_exception_error(EG(exception)); }`. The status test is present and correct; **the fault is on the branch where it says FAILURE**, and the argument the error reporter needs is the thing the error path cannot supply — `zend_exception_error`'s first statement is `Z_OBJCE_P(exception)` (`zend_exceptions.c:519`) → `zend_get_class_entry` → `Z_OBJ_HT_P(NULL)` (`zend_API.c:204`). Upstream `79ed194a64a9` adds `if (!EG(exception)) EG(exception) = old_exception;` — a **restore**, i.e. `I16/O4` word for word.
▸ trigger: ⚠⚠ **`set_exception_handler` VALIDATES ITS ARGUMENT AT REGISTRATION** — `zend_builtin_functions.c:1038 zend_is_callable(*exception_handler, 0, …)`, E_WARNING and no store on failure — so *"a handler that cannot be called"* **cannot be installed**, and the handler must be broken AFTER registration: `class C { function m($e){} } $o = new C; $arr = array($o,'m'); $r = &$arr[1]; set_exception_handler($arr); $r = 12345; throw new Exception("boom");`. `:1060-1061`'s `zval_copy_ctor` copies the array's `HashTable` but **shares its element zvals by refcount**, so the in-place write through the `is_ref` element retypes the *stored* handler's method name to `IS_LONG`, `zend_call_function` returns FAILURE at `zend_execute_API.c:678-680`, and `:1083` derefs NULL. ✅ **Every link verified at source at `TASK_PHP_021`**; this is the corpus's own reproducer and the original one-line trigger was the `ph21` shape — a state the surviving guard refuses.
▸ benign: the handler runs, the global is re-established, the error path is never taken; `u64` = fold of `(handled, reported)`.
▸ blob: a stream of `(raise, handler-callable?)` events.
⚠ risk: **the row is the save/clear/restore triple, not the null-deref** — a kernel that only omits a NULL check has rebuilt ph60. ⚠ The *reason* the call fails is a second defect (a stored callable sharing an `is_ref` element with a live variable) and it is **not** this row's claim; in a kernel it is one blob bit. ⚠ Re-adjudicated out of `C.1` at `TASK_PHP_019` §2.9 (`ADJUDICATION_002` §5 found it first).

""")

# ---------------------------------------------------------------------------


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] not in ("--check", "--apply"):
        print(__doc__)
        return 2
    apply_ = args[0] == "--apply"
    path = CAT
    if "--to" in args:
        path = args[args.index("--to") + 1]

    src = open(path, encoding="utf-8").read()
    bad = []

    print(f"target: {path}")
    n_before = len(re.findall(r"^\| ph[0-9]+ \|", src, re.M))
    print(f"rows in Part A before: {n_before}")
    print("\n-- replacements --")
    for name, old, new in REPLACE:
        n = src.count(old)
        print(f"  {'ok ' if n == 1 else 'BAD'} {name:22s} anchor occurrences: {n}")
        if n != 1:
            bad.append((name, n))
        else:
            src = src.replace(old, new)

    print("\n-- insertions (before anchor) --")
    for name, anchor, text in INSERT:
        n = src.count(anchor)
        print(f"  {'ok ' if n == 1 else 'BAD'} {name:22s} anchor occurrences: {n}")
        if n != 1:
            bad.append((name, n))
        else:
            src = src.replace(anchor, text + anchor)

    rows = re.findall(r"^\| (ph[0-9]+) \|", src, re.M)
    blocks = re.findall(r"^\*\*(ph[0-9]+) ·", src, re.M)
    print(f"\nrows in Part A after : {len(rows)}   Part B blocks after: {len(blocks)}")
    missing = sorted(set(rows) - set(blocks))
    extra = sorted(set(blocks) - set(rows))
    if missing:
        print(f"  BAD in Part A but not Part B: {missing}")
        bad.append(("partA-not-partB", len(missing)))
    if extra:
        print(f"  BAD in Part B but not Part A: {extra}")
        bad.append(("partB-not-partA", len(extra)))
    if len(rows) != 102:
        print(f"  BAD expected 102 Part A rows, got {len(rows)}")
        bad.append(("row-count", len(rows)))

    if bad:
        print(f"\n⚠ REFUSED — {len(bad)} anchor(s) did not resolve exactly once: {bad}")
        print("Nothing written.")
        return 1

    if apply_:
        open(path, "w", encoding="utf-8").write(src)
        print(f"\napplied to {path}")
    else:
        print("\n--check only, nothing written. All anchors resolve exactly once.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
