# TASK_132 review — finding 46, and the grep-a-log class

**Role: research reviewer.** Every number below is read from a file under
`.temp/t132/out/`, and every one of those files is written by
`.temp/t132/REBUILD.sh`, which was re-run to completion **after** the last edit
to any arm (entry 10's defence: a number quoted from a terminal is undated).
Notes: `.temp/t132/NOTES.md`. Arms: `.temp/t132/arms/`.

> **Headline.** Three landed claims are wrong and two of them are in
> `RECAP.md`. **§A the one-run lag is not "status quo": a PASSING gate run can
> leave the tree green and stale, and the next run on an UNCHANGED tree FAILS —
> measured end to end, run 3 `PASS` / run 4 `FAIL`. §C "stage 9c subsumes stage
> 9" is FALSE, with a counterexample on the project's own documented
> three-command loop. §D RECAP row 11's *"EVERY `p42 saw 2` … IS A GREP
> ARTEFACT"* is FALSE — `.temp/t107/gate-p42-rerun.log` carries two genuinely
> distinct blocked rows.** The byte comparison itself is sound and the
> `verdict` fix is real; I reproduced the engineer's `19 of 26` independently.

---

## Severity summary

| # | sev | finding |
|---|---|---|
| 1 | **blocker** | §A The one-run lag lets a **green** gate run publish a table it has just invalidated. Run N `PASS`, run N+1 `FAIL` on a byte-identical tree. Reachable without touching one measurement-hashed file. |
| 2 | **major** | §C *"stage 9c subsumes stage 9"* is false. Stage 9 fires `UNPINNED` while 9c says `FRESH`, on the first gate run of a new pattern. The sentence is in **both** docstrings and in finding 46. |
| 3 | **major** | §D `RECAP.md:11`'s *"EVERY `p42 saw 2` … IS A GREP ARTEFACT"* is false, and it destroys the support for its own neighbouring sentence. |
| 4 | **major** | §B1 `--selfref`'s `9` is a hand-written **deny-list**. `table_render` — stage 9c's *own output* — is not in it. A `report.py` that renders it is measured `26/26` READ while `--selfref` prints `0` and exits `PASS`. |
| 5 | minor | §D `grep -c BLOCKED` originates at **TASK_121**, not TASK_125. Its `sweep.out` carries `p01=3`, `p22=1`, `p42=3`; none reached its report. |
| 6 | minor | §E2 `RECAP` finding 45's `0` is **guard-dependent**: under the reconstruction TASK_131 actually shipped it is **2**. No spelling reproduces `845` or `854`. |
| 7 | minor | §E3 `temp_citations.py`'s assembled-path blindness hid **14** citations across 12 committed files. |

**Clean negatives** (named attacks that did not land, so nobody re-runs them):
`RENDER-ERROR` **is** a failing verdict; the grepped **verdict** and **FAIL
count** agree with the record 130/130; the four run-scoped keys the docstring
names are the only ones that move across three fresh draws; the must-fire arm
on `--selfref` fires and reproduces `19 of 26`.

---

## §A — the trade the engineer asked me to attack. **It does not hold.**

### A3. The measured case: a PASSING run makes the next run fail

`.temp/t132/out/a3_lag.txt`, `a3_gate_run{3,4}.log` — two real `check.py p03`
runs.

**Trigger:** add one `patterns/*/controls/*.json` with no staleness pin.

* `check_control_json_pins` (stage 9b) answers `UNPINNED` with **`rep.shout`,
  not `rep.fail`** — so the run is green;
* the shout lands in the record's `loud` **and** `controls_json`, **both** of
  which `report.py::read_gate_loud` renders (`--reads`: 26/26);
* `controls/*.json` is in **neither** `measure.py::measurement_sources` **nor**
  the gate's `source_sha256` glob (`controls/*.py`). Nothing else moves.

```
== run 3: sidecar added ==
rc=0     check.py: PASS
    ok   results/tables/p03-bounded-stack.md is byte-identical to a fresh render (61a0eb453665)…
    !!   [tables] …/t132_lag_probe.json carries NO staleness pin…        <- a SHOUT, not a fail

== run 4: NOTHING changed since run 3 ==
rc=1     check.py: FAIL
    FAIL [tables] results/tables/p03-bounded-stack.md is STALE IN ITS CONTENT: 1 line(s) differ…
      @@ -80,0 +81 @@
      +- **`tables`** — …/t132_lag_probe.json carries NO staleness pin…
```

⚠⚠ **That is exactly the failure mode the manager was unsure about: a user runs
the gate, sees `PASS`, commits — and the committed tree is stale and green.**
`measure.py --check-stale` does not see it either (it globs `results/*.json`
and `results/gate/p*.json`; table content is not in its scope). Between run N
and run N+1 **nothing in the tree can say so**.

### The *"stage 9 has exactly the same shape"* defence conflates two lags

Stage 9 compares the table's cited contract against `contract_sha` computed
**live from `spec.md`**. Its *detection* has no lag at all; what lags is its
*repair* (`report.py` renders the record's sha, so the fix needs the record to
be current). **Stage 9c's lag is in the DETECTION.** So:

| | what it compares | can a GREEN run leave it wrong? |
|---|---|---|
| stage 9 | live `spec.md` sha vs the table | **no** — a contract move fails stage 9 the same run |
| stage 9c | previous run's record vs the table | **yes** — `loud`, `controls_json`, `idiom_audit` |

The two docstrings and finding 46 say "the same shape". They have the same
*mechanism* and opposite *consequences*, and only 9c's admits a green-and-stale
commit.

### A4. "Frequency unmeasured" — now bounded

`.temp/t132/out/a4_shouts.txt`: **26 `rep.shout(` call sites across 12
sections** in `check.py` (against 199 `rep.fail(` and 4 `rep.block(`). Five
sections fire on today's tree (`idiom-forbidden` 13, `tcb-unsafe` 12,
`collapse-ir` 3, `clause-mut` 3, `twin` 1 = 32 entries, arm D2). **Seven
sections are latent**, and each is a green-run-N / red-run-N+1 trigger the
first time it fires. It is not rare; it is one shout away.

Of the four fields `report.py` reads, I traced which a green run can move:

| field | can a green run change it? | why |
|---|---|---|
| `contract_sha256` | **no** | any move fails stage 9 the same run |
| `idiom_audit` | yes, but only via a rung-source edit | `--check-stale` would flag the record, `check.py` would not |
| `controls_json` | **yes, freely** | `UNPINNED` shouts; the glob covers neither digest — **A3** |
| `loud` | **yes, freely** | 26 shout sites, 7 latent sections |

### What I recommend (reviewer does not fix)

1. `check_table_render` and `read_gate_loud` should say **which** lag they have
   and that stage 9's is a different one. The current sentence is the kind that
   gets believed.
2. Finding 46's *"the one-run lag is KEPT DELIBERATELY … status quo"* needs the
   caveat: **it admits a green-and-stale commit, demonstrated at TASK_132 §A.**
3. ✅ **A fix exists that does not reintroduce the self-reference and needs no
   ordering rule:** stage 9c already knows, at the moment it runs, every field
   it read. It can compare the render against the record **it is about to
   write** for the four read fields only — they are all computed before the
   record write (`audit` at stage 0b, `ctljson` on the line above 9c, `loud`
   accumulated, `contract_sha` at stage 0). That removes the lag *without*
   letting any run-scoped field in, because the four are exactly the
   deterministic ones. I did not build it; `check.py` is not mine to edit and
   it costs a sweep.

---

## §B — is the self-reference gone, or just the one instance?

### B2. MUST-FIRE arm: yes, the detector can fire — and 19/26 reproduces

`harness/report.py` is inside the gate digest, so editing it in place costs a
26-pattern sweep. Instead `.temp/t132/arms/b2_rig.sh` builds a **fake repo**
whose `harness/` is symlinks to the real modules except `report.py`, a copy
with TASK_127's fix reverted (`verdict` back in `read_gate_loud` and in
`shout_section`). The detector itself is copied byte-identically.

```
control (report.py byte-identical, sha256 399df913…):
    run-scoped keys reaching the rendered table: 0    SELFREF: PASS   rc=0
                                              ^^ byte-identical to the shipped run

must-fire (fix reverted):
    ⚠ `verdict` reaches the render on 19 pattern(s): p01…, p02…, p03…, p04…, p05…, p06… …
    run-scoped keys reaching the rendered table: 19   SELFREF: FAIL   rc=1
```

✅ **The detector is not a control that cannot fire, and `19 of 26` reproduces
on a rig the engineer did not build.**

### B1. But the `9` is hand-written, and it is a deny-list

`.temp/t132/out/a1_keys.txt`: 26 records, **34 keys**, identical key set in all
26. The `9` is `len(RUN_SCOPED)`, a literal tuple in
`harness/tools/table_render_inputs.py`. **25 keys are unclassified**, and at
least four of them are functions of the run:

* ⚠⚠ **`table_render` — stage 9c's OWN verdict, `render_sha256`,
  `published_sha256`, `lines_moved`.** The purest self-reference available.
* `published_table` — stage 9's verdict, same run.
* `marginal_ir_per_call` / `marginal_ir_env` — `check.py`'s own comment calls
  `-O3 isolated` *"NOT invariant … ±7 per rung with the initial stack layout"*.

⚠⚠ **A three-draw measurement CANNOT find them, and that is the point.**
`.temp/t132/out/a2_twodraw.txt` — the committed p03 record plus two fresh
`check.py p03` runs of mine — moves exactly `adversarial`, `sanitizer`, `miri`,
`notes`, all four already in `RUN_SCOPED`, none read by `report.py`.
`table_render` did not move **because the run was green both times**; it moves
the first time 9c fires, which is the case the whole finding is about.

**Demonstrated, not argued** (`.temp/t132/out/b3_blindspot.txt`): a `report.py`
that renders `table_render` and `marginal_ir_per_call`:

```
--reads    table_render          26/26 pattern(s)
           marginal_ir_per_call  26/26 pattern(s)
--selfref  run-scoped keys reaching the rendered table: 0 (over 26 patterns x 9 keys)
           SELFREF: PASS -- the render is a function of committed sources only   rc=0
```

⚠ **The detector reports PASS on the exact defect it was built for.** This is
the project's own named class — *a grep that can only find what you already
thought of is not a census*.

**Recommended fix, and it is small and lives outside the digest:** invert the
test. `--reads` already MEASURES the read set. Assert that set is a **subset of
an allow-list** `{contract_sha256, controls_json, idiom_audit, loud}` instead of
disjoint from a deny-list. An allow-list is a census; every future key is
caught by construction and nobody has to remember to extend a tuple. As an
interim, `RUN_SCOPED` is missing at minimum `published_table`, `table_render`,
`marginal_ir_per_call`, `marginal_ir_env`.

### B3. Should the detector be outside the gate?

✅ **Yes, the placement is right — and the engineer's own honest statement
(*"the self-reference is fixed and its detector is opt-in"*) understates the
problem, because §B1 shows the opt-in detector would not fire anyway.** Wiring
it into `check_selftests` would cost a sweep to maintain and would put a
26×9-render probe in every gate run. The cheaper repair is the allow-list
above: it makes the check *correct*, and a correct opt-in check plus a
docstring rule beats an incorrect mandatory one. ⚠ But say so in
`read_gate_loud`'s rule paragraph, which currently reads as though the standing
detector closes the question.

---

## §C — subsumption, and `RENDER-ERROR`

### C1. *"9c subsumes 9"* is **FALSE**, and the counterexample is routine

`.temp/t132/arms/c1_subsumption.py` drives the **real**
`check.check_published_tables` and `check.check_table_render` (imported, not
re-implemented) against a fake repo whose `results/gate/` is missing exactly
one record.

**The scenario is the project's own documented three-command loop for a new
pattern** — `measure.py`, then `report.py`, then gate. At the middle step there
is no gate record, so `read_gate_audit` returns `(None, False)`, `audit_section`
returns early, and the render carries **no contract line at all**:

```
rendered p03-bounded-stack.md with NO gate record present: 32308 bytes, sha256 2ddc7e6666c0
does it cite a contract?   False

== 9. the published table cites THIS contract ==
    FAIL [tables] …cites no `contract_sha256` at all…            <- STAGE 9 FIRES
== 9c. the published table is a fresh render of THIS tree ==
    ok   …byte-identical to a fresh render (2ddc7e6666c0)…       <- 9c DOES NOT

stage 9  verdict : UNPINNED
stage 9c verdict : FRESH

CONTROL (record present): stage 9 FRESH / stage 9c FRESH / failures 0
control holds: the rig itself is not what makes stage 9 fire.
```

⚠⚠ **So the sentence *"9c subsumes all three verdicts below"* in
`check_published_tables`'s docstring, the matching sentence in
`check_table_render`, and finding 46's *"Stage 9 is KEPT even though 9c
subsumes it"* are all wrong on `UNPINNED`.** The direction matters: a reader who
believes the subsumption would consider stage 9 removable, and removing it
leaves `UNPINNED` undetected on precisely the case it was written for.
**Correct wording: 9c subsumes `STALE`; `MISSING` is delegated to stage 9 by
construction; `UNPINNED` is NOT subsumed.** Stage 9 stays, and now for a fourth
reason that is a property rather than a convenience.

### C2. `RENDER-ERROR` **is** a failing verdict — a clean negative

`.temp/t132/arms/c2_render_error.py` drives all six 9c verdicts through the
real function:

```
stage 9c verdict     rep.failures  gate verdict this forces
FRESH                           0  PASS(no fail)
STALE-CONTENT                   1  FAIL
MISSING                         1  FAIL
SKIPPED-NO-TABLE                0  PASS(no fail)
NO-RECORD                       1  FAIL
RENDER-ERROR                    1  FAIL
```

`check.py`: `if rep.failures: verdict = "FAIL"`. ✅ **A pattern whose table
cannot be rendered at all does NOT pass.** `SKIPPED-NO-TABLE` is the only
non-failing branch and it is reachable only when stage 9 has already failed
`MISSING`, so the run is red anyway.

---

## §D — the grep-a-log class. **It is one pass, and it is small.**

### D3. Scope and the census

`.temp/t132/out/d3_sites.txt`. Searched: `RECAP.md`, `.memory/*.md`,
`.tasks/*.md`, `patterns/*/{NOTES,README}.md`, `harness/*.py`,
`harness/tools/*.py`, `synthesis/*.py`, `common/**/*.py`, plus every sweep
generator under `.temp/`.

```
grep/rg mentions over a SOURCE file (a different, weaker class): 534
grep/rg mentions whose target is a TRANSCRIPT                  :  29
```

**Of the 29, exactly one family is defective: `blocked`.** The rest classify as:

| family | sites | verdict |
|---|---|---|
| `grep -c BLOCKED` over a sweep log | `.temp/t121/sweep.sh:19`, `.temp/t121/finish_sweep.sh:13,25,30`, `.temp/t125/sweep.sh:25` | ⚠ **WRONG** — see D1 |
| `grep -c r84_lie/t88_lie gate.log → 0` | `RECAP:79`, `RECAP:3976`, `check.py:4482`, `check.py:7459`, `synthesize.py:1304`, `TASK_084_REVIEW:38`, `TASK_088.md:122`, `TASK_088_REPORT:29` | ✅ **legitimate** — the claim IS about the log's silence; the log is the subject, not a proxy |
| `grep -c AddressSanitizer` | `RECAP:109,112`, `.memory/00-environment.md:462,465`, `TASK_095_REPORT:72` | ✅ **legitimate** — a hand-run ASan probe has no structured record |
| `grep -c 'FAIL \[' gate.log → 0` | `TASK_054_REPORT:275` | ✅ agrees with the record (D2, 130/130) |
| `grep` over `results/gate/*.json` as TEXT | `TASK_033_REVIEW:195`, `TASK_064_REVIEW:340` | ✅ re-derived today: `work_per_call` → 0 on all 26; `==N==ERROR` → 1–3 on 13 records |
| `grep -c "distinct behaviour" results/tables/*.md → 0` | `TASK_127.md:71` | ✅ re-derived → 0 everywhere |

⚠ **No silent cap.** I stopped at the transcript class because the
gate-record-derived families are the ones with a record to check against, which
is what the task file prioritised. **The 534 source-greps are NOT swept** — that
is a different and much weaker class (the source *is* the record), and it would
be a genuine rabbit hole.

### D1. The decoder, and the class checked against the record

`check.py` prints a blocked row **twice** (the in-stage `!! [miri] BLOCKED` line
and the verdict-section `!! BLOCKED [miri]` line) and then the verdict word
`PASS-WITH-BLOCKED-ROWS`. So `grep -c BLOCKED` = **2N + 1**, never N.

`.temp/t132/out/d1_blocked.txt` decodes **130 sweep logs** (`t107`, `t119`,
`t121`, `t125`, `t127` × 26) by counting *distinct* `(rung, input)` pairs:

```
130 (sweep, pattern) log(s) compared against the committed records
rows where the log-derived distinct count != committed record: 0
```

`p01 = 1`, `p42 = 1`, everything else `0`, in every sweep. `p22`'s
`grep -c` = **1** and its true count is **0**: the hit is `p22/NOTES.md:719`
echoed into its own gate log at line 477.

### D1b. ⚠⚠ `RECAP.md:11` is wrong, and it undercuts its own neighbour

RECAP row 11 asserts *"EVERY `p42 saw 2` / `p42 saw 3` / `p22 shows one blocked
row` IN THIS PROJECT'S HISTORY IS A GREP ARTEFACT"*.
`.temp/t132/out/d1b_p42_two.txt`:

```
log                                grep -c  rows  inputs
.temp/t107/gate-p42-rerun.log            5     2  adversarial-wincap.bin, large.bin
.temp/t107/sweep/p42.log                 3     1  large.bin
.temp/t119/sweep/p42.log                 3     1  large.bin
.temp/t121/sweep/p42.log                 3     1  large.bin
.temp/t125/sweep/p42.log                 3     1  large.bin
.temp/t127/sweep/p42.log                 3     1  large.bin
```

**TASK_107's re-run has two genuinely distinct blocked rows, naming two
different input files.** It was taken with `MIRIFLAGS` pinned, it reproduced on
an idle re-run, and TASK_107's `g1_sweep.sh` does not use `grep -c` at all
(`v=$(tail -1 …)`). It is corroborated independently by TASK_114's 4.6 %
two-state timing (`74 s` vs `340 s` against a 180 s `MIRI_TIMEOUT`, 21 timed
runs) — a *timing* measurement, not a grep.

⚠⚠ **And the error is self-defeating.** Row 11's previous sentence says
*"`p42`'s blocked-row COUNT may legitimately vary … Do NOT read a second `p42`
block as a regression"*. Its only evidence is the observations the next sentence
dismisses. **As written, row 11 removes the support for its own advice.**

**Correct scoping, for the manager to land:**
`p42 saw 3` **is** a grep artefact (`2N+1` with `N=1`); `p22 shows one blocked
row` **is** a grep artefact (prose echo, and it could not have been true anyway
since a blocked row forces the other verdict); **`p42 saw 2` is REAL**, was
observed under a configuration that no longer ships, and is what
`.memory/00-environment.md`'s *"can legitimately produce a SECOND blocked row"*
rests on.

### D2. Two clean negatives, and D5 the origin

`.temp/t132/out/d2_verdict_failures_loud.txt`, over the same 130 logs:

```
verdict     grep != record : 0
FAIL-count  grep != record : 0
loud entries in the 26 COMMITTED records: 32  (idiom-forbidden 13, tcb-unsafe 12,
                                               collapse-ir 3, clause-mut 3, twin 1)
```

✅ **`grep -E '^check\.py: ' | tail -1` and `grep -c '^ *FAIL'` are right, 130
times.** A grep that happens to be right is not a defect — but both are one
`tail -1` away from silently reporting nothing on an interrupted run, and both
have a record one `json.load` away.

⚠ **The origin is TASK_121, not TASK_125.** `.temp/t121/sweep.sh:19` and
`.temp/t121/finish_sweep.sh:13,25,30` already compute
`blocked=$(grep -c BLOCKED …)`, and `.temp/t121/sweep.out` carries
`p01 blocked=3`, `p22 blocked=1  check.py: PASS`, `p42 blocked=3`. ✅ **None of
them reached `TASK_121_REPORT.md`** — its only sweep line is *"24 PASS + 2
PASS-WITH-BLOCKED-ROWS (p01, p42), 0 failures"*, which is correct. So the defect
is four tasks older than finding 46 says, and the report that first *published*
it is TASK_125's.

---

## §E — the ride-alongs

### E1. The manifests: promoted to `common/census/`, **506 K not 956 K, zero lost**

`.temp/t132/out/{e1_manifest,e1_verify}.txt`.

```
php        t129   553  promoted   553  identical: True   symmetric-difference: 0
coreutils  t129   963  promoted   963  identical: True   symmetric-difference: 0
cgnu       t129  3826  promoted  3826  identical: True   symmetric-difference: 0
promoted bytes total: 518186 (506 K); TASK_129 scratch was 973049 (950 K)
                                       -- 46.8% smaller, ZERO content lost
```

⚠ **The 950 K was mostly PATH PREFIX.** Every line carried an absolute root up
to 90 bytes long. Corpus-relative paths with the root in a header halve the file
and lose **nothing**: 5342 of 5342 `(path, sha256)` pairs verified identical
against TASK_129's scratch.

**Smaller forms measured and rejected, with what each loses written into
`common/census/README.md`:** gzip → 205 K but stops being diffable or
greppable; a digest-of-digests plus per-program counts → ~2 K, keeps the
re-identification guarantee **in full**, and loses the two things that matter
once a corpus is deleted — *which* file differs, and what the corpus contained.

✅ **The decisive argument for the full list, and it is measured:**
`common/census/census_filelists.py` re-derives TASK_129's **deduplicated
population** from the manifests alone and reproduces **php 299 / coreutils 94 /
cgnu 2162** exactly — the three counts TASK_129 published. It exits 1 if any
moves. A digest-of-digests could not do that. **So: promote, and the manager's
lean was right.**

### E2. `RECAP` finding 45's `845` — and its `0` is guard-dependent too

`common/census/ptr_cursor_regex.py`, `.temp/t132/out/e2_ptr_cursor.txt`:

| corpus | files | v0 | v1 | v2 | v3 |
|---|---|---|---|---|---|
| **MUST-FIRE** planted kernel | 1 | **2** | **2** | **2** | **2** |
| ladder `patterns/*/c/kernel.c` | 26 | **2** | **2** | **0** | **0** |
| ladder `patterns/*/c/*.{c,h}` | 103 | 9 | 7 | 2 | 0 |
| php | 299 | 952 | 920 | 916 | 781 |
| coreutils | 94 | 38 | 38 | 35 | 32 |
| cgnu | 2162 | 3570 | 3504 | 3315 | 2718 |

`v0` no guard (= the spelling TASK_131 actually shipped) · `v1` byte-adjacent ·
`v2` whitespace-skipping · `v3` `v2` + reject a preceding `)`.

⚠⚠ **Three things this settles, and the second is new:**

1. **No spelling reproduces `845` or `854`.** Four honest guards span
   `952 → 781` over PHP — **±10 %**, not the "1 % off" TASK_131 recorded. The
   PHP figure in finding 45 is **not re-derivable and should be struck**, not
   corrected to another number.
2. ⚠⚠ **The `0` is not free either.** It reproduces only under `v2`/`v3` and
   only over the 26 `kernel.c`. Under the guard TASK_131 shipped it is **2** —
   and both hits are `8 * (n + m)` in `p46`, i.e. **a multiplication counted as
   a dereference**, which is the exact false positive that task named and then
   published a number over. Widen the scope to `patterns/*/c/*.{c,h}` and even
   `v2` gives **2**.
3. ✅ **The claim still stands, once its scope and guard are written down:** no
   shipped C *kernel* walks with a pointer cursor. The must-fire arm gives
   **2 in every variant**, so the zero is not a dead detector.

**Recommended edit to finding 45:** replace *"`845` over PHP, `0` over the
kernels, both numbers exact"* with *"`0` over the 26 `patterns/*/c/kernel.c`
under `common/census/ptr_cursor_regex.py --ladder` (`v2`); the PHP figure is
guard-dependent over a `952 → 781` range and is withdrawn."*

### E3. `temp_citations.py`: both known defects fixed, both with must-fire arms

`.temp/t132/out/{e3_mustfire,e3_temp_citations_before,e3_temp_citations_after}.txt`.

* **Defect 1 — another project's `.temp/`.** New `owner(line, start)`: eat the
  path characters to the left; if they form an **absolute** path not under this
  repo, skip. Conservative by design (a false *self* is a citation that gets
  checked; a false *foreign* is one that stops being). Must-fire arm: the
  un-guarded `PAT` **does** match a foreign path and it **does not** resolve
  here — i.e. without the fix that is a dangling citation of a path this repo
  never had.
* **Defect 2 — a path a committed `.py` ASSEMBLES.** New `joined_paths(line)`
  reconstructs `.temp/…` from a `join()` whose argument list contains a
  `".temp"` literal, stopping at the first non-literal. Must-fire arm: the
  literal regex returns `[]` on the same line.

```
before: citations 1874 over 1453 distinct paths;  dangling 77;  rc=0
after : citations 1968 over 1516 distinct paths;  dangling 96;  rc=1, 14 NEW
```

⚠ **The fix immediately found 14 assembled citations that nothing had ever
seen** — `harness/check.py:9006`, `harness/tools/table_render_inputs.py:70`
(the one TASK_127 reported and could not baseline), and twelve
`patterns/*/controls/*.py`. All are `kind: destination` (the citing line is the
assignment that creates the directory); baselined, and `rc=0` again.

⚠ **One interaction to know about:** an entry for a file that is not yet
tracked reports as `RESOLVED … run --update to prune`. That is the behaviour
TASK_127 hit. It is a notice, not a failure — but **do not run `--update`
before committing `common/census/`**, or it will prune the pre-added entry.

---

## §F — verification

| check | result |
|---|---|
| `harness/check.py p03` ×2, clean tree | `PASS` / `PASS`, render `61a0eb453665` both times (= TASK_127's) |
| `harness/check.py p03` ×2, the §A arm | `PASS` then **`FAIL`** — the finding |
| `harness/check.py p23` | `PASS`, stage 9 `FRESH`, stage 9c `FRESH` (`379a68d020b7`) |
| `harness/measure.py --check-stale` | `52 record(s) examined, 0 STALE` |
| ⚠ digest, **confirmed not assumed** | p23 `source_sha256` **37 keys before, 37 after, none added, none removed, none moved**; `common/census/*` and `harness/tools/*` absent from the key set. **NO SWEEP OWED.** |
| `harness/tools/temp_citations.py` | `rc=0` (`new=0 unclassified=0 resolved=1`) |
| `blocked`, read from the JSON | `p01 = 1`, `p42 = 1`, all others `0` |
| tree at finish | `M harness/tools/temp_citations.py`, `M harness/tools/temp_citations_baseline.json`, `?? common/census/` |

**No `check.py` edit was made**, so no sweep. I ran **five** gate runs (p03 ×4,
p23 ×1) and **restored all 26 `results/gate/*.json` byte-exactly from HEAD**
afterwards (`sha256sum -c`, 0 mismatches); my run records are kept in
`.temp/t132/out/`. The §A arm added and then removed one untracked
`patterns/p03-bounded-stack/controls/t132_lag_probe.json`;
`git status --porcelain` was empty immediately after.

---

## Problems

* **My first §A arm wrote invalid JSON** (a literal newline inside a string), so
  stage 9b `rep.fail`ed *"not readable as JSON"* instead of shouting, and the
  run went red for the wrong reason. Caught, fixed, re-run; the failed attempt
  is not in `out/` because REBUILD regenerates it.
* **My first `_NOT_OPERAND_END` guard was insufficient** and I found it only
  because the ladder scored 7 instead of 0 — the byte-adjacent lookbehind
  cannot see past the space in `8 * (n + m)`. It is now `v1` in the shipped
  table rather than deleted, because the difference between `v1` and `v2` is the
  finding.
* **One of my own must-fire expectations was wrong** (`joined_paths` on a
  variable component: I expected `['.temp']`, the correct answer is `[]` — half
  a path is not a citation). Arm corrected, not the code.

## Unsure / not done

* **I did not fix the §A lag.** The design I propose (compare against the four
  fields *this* run has already computed, before the write) is reasoned from the
  source, **not built and not measured.** It is a `check.py` edit and costs a
  sweep. ⚠ **Treat it as a conclusion I did not test.**
* **I did not measure how often the seven latent shout sections actually
  fire** — only that they exist and that one of them (`tables`/`UNPINNED`) does,
  end to end.
* **§C's counterexample is `UNPINNED`, not `STALE`.** I did not find a case
  where stage 9 fires `STALE` and 9c does not, and I believe there is none: a
  stale citation implies the render differs. So the subsumption sentence is
  wrong on one of three verdicts, not all three.
* **`idiom_audit`'s "read" verdict is degenerate.** `--reads` scores it 26/26
  because the mutation makes `report.py` **raise**, not because the bytes move.
  Raising is evidence the key reached the renderer, so the conclusion holds, but
  it is weaker evidence than the other three keys have. The engineer's report
  does not flag this; the tool's `[raised on 26]` marker does.
* **I did not re-derive the PHP corpus from upstream tarballs** to check whether
  the c-gnu tree under another project's `.temp/` is unmodified. The manifests
  pin what is there; they cannot say it matches upstream.
* **`.memory/` untouched** (manager-only). Owed items below.
* I did **not** add stages 9/9b/9c to `check.py`'s module docstring — still
  open from TASK_127, still a `check.py` edit, still a sweep.

## Memory updates

**None — `.memory/` is manager-only.** Owed, from measurements in this report:

1. ⚠⚠ **`RECAP.md:11`** — scope the grep claim. *"`p42 saw 3`"* and *"`p22`
   shows one blocked row"* are grep artefacts; ***"`p42 saw 2`" is REAL***
   (`.temp/t107/gate-p42-rerun.log`, two distinct inputs, `MIRIFLAGS` pinned,
   corroborated by TASK_114's 4.6× two-state timing). As written the row
   destroys the support for its own preceding sentence.
2. ⚠⚠ **`RECAP.md` finding 46** — three corrections: the one-run lag **admits a
   green-and-stale commit** (§A, measured); *"9c subsumes 9"* is **false on
   `UNPINNED`** (§C); the `grep -c BLOCKED` defect **originates at TASK_121**,
   not TASK_125, though only TASK_125 published it.
3. **`.memory/03-measurement.md` failure-class entry 10 may now land** — the
   review it was waiting on. ✅ Its conclusion (*a check whose own output is an
   input to the artefact it checks*) is confirmed, with an independent must-fire
   arm reproducing `19 of 26`. ⚠ **Add the second half this review found: a
   deny-list of run-scoped keys is not a census — the detector reports `PASS` on
   `table_render`, stage 9c's own output.** The question the entry adds should
   be *"does this check write anything the thing it checks reads — and is your
   list of 'anything' a census or a guess?"*
4. **A new entry, or a clause on 10: THE ONE-RUN LAG.** A gate stage that
   compares against the PREVIOUS run's record can be green on a tree it has just
   invalidated. Trigger measured: an unpinned `controls/*.json`, which is in
   neither digest. **26 `rep.shout(` sites over 12 sections; 5 fire today, 7 are
   latent.**
5. **`.memory/03-measurement.md`** — the grep-a-log rule, with the decoder:
   `check.py` prints a blocked row twice plus the verdict word, so
   `grep -c BLOCKED` = **2N+1**. Validated over **130 sweep logs, 130/130
   agreeing with the record.** ✅ And the clean negatives: the grepped
   **verdict** and **FAIL count** agree 130/130, so the rule is *read the
   record*, not *never grep*.
6. **`RECAP` finding 45** — strike the PHP figure (`845`/`854`/`916` are three
   reconstructions of an unrecorded instrument, spread ±10 %); keep the `0`
   **with its scope and guard named**: 26 `patterns/*/c/kernel.c`, guard `v2`.
   Under the guard TASK_131 shipped it is **2**.
7. **`.memory/05-layout.md`** — `common/census/` exists, is outside both
   digests, and carries the three corpus manifests (506 K, corpus-relative),
   `census_filelists.py` (re-derives the census population: 299/94/2162) and
   `ptr_cursor_regex.py`. `harness/tools/temp_citations.py` now sees assembled
   paths; the baseline is **81 entries**, up from 66.

---

⚠ **PROTOCOL rule 2:** I was launched carrying **617**. My branch delta is
**17** — the green-then-red lag arm; the detection/repair distinction between
stage 9's lag and 9c's; the 26-site/12-section shout bound; the hand-written
deny-list and its measured blind spot on `table_render`; the `19/26` must-fire
reproduction; the allow-list repair; the `UNPINNED` subsumption counterexample;
`RENDER-ERROR` confirmed failing; the `2N+1` decoder validated 130/130; the real
`p42 = 2`; the TASK_121 origin; the two clean grep negatives; the 29-vs-534 site
census; the manifests' 46.8 % path-prefix saving and the population re-derivation;
the guard-dependence of finding 45's `0`; and `temp_citations.py`'s 14 invisible
assembled citations. **617 + 17 = 634.** ⚠ **Reconciliation is the manager's,
not mine** — five concurrent branches were still unreconciled when I was
launched; do not re-add across them.
