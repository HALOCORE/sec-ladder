# TASK_PHP_007 — adversarial review of `TASK_PHP_006` — REVIEWER REPORT

**Role:** research reviewer. **Launched from a running count of 15.**
**Under review:** the B1 fix (`gate.py::_tu_closure`), the seven landed
findings, and the manager decisions taken on top of them.

> **Bracket, first and last command, both pasted.**
>
> ```
> FIRST  python3 harness/measure.py --check-stale                  66 record(s) examined, 0 STALE
> FIRST  python3 harness-php/gate.py --tool measure --check-stale   2 record(s) examined, 0 STALE
> LAST   python3 harness/measure.py --check-stale                  66 record(s) examined, 0 STALE
> LAST   python3 harness-php/gate.py --tool measure --check-stale   2 record(s) examined, 0 STALE
> ```
>
> **No-touch disclosure, and this time it is a SNAPSHOT and not a `git status`.**
> `TASK_PHP_006` §9 disclosed that it had *not* used `.temp/php5/snapshot.py`.
> I ran it, with its positive control first:
>
> ```
> $ python3 .temp/php5/snapshot.py control
> control: 27 files snapshotted, one byte-appended
>   CHANGED  common/slb.py  2abd87f76712 -> 27618554643a
> CONTROL FIRED
>
> $ python3 .temp/php5/snapshot.py check .temp/php5/pat-snapshot.json   # TASK_PHP_005's baseline
> snapshot check: 2966 recorded, 2966 now, 0 difference(s)
>
> $ python3 .temp/php5/snapshot.py check .temp/php7/pat-snapshot-007-start.json   # my own, taken at the top of this review
> snapshot check: 2966 recorded, 2966 now, 0 difference(s)
>
> $ git status --porcelain
> (empty)
> ```
>
> ✅ **So `harness/`, `common/`, `patterns/`, `results/` and `pilot/` are
> byte-identical both to the state `TASK_PHP_005` recorded and to the state at
> the top of this review — 2 966 paths, zero differences, with the tool proved
> able to fail.** `TASK_PHP_006`'s no-touch claim is upheld by bytes, not by
> `git`.
>
> **Planting disclosure.** One plant, into a **committed** directory:
> `results-php/preflight/` (finding **M3**). Backed up, restored in a
> `finally:`, and verified **by sha256 per file** — see `05-record-growth.log`;
> `git status --porcelain results-php/` is empty afterwards. Two probes rebound
> `gate.PREFLIGHT_DIR` / `gate.REPO` **in process** rather than editing
> anything; the real directory was digested before and after and is unchanged.
> No tracked file was edited at any point.
>
> **Scratch:** `.temp/php7/` — 13 logs, 13 generators, one snapshot. Every
> fixture tree and binary deleted (`CLAUDE.md` constraint 1). `.temp/php5/`
> (29 entries) and `.temp/php6/` (34 entries) untouched; `snapshot.py`,
> `b1_bypass.py` and `provenance.selftest_overlap` were **re-run, not
> modified**.

---

## Summary

| # | rank | finding | evidence |
|---|---|---|---|
| **B1** | **blocker** | `_tu_closure` simulates a **strictly smaller flag space** than `build.py` compiles in. Three constructs make the allocator live in real measured cells and invisible to the audit — and the tool then prints *"dead code … Not treated as a shim user."* | `01-flagmatrix.log`, `02-fulltext.log` |
| **B2** | **blocker** | The text fallback **fails OPEN**, and a row selects it. A `.c` in `c/` that `build.py` never compiles — or no `gcc` at all — downgrades the whole row to `_INCLUDE_RX`, which a spliced or computed `#include` defeats. Built, linked, ran, allocated. | `02-fulltext.log`, `12-residuals.log`, `13-fallback-spelling.log` |
| **M1** | major | `c_subdir_audit` **skips a symlinked directory by name** (`gate.py:345`). Open item 17's mechanism survives the check written to close it. | `03-subdir.log` |
| **M2** | major | The `#if 0` overlap fix has **nine** other spellings, two of them not disclosed anywhere, and `#elif` is actively **mis**handled. `#if 1 … #else <payload> #endif` scores **100 %** on a kernel that divides while citing multiplication. | `04-overlap.log` |
| **M3** | major | The **committed** preflight record grows **without bound** on two already-seen command lines. +2 runs / +2 385 bytes per cycle, measured. Nothing prunes. The engineer's characterisation ("one entry per *distinct* command line") is wrong. | `05-record-growth.log`, `12-residuals.log` |
| **M4** | major | The **deadlock that justifies "absence is a NOTE"** does not exist. `gate.py:972-978` writes the record **on the failure path**. Demonstrated with a real failing stage. | `08-deadlock.log` |
| **M5** | major | `--audit` checks that a preflight record **exists**, never what it **says**. A row whose only recorded run is `verdict: PREFLIGHT FAILED`, `provenance_skipped: true`, `shim_ok: false` reports *"preflight coverage: complete"*. | `07-manager-calls.log` |
| m1 | minor | A dotfile in `c/` is compiled, in **no** digest, and not refused — `glob` never matches a leading dot. | `03-subdir.log` |
| m2 | minor | `RECAP_PHP.md:188` cites `harness/build.py:169-172`. The engineer **refuted that span** and the manager republished it in the commit that landed the refutation. The digest-pinned file says `168-171` and is right. | `11-allcites.log` |
| m3 | minor | `RECAP_PHP.md:180` still cites `emalloc_shim.h:462`; the engineer disclosed the move to `:463`. `:462` is now a bare `*`. | `10-citations.log` |
| m4 | minor | `RECAP_PHP.md:158` cites `emalloc_shim.h:340` for a claim that no longer lives there. | `10-citations.log` |
| m5 | minor | `PROTOCOL_PHP.md:325`'s **✅ enforced** row names *"the `c/` subdirectory ban, the allocator closure"*. B1/B2/M1 make both half-true. | — |

**Eleven clean negatives are listed in §7. Read them before re-running an attack.**

---

# §1 B1 — **BLOCKER.** The detector simulates two states; `build.py` compiles in eight.

## 1.1 The gap

`harness/build.py:127-138`:

```python
def c_flags(opt, mode, panic):
    f = ["-std=c99", "-Wall", "-Wextra"]
    f.append("-O0" if opt in ("O0", "O0d") else "-O3")      # :129
    if mode == "isolated":
        f.append("-DSLB_ISOLATED")                          # :134
    else:
        f.append("-flto")                                   # :136
```

and `build.py:202-203` picks the **compiler from the cell name** (`c-gcc`
vs `c-clang`). So a measured C cell is built in one of
**{gcc, clang} × {-O0, -O3} × {-DSLB_ISOLATED, -flto}**.

`harness-php/gate.py:249-250` runs:

```python
cmd = (["gcc", "-std=c99", "-MM"] + defs + ["-I", common_dir, "-I", cdir] + tus)
```

with `_MM_CONFIGS = ([], ["-DSLB_ISOLATED"])` (`gate.py:201`). **No `-O` flag,
and `gcc` hard-coded.** `gate.py:197` states the premise out loud:

> `#: -O0`/`-O3` do not change the include closure; `-flto` does not either;

⚠ **That sentence is false.** `-O3` defines `__OPTIMIZE__`; `clang` defines
`__clang__` and `__has_include`. Each is a preprocessor state the audit never
enters.

## 1.2 Three rows, measured (`01-flagmatrix.log`)

```
--- ph70-optimize          (#ifdef __OPTIMIZE__ / #include "emalloc_shim.h")
    gate.py REFUSES        : False
    allocator in GATE digest : False
    allocator in MEAS digest : False
    REAL build.py preprocessor states:
       .      gcc   O0 isolated      LIVE   gcc   O3 isolated
       .      gcc   O0 whole         LIVE   gcc   O3 whole
       .      clang O0 isolated      LIVE   clang O3 isolated
       .      clang O0 whole         LIVE   clang O3 whole

--- ph71-clang             (#ifdef __clang__)
    gate.py REFUSES        : False        LIVE in all four clang cells

--- ph72-hasinclude        (#if __has_include("emalloc_shim.h") && defined(__clang__))
    gate.py REFUSES        : False        LIVE in all four clang cells
```

**And it really allocates.** Same row, real `build.py` command line, built and
run:

```
=== does ph70-optimize really allocate at -O3? ===
    BUILD gcc-O0: ok -> .temp/php7/fix/bin-ph70-optimize-gcc-O0
       | alloc tally = 0
    BUILD gcc-O3: ok -> .temp/php7/fix/bin-ph70-optimize-gcc-O3
       | alloc tally = 1000
```

## 1.3 ⚠⚠ The part that makes this worse than the defect it replaced

The audit does not merely stay silent. `gate.py:449-455` emits a **positive
assurance** (`02-fulltext.log`):

```
NOTE:
   ph70-optimize: c/kernel.c #include(s) an emalloc_shim file but no translation
   unit REACHES it under -DSLB_ISOLATED or without it -- dead code, or a header
   nothing includes. Not treated as a shim user.
```

**The tool tells the reader the allocator is dead code, in the run where half
the measured cells allocate through it.** `TASK_PHP_005` F-8 was the *opposite*
error (a false positive on a comment) and was ranked below the blocker; this is
a **false negative wearing a reassurance**, which is strictly worse, and it is
the same shape as `emalloc_shim.c`'s *"CANNOT BE"* comment that
`TASK_PHP_006` §3 correctly identifies as *"how a guard acquires a hole"*.

**Concrete failure scenario.** A php row extracted from `Zend/` writes
`#if __has_include("zend_config.h")` or an `#ifdef __clang__` guard — both
ordinary in extracted C. `gate.py` passes green, the row ships with no
`c/emalloc_shim.h` symlink, its `Ir` numbers are taken under the shim in the
`c-clang-*` / `-O3` cells, the allocator is in **neither** digest, and a later
`emalloc_shim.h` fix leaves those numbers FRESH for ever — which is exactly the
failure `PROTOCOL_PHP.md` §B2 and this whole audit exist to prevent.

## 1.4 Answering §1.2 and §1.3 of the task file directly

- **§1.2 "find a construct where gcc and clang closures differ, or show the
  concern is empty."** ⚠ **Not empty. Two, both measured** —
  `#ifdef __clang__` and `__has_include`. The engineer's §9 disclosure
  (*"the include closure is compiler-independent for the constructs in play …
  not exercised, not guarded"*) understates it: the closures differ for the
  first construct anyone reaches for.
- **§1.3 "is `-DSLB_ISOLATED` × 2 actually the whole space?"** ⚠ **No. It is
  2 of 8.** The unsimulated axes are `-O0/-O3` and `gcc/clang`. `-flto` is the
  one axis that genuinely does not move the closure (`01-flagmatrix.log`:
  `isolated` and `whole` agree in every row and every cell).

**Cheapest repair** (not applied — reviewers do not fix): make `_MM_CONFIGS`
the real product,
`[(cc, O, D) for cc in (GCC, CLANG) for O in ("-O0","-O3") for D in ("-DSLB_ISOLATED","-flto")]`,
and union. That is 8 calls per row instead of 2; §6 shows the budget carries it.

---

# §2 B2 — **BLOCKER.** The fallback fails OPEN, and the row chooses it.

Task §6 call 1: *"If `gcc -MM` failing means 'this row does not use the shim',
the blocker is not closed, it has moved."*

## 2.1 It does not mean that for the ordinary case — and that is the clean negative

`gate.py:428-436`: **any** error from **either** config discards the
preprocessor result for the whole row and substitutes `texty`. For an ordinary
mid-construction row this is safe, and I checked rather than assumed
(`13-fallback-spelling.log`):

```
=== rows that DO NOT PREPROCESS (mid-construction), by include spelling ===
  REFUSED  ph76-plain       _text_mentions=True     <-- #include "emalloc_shim.h", missing header elsewhere
  BYPASS   ph77-spliced     _text_mentions=False
  BYPASS   ph78-computed    _text_mentions=False
```

## 2.2 It fails open for any spelling `_INCLUDE_RX` cannot see

`_INCLUDE_RX` (`gate.py:193-194`) is `re.M`-anchored and requires the name
**on the same line**. A backslash-newline **spliced** include is valid C
(translation phase 2) and defeats it. Built for real:

```
=== is the spliced include really valid C? build it for real ===
  build rc=0
  ran -> 'alloc tally = 7'
  _INCLUDE_RX sees it: False
```

## 2.3 And the row picks the weak detector, without breaking its own build

`_tu_closure` globs `c/*.c` (`gate.py:242`); `build_c` compiles **exactly
three** TUs (`build.py:162-165`). ⚠ **The detector's TU set is a superset of
the build's**, so a `c/aux.c` that `build.py` never compiles poisons detection
for the entire row. `02-fulltext.log`:

```
=== _tu_closure's OWN view of ph73-fallback ===
  by_tu keys : []
  errors     : 2
      | gcc -MM (no -D) exited 1: .../ph73-fallback/c/aux.c:2:4: error: #error "aux.c must be #included from kernel.c"
      | gcc -MM -DSLB_ISOLATED exited 1: (same)

=== ph73-fallback: real build.py command line, built and RUN ===
  O0/isolated: built ok, ran -> 'alloc tally = 1000'
  O3/whole:    built ok, ran -> 'alloc tally = 1000'

=== and gate.py's verdict on that same row, again ===
  problems for ph73-fallback: 0
```

**A row that allocates 1 000 blocks in every real cell, in neither digest,
preflight green.** `#ifndef X / #error / #endif` on an include-only fragment is
a standard C idiom, not a contrivance.

## 2.4 And with no `gcc` at all it is worse (`12-residuals.log`)

```
  _tu_closure -> by_tu={}  errors=["cannot run gcc -MM: [Errno 2] ... 'gcc'"]
  shim_link_audit -> 0 problem(s), 1 note(s)
     _text_mentions(kernel.c) = False
  => with no gcc: NO problem raised for a row that allocates. FAIL OPEN
```

⚠ `gate.py:253-255` `return`s on `OSError` rather than `continue`ing, so only
one of the two configs is even attempted.

**Answer to §6 call 1: the detector does NOT fail closed. It falls back to a
detector that has a spelling, and a row can force that fallback while building
all 28 cells.** F-1 is not closed; it has moved and become quieter.

---

# §3 M1 — the `c/<subdir>` refusal is not sound (§2 of the task)

`gate.py:345`:

```python
if not os.path.isdir(p) or os.path.islink(p):
    continue
```

`os.path.isdir` follows a symlink, `os.path.islink` is then true, and the entry
is **skipped by name**. `03-subdir.log`:

```
--- ph80-subdir            (c/zend/payload.h)                 <-- the control
    c_subdir_audit REFUSES  : True
    payload really COMPILED : True     payload in GATE/MEAS digest : False/False

--- ph81-dirlink           (c/zend -> ../../extracted-zend)
    c_subdir_audit REFUSES  : False
    payload really COMPILED : True     payload in GATE/MEAS digest : False/False
    ⚠⚠ COMPILED, IN NO DIGEST, AND NOT REFUSED  <-- open item 17 reopened

--- ph82-dotfile           (c/.payload.h)                     <-- finding m1
    c_subdir_audit REFUSES  : False
    payload really COMPILED : True     payload in GATE/MEAS digest : False/False
    ⚠⚠ COMPILED, IN NO DIGEST, AND NOT REFUSED
```

**Failure scenario.** A php row is built by symlinking the extracted subtree —
`ln -s ../../../extract/Zend patterns-php/ph07-x/c/zend` — which is the natural
thing to do when the corpus is a tarball. Every header behind it compiles, none
is in either digest, `check.py --no-build` does not mark a binary stale when one
changes, and the preflight prints `ok no patterns-php/*/c/ subdirectory`.

⚠ **It compounds with B2**: `shim_link_audit`'s `texty` uses `os.walk`, which
does not follow symlinks either, so a shim `#include` behind the link is
invisible to the fallback as well (`12-residuals.log` §3). The preprocessor
still catches *that* one — but only while it runs.

**Repair is one clause**: drop `or os.path.islink(p)` and report a symlinked
directory with its own message.

## m1 — the dotfile

`glob.glob(cdir + "/*")` never matches a leading dot, so `c/.payload.h` is in
neither digest and `c_subdir_audit` (which uses `os.listdir`) sees it but only
looks at directories. Lower likelihood than M1; same mechanism; one `if` to fix.

## §2 second half — re-deriving the escape hatch, and my verdict on the manager's ban

⚠ **The engineer's measurement stands, reproduced independently**
(`03-subdir.log`, row `ph83-flatlink`):

```
--- ph83-flatlink          (c/zend/payload.h + c/zend__payload.h -> zend/payload.h)
    payload in GATE digest  : True
    payload in MEAS digest  : True
    gate digest c/ keys     : ['c/kernel.c', 'c/main.c', 'c/zend__payload.h']
```

⚠⚠ **But the engineer's stated REASON for declining it is refuted.** It was
*"nothing would force the NEXT file added to that subdirectory to get a link,
so the guarantee would hold exactly as long as somebody remembered it."*
That is answerable in twelve lines that run on the same preflight
(`07-manager-calls.log`):

```
(a) MUST NOT FIRE -- every subdir file has a flat link
    0 problem(s)   OK
(b) MUST FIRE -- the engineer's exact scenario: the NEXT file is added and nobody remembers
    1 problem(s)   CONTROL FIRED
      | c/zend/zend_operators.h is in a subdirectory and has NO flat symlink beside it --
        it would be in NO digest. Add: ln -s zend/zend_operators.h c/zend__zend_operators.h
(c) MUST FIRE -- a link that points at the wrong file
    1 problem(s)   CONTROL FIRED
```

*(In (c) the wrong-target link is caught by the same missing-realpath rule, not
by a separate one; I say so rather than claim two mechanisms.)*

**Answer to §6 call 2: the ban is BOTH insufficient and over-strict.** It is
insufficient because M1/m1 walk around it. It is over-strict because the
cheaper design **is** safe with a check that is smaller than the refusal message
already shipped. ⚠ **My recommendation: fix M1 and m1 first — an unsound ban is
worse than an over-strict one — and treat the hatch as available, priced, and
gated on that 12-line audit rather than as forbidden for ever.** `PLAN_PHP.md`
and `PROTOCOL_PHP.md` §B3 should not be written as if the layout were
impossible.

---

# §4 M2 — F-4's floor: nine more spellings, and `#elif` is mishandled

`provenance.py:270` `_LITERAL_FALSE = re.compile(r"^\s*0\s*$")` is the entire
predicate. `04-overlap.log`, floor 50 %, kernel = `_SELFTEST_WRONG` (divides,
cites multiplication), each candidate also proved dead by a real `gcc -E`:

```
spelling                                        overlap   dead in   verdict
                                                          the BUILD
#if 0                 (the fix's own case)         11%       True   refused
#if 0L                                            100%       True   BYPASS
#if (0)                                           100%       True   BYPASS
#if 00                                            100%       True   BYPASS
#if !1                                            100%       True   BYPASS
#ifdef NEVER_DEFINED                              100%       True   BYPASS
#ifndef __STDC__                                  100%       True   BYPASS
#if 1 ... #else <payload> #endif                  100%       True   BYPASS
#if 0 ... #elif 0 <payload> #endif                100%       True   BYPASS
#if defined(NOPE) && defined(NOPE2)               100%       True   BYPASS
// backslash-continued line comment                11%       True   refused
```

Three things are worth separating:

1. **Disclosed.** `provenance.py:262-268` names `#ifdef NEVER_DEFINED` and
   `#if SOMETHING_FALSE`. `#if 0L`, `#if (0)`, `#if 00`, `#if !1`,
   `#ifndef __STDC__` and `#if defined(NOPE)…` are that class. Honest, but it
   means F-4's blocker-shaped major is **one keystroke** from reopening with
   nothing to detect it.
2. ⚠ **NOT disclosed anywhere:** `#if 1 … #else <payload> #endif`. This is the
   exact mirror of the self-test's celebrated case **E**, and it is the natural
   thing to write. Nothing in the suite covers it.
3. ⚠⚠ **`#elif` is a BUG, not a limitation.** `provenance.py:294-296`:

   ```python
   elif kw in ("else", "elif"):
       if skip_at == depth:
           skip_at = None
   ```

   A `#elif 0` arm is **dead**, and this code turns skipping **off** for it.
   The function believes it handles `elif`; it handles it backwards.

**Failure scenario.** A `verbatim` row whose kernel does not implement the cited
mechanism pastes the citation under `#if 1 … #else` (or leaves a `#elif 0`
debug arm behind), scores 100 %, and `provenance.py` prints
`kernel overlap 100% … floor 50% for tier=verbatim` — the strongest evidence
the tool can emit, for the row it exists to refuse.

⚠ **The deeper point, and it is the engineer's own.** `TASK_PHP_006` §1.3
argues correctly that the right answer to a spelling-based detector is *"the
preprocessor closes 1, 2 and F-8 together and **has no spelling**"*. F-4's fix
is spelling-based and has nine. The two halves of the same task took opposite
positions on the same question.

✅ **Clean negative held**: case A, the realistic `verbatim` lift, still scores
**68 %** and passes; the shipped 7-case self-test is **0 FAILED** after all of
the above.

---

# §5 M3, M4, M5 — the preflight record and its absence detector

## M3 — the committed record grows without bound (major)

`gate.py:898-901` collapses a run only when it equals the **immediately
preceding** one. Two command lines used alternately therefore never collapse.
Both commands below are ones the project runs constantly — the second is the
bracket **every task file mandates twice**. `05-record-growth.log`:

```
start: runs=3  bytes=3511

=== (i) REPEAT the same command 4x -- should collapse ===
  after `gate.py --preflight` #1..#4: runs=4 bytes=4655   (unchanged)     <-- the design works

=== (ii) ALTERNATE two routine commands 6x ===
  A = `gate.py --preflight`
  B = `gate.py --tool measure --check-stale`
  cycle 1:  after A runs=4  bytes=4655    after B runs=5  bytes=5896
  cycle 2:  after A runs=6  bytes=7040    after B runs=7  bytes=8281
  ...
  cycle 6:  after A runs=14 bytes=16580   after B runs=15 bytes=17821

end: runs=15  bytes=17821   (+12 runs, +14310 bytes for 6 cycles of 2 ALREADY-SEEN command lines)
per-cycle growth: 2.0 runs, 2385 bytes

=== does anything prune? ===
  gate.py contains 'prune'/'MAX_RUNS'/'truncat'/'rotate': False / False / False / False
```

⚠ **This refutes the engineer's own disclosure.** `TASK_PHP_006` §9 says the
file *"will accumulate one entry per distinct no-row command line … stable
across repeats and small."* It is **not** bounded by the number of distinct
command lines: **two** command lines produce unbounded growth. The file
quintupled in six cycles of ordinary use.

⚠ **And it scales with the catalogue.** `12-residuals.log`:

```
  today (1 php row):  1131 bytes/entry
   10 php rows      :  2068 bytes/entry
   40 php rows      :  5188 bytes/entry
   80 php rows      :  9348 bytes/entry     (why_sizes alone; allocator_symlink_notes
                                             adds one line per shim-using row on top --
                                             06-scaling.log measured 80 notes at 80 rows)
```

At catalogue scale one alternation cycle adds **~19 kB to a committed file**,
for ever, with no pruning. **Failure scenario:** `results-php/preflight/` is the
noisiest thing in the php diff within a dozen tasks, and the reviewable signal
it was committed to carry — *was `--no-provenance` used?* — is buried in
hundreds of near-identical entries.

**Cheapest repair:** collapse against **any** previous entry with the same
`gate_argv`, not only the previous one; or cap `runs` and keep the first, the
last, and every entry with `provenance_skipped` / a non-empty `problems`.

## M4 — the deadlock that justified "absence is a NOTE" does not exist (major)

`TASK_PHP_006` §2c:

> *"if a missing record failed the preflight, the repair
> (`gate.py --preflight <row>`) is itself a preflight and would fail on every
> other uncovered row **before writing anything**."*

The load-bearing words are *before writing anything*. `gate.py:972-978`:

```python
if problems:
    record["verdict"] = "PREFLIGHT FAILED"
    write_preflight_record(record)          # <-- writes
    ...
    return 2
```

Tested by making a **real** preflight stage fail in process
(`08-deadlock.log`):

```
  FAIL patterns-php/MANIFEST.sha256
PREFLIGHT FAILED -- the tool was NOT run:
  preflight coverage: 3 php record(s) have NO preflight record -- SIMULATED HARD FAILURE

>>> rc = 2   (2 = PREFLIGHT FAILED)
>>> written into the preflight dir ON THE FAILURE PATH: ['ph00.preflight.json', 'ph00.when.json']
      ph00.preflight.json: runs=1  verdict='PREFLIGHT FAILED' problems=1
>>> real results-php/preflight/ byte-identical: True
```

**N uncovered rows are repaired by the same N `--preflight <row>` invocations
the NOTE design needs anyway.** The engineer said *"I judged a preflight failure
to be a deadlock and I may be wrong"*; **it is wrong**, and the manager accepted
it without a measurement (§6 call 3, and the manager's own note that *"two
judgements in a row with no adversarial pass"* is the configuration this project
keeps finding defects in — it was, again).

⚠ **I am not recommending the hard failure.** *Loud beats unrunnable* may still
be the right design for other reasons. **What must not survive is the stated
reason**, because it is in `gate.py:684-688`'s docstring and in
`PROTOCOL_PHP.md`, and the next agent will believe it.

*(Incidental, and consistent with the design: `gate.py:806` binds the audit's
first return value to `_cov_bad` and discards it, so the stage could not fail
the run even if `preflight_coverage_audit` returned problems. The engineer's
"the change is one line" is really two — that line plus the return value.)*

## M5 — `--audit` is content-blind (major)

`gate.py:701-703` only asks whether a file **exists**:

```python
hits = glob.glob(os.path.join(PREFLIGHT_DIR, f"{rid}*.preflight.json"))
if not hits:
    uncovered.append(...)
```

`07-manager-calls.log`:

```
  ph99's ONLY recorded run: verdict='PREFLIGHT FAILED', provenance_skipped=True, shim_ok=False
  preflight_coverage_audit -> 0 problem(s), 0 note(s)
  verdict printed by `--audit`: complete
  => a row whose every recorded preflight FAILED counts as covered.
```

`PROTOCOL_PHP.md:326` advertises the record as carrying *"whether
`--no-provenance` was used"*, and `:327` advertises `--audit` as the detector —
but the detector **never opens the file**. **Failure scenario:** a row is gated
on a box without the tarball, every recorded run has `provenance_skipped: true`,
`--audit` reports *"preflight coverage: complete"*, and the one question the
committed record exists to answer is answered wrongly by the only tool that asks
it. Repair: read `runs[]` and report a row whose runs are all `PREFLIGHT
FAILED`, all `provenance_skipped`, or `shim_ok: false`.

---

# §6 §1.5 — the scaling claim: CLEAN NEGATIVE, with a correction

`06-scaling.log`, `ph00-smoke`'s `c/` cloned N times, half of them real shim
users with the sanctioned symlink:

```
 rows  gcc calls    wall s    ms/row  ms/gcc call
    1          2      0.15     145.3         72.6
    9         18      1.21     134.8         67.4
   20         40      2.64     131.9         66.0
   40         80      5.40     134.9         67.5
   80        160     10.81     135.1         67.6
```

- ✅ **Linear, and per-ROW not per-TU** — 2 `gcc` calls per row regardless of
  how many TUs, because `gate.py:248-250` puts every TU in one argv.
- ✅ **The affordability conclusion survives.** 80 rows = **10.8 s** per
  preflight against a ~24-minute gate.
- ⚠ **Correction to the figure**: **~135 ms/row, not ~115.** `TASK_PHP_006`
  measured rows that do **not** include the 668-line shim header; a realistic
  row costs ~17 % more. Its extrapolation *"fifty rows ≈ 5.8 s"* is really
  ≈ 6.8 s. Immaterial to the decision, but the number is quoted in
  `gate.py:228-230`'s docstring and will be believed.
- ⚠ **It runs on `--check-stale` too** (`gate.py:967` → `preflight()`), i.e. on
  the bracket command, twice per task. Still fine at 10.8 s; worth knowing
  before the catalogue is 200 rows.

**The B1 repair does not break this budget**: 8 configs instead of 2 is ~540 ms
per row, ~43 s at 80 rows. That is the price of the blocker being closed, and it
is still under 3 % of a gate.

---

# §7 Clean negatives — attacks that did NOT land

Re-running these is wasted time.

1. ✅ **The frozen PAT tree is untouched, by BYTES.** `snapshot.py` against
   `TASK_PHP_005`'s baseline **and** my own: 2 966 paths, **0 differences**,
   twice, with the positive control firing first. `TASK_PHP_006`'s no-touch
   claim is upheld on stronger evidence than it offered.
2. ✅ **`-m32` is not a hole today, and the engineer's judgement was right.**
   `grep -- '-m32'` over `harness/*.py common/*.py harness-php/*.py
   common-php/*.py` is **empty** — `build.py` has no path that can emit it —
   and the box cannot build 32-bit at all:
   `gcc -m32 → /usr/bin/ld: cannot find Scrt1.o` (no multilib). The only
   realistic route is a hand-run probe or a future standalone consumer of
   `emalloc_shim.c`. ⚠ The `#error` guard is still worth batching with the next
   shim edit — but *"nothing detects it"* is currently a statement about a state
   this box cannot reach.
3. ✅ **F-4's clean negative held.** Case A, the realistic `verbatim` lift,
   still scores **68 %** and passes; the shipped self-test is 7 cases,
   **0 FAILED**, after every attack in §4.
4. ✅ **A backslash-continued `//` comment does NOT bypass the overlap.**
   It is a real C construct that hides the payload from the compiler, but every
   payload line must then carry a trailing ` \`, which changes the normalised
   line and breaks the set match — 11 %, refused. Do not re-try it.
5. ✅ **An ordinary mid-construction row is still caught.** `#include
   "emalloc_shim.h"` plus a missing header elsewhere → `-MM` fails → the text
   fallback fires → **REFUSED**. B2 needs the compound (failure **and** a
   spelling the regex misses); saying otherwise would overstate it.
6. ✅ **Consecutive identical runs really do collapse.** Four identical
   `--preflight` runs left the committed file **byte-identical**
   (`runs=4 bytes=4655` all four times). F-2(a)'s design works; M3 is about
   alternation only.
7. ✅ **The flat-symlink hatch is real.** Independently re-derived: the real
   bytes land in **both** digests under `c/zend__payload.h`.
8. ✅ **`-flto` does not move the include closure.** `isolated` and `whole`
   agree in every row × cell in `01-flagmatrix.log`. Only `-O` and the compiler
   do.
9. ✅ **Eleven load-bearing `harness/*.py:NNN` citations all resolve**, including
   `check.py:10314`, `measure.py:226`, `check.py:10187-10189`, `check.py:1866`,
   `check.py:1872-1873`, `build.py:162-165` and `build.py:168-171`. The
   citation-rot class is clean apart from m2/m3/m4, all in `RECAP_PHP.md`.
10. ✅ **All three of `TASK_PHP_006`'s refutations reproduce exactly**, measured
    with an independent parser rather than by importing `why_sizes`
    (`09-refutations.log`):

    ```
    p16-tlv-walk  row-specific 3140  (prefix 109, tail 3031)   total 4995
    p17-http-range row-specific  500  (prefix 154, tail  346)
    p49-interned-pool row-specific 2533 (prefix 2533, tail 0)
    PAT n=33  min 197  median 989  max 3140
    rows with a REAL tail (>1 word): [('p16-tlv-walk', 3031), ('p17-http-range', 346)]
    rows whose `why` contains \n: 0 of 34   []
    largest TOTAL why: 4995 (p16-tlv-walk);  median 2839;  smallest 2052
    ```

    So: the reviewer's F-5 table **was** measured on the wrong span; the
    structural rule **is** unsatisfiable; the manager's *"~7 000-word"* figure
    **is** invented. ⚠ **The engineer was right on all three and I could not
    break any of them.**
11. ✅ **The preprocessor still catches a shim include behind a symlinked
    subdirectory** (M1's compound), *while it runs*. M1 is a digest hole, not by
    itself an allocator hole.

---

# §8 Minors, with file:line

- **m1** `harness-php/gate.py:343-345` — `c_subdir_audit` iterates
  `os.listdir` but only inspects directories; and both digests come from
  `glob("c/*")`, which never matches a dotfile. `c/.payload.h` is compiled and
  in no digest. Same one-`if` class as M1.
- **m2** `RECAP_PHP.md:188` — cites `harness/build.py:169-172` for the
  `-fuse-ld=lld` insert. `TASK_PHP_006` §3 **explicitly refuted that span**
  (*"`build.py` inserts it at 168-171, not 169-172"*) and the digest-pinned
  `common-php/emalloc_shim.h:492` carries the corrected `168-171`. The manager
  landed the report and republished the refuted span in the same commit
  (`7a16ddc`). ⚠ **The sentence containing the stale citation is the one
  invoking `PROTOCOL.md` rule 13.** Two files in the tree now disagree about the
  same fact and the pinned one is right. `11-allcites.log`:
  ```
  RECAP_PHP.md:188  ->  harness/build.py:169-172
        lld = os.path.expanduser(...) / if os.path.exists(lld): / cmd.insert(1, "-fuse-ld=lld") / return run(cmd, dry)
  common-php/emalloc_shim.h:492  ->  harness/build.py:168-171
        if mode == "whole" and "clang" in os.path.basename(cc): / lld = ... / if ... / cmd.insert(1, "-fuse-ld=lld")
  ```
- **m3** `RECAP_PHP.md:180` — cites `common-php/emalloc_shim.h:462`; the
  engineer disclosed the move to `:463`. `:462` is now a bare `*`. One of the
  two disclosed sites was corrected; this one was not.
- **m4** `RECAP_PHP.md:158` — cites `emalloc_shim.h:340` for the
  `__builtin_mul_overflow` *"same predicate"* claim. That text is gone from
  `:340` (which now reads `*   :151  the cache-hit arm`); the surviving
  discussion is at `:454` and `:471`. A historical citation is fine; a
  historical citation that lands on unrelated code is not.
- **m5** `.tasks-php/PROTOCOL_PHP.md:325` — the **✅ enforced** row lists
  *"the `c/` subdirectory ban, the allocator closure"*. Given B1, B2 and M1
  neither is enforced in the sense a reader will take. The same table's
  ❌ rows are careful and correct; this row now overstates by comparison.
  `gate.py:65-75` has the same problem.
- **m6** (already disclosed by the engineer, confirmed) `gate.py:803-804` —
  the PAT band `median 989, p90 1817, max 3140` is a hard-coded constant inside
  a printed string, and `why_sizes` reads `patterns-php/` only. It is the rot
  class the project keeps finding; the disclosure is accurate.

---

# §9 What I refute, and what I uphold

**Launched from 15. Reconciliation is the manager's job, not mine.**

**Refuted — against the ENGINEER (3):**

1. ⚠⚠ *"`gcc -MM` … has no spelling"* / *"both `-D` states are swept and
   unioned"* (`TASK_PHP_006` §1.1, `gate.py:197`). **The swept space is 2 of 8.**
   `__OPTIMIZE__`, `__clang__` and `__has_include` each give a live allocator in
   a real measured cell with the audit silent and a note asserting dead code.
   The engineer's own §9 disclosure of the `gcc` hard-coding is present but
   understated as *"could in principle differ"*; it differs on the first
   construct anyone writes.
2. ⚠ *"The `_norow.preflight.json` file will accumulate one entry per distinct
   no-row command line … stable across repeats and small"* (§9). **Measured
   false.** Two command lines, alternated, grow it without bound: +2 runs and
   +2 385 bytes per cycle, ×5 in six cycles, ~19 kB/cycle at 80 rows, nothing
   prunes.
3. ⚠ *"I judged a preflight failure to be a deadlock (§2c) and I may be
   wrong."* **Wrong, and demonstrated**: `gate.py:972-978` writes the record on
   the failure path, so *"would fail on every other uncovered row before writing
   anything"* is false. The conclusion (*loud beats unrunnable*) may still be
   right; the **mechanism** is not, and it is now written into `gate.py`'s
   docstring and `PROTOCOL_PHP.md`.

**Refuted — against the MANAGER (1):**

4. ⚠ **§6 call 2 — the `c/<subdir>` ban.** It is *both* insufficient (a
   symlinked directory and a dotfile walk around it, M1/m1) and over-strict
   (the flat-symlink hatch is safe under a 12-line audit that I built and
   exercised in both directions). **The manager asked to be told before the
   catalogue is written around it. This is that.**

**Corrected, not refuted (1):** the `gcc -MM` price is **~135 ms/row**, not
~115 — measured on realistic rows that include the shim. The affordability
*conclusion* is unchanged and is upheld.

**Upheld against my own attacks — the engineer was right and I could not break
it (5):** all three of its refutations (F-5's wrong span; the unsatisfiable
paragraph rule; the invented ~7 000); the decision not to add the `-m32`
`#error` guard; and the no-touch claim, which I verified by bytes rather than
by `git`.

---

# §10 What I did NOT do, and what I am unsure about

- **I did not fix anything.** No tracked file was edited. Every repair above is
  described, not applied.
- **I did not run a full `harness-php/gate.py ph00`** (~5-24 min). Nothing I
  found moves a gate record, and the closing bracket shows both records FRESH;
  but I did not re-certify `ph00` end to end.
- **I did not build the 8-config `_MM_CONFIGS` repair and measure its false-
  positive rate on a real corpus.** I measured its *cost* (§6) and not its
  behaviour on rows that legitimately differ between compilers. A row whose
  clang cells use the shim and whose gcc cells do not is a **real** state, and
  the union would demand the symlink for both — which I believe is correct
  (the symlink pins bytes, it does not assert use) but have not tested.
- **I did not test `__has_include` on `gcc`** as a *positive*; gcc 13 supports
  it, so a row could equally hide the include from `clang`. My fixture aimed at
  clang because `_tu_closure` runs gcc.
- **M1's severity is a judgement.** No row does it, and it takes a deliberate
  `ln -s` of a directory. I ranked it `major` rather than `blocker` on that
  ground; if the manager thinks symlinking an extracted subtree is the obvious
  way to build a php row — and I think it might be — it is a blocker.
- **I did not check whether `check.py` itself would refuse a symlinked `c/`
  subdirectory downstream of the preflight.** `check.py` is out of bounds to
  edit but not to read; I read its glob and not its whole `--no-build` path, so
  there may be a second line of defence I have not found.
- **The `#if 1 / #else` bypass assumes the row keeps `#if 1`.** A real
  preprocessor constant-folds it and `-Wall -Wextra` says nothing, which I
  verified with `gcc -E`; I did not check whether any linter in this project
  would.
- **I did not measure how large `results-php/preflight/` becomes over a
  realistic task history** — only the per-cycle rate. The extrapolation to
  "noisiest thing in the php diff within a dozen tasks" is arithmetic, not a
  measurement.
