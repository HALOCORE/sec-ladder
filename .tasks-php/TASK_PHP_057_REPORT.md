# TASK_PHP_057_REPORT — the review round: F114–F126 + F96's R2/R4/R5

**Role:** research reviewer / analyst, alone. **Written as I went** (`PROTOCOL.md` rule 10).
**Scratch:** `.temp/php57/` only. Generators kept, artefacts (`.so`, `.php` probes) noted below.

---

## §0 BRACKETS — QUOTED FIRST

Run 2026-09-15, at the start of this task, before anything else:

```
$ python3 harness/measure.py --check-stale            → 66 record(s) examined, 0 STALE
$ python3 harness-php/gate.py --tool measure --check-stale → 24 record(s) examined, 0 STALE
```

**`66/0` and `24/0`, as the task file predicts.** (Last quote is at the end of this file.)

---

## §1 — `F120` / `PROTOCOL_PHP.md` §A3a

### 1.1 The measurement, re-run — ✅ **REPRODUCES EXACTLY**, and the four added questions all answer

Binary: the wrapper `…/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext`,
`-v` → `PHP 5.0.0 (cli) (built: Aug  5 2026 09:26:33)`. Probe rebuilt from the
committed generator `.tasks-php/probes/segaddr.c` into `.temp/php57/segaddr.so`.

**A 12-cell matrix — 3 scripts × {LD_PRELOAD, none} × {`-n`, no `-n`}:**

| script | preload `-n` | preload, ini | bare `-n` | bare, ini |
|---|---|---|---|---|
| `mb_get_info()` | **139**, `SIG11 si_code=1 si_addr=(nil)` | **139**, same | **139** | **139** |
| `mb_get_info("internal_encoding")` | 0, `string(10) "ISO-8859-1"` | 0 | 0 | 0 |
| `mb_get_info("all")` | 0, `array(4){…}` | 0 | 0 | 0 |

**Answers to the four questions §1.1 asks:**

1. ⭐ **Does it fault WITHOUT the `LD_PRELOAD`? YES — rc `139` bare.**
   **The shim is NOT load-bearing for the crash**; it only *names* the address.
   The measurement is about the program, not about the shim. ✅ F120 clean here.
2. ⭐⭐ **Is `si_addr=(nil)` really `strcasecmp`'s read? YES, AND IT IS
   SEPARABLE WITHOUT gdb** — see §1.1a. The manager wrote *"there is no gdb …
   an honest 'I cannot separate these two hypotheses' is the answer this
   section most wants."* ⛔ **That premise is wrong: the hypotheses separate in
   about ten minutes with a second `LD_PRELOAD`.**
3. ⚠ **Does `-n` matter? NO.** Identical on all six pairs. The crash does not
   depend on ini state. ✅ F120 unaffected.
4. ⭐ **Does the benign control cover the faulting branch? The one F120 SHOWS
   does not; the one it did not run DOES.** `mb_get_info("all")` returns
   `array(4)` cleanly, exit 0. **It drives the *same* `strcasecmp("all", typ)`
   compare with a non-NULL operand.** ▶ **F120's table under-states its own
   evidence exactly as the task file suspected**, and `"all"` is the *better*
   control because `internal_encoding` only proves the function can return.

### 1.1a ⭐⭐⭐ THE SECOND METHOD — a `strcasecmp` interposer, and it is both LOCALISING and CAUSAL

`strcasecmp` is `U strcasecmp@GLIBC_2.2.5` in the oracle's `.dynsym` (the CLI is
a dynamically-linked PIE), so it is interposable. Generator kept at
`.temp/php57/scc_trace.c`. Two modes.

**(a) TRACE — the last call before the fault:**

```
[scc] strcasecmp("stderr", "stderr")
[scc] strcasecmp("all", NULL)

[segaddr] SIG11 si_code=1 si_addr=(nil)
rc=139
```

**(b) GUARD — refuse the NULL read inside `strcasecmp`, change nothing else:**

```
[scc] strcasecmp("all", NULL)
[scc] GUARD: NULL operand, skipping the real read
[scc] strcasecmp("internal_encoding", NULL)   … http_input … http_output … func_overload
bool(false)
rc=0
```

▶ **Removing that one read removes the fault. This is a causal test, not an
inference.** ⭐ And it shows the shape better than the source reading did: the
function walks **five** `strcasecmp(<lit>, typ)` comparisons with `typ == NULL`
and the **first** is the one that dies — so F120's *"the `"all"` compare"* is
right, and *"first of five"* is new.

⚠⚠ **WHAT THE GUARD IS NOT.** It is **not** the R1h fix. R1h is
`if (!typ || !strcasecmp("all", typ))`, which short-circuits into the *"all"*
branch and returns the array; my guard returns `1` (unequal) and so falls
through to `bool(false)`. **The guard localises the fault; it does not
demonstrate the repair.** That distinction matters for §1.2 and I keep it.

### 1.1b ⛔⛔ **A REFUTATION NOBODY ASKED FOR: THE BUILD IS MIS-NAMED IN FOUR PLACES, AND IT IS THE ONE CAUTION §A3a ITSELF INSISTS ON**

`PROTOCOL_PHP.md` §A3a, `RECAP_PHP.md` F120, `RECAP_PHP.md` F116 and
`.tasks-php/probes/segaddr.c`'s own header all describe the named binary as
the oracle build **`-O3 -march=native -flto`**. §A3a's first caution is
literally *"**Say which build.** … A fault address is a property of a build."*

**Measured — `config.nice` and `Makefile` of the build the wrapper `exec`s:**

| bin/ wrapper | `CFLAGS_CLEAN` from its own `Makefile` | `.buildinfo`? |
|---|---|---|
| ⛔ **`php-5.0.0-mysql-webext`** ← **the one §A3a/F120/F116/`segaddr.c` name** | **`-O0 -std=gnu89 -fcommon …`** — **no `-O3`, no `-flto`, no `-march=native`** | **none** |
| `php-5.0.0-mysql-webext-O3lto` | `-O3 … -flto` | yes |
| `php-5.0.0-mysql-webext-maxlto` | `-O3 -march=native -mtune=native -fomit-frame-pointer … -flto` | yes |

⛔ **The string `-O3 -march=native -flto` describes `-maxlto`, a DIFFERENT
binary with a DIFFERENT name.** The binary actually measured is `-O0`.

▶ **Consequence, and it cuts the friendly way**: an `-O0` build is *closer* to
a museum-default 5.0.0 than the `-O3 -march=native -flto` one, so the
**result** is if anything more transferable than F120 claimed. ⛔ **But the
label is false in four places, one of which is the protocol section that
mandates the label, and one of which is the instrument's own header.** ▶ **Four
one-line corrections are owed** (manager's to make; I did not edit them).

⭐⭐ **AND I THEN RAN THE OTHER TWO BUILDS, because a label error about a
build is worth nothing until you know whether the build matters:**

| binary | `CFLAGS` | trigger | benign `"all"` |
|---|---|---|---|
| `…-mysql-webext` | `-O0` | `SIG11 si_code=1 si_addr=(nil)`, rc **139** | rc 0 |
| `…-mysql-webext-O3lto` | `-O3 … -flto` | **identical** | rc 0 |
| `…-mysql-webext-maxlto` | `-O3 -march=native … -flto` | **identical** | rc 0 |

✅✅ **THE FAULT IS BUILD-INDEPENDENT ACROSS ALL THREE OPTIMISATION TIERS.**
▶ **So F120's RESULT is stronger than F120 claims** — its own third caution
(*"It is a property of a BUILD"*) is, on this row, **over-cautious** — **while
its LABEL is still wrong in four documents.** ⭐ **Conclusion strengthened,
reason corrected: the thing that makes the caution unnecessary here is the
measurement nobody took, not the build that was named.**

---

### 1.2 THE RULE — §A3a's four obligations

#### 1.2.1 ⭐⭐⭐ THE COST OF THE FIFTH OBLIGATION — **MEASURED, AND IT IS 30 SECONDS**

The manager declined to run it ("`_056` was measuring instruction counts"). I ran it.

Staged a relocated oracle home under `.temp/php57/oracle` (the script honours
`APPTEST_ORACLE_HOME`), seeded with the **cached** tarball — **no network**:

```
sha256(.temp/php57/oracle/build-5.0.0/php-5.0.0.tar.gz)
  = 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
```

⭐ **which is the corpus's own citation-base sha256 `5783e0c0…d6919`, byte for
byte** — so the oracle and the catalogue are built from the same tarball, a
thing no document on file states.

**MEASURED COST, `WEBEXT=1 MYSQL_PREFIX=…` (the oracle's own extension set):**

| item | measured |
|---|---|
| **cold build, clean extract → configure → `make -j80` → smoke tests** | **30 s wall** |
| **apply R1h + incremental `make -j80`** (one `.c`, one relink) | **685 ms** |
| disk, whole relocated home incl. the tarball copy | **60 MB** |
| sudo / root | **none** |
| network | **none** (cached tarball; `curl` never fired) |
| human steps | **one command** |

**And it works end to end, first try:**

```
==> 9. smoke tests
    version                    PHP 5.0.0 (cli) (built: Sep 15 2026 07:15:15)
    modules  … mbstring … OK
==> DONE
```

**PRISTINE rebuild reproduces the fault**: `SIG11 si_code=1 si_addr=(nil)`, rc `139`.
**R1h applies**: `Hunk #1 succeeded at 3216 (offset -13 lines)` — ⭐ **F120's
`offset −13` reproduces exactly**, independently.
**POST-IMAGE build**: `if (!typ || !strcasecmp("all", typ))` at `:3219`, and

```
$ <hardened php> -n <mb_get_info() trigger>
array(4) { ["internal_encoding"]=> string(10) "ISO-8859-1" … }   rc=0
```

⭐⭐⭐ **and under the `strcasecmp` interposer the NULL compare is NEVER CALLED
on the hardened build.** ▶ **The fifth obligation is not merely possible, it is
cheaper than one `harness-php/gate.py` run.**

#### 1.2.2 ▶ **ANSWERS TO §1.2's THREE QUESTIONS**

1. **COST:** 30 s + 0.7 s/iteration + 60 MB, above. ⚠ **Three prerequisites make
   it that cheap and they must be named**: the cached tarball, the
   `expat-prefix` symlink farm, and a built `mysql-4.1.15` — all three already
   on the box. **Without the tarball cache the script fetches from
   `museum.php.net`, which is network.** ▶ So the honest form is *"30 s **given
   the cache**"*, and a row's protocol line should say **copy the cached
   tarball, never fetch**. ⭐ **How the patch is applied given the clean
   re-extract:** it is **not** applied through the script at all — run the
   script once, then `patch -p1` the built tree and `make` **incrementally**.
   The script's `rm -rf "$SRC"` destroys an in-tree patch on the *next* run, so
   the post-image tree is a **derived artefact to be rebuilt, not kept** —
   which is exactly `CLAUDE.md` rule 1's arrangement.
2. ⭐⭐⭐ **REQUIRED OR PERMITTED? — I recommend REQUIRED, and the manager's
   stated reason against it is refuted by the number.** The objection was
   *"requiring it makes every row pay for a full PHP compile, and §A3a's whole
   merit is being cheap enough that nobody skips it."* **A full PHP compile is
   30 seconds.** That is below the noise of a single row's build round and far
   below `check.py`. ⛔ **The cheapness argument does not survive measurement.**
   ⚠ **REQUIRED with the same guard the other four carry** — *where a
   reproducer exists **and the pre-image run faulted***. A row whose trigger
   runs clean has nothing for the post-image to be compared against, and
   forcing a build there would be ritual.
3. **WHAT IT BUYS OVER THE APPLIED POST-IMAGE:** the manager's answer
   (*"whether the fix actually stops the fault, rather than whether it looks
   like it should"*) is **correct and I confirm it on this row** — `_056`
   verified the patch's *bytes*; only the build shows `rc 139 → rc 0`. ⭐ **But
   it buys a second thing the manager did not name and it is the better one:
   it prices the fix's DOMAIN CHANGE.** The post-image does not merely stop
   faulting, it **answers** — `mb_get_info()` now returns the full `array(4)`,
   i.e. upstream **widened the benign domain** rather than rejecting the input.
   A byte-level patch read cannot tell "made safe" from "made useful"; the
   build can, in one run.

#### 1.2.3 ⛔⛔ **P1b SCORED: THE MANAGER'S PREDICTED FORM IS WRONG, AND SO IS MY FIRST INSTINCT**

P1b predicted the fifth obligation would land as *"required for rows whose R1h
is one hunk, permitted otherwise"*, and predicted that would be refuted as
tracking convenience. ✅ **P1b is CORRECT that the form is wrong, and correct
about why.** The hunk count is irrelevant: `patch` does not care, and the
30 s is dominated by `configure`+`make`, **neither of which scales with hunks**.
The gate that matters is **did the pre-image fault**, not **how big is the patch**.

#### 1.2.4 ⭐⭐⭐ **ARE §A3a's FOUR THE RIGHT FOUR? — NO. TWO OBLIGATIONS ARE MISSING AND BOTH COST MILLISECONDS**

Neither is the fifth the manager was arguing about. Both were found by running
things §A3a tells a row to run once.

**(i) ⛔⛔ REPEAT THE RUN — because one trigger has THREE different outcomes.**
Two passes of my reproducer sweep disagreed by one row. Isolated it:

```
FLAKY ph75 CRASH-161.php rcs=[-6, -6, -11, -11, 255, 255, 255]
```

**`ph75`'s reproducer returns SIGABRT, SIGSEGV or exit 255 depending on the
run.** §A3a obligation 1 says *"Run the trigger. Record the exit status"* —
**singular** — and obligation 4 says write it into `NOTES.md` as a durable
EVENT. ▶ **On `ph75`, a compliant row records one of three incompatible
verdicts and cannot know it.** ⓘ `ph75` is also one of F115's three
non-binding `fix_commit` rows; the convergence is a coincidence but a useful one.

**(ii) ⛔⛔ SAY WHETHER `si_addr` IS REPRODUCIBLE — because for most rows it is not.**
Obligation 3 says *"Capture `si_addr`"*. Measured, 4 runs each:

| row | reproducer | `si_addr` over 4 runs | verdict |
|---|---|---|---|
| `ph79` | `CRASH-038` | `0x55dd00000000` · `0x559300000000` · `0x55b500000000` · `0x556500000000` | ⛔ **ASLR — a different number every run** |
| `ph89` | `CRASH-034` | `0x65320c9ae77` ×4 | ✅ stable, though large |
| `ph90` | `CRASH-029` | `0x10` ×4 | ✅ stable — **F116's claim confirmed** |
| `ph91` | `CRASH-071` | `0x20` ×4 | ✅ stable — **F118's claim confirmed** |

⛔ **In `_054` agent B's own log, 12 of the 14 `si_addr` values are large/PIE
addresses**, and at least one of those is demonstrably ASLR-varying. §A3a
would have a row write such a number into `NOTES.md` **as an EVENT**, where an
EVENT is supposed to mean *re-derivable*. ⚠ **And `segaddr.c`'s header already
warns *"si_addr=<large/garbage> a WILD pointer … Say so"* — a caution the
protocol section did not inherit.** ⭐ **Fourth un-inherited caution; F122's own
rate claim, holding again.**

#### 1.2.5 ⭐⭐⭐ **DOES §A3a DOWN-RANK ROWS WITH NO CLI REPRODUCER? — THE CONCLUSION IS YES AND THE STATED REASON IS REFUTED**

Derived from two **committed** sources — `patterns-php/CATALOGUE.md` Part A and
the corpus's tracked `index.csv` — by `.temp/php57/p1_reproducers.py`
(generator kept). Part A parses to **102 rows, 42 spatial · 29 type ·
31 temporal**, matching the catalogue's own header, which is the parser's control.

**Existence of a runnable `.php` reproducer:**

| axis | rows | with ≥1 existing corpus `.php` | without |
|---|---|---|---|
| **temporal** | 31 | ⭐ **31** | **0** |
| spatial | 42 | 41 | 1 (`ph95`) |
| type | 29 | 28 | 1 (`ph94`) |

⛔⛔ **P1 IS REFUTED IN ITS STATED FORM. Not "a clear majority of the 31
temporal rows have no single-line CLI reproducer" — *every one of the 31 has
one*,** and it is on disk, and it runs. ⓘ The two misses are the *known*
`V5C-` namespace defect (F51 / item 39): `V5C-015` and `V5C-116` live only in
`merged_members`. `ph03` still resolves via `CRASH-115`; `ph95` does not.

**But now execute them** — one reproducer per row, `-n`, on the oracle CLI.
Counting a **fault** as SIGSEGV (`-11`) or SIGABRT (`-6`):

| axis | rows run | **faults** | clean `0` | fatal `255` | **fault rate** |
|---|---|---|---|---|---|
| **type** | 28 | 22 | 5 | 1 | ⭐ **78.6 %** |
| **spatial** | 41 | 24 | 16 | 1 | **58.5 %** |
| ⛔ **temporal** | 31 | **12** | 16 | 3 | ⛔ **38.7 %** |

⭐⭐⭐ **SO THE DOWN-RANK IS REAL, IT IS MEASURED, AND IT IS STEEP — a temporal
row is HALF as likely as a type row to be able to satisfy §A3a's executed
clause.** ▶ **The manager's CONCLUSION ("the down-rank question is real and I
have not answered it") is UPHELD. The manager's REASON ("most temporal rows
have no CLI reproducer") is REFUTED.** ⭐ **The programme's characteristic
failure mode, this time inside a registered prediction: the conclusion
survives, the reason dies.** The bias does not live in reproducer *existence*
— it lives in the *fault rate*, which is the one place nobody looked.

⚠⚠ **AND THIS IS EXACTLY `CLAUDE.md` rule 6's audited shape**: the gradient
lives in the *bar*, not in any row, so no row-level review could see it.
▶ **§A3a needs a sentence it does not have** — something of the form *the
executed clause is evidence of presence only; its ABSENCE is axis-correlated
at a measured 79 % / 59 % / 39 % and is not a property of the row.* ⛔ **I am
not writing it; the layer and the protocol are manager-only.**

⚠ **What I did NOT establish**: I ran the *first* corpus id per row only, so
every fault rate above is a **lower bound**; and a clean run is F3's
non-evidence, so "16 temporal rows ran clean" is not "16 rows do not fault".

### 1.3 `F116`, which `F120` rests on — ⚠ **UPHELD-NARROWED**

✅ **The count reproduces exactly**: `grep -ac 'rc=139' …corpus_repro.log` →
**14**, against **36** `rc=` lines. The 14 are `ph77` ×2, `ph78` ×2, `ph79` ×3,
`ph80` ×2, `ph81`, `ph87`, `ph89`, `ph90`, `ph91`.

⛔⛔ **AND THE §1.3 QUESTION ANSWERS THE BAD WAY: it rests on scratch.** Not
only is the log gitignored — **so is its generator.** `git check-ignore -v`
returns `.gitignore:3:.temp/` for **both** `corpus_repro.log` **and**
`corpus_repro.sh`. ▶ **`CLAUDE.md` rule 1's test is *keep the generator*, and
here the generator is inside the thing that gets deleted.** **F51/F99's defect,
fourth instance.**

✅ **SECOND METHOD, and it is better than the original**: my
`p1_reproducers.py` re-derives a strictly larger version of the same claim
(100 rows across three axes, not 36 runs) from **two committed sources**, and
`ph90`'s `si_addr = 0x10` reproduces four times out of four. ▶ **F116's
substance stands; its evidence base should be re-cited to something committed.**

---

## §1.5 — `F125`, AND **§7's ITEM 0**, WHICH IS THE BIGGEST THING IN THIS REPORT

### 1.5.1 The two percentages — ✅ **REPRODUCE EXACTLY, INDEPENDENTLY**

From `patterns-php/ph97-optarg-unwritten/controls/libc_compare.json`, computed
by me rather than read off:

```
A1  libc vs in-kernel : -28.6130 %     (27 756 101 vs 38 881 170)
W   libc vs in-kernel : +9.3911 %      (43 032 368 vs 39 338 098)
inside_share  in-kernel 98.8385 %   libc 64.5005 %   Δ -34.3379 pp
```

**Both are computed the way I would compute them** — relative change against
the in-kernel cell as the base. Checksums agree (`9594554053753204562`), both
exit 0. ▶ **`F125`'s MEASUREMENT is UPHELD without qualification.**

### 1.5.2 ⛔⛔ **THE TASK FILE'S OWN PREMISE IS FALSE, AND IT IS WHY ITEM 0 MATTERS**

§1.5 says: *"⛔ DO NOT build anything to answer this. `inside_share` is in every
row's `controls/` already."* **Measured:**

```
$ ls patterns-php/*/controls/inside_share.json   →  ph97 ONLY
```

and a full `grep -arl inside_share patterns-php/ results-php/` finds recorded
**values** in exactly **four** built rows: `ph52`, `ph55`, `ph56`, `ph97`.

### 1.5.3 ⭐⭐⭐ **ITEM 0 ANSWERED: YES — AND THE ROW IS `ph29`, WHICH PUBLISHES IN `A1`**

`inside_share` state of all eleven built rows, against the statistic each publishes:

| row | publishes | `inside_share` | where recorded |
|---|---|---|---|
| `ph03` | **A1** | ⛔ **never measured** | — |
| `ph07` | A3 | ⛔ never measured | — |
| `ph16` | **A1** | ⛔ **never measured** | — |
| ⛔⛔ **`ph29`** | **A1** | ⛔⛔ **C 0.655 vs Rust 0.927 — Δ 27 pp** | ⚠ **a Python DOCSTRING only** |
| `ph64` | B1 | ⛔ never measured | — |
| `ph45` | A1 + W1 | **9.5 %** → row chose **W1** | `NOTES.md` |
| `ph53` | A1 + W1 | 89.5 % → **A1** | ⚠ cited in *`ph52`'s* NOTES, not its own |
| `ph52` | A1 + W1 | **22.24 %** → row chose **W1** | `NOTES.md` §8a |
| `ph55` | A1 + W1 | C **74–83 %**, Rust 96–99 % → cross-lang **W1** | `NOTES.md` §8a |
| `ph56` | A1 + W1 | C 85–98 %, Rust 97–99 % | `controls/statistic.json` |
| `ph97` | A1 + W1 | 87–99 % | `controls/inside_share.json` |

⛔⛔⛔ **FIVE OF ELEVEN BUILT ROWS NEVER MEASURED `inside_share` AT ALL, AND
THREE OF THOSE FIVE PUBLISH AN `A1` HEADLINE** (`ph03`, `ph16`, `ph29`).

⭐⭐⭐ **AND `ph29` IS THE ONE THAT MATTERS.** Its own
`controls/spellings.py:48-49` says, in a docstring:

> *"A1 … is NOT right for this row's C-vs-Rust column (0.927 vs 0.655) and that
> comparison is not made here."*

**`0.655` is 65.5 % — essentially F125's pathological libc cell (64.50 %).** And
`ph29` is precisely the row `RECAP_PHP.md`'s *which statistic* cell names as the
programme's largest open thread: *"On `ph29/large` A says C is +33 % dearer than
naive safe Rust while three other statistics say ~1 % cheaper."*

▶ **So the answer to the question the manager most wanted answered is: YES, and
it is not new — it is the row the programme has been arguing about for thirty
tasks, and the number that explains it has been sitting in a `.py` docstring,
in no JSON, in no `NOTES.md`, in no gate record.** ⚠ **That is `F121`'s class
one level up: the load-bearing figure is *prose about* a measurement.**

### 1.5.4 ⛔⛔ **`F125`'s DISCLAIMER IS FALSE IN BOTH CLAUSES — AND ITS CONCLUSION SURVIVES ANYWAY, ON A DIFFERENT GROUND**

F125 says: *"It does **not** show any published figure is wrong: every php row
measures a kernel that does its own work, and `inside_share` is reported per
cell precisely so a low one is visible."*

- ⛔ ***"every php row measures a kernel that does its own work"*** — **FALSE.**
  `ph45` is at **9.5 %** and `ph52` at **22.24 %**. Both are *far* below the
  64.50 % F125 calls pathological. `ph45` puts **90.5 %** of its program outside
  the kernel symbol.
- ⛔ ***"`inside_share` is reported per cell precisely so a low one is
  visible"*** — **FALSE, and `ph55`'s own NOTES §8b refutes it in terms**:
  *"an `inside_share` of 74–83 % is high, and A1 is still blind here … **Do not
  read a high `inside_share` as a certificate.**"* It is also not *reported* at
  all on five of eleven rows.

✅ **BUT THE OPERATIVE CONCLUSION — *no published figure is shown wrong* —
SURVIVES.** It survives for a reason F125 does not give: **the rows that had a
low `inside_share` MEASURED it and CHANGED COLUMN.** `ph45` at 9.5 % → W1;
`ph52` at 22.24 % → W1; `ph55` → W1 cross-language, A1 same-language only.
▶ **Verdict: `UPHELD-ON-NEW-GROUND`.** The protection is *row discipline*, not
*kernel self-sufficiency*.

### 1.5.5 ⭐⭐ **QUESTION 2 — DOES IT CHANGE `F91`'s AXIS? NO. IT IS THAT CLAIM WITH A NUMBER ON IT — AND NOT THE FIRST NUMBER**

`F125` claims *"the failure mode is REACHABLE AND CHEAP, which nobody had priced."*

⛔ **Two built rows had already demonstrated it, one of them more strongly:**

1. **`ph29` (row 4)** — a **27 pp** C-vs-Rust `inside_share` asymmetry and a
   **34-point** disagreement between A1 and three other statistics on the same
   cell. That is the *same* phenomenon on a *real* row.
2. ⭐⭐⭐ **`ph55` (row 9) is STRONGER THAN `ph97`.** `NOTES.md` §8b: `kernel.c`
   and `kernel_hardened.c` compile to a **byte-identical `kernel` symbol**
   (`asm.py` level `exact`), **one binary SEGVs on `adversarial-nullcall.bin`
   and the other answers**, and **A1 reports the fix at `0.000 %` on every cell
   and every input.** ▶ **A1 reporting a SEGV-to-correct repair as *zero* is a
   worse failure than reporting a sign backwards**, and it was written down two
   rows before `ph97`.

▶ **So `F125` is `UPHELD-NARROWED`.** ⭐ **What is genuinely new, and it is
worth having**: `ph97` is the first **CONTROLLED** demonstration — same
checksum, same computation, a single symbol boundary as the only variable. The
confound `ph29` and `ph55` both carry (the low-share cell is also doing
*different work*) is eliminated. **That is a real contribution and F125 should
be re-stated as "the first controlled measurement", not "the first pricing".**

### 1.5.6 Question 4 — law 12

⚠ F125 is a manager-verified engineer finding from one row and one
substitution. **Law 12 applied and it narrowed**, above. The CONCLUSION
(`A1` can invert a comparison across a symbol boundary) is **UPHELD**; the
REASON offered for why it is safe (`inside_share` makes it visible) is
**REFUTED**; the novelty framing is **NARROWED**.

### 1.5.7 ⛔ WHAT I RECOMMEND, AND IT IS NOT MINE TO WRITE

▶ **`ph03`, `ph16` and `ph29` publish `A1` headlines and have no measured
`inside_share`.** `ph29`'s only figure lives in a docstring and says A1 is the
wrong column for its own C-vs-Rust comparison. ⭐ **Measuring `inside_share` on
those three rows is cheap — `ph97`'s `controls/inside_share.py` is a working
generator and the binaries exist** — and it is the single highest-value follow-up
this round found. ⛔ **I did not run it: `CLAUDE.md` forbids me writing into
`patterns-php/<row>/`, and doing it in scratch would produce exactly the
uncommitted evidence §1.3 just criticised.**

---

## §2 — `F96`'s R2 / R4 / R5, THE ONLY CLAUSES STILL OWED

**Source of truth:** `patterns-php/ph53-iface-tail-uninit/NOTES.md` §8a (the A1
table, `O3/isolated`) and its `O0` paragraph. **Every figure below I re-computed
from the table's raw `Ir/call` values, not read off the percentage column.**

### 2.1 ⭐ **ALL THREE NUMBERS REPRODUCE — P2's FIRST HALF IS CORRECT**

```
base = R1 (c-gcc)          small        large
  R1h                    +0.231 %     -0.720 %
  R2  safe_naive         +6.967 %    +25.370 %
  R4  unsafe            -18.858 %     -2.192 %
base = c-clang             small        large
  R2  safe_naive        +52.716 %    +56.267 %
  R4  unsafe            +15.846 %    +21.912 %
O0 / small, base R1:  R2 +226.295 %   R4 +306.823 %
```

### 2.2 `R2` — ⚠ **UPHELD-NARROWED. The number is exact; the sentence pays 0 of F108's 5**

| F108 owes | F96's sentence *"`+6.97 %` against R1h's `+0.23 %`"* |
|---|---|
| **STATISTIC** | ⛔ absent — it is **A1** |
| **INPUT** | ⛔ absent — **`small.bin`**; `large.bin` reads **`+25.370 %`**, and **R1h's sign FLIPS to `−0.720 %`** |
| **OPT/MODE** | ⛔ absent — **`O3/isolated`**; at `O0` R2 is **`+226.295 %`** |
| **BASE** | ⛔ absent **and actively misleading** — the phrasing *"against R1h's"* reads as *R2 measured against R1h*. **Both are measured against R1 `c-gcc`.** |
| **COMPILER, BOTH COLUMNS** | ⛔ absent, **and this is the one that bites.** Against **`c-clang`**, R2 is **`+52.716 %` / `+56.267 %`** — ⭐ **the headline moves by 7.6× with the choice of C compiler.** |

⭐ **The task file is right that the C-compiler clause applies here** (R2-vs-R1h
is Rust-vs-C, unlike group (d)'s Rust→Rust). **Both columns, stated: gcc
`+6.967 %`, clang `+52.716 %`, `A1`, `small.bin`, `O3/isolated`, base R1.**

### 2.3 `R4` — ⛔⛔ **REFUTED IN PART, AND IT IS THE *"OUTSIDE BOTH ARMS"* CLAIM THAT FALLS**

The number reproduces: **`−18.858 %`** vs R1 `c-gcc`, `small.bin`, `A1`,
`O3/isolated`. F108 score: **1 of 5** (BASE is stated — *"than R1"*; statistic,
input, opt/mode and compiler are not).

⛔⛔ **But `F96`'s meta-claim is the bigger target and it does NOT survive.**
`_040` §5.6 offered two arms: *the fill elides, byte-identical to R1* **or**
*"R4 is DEARER than the C it models"*. F96 says **the truth was outside both**,
and the task file flags this as *"exactly the kind of claim that flatters the
person who wrote it."* ▶ **It does.**

| where you look | is arm 2 (*R4 dearer than the C*) true? |
|---|---|
| vs `c-gcc`, `O3`, `small` | ❌ no — `−18.858 %` (**the only cell F96 quotes**) |
| vs `c-gcc`, `O3`, `large` | ❌ no — `−2.192 %`, but **8.6× smaller than the headline** |
| ⛔ **vs `c-clang`, `O3`, `small`** | ✅ **YES — `+15.846 %`** |
| ⛔ **vs `c-clang`, `O3`, `large`** | ✅ **YES — `+21.912 %`** |
| ⛔ **vs `c-gcc`, `O0`, `small`** | ✅ **YES — `+306.823 %`, dearest of all six rungs** |

⭐⭐⭐ **So arm 2 is TRUE on three of the five cells, and F96 declared it false
by quoting the one cell where it is most false.** ▶ **The truth is not
"outside both arms" — it is "arm 2, on the clang column, which F96 did not
look at."** ⚠ **F108's own rule is what refutes F96's proudest claim**, and
`.memory-php/03-numbers.md` already carries that rule.

⚠ **The `O0` cell is a weaker witness** — `.memory/02-bench-rules.md` bars
performance claims resting on `O0`, and `ph53`'s NOTES says so itself. ▶ **The
clang cells carry the refutation on their own; I do not need `O0` and do not
lean on it.**

### 2.4 `R5` — ⛔ **REFUTED IN PART, AND THE HALVES SPLIT THE OPPOSITE WAY TO THIS PROGRAMME'S USUAL PATTERN**

**The `Seq<Option<u32>>` is real and is where F96 says it is.**
`patterns-php/ph53-iface-tail-uninit/verus.rs:173`:

```rust
pub open spec fn abst(slots: Seq<MaybeUninit<u32>>, wrote: Seq<bool>, n: int) -> Seq<Option<u32>>
```

✅ **THE REASON REPRODUCES.** It is for the **value** postcondition, not memory
safety — **and that is independently checkable rather than taken from the
comment**: initialisedness is carried separately, by
`wrote@[j] ==> slots@[j].mem_contents().is_init()` in the `requires` at `:505`
and the loop invariant at `:538`. **Memory safety does not route through the
`Seq`.** ✅ F96's *"none for memory safety"* is correct.

⛔⛔ **THE CONCLUSION IS THE HALF THAT FAILS.** The prediction was *"no
hand-rolled ghost **state**"*. What `:173` is, is an abstraction **function** —
a pure spec-mode function of exec state, re-derived at each use and pinned by
the invariant `a == abst(slots@, wrote@, …)` at `:535`. **Nothing maintains it
in parallel with the exec code, which is what makes ghost state hand-rolled.**

⭐⭐ **SECOND METHOD — a cross-row control, counted rather than argued:**

| row | `Ghost<` | `Tracked<` | `let ghost` |
|---|---|---|---|
| **`ph53`** | ⭐ **0** | **0** | 7 |
| `ph52` | ⛔ **3** | 0 | 3 |
| `ph45` | 0 | 0 | 5 |
| `ph55` | 0 | 0 | 11 |
| `ph97` | 0 | 0 | 0 |

▶ **`ph53` declares ZERO ghost-state bindings, while `ph52` declares three.**
By the programme's own available comparator, `ph53` is a row with *no*
hand-rolled ghost state. ⭐ **So the prediction is UPHELD and F96's grade of
`HALF-REFUTED` is itself an over-claim — in the refuting direction, which is
unusual and worth naming.**

⚠⚠ **AND WHAT THE ROW ACTUALLY PAYS, WHICH NEITHER THE PREDICTION NOR `F96`
NAMES:** a **real exec array** `wrote: [bool; MAXD]` (`verus.rs:711`,
`unsafe.rs:230`). ⛔ **It is in R4 as well as R5** and absent from R2/R3 — so it
is the `MaybeUninit` design's runtime cost, **paid by the unsafe rung too, and
therefore not a proof burden at all.** ▶ **The interesting cost on this row is
exec state that R4 and R5 share, not ghost state that R5 adds.**

⚠ **F108 does not apply to R5** — it is not a numeric claim. Saying so
explicitly, as `_055` did for group (d).

### 2.5 ▶ **VERDICT TABLE FOR §2**

| clause | CONCLUSION | REASON |
|---|---|---|
| **R2** | ✅ **UPHELD** — R2 is nothing like R1h | ⚠ **UPHELD-NARROWED** — true on gcc/small only; **0 of F108's 5** |
| **R4** | ⚠ **UPHELD-NARROWED** — R4 *is* cheaper than gcc R1 at `O3` | ⛔ **REFUTED** — *"outside both arms"* is false; arm 2 holds on the clang column. **1 of F108's 5** |
| **R5** | ⛔ **REFUTED** — the prediction stands; *"half-refuted"* over-claims | ✅ **UPHELD** — the `Seq` exists, is for the value postcondition, and memory safety is carried elsewhere |

⭐ **Note the shape**: on R5 the **reason survived and the conclusion died** —
the inverse of the programme's standing pattern, and the first instance I can
see on file.

---

## §3 — `F115`, `F118`, `F119`

### 3.2 ⭐⭐⭐ `F118` — **THE GROUND IS NOT WEAK, IT IS BACKWARDS. `P3` IS CORRECT AND UNDER-STATED**

**This is the highest-value single question in §3 and it answers cleanly.**

`F118`'s decision text: *"the temporal axis stays at ONE row … **I am overruling
it on one ground only: F116 landed in the same round, and a measurable C-side
bar lowers the cost of temporal rows specifically.**"* `F116`'s own words:
*"temporal harms are the hardest to argue and **the easiest to execute**."*

▶ **That is a testable claim and it is false.** Two independent routes:

**Route 1 — I executed them** (one reproducer per catalogue row, `-n`, oracle CLI):

| axis | rows run | faulted (SIGSEGV/SIGABRT) | **rate** |
|---|---|---|---|
| type | 28 | 22 | **78.6 %** |
| spatial | 41 | 24 | **58.5 %** |
| ⛔ temporal | 31 | 12 | ⛔ **38.7 %** |

**Route 2 — the corpus's own `crashes_pristine_5_0_0` column**, populated by the
corpus authors years before this programme existed, counted per cited id:

| axis | ids | `True` | **rate** |
|---|---|---|---|
| type | 34 | 24 | **70.6 %** |
| spatial | 44 | 19 | **43.2 %** |
| ⛔ temporal | 89 | 29 | ⛔ **32.6 %** |

⭐⭐⭐ **Same ordering, same gap, two methods that share no code.** And the
`build` column agrees on the mechanism: **95.5 %** of temporal ids are filed
`build=asan` against **79.5 %** of spatial — the temporal axis is the one most
dependent on an instrumented build and least visible to plain execution.

⭐⭐ **THE MECHANISM, and it is not hard**: a use-after-free reads memory that is
**still mapped**, so it returns stale bytes instead of faulting. `SIGSEGV` +
`si_addr` is structurally weakest on exactly the axis `F116` claimed it helps
most. ⓘ Consistent with this, the temporal rows that *do* fault are largely the
**null-deref** subclass (`ph90` at `0x10`, `ph91` at `0x20`), not true UAF.

▶ **VERDICT on `F118`'s ground: `REFUTED`.** Not *"true in principle and weak in
practice"* — **false in practice and inverted**: `F116`/§A3a lowers the cost of
a **type** row by about twice what it lowers a temporal row's, and the row the
manager chose (`ph97`) **is a type row**. ⛔ **The manager owes a corrected
justification, and the decision is not thereby wrong** — `F118`'s *other*,
research-grade reason (*"T6 is five rows of ONE obligation failed five different
ways, and three have the guard PRESENT AND PASSING"*) stands on its own and
needs no `F116`. ▶ **Replace the ground, keep the decision.**

⚠⚠ **`CLAUDE.md` rule 6, explicitly**: nothing above is a reason to down-rank a
temporal row. A low executed-fault rate is `F3` — **not evidence of absence**,
and not a kill. It is a fact about the **instrument**, and I report it as one.

### 3.3 `F119` — ⚠ **UPHELD AND UNDER-STATED, and its stated MECHANISM is about the wrong column**

✅ **Re-derived all three gate records from git, as EVENTS:**

| commit | `envp_stack_bytes` | `md5(marginal_ir_per_call)` |
|---|---|---|
| `4297b1d` | **3686** | `79716501c531` |
| `bee710e` | **3697** | `79716501c531` |
| `b754da4` | **3698** | `79716501c531` |

⭐ **My md5 recipe was chosen independently and lands on the published twelve hex
characters**, so this is a reproduction and not a re-reading. ✅ **And the
block is exactly 96 cells** — `48 isolated + 48 whole` — so *"all 96 family-B
figures bit-identical"* reproduces to the cell.

⛔⛔ **BUT THE MECHANISM DOES NOT FIT ITS OWN EVIDENCE.** F119's load-bearing
reason is *"100 % of the ±7 swing is inside a libc `memset` callee, which
`kernel_exclusive_ir` excludes **structurally**"*. That is a statement about
**A1**. **The evidence is 96 cells of `marginal_ir_per_call`, 48 of which are
`whole`** — the whole-program column, which A1's structural exclusion **cannot
protect**. ▶ **The finding explains the stability of column Y with the immunity
of column X.**

⭐⭐ **AND THE RECORD'S OWN `domain` FIELD SAYS THE COMPARISON IS INADMISSIBLE:**

> *"Comparable **ONLY** against a record with the same `envp_stack_bytes` … When
> the three differ, compare `kernel_exclusive_ir` … instead — structurally
> immune, 0 of 288 triples moved."*

**F119 compares across three different `envp_stack_bytes` values, which is
precisely what that sentence forbids.** ⭐ **The honest reading is the stronger
one and the finding should be re-stated as it**: the ±7 term **did not fire on
this row at all**, on three draws, *including in the column that is supposed to
be vulnerable — so the `domain` guard is more conservative than this row needs.*
⛔ **That is a better result than F119 claims and it does not need the `memset`
mechanism, which I could not verify for `ph53`** — `ph53`'s own `NOTES.md` §8b
says its `memset` of `8·n_decl ≤ 128` bytes is **inlined to `xmm` stores**, i.e.
*inside* `kernel`, not a libc callee at all. **The `p03` measurement the layer
records (`__memset_avx2_unaligned_erms`, `43.0 → 50.0`) is a PAT-side fact about
a different pattern.**

✅ **`.temp/php50/sw_ph53.json` is gitignored** (confirmed) and
`php50_align_sweep.py` is committed — so the gate records are the durable
citation and the sweep is re-derivable, exactly as §3.3 says. **No correction owed there.**

### 3.1 `F115` — ✅ **UPHELD, on an independent re-implementation**

✅ **`fixsurvey.py --offline` reproduces the three verbatim:**

```
49bd45a2c175  BOUND-TO-OTHER:bc9f2fb8dfadc1dba4264695ded28f673c54dc75
abb09693ac4d  BOUND-TO-OTHER:6a6c273893178bb9b59c117e31761fe0193d0c9f
ed4c0245c7ca  BOUND-TO-OTHER:9dfa843a386b65b18353c510f032e322004d0bb7
```

⭐ **SECOND METHOD — a 12-line byte reader of my own, not the survey**: **163**
cached patches, **163** carry a `From ` header, **exactly 3** do not bind to
their filename sha, **the same three, with the same twin shas.**
`fixsurvey.py --selftest` and `--offline` both `rc=0` in the sweep, so B1–B6 and
the derived B7 ratchet do fire. **No network touched.**

⚠ **The mechanism remains UNEXPLAINED and I did not supply one.** ▶ **What the
guard could and could not have seen**: `startswith(b"From ")` tests that the
first five bytes are a header **shape**; the sha lives at bytes 5–45 and was
never read. ⭐ **The transferable part**: any guard in this tree that validates a
*container* rather than its *identity* has the same hole. **F10's class** — *a
guard that is a string search is a guard with a spelling*.

---

## §4 — `F114`, `F117`, `F121`, `F122`, `F124`, `F126`

### 4.1 `F114` — ✅ **UPHELD. The four reports say what it says they say**

Checked header by header, and the structural claim too:

| task | role in its own header | `F96` mentions |
|---|---|---|
| `_042` | *"research **engineer**"* | **0** ✅ — and §3's heading really is *"THE ANSWER ON R3 — **the prediction's mechanism was wrong**, with the disassembly"* |
| `_043` | *"research **reviewer**"* | 10 |
| `_047` | *"research **reviewer** … **Job: falsify.**"* | 8 |
| `_050` | *"research reviewer"* | 22 — ✅ **and `TASK_PHP_050.md`'s title literally reads *"and review `F109` · `F107` · `F96` behind it"*** |
| `_053` | *"research **reviewer**"* | 15 |

⭐ **On the structural question** — *is "the table's one-cell-per-finding shape
forced the mis-filing" true, or fitted after the fact?* ⚠ **Neither, quite.**
The shape is a **permissive** cause, not a forcing one: nothing stopped a
reviewer writing *"F96 clause (c): verdicted"* in a one-cell table. What the
shape did was make the *cheap* move (file under your own number) also the
*legible* one. ▶ **I would call it UPHELD-NARROWED: the shape explains why
nobody noticed, not why it happened.**

### 4.2 `F117` — ✅ **UPHELD.** Run, not read

`python3 .tasks-php/checkers.py` → **`CHECKERS PASS`**, `19 filed, 19 on disk`,
`checkers 15 · of which FLAG-GATED negatives 5`. ✅ **The flag-gating claim is
live and current.** `citecheck.py` exits `1`; **its COUNT is `1`** — a single
`ROT` line, and it is the adjudicated false positive
(`TASK_PHP_048.md`, the three-files-as-one-path line). ✅ *"Read the count,
never the exit code"* confirmed by running it.

### 4.3 `F121` — ✅ **UPHELD, and its repair VERIFIED LIVE**

`checkers.py`'s `N12` arm prints its own verdict:

```
ARM-COUNT CLAIMS -- `why` prose vs what the checker PRINTS
  ok cbaseline_check.py  claims 10  observed 10
  ok contract_audit.py   claims  8  observed  8
  ok task_cost.py        claims 16  observed 16
```

⭐ `task_cost.py` now claims **16** where `F121` caught it claiming 15 against
14 — **the count moved twice more and `N12` tracked it both times.** That is the
repair working, not a passing run. ▶ **On the LAYER-shaped clause** (*law 6
should cover prose about code*): ✅ **I would support it** — this round adds a
**ninth** instance in §4.6 below, and `ph29`'s `inside_share` living only in a
`.py` docstring (§1.5.3) is a **tenth, and the most expensive one yet**. ⛔ **It
is not in the layer and does not go there on my say-so.**

### 4.4 `F122` — ⛔⛔ **REFUTED IN PART: THE REPAIR FIXED ONE HALF OF ITS OWN MECHANISM AND LEFT THE OTHER**

✅ **The finding's diagnosis is right** and `benign()` at `citecheck.py:73,80`
now matches both spellings via `_REPORT(?:_[A-Za-z0-9]+)?\.md$`. ✅ **And it is
confirmed live by this very task**: `TASK_PHP_057.md` cites its report, the
report exists (rule 10), and **rot is 1, not 2.**

⛔⛔ **BUT `citecheck.py:90-91` STILL USES THE OLD SPELLING:**

```python
LIVE = [d for d in DOCS if not d.endswith('_REPORT.md')]
HIST = [d for d in DOCS if     d.endswith('_REPORT.md')]
```

**Demonstrated:**

| document | `benign()` matches? | LIVE/HIST class |
|---|---|---|
| `TASK_PHP_055_REPORT.md` | ✅ | `HIST` |
| ⛔ `TASK_PHP_054_REPORT_E2E3E4.md` | ✅ (fixed) | ⛔ **`LIVE`** |
| ⛔ `TASK_PHP_054_REPORT_E5E6E7E8.md` | ✅ (fixed) | ⛔ **`LIVE`** |
| ⛔ `TASK_PHP_054_REPORT_S4S5S6T2T4T6.md` | ✅ (fixed) | ⛔ **`LIVE`** |

▶ **A split report is still classified LIVE, so any un-benign missing citation
*inside* one counts as rot, while the identical citation inside a plain
`_REPORT.md` counts as `hist` and does not.** ⭐ **The split-name mechanism had
TWO limbs — the name as a CITED path and the name as a CITING document —
and `F122` found and fixed only the first.**

⚠ **LATENT, not live**: rot is `1` today because the three split reports happen
to carry no un-benign missing citation. ⓘ **That is item 114's sentence
verbatim** — *a checker can agree with the truth for a long time because the
state that would separate them has never occurred* — and `F121` quoted it one
finding earlier.

⛔⛔ **AND `N6c` IS THE CHECK THAT SHOULD HAVE CAUGHT IT AND STRUCTURALLY CANNOT.**
`N6a`/`N6b`/`N6c` all call `benign(...)`. **None touches the LIVE/HIST split.**
✅ **§4's question — *did the widening swallow a real rot?* — answers NO**
(`N6c` asserts `not benign('.tasks-php/TASK_PHP_056.md')` and the sweep is
green, so a missing task SPEC is still rot). ⛔ **But the widening was
incomplete in the other direction, and §H's must-fire negatives do not reach the
half that was left.** ▶ **That is §H's own stated target.**

### 4.5 `F124` — ⛔ **`P1`'s CONCLUSION SURVIVES; ITS LABEL DOES NOT. `0.0000` IS REAL AND IT IS NOT WHAT THE SENTENCE SAYS**

From `controls/optional_cost.json`, the two variants are **byte-identical in
every field**:

| | `unwrap_unchecked` (v00) | `unwrap` (v01) |
|---|---|---|
| `kernel_exclusive_ir` small | 11 107 522 | **11 107 522** |
| `kernel_exclusive_ir` large | 12 931 596 | **12 931 596** |
| `inside_share_pct` small | 87.32117864765371 | **87.32117864765371** |
| checksum | `9594554053753204562` | same |

⭐ **`0.0000` IS A MEASUREMENT, NOT AN ARTEFACT OF SHARING — and it is stronger
than F124 says.** The driver makes 20 000 calls (`555.3761 × 20 000 =
11 107 522`, exact). **One extra `cmp`+`jne` per call would add 40 000 `Ir`.**
It added **zero**. ▶ **LLVM did not make the check cheap; it removed the check
entirely.** ✅ §4's *"one function body apart"* is verified: the control's own
docstring names the single edit (`opt_get`'s body, `v00` vs `v01`) and pins the
`vNN` path widths against F101/item 109.

⛔⛔ **THE LABEL IS WRONG, AND THE CONTROL SAYS SO ITSELF.**
`optional_cost.py`'s docstring: *"The A1 difference between them IS the
discriminant **TEST**, and nothing else is in it."*
`F124`/`RECAP` drops the word: *"**The optional's discriminant costs
`+0.0000 Ir/call`**"*. ▶ **The control priced the TEST; the finding reports the
DISCRIMINANT.** ⚠⚠ **That is `PROTOCOL.md` rule 9's exact shape — the manager's
write-up is STRONGER than the engineer's artefact** — and it is the second time
this round (see `F125`'s disclaimer, §1.5.4).

⚠ **And *"free BY CONSTRUCTION"* is two legs wearing one phrase:** the **size**
leg (`Option<&[u8;21]>` is 8 bytes, compile-time assertion) **is** by
construction — null-pointer optimisation is a language guarantee. The
**runtime** leg is by **elision at this call site**, which is an optimiser
result, not a construction. ▶ **A call site where LLVM cannot prove `Some`
would pay, and nothing here bounds that.** **Verdict: `UPHELD-NARROWED`.**

### 4.6 `F126` — ⛔⛔ **CONCLUSION UPHELD; AND A PUBLISHED FIGURE IS *ALREADY STALE AGAIN*, INSIDE ONE ROUND**

**(a) ✅ The split and the `ph07` sensitivity both reproduce**, re-derived from
the tool's own per-row series `[2.83, 5.50, 1.33, 3.33, 2.00, 3.00, 3.00, 2.00,
1.00, 2.00, 1.00]`:
openers = `ph03 ph16 ph29 ph64 ph45 ph53 ph55 ph97` → `17.49 / 8 = 2.186` ✅ **2.19**;
follow-on = `ph07 ph52 ph56` → `9.50 / 3 = 3.167` ✅ **3.17**;
**dropping `ph07`**: `4.00 / 2 = 2.00` against openers' `2.19` ✅ — **openers dearer by 0.19.**
▶ **The conclusion survives dropping the only rebuilt row, weakly, exactly as
`F126` says. `4.00` is unsupported either way.**

**(b) ⛔⛔ THE SEPARABILITY CLAIM IS REFUTED, AND IT NAMES THE WRONG PAIR.**
`F126` and the START HERE box both say the two causes — *floor 40 → 37* and
*`ph97` landing* — *"are separable in the tool's own output."* **Run it.** The
tool prints **one** counterfactual:

```
⚠ At the OLD pinned OPENER_RATE = 4.00 the middle would read ~84 --
  the difference is the refuted premium, shown so the change ... is visible
```

▶ **That separates the OPENER-RATE change. It does NOT separate the floor
change** — there is no 40-row counterfactual anywhere in the output; the tool
prints only `THE 37-ROW FLOOR (26 rows still owed)`. ⛔ **So the claim is true
of a different pair than the one it names.**

**(c) ⛔⛔⛔ AND THE PUBLISHED FIGURE HAS MOVED AGAIN, UNQUOTED.** `F126` and
`RECAP_PHP.md`'s START HERE box publish **`~70 .. ~92, middle ~73`**.
**`python3 .tasks-php/task_cost.py`, run today, prints:**

```
▶ PUBLISH THE RANGE: ~63 .. ~82, middle ~66
```

▶ **Every one of the three numbers in the authoritative handoff is stale, one
round after the finding that moved them, and the finding's own theme is figures
going stale.** ⚠ **Trap §6.4 exactly — a re-derivable reading quoted as a
STATE.** ⭐ **The repair is the EVENT form**: *"`~63 .. ~82, middle ~66`, as
printed by `task_cost.py` on 2026-09-15"*, or better, **stop quoting it and cite
the command**, which is what `F121` did for the README.

---

## §5 ⭐⭐⭐ VERDICT TABLE — **CONCLUSION AND REASON SCORED SEPARATELY, EVERY TIME**

| finding | **CONCLUSION** | **REASON** | second method used |
|---|---|---|---|
| **F114** | ✅ **UPHELD** | ⚠ **UPHELD-NARROWED** — the one-cell shape is *permissive*, not *forcing*; it explains why nobody noticed, not why it happened | role headers + `F96` mention counts + `_050`'s title, read independently |
| **F115** | ✅ **UPHELD** | ✅ **UPHELD** — the guard tested header SHAPE not CONTENT, verified in the source | ⭐ my own 12-line byte reader: 163 patches, 3 non-binding, same twins |
| **F116** | ✅ **UPHELD** | ⛔ **REFUTED** — the evidence is **not** re-derivable: log *and generator* are both gitignored (F51/F99, 4th time) | `p1_reproducers.py` over two committed sources; `ph90 0x10` ×4 |
| **F117** | ✅ **UPHELD** | ✅ **UPHELD** | ran `checkers.py` + read `citecheck`'s COUNT |
| **F118** (ground) | ✅ decision stands on its **other** reason | ⛔⛔ **REFUTED, AND INVERTED** — F116 helps the **type** axis ~2× more than temporal | ⭐⭐ two routes: live execution **and** the corpus's own `crashes_pristine_5_0_0` |
| **F119** | ✅ **UPHELD and UNDER-STATED** — 96 cells, 3 draws, bit-identical | ⛔ **REFUTED** — the `memset`/A1 mechanism is about a **different column** than the evidence, and is a `p03` fact | re-derived 3 gate records from git + read the record's own `domain` field |
| **F120** | ✅ **UPHELD** — measurement reproduces 12/12 | ⚠ **UPHELD-NARROWED** — the build label is wrong in 4 places; the benign control under-states | ⭐⭐⭐ `strcasecmp` interposer, trace **and** causal guard |
| **F121** | ✅ **UPHELD** | ✅ **UPHELD** | ran the repair; `N12` tracked two further count moves |
| **F122** | ⚠ **UPHELD-NARROWED** | ⛔⛔ **REFUTED IN PART** — the repair fixed the CITED-path limb and left the CITING-document limb (`citecheck.py:90-91`) | source read + constructed classification table; `N6c` shown structurally unable to reach it |
| **F123** | ✅✅ **UPHELD, AND UNDER-STATED** — see §5.1 | ✅ **UPHELD** | ⭐⭐⭐ **I ran the build: 30 s** |
| **F124 `P1`** | ⚠ **UPHELD-NARROWED** — `0.0000` is real and stronger than stated (the check was **removed**, not made cheap) | ⛔ **REFUTED** — the control priced the **TEST**; the finding reports the **DISCRIMINANT**; *"by construction"* holds for the size leg only | arithmetic on the record (20 000 calls; a `cmp`+`jne` would cost 40 000 `Ir`) + the control's own docstring |
| **F125** | ⚠ **UPHELD-NARROWED** — first **CONTROLLED** demo, not first pricing | ⛔⛔ **REFUTED** — both clauses of its disclaimer are false | ⭐⭐ `inside_share` census over all 11 built rows; `ph55` §8b; `ph29`'s docstring |
| **F126** | ✅ **UPHELD** — the split and the `ph07` sensitivity both reproduce | ⛔⛔ **REFUTED** — separability names the **wrong pair**, and the published figure is **already stale again** (`~70..~92/~73` → `~63..~82/~66`) | re-derived the two means by hand; ran `task_cost.py` |
| **F96 R2** | ✅ UPHELD | ⚠ UPHELD-NARROWED — **0 of F108's 5** | recomputed from raw `Ir/call`, both C columns |
| **F96 R4** | ⚠ UPHELD-NARROWED | ⛔ **REFUTED** — *"outside both arms"* is false; arm 2 holds on clang. **1 of 5** | the clang column, which F96 never looked at |
| **F96 R5** | ⛔ **REFUTED** — the prediction stands; *"half-refuted"* over-claims | ✅ **UPHELD** | ⭐ cross-row `Ghost<`/`Tracked<` census |

### 5.1 ⭐⭐⭐ **`F123` IS UPHELD AND UNDER-STATED, AND THAT IS THIS ROUND'S SHARPEST RESULT**

`F123` says a check an engineer called *"the cheapest remaining"* became, in four
documents, a thing the protocol treats as impossible. ▶ **All four links verified
by reading the four documents.** ⭐⭐ **And it is worse than `F123` says, because
now the cost is measured: the check is 30 SECONDS.** The engineer's word was not
merely defensible — **it was an under-statement.**

▶ **§1.2a's question 1 — *was the demotion justified at the time?*** ⛔ **NO,
and this is now decidable rather than a matter of taste.** `_052` demoted it to
*"nice to have … Skip it"*. **The thing demoted costs 30 s and 60 MB and needs
one command.** ⚠ **The manager could not have known that without running it —
but that is the point: the demotion was made without the measurement, and
`PROTOCOL.md` rule 14 is *run the premise before you write it into a task
file*.** ▶ **The defect is a manager habit, and steps 3–4 are its consequence.**

▶ **§1.2a's question 3 — should the layer carry the law?** ⭐ **I support it,
and I would strengthen the wording**: not just *an engineer's own uncertainty
may be DEFERRED but not DOWNGRADED*, but — ⭐⭐ ***an engineer's own estimate of
a check's COST is evidence, and demoting a check on cost grounds without
measuring the cost is `PROTOCOL.md` rule 14.*** ⛔ **It is not in the layer and
does not go there on my say-so.**

▶ **§1.2a's question 2 — the count over `WHAT I AM UNSURE OF` sections.**
⛔ **NOT DONE. See §7.**

---

## §6 THE FOUR REGISTERED PREDICTIONS, SCORED BY NAME

**P1 — ⛔ SPLIT: the CONCLUSION is CORRECT, the STATED REASON is REFUTED.**
The manager predicted *"a clear majority of the 31 temporal catalogue rows have
**no single-line CLI reproducer**"* and named the falsifier as *a count showing
most temporal rows DO have one*. ▶ **The falsifier fired: 31 of 31 have one, on
disk, and all 31 run.** ⛔ **P1's reason is refuted outright.** ✅ **But P1's
framing claim — *"§A3a's 'where a reproducer exists' does more work than I gave
it credit for"* — is CORRECT, on a different mechanism**: the work is done not
by *existence* but by the **fault rate**, 78.6 % / 58.5 % / **38.7 %** by axis.
⭐ **You were right that the down-rank is real and wrong about where it lives.**

**P1b — ✅ CORRECT, in both halves, and I am saying so plainly.** You predicted
you would get the FORM wrong, and predicted the form would be *"required where
the R1h is one hunk, permitted otherwise"*. ▶ **That form is wrong for the
reason you guessed**: hunk count tracks nothing — `patch` is instant and the
30 s is `configure`+`make`, neither of which scales with hunks. ⭐ **The right
gate is *did the pre-image fault*.** **P1b scores correct.**

**P2 — ⚠ HALF CORRECT.** ✅ *"The numbers will REPRODUCE"* — **all three do,
exactly; the falsifier did not fire.** ✅ *"Their SENTENCES will owe F108's five
things"* — **they do: R2 pays 0 of 5, R4 pays 1 of 5.** ⛔ **But P2's stated
pattern — *"conclusions survive, reasons and labels do not"* — is REFUTED ON R5,
where the REASON survived and the CONCLUSION died.** ▶ **The pattern is not a
law; this round found a counter-example inside the very finding P2 was about.**

**P3 — ✅ CORRECT, AND UNDER-STATED. You predicted against yourself and you were
right to.** You predicted the row-11 ground would be *"true in principle and
weak in practice"*. ▶ **Measured on two independent routes, it is false in
practice and points the other way.** ⭐ **You owe a corrected justification, as
you said. The decision itself does not need one** — `F118`'s T6-obligation
argument carries it without `F116`.

**P4 — ⛔ REFUTED.** You predicted *"nothing in §4 will be refuted outright,
because all four are measurements over committed artefacts rather than
inferences."* ▶ **`F122` is refuted in part** (`citecheck.py:90-91` still carries
the spelling `F122` says it repaired), **`F124`'s `P1` label is refuted**, and
**`F126`'s separability clause is refuted and its published figure is stale
again.** ⛔ **And the premise is what fails**: `F122`, `F124` and `F126` are not
*measurements over committed artefacts* — each attaches an **inference** (*"the
repair is complete"*, *"the discriminant is free"*, *"the two causes are
separable"*) to a measurement, and **every one of the three inferences is where
the defect was.** ⭐ **So P4's own theory is confirmed while P4 is refuted: the
defect rate does live in the inferences — there were simply more inferences in
§4 than you counted.**

---

## §7 ⭐⭐ WHAT I DID NOT REACH, BY SECTION, WITH ITS COST

1. ⛔ **§1.2a question 2 — the count over landed reports' `WHAT I AM UNSURE OF`
   sections** (*how many other "cheapest remaining check" items are sitting
   demoted?*). **NOT DONE.** ⭐ **This is the single most valuable thing left**
   and the manager explicitly declined to scope it. **Cost: ~1 h** — 57 task
   reports, a section-extractor plus a hand read of each item, because the
   judgement *"is this a cheap check that was demoted?"* is not greppable.
2. ⚠ **`ph03` / `ph16` / `ph29`'s `inside_share`.** I identified the gap
   (§1.5.3) and did **not** close it. **Cost: ~20 min** using `ph97`'s
   `controls/inside_share.py` as the template; ⛔ **but it must be done by an
   engineer, because it writes into `patterns-php/<row>/controls/` and costs
   those rows a re-gate.**
3. ⚠ **§3.1's *"has any other guard in this repo the same shape?"*** I named the
   class (validate the container, never the identity) and did **not** sweep for
   other instances. **Cost: ~30 min** of reading every `startswith`/`endswith`
   guard in `.tasks-php/` and `harness-php/`. ⓘ **§4.4 is one hit found by
   accident**, which suggests the sweep would pay.
4. ⚠ **I ran only the FIRST corpus id per catalogue row.** Several rows cite
   3–5 ids. **Every fault rate in §1.2.5 and §3.2 is a LOWER BOUND.** **Cost:
   ~10 min** to run all 167 cited ids; it would move the rates up but the
   *ordering* is corroborated by the corpus column, which has no such limit.
5. ⛔ **I did not re-run `harness-php/gate.py` on any row**, by design — the
   brackets must not move and they did not.

---

## §8 ⭐ WHAT I AM UNSURE OF — **read this first**

1. ✅ ~~**UNTESTED: whether the `-O0` finding changes any conclusion.**~~
   **CLOSED before filing** — I ran all three builds (§1.1b). **Identical fault
   on every tier**, so the label error does **not** touch F120's result. ⚠ **The
   residual unknown is narrower and I did not test it**: whether a *museum-era
   compiler* (not just a lower `-O`) would agree. Nothing on this box can answer
   that.
2. **I could not tell whether `ph75`'s three-way non-determinism (§1.2.4) is
   ASLR, a race, or allocator state.** I established only *that* it varies. ⛔ **I
   deliberately did not guess a mechanism** — §3.1's own instruction.
3. **The `inside_share` census (§1.5.3) reads `0.655` for `ph29` out of a Python
   docstring.** I did **not** re-measure it. ⚠ **It may itself be stale**, which
   would be the same class of defect I am reporting it as.
4. **My axis fault rates count `SIGABRT` as a fault.** If ASan/glibc aborts
   should be excluded, temporal drops to 10/31 and spatial to 19/41 — **the
   ordering is unchanged**, but the absolute rates move.
5. **On `F96` R5 I am relying on `Ghost<`/`Tracked<` counts as the comparator
   for "hand-rolled ghost state".** ⚠ **That is my definition, not the
   programme's** — `.memory/04-verus.md` may define it otherwise and I did not
   check. **If `let ghost` counts, `ph53`'s 7 is the second-highest of five rows
   and F96's grade is defensible.** ▶ **This is the verdict in this report I am
   least confident of.**
6. **§3.3: I did not measure `ph53`'s callee profile.** I showed the `p03`
   `memset` mechanism is a different pattern's fact and that `ph53`'s `memset`
   is inlined per its own NOTES. **I did not run `outward_by_callee` on `ph53`**,
   which is what would settle it. **Cost: one callgrind pair.**
7. **`F123`'s 30 s is on THIS box with THREE prerequisites cached** (tarball,
   `expat-prefix`, `mysql-4.1.15`). ⚠ **On a fresh clone it is a network fetch
   plus a MySQL build, which is hours.** **My REQUIRED recommendation is
   conditional on the cache surviving, and that should be written into §A3a.**

---

## §9 ▶▶ **ORDER TO RESUME IN — AND THIS IS MY STATED PRIORITY, WHICH BINDS**

⭐ **I reached every section. What follows is what the round OPENED, ranked.**

1. ⭐⭐⭐ **MEASURE `inside_share` ON `ph03`, `ph16`, `ph29`.** Three built rows
   publish `A1` headlines with no measured `inside_share`, and `ph29` — the row
   at the centre of the programme's largest open thread — has `0.655 / 0.927` in
   a docstring saying **A1 is the wrong column for its own C-vs-Rust
   comparison**. ▶ **This is more important than any finding in this round,
   including the one it came out of.** *(engineer task; ~20 min + 3 re-gates)*
2. ⭐⭐⭐ **RULE §A3a's FIFTH OBLIGATION — REQUIRED, with the guard *"where the
   pre-image run faulted"*, and write the 30 s / 60 MB / no-network cost into the
   section** so nobody re-derives it as impossible a third time. **Add the two
   MISSING obligations too: REPEAT THE RUN, and SAY WHETHER `si_addr` IS
   REPRODUCIBLE.** *(manager; the measurement is done, in §1.2)*
3. ⭐⭐ **CORRECT THE BUILD LABEL IN FOUR PLACES** (§A3a, F120, F116,
   `segaddr.c`) — the measured binary is **`-O0`**, not `-O3 -march=native
   -flto`. ✅ **It is a pure label fix**: I ran all three tiers and the fault is
   identical on each (§1.1b), so nothing downstream moves. ⭐ **Record the
   three-tier agreement while you are there** — it is free evidence that F120's
   *"property of a BUILD"* caution does not bind on this row.
4. ⭐⭐ **THE `WHAT I AM UNSURE OF` CENSUS** (§1.2a q2). ⛔ **The manager said he
   does not want to be the one who scopes it. Scope it anyway** — `F123` is one
   instance and the whole finding is that the rate matters, not the instance.
5. ⭐ **FIX `citecheck.py:90-91`** and give it an `N6d` must-fire that tests the
   **LIVE/HIST** split rather than `benign()`. *(§H; ~10 min)*
6. ⭐ **RE-STATE `F119` ON ITS REAL EVIDENCE** (48 `whole` cells stable across 3
   draws, out of the record's own declared `domain`) and **drop the `p03`
   `memset` mechanism**, which is another pattern's fact.
7. **RE-QUOTE `F126`'s RANGE AS AN EVENT** — `~63 .. ~82, middle ~66` as printed
   today — or stop quoting it and cite the command.
8. **RE-LABEL `F124`'s `P1`** from *"the discriminant"* to *"the discriminant
   TEST"*, and split *"free by construction"* into its size leg (by
   construction) and its runtime leg (by elision).

---

## §10 BRACKETS — QUOTED LAST

```
$ python3 harness/measure.py --check-stale             → 66 record(s) examined, 0 STALE
$ python3 harness-php/gate.py --tool measure --check-stale → 24 record(s) examined, 0 STALE
```

✅ **`66/0` and `24/0` — UNMOVED from §0.** Nothing was measured, built into a
row, or re-gated. `git status --porcelain` shows exactly one entry, this report.

## §11 SCRATCH — generators kept, artefacts deleted (`CLAUDE.md` rule 1)

`.temp/php57/` is **32 KB** and holds only generators:
`rebuild_hardened_php.sh` (the §1.2 cost measurement, end to end),
`p1_reproducers.py` (§1.2.5 / §3.2), `flaky.py` (§1.2.4's `ph75`),
`scc_trace.c` (§1.1a's interposer), and the three `t_*.php` triggers.
**Deleted**: the 60 MB oracle build tree, both `.so` shims, `__pycache__`.
⛔ **Nothing outside `.temp/php57/` was created or modified.** No `git add`, no
`git commit`, no network.

