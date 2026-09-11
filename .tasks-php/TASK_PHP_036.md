# TASK_PHP_036 — BUILD `ph45`, the FIRST TYPE ROW

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_036_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR SPECIFICATION IS `TASK_PHP_034_REPORT.md` §6, AND IT IS NOT RESTATED
HERE.** That hunt settled R1h, computed every `extract_sha256`, measured the
placement under all four build-flag combinations, measured the oracle, and said
what a build task would otherwise stall on. **Read §6.1–§6.9 and build to it.**
This file carries only the manager's decisions, the scope and the traps.

⚠ *Two copies of one specification is how both go stale.* **If §6 and this file
disagree, §6 wins on anything technical and this file wins on scope.** Say so if
you find a disagreement.

**Read**, in this order:
1. **`.tasks-php/TASK_PHP_034_REPORT.md` in full.** §6 is the brief. §5.4 is the
   finding that decides the row's design. §7 is where its own task file was
   wrong. ⭐ **§8 is what it is unsure of — read it before trusting §6.**
2. `.tasks/PROTOCOL.md` — rules 6, 9, 10, 11, 13, **14**.
3. `.tasks-php/PROTOCOL_PHP.md` — **§A1, §A2/§A2a, §B1, §C and §F5 all bind.**
4. `.memory-php/` 00–04 **in full** — authoritative, and it supersedes any task
   report it contradicts, **including `_034`'s**.
5. ⭐ `patterns-php/ph64-callback-frees-cursor/` — **the most recent built row**,
   and the closest precedent for a row whose catalogue oracle measured nothing.
   `patterns-php/ph07-strcut-cursor/` remains the conventions template.
   **Read them; do not touch either.**
6. `patterns-php/SOURCES.md` §2 — the tarball read recipe.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠⚠ **AND NONE UNDER `common-php/` EITHER, FOR THIS ROW** — see §2.3.
⚠ **No `git add` / `git commit`.** Never touch `.web/` — a **concurrent session**
edits it.
⚠ Scratch under `.temp/php36/`. ⭐ **`.temp/php36/` is yours; `.temp/php34/`
holds the spans, the patch, the placement probe and 18 logs — REUSE it.**
⚠ **`grep -a` ALWAYS** (F35). **No `until … sleep` poller loops** — foreground
`sleep` is blocked; one tracked background job, wait for its notification.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`12/0`**, first and last.
⚠ **`TASK_PHP_035` may have moved the php figure** — it re-gates `ph29` and adds
a control. **If your FIRST reading is not `12/0`, do not assume damage**: check
`git log` and report the figure you actually get. ⚠ A new row adds **two**
measure records, so expect **14/0** at the end.

---

## §1 Why this row matters

**The TYPE axis is at ZERO rows.** Spatial has 4, temporal has 1. `ph45` is the
first, and it is the cheapest of the 29 type candidates.

⭐⭐ **And the ladder question here is the sharpest in the corpus so far**: safe
Rust **cannot store a pointer in an `i32` at all**. So R2/R3 must model the
field some other way — an index, a handle, a `usize`. ⚠⚠⚠ **THAT IS A RESULT TO
REPORT, NEVER A KILL.** `CLAUDE.md` rule 6 lists *"safe Rust can't express it"*
among the reasons that are **findings**. Admission was decided C-side and is
already settled. **Whatever the Rust and Verus rungs land on is the finding.**

---

## §2 The manager's decisions

All four were made after reading `_034`'s report in full. ⚠ **They carry no
review.**

### 2.1 ✅ TIER — `narrowed`, and it is **already landed in `CATALOGUE.md`**

`_034` argued `verbatim → narrowed` and flagged it as a judgement call it wanted
attacked. **Accepted.** ⚠ **If your build shows it should be `modelled`, say so
and ship `modelled`** — §2.2 is the live question underneath it.

### 2.2 ⚠⚠ THE PLACEMENT IS A `projection`, NOT A `modelled` DIVERGENCE — and this is the call I am least sure of

`_034` §8.3 hands this up explicitly, and it is the row's crux. §A2's rule is
that a divergence **changing behaviour** makes the row `modelled`. The
placed-arena design chooses where `mbfl_malloc` returns, and that choice decides
whether the defect fires at all.

**My ruling, with the argument, so you can attack it:**

1. ⭐ **The placement RESTORES the platform the code was written for; it does
   not invent one.** §6.3 point 1: a non-PIE `php` binary's `brk` heap on 2004
   64-bit Linux sat **below 2³²**, `(int)p` was **lossless**, and that is
   precisely why this shipped and was reported as *a compiler warning*. A row
   that only ever ran above 2³² would be modelling a **different** program's
   history.
2. ✅ **It is DEMONSTRATED behaviour-preserving in the benign regime, not
   asserted** — §A1's bar. R1 ≡ R1h **bit-identical on all four inputs** at `LO`.
3. ⚠⚠ **BUT IT MUST BE AN EXPLICIT, ITEMISED PARAMETER OF THE ROW — NOT A
   HIDDEN DEFAULT.** ▶ **Put the placement in `provenance` as an itemised
   projection with a `why` that ends in the §A1 formula, put it in the hashed
   `why`, and say in `NOTES.md` that the row reports at BOTH placements.**
   A row that silently picks one platform and publishes one number is doing the
   thing `PLAN_PHP.md` §4.3 warns about, in reverse.
4. ⚠ **If you conclude it is `modelled`, ship `modelled` and say why.** **A tier
   is a cost, never a filter** — `_034` says this and it is right.

### 2.3 ⛔ DO NOT EDIT `common-php/emalloc_shim.h`

`_034` measured that backing the shim from a placed arena would be **more
faithful** and would **stale every php row** — the shim is in every row's gate
*and* measurement digest (`PROTOCOL_PHP.md` §B2). **Rejected.** The `-no-pie`
alternative is also rejected: `harness/build.py` is frozen and passes no such
flag. ▶ **Both are already measured and written down. Do not re-try either.**

### 2.4 The oracle — use `_034`'s, not the catalogue's

⚠ **The catalogue's `u64 = decoded bytes + (allocs, frees)` MEASURES NOTHING**:
R1 ≡ R1h bit-identically in the lossless regime — **`ph64`'s lesson repeating on
a second row**, which is now twice and is worth a sentence in your report.
▶ Use §6.4's measured replacement: two filters 2³² apart alias under truncation,
and R1 decodes `&amp;` to **674** where R1h gives **38** — non-fatal,
deterministic and `u64`-visible. ⚠ **Re-derive it before trusting it.**

---

## §3 ⚠ Which statistic your numbers are in — manager decision, UNREVIEWED

▶ **Publish the `fixed-R4 bound` in `A1`** — kernel-exclusive `Ir`, per call,
`small.bin` — **and name the statistic.** The decider is the **R4/R5 null
control**: `identity` pins R4 and R5 byte-identical, so `verus − unsafe` has a
known true value of **0**; **family A reads `0.000 %` across all 39 rows of both
programmes while family B reaches `+3.65 %` / `+5.01 %`**, exceeding on one cell
the very effect it is used to measure (F74).

⚠⚠ **WITH ITS CONDITION, WHICH BINDS THIS ROW HARD.** A is the headline **only
where the two compared cells have comparable callee share**
(`inside_share = (kernel_exclusive_ir / n_iters) / marginal_ir_per_call`).
**31 sign flips in 310 comparisons, every one above `|Δinside_share| = 0.02` and
none below.** ▶ **This row allocates, so compute `inside_share` for every rung
and report it.** Where two cells differ by more than 0.02 — and the **C-vs-Rust**
column is the likely one — **publish BOTH families, labelled.**

⚠ **Two labelled quantities, never three. NO PAIR INTERVAL.**
`min(R3 found) − min(R4 found)` is not the repair.

---

## §4 ⚠ The traps

1. ⚠⚠ **`_034` ran no gate, no `check.py`, no measurement and neither bracket** —
   by instruction. **Every number in §6 is from its own probes, not from the
   harness.** Re-derive rather than transcribe, and say which you did.
2. ⚠⚠⚠ **Do NOT lift the ENCODE half of `mbfilter_htmlent.c`.** `:123` carries a
   **separate, uncatalogued** stack OOB write (`tmp + sizeof(tmp)` on an
   `int tmp[64]`), fixed in the same window by a **different** commit that
   `_034` did **not** identify. §8.5: *"nobody should act on it without doing
   so."*
3. ⚠ **Fifteen tarball lines, three functions, eleven dereferences** — not the
   catalogue's *"five lines, two functions"*, which is corrected. ⭐ **Measure
   the EXTRACTION, not the mechanism** (§6.6), and report **both** numbers.
   `ph64` was described as *"8 lines"* and measured **~140**.
4. ⚠ `#define _GNU_SOURCE` is required: `-std=c99` sets `__STRICT_ANSI__`, which
   hides both `mmap` flags. §6.3.
5. ⚠ The `mmap` must happen **ONCE, outside the measured region** — a per-call
   `mmap` puts a syscall in the marginal-`Ir` subtraction.
6. ⚠ **`clang` is not on `PATH`**; use `harness/build.py:53`'s
   `~/tools/llvm/bin/clang`.
7. ⚠ **A probe's CRASH/CLEAN verdict is wrong under ASan** — ASan `_exit(1)`s
   rather than re-raising, so `WIFSIGNALED` is false. Use
   `ASAN_OPTIONS=abort_on_error=1`. **The ASan report is the evidence, not the
   verdict line.**
8. ⭐⭐ **`_034` declared its expectations before running its probe and the
   expectations caught two of its own errors** that *"would not have been
   visible from the output alone"*. **Do the same.** This is F52's countermeasure
   and it is the single most valuable habit in the report.
9. ⚠ **Read the ERROR TEXT, not the exit code**, on every Verus run.
   `is not supported` disqualifies; `postcondition not satisfied` does not.
10. ⚠ **§4.3's double free and §6.8's ladder prediction are INFERENCES**, not
    measurements (§8.4, §8.6). Do not ship either as a finding without measuring.

---

## §5 Definition of done

1. Five rungs + R1h, `spec.md`, `model.py`, `inputs/gen.py`, controls, `NOTES.md`,
   `README.md`, to `ph07`/`ph64` conventions.
2. **`harness-php/gate.py ph45-<slug>` GREEN**, verdict read **out of
   `results-php/gate/`**.
3. The placement itemised in `provenance` per §2.2, and the row's results
   reported at **both** placements.
4. `inside_share` per rung, and the bound in **A1**, named (§3).
5. Both brackets, first and last. Expect **14/0** at the end.
6. ⚠⚠ **Your headline and your gate are two separate claims, and only the gate
   record settles the second.** A task reported "built" while its gate was still
   running and that gate then failed twice. **Do not write a verdict you have
   not read out of the record.**
7. ⭐ **The ladder result — what safe Rust does with a pointer in an `i32` — is
   the finding this row exists for. Report it whatever it is.**
8. Anything contradicting this file or `_034`'s §6 — say so. §2 is the manager's
   own unreviewed work, and §2.2 is the part I am least sure of.
