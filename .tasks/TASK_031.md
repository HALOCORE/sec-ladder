# TASK_031 — withdraw two patterns' wall-clock rows, and say which ones survive

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_030_REVIEW_REPORT.md`
in full** — it is your whole task — then `.memory/03-measurement.md`'s section
*"Code layout: the 32-byte fetch grid"* and `.memory/00-environment.md`'s
branch/cache-simulator paragraph. **Both are already written by the manager and
are the wording to follow rather than re-invent.**

Everything below is measured, reproduced and reviewed. **Do not re-derive it** —
`.temp/r30/` has the working harness (`layout_gen.py`, `loopfit.py`,
`predictors.py`, `survives.py`, `q3_convergence.py`, `predict_then_time.py`), and
`.temp/r30/NOTES.md` has the recipes.

## What was measured

Code layout moves wall clock by up to **27%** at an unchanged executed instruction
stream, and the mechanism is the **32-byte instruction-fetch / DSB window grid** —
`win32` (loop body spans one more window) or `jcc32` (a loop branch crosses a
32-byte boundary; this box is Cascade Lake carrying Intel **SKX102**). Both are
static, zero-parameter, and were confirmed on 20 **pre-registered** fresh layouts.

Measured on **all seven patterns**: real on **p07 and p01**, marginal on p08,
**absent on p02, p05, p16, p17**. The geometry flips on all seven; only a
front-end-bound loop pays for it.

## What to land

### 1. p01 — withdraw the `small` R2/R3 `ns` cells (blocker)

`results/tables/p01-array-sum.md:125-142` publishes R2 **+5.40%** and R3
**+4.72%** over R4 on `small`. Mode-matched over 30 layouts those are
**+5.24% / −4.10%** and **+7.01% / −5.67%** — perfect separation on all three
rungs, and the two safe rungs' modes run *opposite* to R4's. **The sign is not
established.** Failure scenario to write down, because it is concrete: a reader
takes "safe-naive costs 5.4% of wall clock", rebuilds `p01/safe_naive.rs` with any
different link order, and measures R2 **4% faster** than `unsafe`.

### 2. p05 — withdraw the `small` R2/R3 `ns` cells, for a different and worse reason (blocker)

p05 has **no mode**. Its problem is that the **shipped binary is the slowest R2
layout of 31 and the shipped R3 is the fastest**:

```
safe_naive   shipped 7.454 ms   population median 6.334   rank 30/30
safe_tuned   shipped 5.138 ms   population median 5.922   rank  0/30
unsafe       shipped 5.703 ms   population median 5.910   rank  1/30
safe_naive vs unsafe:  SHIPPED +30.69% / +34.97%    population +7.17% / +6.96%
safe_tuned vs unsafe:  SHIPPED  -9.91% / -11.57%    population +0.22% / +0.54%
```

So the published **+36.01%** is a worst-against-best pairing where the population
says **+7.17%**. Reproduced in a second session. And p05's `small` cell drifts
**10–20 points between sessions on byte-identical binaries** — round-robin width
is ruled out (`interleave.py`: +33.75 / +31.24 / +29.25 / +30.26% at widths
1/5/15/30), so it is something slower-moving and **not diagnosable without root**.
Say that plainly; an undiagnosed 15% shipped-layout penalty is a finding, not an
embarrassment.

### 3. Say which rows SURVIVE — this is not a retreat

p02's **+18.04%** and p08's **+105.16%** survive mode-matching essentially
unchanged (+16.68/+17.03% and +104.43/+110.05%), and p16's and p17's `small` gaps
are under 1% either way in both modes. **State that in each pattern's `NOTES.md`**,
with the numbers. A reader who sees two withdrawals and no survivors will conclude
the project's whole `ns` column is unsound, and that is not what was measured.

### 4. p07 §11e — the mechanism is identified, not "narrowed" (major 5)

`NOTES.md:1206+` publishes "bit 4 of the kernel's entry address" as the law and
says the mechanism is *"narrowed, not identified — front end or an
address-indexed predictor"*. Replace both. Bit 4 is a **proxy** that works only
because kernels are 16-byte aligned. And §11e's geometric negative uses the wrong
loop: it rests on `[+0x140,+0x186)` (70 B), whose window count is 3 in both modes
— but that loop's fused `cmp;je` crosses a 32-byte boundary in exactly one mode,
and a second back-edge `[+0x148,+0x191)` (73 B) *does* go 3 → 4 windows. **The
geometry evidence points the right way once the right loop and property are used.**
Record why the wrong loop was picked: a "tightest backward branch" heuristic finds
the 12-byte scalar tail instead of the 30-byte SSE loop on any vectorised kernel.

### 5. p07's R4 band, which nothing explains (minor 8)

§11e records R4 as "0.4%, no mode" from the bit-4 partition alone. Its `small`
spread is **7.68–9.33%** across every pass and both CPUs, reproducible (Spearman
ρ +0.92…+0.96), separated by no bit, unmoved by `jcc32`. **It is larger than
several published gaps.** Write it down as open.

### 6. The reproduction path — report, do not build

`controls/*.py` is inside `source_sha256` precisely so a control's reproduction
path ships, and this finding currently lives entirely in `.temp/r30/`. But it is
**pattern-generic** — one harness serving p01, p05, p07 and any future pattern —
so per-pattern `controls/` may be the wrong home and `common/` is off-limits to
you. **Report what you would do and what it would cost**: which scripts, where,
and whether shipping them re-runs one gate or all seven. Do not implement it.

## Explicitly NOT this task

Do not re-measure the layout populations. Do not touch `harness/`. Do not attempt
to *fix* p05's shipped-layout penalty by relinking a rung — swapping a shipped
cell to a faster layout would be choosing a number, which is the exact move this
project has a rule against.

## Done when

Items 1–5 land in the pattern files; `check.py` green for **every pattern you
touched** (expect p01 `PASS-WITH-BLOCKED-ROWS`, which is policy, not a
regression); `md5_fn` unchanged everywhere; tables regenerated with
`harness/report.py`, never hand-edited. Item 6 is a paragraph in your report.

## Constraints

No root; no `/tmp` (scratch `.temp/p31/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. Prose only, plus `spec.md` if a withdrawal belongs in
a hashed block — **nothing in `harness/`, no rung source, no cell relinked**.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill. **Measurements in the FOREGROUND**, per-PID scratch paths.
Delete binaries and blobs when the gates are green; keep scripts and notes.

Notes to `.temp/p31/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Forty agents
have contradicted the manager and all forty were right. The last one corrected
three things I had written into `.memory/` one task earlier, including a statistic
I introduced *as the fix* for the statistic it has the same defect as. What I am
least sure of here is **item 3's framing** — whether "these two rows are withdrawn
and these four survive" is the honest summary, or whether the right conclusion is
that **no** `ns` row on an L1-resident kernel should be published without a layout
population beside it, which would mean p02 and p08 are not survivors but
untested-and-lucky. p02 and p08 *were* mode-matched, so I think the first is
right; but the C rungs of every pattern remain unbracketed and I do not know what
they would do.
