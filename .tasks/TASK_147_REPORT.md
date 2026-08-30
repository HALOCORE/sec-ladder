# TASK_147 — `p32`'s review corrections landed, in ONE re-measure and one re-gate pair

**Role: research engineer.** `.memory/`, `RECAP.md`, `results/SYNTHESIS.md`
(CAPITALS), `harness/`, `pilot/`, `../LearnVeri/` and every cited `.temp/`
directory (`t136 t137 t139 t140 t141 t142 t143 t144 t145 t91 mgr146 mgr147
mgr148 mgr149 mgr150`) were **not edited**. No `git add`, no `git commit`. Verus
ran only via `./verus_run.py` in single-file mode, never `--cargo`. Every
hand-run sanitiser had `LD_PRELOAD` unset; no sanitiser log was truncated.
Scratch is `.temp/t147/` only; no `/tmp` file was written at any point.

---

## HEADLINE

> ### **`harness/check.py p32` PASSES — `failures []`, `blocked []`, `complete_run true`, all five control sidecars FRESH. M1 was taken as option (a): `model.py`'s sanitiser derivation is now a check that CAN fire, and `TASK_145`'s own 20 000-fuzzed-buggy-window falsifier — the sweep that gave it **0 firings** — now gives **19 622 of 20 000 with the `h == NIL` guard deleted and 0 of 20 000 with both guards present.** The verdict did not move; the evidence for it did.**

> ### **Budget held: ONE `harness/measure.py p32`, ONE `report.py`, TWO gate runs (the documented `[tables]` ordering). The re-measure moved 103 of 1366 leaves — 96 wall-clock, 3 source hashes, 2 git, 1 timestamp, 1 vanished `warning` — and ZERO `Ir`, md5, identity, checksum or `model_stdout`, which was stated as the prediction before the run.**

⚠ **One cost the task file did not name, found and closed:** a gate re-run that
moves `source_sha256` makes `synthesis/licence.json`'s pin stale, and
`results/synthesis.md` then publishes **`LICENCE STALE`** for p32 in four tables.
Re-emitting took seconds and was **surgical — 12 leaves, all p32's
`gate_source_sha256`, zero verdicts, zero other patterns** — which is itself the
proof that nothing in this task moved a single instruction. §7.

---

## 1. ⚠⚠⚠ M1 — option (a) was taken, and here is the justification

**The task offered *make the check real* or *retract and declare*. (a) was taken
because the review's own diagnosis names the repair, and it is one line deep.**

`Pool.oob` could not fire because the simulation **erased the rungs' NIL
sentinel**. A handle was a `Block` object or `None`; `Block.slot` is drawn from
`range(SLOTS)` by construction; `None` is not an index. So `0 <= s < SLOTS` was
false of nothing the simulation could form — a tautology of its own
representation. **Every rung carries `255` in that slot instead, and 255 IS an
index.** Carrying the handle through the *index* path the way the rungs carry it
makes an escape representable **without turning the model into the C kernel** —
the staleness decision stays Python object identity, which is the independence
the row rests on.

### 1a. What `model.py` does now

| | |
|---|---|
| `Pool.head_index()` | `freehead` as the rungs spell it: a slot, or `NIL` |
| `h = NIL if blk is None else blk.slot` | the rungs' `regs[r]`, in `_sim_window` |
| `Pool.touch(name, i, limit)` | ⚠ **a check about a VALUE, not a representation**: the caller hands it the integer a rung would form and the extent of the array it would form it into. Raises `_Escape`, which the window catches — **a firing is REPORTED, not crashed on** |
| `Pool.touch_slot(h)` | `gen[h]`, `nx[h]`, `pool[h*BLK]`, `pool[h*BLK+1]` — called on **ALLOC's `freehead` side as well as** FREE/READ/WRITE's |
| plus | `buf[off+p+1]` and `regs[r]` at the top of the loop |

**All four of `TASK_145_REPORT` §4b's defects are closed by construction**:
the tautology (a value check, not a representation check); the crash
(`_Escape`); *"three times over"* (`gen`/`nx`/`regs` and ALLOC's own write are
now touched); and `M3-nil-test`'s unrepresentable shape (it is now the must-fire
arm).

⚠ **What it derives, stated narrowly in all six places:** the **spatial** half —
no index leaves an array, which is what ASan and UBSan look for. Miri's silence
is not derived here and needs no simulation: Miri is an instrument about
allocations and this kernel makes none (`spec.md`'s `miri.reason`).

### 1b. The must-fire arm, and the gate runs it

`model.py::detector_selftest()` → called from `selfcheck()` →
`harness/check.py::build_models` calls it **once per input on every gate run**
and `rep.fail("model", …)`s on it. **So the arm is re-derived by the gate, not
once by me** — `TASK_141` repair 2's requirement.

```
$ python3 .temp/t147/mustfire_probe.py            # OUTSIDE model.py, on purpose
1. the four cells of detector_selftest(), re-derived
   PROBE_NIL   h == NIL kept              oob=False want=False OK
   PROBE_NIL   h == NIL DELETED           oob=True  want=True  OK
   PROBE_HEAD  freehead == NIL kept       oob=False want=False OK
   PROBE_HEAD  freehead == NIL DELETED    oob=True  want=True  OK
   model.detector_selftest() -> []

2. Pool().touch_slot(255) in isolation
   raised _Escape(gen[h] = 255, outside [0, 8))   oob=True  sites=['gen[h] = 255, outside [0, 8)']

3. 20 000 fuzzed buggy windows, `h == NIL` DELETED  (must fire)
4. the same 20 000 with both guards PRESENT           (must be 0)
   guards deleted : 19622 / 20000 fired
   guards present :     0 / 20000 fired

ALL ARMS AS EXPECTED
```

⚠ **Line 3 is `TASK_145`'s own falsifier, re-run against the repair.** The same
sweep that measured *"0 firings in 20 000"* against the old detector now fires
19 622 times when the guard is deleted and 0 times when it is not — **the
two-cell form this whole pattern is built on, applied to its own instrument.**
Item 2 is defect 3 specifically: it raises `_Escape`, **not** `IndexError`.

### 1c. The claim retracted in all six places, not overwritten

`spec.md`'s hashed `idiom.why`, `README.md`, `NOTES.md` 2a, `model.py`'s module
docstring, `sanitizer_expect`'s docstring, and a new **`NOTES.md` §11** that
writes out what was claimed, why it was false four ways, what the repair is, the
must-fire table, and the before/after evidence. **Each site quotes the old
sentence and marks it retracted**, so a later reader cannot "confirm the
derivation by finding nothing". `TASK_144_REPORT` §4 and `RECAP` 55 are historical
documents and the manager's; both are named in §11 as carrying the claim.

### 1d. ⚠ The honest sentence the manager asked for (`mgr150`)

The manager's audit found `p04` and `p32` are the only two patterns with a
derived `sanitizer_expect` that fires on nothing, and offered `p04` as the
exemplar. **I agree with the audit and I can sharpen the distinction it asked
for, because option (a) is exactly that distinction made operational:**

* **`p04`'s predicate is false by MODULAR ARITHMETIC** — every index is `head` or
  `tail`, every update is `(x + 1) % RING_CAP`. **That is a fact about the
  PROGRAM.**
* **`p32`'s was false because the SIMULATION could not represent an out-of-range
  slot at all.** **That is a fact about the MODEL.**

⚠⚠ **Those are different failures and only the second is a defect.** The first is
a derivation whose answer happens to be constant; the second is a constant
wearing a derivation's clothes. **They are indistinguishable from the outside
without a must-fire arm** — which is why `detector_selftest()` is the load-bearing
part of this repair and not the index plumbing. p32's predicate is now false for a
reason about the *program* (`regs[r]` and `freehead` are `NIL` or a real slot, and
both rungs test for `NIL`), i.e. it has been moved from the second class to the
first. Written into `NOTES.md` §11g. **`p04` was not touched** — out of scope, and
it is not a defect.

---

## 2. M2 — `c/kernel.h`'s THREE SITES, and a third copy the review did not name

`c/kernel.h:73` and `:143` now say **ONE site**, with the stale-text history
named inline so the correction is auditable rather than silent.

⚠ **`inputs/gen.py:29` carried the same sentence** — *"`gen[h] != g` at the three
handle-consuming sites"*, immediately above a snippet showing one `if/else if`.
Same defect, one file over, in a **measurement-hashed** file, so fixing it was
free at the margin of the re-measure M2 already required. **Disclosed as an
extension of M2 rather than taken silently.** `gen.py` was re-run and **all nine
matrix blobs are byte-identical** (`.temp/t147/blobs_before.txt` vs
`blobs_after.txt`), so no blob hash moved.

Every surviving occurrence of *"three sites"* / *"four operations"* in the
pattern is now inside a sentence that is retracting it. Verified by grep.

---

## 3. M3 — `storage_arms.py`'s two narrowings, plus a trap found while fixing them

**3a. The `c-arena` description.** It said *"the SHIPPED C kernels … exactly as
`harness/build.py` builds them"*; `build()` never compiles anything out of
`../c/` and never calls `harness/build.py`. The docstring now says what it is
(`arm_malloc.c -DP32_ARENA`), names `PROTOCOL` rule 13's shape, and **cites the
reviewer's measurement rather than re-deriving it**: the SHIPPED `c/kernel.c` and
`c/kernel_hardened.c` on this control's own five op streams, **10 of 10 cells, 0
mismatches** (`TASK_145_REPORT` §2c, `.temp/t145/shipdrv/main_hex.c`). The inline
comment in `build()` was updated to match, because it was the half that had
stayed true while the header rotted.

**3b. *"Storage the only variable"* is narrowed to *"…in the kernel"*** in
`storage_arms.py`'s title, `README.md` and `NOTES.md` 2. New **`NOTES.md` §2e**
enumerates the complete six-item difference including the **17-line teardown**,
and keeps the evidence that the aborts are the bug: ASan puts
`attempting double-free` at `arm_body.inc:112` and `heap-use-after-free` at
`:119`, while the teardown's `free` at `:148` appears in no trace. **All three
line numbers re-verified against the shipped `arm_body.inc` this task** —
`grep -n 'free(blk\['` gives 112 and 148, and `sed -n 119p` is the payload read.

**3c. ⚠ A trap found while doing 3b, and it would have bitten the next agent.**
`storage_arms.py::main` enumerated its builds with `os.listdir(BIN)` on
`.temp/build/p32-arms` — **and `forgeable.py` writes its binary into that same
directory.** Any stray executable is then enumerated as a build, run with `ctl`,
fails to fire the positive control, and lands in `positive_control_dead_builds`
— **a red headline control caused by a neighbour.** Found because `repro.py`'s new
negative control would have been the second offender. Closed at both ends:
`build()` now **returns the names it made**, and `repro.py` builds into
`.temp/build/p32-repro`.

---

## 4. Ride-along 1 — `X3-spec-only-weaken`, and the R5 headline becomes a three-cell result

**The reviewer's arm was taken; its verdict was RE-DERIVED, not quoted.**

```
  M0-control               control     expect=verify got=verify OK  15/0 []
  M1-generation-conjunct   attack      expect=fail   got=fail   OK  14/1 ['assertion failed']
  M2-constant-body         vacuity     expect=fail   got=fail   OK  12/1 ['postcondition not satisfied']
  M3-nil-test              attack      expect=fail   got=fail   OK  14/1 ['precondition not satisfied']
  M4-spec-weaken           must-verify expect=verify got=verify OK  15/0 []
  X3-spec-only-weaken      attack      expect=fail   got=fail   OK  14/1 ['assertion failed']
  M5-freehead-range        deletion    expect=fail   got=fail   OK  14/1 ['precondition not satisfied']
  M6-nx-init               deletion    expect=fail   got=fail   OK  14/1 ['invariant not satisfied at end of loop body']
8 of 8 behaved as expected
```

| the conjunct is deleted from | verdict |
|---|---|
| the **exec code** only (`M1`) | **fail** `14/1` |
| the **specification** (`step`) only (`X3`) | **fail** `14/1` |
| **both** (`M4`) | **verify** `15/0` |

**`X3` is what rules out *"`step`'s conjunct is inert"*.** The battery shipped
`M1` and `M4` and asserted the conclusion; it now measures it. Kept under the
reviewer's name `X3-spec-only-weaken` so `TASK_145_REPORT` §3's citation
resolves, and placed immediately after `M4`. `NOTES.md` 6b and `README.md` carry
the three-cell table.

---

## 5. Ride-along 2 — `repro.py`'s negative control

```
  adversarial-stale-read.bin   R1= 1/20  R1h= 1/20   R1 DIVERGES
  adversarial-recycle.bin      R1= 1/20  R1h= 1/20   R1 DIVERGES
  adversarial-doublefree.bin   R1= 1/20  R1h= 1/20   R1 DIVERGES
  adversarial-alias.bin        R1= 1/20  R1h= 1/20   R1 DIVERGES
  adversarial-many.bin         R1= 1/20  R1h= 1/20   R1 DIVERGES
  degenerate.bin               R1= 1/20  R1h= 1/20   agree
  small.bin                    R1= 1/20  R1h= 1/20   agree

  NEGATIVE CONTROL  arm_aslr.c   20/20 distinct   randomize_va_space=2   FIRED
```

`controls/arm_aslr.c` (new, flat in `controls/` for `TASK_144` §9's digest
reason) runs through **the same twenty-run counter as every cell above**, and
`repro.py` now **exits non-zero if it does not fire**. `randomize_va_space` is
recorded in the sidecar.

⚠ **It is deliberately p32's OWN `c-malloc` failure mode** — free a chunk, read
user offset 0, get glibc's safe-linked `next` derived from the heap base — so the
negative control and the `NOT REPRO` contrast the pattern publishes are **the
same mechanism**, in eight lines. **I did not use `p29`'s R1** (the reviewer's
route, which also works): it couples this control's `derived_from_sha256` to
another pattern's sources, so a `p29` edit would report `p32`'s control STALE.

---

## 6. Ride-along 3 — the four minors

1. **`Pool`'s docstring.** *"no generation counter anywhere"* → **no counter in
   the STALENESS TEST**, with `rel[]` named as what it is (a release count that
   makes the fold agree) in both the class docstring and the module docstring's
   independence bullet.
2. **`arm_forgeable.c`'s `alias` flag is now a real liveness test**, not just a
   narrowed label: `checked_out[]`, set at ALLOC and cleared at an accepted FREE.
   ⚠ **Measured both ways, which is the positive/negative pair the old flag could
   not have:**

   | variant | free list simple | handed out while already checked out | exit |
   |---|---|---|---|
   | shipped `arm_forgeable.c` | **NO — cyclic** | **YES** | 0 (it broke, as it must) |
   | + the reviewer's fix (`.temp/t147/forge_neg/arm_fixed.c`) | YES | **no** | **1 — *"did NOT break"*** |

   Under the OLD flag the second row would have printed `simple: YES` **and**
   `ALIAS ONE BLOCK: YES` together — the self-contradiction the reviewer hit.
   The transcript in `NOTES.md` 1b is the new one, verbatim.
3. **`spec.md`'s *"four operations"* → five**, in the prose **and** in the hashed
   `why`. `arm_forgeable.c:10` carried the same error and was fixed too.
4. **`NOTES.md` §10's rule and denominators.** Counted, not asserted: the gate
   requires one section per `harness/check.py::_is_trusted` item —
   `#[verifier::external_body]` **with a non-empty `ensures`** — and

   | | `external_body` items | sections the gate required |
   |---|---|---|
   | `p32` | **5** | **3** |
   | `p27` | 7 | 5 |
   | `p29` | 7 | 7 |

   `load_input` and `emit` carry no `ensures`, so the gate does not govern them.
   §4's *"TCB: FIVE … `p27` and `p29` ship SEVEN"* is the item count and is
   **correct**; §10 was the one mixing the two. ⚠ `spec.md`'s `miri.reason`
   *"p32 has three"* is **also correct** under `_is_trusted` and was **not**
   changed — checked before touching it.

---

## 7. ⚠⚠ THE COST THE TASK FILE DID NOT NAME, and why I closed it rather than stopping

After the re-gate, `python3 synthesis/synthesize.py` published **`LICENCE STALE`
for p32 in four tables** where it had said `LICENSED`. The mechanism is working
as designed: `synthesis/licence.json` pins the gate `source_sha256`, and any doc
edit moves it. **This is a standing consequence of every correction task and the
task file does not mention it.**

The rule says stop rather than half-land. **I checked the cost first, to
scratch,** because `licence.py --emit` refuses to write if any cell is unbuilt:

```
$ python3 synthesis/licence.py --emit .temp/t147/licence_try.json
wrote .temp/t147/licence_try.json: 28 patterns, 112 pair verdicts (LICENSED, NOT-LIC, UNDEC)
```

**Seconds, no rebuild needed, no `NOT-BUILT`.** And the diff against the
committed sidecar is the reason to land it:

```
leaves 2246 -> 2247;  moved 12 of 2247
patterns touched: ['p32']
any VERDICT moved? NONE
```

**All twelve are p32's own `gate_source_sha256` entries. Zero verdicts, zero
cells, zero other patterns.** ⚠ **That is itself the strongest evidence in this
report that the task moved no instruction anywhere**: the licence tag is a
disassembly property of the built `-O3 isolated` matrix, and it is bit-identical.
With it refreshed, **`results/synthesis.md` is BYTE-IDENTICAL to `HEAD`** (the
one surviving `LICENCE STALE` string is the legend explaining the mechanism).
`results/SYNTHESIS.md` (CAPITALS) verified untouched by sha256 before and after.

**If the manager disagrees, `git checkout synthesis/licence.json` restores the
old pin and `synthesize.py` will publish four `LICENCE STALE` rows instead;
nothing else depends on it** (`licence.json` is in no gate digest and in no
`measurement_sources`).

---

## 8. THE CONTRACT HASH MOVED, AND THIS DISCLOSURE NEEDS NO GITIGNORED ARTEFACT

```
HEAD  contract_sha256  80059fefdd89a443f1393e5e5ae2cbc18ce969c13d3ad80e61fea091bb365f26
tree  contract_sha256  4611eff514dcbd21ee3822eca242a8bff2e79e110a2340e307b4b63fba0c4aed
```

⚠ `TASK_145_REPORT` §11 recorded, correctly, that it **could not reproduce**
`TASK_144`'s hash-move disclosure, because that check needed
`.temp/t144/spec/mkspec.py`'s output and gate logs which are gitignored — *"a
real gap in the evidence chain"*. **`p32` is now committed, so the pre-edit
`spec.md` is in `git`, and `.temp/t147/contract_diff.py` closes the gap for this
move and every future one:** it parses the `slb-contract` JSON out of
`git show HEAD:…` and out of the tree and diffs the dicts key by key, recursing
into `idiom`.

```
  collapse   IDENTICAL     kernel     IDENTICAL     note       IDENTICAL
  driver     IDENTICAL     miri       IDENTICAL     requires   IDENTICAL
  ensures    IDENTICAL     model      IDENTICAL     verus      IDENTICAL
  identity   IDENTICAL
  idiom      ⚠ MOVED
    idiom.forbidden  IDENTICAL
    idiom.required   IDENTICAL
    idiom.why        ⚠ MOVED   (the DERIVES sentence + retraction; `four` -> `five`)
2 path(s) moved out of 11 top-level key(s): ['idiom', 'idiom.why']
```

**`required`, `forbidden`, `verus`, `driver`, `collapse`, `identity`, `miri`,
`model`, `kernel`, `requires`, `ensures` and `note` are byte-identical.** The
`sha_of_block` helper spells `check.py::read_contract`'s exact regex, so the
number it prints **is** the gate's. Recorded in `NOTES.md` §0 with a forward
pointer, per definition-of-done item 6's *"if the hash changes later, say so and
say why"*.

⚠ **I did not edit `.temp/t144/spec/mkspec.py`** (forbidden directory). The
artefact-vs-generator skew is therefore **open and disclosed**: `spec.md` was
generated once by that script and has now been hand-edited twice (once at
`TASK_144`, once here). ⚠ **Re-running `mkspec.py` today would revert both.**
`.temp/t147/contract_diff.py` is the check that replaces it and does not depend
on a gitignored file. **Recommend the manager either promote a generator into the
pattern or record that `spec.md` is now hand-maintained.**

---

## 9. THE RE-MEASURE — the prediction, stated first, then the result

**Stated before the run:** wall-clock, timestamps and three source hashes move;
`Ir`, md5, identity, checksum **and `model_stdout`** do not. ⚠ The task file
allowed a `model_stdout` move under option (a); **I claimed none, because the
checked path is untouched and the buggy path's result was already discarded.**

```
leaves: before 1366  after 1365  moved 103 of 1366
     96  wall-clock  (median_s / min_s / spread_pct)
      3  source_sha256   c/kernel.h, inputs/gen.py, model.py
      2  git
      1  timestamp
      1  a `warning` leaf that VANISHED

SANITY: any Ir / md5 / identity / checksum / model_stdout leaf moved?   NONE
```

**Zero blob hashes moved.** And, independently, the model's own answers:
`.temp/t147/model_before.txt` vs `model_after.txt` — checksum, `sanitizer_expect`,
`expected_exit`, `n_calls`, `work_per_call`, `nwin`, `selfcheck()` and eight
`pool_fold` samples for **all nine inputs** — **`diff` is EMPTY.** The nine
checksums also still match `TASK_145_REPORT` §4a's independent `driver_replay.py`
figures exactly.

⚠ **The one leaf that vanished is worth naming, because it changes a published
artefact.** `cells/7 / small.bin`'s min-to-median wall-clock spread was **11.73%**
and is now **3.76%**, so the `spread > 10% -- discard` warning cleared. **The
rendered table therefore no longer carries its one ✗-marked discarded cell**
(`results/tables/p32-free-list-pool.md`, 46 lines differ). It is a wall-clock
artefact of one run, **p32 publishes no cost headline at all**, and no claim
anywhere rests on it — but `TASK_145_REPORT` §7 mentions that cell, so it is
recorded here rather than left to be noticed.

---

## 10. GATE AND TOOLING — every command, and the actual output

```
harness/measure.py p32              wrote results/p32-free-list-pool.json      (rc 0)
harness/check.py p32  (run A)       FAIL -- [tables] ONLY, x2, both the documented
                                    "contract moved, run report.py" pair
harness/report.py p32               wrote results/tables/p32-free-list-pool.md (rc 0)
harness/check.py p32  (run B)       PASS
  verdict      PASS
  failures     []
  blocked      []            <- read out of the RECORD JSON, never grepped
  complete_run True
  contract     4611eff514dcbd21ee3822eca242a8bff2e79e110a2340e307b4b63fba0c4aed
  controls     forgeable FRESH  proof_mutants FRESH  repro FRESH
               safety_line FRESH  storage_arms FRESH
  loud         1   ([tcb-unsafe] arr_set_unchecked's `x`, the parameter-coverage
                    false positive `.memory/04-verus.md` names; p32 is the 7th)
  idiom audit  forbidden: 28 spelling(s), 0 hit(s), 0 entries with no backticks

harness/measure.py --check-stale    56 record(s) examined, 0 STALE
harness/tools/composition.py --check OK, 28 patterns / 10 classes, p32 temporal + caveat
harness/tools/temp_citations.py     OK  (new=0 unclassified=0 resolved=0)
synthesis/licence.py --emit         28 patterns, 112 pair verdicts, no NOT-BUILT
synthesis/synthesize.py             results/synthesis.md BYTE-IDENTICAL to HEAD
results/SYNTHESIS.md                sha256 verified UNCHANGED, before and after
```

**`blocked` across all 28 committed records, read from the JSON:** `p01 = 1`
(miri), `p42 = 1` (miri), **everything else 0, total 2**, and **`p32 = 0`** — the
expected figures, and `p42` is at 1 rather than the permitted 2.

**Control regeneration, all after the sources were final** (`TASK_139`'s lesson),
all `rc=0`, log in `.temp/t147/controls.log`:

```
storage_arms.py   positive control FIRED in 10 of 10 C builds; dead builds []
                  safe Rust == the C ARENA rung on 10 of 10 (input, arm) cells
forgeable.py      the hardened forgeable variant still breaks; alias now DECIDED
safety_line.py    preprocessed diff +2 / -0, `gen[h] != g` at exactly 1 site
repro.py          every cell 1/20; NEGATIVE CONTROL 20/20 at randomize_va_space=2
proof_mutants.py  8 of 8 as expected
```

---

## 11. INSTRUMENT FINDINGS, recorded rather than quietly repaired

1. ⚠⚠ **`storage_arms.py` enumerated its builds with `os.listdir` on a directory
   `forgeable.py` also writes into.** A neighbour's binary would have painted the
   row's headline control red via `positive_control_dead_builds`. §3c. **Fixed at
   both ends**; found only because the new negative control would have been the
   second offender.
2. ⚠ **A gate re-run that moves `source_sha256` silently stales
   `synthesis/licence.json`.** §7. Cheap to clear on a warm build tree, **fatal to
   clear on a cleaned one** — `licence.py --emit` dies rather than writing, which
   is `TASK_075_REVIEW` M2's guard working. **Worth a line in
   `.memory/03-measurement.md`'s correction-cost table, which currently lists
   `contract_sha256` / gate / measure and not this.**
3. ⚠ **The `NOT REPRO` cell's record is now EIGHT values, and two of them come
   from the SAME script invocation seconds apart** — the summary row's
   `malloc-plain` reads `33234` while the per-build matrix's `malloc-plain` reads
   `35776`. That is a sharper demonstration than any cross-build spread, and it is
   in `NOTES.md` 2 **explicitly labelled as measurements OF the
   non-reproducibility, never as values** — which is the distinction
   `TASK_145_REPORT` §9 found `RECAP` 55 had lost.
4. **Verus obligation counts are stable across the battery**: `15/0` shipped,
   `14/1` for every attack arm, `12/1` for the constant body. `X2b`/`X4`'s
   observation that `15/0` is not a discriminator (`TASK_145_REPORT` §3) is
   unchanged and untouched — see §12.

---

## 12. WHAT I DID NOT DO

* ⚠ **`check.py`'s `assume(false)` shout.** The task file said leave it and I
  **agree**, on the evidence: `p32`'s own `assume(`/`admit(` count is **0**,
  `check.py` is in the gate digest, and changing it is a 28-pattern re-gate.
  Recorded, not touched.
* **`RECAP.md` finding 54's `p32 +9/−0` with no forward pointer**, and finding
  55's copies of M1 and of the `35094` figure. Manager-owned; **`NOTES.md` §11
  is written so it can be lifted into `RECAP` 55 directly.**
* **`.memory/`, `RECAP.md`, `results/SYNTHESIS.md` (CAPITALS)** — untouched, and
  the last verified by sha256.
* **`p04` was not touched** (`mgr150`) — correct as it stands, and out of scope.
* **I did not re-gate any other pattern** and did not run the tree sweep.
  `--check-stale`, `composition.py --check` and `temp_citations.py` are the
  whole-tree checks I ran.
* **I did not re-derive `TASK_145_REPORT` §2c's 10/10 shipped-rung run**, §2a's
  `cc -E -P` line counts, or §2b's ASan traces. The task said cite them; I did,
  and I **did** re-verify the three `arm_body.inc` line numbers (112/119/148)
  against the shipped file.
* **I did not edit `.temp/t144/spec/mkspec.py`** — forbidden directory. The
  generator skew is disclosed in §8 rather than fixed.
* **`sweep-*` bands**: not generated, nothing measured on them, unchanged.

## 13. UNSURE

* ⚠ **The `synthesis/licence.json` refresh (§7) is the call I am least sure of.**
  It is a whole-tree artefact and the task file did not authorise it. My argument
  is that the diff is provably confined to p32's pin, `results/synthesis.md`
  returns to byte-identical, and the alternative publishes four `LICENCE STALE`
  rows for a tag that did not move. **One `git checkout` reverses it.**
* **Whether `inputs/gen.py`'s "three handle-consuming sites" was in scope.** It
  is the same wrong sentence as M2, in a measurement-hashed file, at zero
  marginal cost — but it is an extension. Disclosed in §2.
* **Whether `X3` should have been renamed `M7`.** I kept the reviewer's name so
  `TASK_145_REPORT` §3's citation resolves; it makes the battery's naming mixed.
* **`detector_selftest()` runs on every input, so its two probes run 9 times per
  gate.** Cost is microseconds and the redundancy buys nothing, but making it
  run once would mean module-level state, which is worse.

---

## 14. EVIDENCE

```
patterns/p32-free-list-pool/model.py            M1: the real detector + must-fire arm
patterns/p32-free-list-pool/NOTES.md            0 (hash move), 1b, 2, 2a, 2d, 2e, 6b, 10, 11
patterns/p32-free-list-pool/spec.md             the hashed why, retraction + `five`
patterns/p32-free-list-pool/README.md           derivation, 3-cell R5, negative control
patterns/p32-free-list-pool/c/kernel.h          M2: ONE site, twice
patterns/p32-free-list-pool/inputs/gen.py       M2's third copy
patterns/p32-free-list-pool/controls/
    storage_arms.py                             M3: c-arena, the teardown, the listdir trap
    proof_mutants.py + .json                    + X3-spec-only-weaken, 8 of 8
    repro.py + .json                            + the negative control
    arm_aslr.c                                  NEW -- the negative control's arm
    arm_forgeable.c + forgeable.json            the alias flag made a liveness test
    safety_line.json                            re-pinned (c/kernel.h moved under it)
results/p32-free-list-pool.json                 the re-measure
results/gate/p32-free-list-pool.json            PASS, blocked []
results/tables/p32-free-list-pool.md            re-rendered at contract 4611eff514dc
synthesis/licence.json                          p32's pin only; zero verdicts moved
.temp/t147/NOTES.md                             an index of everything below
.temp/t147/mustfire_probe.py + .log             M1's evidence, from outside model.py
.temp/t147/contract_diff.py + .log              the hash-move disclosure, git-based
.temp/t147/forge_neg/arm_fixed.c                the forgeable control's negative arm
.temp/t147/model_before.txt / model_after.txt   diff EMPTY -- no answer moved
.temp/t147/record_diff.log                      103 of 1366, none of them Ir
.temp/t147/licence_diff.log                     12 of 2247, zero verdicts
.temp/t147/gateA.log gateB.log measure.log report.log controls.log proof_mutants.log
.temp/t147/blobs_before.txt / blobs_after.txt   gen.py still writes the same bytes
```

Binaries are deleted; `harness/build.py`, `inputs/gen.py`, the five
`controls/*.py`, `mustfire_probe.py` and the one `gcc` line in
`.temp/t147/NOTES.md` rebuild every one of them.

---

**PROTOCOL rule 2 running count: launched from 733 (`TASK_145_REPORT.md`'s
closing paragraph), carried to 745** — branch delta **+12**:

1. **M1 landed as option (a), and it is now a measurement**: `TASK_145`'s own
   20 000-window falsifier fires **19 622/20 000** with the guard deleted and
   **0/20 000** with it present, against **0/20 000** for the old detector.
2. **The distinguishing sentence the manager asked for**: a predicate false by a
   fact about the PROGRAM (`p04`) and one false by a fact about the MODEL (`p32`
   as shipped) are indistinguishable from outside **without a must-fire arm** —
   which is why the arm, not the plumbing, is the repair.
3. ⚠ **`storage_arms.py` enumerated builds with `os.listdir` on a directory
   `forgeable.py` writes into** — a neighbour's binary would have failed the
   headline control's positive control.
4. ⚠ **A gate re-run that moves `source_sha256` stales `synthesis/licence.json`
   and publishes `LICENCE STALE`.** Not in any cost table.
5. **The licence re-emission is itself a proof of no-op**: 12 leaves, all one
   pattern's pin, **zero verdicts** — a disassembly-level check that the whole
   task moved no instruction.
6. `X3-spec-only-weaken` **re-derived** at `14/1 assertion failed`; the R5
   headline is now exec-only fail / spec-only fail / both verify.
7. `repro.py`'s negative control gives **20/20 at `randomize_va_space = 2`**, and
   is p32's own `c-malloc` failure mode rather than an unrelated entropy source,
   so it does not couple the sidecar to `p29`.
8. `arm_forgeable.c`'s alias flag is a liveness test, with **both arms measured**
   — the shipped variant breaks, the reviewer's fixed variant exits 1.
9. ⚠ **The `NOT REPRO` cell disagreed with ITSELF inside one script invocation**
   (`33234` vs `35776`, same binary, seconds apart) — eight recorded values now.
10. **The contract-move disclosure needs no gitignored artefact** once a pattern
    is committed: `git show HEAD:spec.md` is the snapshot, which closes
    `TASK_145_REPORT` §11's named gap for every future move.
11. ⚠ **`spec.md` is now hand-maintained**: `mkspec.py` lives in a forbidden
    directory and would revert both edits. Disclosed, not fixed.
12. The re-measure **removed the pattern's one ✗-discarded wall-clock cell**
    (spread 11.73% → 3.76%), which is the first time a comment-only correction
    has changed what a published table shows.

⚠ **A rigour signal, not a ledger — reconciliation across branches is the
manager's job, not mine.**
