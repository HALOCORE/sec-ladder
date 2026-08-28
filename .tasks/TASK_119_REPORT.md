# TASK_119 — the instrument corrections `TASK_114` earned. ONE sweep, done.

**Role: research engineer.** Everything below was run. Probes, logs and JSON:
`.temp/t119/` (`NOTES.md` there is the index and says how to re-derive each one).

**Headline:** all seven items landed in **one** 26-pattern sweep —
**24 PASS + 2 PASS-WITH-BLOCKED-ROWS, 0 failures**, `52 record(s) examined,
0 STALE`. `p42` has **one** blocked row, the declared `large.bin` one, same as
HEAD. **§A's new integer works and I broke it anyway** (`argv`, on purpose, and
the record now says so). **§B's answer is NO and that is the useful answer.**

---

## §A — the env pin's second integer. `nvars`, and three more keys

`check.py::_env_block` now returns

```
{"bytes", "nvars", "envp_stack_bytes", "tuning_vars", "repo_path_bytes", "domain"}
```

* **`nvars`** is `b.count(b'\x00')` on **the same blob the same child already
  read** — one child, one `/proc/self/environ`, no `os.environ` arithmetic and
  no read of `check.py`'s own block. Both of those are documented ways this
  project has already got it wrong and the docstring names them.
* **`envp_stack_bytes` = `bytes + 8*nvars`** — the single integer the comparison
  rule now uses. ⚠ Named after `TASK_114`'s own proposal, and the docstring says
  what it is **not**: the envp contribution only, with `argv`, `auxv` and
  `AT_EXECFN` outside it.
* **`repo_path_bytes` = `len(REPO)`** and a **`domain`** string, *in the record*,
  because `TASK_114` §A.3's finding was that *"valid within one clone location"*
  lived in a task report and nowhere a reader of the pin would look.

### Acceptance — `.temp/t119/a1_nvars_pin.py all` → `a1_all.json`, 4/4 arms

p03 `unsafe` `-O3 isolated` `small.bin`, marginal computed exactly as
`check_marginal_ir` does. 7.6 s for the whole thing.

**`count` — the deliverable, with the OLD field as its must-fire arm:**

```
  1 filler var(s)  bytes=3520 nvars=49 envp_stack_bytes=3912 (mod32= 8)  marginal=3059.00
  2 filler var(s)  bytes=3520 nvars=50 envp_stack_bytes=3920 (mod32=16)  marginal=3059.00
  3 filler var(s)  bytes=3520 nvars=51 envp_stack_bytes=3928 (mod32=24)  marginal=3066.00
  4 filler var(s)  bytes=3520 nvars=52 envp_stack_bytes=3936 (mod32= 0)  marginal=3066.00

  OLD field distinct values: 1   marginals: [3059.0, 3066.0]
  MUST-FIRE (old field says 'same draw' across a real difference): FIRED
  NEW field distinct values: 4; groups with a split marginal: 0
  THE FIX (new field distinguishes what the old one did not): YES
```

`TASK_114`'s `3059/3059/3066/3066` ladder reproduces to the instruction at a
byte-identical `bytes = 3520` with identical (empty) `tuning_vars`. The old
field takes **one** value across a 7.00 `Ir`/call split — that is the arm that
fires. The new field partitions the four with **zero** groups carrying a split
marginal.

**And the new integer is not merely *a* discriminator — it sorts BOTH ladders.**
Run the length ladder too and bucket every row by `envp_stack_bytes mod 32`:

```
  marginal   3059.00  <- residues [8, 14, 16, 22]
  marginal   3066.00  <- residues [0, 6, 24, 30]
  residue sets disjoint across the two states: True
```

`pad` moves the block length at a fixed count, `count` moves the count at a
fixed length; **one integer puts both into the same two states**, with the
16-wide window at period 32 that `_env_block`'s docstring already documented.

### ⚠ The manager's named doubt 1, answered: I tried to break the new pin, and I did

**`split` (a clean negative).** Hold `bytes` **and** `nvars` **and**
`tuning_vars` fixed, and redistribute the same 240-byte budget over the same
three variables five different ways (even ×2, `(150,40,14)`, `(14,40,150)`,
`(2,2,200)`): **`marginal = 3066.00` in all five.** So the count is not just one
more thing that happens to vary — the composite is doing real work.

**`argv` (it fires).** Hold **all three recorded fields identical** and vary
only `argv[1]`'s path length:

```
  argv[1] len=57/58/59/61  ->  3059.00
  argv[1] len=65/73        ->  3066.00
  recorded field identical across the sweep: True
```

> ⚠⚠ **So the new pin is INCOMPLETE TOO, and I have said so in the code rather
> than shipping a second "must match EXACTLY".** The rule beside
> `marginal_ir_env` in `main()` is now stated as a **NECESSARY** condition —
> *any of the three differs ⇒ not comparable* — with *all three equal ⇒ this
> record cannot tell the two draws apart*, and **SUFFICIENCY marked OPEN** in
> those words. `bytes` also explained a measured period and was believed
> sufficient; that is exactly the mistake not to repeat.

### ⚠⚠ And the pin had a live outing during this task, unplanned and decisive

Re-running `harness/check.py p03` **with identical code, in the same shell,
minutes after the sweep**:

```
  bytes 3264 -> 3280   nvars 48 -> 48   envp_stack_bytes 3648 -> 3664
  -> exactly 30 of 96 marginals moved, by exactly ±7.00 and nothing else
```

*"Re-run the gate and compare"* is not a reproduction test, and the field now
says why. (I then re-gated p03 through `.temp/t119/regate_one.sh` — the same
shell shape `sweep.sh` used — so **all 26 committed records share one draw**:
`bytes=3264 nvars=48 envp_stack_bytes=3648 repo_path_bytes=33`, and p03's
`marginal_ir_per_call` is byte-identical to its sweep run.)

---

## §B — a DECISION. The answer is NO, and no mechanism is proposed

### The one question asked: does §A's integer separate the fast and slow states?

`.temp/t119/b1_miri_state.py` → `b1_miri_state.json` / `.log`. p42 `unsafe.rs`
on `adversarial-wincap.bin`, `cwd=pdir`, the exact `check_miri` command line —
`TASK_114` §B2's setup. Five timed runs:

```
  A  ambient (MUST FIRE: slow)     368.9s SLOW  bytes=3280 nvars=48 envp=3664 (16)
  D  ambient + decoy var           75.3s  fast  bytes=3296 nvars=49 envp=3688 ( 8)
  B  SAME envp_stack_bytes as A    74.2s  fast  bytes=3272 nvars=49 envp=3664 (16)
  C  SAME residue, envp+32         74.7s  fast  bytes=3304 nvars=49 envp=3696 (16)
  A' ambient repeated             341.2s  SLOW  bytes=3280 nvars=48 envp=3664 (16)
```

* **MUST-FIRE fired**: the ambient block is SLOW, twice — the **fifth and sixth**
  independent slow measurement after `TASK_114`'s four.
* **Negative control D reproduces `TASK_114`'s arm C byte-for-byte** (3296 / 49,
  74.4 / 75.9 s there, 75.3 s here).
* ⚠⚠ **Arm B is the answer. An environment carrying the SLOW block's EXACT
  `envp_stack_bytes` (3664) ran FAST.** Arm C says the residue does not carry it
  either.

> **So `envp_stack_bytes` does NOT determine the Miri state, and the record
> cannot answer via that field.** ⚠ **I am proposing no mechanism.** This is a
> correlation killed by measurement and reported rather than suppressed, which
> is what `TASK_114` did with `base % 4 == 3` and what this axis needs after two
> wrong published mechanisms.

### Therefore: the wall time is recorded, unconditionally

`check_miri` now writes **`miri.runs[].seconds`** on every row, including the
timeout-blocked one (where it is the cap, and the code says so). It is the only
wall-clock number in the gate record; nothing hashes it, nothing compares it, no
verdict depends on it, and the comment states that the per-re-gate churn is the
price of the row above being readable at all.

**It answered its first question on its first outing.** In the sweep, p42's
`adversarial-wincap.bin` — the row `TASK_114` B2.3 predicted could block —
recorded **`seconds: 74.3`**, the fast state, against the 180 s budget, while my
own ambient shell measured **368.9 / 341.2 s** for the same source and input two
hours earlier. **Before this key the record could not have told the two apart**,
and `miriflags` / `miriflags_removed_ambient` / `miri_version` are identical in
both states.

### Should `MIRI_FLAGS = ()` stay? YES — on a different argument, now written down

**It stays.** But the code carried the *retracted* justification, in four places
(`.memory/` had the retraction; `check.py` did not), including a line the gate
**prints on every Miri run**:

```
MIRIFLAGS = <UNSET>  -- deliberately, not by omission: setting it AT ALL, even
to "", costs 4.6x on p42 (74 s -> 340 s, past the 180s budget).
```

All four are struck and replaced with `TASK_114`'s measurement, the driver
result (`miri` the **rustc driver** never parses `MIRIFLAGS`; it is
`cargo-miri`'s), **mechanism OPEN**, and the true reason:

> the gate must not inherit a flag set from the invoking shell — `MIRIFLAGS`
> *is* read by `cargo miri`, and a row certified under an ambient
> `-Zmiri-ignore-leaks` would be a silently weaker check than the record claims.
> **That argument is about REPRODUCIBILITY, not speed, and it does not depend on
> any mechanism for the 4.6×.**

⚠ **I did not chase the mechanism** (manager doubt 2). I think that is right: I
spent five timed runs on the one question the record could act on, got a clean
negative, and stopped. Characterising *which* environments are slow needs a wide
sweep at 75–370 s per point — a task, not an arm.

---

## §C — FIX three, DOCUMENT one. The argument is a design one

**Decision: closed `N7aV`, `N7bV`, `N7cV`; `N8V` is a NAMED RESIDUAL.**

⚠ Manager doubt 3 offered "document all four and leave it", and I did not take
it, for a reason that is not "one more spelling". `_path_includes`'s own
docstring licenses the regex to lose on attribute spellings **because dep-info is
exact for them**. `TASK_114`'s four routes are all *inside `verus!{}`* — where
rustc cannot expand the macro, dep-info returns nothing and **the regex stands
alone**. The stated division of labour is void in exactly that cell, so three of
the four are not new spellings at all; they are the same spellings the design
already promised to cover, written one construct deeper.

* **`_PATH_ATTR_RE`** replaces the inline `#\[\s*path\s*=\s*"..."\]` regex:
  accepts a **raw string** and `path` **nested inside another attribute**
  (`cfg_attr`). ⚠ **Anchored to `#[` on purpose** — the obvious broadening
  (`path = "..."` anywhere) is *unsafe here*, because `_path_includes` reads RAW
  text and the emitted set is scanned by stages that FAIL: a doc comment reading
  `path = "spec.md"` would pull `spec.md` into `_scan_unsafe_sites` and turn the
  gate red on prose.
* **one level of inline `mod` nesting** for `N7cV`: every `mod NAME {` in a file
  is offered as a candidate prefix, filtered by `os.path.exists`. ✅ A strict
  no-op today — `grep -E '\bmod\s+\w+\s*\{'` over `patterns/**/*.rs` and
  `common/*.rs` returns nothing.
* **`N8V` stays open, named, with its reason**: the path arrives as a *macro
  argument*, so no literal ever exists in the text and no regex can see it. It
  is the `include!(concat!(...))` class, and the refusal `_check_opaque_includes`
  applies there cannot be applied here without failing the gate on every
  `macro_rules!` in the tree. Two more residuals are named beside it (inline
  `mod` nesting **deeper than one level**; `cfg` combinations `_DEP_INFO_CFGS`
  does not enumerate, inside `verus!{}`), and the docstring says all three are
  **deliberate-author** routes under `.memory/02-bench-rules.md`'s settled threat
  model. The struck `13 of 13` line is struck, not deleted.

### Acceptance — two probes, because the change has two claims

`.temp/t119/c1_union_routes.py` (`TASK_114`'s own rig, with an explicit expected
map so the file states its own verdict):

```
N7aV  verus-reads-leaf=True  dep=False  union=True   union_files=['h.rs']
N7bV  verus-reads-leaf=True  dep=False  union=True   union_files=['h.rs']
N7cV  verus-reads-leaf=True  dep=False  union=True   union_files=['x/m.rs']
N8V   verus-reads-leaf=True  dep=False  union=False  *** UNION MISSES ***
CONTROL-R5     union=True        CONTROL-plain  seen by nobody
N8 / N9-symlink  union=True (by dep-info, unchanged)

ALL ARMS AS EXPECTED: three routes closed, one residual still open by design,
both controls holding.
```

⚠ **`CONTROL-plain` is what makes this a test**: the change is an
over-approximation, and an over-approximation that answered "found" to
everything would pass every positive arm.

`.temp/t119/c2_census.py` — the no-op half, loading `git show
HEAD:harness/check.py` and running the two implementations side by side:

```
  26 patterns; distinct union results: {('.../common/driver.rs',)}
  patterns whose union MOVED vs HEAD: none
  roots that produced NO .d: 0
  MUST-FIRE (planted N7bV: new finds it, HEAD does not): FIRED
```

---

## §D — the three small ones, plus the `TASK_118` rider

### D.1 stage 9's `MISSING` fix instruction — confirmed wrong, rewritten

Verified rather than argued:

```
$ python3 harness/report.py p99
report.py: p99 matches [] in results/       (rc=1)
```

and `report.py::main` calls `load(pid)` **first**; `load` requires
`results/pNN-*.json` (measure.py's record, discriminated by a `cells` list). The
gate record is read only by `read_gate_audit`. **So on the brand-new-pattern
case the message names, the two-command loop deadlocks.**

Both the message and `check_published_tables`'s docstring now split the fix by
verdict: `STALE`/`UNPINNED` really are *gate → `report.py` → gate*; `MISSING` is
**three** commands, `measure.py pNN` first. ⚠ The docstring's summary line said
they were the same fix — `PROTOCOL.md` rule 13's shape again.

### D.2 the 33 shouts that rendered nowhere — surfaced

`report.py::shout_section` + `read_gate_loud` render the gate record's `loud`
list and any non-`FRESH` `controls_json` verdict into every published table,
**reporting-only and labelled as such**. Deduped so p23's sidecar is not printed
twice in two spellings.

All 26 tables regenerated: **19 files changed, 147 insertions, 0 deletions** —
only the 19 patterns that *have* shouts moved, the other 7 are byte-identical,
which is the check that the change is purely additive. The three biggest
families are now readable by anyone opening `results/tables/`: a `forbidden`
entry with no backticked spelling (13), a trusted item whose `requires`
constrains nothing about a parameter its body uses (12), an anti-collapse floor
far below the tightest measured cell (3).

⚠ **Ordering note, and it is verified rather than assumed:** the tables had to be
rendered **before** the sweep so stage 9 saw them. `.temp/t119/e1_gate_delta.py`
confirms **no `loud` list moved** across all 26 records, so the pre-sweep render
is correct and no re-render is owed.

### D.3 `limbs.py`'s two copied constants — imported, and the general form swept

`TWIN_PREFIX`/`TWIN_CFG` are now `_check.TWIN_PREFIX`/`_check.TWIN_CFG`, and
they matched HEAD's copies exactly before the change (verified by import against
`git show HEAD:harness/limbs.py`).

The general form, `.temp/t119/d3_copies.py` — every module-level constant of
`check.py` matched **by name and by value** against `harness/*.py`,
`synthesis/*.py`, `common/*.py`, `verus_run.py`:

```
  check.py module-level literal constants: 38 (34 non-trivial)
  == WORKING TREE ==
    harness/measure.py::VALGRIND   = expanduser('~/tools/valgrind/bin/valgrind')  AGREES
    synthesis/outward_ir.py::VALGRIND = same                                      AGREES
  == MUST-FIRE: HEAD's limbs.py ==
    TWIN_CFG / TWIN_PREFIX reported as copies -> FIRED
  working tree, limbs.py copies remaining: none
```

⚠ **The first version of that scanner reported "no copies" and was blind to
`VALGRIND`**, because `os.path.expanduser(...)` is a Call and `ast.literal_eval`
refuses it — i.e. it was itself a control that could not fire on the one case
already known by hand. Fixed, and it now reproduces `TASK_114`'s hand-found
duplicate exactly and finds nothing else.

**`VALGRIND` is LEFT, deliberately**, same call `TASK_114` made: `measure.py` is
**measurement-hashed**, so importing it costs a full re-measure for a filesystem
path that fails loudly if wrong.

### D.2 (task numbering) — the `TASK_118` rider, applied and re-tested

`git apply .temp/t118/E-check-py.diff` — both hunks, offset 67, clean. The Miri
`leak` key plus its own failure branch above the exit-code branch.

⚠ **One change I made to it, and it is a citation fix rather than a code
change.** The comment cited
`patterns/p42-goto-cleanup/controls/miri_leak_key.py`, **which does not exist** —
`TASK_118` moved the file to `.temp/` on withdrawal and this task is forbidden to
add files under `patterns/`. Rather than ship a dangling citation into
`check.py`, it now cites `.temp/t119/miri_leak_key.py` and says in the same
comment that promoting it is **one `git mv` and one `check.py p42`**
(`controls/*.py` is in the gate record's `source_sha256` and is **not** in
`measure.py::measurement_sources`). The control's `REPO`/`PDIR` now resolve from
either location, so the move needs no edit.

Re-run in full, `--old-rev HEAD`:

```
  MUTANT-A   exit=1  ub=False  leak=True
  CONTROL-B  exit=0  ub=False  leak=False
  ok  the RECORD says leak=True on the leaking rung
  ok  ub=False on the same row, so the `leak` key is NEEDED
  ok  the gate FAILS the mutant: "Miri reports a MEMORY LEAK at process exit"
  ok  the shipped rung passes with leak=False
  OLD-CODE   exit=1  ub=False  leak=<KEY ABSENT>
  ok  the old record has NO leak key and ub=False
  ok  ...and the old gate still FAILED, on the exit code
ALL ARMS BEHAVE
```

I did **not** re-land the prose; `patterns/p42-goto-cleanup/NOTES.md` 10a already
carries the finding.

---

## §E — the sweep

**Commands, in the mandated order** (`.temp/t119/sweep.out`, `sweep/<p>.log`,
`e2`…`e6` logs):

```
26 x harness/check.py                    24 PASS + 2 PASS-WITH-BLOCKED-ROWS, 0 failures
synthesis/licence.py --emit ...          51.5 s, 26 patterns, 104 pair verdicts
synthesis/synthesize.py                  78219 bytes, 565 lines
synthesis/outward_ir.py --emit ...       5m08s, 26 patterns
synthesis/synthesize.py   (again)        78240 bytes  <- the second run IS mandatory
harness/measure.py --check-stale         52 record(s) examined, 0 STALE   rc=0
```

`synthesize.py` run twice more: md5 `c0dd268d2cb2bab4bd123ed181654490` all three
times — deterministic.

**Blocked rows — both declared, both the same as HEAD:**

```
p01-array-sum      unsafe.rs on large.bin   miri did not finish within 180s
p42-goto-cleanup   unsafe.rs on large.bin   miri did not finish within 180s
```

⚠ **`p42` has ONE blocked row, not two**, and the new `seconds` key says why:
`adversarial-wincap.bin` took **74.3 s** — the fast state. I did **not** chase
it, and I claim no mechanism for why the sweep shell was fast when my
interactive one was slow. The environment beside it, for all 26 records:

```
bytes=3264  nvars=48  envp_stack_bytes=3648  repo_path_bytes=33
tuning_vars={"LD_PRELOAD": "/usr/libexec/coreutils/libstdbuf.so"}
```

### What the 26 gate records moved (`.temp/t119/e1_gate_delta.py`)

```
ADDED    386 miri leak/seconds  + 104 marginal_ir_env (26 x 4)  + 13 other
MOVED    78 source_sha256 (26 x 3 harness/*.py) + 50 marginal_ir_per_call
         + 26 marginal_ir_env (`bytes` 3269 -> 3264) + 155 other
REMOVED  5 other
`loud` lists that MOVED: NONE
```

**The 173 "other" leaves are pre-existing run-to-run nondeterminism, and that is
measured, not asserted.** They are all `adversarial.*` garbage stdout / row
grouping and `sanitizer.*.diagnostic` text. Control: re-ran `check.py p03` with
**identical code in the same shell** and diffed the two records —

```
MOVED {marginal_ir_env: 2, marginal_ir_per_call: 30, adversarial: 29,
       sanitizer: 2, miri seconds: 1}   ADDED {} REMOVED {}
```

Checked further on the two records that looked worst: p23's
`adversarial-single.bin/c-gcc` has the **identical set of diverging cells** old
and new (all four); only the grouping and the OOB garbage value moved. p03's
adversarial block has the same cell set, exits, `signal` and `hung`.

### `results/synthesis.md`: exactly 5 numbers moved, all one draw of the ±7

```
calibration   188 hit / 4 miss / 16 false alarm  ->  194 / 0 / 14
              residual median 0.30 -> 0.18   (p95 7.00, max 15.79 unchanged)
              and "⚠ Misses: p03 small/large R3-R4 -7.00, p04 ..." DISAPPEARS
band < 2.00   4 real / 139 spurious   ->   0 real / 143 spurious
band 2..16    8 real /  16 spurious   ->  10 real /  14 spurious
licence tag   179 hit / 17 false LICENSED  ->  181 / 15
p46 row       small +2076.00 (-87.00)   -> +2069.00 (-94.00)
              large +5656.10 (-121.90)  -> +5649.10 (-128.90)
```

**Why, from the sidecar rather than from the prose.** `outward_ir.json` moved
150 leaves: 78 `gate_source_sha256` plus 72 numeric on p03 (12), p04 (24),
p08 (22), p46 (14). The p03/p04/p46 moves are the memset phase term —
`outward_by_callee` `0x189480` (`__memset_avx2_unaligned_erms`) **43.0 → 50.0**,
so `p03 R3-R4 moves_by` goes **−7.0 → 0.0** and the two "misses" stop existing.
p08's 22 are sub-instruction rounding (0.00175 `Ir`/call), not the phase.
`licence.json` moved **78 leaves, all `gate_source_sha256`** — no verdict moved.

⚠ **NOT A FINDING**, as the task file predicted. And the file stays honest: the
`< 2.00` band's retraction paragraph is **unchanged** and still says `0 real`
must not be read as *"safe"* — it even states the reason this run reads 0
(*"p03's and p04's R3-R4 correction is 0.00 at 16 of 32 environment phases"*).
The 22 `‡` markers are unchanged.

---

## Problems

1. ⚠⚠ **I edited a `check.py` DOCSTRING four minutes after starting the sweep** —
   exactly what this task file forbids, and what `TASK_118` paid for. Caught
   immediately: only `p01` was in flight, `sweep.out` was still empty and
   `results/gate/` was untouched. Stopped the background task **by its task id**
   (no `pkill`), confirmed `ps -eo pid,etimes,args | grep -E "check\.py|sweep\.sh"`
   was empty and `git status --short results/gate/` showed only my earlier p47
   smoke test, then restarted clean. Cost ~4 minutes.
   **Transferable: the freeze has to include DOC edits, because `source_sha256`
   hashes the file, not the semantics.**
2. **p03's gate record was written three times** (sweep, determinism control,
   re-gate). Disclosed rather than hidden: the final one was taken through
   `.temp/t119/regate_one.sh`, the same shell shape the sweep used, and its
   `marginal_ir_per_call` is byte-identical to the sweep run. All 26 records now
   carry one `marginal_ir_env`.
3. **`miri.runs[].seconds` will churn on every re-gate.** That is deliberate and
   the comment says so; it is the only wall-clock key in the gate record, nothing
   hashes or compares it, and it is the only thing that makes the two-state Miri
   row readable.

## Unsure / not done

1. **§A's pin is still not sufficient, and I proved it rather than suspecting
   it.** `argv` beyond the repo prefix moves the marginal ±7 with all three
   fields equal. `repo_path_bytes` captures the *clone-location* term only.
   I judged that recording the whole of `argv` is wrong here — it varies **within
   a single gate run** (probe filenames differ per input), so one figure would be
   a claim about a run that did not happen. **Open, and named in the record's
   `domain` string.**
2. **No mechanism for the Miri 4.6×, and I did not look for one.** I have one
   more clean negative (`envp_stack_bytes` and its residue do not carry it) and
   two more slow ambient draws. ⚠ **Do not read arm B as evidence about what
   *does* select it.**
3. **I did not measure the Miri blast radius across the other 21 patterns**
   (`TASK_114` B2.4). The new `seconds` key now makes every sweep a free sample
   of it — this sweep's 386 recorded row-times are the first.
4. **§C's fix is latent.** All 26 patterns still return exactly
   `['common/driver.rs']`; the three closed routes do nothing today. That is the
   same "blast radius zero" `TASK_114` §C.2 asked to be read as *the limb does
   nothing yet*.
5. **I did not promote `miri_leak_key.py` into
   `patterns/p42-goto-cleanup/controls/`** — forbidden by this task. It is one
   `git mv` plus one `check.py p42`, no re-measure, and the file resolves its
   paths from either location. ⚠ **Until then the only regression control for the
   `leak` key lives in gitignored scratch.**
6. **`.memory/03-measurement.md`'s stale `< 2.00` line is still stale**
   (`TASK_114` m7a: *"120 rows, 0 real … nothing real hides below the floor"*,
   contradicted 1200 lines later in the same file). Manager-only; I did not touch
   it. ⚠ Note this run's `0 real / 143 spurious` makes the stale line look
   *more* right, which is the worst possible time for it to sit unannotated.
7. **`synthesize.py:229`, `:931` and `outward_ir.py:13`** still carry the
   pre-retraction `120 rows / 0 real` text (`:931` is the fallback that renders
   only when the sidecar is absent). Latent, not published today, not touched.
8. **I did not re-render the 26 tables after the sweep.** Justified by
   measurement — no `loud` list moved — not by assumption.

## Memory updates

**None written by me** — `.memory/`, `RECAP.md` and `results/SYNTHESIS.md` are
manager-only. Durable facts this task established, for the manager to land after
review:

* **`marginal_ir_env` now carries `nvars` / `envp_stack_bytes` /
  `repo_path_bytes` / `domain`, and the rule it licenses is NECESSARY, not
  sufficient.** `.memory/03-measurement.md`'s env-pin section says *"Fix is one
  integer"*; the fix shipped is one integer **plus the domain**, and the
  sufficiency question is **still open** with `argv` as the measured
  counterexample.
* **§B's clean negative:** `envp_stack_bytes` does **not** discriminate the p42
  Miri fast/slow state (arm B, same value, fast). ⚠ Mechanism **still OPEN**;
  this is a third dead correlation, not a third mechanism.
* **`MIRI_FLAGS = ()` stays, on a reproducibility argument, not a speed one.**
  `.memory/00-environment.md` can drop the *"the shipped design is `MIRIFLAGS`
  deliberately UNSET \[because it costs 4.6×]"* framing.
* **`miri.runs[].seconds` exists**, so *"a green Miri row is a claim about an
  unrecorded draw"* is now half-answerable from the record.
* **`.memory/02-bench-rules.md`'s known-residual list** should gain
  `_path_includes`'s three named residuals (N8V, `mod` nesting > 1 level,
  unenumerated `cfg` inside `verus!{}`).

---

⚠ **PROTOCOL rule 2's running count: 502 + 9 on this branch.** Reconciliation is
the manager's job, not mine. The nine, each with an arm that fired:

1. **The env pin was one integer short** — `3059/3059/3066/3066` reproduced at
   `bytes=3520`, old field single-valued across the split. **Fixed.**
2. **The new pin is ALSO insufficient** — `argv[1]` length moves the marginal
   ±7 with `envp_stack_bytes`, `tuning_vars` and `repo_path_bytes` all equal.
   Recorded as OPEN instead of shipping a second false "must match EXACTLY".
3. **`envp_stack_bytes` does NOT select the Miri state** — an environment with
   the slow block's exact value ran fast (74.2 s vs 368.9 s). §B's hypothesis,
   killed.
4. **`check.py` still asserted the RETRACTED `MIRIFLAGS` mechanism in four
   places**, one of them **printed on every Miri run**, while `.memory/` had
   carried the retraction since `TASK_114`.
5. **The gate's `MISSING` fix instruction cannot work** — `report.py p99` →
   `matches [] in results/`, reproduced; and `check_published_tables`'s docstring
   asserted the two failure modes had one fix.
6. **Three of `TASK_114`'s four union routes are closed** — `N7aV`/`N7bV`/`N7cV`
   found, `N8V` still missed, both controls holding, and a 26-pattern census
   proving the widening is a strict no-op.
7. **33 shouts rendered nowhere** — now in 19 tables; the other 7 are
   byte-identical, which is the arm proving the render is additive.
8. **`limbs.py`'s last two copied constants imported**, and the general-form
   scan's **first version was itself blind** to the one duplicate already known
   by hand (`VALGRIND`, via `os.path.expanduser`). Fixed before use.
9. **The `TASK_118` rider cited a file that does not exist** —
   `patterns/p42-goto-cleanup/controls/miri_leak_key.py`. Repointed at the real
   location with the promotion cost stated.

**The manager's three named doubts, answered:**

1. ⚠ **`nvars` is the right second integer AND it is not the last one.** It
   explains the measured period, it unifies both ladders under one residue, and
   holding it fixed does not close the axis — `argv` does the same ±7. The
   honest shipping decision was to state the rule as necessary-not-sufficient,
   which is what `bytes` should have said in the first place.
2. ✅ **"Stop at diagnosable" was right, and the measurement is what makes it
   right rather than obedient.** Five runs answered the one question the record
   could act on, and the answer was no — which is precisely why
   `miri.runs[].seconds` had to be unconditional rather than a derived field.
3. ⚠ **I did NOT take the "document it all" option, and the reason is not
   completeness.** Three of the four routes fall inside the design's own stated
   division of labour, in the one cell (`verus!{}`) where that division is void.
   The fourth is structurally different and is named, with two more residuals
   beside it and the threat model quoted.
