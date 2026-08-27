# TASK_107 — batched harness work, and ONE sweep

Every number below was run. Scratch, probes and logs: `.temp/t107/`
(`NOTES.md` there is the running log).

**⚠⚠ THERE WERE TWO SWEEPS, AND THE FIRST ONE REFUTED ONE OF MY OWN
DECISIONS.** Sweep 1 ran with `MIRIFLAGS` pinned and cost p42 a
UB-checked Miri row. I measured why, reversed the decision, and re-swept. Sweep
1's log is kept as `.temp/t107/sweep-SUPERSEDED-miriflags.log`; the tree carries
sweep 2 (`.temp/t107/sweep2.log`). §C and §G below are about sweep 2.

---

## §G — THE SWEEP (26 patterns; `p42` HAS landed, so 26, not 25)

```
== sweeping 26 patterns ==
p01 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11 p12 p13 p14 p16 p17 p18 p19
p22 p23 p27 p36 p38 p42 p46 p47

  24 PASS
   2 PASS-WITH-BLOCKED-ROWS   <- p01 (338 s) and p42 (448 s), exactly the two
== gate: 0 non-zero exit(s) ==

== 2. licence.py --emit (BEFORE synthesize) ==
wrote synthesis/licence.json: 26 patterns, 104 pair verdicts
== 3. synthesize.py ==            wrote results/synthesis.md (71825 B, 557 lines)
== 4. outward_ir.py --emit ==     wrote synthesis/outward_ir.json: 26 patterns
== 5. synthesize.py AGAIN ==      wrote results/synthesis.md (71947 B, 557 lines)
== 6. measure.py --check-stale ==
52 record(s) examined, 0 STALE          check-stale rc=0
```

**Nothing else turned red.** p01's block is the real 180 s Miri timeout; p42's
is `unsafe.rs on large.bin`, its declared one.

⚠ **Step 5 is an extra step I added and it is mandatory now.** §G's order runs
`outward_ir.py` *after* `synthesize.py`, so with §F's new staleness pin the
rendered file would describe the sidecar as it was *before* step 4 re-emitted
it. `.temp/t107/g1_sweep.sh` re-renders and says why. `licence.py --emit` still
runs **before** the first `synthesize.py`, as mandated — no row published
`LICENCE STALE`.

### `results/synthesis.md`: 6 lines moved, 2 hunks, all four numeric changes attributed

`diff -u` against the committed HEAD (`.temp/t107/synth_diff_FINAL.txt`):

| # | line | HEAD | now | cause |
|---|---|---|---|---|
| 1 | §2 calibration | `208 rows, 194 hit, 0 miss, 14 false alarm`; resid p95 5.35 | `208 rows, 188 hit, **4 miss**, 16 false alarm`; p95 7.00 | re-emitted `outward_ir.json` |
| 2 | band `< 2.00` | `143 | 0 real | 143 spurious` | `143 | **4 real** | 139` | same |
| 3 | band `2.00…16.00` | `24 | 10 | 14` | `24 | 8 | 16` | same |
| 4 | §2 sidecar note | *"the only thing in this file with no staleness pin"* | ✅ **FRESH**, 26/26 entries pinned | **§F** |
| 5 | §2 licence score | `181 hit, 15 false LICENSED` | `179 hit, **17** false LICENSED` | re-emitted sidecar |
| 6 | §5 calibration note | *"carries no staleness pin at all"* | now describes the pin | **§F** |

**Lines 1/2/3/5 are one effect and it is fully attributed, row by row.** The
four new "misses" printed by the file itself are:

```
⚠ Misses: p03 small R3-R4 -7.00, p03 large R3-R4 -7.00,
          p04 small R3-R4 -7.00, p04 large R3-R4 -7.00
```

and the licence score moved on exactly six rows, computed row-by-row rather
than inferred:

```
 (p03, small, R3-R4)  hit -> falseLIC        outward moves_by  0.00 -> -7.00
 (p03, large, R3-R4)  hit -> falseLIC                          0.00 -> -7.00
 (p04, small, R3-R4)  hit -> falseLIC                          0.00 -> -7.00
 (p04, large, R3-R4)  hit -> falseLIC                          0.00 -> -7.00
 (p04, small, R5-R4)  falseLIC -> hit                         -7.00 ->  0.00
 (p04, large, R5-R4)  falseLIC -> hit                         -7.00 ->  0.00
                                              net: -2 hit, +2 false LICENSED
```

Every one is a **±7 phase flip on p03/p04**, the cells
`.memory/03-measurement.md` enumerates as exposed. `outward_ir.json` moved 88 of
3208 common leaves, and **16 of the 88 land on `0x0000000000189480`** — which
that file names as `__memset_avx2_unaligned_erms`. The sidecar had not been
re-emitted for a long time and its previous emission was taken at a different
environment phase.

⚠⚠ **A PUBLISHED CLAIM CHANGES AND THE MANAGER SHOULD LOOK AT IT.**
`results/synthesis.md` now prints **`4 miss` in what it itself labels "the
dangerous direction"** where it printed `0`, and the `< 2.00` band goes
`0 real / 143 spurious` → `4 real / 139 spurious`. **The file's own prose
already predicted this in words** — *"p03's and p04's `R3-R4` correction is
`0.00` … at 16 of 32 environment phases and `±7.00` at the other 16"* — so this
is that sentence arriving in the generated table for the first time, not a
regression. It does mean the band's rehabilitated claim now has a **measured**
counterexample rather than only an argued one.

### The 26 gate records: 0 `Ir` moved

```
27164 leaves -> 27385;  NEW 240;  MOVED 185
moved by top-level key: adversarial 85, source_sha256 52, sanitizer 47, notes[0] 1
marginal_ir_per_call leaves moved: 0
```

* **`source_sha256` 52 = 26 × 2** (`harness/check.py`, `harness/limbs.py`).
* **`adversarial` 85 and `notes[0]` 1** are the known per-run class: reordered
  lists, and C rungs diverging on adversarial inputs (`p23`'s `c-gcc` on
  `adversarial-single.bin` went "4 distinct behaviours" → "2"). **Proved
  pre-existing rather than assumed**: two consecutive `check.py p03` runs with
  no edits between moved 31 leaves, **all of them `adversarial` (29) and
  `sanitizer` (2)**, and 0 `marginal_ir_per_call`.
* **`sanitizer` 47** is the ASan pid in the diagnostic string.
* **Zero `Ir`, zero identity, zero digests, zero checksums, zero verdicts.**
* `inputs_checked` is unchanged on all 26.

New fields, uniform across all 26 records:

```
marginal_ir_env  {"bytes": 3269, "tuning_vars": {"LD_PRELOAD": "/usr/libexec/coreutils/libstdbuf.so"}}
published_table  FRESH x 26
miri.miriflags   null      miri.miriflags_removed_ambient  null
miri.miri_version  "rustc 1.99.0-nightly (d453bdd8f 2026-08-14)"
controls_json    p23 -> {"sweep_fit.json": "UNPINNED"}   (a SHOUT, not a failure)
```

⚠ **`LD_PRELOAD=/usr/libexec/coreutils/libstdbuf.so` is real and is mine**: it
is in this agent's shell, inherited by every child. It is recorded because that
is what §D is *for*. A manager re-running from a plain shell will see a
different `tuning_vars` and should expect the p03/p04 marginals to be a
different draw — which the field now makes diagnosable instead of mysterious.

---

## The three calls the task named

### 1. ⚠⚠ `--emit=dep-info` is the RIGHT INSTRUMENT and the WRONG REPLACEMENT. Do not replace the walk — UNION with it.

The manager's own doubt was right and sharper than stated: **Verus is a
different front end, and rustc cannot expand the `verus!` proc macro at all.**

Measured before rewriting anything (`.temp/t107/a1_routes.py`, **14 routes × 3
instruments, every arm run**):

| route | Verus reads the leaf | dep-info | dep-info `+ --cfg` | regex walk |
|---|---|---|---|---|
| R1–R4 `include!` ×4 (paren/bracket/brace/raw) | yes | yes | yes | yes |
| R5 `#[path] mod` | yes | yes | yes | yes |
| R6 `#[path]`-of-`#[path]` | yes | yes | yes | yes |
| R7 `macro_rules!` → `#[path]` | yes | yes | yes | yes |
| **R7a `#[cfg_attr(all(), path=…)]`** | yes | yes | yes | **NO** |
| **R7b `#[path = r"h.rs"]`** | yes | yes | yes | **NO** |
| **R7c `mod x { mod m; }`** | yes | yes | yes | **NO** |
| **N1 `#[path] mod` INSIDE `verus!{}`** | yes | **NO** | **NO** | yes |
| **N2 `include!` INSIDE `verus!{}`** | yes | **NO** | **NO** | yes |
| **N3 `#[cfg(slb_twin)] #[path]`** | yes | **NO** | yes | yes |
| CONTROL-plain (no include) | no | no | no | no |

**N1 and N2 are new — a tenth and eleventh route, and they decide the design:**

```
main.rs:  use vstd::prelude::*;  verus! { #[path = "h.rs"] mod m; … }
h.rs:     #[verifier::external] pub fn t107_leaf(p:*const u64)->u64 { unsafe { *p } }

./verus_run.py main.rs --crate-type=lib   ->  "1 verified, 0 errors"
rustc --edition 2021 --emit=dep-info=out.d main.rs
    out.d: main.rs                         <-- h.rs ABSENT
    rustc: "error: cannot find macro `verus` in this scope"
check._path_includes(dir, ['main.rs'])    ->  ['…/h.rs']
```

**Replacing the walk would have closed three routes and opened three — and the
three it opened live inside the construct every R5 in this project is written
in.** So `_path_includes` is now two limbs feeding one list: dep-info is exact
for what rustc resolves (every attribute spelling, where the regex kept losing);
the regex is cfg-blind and macro-blind, i.e. it over-approximates, which is the
safe direction for a *file set* and is what covers N1/N2/N3.
**Union 13/13; either limb alone 10/13.**

The `TASK_084_REVIEW` major-1 asymmetry is **not** re-opened: the change is
inside the shared function, so `_verus_file_list` (→ `_trusted_items`,
`_axiom_items`, `check_call_site`), `_scan_unsafe_sites` and
`_check_twin_cfg_hygiene` all get the same list, as before.

⚠ **N3 deserves its own line.** dep-info catches it **only because
`_DEP_INFO_CFGS` passes `--cfg slb_isolated --cfg slb_twin`** — i.e. only
because the gate happens to know the project's cfg names. A `#[cfg(anything
else)]` is invisible to dep-info under any fixed flag set; the cfg axis is
combinatorial and the compiler cannot be asked about all of it at once. That is
not a hole *because* the cfg-blind regex limb covers it, and it is the reason
the regex limb must stay.

**Fail-closed is wired.** `_dep_info_files` returns `(None, err)` when rustc
writes no `.d`; `_path_includes` collects those; `_check_opaque_includes` turns
each into a `rep.fail("tcb-unsafe", …)` naming the root, the exact command and
rustc's message. It never falls back to the regex silently. (rustc **does** emit
the `.d` even when compilation fails — that is what makes this usable on a Verus
source, which does not compile under plain rustc.)

**Blast radius: zero.** `.temp/t107/a2_census.py`, 26 patterns: dep-info **adds
0 files, misses 0, and 0 roots produced no `.d`**. Every pattern's walk returns
exactly `['common/driver.rs']`, before and after.

### 2. ⚠⚠ §D's one integer is NOT enough. A length is a lossy pin, and here is the counterexample.

`.temp/t107/d1_env.py`, p03 `unsafe` `-O3 isolated` `small.bin`.

**The must-fire arm fires** (`d1_env.py length`) — env length varied only, block
length read from a **real child's** `/proc/self/environ`:

```
pad=  0   child block 3290 B   marginal 3066.00
pad=  8   child block 3298 B   marginal 3059.00
pad= 16   child block 3306 B   marginal 3059.00
pad= 24   child block 3314 B   marginal 3066.00     <- ±7, bistable, period 32
```

**And the content arm kills the length-only pin** (`d1_env.py content`) — two
environments whose child-measured block length is **byte-identical**:

```
3332 B   GLIBC_TUNABLES=glibc.cpu.x86_rep_stosb_threshold=64   marginal 3545.00
3332 B   SLB_T107_FILLER=<35 z>                                marginal 3059.00
                                                    SAME LENGTH,      +486.00
```

**+486.00 Ir/call at an identical recorded length — 69× the ±7 the pin exists to
diagnose.** p03 `memset`s a stack array per call and the tunable selects a
different libc `memset` path, so it lands in the per-call term rather than the
start-up constant that cancels. A length-only record would have said *"same
length, so the marginal must match exactly"*, and that implication is false.

**So the record carries two things:**

```json
"marginal_ir_env": {"bytes": 3269, "tuning_vars": {"LD_PRELOAD": "…/libstdbuf.so"}}
```

`tuning_vars` = every variable matching `GLIBC_TUNABLES` / `LD_*` / `MALLOC_*`,
the set that can change a libc code path **per call** without changing the
length. Derived from the measurement, not from a list.

**How the integer is taken, and the two ways this project has already got it
wrong:** read **inside a child spawned the way `_callgrind_total` spawns** — not
from `os.environ` (a Python dict; control entry 7, and a variable costs an envp
slot + name + `=` + value + NUL) and not from `check.py`'s own
`/proc/self/environ` (frozen at *this* process's `execve`, equal to a child's
only while nothing mutates `os.environ`).

⚠ It is **not** the client's block under valgrind (valgrind appends `vgpreload`
entries and synthesises the client stack), so it is a **coordinate on the axis**
offset by a deterministic function of itself — sufficient for the rule *same
recorded value ⇒ must match exactly*, and said so in the docstring.
⚠ **argv is the other half of the same axis** and is not recorded: the gate's
argv is fixed by the repo path and the pattern id, so the pin is valid **within
one clone location** — the same restriction `md5_fn` already carries.

**✅ Validated three ways, and the third is the best one.**

*(a) Same session, no edits, two `check.py p03` runs:*
```
both runs  marginal_ir_env {"bytes": 3280, "tuning_vars": {...libstdbuf.so}}
           0 of 96 marginal_ir_per_call leaves moved
           31 leaves moved: 29 adversarial + 2 sanitizer  (the known class)
```

*(b) Against the committed record, from a different session:* p03's three
exposed cells moved by exactly the documented amounts and directions —
`safe_tuned +7`, `unsafe +7`, `verus −7` — so the published pair `verus−unsafe`
goes `+6.00 → −8.00`, the sign flip. Not a code change; a different environment.

*(c) ⚠⚠ **AND IT CAUGHT A LIVE ONE, WHICH IS WHY §A's `CONTROL-none` "FAILED"
AFTER THE SWEEP AND THE FAILURE IS A TRUE POSITIVE.*** Re-running the exact
`check.py p03` → `licence --emit` → `synthesize` chain from the **interactive
shell** instead of the **sweep's shell** moved `results/synthesis.md`:
p03's published row went from `small +5117.00 (+7.00) ? / large +17244.00
(+7.00) ?` to blank. Cause, read straight off the new field:

```
sweep shell        marginal_ir_env.bytes = 3269   unsafe/O3/isolated/small = 3059.00
interactive shell  marginal_ir_env.bytes = 3280   unsafe/O3/isolated/small = 3066.00
                   22 of p03's marginal leaves moved by exactly ±7
```

**An 11-byte environment difference between two shells — the same size as the
`OLDPWD` difference `.memory/03-measurement.md` documents — moved a published
number, and the field is what says so.** This is
*"re-run the gate and compare is NOT a reproduction test"*, reproduced live and
now diagnosable. The tree was restored to the sweep's coherent set afterwards
(`--check-stale` re-run: 52 records, 0 STALE).

### 3. §E belongs in `check.py`, and the cost argument is the weaker of the two reasons.

I agree with the task and want to add the reason it did not give.

The cost argument is real: `measure.py` is inside
`measure.py::measurement_sources`, so a staleness check there costs a full
matrix re-measure — which re-takes the wall-clock block — for a **bookkeeping**
check. `check.py` is not measurement-hashed.

**But the decisive reason is structural, and it is the defect the prototype
had.** `.temp/mgr99/tables_stale.py` globbed `results/tables/*.md` and reported
*"24 checked, 0 STALE"* on a 25-pattern tree, because **a checker that can only
see the files it is checking cannot report an absent one.** *"Iterate over
patterns, not over tables"* is, in a standalone script, a rule someone has to
remember. **In a per-pattern gate stage the iteration IS the pattern list** — a
pattern with no table fails **its own** gate and there is no list to forget.

Second-order: **nothing runs a standalone script.** Item 23 was closed at
TASK_084, its closing note predicted the recurrence in writing, and it took 16
tasks to recur.

⚠ **Cost of being wrong, stated:** the gate is now **20 stages** (18 + `9` +
`9b`), the two new ones take milliseconds, and they add **one ergonomic**: a
brand-new pattern's *first* gate run FAILs on `MISSING` until
`harness/report.py pNN` has run. That is a two-command loop, and the diagnostic
says so and points out that `check.py` writes `results/gate/<pattern>.json`
**even on a FAIL**, so the record `report.py` renders from is available at once.
Zero of the 26 shipped patterns are affected.

---

## §A — implementation and acceptance

`check.py::_dep_info_files`, `check.py::_path_includes`,
`check.py::_check_opaque_includes`.

**`.temp/t107/a3_source_to_published.py --all` — 15 arms, ONE command,
`harness/check.py p03` → `synthesis/licence.py --emit` →
`synthesis/synthesize.py`, every arm snapshotting and restoring the tree by
bytes in a `finally:`.**

```
 arm             regex-only  dep-only  union   chain
 R1              True       True      True    ok
 R2              True       True      True    ok
 R3              True       True      True    ok
 R4              True       True      True    ok
 R5              True       True      True    ok
 R6              True       True      True    ok
 R7              True       True      True    ok
 R7a             False      True      True    ok
 R7b             False      True      True    ok
 R7c             False      True      True    ok
 N1              True       False     True    ok
 N2              True       False     True    ok
 N3              True       True      True    ok
 CONTROL-plain   False      False     False   ok
 CONTROL-none    None       None      None    ok

 dep-info ALONE would miss : ['N1', 'N2']
 the HEAD regex ALONE misses: ['R7a', 'R7b', 'R7c']
 the UNION misses           : []

 git status unchanged: True
 15 arm(s), 0 failure(s)
```

Each of the **13 route arms**, on the real tree:

```
gate rc=1 (want != 0); tcb-unsafe lines naming h.rs: 2; synthesis.md MOVED
  FAIL [tcb-unsafe] patterns/p03-bounded-stack/t107p/h.rs:6 `unsafe` in a shared
  driver file the rungs `#[path]`-include. …
```

and the controls:

* **`CONTROL-plain`** — `unsafe` planted **directly in the root `verus.rs`**, by
  no route. All three walks say `False` (correct: a root is not an include), the
  gate still **FAILS** and `synthesis.md` still **MOVES**. This is the arm that
  proves the rig can see a plant.
* **`CONTROL-none`** — no plant: gate rc=0, `synthesis.md` **byte-identical**
  (and see call 2(c) for the one later run where it correctly did *not* stay
  byte-identical).

⚠ The `regex-only` column is `git show HEAD:harness/check.py`'s
`_path_includes` **extracted and exec'd, not transcribed** — TASK_099's model
transcribed it, and a transcription can drift from the thing it references.

⚠ **A probe artefact I made and caught.** The first route matrix named every
module `h`, so `_path_includes`'s `\bmod\s+(\w+)\s*;` fallback resolved `h.rs`
**by accident** and R7a/R7b/N3 read as *"the regex sees raw strings and
`cfg_attr`"* — the opposite of the truth. Every module is named `m` now and the
comment saying why is in the file.

## §B — `_check_opaque_includes` no longer fails the gate on prose

All five reported false-positive shapes fixed, a sixth added, both must-fire
arms fire (`.temp/t107/b1_opaque_shapes.py`):

```
  ok   FP-1 line comment                                  fires=False want=False
  ok   FP-2 //! doc comment                               fires=False want=False
  ok   FP-3 block comment                                 fires=False want=False
  ok   FP-4 string literal                                fires=False want=False
  ok   FP-5 commented-out real                            fires=False want=False
  ok   FP-6 doc comment on an item (the accident route)   fires=False want=False
  ok   real-opaque MUST FIRE                              fires=True  want=True
  ok   real-missing MUST FIRE                             fires=True  want=True
  ok   real-literal, file exists (must NOT fire)          fires=False want=False
§B shapes: PASS
```

**How, and there is a trap inside the fix.** Sites are located in
`vparse.blank_noncode(txt)`; **the literal is read back out of the RAW text at
the same offset.** They cannot be the same string — `blank_noncode` blanks
string literals too, so `include!("h.rs")` becomes `include!(        )` and a
check run on the blanked text alone classifies **every legitimate literal
include as OPAQUE**, trading a false positive on comments for one on real code.
Offsets survive blanking, so find-in-one/match-in-other is exact. I hit this on
the first attempt; it is written up in `_include_literals`'s docstring.

**The diagnostic is fixed.** *"Use a literal path"* is unactionable for the case
it names. It now says: write the literal if there is one; if it is
`concat!`/`env!("OUT_DIR")` there is no literal **and no build script either**
(`build.py` invokes rustc directly, no `OUT_DIR`), so commit the generated code
as a real `.rs` (generator in `controls/`, which the gate hashes) and `include!`
*that*; and if you are **quoting** the idiom, put it in a comment or a string —
this check reads code only now.

**Scope gap: EXTENDED, and the old reason was incomplete.** The check now covers
the pattern's own `*.rs` roots as well as the `verus.obligations` sources and
the walked includes. *"No stage scans the safe rungs for `unsafe` tokens"* is
true and is not the only thing at stake: stage 0b's spelling audit, `dloop`'s
driver-loop diff and `exec_code` all read rung sources, and an unresolvable
`include!` hides tokens from every one of them. Cost of extending: **zero rows**
— the 26 patterns contain no `include!` of any spelling.

## §C — ⚠⚠ `MIRIFLAGS` must be UNSET, and my first answer was wrong

**What I did first, and what refuted it.** I measured the seed question, chose
*(a) pin*, picked `MIRIFLAGS="-Zmiri-seed=0 -Zmiri-symbolic-alignment-check"` on
the strength of **38 rows across p03/p38/p46/p14/p02 at 11.4 s vs 11.3 s, 0
verdicts moved**, and swept. **Sweep 1 then showed p42 with a SECOND blocked
Miri row** — `adversarial-wincap.bin` joined `large.bin`. It reproduced on an
idle re-run, so it was not contention.

**Measured properly afterwards**, on p42's `adversarial-wincap.bin`, the gate's
own probe file (md5-identical to a fresh one), `cwd=pdir`, the exact
`check_miri` command line (`.temp/t107/c4_*.log`):

```
MIRIFLAGS unset                                    74.6 / 73.4 / 74.0 / 73.8 / 73.2 s
MIRIFLAGS=""                            (EMPTY)                            339.8 s
MIRIFLAGS="-Zmiri-disable-isolation"    (a DUP of a command-line flag)      342.0 s
MIRIFLAGS="-Zmiri-provenance-gc=10000"  (the documented DEFAULT VALUE)      338.2 s
MIRIFLAGS="-Zmiri-seed=0"                                          340.4 / 338.3 s
MIRIFLAGS="-Zmiri-symbolic-alignment-check"                        337.8 / 337.0 s
MIRIFLAGS="-Zmiri-seed=0 -Zmiri-symbolic-alignment-check"          342.7 / 339.0 s
```

**Seven settings, all ≈4.6×. The only fast configuration is the variable being
ABSENT — even the empty string costs the full 4.6×, so the trigger is the
variable's PRESENCE, not its content.** `MIRI_TIMEOUT` is 180 s, so pinning any
value turns a 74 s UB-checked row into a blocked one — and p42's own `spec.md`
calls Miri *"load-bearing for the pattern's own subject on the R4 side"*,
because R4 has no proof and Miri's exit-time leak report is the only mechanical
check that it does not leak.
⚠ **THE MECHANISM IS OPEN.** I have the effect seven ways and no explanation for
it. Do not write one down until somebody measures it.

⚠ **And one of my own earlier measurements does not reproduce and I cannot
explain it.** A first pass reported 72.8 / 73.8 / 73.6 s for unset / seed /
seed+symbolic on a byte-identical probe. Three later repeats **and the gate
itself, twice**, contradict the seeded numbers. Recording the disagreement, not
a mechanism.

**Landed: `MIRI_FLAGS = ()`.** An ambient `MIRIFLAGS` is **removed** from the
child (so the gate's configuration does not depend on the invoking shell) and
what was removed is recorded. The record carries:

```
miri.miriflags                  null      <- UNSET, which is NOT the same as ""
miri.miriflags_removed_ambient  null
miri.miri_version               "rustc 1.99.0-nightly (d453bdd8f 2026-08-14)"
```

**`miri_version` is the substantive replacement for the seed.** Miri's unseeded
default address assignment is *deterministic for a given miri* (five timings
agree to 1.9%; the address probe reproduces `base % 4 == 3`). What actually went
stale between TASK_102 and now is the **miri build**, so that is what a green
row needs beside it to be reproducible.

**Sweep 2 confirms the reversal:** p42 is back to **one** blocked row
(`unsafe.rs on large.bin`).

**⚠ The premise in `.memory/00-environment.md` does not reproduce.** It says the
same source is *"clean under `-Zmiri-seed=0` and `2` and UB under `1` and `3`"*.
Measured (`.temp/t107/c2_miriflags.py --probe`, two families × 12 seeds):

```
FAMILY 1 -- Vec<u32>, allocation alignment 4 (answers fixed BY CONSTRUCTION)
  byte off   0    1    2    4
  unset      ok   UB   UB   ok        0 misses, 0 false positives
  seed=N     ok   UB   UB   ok        identical for N = 0..11
  seed+sym   ok   UB   UB   ok        identical for N = 0..11

FAMILY 2 -- Vec<u8>, allocation alignment 1 (answer = a function of the ADDRESS)
  ptr::read::<u32> at byte offset 1
  unset    CLEAN        seed=N  UB (all 12)        seed+sym  UB (all 12)
```

and `base % 4` is **3** unseeded and **1** for every seed tried
(0/1/2/3/7/100/1000/12345/999999). **The live variable is unseeded-vs-seeded,
not seed-vs-seed**, so *design (b), a seed sweep, buys nothing measurable* —
`0 of 40` p01 rows and `0 of 20` p09 rows change UB verdict or timeout status
with the seed — while costing exactly 4.00× (p01's Miri stage 182.0 s → 728.0 s,
of which **720 s is one row hitting `MIRI_TIMEOUT` four times**).
The entry's **conclusion** — that a green Miri row was a claim about a
configuration nobody had written down — stands, and recording the configuration
is the answer to it.

## §D — the environment block in the gate record

Covered under call 2. `check.py::_env_block` (a real child, `/proc/self/environ`)
called inside `check_marginal_ir`, popped in `main()` into `marginal_ir_env`
beside `marginal_ir_per_call`. **It records; it does not pin** — it does not
force an environment, so it cannot make the number reproducible-and-wrong. The
rule it enables is written into `main()` beside the field:

* same `bytes` **and** same `tuning_vars` ⇒ the marginal must match **exactly**;
* different `bytes` ⇒ compare `kernel_exclusive_ir` (structurally immune, 0 of
  288) or re-run at the recorded length;
* same `bytes`, **different `tuning_vars`** ⇒ **not comparable at all**
  (+486.00 measured).

## §E — `results/tables/` and `controls/*.json` now have detectors

`check.py::check_published_tables` (stage 9) and
`check.py::check_control_json_pins` (stage 9b); recorded as `published_table`
and `controls_json`.

**Both failure modes fail, every arm run** (`.temp/t107/e1_tables.py`):

```
check_published_tables:
  ok   FRESH  (must NOT fail)                 verdict=FRESH     fires=False want=False
  ok   STALE  (must fail)                     verdict=STALE     fires=True  want=True
  ok   UNPINNED (must fail)                   verdict=UNPINNED  fires=True  want=True
  ok   MISSING  (must fail)                   verdict=MISSING   fires=True  want=True
  ok   UNPINNED-with-md5-decoys (must fail)   verdict=UNPINNED  fires=True  want=True
check_control_json_pins:
  ok   UNPINNED -> shout, not fail        UNPINNED  fail=False shout=True
  ok   STALE    -> fail                   STALE     fail=True  shout=False
  ok   FRESH    -> neither                FRESH     fail=False shout=False
§E arms: PASS
```

**and end-to-end through the real gate** (`e1_tables.py --end-to-end`):

```
  planted a stale citation c51288b0c9f6 -> 000000000000
  gate rc=1 (want != 0); [tables] lines: 2
    FAIL [tables] results/tables/p03-bounded-stack.md is STALE: it cites contract
    ['000000000000'] and `spec.md`'s `slb-contract` block now hashes to c51288b0c9f6…
  results/tables restored, git status: clean
```

⚠ **The `md5-decoys` arm is the one worth keeping.** A generated table's `why`
block is full of 12-hex md5 prefixes (`e207ec6c8697`, `da08af26d9b1`, …), so a
loose *"is any 12-hex string equal to the contract digest"* scan both
false-positives and false-negatives. The detector matches
`report.py::audit_section`'s **own citation line** —
``from `results/gate/<pattern>.json`, contract `<12 hex>` `` — i.e. it computes
from the artefact, not from the prose around it.

Third verdict beyond the two named: **`UNPINNED`** — a table that exists and
cites no contract at all. Fail-closed; fires on nobody today.

**`controls/*.json`: I built the READER and could not build the WRITER.** `p23`
ships `patterns/p23-partition/controls/sweep_fit.json` with no pin, and adding
one means editing a generator under `controls/`, which this task's constraints
forbid. So an unpinned sidecar is **SHOUTED**, not failed (failing would paint
p23 red for a fix I was not allowed to make); a sidecar that *does* carry the key
is checked and a mismatch **FAILS**. ⚠ **The generator edit is OWED and is
cheap**: `controls/*.py` is in the **gate** record's `source_sha256` and **not**
in `measure.py::measurement_sources` (verified by reading both), so writing the
pin costs **one gate re-run and no re-measure**.

## §F — the two small ones

**`harness/limbs.py::TWIN_BANNED`** — fixed by **importing** `check._TWIN_BANNED`
rather than by adding the missing string, because this file's own docstring says
it re-derives `check.py`'s comparison and a copy can drift. The failing arm, on
a body containing `#[verifier::external_body]`:

```
new (imported)  ('unsafe','assume','admit','assume_specification','external_body','external')
                -> fires: external_body
old (copied)    ('unsafe','assume','admit','assume_specification','external')
                -> fires: NOTHING     <- the under-report; entry 3 on
                                         .memory/03-measurement.md's list
```

`\bexternal\b` cannot match `external_body` because `_` is a word character.

**`synthesis/outward_ir.json`** — now carries `gate_source_sha256` per pattern,
the same key and shape `licence.json` uses
(`synthesis/outward_ir.py::_gate_source_sha256`), and
`synthesis/synthesize.py::calibrate` computes `stale`/`unpinned` on every run and
prints the status in §2. **The detector fired on real data before the fix
landed** — run against the pre-existing sidecar it published *"IS STALE … No pin
at all (emitted before TASK_107): p01, …, p47"*; after the re-emit it publishes
*"✅ FRESH — all 26 entries…"*. The two sentences asserting the sidecar had no
pin are replaced by the live status.

---

## Files changed

```
harness/check.py           §A §B §C §D §E   (not measurement-hashed)
harness/limbs.py           §F               (not measurement-hashed)
synthesis/outward_ir.py    §F               (in no hash set)
synthesis/synthesize.py    §F               (in no hash set)
results/gate/p*.json  x26  regenerated by the sweep
results/synthesis.md, synthesis/licence.json, synthesis/outward_ir.json
.tasks/TASK_107_REPORT.md  this file
```

**No `patterns/` file, no `harness/{build,asm,measure}.py`, no `.memory/`, no
`RECAP.md`, no `git add`/`commit`.** `check.py::_scan_unsafe_sites` untouched.

## What I did NOT do, and what I am unsure about

1. **The `controls/*.json` pin is only half-built** (reader yes, writer no) —
   see §E. One line in `patterns/p23-partition/controls/*.py`, costing one gate
   re-run.
2. **The `MIRIFLAGS` 4.6× has no mechanism.** Seven configurations, one effect,
   no explanation. And one of my own earlier measurements of it does not
   reproduce.
3. **I edited `check.py` once while an acceptance run was in flight** (renaming
   the dep-info scratch file to include the pid). The change is inert inside a
   single process, but I re-ran `R1`, and later `CONTROL-none`/`CONTROL-plain`/
   `N1`, plus the whole §B and §E suites, under the final `check.py`. Recorded in
   `.temp/t107/NOTES.md` rather than glossed.
4. **`tuning_vars` is a chosen prefix set** (`GLIBC_TUNABLES`, `LD_*`,
   `MALLOC_*`). It is derived from one measurement, and I have not shown it is
   *complete* — another variable could in principle change a per-call libc path.
   It is strictly better than a length alone; it is not a proof.
5. **The `< 2.00` band's new `4 real` rows** change a published claim. I
   attributed them completely to the p03/p04 ±7 cells, but I did not re-run the
   32-pad sweep to confirm this run's phase against `.temp/r98/`'s.
6. **§C's blast radius outside p42 is not measured.** I know `MIRIFLAGS`
   presence costs 4.6× on p42's allocation-heavy kernel and ~0% on 38 rows across
   five other patterns. I did not test the other 20.
7. **`.memory/00-environment.md`'s seed sentence and `p42`'s
   `spec.md::miri.blocked_reason`** both now state things that no longer hold
   (the seed split, and *"check.py passes no MIRIFLAGS … a green row is 'no UB
   at whatever seed ran'"* — the second half is now answered by
   `miri.miri_version`). Both are manager-only files; flagged, not touched.

---

⚠ **PROTOCOL rule 2's running count: 399 → 403.** Four manager premises
contradicted with a measurement, each with an arm that fired:

1. **§A's "replace the walk with `--emit=dep-info`"** — refuted; N1/N2 are a
   tenth and eleventh route that Verus takes and dep-info cannot see.
2. **§D's "one integer is enough"** — refuted; **+486.00 Ir/call at a
   byte-identical block length**.
3. **§C's premise, inherited from `.memory/00-environment.md`** — *"clean under
   seed 0 and 2, UB under 1 and 3"* does not reproduce at this toolchain.
4. **§C's framing that the choice is (a) pin vs (b) sweep** — both are wrong
   here: **setting `MIRIFLAGS` at all, even to `""`, costs 4.6× and blocks a
   UB-checked row**, so the answer is *record the configuration, do not pin it*.
   ⚠ **This one refuted MY OWN first answer, and the thing that refuted it was
   the sweep the task told me to run last.**

**Reconciliation is the manager's job, not mine** — this task was launched from
399 and ran alone, so 403 is a carry-forward from a single branch.
