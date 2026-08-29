# TASK_142 — both residuals LANDED, and the second one's headline count was wrong

**Role: research engineer.** Only agent running. Scratch is `.temp/t142/`.
No `git add` / `git commit`. `.memory/`, `RECAP.md` and `results/SYNTHESIS.md`
untouched — every correction they need is in §6. `.temp/t136/`, `t137/`,
`t139/`, `t140/`, `t141/` were **read only**, never written; `git status` never
showed a file under any of them.

> ## ⚠⚠ READ THIS FIRST — THE COUNT IN BOTH RESIDUALS WAS WRONG, IN OPPOSITE DIRECTIONS
>
> **Residual 2's *"EIGHT committed control files"* is TEN.** `TASK_141`'s own
> §3 table **lists ten files** under a header that says eight, and the header
> is what `RECAP`'s START HERE box and this task file both copied. PROTOCOL
> rule 13, verbatim: *only the body gets maintained.* Re-derived by measurement
> (`.temp/t142/census_controls.py`), not by reading:
>
> ```
> committed patterns/*/controls/*                 115   (22 patterns)
>   96 .py   10 .sh   6 .json   1 .rs   1 .log   1 .c
>
> in the GATE digest        96 / 115      (every .py, and only the .py)
> in a MEASUREMENT record    0 / 115      <- 27 records, re-verified
> in NO digest at all       17            of which
>     6 .json + 1 .log  -- self-describing, stage 9b reads their own pins
>    10 CONTROL SOURCES -- in nothing, and THAT is the class
> ```
>
> **The ten**: `build_controls.sh` ×4 (p06, p14, p18, **p27**),
> `verify_controls.sh` ×3 (p06, p14, p18), and p42's `affine_leak.rs`,
> `leak.sh`, `miri_seeds.sh`. `p27`'s is the one every prose list drops — it is
> cited by no `.md` anywhere, only by two `.py` generators.
>
> **And `TASK_141`'s ~40-minute cost estimate for residual 1 was wrong by a
> factor of ~25 in the OTHER direction.** It budgeted *"a Verus mutant battery
> + Miri"* at ~20–25 min and ~15 min respectively. **Measured, on the edited
> tree: `proof_mutants.py` 51.4 s for all ten Verus runs, `miri_arms.py` 1.6 s
> for all eight Miri runs.** The whole sidecar half of residual 1 is **53
> seconds**. The real cost is the re-measure and the re-gates, which the
> estimate treated as the cheap half.

---

## VERDICT IN ONE SCREEN

| residual | state |
|---|---|
| **1 — the retracted claim in `p29`'s `.rs` rung sources** | ✅ **LANDED in all four** (`unsafe.rs`, `verus.rs` ×3 sites, `safe_naive.rs`, `safe_tuned.rs` — the task file and `TASK_141` §2c both say *"three"* in the header and list four in the body). Comment-only, verified line by line. Both pinned sidecars regenerated (`miri_arms.json`, `proof_mutants.json` — **one leaf moved in each, the pin**), `p29` re-measured (**6 m 20 s**) and re-gated **`PASS`, `failures: []`, `blocked: []`**. §1. |
| **2 — control files in no digest** | ✅ **LANDED, and it is TEN files, not eight.** `check.py`'s gate glob `controls/*.py` → `controls/*` minus `.json`/`.log`. Chosen over the two alternatives **with the reason stated** (§2b), with a **must-fire arm on the real `check_stale` reader** (§2c), and paid for with a full 27-pattern sweep. §2. |
| **the sweep** | §3 |
| **Running count** | base **695**, branch delta, sum: §7 |

---

## 1 — RESIDUAL 1: THE CLAIM IS OUT OF EVERY RUNG SOURCE

### 1a. The six sites, and the two I left alone on purpose

`.temp/t142/apply_rs.py` — six exact-match substitutions, each asserted
**unique** in its file, `--check` first, and **idempotent by construction**:
every site tests `new in text` *before* looking for `old`, which is the trap
`TASK_141`'s equivalent script fell into and caught by running it twice.
Verified the same way: a second real run reports `0 applied, 6 already applied`
and `git status` shows no new modification.

| file | what it said | what it says now |
|---|---|---|
| `unsafe.rs` SAFETY (5) | *"**This is the obligation p29 is about and it takes TWO conjuncts**"* | *"…and **ONE SOURCE LINE CARRIES TWO BUG CLASSES SELECTED BY THE INPUT**"*, with the free/recycle split named per half, *"the half every detector sees is the half that CANNOT BE GATED"*, and the retraction with its evidence |
| `verus.rs` header (TCB) | *"**the second obligation costs none of them**"* | *"**the OCCUPANT-IDENTITY TEST costs none of them**"* — the same repair `TASK_141` §6 asks the manager to make in `.memory/06-catalogue.md` clause 5 |
| `verus.rs` `del_walk` doc | *"the whole reason `p29`'s safety line **needs a second conjunct**"* | *"…**cannot be a LIVENESS TEST ALONE**"*, named as the use-after-recycle half, plus *"how many conjuncts it takes is a SPELLING question and the answer is ONE"* |
| `verus.rs` `rec_free` | *"why the safety line **has a second conjunct** that has nothing to do with linearity"* | *"carries an **OCCUPANT-IDENTITY TEST** that has nothing to do with linearity"*, + second-conjunct-vs-widened-`live[]` is a choice |
| `safe_naive.rs` splice | *"why the safety line below **needs a second conjunct**"* | *"…**cannot be the discriminant alone**"* + the occupant test is what is needed |
| `safe_tuned.rs` splice | *"why the safety line below **needs its second conjunct**"* | same |

⚠ **Two sites were deliberately NOT touched, and they are the ones a reader
might expect to be:**

- **`safe_naive.rs`'s header items 1 and 2** (*"the first conjunct … is written
  by the language"* / *"**The second conjunct is not.**"*) and
  **`safe_tuned.rs:21`** (*"the SAFETY LINE is still the same two conjuncts"*).
  These describe **what this rung spells**, which is true and is the thing the
  file is documenting. The retracted claim was about what the PROPERTY needs.
- **`unsafe.rs:351` / `safe_naive.rs:232` / `verus.rs:1314`**, all
  *"THE SAFETY LINE. c/kernel.c omits both conjuncts."* Also true of the shipped
  spelling, and `spec.md`'s `idiom.c` pins that exact two-conjunct line.

⚠ **`spec.md` was not touched and did not need to be** — `TASK_141` already
carries the retraction inside the hashed `why` and in the `idiom` note.
`contract_sha256` is **unchanged at `a7249f0d60f3…`**, which is the point: this
was a rung-source repair, not a contract move.

### 1b. THE ACCEPTANCE TEST, AND I MADE IT ABLE TO FAIL BEFORE BELIEVING IT

`.temp/t142/leafdiff.py` classifies every moved leaf. **Measurement record,
against `git show HEAD:results/p29-bst-delete.json`:**

```
leaves: 1345   moved: 103
     96  wall-clock
      3  timestamp / git
      4  source hash   (safe_naive.rs safe_tuned.rs unsafe.rs verus.rs)
      0  Ir      0  md5/static      0  checksum
```

`TASK_141` saw **102** with three `c/*` hashes; this is **103** with four `.rs`
hashes, and the other 99 are the same two classes. ⚠ **The record carries no
`discarded` field, so this is DERIVED and not read: over both records' 32
wall-clock cells, `spread_pct` never reaches 10%** — max **2.94 %** before and
**3.61 %** after, `0` cells over 10% either side. The box was kept quiet for
the whole 6 m 20 s and this was checked afterwards rather than assumed.

⚠⚠ **The `0 Ir / 0 md5 / 0 identity` line is only worth something if the
classifier can SEE those leaves, so I measured that too** — `.memory/`'s own
*"before believing a check, ask what would make it FAIL"*:

```
classifier over the WHOLE measurement record : Ir 201   md5/static 320
                                               checksum 64   identity 0
classifier over the WHOLE gate record        : Ir 104   md5/static 6
                                               identity 29   checksum 0
```

⚠ **So `identity: 0 moved` is VACUOUS on the measurement record** — identity
lives in the gate record. Checked there instead: **gate record, 1608 leaves, the
two `identity` rows are `('unsafe vs verus','O0','differ')` and
`('unsafe vs verus','O3','norel')`, unmoved, and all 29 identity leaves and all
6 `md5_fn_*` leaves are unmoved.**

**The gate record moved 67 leaves and every one is in the task file's own
not-reproducible list:**

```
  4  source hash            the four .rs
  2  "Ir"-classified        marginal_ir_env/{bytes 3264->3280,
                            envp_stack_bytes 3648->3664}
 61  adversarial group ordering + the buggy C rung's per-input stdout
```

⚠ **The two `marginal_ir_env` leaves are BYTE COUNTS OF THE ENVIRONMENT, not
instruction counts** — my classifier bins them under `Ir` because the path
contains `ir`, and the honest reading is that the shell environment grew 16
bytes between the two runs. ✅ **`marginal_ir_per_call` is byte-identical**,
which is the leaf that would have meant something.

### 1c. THE SIDECARS, AND `TASK_141`'s COST ESTIMATE

Both regenerated by their own `pin.regenerate` command on the edited tree.

```
proof_mutants.py   real 0m51.444s   10 of 10 behaved as expected
                   M0-control verify 25/0 ; M2b precondition ; M3b assertion ;
                   M6-constant-body FAILS (vacuity)
                   114 leaves, 1 moved: the verus.rs pin
miri_arms.py       real 0m1.632s    8 runs
                   shipped: no UB on all four inputs
                   r1line : UB on adversarial-uaf and adversarial-succ,
                            NO UB on adversarial-recycle  <- the row's point
                   64 leaves, 1 moved: the unsafe.rs pin
```

⚠⚠ **Every measured cell of both batteries is byte-identical across the edit,
including Miri's `alloc1954` / `alloc1994` allocation IDs.** So unlike `p29`'s
`arms.json` (`.memory/03-measurement.md` entry 18), these two sidecars ARE
reproducible on this box — a useful counterpoint to that entry rather than a
contradiction of it: neither battery reads memory the program does not own.

### 1d. The two gate runs, and why there were two

`harness/check.py p29` after `report.py p29` returned **`FAIL`, one failure,
`[tables]` STALE-CONTENT, 2 lines** — and that is **correct behaviour of
`TASK_141`'s repair working as designed**, not a regression. `report.py` reads
the *previous* gate record; the previous record predated the sidecar
regeneration and the re-measure, so the table it rendered differed from what
the new run computes. Stage 9c now compares against the record **this** run
writes, so it saw it. Repair is the documented two commands:

```
harness/report.py p29 ; harness/check.py p29
   -> PASS   failures []   blocked []
      table_render  FRESH   render == published == 0d005a5fcb18e3ea
      controls_json arms/miri_arms/proof_mutants/repro : all FRESH
      verus 25 verified / 0 errors, tcb_items 7
      contract_sha256 a7249f0d60f3… (UNMOVED)
harness/measure.py --check-stale -> 54 record(s) examined, 0 STALE
```

⚠⚠ **AND I WALKED INTO THE READ-A-STALE-RECORD TRAP MYSELF, IN THIS TASK,
WHILE HOLDING THE RULE IN MY HEAD — disclosed because the mechanism is new.**
I waited for the first gate with `until grep -qE 'real\s' <log>`, intending to
match `time`'s `real 6m53s`. **`grep` matched `ok f: real call site found` at
line 75**, so I read `results/gate/p29-bst-delete.json` while `check.py` was
still running and reported `verdict: PASS` off the **previous** run's record.
Caught by noticing that the record's `unsafe.rs` hash was still the pre-edit
`e1f1669c…`. **This is `.memory/03-measurement.md`'s *"a number grepped out of
a log is not a number read out of a record"* and entry 15's *"ask WHICH RUN
wrote the record you are reading"* — combined, on the reader's side, in a wait
condition rather than in a check.** The fix that worked: wait on the **PID**
(`while ps -p <pid>; do sleep 20; done`), never on log text.

---

## 2 — RESIDUAL 2: THE LIST, THE EXPOSURE, THE DECISION, AND THE ARM

### 2a. The census, re-derived — and the count is TEN

`.temp/t142/census_controls.py`. It asks one question per committed file under
`patterns/*/controls/`: is this path a key in any gate record's
`source_sha256`, in any measurement record's `source_sha256`, or in any
committed sidecar's `derived_from_sha256`? ⚠ **`--head` reads the gate records
out of `git show HEAD:` rather than off disk, so the BEFORE arm survives the
sweep that rewrote all 27 records** (`.temp/t142/census-head.txt`).

```
committed patterns/*/controls/*   115 across 22 patterns
   96 .py   10 .sh   6 .json   1 .rs   1 .log   1 .c

BEFORE (HEAD's records)
  gate source_sha256           96 / 115   <- every .py, and ONLY the .py
  measurement source_sha256     0 / 115   <- 27 records
  in no digest at all          17
```

The 17 split cleanly and the split is the whole point:

| files | covered by | verdict |
|---|---|---|
| 6 `.json` sidecars | their own `derived_from_sha256`, re-hashed by stage 9b every run | ✅ **not the class** — these are self-describing OUTPUTS |
| `p23/controls/controls.log` | named by `controls_pin.json`'s `pins`, and its `not_covered` says it is deliberately NOT hashed (ASLR addresses, PIDs, BuildIds, absolute paths) | ✅ **declared, not silent** |
| **10 control SOURCES** | **nothing** | ⚠⚠ **the class** |

**The ten**, and `TASK_141` §3 lists exactly these ten under a header that says
eight:

```
p06 build_controls.sh  verify_controls.sh
p14 build_controls.sh  verify_controls.sh
p18 build_controls.sh  verify_controls.sh
p27 build_controls.sh
p42 affine_leak.rs  leak.sh  miri_seeds.sh
```

⚠ **`p27/controls/build_controls.sh` is the one that falls out of every prose
list, including `RECAP`'s.** It is cited by **no `.md` in the repo** — only by
`ir_table.py` and `gotresolve.py`, both of which are hashed, so the *invocation*
is pinned and the **flag string it invokes with is not**.

⚠ **Where the `8` most likely came from, offered as a lead rather than a
finding:** `.memory/05-layout.md`'s `p23`-deviation entry records the tree as
*"92 files across 24 patterns … **87 `.py` + 8 `.sh`**"*. That was true when it
was written; today it is **115 across 22 patterns: 96 `.py`, 10 `.sh`, 6
`.json`, 1 `.rs`, 1 `.log`, 1 `.c`**. An `8` in the authoritative layer, a
different `8` in a report header, and the same `8` copied into `RECAP` and into
this task file.

### 2b. The exposure — which published prose depends on them

Every one of the ten is either **the flag string a published control number was
taken at** or **the runner whose behavioural table `NOTES.md` transcribes**:

| file(s) | what depends on it |
|---|---|
| `p42/leak.sh` | `NOTES.md` §3's **352 points** = 2 kernels × 4 opt levels × 44 inputs, and the LSan-specifically grep the gate's coarse `"fires"` obligation cannot do (§2 quotes the gate's own predicate). Cited in `README.md`, `spec.md`, **`results/tables/p42-goto-cleanup.md`**, `.memory/` 00/01/02/06 and `RECAP.md` |
| `p42/miri_seeds.sh` | `NOTES.md` §11c's **seeds 0–7 over nine inputs, no UB no leak**, the `large.bin` BLOCKED row, and the **must-fire positive control table** (`rc=1 miri-leak=YES` ×3). Cited in `.memory/03-measurement.md` entry 16 |
| `p42/affine_leak.rs` | `README.md`'s *"bare `Tracked<Dealloc>` … `2 verified, 0 errors`"*, in `spec.md`, in **`results/tables/p42-goto-cleanup.md`**, in `.memory/04-verus.md` and `.memory/06-catalogue.md` |
| `p06`/`p14`/`p18`/`p27` `build_controls.sh` | each carries, in its own header AND its own `RUSTC`/`CC` lines, the flags the pattern's control cells were built at — *"A control built at other flags is not on the same axis as the cells it is compared with"* is `p14`'s and `p18`'s own wording. `p18`'s also builds `O0d`/`O3d`, the axes `NOTES.md` §7/§9/§10 price |
| `p06`/`p14`/`p18` `verify_controls.sh` | `p06/NOTES.md`'s two-run mutant verdict table, `p14/NOTES.md` §12's model checksums over eight matrix inputs, `p18/NOTES.md` §7/§10's delete-the-check and Verus-mutant rows |

⚠ **And the accident has already happened once inside this very family.**
`TASK_109`/`TASK_110` found `leak.sh` publishing **88** in its header comment,
in its own success message and in `p42/README.md` when the loop produces
**352**. That one was caught by a review, not by a hash — but it is the
existence proof that these files drift, and the threat model
(`.memory/02-bench-rules.md`) asks exactly *could this happen by accident?*
Here it did.

### 2c. THE DECISION, AND WHY IT IS NOT THE ONE THE TASK FILE LEANS TOWARDS

**Landed: widen the gate's control glob from `controls/*.py` to
`controls/*` MINUS `.json` and `.log`.** One expression in
`harness/check.py::main`'s `srcs` list, plus the comment block that justifies it
and a correction to `check_control_json_pins`'s docstring, which asserted the
old glob.

```python
-                  + glob.glob(os.path.join(pdir, "controls", "*.py"))
+                  + [p for p in glob.glob(os.path.join(pdir, "controls", "*"))
+                     if not p.endswith((".json", ".log"))]
```

**Why this and not a `derived_from_sha256` sidecar per pattern** (the task
file's middle option, and the cheaper one at ~33 min of gate runs against a
~65-minute sweep):

1. ⚠⚠ **The project has already adjudicated the principle, and the glob
   contradicts it.** `.memory/05-layout.md`'s ruling on the `p23` deviation:
   *"**The convention was never 'Python only', it was 'a generator, not an
   artefact'**, and a `.c` a script compiles is a generator's input."*
   `check.py`'s own comment on the line calls it *"committed control
   **generators**"*. **The `.py` filter was never a design decision** — it was
   the extension that happened to exist when the line was written, and it
   under-delivered against its own stated rule the moment a `.sh` arrived.
2. **A sidecar does not generalise and this failure mode is exactly
   non-generalisation.** Five hand-written pin files cover ten files today and
   say nothing about the eleventh. The glob covers the eleventh on arrival —
   including a `.cpp`, a `Makefile` or a `.sh` in a pattern that does not exist
   yet, because the rule is now *everything except the two output extensions*
   rather than *one whitelisted source extension*.
3. **The price is the same price ANY gate change costs.** `harness/*.py` is in
   every gate record's `source_sha256`, so a one-character edit to `check.py`
   already stales all 27 records. There is no cheaper spelling of a gate change,
   and the sidecar option's saving is real only because it avoids touching
   `check.py` at all.
4. **The task file's objection — *"pulls those files into a hash that fires on
   comment edits"* — is true and is not new.** A comment edit in any of the 96
   `controls/*.py` already costs that pattern one gate re-run today, and the
   project accepts it. The ten `.sh`/`.c`/`.rs` are the same kind of file.

**Why `.json` and `.log` are EXCLUDED, which is the part I would defend
hardest:**

⚠⚠ **They are control OUTPUTS, and stage 9b is the mechanism built for
outputs.** Putting a generated sidecar into `source_sha256` puts a file that
*this run's own stage 9b evaluates* inside the digest that certifies the run.
Today that is merely noisy — all six sidecars use `derived_from_sha256`, which
is path-local. **But stage 9b still accepts a second key,
`gate_source_sha256`** (`synthesis/licence.json`'s shape, kept deliberately for
a sidecar that derives from the whole gate record), **and for such a sidecar the
combination is an unreachable fixpoint**: writing the sidecar moves
`source_sha256`, so the value it must record can never equal the value the next
run computes. The hazard is one sidecar away, and a blanket `controls/*` would
build it in. `p23/controls.log` is out for that reason **plus its own** — its
`controls_pin.json` declares it un-hashable because it embeds ASLR addresses,
PIDs, BuildIds and absolute repo paths.

⚠ **What the change does NOT buy, said plainly:** a green `source_sha256` proves
the script has not moved since the record was written. It does **not** make the
numbers those scripts print reproducible (`.memory/03-measurement.md` entry 18),
and it would **not** have caught the `88`-vs-`352` defect, which was a script
self-consistent with its own hash. It closes *edited and not re-run*, which is a
different and real accident.

### 2d. THE MUST-FIRE ARM — driven against the real reader, not a model

`.temp/t142/arm_glob.py`. Three arms, all through
`harness/measure.py --check-stale`, which is the actual reader of
`source_sha256`; the perturbation is one appended comment line, removed in a
`finally:`, and the arm prints `git status` for both touched paths so a leftover
is visible rather than silent. ⚠ The gate record is stashed and restored **as
raw bytes**, not re-serialised, because stage 9c compares bytes.

**Run on three files spanning all three orphan extensions. `ARM: PASS` each
time, `rc=0`:**

```
p18-varint-shift / controls/verify_controls.sh        (.sh)
  in HEAD's gate source_sha256 : False
  in TREE's gate source_sha256 : True
  CTL  nothing perturbed        FRESH  44 source(s)              must NOT fire
  NEW  perturbed                STALE  ...verify_controls.sh     FIRED
  OLD  HEAD's record, perturbed STALE  harness/check.py ONLY     BLIND

p42-goto-cleanup / controls/leak.sh                   (.sh, publishes numbers)
  CTL  FRESH 42 source(s)   NEW  STALE ...leak.sh   OLD  BLIND
p42-goto-cleanup / controls/affine_leak.rs            (.rs)
  CTL  FRESH                NEW  STALE ...affine_leak.rs   OLD  BLIND
```

⚠ **DISCLOSED CONFOUND in the OLD arm, because it would otherwise read
stronger than it is:** HEAD's record is *also* stale on `harness/check.py`,
since this task edited that file — so the OLD arm does not print a clean
`FRESH`. What it proves is the thing that matters and the arm tests exactly
that: **HEAD's record does not contain the perturbed path at all**
(`in HEAD's … source_sha256 : False`, printed first), so no edit to it could
ever have been seen. The one `STALE` it does print names a different file.

⚠ Every arm restores both touched paths in a `finally:` and prints
`git status` for them; after all three, `git status --porcelain patterns/`
shows only the six intended `p29` modifications.

---

## 3 — THE SWEEP

**27 patterns, every record written by a full non-`--skip` run.** Read out of
`results/gate/*.json` key by key, **never grepped** — `grep -c BLOCKED` matches
the verdict string `PASS-WITH-BLOCKED-ROWS` and decodes as `2N+1`.

```
records         27
verdicts        PASS 25   PASS-WITH-BLOCKED-ROWS 2
failures        0 on every pattern
blocked rows    p01 = 1   p42 = 1   every other pattern = 0   (total 2)
stage 9         FRESH 27/27
stage 9c        FRESH 27/27
```

⚠ **`p42` came back at 1, not 2** — the committed state, and the task file's
note that 2 is also legitimate did not need to be used.

✅ **The sweep is its own must-not-fire arm for the glob change**: `source_sha256`
is not one of the four keys `report.py` reads, so moving all 27 of them should
change no published table — and **stage 9c is `FRESH` 27/27**, plus all 27 tables
re-rendered through `report.py` and diffed against the committed files:
**27 checked, 0 differ.**

**Timings**, `.temp/t142/sweep/rc.txt`, `rc=0` on all 27:

```
p01 339  p02 111  p03  93  p04  95  p05  85  p06 126  p07  88
p08 130  p09  95  p10  81  p11  85  p12 104  p13 108  p14 123
p16  89  p17 101  p18  77  p19  89  p22 303  p23 107  p27 205
p29 412  p36  95  p38  96  p42 447  p46 105  p47  79
                                        total 3868 s = 64.5 min
```

⚠ **DISCLOSED: the sweep ran in two pieces and neither break was mine.** The
harness stopped the background wrapper after `p38` (24 of 27 complete);
`CLAUDE.md` constraint 2 was not touched and nothing was killed by me. **Nothing
is lost or double-counted, and this time that is structural rather than
reconstructed**: `.temp/t142/sweep.py` **skips a pattern whose gate record
already carries this `check.py`'s sha256**, so resuming is one command and
`--status` reports what is left. `p42` had been interrupted mid-run and its
record still carried the OLD hash, so it was re-run from scratch. `--status`
now reports `remaining 0`.

### 3a. What the change actually did to the digests

```
                       BEFORE (git show HEAD:)      AFTER (this tree)
controls/* in gate         96 / 115                    108 / 115
controls/* in measurement   0 / 115                      0 / 115   (unchanged)
in NO digest at all        17                            7
   of which control SOURCES 10                           0   <- the residual
   of which self-describing  7                           7   <- 6 .json + the .log
```

⚠ **Checked and NOT a problem: `__pycache__`.** Twelve patterns have a
`controls/__pycache__/` directory on disk, which `controls/*` matches.
`source_sha` filters on `os.path.isfile`, so directories are dropped —
verified in the records: **0 `__pycache__` entries across all 27**. There is no
other non-source file on disk under any `controls/`.

---

## 4 — THE FINISHING CHECKS

```
harness/measure.py --check-stale       54 record(s) examined, 0 STALE
harness/tools/composition.py --check   OK: published composition table matches
                                       the tree (27 patterns, 10 classes)
harness/tools/temp_citations.py        OK  (new=0 unclassified=0 resolved=0)
synthesis/licence.py --emit synthesis/licence.json
                                       27 patterns, 108 pair verdicts, 53.2 s
python3 synthesis/synthesize.py        wrote results/synthesis.md
                                       79259 bytes, 578 lines
                                       494706bbf6bb -> 52a3549419fc
                                       `Patterns: 27`, 14 occurrences of `p29`
                                       `LICENCE STALE` appears ONCE and it is
                                       the paragraph explaining the mechanism
all 27 published tables re-rendered    27 checked, 0 differ
```

⚠ **`licence.py --emit synthesis/licence.json` with the PATH, and AFTER the
sweep** — `licence.json` pins the gate `source_sha256` per pattern, this task
moved all 27, and bare `--emit` exits `rc=2` writing nothing (`RECAP` 46).

✅ **`results/SYNTHESIS.md` (CAPITALS) was never opened for writing.** Belt and
braces: its md5 was taken before `synthesize.py` and re-checked after
(`md5sum -c` → `OK`), and `git diff --stat results/SYNTHESIS.md` is empty.

---

## 5 — CLEAN NEGATIVES: named attacks that did NOT land

1. **"The rung-source edits changed code, not comments."** No.
   `git diff -U0 -- patterns/p29-bst-delete/*.rs`, every `+`/`-` line filtered
   against `^[+-]\s*(//|/\*|\*)`: **0 non-comment lines**, 38 insertions and 12
   deletions, all comment.
2. **"The comment edits broke the proof."** No. `proof_mutants.py`'s
   `M0-control` — the shipped file through the same harness — verifies
   **`25 / 0`**, and the gate's own stage 5 agrees (`verus 25 verified, 0
   errors`, `tcb_items 7`).
3. **"The re-measure moved a published number."** No. **0 `Ir`, 0 md5/static,
   0 checksum out of 1345 leaves**, and `marginal_ir_per_call` in the gate
   record is byte-identical. The only `Ir`-shaped movers are the two
   `marginal_ir_env` **byte counts** (§1b).
4. **"`identity` did not move, so the identity pin is fine."** ⚠ **The
   measurement-record form of that claim is VACUOUS and I nearly published
   it** — `identity` has **0 leaves** there. It is checked in the gate record
   (29 leaves, unmoved, `O0 differ` / `O3 norel`).
5. **"The `arms.json` draw (`.memory/03-measurement.md` entry 18) will make the
   other two sidecars irreproducible too."** No. `proof_mutants.json` and
   `miri_arms.json` regenerated with **exactly one moved leaf each — the pin
   itself** — including Miri's allocation IDs. Entry 18's rule holds and is
   narrower than it might read: it is about arms that **read memory the program
   does not own**, and neither of these does.
6. **"`spec.md` still carries the retracted sentence, so the contract has to
   move again."** No. `TASK_141` already struck it inside the hashed `why` and
   annotated the `idiom` note; `contract_sha256` is unchanged at
   `a7249f0d60f3…` before and after this task.
7. **"Any sidecar under `controls/` is already covered because stage 9b reads
   it."** No — 9b reads a sidecar's `derived_from_sha256` and re-hashes the
   paths it names. It says nothing about a `.sh` that no sidecar names, which is
   all ten of them.
8. **"`p23`'s `guard_variants.c` and `run.sh` were already covered, so the glob
   change is redundant for them."** They were — by `controls_pin.json`. The
   glob now covers them **as well**, which is double coverage and harmless: one
   pin proves the log was derived from them, the other proves the gate record
   was.

---

## 6 — FOR THE MANAGER: everything in a file I may not edit

Nothing below was touched by me. Each is either falsified by a measurement in
this task or made stale by it.

| file | what is wrong | the correction |
|---|---|---|
| `RECAP.md` START HERE, `Do this next`, item **(1)** | *"THREE `.rs` RUNG SOURCES IN `p29` STILL CARRY THE RETRACTED CONJUNCT-COUNT SENTENCE"* + *"Cost: … ~40 min"* | **FOUR** sources, **six** sites — and the whole thing is **DONE**. The measured cost was `proof_mutants.py` **51 s**, `miri_arms.py` **1.6 s**, re-measure **6 m 20 s**, two gate runs **≈ 14 min**. The mutant battery, which the estimate called the expensive half, is **~1.4 % of it** |
| `RECAP.md` START HERE, `Do this next`, item **(2)** | *"**EIGHT** committed control files (`*.sh`/`*.c`/`*.rs`) are in NO DIGEST AT ALL"* | **TEN.** `TASK_141` §3's own table lists ten under a header saying eight — PROTOCOL rule 13. And it is **DONE**: `check.py`'s glob now covers all ten (§2c) |
| `.memory/05-layout.md` ~636 | *"the other **92** files across **24** patterns are **87 `.py` + 8 `.sh`**"* | **115 files across 22 patterns: 96 `.py`, 10 `.sh`, 6 `.json`, 1 `.rs`, 1 `.log`, 1 `.c`.** `git ls-files 'patterns/*/controls/*' \| sed 's/.*\.//' \| sort \| uniq -c` |
| `.memory/05-layout.md` 722–726 | *"STILL UNPINNED: 21 `controls/*.py` sidecars … **because the glob is `controls/*.py`**"* | The item is already retired (`TASK_141`); **the parenthetical reason is now also false** — the glob is `controls/*` minus `.json`/`.log` |
| `.memory/05-layout.md` 639–642 | ✅ **nothing wrong — it is the AUTHORITY for this task's change** and deserves a forward pointer: *"the convention was never 'Python only', it was 'a generator, not an artefact'"* is exactly what the `.py` glob violated for 10 files and ~40 tasks |
| `.memory/02-bench-rules.md` ~214 | *"The glob also gained `patterns/*/controls/*.py`"* | historical, but worth a `→ now `controls/*` minus `.json`/`.log` (TASK_142)` |
| `.memory/03-measurement.md` entry **15** | still open per `TASK_141` §6; **and this task supplies a second, independent instance from the READER's side** — see the running-count item on the `grep -qE 'real\s'` wait condition |
| `.memory/03-measurement.md` entry **18** | ✅ stands, and now has a **negative control**: `proof_mutants.json` and `miri_arms.json` regenerate with one moved leaf each (the pin). The rule's scope — *arms that read memory the program does not own* — is confirmed rather than weakened |
| `.memory/06-catalogue.md` line 381 clause 5 | *"TCB 7 — THE SECOND CONJUNCT COSTS NONE OF THEM"* (`TASK_141` §6 already asks for this) | ✅ **`verus.rs`'s header now reads the corrected form** — *"the OCCUPANT-IDENTITY TEST costs none of them"* — so the catalogue can copy the shipped wording verbatim |
| `CLAUDE.md`, the `harness/` bullet | unaffected by this change, but note `check.py`'s digest description now differs from any prose that says `controls/*.py` | — |

⚠ **One substantive item for `.memory/05-layout.md`, and it is the reason the
glob excludes two extensions rather than none:** stage 9b accepts
`gate_source_sha256` as well as `derived_from_sha256`. **A sidecar that used the
former AND sat inside `source_sha256` would be an unreachable fixpoint** —
writing it moves the digest it must equal. No sidecar uses that key today (6 of
6 use `derived_from_sha256`; `gate_source_sha256` appears only in
`synthesis/licence.json` and `synthesis/outward_ir.json`), so this is a hazard
that was one sidecar away and is now designed out. **The general rule: a digest
of INPUTS must not contain a file the same run's own stages EVALUATE.**

---

## 7 — PROTOCOL rule 2 running count

Base **695** (as given by the task file). Branch delta **+9**:

0. ✅ **Residual 1 is LANDED in all FOUR rung sources across SIX sites, and the
   acceptance test came out exactly as the task file predicted**: **103 of 1345
   leaves moved — 96 wall-clock, 3 timestamp/git, 4 source hashes, and ZERO
   `Ir`, md5/static or checksum** — with `identity` checked in the **gate**
   record (29 leaves, unmoved) because the measurement record has none.
   `contract_sha256` did not move.
1. ⚠⚠ **`TASK_141`'s ~40-minute cost for residual 1 is wrong by ~25×, and in
   the direction that made the repair look unaffordable.** Measured on the
   edited tree: **`proof_mutants.py` 51.4 s** against an estimated 20–25 min,
   **`miri_arms.py` 1.6 s** against an estimated ~15 min. The estimate named the
   Verus mutant battery as the expensive half; it is **1.4 %** of the total. The
   expensive half was the two gate runs, which the estimate called cheap.
   ⚠ **This is the project's own *"before quoting a cost, measure it"* broken
   again** — `.memory/05-layout.md` already records `sweep_fit.json`'s
   *"~30 minutes"* that measured **47 s** and shaped a task file the same way.
2. ⚠⚠ **"EIGHT committed control files in no digest" is TEN, and the eight is a
   PROTOCOL rule 13 header over a body that already listed ten.** `TASK_141`
   §3's own table names all ten; `RECAP`'s START HERE box and this task file
   both copied the header. **`p27/controls/build_controls.sh` is the one every
   prose list drops** — it is cited by no `.md` in the repo, only by two hashed
   `.py` generators, so the invocation is pinned and the flag string it invokes
   with was not.
3. ✅ **The fix is a glob whose EXTENSION FILTER was the accident, and
   `.memory/` had already adjudicated it in as many words.**
   `.memory/05-layout.md` on the `p23` deviation: *"**the convention was never
   'Python only', it was 'a generator, not an artefact'**"*, and `check.py`'s
   own comment on the line says *"committed control **generators**"*. The `.py`
   whitelist contradicted the project's written rule for ten files, and it
   under-delivered against that rule from the first `.sh` onwards.
4. ⚠⚠ **A DIGEST OF INPUTS MUST NOT CONTAIN A FILE THE SAME RUN'S OWN STAGES
   EVALUATE** — the reason the new glob excludes `.json`/`.log` rather than
   being a blanket `controls/*`. Stage 9b accepts `gate_source_sha256` as well
   as `derived_from_sha256`, and **a sidecar using the former from inside
   `source_sha256` is an unreachable fixpoint**: writing it moves the digest it
   must equal. Measured: **0 of 6** committed sidecars use that key today, so
   the hazard was one sidecar away and is now designed out rather than
   discovered.
5. ⚠⚠ **I WALKED INTO THE STALE-RECORD TRAP MYSELF, IN THIS TASK, AND THE
   ARTEFACT WAS IN A WAIT CONDITION RATHER THAN IN A COUNT.**
   `until grep -qE 'real\s' <gate.log>` was meant to match `time`'s `real
   6m53s`; it matched **`ok f: real call site found` at line 75**, so I read
   `results/gate/p29-bst-delete.json` while `check.py` was still running and
   reported `verdict: PASS` off the **previous** run's record. Caught only
   because the record's `unsafe.rs` hash was still the pre-edit `e1f1669c…`.
   ⚠ **This is `.memory/03-measurement.md`'s *"a number grepped out of a log is
   not a number read out of a record"* and entry 15's *"ask WHICH RUN wrote the
   record"* combining in a new place: the grep artefact decided WHEN to read,
   not WHAT was read.** The wait that works is on the **PID**, never on log
   text.
6. ✅ **A negative control for `.memory/03-measurement.md` entry 18.**
   `proof_mutants.json` and `miri_arms.json` regenerated on the edited tree with
   **exactly one moved leaf each — the pin itself** — including Miri's
   `alloc1954`/`alloc1994` allocation IDs. So entry 18's *"a `derived_from_sha256`
   that re-hashes clean does not make the numbers reproducible"* is confirmed as
   **scoped to arms that read memory the program does not own**, rather than
   being a general property of sidecars.
7. ⚠ **AN ACCEPTANCE TEST CAN BE VACUOUS IN EXACTLY THE LEAF CLASS IT IS ABOUT,
   AND I NEARLY PUBLISHED ONE.** *"0 identity leaves moved"* in the measurement
   record is true and empty — that record contains **0 identity leaves**; they
   live in the gate record. Found by making the classifier print its histogram
   over the whole record before believing its diff (`Ir 201`, `md5 320`,
   `checksum 64`, `identity 0`). ⚠ **And two of the leaves it binned as `Ir` are
   `marginal_ir_env/{bytes, envp_stack_bytes}` — BYTE COUNTS OF THE
   ENVIRONMENT, not instruction counts.** `marginal_ir_per_call` is
   byte-identical.
8. ✅ **A sweep should be RESUMABLE BY CONSTRUCTION, not argued safe
   afterwards.** `TASK_141`'s sweep was stopped three times and its report had
   to reconstruct that nothing was lost. `.temp/t142/sweep.py` skips any pattern
   whose gate record already carries this `check.py`'s sha256, so the one
   interruption here (after `p38`, 24 of 27) cost one command, and `--status`
   **proves** `remaining 0` instead of asserting it.

**695 + 9 = 704.**

---

## 7b — UNSURE / NOT DONE

- ⚠ **The OLD arm of the glob probe has a disclosed confound** (§2d): HEAD's
  record is also stale on `harness/check.py`, so it prints one `STALE` of its
  own. The load-bearing evidence is that HEAD's record **does not contain the
  perturbed path**, which the arm prints first. A cleaner arm would rebuild a
  sandbox with the pre-edit `check.py`, the way `TASK_141`'s `probe_9c` does;
  I judged that not worth a second sweep's worth of machinery for a one-line
  glob.
- ⚠ **The glob change hashes whatever is on disk under `controls/`, tracked or
  not.** That is already true of `controls/*.py`, `pdir/c/*` and `harness/*.py`,
  so it is not new — but a stray untracked `.sh` dropped into a `controls/`
  would now enter that pattern's digest. Checked today: the only untracked
  things under any `controls/` are 12 `__pycache__` directories, which
  `os.path.isfile` drops (§3a).
- ⚠ **`p23/controls/controls.log` remains in no digest, deliberately**, and its
  `controls_pin.json` says so. I did not change that, and I think it is right:
  the file embeds ASLR addresses, PIDs, BuildIds and absolute repo paths.
- ⚠ **Not attempted, and not this task's:** `RECAP` finding 46 (iii), the
  detector allow-list inversion; and the `SYNTHESIS.md` reconciliation whose §0
  scope note says its four Results were drawn from 26 kernels without `p29`.
- ⚠ **I did not put the two `verus.rs` sites that describe `wf`'s own two
  conjuncts through any change** (`verus.rs:416`, `:593`'s neighbourhood beyond
  the one sentence I did edit). They describe the shipped spelling. A reviewer
  who disagrees should say so — it is the call in residual 1 I am least sure of.
- ⚠ **`.memory/03-measurement.md` entry 15 and the `.memory/06-catalogue.md`
  `p29` cell still carry what `TASK_141` §6 asked for.** I may not edit them;
  §6 above restates them plus the new items.

---

## 8 — SCRATCH

`.temp/t142/` — generators and evidence kept; no binaries were produced that
`build.py` / the generators do not rebuild, and `proof_mutants.py` deletes its
own mutant sources on success.

```
apply_rs.py          the 6 rung-comment substitutions, --check first, idempotent
leafdiff.py          classify every moved leaf of two JSON records; also
                     reports the class HISTOGRAM so the test cannot be vacuous
census_controls.py   the controls/ digest census; --head reads gate records out
                     of `git show HEAD:` so the BEFORE arm survives the sweep
arm_glob.py          the must-fire arm for the glob change (CTL / NEW / OLD)
sweep.py             the 27-pattern re-gate, RESUMABLE: skips a pattern whose
                     gate record already carries this check.py's sha256
baseline/            pre-edit copies: the p29 measurement + gate records, the
                     two sidecars, the four .rs sha256s
census-head.txt      the BEFORE census, captured
logs/                proof_mutants.log miri_arms.log measure-p29.log
                     report-p29.log gate-p29.log gate-p29-2.log sweep-run1.log
sweep/<pattern>.log  one gate log per pattern; sweep/rc.txt the verdict table
```

Everything regenerates:

```sh
python3 .temp/t142/apply_rs.py --check        # 0 applied, 6 already applied
python3 .temp/t142/census_controls.py         # AFTER
python3 .temp/t142/census_controls.py --head  # BEFORE
python3 .temp/t142/arm_glob.py                # ARM: PASS  (p18 / verify_controls.sh)
python3 .temp/t142/arm_glob.py p42-goto-cleanup controls/leak.sh
python3 .temp/t142/sweep.py --status          # remaining 0
python3 patterns/p29-bst-delete/controls/proof_mutants.py   # ~51 s
python3 patterns/p29-bst-delete/controls/miri_arms.py       # ~2 s
```

⚠ `.temp/t136/`, `t137/`, `t139/`, `t140/`, `t141/` were **read and never
written** — including `t141/probe_9c/`, the stage-9c must-fire arm.
