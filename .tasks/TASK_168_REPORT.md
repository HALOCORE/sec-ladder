# TASK_168 REPORT — the backlog bundle

**Role: research engineer.**

⚠⚠⚠ **HEADLINE: item A does NOT close for free, and it does not close because the
bar in the task file is the wrong bar.** The question exactly as posed — *"does
any single `mem*` call exceed **8192** bytes?"* — has the answer **no**, and
answering it as posed would have closed the item while missing **both** live
instances. Both are **4096-byte `memset`-class** transfers, and `memset`'s
byte-wise threshold is **2–3 KiB**, which `.memory/03-measurement.md` records
three lines above the 8192 figure. One of the two is **new, asymmetric, on the
pattern's own axis, and printed in `results/synthesis.md`**. A second mechanism
the framing excludes entirely — an **inlined** `rep` — turns out to be live on
**nine** patterns where `.memory/` says *"only p08's"*.

**Final state: 33/33 gate-green — 30 `PASS` + 3 `PASS-WITH-BLOCKED-ROWS`, 0
failures, `blocked` `p01` 1 / `p35` 3 / `p42` 1 — exactly the expected figures.**

⚠⚠ **TWO BUDGET OVERRUNS, both forced by the gate, both disclosed below:** a
re-measure stales the pattern's **published table** (5 `report.py` + 6 extra
single-pattern gate runs), and `p35` had **three** stale sidecars, not two.
⚠ **AND ONE ITEM I DID NOT SPEND, PER THE RULE:** `synthesis/outward_ir.json` is
now **stale on all 33 patterns** and re-emitting is **352 callgrind runs**.
**Stopped and reported.**

---

## Did

### A. Item 28 — answered first, statically, before any edit

Full write-up: **`.temp/t168/ITEM_A.md`**. Instruments and raw output:
`.temp/t168/A_outward_max.txt`, `A_bulk_calls.txt`, `A_asym.txt`,
`rep_scan.py` + `rep_scan.log` + `rep_scan.json`.

### B. Item 12 — eight citations, five patterns, all re-cited by function; plus the check

| file | was | now |
|---|---|---|
| `p12-strcat-fixed/inputs/gen.py` | `check.py:1249-1278` | `check.py::check_checksums`, `check.py::inputs_of` |
| `p13-strncpy-trunc/inputs/gen.py` | `check.py:1249-1278` | same |
| `p13-strncpy-trunc/model.py` | `check.py:1249-1278`, `check.py:469` | `check.py::check_checksums`; `check.py::inputs_of` **with its comment quoted** |
| `p16-tlv-walk/model.py` ×2 | `check.py:625`, `check.py:625`+`:632` | `check.py::check_marginal_ir`, + the `rep.fail("collapse-ir", …)` text quoted |
| `p35-tagged-union/controls/rust_bug.py` | `check.py:8841` | `check.py::check_miri` |
| `p38-alias-pun/inputs/gen.py` | `check.py:459-460`, **`measure.py:60`** | `check.py::inputs_of`, `measure.py::SKIP_INPUT_PREFIX` |

New gate stage **`0c`** in `harness/check.py`: `check_doc_citations`,
`citation_verdict`, `line_citations`, `harness_module_names`. **Hard-fails** on
`check.py:NNNN` anywhere under the pattern; **reports** line citations into other
harness modules. Recorded as `doc_citations` in every gate record.
Six must-fire arms (`_CITE_VERDICT_CASES`).

### C. Item 31 — a header hoisted onto `check_marginal_ir`

Nine lines at the top naming both mechanisms with their magnitudes, pointing at
the two tables **by their own headline text** (not by a coordinate) and at the
operative rule. **The body is untouched** — no number in it moved.

### D. Item 33 — `vparse`'s unclassified-`global` fallback

`harness/vparse.py::axiom_decls`: line anchor → **preceding-non-space-character**
anchor over `{};]`. `]` is in deliberately, so an attributed `global` is seen and
this does not repeat `impl_spans`' documented `]` gap. Three new arms, **each
confirmed to fail against the old matcher**; one relabelled control; one widened
negative.

### E. Item 16(b) — `CODEGEN_CFGS` coupled to `build.py`

New gate stage **`0d`**: `check_codegen_cfgs`, `codegen_cfg_verdict`,
`build_cfg_flags`. It **tokenises** `build.py` — a grep counts `build.py`'s own
`--cfg` *comment* as a flag. `build.py` is **not** edited. Recorded as
`codegen_cfgs`. Six must-fire arms (`_CFG_VERDICT_CASES`).
Also fixed `CODEGEN_CFGS`' own `build.py:150` citation → `build.py::rust_flags`.

### F. Item 15 — measured, nothing changed

Severity untouched, nothing backticked. Answer below.

---

## Evidence

### A1 — the framing, refuted in three places

**(a) 8192 is the `memcpy`/`memmove` bar, not the `memset` bar.**
`.memory/03-measurement.md` records ***"`memset` flips at 3 KiB"*** and a
separately measured flip at **2 KiB**, and says ***"do not trust either
constant"*** — on the same page as the 8192 figure. Both live hits sit at
**4096 bytes: under the stated bar, over the real one.**

**(b) It is not only about a `memcpy`/`memmove`/`memset` CALL.** The p08 sentence
this item re-checks is about an **inlined instruction**
(*"gcc inlines `rep stos %rax` … Only p08's gcc kernels contain a `rep`
instruction"*), and the second live hit is `__rust_alloc_zeroed`, which carries
none of the three names — `asm.py::bulk_calls` records calls only, and p42's
`bulk_calls` list contains **no `memset` at all**.

**(c) "Answerable statically" — half.** The call/callee half is answerable **from
the records, better than statically** (614 callee edges with measured `Ir` per
callee call). The inlined-`rep` half is **not answerable from any committed
artefact** — nothing records mnemonics — and needed a disassembly, which was free
after the sweep.

⚠ Coverage: `synthesis/outward_ir.py::run_pattern` defaults `opt="O3",
mode="isolated"`, so the outward data is **one of four (level × mode)
quadrants**. ⚠ Minor: `outward_ir.json` *"names the callee"* only where a symbol
exists; glibc has none here, so every `mem*` is a bare address and I identified
them **by measured `Ir`/byte**.

### A2 — the size bound (nothing exceeds 8192)

```
p08  memset(scr, 0, P08_SCR)       P08_SCR = 4096u      <- largest in the tree
p42  vec![0u8; len] / malloc(len)  len = LARGE_WIN = 4096
p02  memcpy(dst, src+off+2, len)   len <= 4092 (TASK_074's evidence)
all other buffers <= 256 B: SCR 64 · TABCAP 32 ptrs · SLB_P46_BCAP 256 ·
                            SLB_P38_SCRATCH_W 256 · P34_DLEN 8 · P49_MEM 64
```

`P42_MAXWIN 65536` is a **ceiling, not a length**: only `adversarial-wincap.bin`
reaches it, at `MAXWIN + 1`, and the cap **rejects** it.

Corroborated from the records — max `outward_ir_per_callee_call` over all
**614** edges (33 patterns × 2 blobs × 8 cells) is **4828.00**, so **no
`memcpy`/`memmove` call anywhere is in the `rep movsb` regime**. That half
**closes**.

### A3 — the two `memset`-class hits, and `Ir`/byte separates them cleanly

| site | bytes | `Ir`/call | `Ir`/byte | path |
|---|---:|---:|---:|---|
| p02 `large` `0x188a80` memcpy | 4092 | 412.88 | **0.1009** | vector |
| p08 both blobs `0x189480` memset | 4096 | 4113.00 | **1.0041** | **`rep stosb`** |
| p42 `large` `alloc_zeroed − alloc` | 4096 | **4160.00** | **1.0156** | **`rep stosb`** |

(`.memory/03-measurement.md`'s own probe: `rep stosb` over 4096 B = 4110.00 `Ir`,
1.0034 `Ir`/byte. Both hits reproduce it to three digits.)

**Hit 1 — p08: known, symmetric, cancels.** 4113.00 `Ir` once per kernel call in
**all eight cells**; `p08/c/kernel.c`'s own header calls it *"a uniform per-call
constant in all six rungs"*, so it drops out of every pair. ✅ No p08 number moves.

**Hit 2 — p42: NEW, ASYMMETRIC, PUBLISHED.** `safe_naive` spells
`vec![0u8; len]` → `__rust_alloc_zeroed`; `safe_tuned`/`unsafe`/`verus` spell
`Vec::with_capacity` → `__rust_alloc`. Measured on `large.bin`
(`LARGE_WIN = 4096`):

```
safe_naive  __rustc::__rust_alloc_zeroed   4342.00 Ir/call   n=1.0/kernel call
unsafe      __rustc::__rust_alloc           182.00 Ir/call   n=1.0/kernel call
                                    delta  4160.00  =  1.0156 Ir/byte
```

On the vector path that zeroing prices at ≈426 `Ir` (0.104/byte), so
**≈3730 `Ir`/call — about 90% of the term — is counter artefact, not work.**
On `small.bin` (`SMALL_WIN = 97`) the term is +189.01 and is **not** in the
byte-wise regime, which is why only `large` is affected.

⚠ **It is published.** `results/synthesis.md` §2, `R2−R4`:

```
| p42-goto-cleanup | 599.00 | 25092.00 | NOT-LIC | **small +752.00** (+153.00) / **large +29252.00** (+4160.00) | undeclared |
```

`+4160.00` prints in **bold**, which that table's legend defines as *"at or above
16.00 every row is real"*. ✅ p42's kernel-**exclusive** published pair
(`+599.00 / +25092.00`) is immune, and the row is already `NOT-LIC` with the
`why` naming `__rust_alloc_zeroed`. ⚠ **What is wrong is the MAGNITUDE, by ~10×,
in the band labelled "real".** Per the task I stopped and did **not** re-measure.
✅ Chasing it would not need one: the correction is **derived**
(`synthesize.py::CALLEE_NOTE`), so the repair is a note plus a
`GLIBC_TUNABLES=glibc.cpu.x86_rep_stosb_threshold` control.

**Clean negatives, same instrument.** Every other edge ≥2048 `Ir`/call is a loop
of frees and prices as one: p29 `drop_glue<[Option<Box<Rec>>;32]>` 3246.60
(≈101/drop), p34 1505.75 (≈94/drop), p27 1252.36 (≈39/drop). p08's 4828.00 edge
runs **4e-05 times per kernel call** = 0.19 `Ir`/call amortised.

### A4 — ⚠⚠ `.memory/03-measurement.md`'s *"Only p08's gcc kernels contain a `rep` instruction"* is FALSE at 33 patterns

`.temp/t168/rep_scan.py`, run after the sweep against the built tree, over the
**same symbol `measure.py` counts** (`kernel` isolated / `main` whole):

```
scanned 1052 measured windows; 0 not built
windows containing an inlined `rep` string instruction: 26
patterns with any inlined `rep`: ['p06', 'p08', 'p14', 'p23', 'p27', 'p29', 'p32', 'p35', 'p46']
by cell/opt/mode: {('c-gcc','O3','whole'): 7, ('c-gcc-h','O3','whole'): 7,
                   ('c-gcc','O3','isolated'): 6, ('c-gcc-h','O3','isolated'): 6}
mnemonics: {'rep stos': 32, 'rep movsq': 2}
```

**NINE patterns, not one.** ✅ *"gcc"* and *"-O3"* are right — every one of the 26
is `c-gcc`/`c-gcc-h` at `-O3`, and **zero** clang or Rust windows. ✅ And all 34
instructions are the **word-wise** form (`%rax`/`%eax`), i.e. ≈0.126 `Ir`/byte —
so the direction is that **gcc's `Ir` UNDERSTATES its work** relative to clang
and to Rust, which is p08's documented `Ir`-vs-`ns` direction disagreement, on
nine patterns instead of one. ⚠ **The exposed column is `gcc-clang`, which
`results/synthesis.md` publishes; the R2/R3/R4/R5 pairs are untouched** (every
hit is a C cell).

### B — the citations

```
$ grep -rn 'check\.py:[0-9]' patterns/ | wc -l
0
```

⚠ **`p38` was rotten in BOTH coordinates and the item counted one:**
`measure.py:60` is inside the `CG_PLAN` list; `SKIP_INPUT_PREFIX` is at `:64`.

⚠⚠ **AND THE FATAL SET IS NARROWER THAN THE PROBLEM.** Stage 0c reports
**13 line citations into other harness modules across 6 patterns**, summed from
the gate records (`doc_citations.other`):

```
p12 README.md:48 -> measure.py:64        p19 inputs/gen.py:38 -> measure.py:64
p14 NOTES.md:623 -> measure.py:56        p22 inputs/gen.py:33 -> measure.py:64
p18 NOTES.md:758 -> build.py:66   <ROTTEN>   p36 inputs/gen.py:25 -> measure.py:64
p18 NOTES.md:762 -> build.py:26          p27 NOTES.md:342/605/1040/1747,
                                             controls/mkspec.py:361, spec.md:24
                                             -> dloop.py:361 ×3, measure.py:238 <ROTTEN>,
                                                build.py:67, measure.py:225
```

**Two are rotten right now**: `measure.py:238` (cited for staleness detection;
now `def matrix_inputs` — the glob it means is `:229`) and `build.py:66` (cited
for the `O0d` level; now `ALL_CELLS` — `ALL_OPTS` is `:68`).
⚠ **So `.memory/02-bench-rules.md`'s clean negative *"Only `check.py` decays"* was
true of the `.memory/` layer at TASK_066 and is NOT true of the pattern layer
today.** Left as a report, not a fail, because promoting it costs **three extra
MEASUREMENT re-runs** (`p19`, `p22`, `p36` each cite `measure.py:64` from
`inputs/gen.py`). **The manager's call; the data is in the records so nobody
re-derives it.**

**What it would have cost historically:** nothing today (0 hits); it would have
fired on **25 citations / 13 patterns** at TASK_068 and on the residual **8 / 5**
from then to now — exactly the set that kept being written.

⚠ **`.memory/` has SIX of its own and at least two are rotten** — the task file
names `03-measurement.md:3146 → check.py:2387` and `:3375 → check.py:2805`.
**Not edited: `.memory/` is the manager's.** ⚠ Stage 0c does **not** scan
`.memory/` (it is per-pattern), so this is a report, not a check.

### C — the docstring header

Inserted after the summary line; the 250-line body is byte-unchanged. It names
mechanism (1) (environment block, `±0.20 … ±7`) and mechanism (2)
(whole-program slope carrying callees, `+1732.73`), says **38×**, and points at
both tables by their headline text and at *"THE OPERATIVE RULE"*.

### D — the `global` arm, confirmed to fail against the old matcher

`.temp/t168/global_arm.py` rebuilds the line-anchored predicate by string
substitution (**asserting the substitution count**, CLAUDE.md) and runs both:

```
case                                                       OLD          NEW  arm fires?
unknown `global` after `}` ON THE SAME LINE                 [] [('global',   YES (old!=new)
unknown `global` after `;` ON THE SAME LINE                 [] [('global',   YES (old!=new)
unknown `global` after an ATTRIBUTE                         [] [('global',   YES (old!=new)
--- control: KNOWN `global size_of` sharing a line  [('global si [('global si  no  (old==new)
--- negative: a LOCAL named `global`                        []           []  no  (old==new)
--- the pre-existing OWN-LINE arm                  [('global',  [('global',   no  (old==new)
vparse selftest: PASS
RESULT: OK
```

⚠⚠ **The probe caught a vacuous cell in my own first arm set and I fixed it.**
*"a KNOWN `global` sharing a line is still classified"* was written as a
must-fire arm and **passes under both matchers** — the two known forms were never
line-anchored, only the unclassified fallback was. It is now **labelled a
CONTROL** in `vparse.py` and in the probe. **Calling it an arm would have been
queue item 33's own defect one level further down.**

**Clean negative on the shipped tree:** old vs new matcher over every tracked
`.rs` —

```
152 tracked .rs scanned; 0 whose axiom_decls MOVED under the widened anchor
total `global*` declarations seen by the NEW matcher: 10
Counter({'global size_of': 7, 'global layout': 3})
```

which reproduces `.memory/`'s TASK_164 census exactly.

### E — the `CODEGEN_CFGS` cross-check

```
== 0d. CODEGEN_CFGS covers every `--cfg` harness/build.py passes =====
    ok   build.py passes --cfg ['slb_isolated']; all in CODEGEN_CFGS (18 names)
```

Must-fire arms include the one a **grep** gets wrong:
`codegen_cfg_verdict('# forwards --cfg slb_bogus verbatim\nx = 1\n')` must be
`("OK", [], 0)`, and `'f += ["--cfg", "slb_bogus"]'` must be
`("FAIL", ["slb_bogus"], 0)`. A `--cfg` whose value is not a literal is counted
`unresolved` and **shouted**, never dropped.

⚠ **Both new stages' arms are placed ABOVE `check_selftests`' `fixture.ensure()`
early return** — RECAP queue item 34's defect, which every existing arm sits
behind. The existing arms are **not** moved (out of scope).

### 3/4 — the re-measure prediction, written before the run

`.temp/t168/PREDICTION.md` → `.temp/t168/PREDICTION_OUTCOME.md`. All four
`rc=0`.

| class | predicted | p12 | p13 | p16 | p38 | |
|---|---|---:|---:|---:|---:|---|
| `generated_utc` | 1 | 1 | 1 | 1 | 1 | ✓ |
| `git` | 2 | 2 | 2 | 2 | 2 | ✓ |
| `source_sha256` | 1/**2**/1/1 | 1 | 2 | 1 | 1 | ✓ exactly the five edited files |
| **`ir`** | **0** | **0** | **0** | **0** | **0** | ✓ |
| **`checksum`** | **0** | **0** | **0** | **0** | **0** | ✓ |
| **`static`/md5** | **0** | **0** | **0** | **0** | **0** | ✓ |
| `input_sha256` / `inputs` | 0 | 0 | 0 | 0 | 0 | ✓ |
| `timing_cpu` | 0 | 0 | 0 | **1** | 0 | ✗ |
| wall clock | 96 | **129** | **129** | **101** | **103** | ✗ |
| **total** | 100/101/100/100 | 133 | 134 | 106 | 107 | |

**The deterministic half was exactly right.** Zero `Ir`, zero checksum, zero
md5, zero static count, zero input hash — the docstring-only argument held.

⚠⚠ **The wall-clock half was wrong, and the reason is worth keeping: I PREDICTED
FROM THE RECORD'S CONTENTS AND THE MOVERS WERE THE COMMAND'S ARGUMENTS.** Two
fields I read as constants are `argparse` defaults:

* **`reps`** — `p12`/`p13`'s committed blocks were taken at **`--reps 31`**; the
  default is **30**. So all **four** wall fields moved on those two, not three.
* **`timing_cpu`** — `p16`'s block was taken on **`--cpu 5`**; the default is
  **3**. That is why `p16`'s four `>10%` spread warnings vanished.

Plus `protocol.wall`, a prose string that interpolates both. Fully accounted:
`p12/p13 = 32×4 + 1 = 129`; `p16 = 32×3 + 4 warnings + 1 = 101`;
`p38 = 32×3 + 7 warning-key diffs = 103`.

⚠ **This silently retired two non-default protocols.** `p12`/`p13` are now
`reps 30` (were 31) and `p16` is `cpu 3` (was 5). The four are now mutually
consistent, which they were not — **but it was unintended, nothing in the tree
recorded those choices as deliberate, and if either was, this run destroyed it.**
⚠ **`p38` now flags 10 of 32 wall cells at `>10%` spread, against 5**, on
byte-identical binaries with identical `Ir` — box noise, but the flag count is a
published-artefact input.

### 6 — the sweep

33 patterns, one pass, background, waited on a `.done` sentinel (**no `pgrep -f`
waiter**). `harness/check.py` and `harness/vparse.py` were **frozen before it
started** (`.temp/t168/FROZEN.txt`, md5s recorded) and **not touched again**.

First pass: **28 `rc=0`, 5 `rc=1`** — `p12 p13 p16 p38` (`tables`) and `p35`
(`tables` ×4). **Both causes are forced staleness, not defects**, and both are
disclosed as overruns below. After the repair chain:

```
verdicts: {'PASS': 30, 'PASS-WITH-BLOCKED-ROWS': 3}
failures anywhere: 0
blocked: {'p01': 1, 'p35': 3, 'p42': 1}
```

⚠ Read from the **records**, never by grepping a log (`.temp/t168/final_verdicts.txt`).
`p42` is 1, not 2.

### 7 — `p35`'s sidecars: THREE, not two

```
proof_mutants rc=0  17s
union_oracle  rc=0   3s
rust_bug      rc=0   2s
```

⚠⚠ **`rust_bug.json` was stale too — it pins its own generator
`controls/rust_bug.py`, which item B edited.** The task file's budget derivation
put `patterns/*/controls/*.py` under *"gate digest only"* and did not notice that
a `controls/*.json` sidecar pins its generator. `.memory/05-layout.md`'s
*"3 of 46 sidecars pin something under `harness/`"* is right about `harness/` and
is **not the whole trigger set**.

⚠⚠⚠ **AND REGENERATING IT MOVED A PUBLISHED NUMBER — this is the sharpest
finding of the task.**

```
-        "rc": -11,                        (SIGSEGV)
+        "rc": -7,                         (SIGBUS)
-      "unsafe_reproduces_c": true,
+      "unsafe_reproduces_c": false,
```

on `adversarial-ptr-confusion.bin`. Measured, `.temp/t168/p35_signal_probe.sh`,
40 runs each:

```
adversarial-ptr-confusion    arm-unsafe  rc=139:37 rc=135:3
adversarial-ptr-confusion    c-r1        rc=139:40
adversarial-ptr-confusion    arm-safe    rc=101:40
adversarial-ptr-deep         arm-unsafe  rc=139:38 rc=135:2
adversarial-ptr-deep         c-r1        rc=139:40
adversarial-ptr-deep         arm-safe    rc=101:40
```

**The Rust unsafe arm's signal is a TWO-STATE DRAW — SIGSEGV ≈93%, SIGBUS ≈7%,
on BOTH ptr inputs. The C rung and the safe arm are deterministic, 40/40.**

`patterns/p35-tagged-union/NOTES.md:369, 370, 1027` and `spec.md:116` publish
*"the unsafe arm SIGSEGVs, `rc=-11`, exactly as C does"* **as a fact**, and
`spec.md`'s hashed `why` says it too — *"controls/rust_bug.py refutes the natural
reading of that — the unsafe arm SIGSEGVs on adversarial-ptr-confusion and
adversarial-ptr-deep, rc=-11, exactly as c/kernel.c does"*. **That is one draw of
a two-state distribution presented as a property**, the same shape as the ±7
environment phase and p03/p04's withdrawn `+6.00`.

⚠ **Nothing fires.** `rust_bug.py::main` computes `unsafe_reproduces_c` from
`stdout` **and `rc`** equality but asserts it **only on the three SILENT inputs**
(lines 226–238); for the two ptr inputs it checks only that C died on a signal,
that the safe arm did not exit 0, and that the safe arm did not reproduce C. So
the flip produced `problems: []` and `rc=0`, and gate stage 9b checks the
sidecar's **freshness**, never its values. ⚠ **And nothing couples a pattern's
`NOTES.md` prose to its own control sidecar at all.**

✅ **I kept the honest draw.** Re-running until it drew SIGSEGV would have been
cherry-picking. **The sidecar now says `rc=-7` and the pattern's docs say
`rc=-11`; that contradiction is live in the tree and is for the manager**, since
one copy is inside `contract_sha256` and correcting it is a declaration edit
owing the direction test.

### 8 — the closing checks, each read from its own exit status

```
harness/measure.py --check-stale        rc=0   66 record(s) examined, 0 STALE
harness/tools/composition.py --check    rc=0   OK: published composition table matches the tree (33 patterns, 10 classes)
harness/tools/temp_citations.py         rc=0   OK  (new=0 unclassified=0 resolved=4)
synthesis/licence.py --emit             rc=0   33 patterns, 132 pair verdicts
synthesis/synthesize.py                 rc=0   wrote results/synthesis.md (103530 bytes, 720 lines)
```

**66 = gate + measurement, 33 of each** ✓. `temp_citations`' 4 `RESOLVED` are
RECAP item 32's known four; **`--update` deliberately not run** — item 32
establishes that pruning them makes the check exit 1 the moment `.temp/` is
cleaned.

`synthesis/licence.json`: **144 lines moved, 132 of them the two harness hashes
and 12 the five edited pattern files. ZERO verdicts moved.**

`results/synthesis.md`: **exactly ONE line moved** — see the overrun below.
`results/SYNTHESIS.md` (CAPITALS) **untouched**, confirmed by `git status`.
`results/tables/p35-tagged-union.md` ends byte-identical to `HEAD`.

---

## Problems

### P1 ⚠⚠ BUDGET OVERRUN 1 — a re-measure stales the pattern's PUBLISHED TABLE, and nothing prices that

The sweep failed `p12 p13 p16 p38` on stage 9c: `results/tables/pNN.md` is
rendered from the measurement record, so a re-measure makes it stale and
`check_table_render` **hard-fails**. Cost, forced: **5 `report.py` runs + 6 extra
single-pattern gate runs** (`p35` needs two, because the sidecar fix moves
`controls_json`, which 9c renders — so the loop is *fix → gate → report → gate*).

⚠ **`PROTOCOL` rule 6's measured re-measure cost — *"p46 moved 111 of 1371
leaves … zero `Ir`, zero md5"* — is about the RECORD and says nothing about the
TABLE.** The task file inherited that and budgeted *"one batched re-measure"* as
if it were self-contained. **It is not: a re-measure costs a re-render and a
re-gate per pattern.** Rule 6's cost table needs the row.

### P2 ⚠⚠ BUDGET OVERRUN 2 — `p35` had THREE stale sidecars

Covered under §7. The trigger set for `controls/*.json` staleness is **anything
in its own `derived_from_sha256`**, which includes **its own generator** — not
only `harness/`.

### P3 ⚠⚠⚠ NOT SPENT, STOPPED AND REPORTED — `synthesis/outward_ir.json` is now STALE on all 33

`synthesize.py` replaced its green line with:

> ⚠⚠ **`synthesis/outward_ir.json` IS STALE against the gate records, so the
> calibration above is scored partly on rows taken against sources that have
> since moved.** **STALE: p01 … p49** *(all 33)*.

`outward_ir.json` pins the **gate `source_sha256`** per pattern, so **every
`harness/*.py` edit stales it wholesale**. Re-emitting is **352 callgrind runs**
— far outside this task's budget — so I **stopped and reported** per the task's
own rule. The artefact is honest and one line redder; **no number in it moved**.

⚠ **This is a SEVENTH pinned artefact that `.memory/05-layout.md`'s *"a `check.py`
edit … IS NOT THE WHOLE COST"* section does not mention**, and it is the most
expensive one. **Every future `harness/` bundle pays it.**

⚠ **And `synthesis/outward_ir.py`'s own module docstring is FALSE about this:**
line 25 reads *"⚠ **It carries no staleness pin**, unlike
`synthesis/licence.json`"*. It **does** — `gate_source_sha256` per pattern —
and `synthesize.py` checks it at `:883-884` and says so in a comment at `:1296`.
`results/synthesis.md`'s own text carried the same error and was corrected at
TASK_107 §F; **the generator's docstring was never corrected with it.**
**Not edited — reported, per "do not improve scope".**

### P4 — a `check.py` docstring claim that is now slightly stale

`forbidden_verdict`'s docstring says backticking p05's other entry *"would move
it out of the loud all-vacuous state into a **quiet** partly-vacuous one"*. Since
TASK_069 the vacuity shout is **per entry**, so `forbidden[1]` would still shout
and the state would not be quiet. **The conclusion is right and the adjective is
wrong.** Not edited: item F says do not change the severity, and rewriting its
rationale is adjacent.

---

## Item F — the measurement the manager asked for

**Not changed: severity untouched, nothing backticked.**

### (i) What would each of the three entries have to say to be auditable?

| entry | text | token? | verdict |
|---|---|---|---|
| p01 `forbidden[0]` | *"a dead v_len parameter on the C kernel"* | **no** | It forbids a **property** (a parameter that exists and is unused). The nearest token, `v_len`, is a proxy that is **both too strong and too weak**: a *used* `v_len` would trip it, and a dead parameter named `n` would not. It would also need to be per-language (`{"c": …}`) or it ranges over four Rust rungs that have no such parameter. |
| p05 `forbidden[0]` | *"chunks_exact"* | **YES — it already IS the exact token** | `` `chunks_exact` `` is one pair of backticks. Should be `{"rust": …}`: a C rung cannot spell a Rust method name, so an unqualified entry would audit the C rungs against an empty set — the same defect one level down. |
| p05 `forbidden[1]` | *"a running row pointer"* | **no** | It forbids a **structure** (strength-reducing `i*ncol + j`). Its implementations are open-ended — `p += ncol`, `ptr.add(ncol)`, `.offset(ncol)`, an advanced subslice. Backticking any one **pins one implementation and licenses the rest**. |

**One of three is backtickable; two are not.** That is the shape of the item.

### (ii) Does `forbidden_hits`' hard fail change the argument?

**No — and it is a reason to KEEP the shout, not to change it.** The mechanism:

* `forbidden_hits` fails on a **hit**; `forbidden_unaudited_entries` shouts on an
  entry with **nothing to hit with**. They are **disjoint**: an entry with no
  backticked span contributes 0 to `forbidden_spellings`, so it can never
  produce a hit and the hard fail can never reach it. A stricter hard fail does
  not make an unauditable entry auditable.
* ⚠ **The hard fail makes the vacuity shout MORE load-bearing.**
  `forbidden_verdict`'s `elif au["forbidden_spellings"]` branch now prints
  *"0 hit(s) over N forbidden spelling(s) … Decidable and ENFORCED since
  TASK_068 — a hit is a gate failure"*. With `forbidden_spellings = 0`, p01 and
  p05 reach **neither** branch, which is correct. **Backticking p05's
  `chunks_exact` alone would move it to 1 and print that enforcement claim over
  a declaration half of which is still unaudited** — TASK_068_REVIEW M2's exact
  regression (the list of 2 was a list of 5: p08 3-of-4, p16 1-of-2, p17 2-of-3).
* ✅ **So shout is still the right severity, and the item's closing question
  answers itself in the negative.** (See P4 for the one word in that docstring
  that is now stale.)

### (iii) What backticking would cost

The `idiom` block is **inside** the ```` ```slb-contract ```` fence, so any edit
**moves `contract_sha256`**. Chain, all forced:

1. `contract_sha256` moves in the gate record.
2. `idiom_audit` moves too (`forbidden_spellings` 0→1,
   `forbidden_unaudited_entries` 2→1 on p05).
3. `loud` moves (one fewer shout on p05).
4. **Three of the four keys `report.py` renders move**, so
   `results/tables/p01.md` / `p05.md` must be regenerated or stage 9c FAILS.
5. **Cost: 2 × (gate → `report.py` → gate) = 4 single-pattern gate runs + 2
   renders. NO re-measure** — `spec.md` is gate-hashed only
   (`measure.py::measurement_sources` globs `*.rs`, `c/*`, `model.py`,
   `inputs/gen.py`, not `*.md`), and **no sweep**.
6. ⚠ It is a **declaration edit made after measuring**, so it owes PROTOCOL rule
   6's direction test and a disclosure with both hashes.
   ✅ **The direction is safe and checkable in advance**: adding a backticked
   `forbidden` spelling can only **narrow** the admissible class, and no p01/p05
   rung spells `chunks_exact` or `v_len`, so no shipped cell moves —
   `check.py::spelling_matches` decides it before the edit.

⚠ **The price buys one third of the item.** The manager decides.

---

## Unsure / not done

* **`synthesis/outward_ir.json` is stale on all 33 and I did not re-emit it**
  (352 callgrind runs, over budget). **The single highest-priority follow-up.**
* **The p42 `+4160.00` correction is reported, not fixed** — the task says stop.
  I have not verified the `≈426 Ir` vector-path counterfactual by running the
  `GLIBC_TUNABLES` control; it is derived from `.memory/`'s 0.104 `Ir`/byte.
* **The nine-pattern inlined-`rep` result is scoped to the measured symbol only.**
  A `rep` inside a *callee* of the kernel in the same binary would not be seen; I
  scoped it to the measured window because that is what `kernel_exclusive_ir`
  counts. I have **not** quantified how much `Ir` each of the 26 contributes.
* **`outward_ir.json` covers `-O3 isolated` only**, so item A's `Ir` attribution
  covers one of four (level × mode) quadrants. The **size** bound covers all four.
* **I did not scan `.memory/` or `RECAP.md` for citation rot** beyond confirming
  the two the task named — stage 0c is per-pattern by construction.
* **The two retired non-default measurement protocols** (`p12`/`p13` reps 31→30,
  `p16` cpu 5→3). I do not know whether either was deliberate.
* **`.temp/build/` (2.4 GB) is left in place.** CLAUDE.md constraint 1 says
  delete binaries once gates are green, but `synthesis/outward_ir.py --emit` —
  the next owed action — needs a fully built tree, and rebuilding it is far more
  expensive than the disk. **Flagging the deviation rather than taking it.**
* **Not edited, by rule:** `.memory/`, `RECAP.md`, `results/SYNTHESIS.md`,
  `harness/tools/composition.py`, `harness/build.py`, `synthesis/outward_ir.py`,
  `patterns/p35-tagged-union/{NOTES.md,spec.md}`.
* **No `git add` / `git commit` / history-mutating git was run.**

---

## Memory updates

**None written — `.memory/` is the manager's.** Requested, in priority order:

1. **`.memory/03-measurement.md`** — ***"Only p08's gcc kernels contain a `rep`
   instruction, so no previously published `Ir` comparison is contaminated"* is
   FALSE at 33 patterns: 26 of 1052 measured windows across NINE patterns
   (`p06 p08 p14 p23 p27 p29 p32 p35 p46`), all `c-gcc`/`c-gcc-h`, all `-O3`,
   all word-wise (`rep stos %rax`/`%eax`, 2 × `rep movsq`).** Direction: gcc's
   `Ir` understates. Exposed column: `gcc-clang`. Instrument:
   `.temp/t168/rep_scan.py`.
2. **`.memory/03-measurement.md`** — the `rep` re-check needs **TWO bars**:
   8192 for `memcpy`/`memmove`, **2–3 KiB for `memset`**. And the p42 hit:
   `+4160.00 Ir/call at 1.0156 Ir/byte`, ~90% counter artefact, published in
   `results/synthesis.md` §2's `≥16.00` band.
3. **`.memory/05-layout.md`**, *"a `check.py` edit … IS NOT THE WHOLE COST"* —
   add (a) `synthesis/outward_ir.json` pins the **gate `source_sha256` for all 33**,
   so any `harness/*.py` edit stales it and re-emitting is **352 callgrind runs**;
   (b) a `controls/*.json` sidecar also pins **its own generator**, so `p35` is
   **3 re-runs, not 2**, whenever a `controls/*.py` moves.
4. **`.tasks/PROTOCOL.md` rule 6's cost table** — a re-measure also stales
   `results/tables/pNN.md` and stage 9c hard-fails it: **+1 `report.py` +1 gate
   per pattern**, and **+2 gate runs** where `controls_json` also moved.
5. **`.memory/02-bench-rules.md`** — the clean negative *"Only `check.py`
   decays"* is **true of `.memory/` and false of the pattern layer**: 13 line
   citations into `measure.py`/`build.py`/`dloop.py` survive under `patterns/`,
   **two rotten now** (`measure.py:238`, `build.py:66`).
6. **`patterns/p35-tagged-union/{NOTES.md,spec.md}`** (manager, declaration edit)
   — *"the unsafe arm SIGSEGVs, `rc=-11`, exactly as C does"* is **one draw**:
   37/40 and 38/40 SIGSEGV, the rest SIGBUS, on the two ptr inputs; C is 40/40.
   `controls/rust_bug.py` records `unsafe_reproduces_c` for those inputs and
   **never asserts it**.
7. **`.memory/` citation rot** — `03-measurement.md:3146 → check.py:2387` and
   `:3375 → check.py:2805`, plus four more, still line-anchored.
8. **A prediction lesson (PROTOCOL rule 14's shape)** — *predict from the
   COMMAND'S DEFAULTS, not from the RECORD'S VALUES.* A record field that is an
   `argparse` argument (`reps`, `timing_cpu`) moves whenever the argument does,
   and the record is exactly where you cannot see that. It cost me 33 leaves on
   two patterns.

**PROTOCOL rule 2 running count: launched from 942.** This task refutes the
manager on: item A's 8192 bar; item A's *"an individual `mem*` CALL"* scoping;
item A's *"answerable statically"*; item A's *"names the callee"*; the budget's
*"two `p35` re-runs"*; and the budget's omission of the table/re-gate chain and
of `outward_ir.json`. **942 → 948.** ⚠ **Reconciliation is the manager's.**
