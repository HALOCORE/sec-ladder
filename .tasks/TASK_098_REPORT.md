# TASK_098 — review report: the ±7 blast radius

**Role: research reviewer.** Nothing was fixed. Scratch is `.temp/r98/` only.
`git status --porcelain` is **empty** at the end of this task; `results/gate/`
was never rewritten (see §0 for how `check.py` was run without touching it).

---

## THE ANSWER, FIRST

> **The ±7 lives entirely inside ONE libc symbol — `__memset_avx2_unaligned_erms`
> at `libc+0x189480` — which is a CALLEE. `kernel_exclusive_ir` therefore cannot
> see it, and does not: 0 of 288 (pattern, cell, blob) triples moved. Every
> headline in `results/synthesis.md` §1, and both the `small` and `large` columns
> of all four §2 pair tables, is in that convention and SURVIVES.**
>
> **Exactly one published column is exposed, and it is exposed 1:1 rather than
> partially: `corrected (derived)`. `synthesize.py::derived()` prints
> `k − k2 + c` with `c = (ma−mb) − (ka−kb)`, `k = ka`, `k2 = kb`, so the printed
> figure is ALGEBRAICALLY `ma − mb` — the whole-program marginal difference,
> with the kernel-exclusive terms cancelled out of it. On p03 and p04 `R5−R4`
> that figure takes THREE values over 32 consecutive environment sizes:
> `{−8.00, −1.00, +6.00}`. The published `+6.00` has ~44% support and the
> opposite sign has ~44%. Those four cells are not resolvable and should be
> withdrawn.**
>
> **The small-integer headlines are PROTECTED, and by two independent
> mechanisms, both measured rather than argued** (§1.2).
>
> **§4A: NO, `p35` does not reopen on the merits — but the manager's stated
> refusal is not the complete one, and I found a fifth route the four-route
> table does not contain. `include!("helper.rs")` splices an `unsafe` helper
> into the crate that `_scan_unsafe_sites` and `_path_includes` BOTH miss
> (measured: 0 failures, `_path_includes` returns `[]`), and a `p35` built that
> way verifies `1 verified, 0 errors` with the gate blind. It is
> TASK_009_REVIEW blocker x1 re-opened through a different splice.** Ranked
> `major`, not `blocker`, and §4A says why.

---

## §0 — method, and what I did NOT run

- **`harness/measure.py`: never invoked.** `harness/build.py`: never invoked;
  every binary came from the pre-existing `.temp/build/<pattern>/`.
- **`harness/check.py` was run ONCE**, as `check.py p03 --no-build
  --no-callgrind`. That is a **PARTIAL** run by `main()`'s own predicate
  (`partial = bool(a.skip) or a.no_callgrind or a.no_build or ...`), and a
  partial run writes to `.temp/gate-partial/`, **not** to `results/gate/`.
  Verified by hashing all 24 records before and after:

  ```
  $ sha256sum results/gate/*.json > .temp/r98/gate_before.sha   # 24 files
  $ timeout 900 python3 harness/check.py p03 --no-build --no-callgrind ; echo rc=$?
  rc=1
  $ sha256sum -c .temp/r98/gate_before.sha | grep -v ': OK'
  (no output)
  $ git status --porcelain
  (no output)
  ```

  **No `git checkout -- results/gate/` was needed and none was done.**
- Verus only through `./verus_run.py`, single-file, never `--cargo`.
- All instruments are generators kept under `.temp/r98/`: `probe.py` (symbol
  attribution), `sweep.py` (32-pad sweep), `treescan.py` (24 patterns × 6 cells
  × 2 blobs), `audit.py` (the published-difference enumeration), `argv_axis.py`,
  `verus_rc_census.py`, `e5_positive_control.py`, `p35_route5*.py`,
  `include_hole.py`. Their `.json`/`.log` outputs stay; `cg/` and `argv/` hold
  re-derivable blobs.

---

## §1 — THE AUDIT

### 1.1 The two conventions, and why only one is exposed

**E1, the symbol attribution — this is the finding everything else rests on.**
Same binary, same blob, same shell, only `SLBPAD`'s length varied, and the
per-function exclusive `Ir` recorded in the same callgrind runs
(`.temp/r98/probe.py`, `.temp/r98/p03_small.json`):

```
# p03 O3/isolated input=small.bin iters 100->200 dcalls=100
  unsafe       pad=0     marginal=   3059.00   kernel_exclusive_marginal=3002.0
  unsafe       pad=15    marginal=   3066.00   kernel_exclusive_marginal=3002.0
  verus        pad=0     marginal=   3065.00   kernel_exclusive_marginal=3002.0
  verus        pad=15    marginal=   3058.00   kernel_exclusive_marginal=3002.0

# per-function marginal Ir/call, only functions that MOVED with pad
  unsafe pad0->pad15: total 3059.00 -> 3066.00
         +7.00        43.00 ->      50.00   0x0000000000189480
  verus pad0->pad15: total 3065.00 -> 3058.00
         -7.00        50.00 ->      43.00   0x0000000000189480
```

**ONE symbol carries 100% of it.** `0x189480` is in
`/usr/lib/x86_64-linux-gnu/libc.so.6` (callgrind `ob=(2)`); a stripped libc
mis-attributes it to `__nss_database_lookup+0x1440`, and the disassembly settles
it:

```
189484: vmovd  %esi,%xmm0
189495: vpbroadcastb %xmm0,%ymm0
1894a0: vmovdqu %ymm0,(%rdi)
1894a4: vmovdqu %ymm0,-0x20(%rdi,%rdx,1)
```

`__memset_avx2_unaligned_erms`. It is the symbol `patterns/p03-bounded-stack/NOTES.md`
§3b already names (`glibc memset (libc+0x189480)`), with the same two values 43
and 50.

The full three-term decomposition, from the same runs:

| term | unsafe | verus | moves with the pad? |
|---|---:|---:|---|
| `kernel` (exclusive) | **3002.00** | **3002.00** | **NO** |
| `libc+0x189480` memset | 43 ↔ 50 | 50 ↔ 43 | **YES, ±7** |
| `main` (exclusive) | 14.00 | 13.00 | **NO** |

So `R5 − R4` whole-program = `0 + (memset ∈ {−7, 0, +7}) + (−1)`.
⚠ **The only reproducible content of p03's published `+6.00` is `−1.00` — the
opposite sign to what is printed.**

**The level, not just the slope, is invariant.** `kernel_exclusive_ir` totals
were byte-identical at both pads: `600400` at n=200 and `300200` at n=100 for
both cells, i.e. `3002.00`/call — which is exactly the figure
`results/synthesis.md` §1 publishes for p03 `unsafe` and `verus` on `small`.

**Tree-wide** (`.temp/r98/treescan.py`, 24 patterns × 6 cells × 2 blobs at pads
0 and 16, which `sweep.py` established are guaranteed opposite states):

```
triples=288   marginal moved=14   kernel_exclusive moved=0
```

The 14 movers are p03 `{safe_tuned, unsafe, verus}` × 2 blobs, p04
`{safe_tuned, unsafe, verus}` × 2 blobs, and p46 `c-clang` × 2 blobs.
**Nothing else in the tree moves at `-O3 isolated`, on either blob.**

This independently reproduces and extends `results/synthesis.md` limit 2's
*"kernel-exclusive `Ir`/call moved in 0 of 348 triples"* — and, unlike that
line, it names the mechanism, so the immunity is **structural** rather than a
lucky draw: a callee's `Ir` is by construction not in a caller's exclusive count.

### 1.2 Every published pair difference, by convention, with the flags

`.temp/r98/audit.py` enumerates all **192** rows (24 patterns × 4 published
pairs × 2 blobs) from the committed records only.

| convention | where it is published | `|Δ| < 14` | `|Δ| < 7` | exposed? |
|---|---|---:|---:|---|
| **A. kernel-exclusive** `results/pNN.json::kernel_exclusive_ir / n_iters` | synthesis §1 whole table; the `small` and `large` columns of all four §2 pair tables; every `results/tables/*.md` `Ir` column | **60 / 192** | **55 / 192** | **NO — measured 0/288, and structurally so** |
| **B. whole-program marginal** `results/gate/pNN.json::marginal_ir_per_call` | the **entire** `corrected (derived)` column (value *and* parenthetical), because the printed figure is `ma − mb` | 62 / 192 | 55 / 192 | **YES, ±14 on a pair** |

**48 of convention A's 60 sub-14 rows are the `R5−R4` rows at exactly `+0.00`**,
and they are protected by something stronger than this effect: the gate's
`identity: unsafe == verus, O3 exact` pin, i.e. byte-identical machine code
(`md5_fn`). They are not measurements that happened to come out small.

**The 12 that are genuinely small non-zero convention-A numbers** — the ones a
reader would call a headline — and all 12 are invariant:

```
p22  R3-R4  small/large  +2.00     p01  R2-R4  small   +11.00
p12  R3-R4  small        +3.00     p02  R3-R4  small   +11.00
p01  R3-R4  small        +4.00     p02  R3-R4  large   +11.00
p01  R3-R4  large        +5.00     p02  gcc-clang small +9.00
p04  R3-R4  small/large  +5.00     p18  R3-R4  large   -12.00
```

**Named headlines, checked one by one:**

| headline | convention | verdict |
|---|---|---|
| **p01 `+4…+5` instructions per call** (`R3−R4`) | A | ✅ **SURVIVES.** 32-pad sweep: `R3-R4 distinct values over 32 pads: [4.0] swing 0.00`; `R2-R4 [11.0]`, `R5-R4 [-1.0]`. Zero cells moved on either blob. |
| **p16 "a single integer per call"** | A | ✅ **SURVIVES.** `R3-R4 [27.0] swing 0.00`, all four Rust cells flat over 32 pads. |
| **p46 `0.00000` per-MAC tax** (`R5−R4`) | A | ✅ **SURVIVES.** `R5-R4 [0.0] swing 0.00` over 32 pads; p46's four Rust cells do not move at all. ⚠ Its **`c-clang`** cell does (`6216 → 6209`), so p46's `gcc-clang` carries ±7 — 0.34% of `+2069`, harmless, but it is the one p46 row that is not invariant and nothing in the tree says so. |
| **p04 "`0.00000` Ir per ring access at CAP=64 / `2.00000` at CAP=60"** | A + **slope** | ✅ **SURVIVES TWICE.** |
| **p03 `3.00000` Ir per executed pop** | A + slope | ✅ **SURVIVES.** |
| **p03 / p04 `R5−R4` `+6.00 (+6.00)` ?**, 4 cells | **B** | ❌ **NOT RESOLVABLE — withdraw.** |
| **p03 / p04 `R2−R4` derived correction `+7.00`**, 4 cells | **B** | ⚠ the correction itself is the ±7 term; the row's magnitude (`+5117` / `+17244`) is unaffected. |

**⚠ THE PROTECTION THE TASK FILE ASKED ME TO LOOK FOR IS REAL, AND IT IS
EXACT.** A **slope** is immune where a **level** is not, and not approximately —
the ±7 is a per-CALL constant identical on both probe blobs, so it cancels
in every rate. Measured on every cell of both exposed patterns:

```
== p03
  unsafe       pad0 small=  3059.00 large=  8441.30 d_ir_d_work=1.8152782462
               pad16 small=  3066.00 large=  8448.30 d_ir_d_work=1.8152782462
               DELTA d_ir_d_work = +0.000000000000
  verus        pad0 small=  3065.00 large=  8447.30 d_ir_d_work=1.8152782462
               pad16 small=  3058.00 large=  8440.30 d_ir_d_work=1.8152782462
               DELTA d_ir_d_work = +0.000000000000
```

(and the same `+0.000000000000` for `safe_naive`, `safe_tuned`, and all four
p04 cells). `1.8152782462` is the committed `results/gate/p03-bounded-stack.json::
marginal_ir_per_call["unsafe/O3/isolated/d_ir_d_work"] = 1.8152782462057333`.
**So the gate's own derived anti-collapse floor is exactly unaffected**, and any
published *rate* — p04's `0.00000` and `2.00000` per ring access, p03's
`3.00000` per pop, p46's `0.00000` per MAC — inherits that immunity even before
the kernel-exclusive argument is applied.

### 1.3 PER-BINARY, not per-rung-pair — and the pair swing is 14, not 7

`.temp/r98/sweep.py`, p04, pads 0…31, `-O3 isolated`, `small.bin`:

```
pad     safe_naive   safe_tuned       unsafe        verus
0          8183.00      3425.00      3420.00      3426.00
6          8183.00      3425.00      3427.00      3426.00
8          8183.00      3425.00      3427.00      3419.00
14         8183.00      3432.00      3427.00      3419.00
22         8183.00      3432.00      3420.00      3419.00
24         8183.00      3432.00      3420.00      3426.00
30         8183.00      3425.00      3420.00      3426.00
```

**Each binary is a square wave in the pad length: exactly TWO levels, 7 apart,
half-period 16, and a BINARY-SPECIFIC PHASE** (p04: `safe_tuned` flips at 14,
`unsafe` at 6, `verus` at 8). Mechanism, and it is fully determined: the env+argv
byte count shifts the initial stack pointer; glibc realigns it to 16, so the
per-call stack array's address **mod 32** takes exactly two values, alternating
with half-period 16 in pad length; the AVX2 `memset` takes a different tail in
each. `safe_naive` has no phase at all — its level never moves.

**Consequence, and it answers §1.3 directly: the effect is a property of the
BINARY (its frame offset), not of the pair.** Two binaries with equal phase move
in common mode and their difference is protected; two with different phases
realise all four state combinations, so **the pair swings by 14, not 7**:

```
## VERDICT per pair (p04, small.bin, 32 pads)
   R2-R4        distinct values over 32 pads: [4756.0, 4763.0]      swing  7.00
   R3-R4        distinct values over 32 pads: [-2.0, 5.0, 12.0]     swing 14.00
   R5-R4        distinct values over 32 pads: [-8.0, -1.0, 6.0]     swing 14.00

## VERDICT per pair (p04, large.bin, 32 pads)
   R2-R4        distinct values over 32 pads: [16616.0, 16623.0]    swing  7.00
   R3-R4        distinct values over 32 pads: [-2.0, 5.0, 12.0]     swing 14.00
   R5-R4        distinct values over 32 pads: [-8.0, -1.0, 6.0]     swing 14.00

## VERDICT per pair (p03, small.bin, 32 pads)
   R2-R4        distinct values over 32 pads: [5110.0, 5117.0]      swing  7.00
   R3-R4        distinct values over 32 pads: [352.0, 359.0, 366.0] swing 14.00
   R5-R4        distinct values over 32 pads: [-8.0, -1.0, 6.0]     swing 14.00
```

⚠ **A two-pad probe is NOT sufficient for a pair.** Pads 0 and 16 flip every
exposed *cell* (guaranteed, by the half-period), but when both cells of a pair
flip together the pair reads the same at both — p03's `R3−R4` is `+359.00` at
pad 0 **and** at pad 16, while the full sweep shows `{352, 359, 366}`. Anyone
re-running this must sweep a full period.

---

## FINDINGS

### BLOCKER 1 — four published `corrected (derived)` cells change SIGN and are not resolvable; withdraw them

`results/synthesis.md:322-323` (§2 `R5-R4` table) and the same two rows'
`corrected (derived)` cells:

```
| p03-bounded-stack | 0.00 | 0.00 | LICENSED | small +6.00 (+6.00) **?** / large +6.00 (+6.00) **?** |
| p04-ring-buffer   | 0.00 | 0.00 | LICENSED | small +6.00 (+6.00) **?** / large +6.00 (+6.00) **?** |
```

**Measured range over 32 consecutive environment sizes: `{−8.00, −1.00,
+6.00}`, on both patterns and both blobs.** Support, counted over pads 0…31:
`+6.00` on 14, `−8.00` on 14, `−1.00` on 4. **The published value is not even
the modal one; it is tied with its own sign-reverse.**

Concrete failure scenario: a reader quotes *"p03's proof costs +6 instructions
per call once the callee is corrected for"*. Another agent re-runs the gate from
a shell whose environment is 16 bytes longer, gets `−8.00`, and both numbers are
past the same `±2.00` floor with a `**?**` beside them. The `**?**` marker is
supposed to mean *"look further"* — but there is nothing further to look at,
because the quantity itself has no value.

**The decomposition says exactly what is left**: `R5−R4` whole-program =
`0 (kernel) + memset ∈ {−7,0,+7} + (−1) (main)`. The reproducible content is
**`−1.00`**, from `main`'s exclusive count (14 vs 13). Publishing `+6.00` from
a quantity whose reproducible part is `−1.00` is worse than publishing nothing.

**Not a fix, a report** — but the honest replacements, in order of cost, are in
§3.

### BLOCKER 2 — the `corrected (derived)` column's own calibration is a one-draw statistic, and two of its three published band counts sit on the exposed cells

`results/synthesis.md:169-179`, the band table and the calibration line:

```
| `< 2.00` (blank / `<2.00`) | 120 | 0 | 120 | 0.00 | **safe**: nothing real hides below the floor |
| `2.00 … 16.00` (marked **?**) | 22 | 8 | 14 | 2.00 | **a coin flip — do not quote alone** |
| `≥ 16.00` (**bold**) | 34 | 34 | 0 | 17.00 | **every one is real** |
```

TASK_097's own negative-control arm already moved these (`120 → 122`,
`22 → 20`). I can now say **why, and how far**: `audit.py` reproduces the
current split as **22 `?` / 36 bold**, and **all 22 `?` rows are inside the ±14
pair swing by construction** (the band's own upper edge is 16). Of the 22, the
**8 p03/p04 rows are the ones that move**; the other 14 are p02/p07/p22/p47 and
were measured invariant at both pads on both blobs.

The sharper problem is the **`< 2.00` band's headline claim**, *"safe: nothing
real hides below the floor"*. p04's `R3−R4` derived correction is `0.00` at the
committed environment — i.e. **blank, in the safe band** — and takes `−7.00`
and `+7.00` at other pads. So a cell in the band described as *"nothing real
hides below the floor"* holds a term worth 7, three and a half times the floor,
that is invisible at this one draw. The band table is measured per run and is
correct *about this run*; the adjective **"safe"** is not.

⚠ **And `synthesis.md:180`'s own hedge is right for the wrong reason**: *"a
second sweep under a 64-byte-longer environment block reads `152 / 14 / 0 / 10`,
the excess being p03's and p04's memset term — so the published triple is one
draw"*. A 64-byte pad is `64 mod 32 == 0`, i.e. **the same phase as pad 0 on
every binary**. My sweep shows pads 0 and 64 are the *same* state. Whatever
produced that second sweep's difference, it was not the pad length alone.

### MAJOR 3 — `check_marginal_ir`'s docstring is wrong in a SECOND way nobody has reported: the four-pattern list

`harness/check.py:2556` and `:2586`:

> *"The tree now has **FOUR patterns at ±7 Ir/call** (p03, p04, p38 and — since
> TASK_092 — p46)"* … *"The mechanism is a stack array … p03, p04, p38 and p46
> all `memset` a stack scratch buffer per call"*

**At `-O3 isolated`, p38 and p46 do not move at all.** 32-pad sweeps:

```
p38  R2-R4 [257.0] swing 0.00   R3-R4 [21.0]   swing 0.00   R5-R4 [-1.0] swing 0.00
p46  R2-R4 [-165.0] swing 0.00  R3-R4 [-119.0] swing 0.00   R5-R4 [ 0.0] swing 0.00
```

and the tree scan finds **zero** moving cells in p38 on either blob, and exactly
**one** in p46 — `c-clang`, not a Rust rung and not the `memset` story.

TASK_097's blocker corrected the docstring's *scope* claim (`-O3 isolated` is
not invariant). It did **not** correct the *population* claim, and RECAP and
`.memory/03-measurement.md` both inherit it. **The exposed set at `-O3
isolated` is two patterns, not four**, and the exposed cells are seven of 144.
Concrete failure: an agent budgeting the layout instrument for "the four
memset patterns" spends 2× the necessary time and, worse, concludes from p38's
flat result that the effect is unreliable or intermittent.

### MAJOR 4 — a fifth route to a gate-clean `p35`: `include!` defeats `_scan_unsafe_sites`

The task asked whether a spelling reaches a legal `p35` that neither the
manager nor TASK_097 thought of. **There is one, and it is not a spelling of the
twin — it is a splice that removes the `unsafe` token from every file the gate
reads.**

`check.py::_scan_unsafe_sites` reads the files named in `verus.obligations`
plus whatever `_path_includes` returns. `_path_includes:3310-3318` looks for
exactly two things: `#[path = "..."]` attributes and plain `mod X;`
declarations. **`include!("x.rs")` is neither**, and `_scan_unsafe_sites` reads
the *file*, never the expansion.

**Measured** (`.temp/r98/p35_route5c.py`, generic `get_unchecked` shape):

```
_scan_unsafe_sites failures: 0
   *** CLEAN -- the gate saw NO `unsafe` anywhere ***
_path_includes saw: []
   item r98_get        external='verifier::external_body' _is_trusted=True
   item main           external=None _is_trusted=False

verus_run.py rc=0  ['verification results:: 1 verified, 0 errors']
```

with `inc_helper.rs` holding
`pub fn r98_raw_get(v: &[u64], i: usize) -> u64 { unsafe { *v.get_unchecked(i) } }`
and `verus.rs` holding `include!("inc_helper.rs");` outside `verus! {}`.
**That is TASK_009_REVIEW blocker x1 exactly, reached by `include!` instead of
by `macro_rules!`.**

**And it does reach a `p35` the gate accepts.** `.temp/r98/fakep35/5e_p35_min/`:

```
$ python3 verus_run.py .temp/r98/fakep35/5e_p35_min/verus.rs
verification results:: 1 verified, 0 errors
$ _scan_unsafe_sites  ->  scan failures: 0
   r98_read_i external= verifier::external_body _is_trusted= False
```

with the union declared inside `verus! {}`, `r98_read_i` carrying
`requires v is i` and calling the included helper, and the `unsafe { v.i }` in
`inc_helper.rs`. ⚠ **Note `_is_trusted = False`**: with the `unsafe` moved out
and no `ensures`, the item satisfies neither disjunct, so **no twin is
required, `_check_trusted_unsafe`'s "a trusted `unsafe` item must demand
something" never applies, and 5c-twin reports "no trusted item".** The
`requires v is i` is checked by nothing at all.

**My verdict, and I am ranking this AGAINST myself: this does NOT reopen the
catalogue.** A `p35` shipped this way publishes a type-confusion result whose
central precondition no stage tested — the same objection that killed TASK_097's
route 1, and a stronger one, because here the gate does not even *shout*. **The
catalogue closes, and TASK_097's §A answer stands on its conclusion.** What does
**not** stand is the *reason* the manager verified: *"`_is_trusted` requires
`external_body` and `_TWIN_BANNED` bans it"* is a complete refusal only if
`_scan_unsafe_sites` sees every `unsafe`, and it does not.

**Clean negatives on the same hunt** (`.temp/r98/p35_route5.py`), so nobody
re-runs them:

| candidate route | gate | Verus/rustc |
|---|---|---|
| plain `mod helper;`, no `#[path]` | **CAUGHT** — `FAIL [tcb-unsafe] helper.rs:7` | rejected anyway |
| `include!` **inside** `verus! {}` | blind (0 failures) | **rejected**: `include!` splices after `verus!` parses, so `(r: u64)` / `requires` cannot live in the included file |
| `include!` **outside** `verus! {}`, plain-Rust helper | **BLIND** | **accepted, rc=0** |

**Severity `major`, not `blocker`, and the "could this happen by accident?"
test is why.** `.memory/02-bench-rules.md`'s threat model is honest mistake, and
no honest author reaches for `include!`. But `_path_includes` went out of its
way to cover plain `mod X;` — its own comment says *"No pattern uses that today;
leaving it out would mean an `unsafe` helper … was outside both scans, which is
the whole shape of the bug this exists to close"* — so the omission is an
inconsistency in a rule the project treats as structural, and the repair is one
regex in `_path_includes`' `cand` list. `check.py` is **not** in
`measure.py::measurement_sources`, so the fix costs a gate re-run and no
re-measure.

⚠ **Two secondary facts, measured:** (a) an `include!`d **sibling** `.rs` IS
hashed into `source_sha256` (`check.py:7350` globs `pdir/*.rs`), so a change to
it is *detectable* even though its contents are unscanned; (b) an `include!`
target in a **subdirectory** (`include!("h/x.rs")`) is caught by neither the
glob nor the scan — unpinned *and* unscanned. I did not test (b) end to end.

### MINOR 5 — `p03/NOTES.md` §3b presents one draw as a property of the two binaries

`patterns/p03-bounded-stack/NOTES.md:199-207`. The table

```
glibc memset  (libc+0x189480)                       :    43.00  vs    50.00   <- +7
whole-program marginal                              :  3059.00  vs  3065.00
```

and the sentence *"the two binaries … differ by 7 Ir/call inside libc's
`__memset_avx2_unaligned_erms`, because `main`'s frame puts the 512-byte array
at a different alignment"*. The **magnitude** is right and the mechanism is
right — §3b is the section in the whole tree that got this correct, and my
measurement is its measurement. What is not right is that **`43` and `50` are
not properties of `unsafe` and `verus`**: at pad 16 they read 50 and 43. Both
binaries take both values; only their *phase* differs. The section's own
conclusion (*"the kernel-exclusive column is the exact one"*) is unaffected and
is now confirmed by symbol attribution.

### MINOR 6 — `results/tables/*.md` boilerplate points readers at the exposed column

`results/tables/p03-bounded-stack.md:84-86` (generated, so in all 24 files):
*"rung-to-rung **ratios** of this column are directly comparable with the same
ratios of `marginal_ir_per_call` … Agreement means the kernel-exclusive figure
is the whole cell; disagreement means it is not, and then only the marginal is
comparable across rungs."* On p03 and p04 that instruction sends a reader to the
one column that does not reproduce, to adjudicate the one that does. The named
worked examples (p08 58%↔33%, p11 30%↔21%) are far outside ±7 and are safe; the
*rule* is not, on two patterns. The same files' §"Static + executed
instructions" already says *"The whole-program total is deliberately absent: it
moves with the size of the environment block"* — the two paragraphs disagree.

---

## §2 — the unprobed patterns: universal, pattern-specific, or keyed?

**Keyed, and the key is now exact.** A cell moves iff it calls glibc's
`memset` **out of line** with a **stack** destination, once per kernel call.
Six patterns probed at 32 pads (`p01 p03 p04 p16 p38 p46`) plus all 24 at the
two guaranteed-opposite pads on both blobs:

| pattern | Rust cells that move | why |
|---|---|---|
| **p03** | `safe_tuned`, `unsafe`, `verus` (**not** `safe_naive`) | `[0u64; 64]` per call → out-of-line `memset` |
| **p04** | `safe_tuned`, `unsafe`, `verus` (**not** `safe_naive`) | same |
| **p38** | **none** | ⚠ named in the docstring; does not move at `-O3 isolated` |
| **p46** | **none** (its `c-clang` does) | ⚠ named in the docstring; the two stack arrays do not reach an out-of-line `memset` here |
| p01, p16, p22, p27 and the other 16 | none | |

⚠ **`safe_naive` is exposed on NEITHER p03 nor p04** — 8183.00 flat across all
32 pads on p04 — which is why `R2−R4` swings 7 and not 14 there, and why
p03/p04's *large* published R2−R4 corrections are the memset term appearing
one-sided.

**A pattern's step is `7 × (out-of-line per-call stack memsets)`, and it is 0
for the two patterns the docstring counts.** I did not disassemble p38's and
p46's Rust rungs to show the `memset` inlined; that is the obvious next step and
I did not take it (see *Unsure*).

---

## §3 — is `common/layout/` the right instrument? NO, and it fails in the dangerous direction

**It is a different axis, and running it would return a false zero.**

1. **The axis is the PROCESS IMAGE, not the program.** Measured
   (`.temp/r98/argv_axis.py`): same binary bytes, `SLBPAD` unset in every run,
   only the number of characters in the two **paths** varied:

   ```
    argv0 len  blobpath len   marginal  kernel_exclusive  memset
           52            59    3059.00           3002.00   43.00
           53            59    3059.00           3002.00   43.00
           59            59    3066.00           3002.00   50.00
           68            59    3059.00           3002.00   43.00
           52            66    3066.00           3002.00   50.00
           52            75    3066.00           3002.00   50.00
   ```

   **`argv` length and `envp` length are ONE axis**, and `kernel_exclusive` is
   `3002.00` in all nine runs.

2. **RECAP's settled answer 1 is the SAME FAMILY but a DIFFERENT VARIABLE, and
   the task file asked exactly this.** Settled answer 1's *"source-path-length
   artefact (it moves if you clone elsewhere)"* is about the **R4/R5 kernel's
   offset inside the binary** — a build-time property, different program bytes.
   This is a run-time property with **identical** program bytes. Both are
   "path length"; they act through different mechanisms and one instrument
   cannot serve both.

3. **`common/layout/` varies the program and measures `ns`.** `layout_gen.py`
   drives `-align-all-functions` and `--symbol-ordering-file`; the population's
   environment is held fixed; and `modesim2.py`'s own committed result is that
   callgrind's simulators *"move by ≤6 events in 10⁸"* across a full layout
   mode. **So a layout population run on `Ir` would report ≈0 for a term worth
   7 — a clean bill of health on an unresolvable number.** That is the worst
   possible failure mode for a verification instrument.

   ⚠ **One live confound worth recording**: `layout_gen.py:150` names binaries
   `os.path.join(scr, f"{cell}.{tag}")`, and cell names differ in length
   (`safe_naive` 10, `unsafe` 6, `verus` 5) while tags differ between `o1` and
   `o10`. Under the axis measured in (1), **the layout populations already
   sample the stack-alignment axis by accident, aliased onto "layout" and onto
   "rung"**. It does not threaten finding 16 (7 `Ir` in 3059 is 0.23%, far
   inside p01's 1–3% and p05's 5–45% identical-copy floors), but it means the
   populations are not a clean control for this term either.

4. **What the layout route would cost, as a number.** `common/layout/README.md`:
   ~10 min per pattern for the population plus ~2 min for the mandatory
   identical-copy noise floor. **24 patterns ≈ 4.8 h**, and it returns zero.

5. **THE CHEAP INSTRUMENT, and it is 200× cheaper.** `.temp/r98/sweep.py` — one
   full period of the pad, 4 cells, one blob:

   ```
   $ time python3 .temp/r98/sweep.py p04 --cells safe_naive safe_tuned unsafe verus --pads $(seq 0 31) --input small.bin
   real  0m58.225s
   $ ... --input large.bin
   real  1m3.496s
   ```

   **≈2 min per pattern for both blobs, 24 patterns ≈ 48 min** — and by §2 only
   **p03 and p04** need it at all, i.e. **≈4 minutes** to bracket every exposed
   cell in the tree exhaustively rather than sample it. `treescan.py`'s two-pad
   screen over all 24 patterns × 6 cells × 2 blobs is what identifies that set,
   and it ran inside the 90-minute budget end to end.

6. **PINNING vs BRACKETING — and pinning is the wrong answer.** Pinning the
   environment (running `_callgrind_total` under a normalised `env -i …`)
   would make `marginal_ir_per_call` *reproducible*, and `check.py` is **not**
   in `measure.py::measurement_sources` so it costs one gate sweep
   (TASK_097 measured 24 patterns at ≈2600 s ≈ 43 min) and **no re-measure**.
   ⚠ **But reproducible is not right**: the published pair would then be one
   arbitrary draw from a two-state distribution, permanently, with no marker
   saying so. The number would stop moving and stay wrong.

   **The instrument that answers the question is the 32-pad bracket**, and the
   honest publication is a range (`p03 R5−R4 ∈ {−8, −1, +6}`) or a withdrawal —
   ideally both: withdraw the point estimate, publish the decomposition
   (`kernel 0 + memset ±7 + main −1`), which is the part that reproduces.

---

## §4 — attacking the rest of TASK_097

### §4A — `p35`: covered above (MAJOR 4). **The catalogue stays closed.** The engineer's conclusion is upheld; the manager's stated *reason* is not complete.

### §4B — the `_verus` fix and stage 5e: CLEAN, and I checked BOTH directions

**Does 5e fire on the five mutant sites?** `.temp/r98/verus_rc_census.py` wraps
`check.py::_verus` and drives all five Verus stages on the real p03:

```
=== 28 `_verus` RUNS, by stage (pattern p03-bounded-stack) ===
-- 5.  check_verus_contract  (success-expecting): 1 run(s)      verified=9  errors=0
-- 5b. check_call_site       (success-expecting): 2 run(s)      verified=5/2 errors=0
-- 5c. check_clause_deletion (2 MUTANT sites + 1 control): 6 run(s)
     verified=9 errors=0 | 8/1 | 7/2 | 8/1 | 8/1 | 8/1
-- 5c-req. check_requires_strength (1 MUTANT + 1 control): 14 run(s)
     9/0 | 9/1 | 10/1 | None/None | 9/1 | 10/1 | None/None | 9/1 | None/None |
     None/None | 9/1 | 10/1 | None/None | 8/1
-- 5c-twin. check_trusted_twins (1 MUTANT + 2 controls): 5 run(s)
     9/0 | 12/0 (--cfg slb_twin) | 11/1 | 11/1 | 11/1

_VERUS_RC_ANOMALIES after every stage: 0
rep.failures: 0
teeth: 16 run(s) reported errors > 0 (mutants that DIED); 7 reported 0 errors
```

✅ **28 real runs, 0 anomalies, 16 mutants dying with `errors > 0`.** The
predicate `summary parsed AND errors == 0 AND rc != 0` is unreachable at every
mutant site on this pattern, exactly as `_verus`'s docstring claims. The five
`(None, None)` are `_run_taut_battery`'s tactic-inapplicable arm (`by
(bit_vector)` on slice lengths), which the stage reports as
*"5 (conjunct, tactic) pair(s) are NOT claimed"* — not anomalies.
✅ **The battery still has teeth**: a full `check.py p03 --no-build
--no-callgrind` prints 5c, 5c-req and 5c-twin all `ok`, with the only failure
being the `--no-callgrind` one it is designed to produce.

**And the other half — WHAT WOULD MAKE 5e FIRE?** RECAP's own question, because
a stage that cannot fire is the tautology trap. `.temp/r98/e5_positive_control.py`
drives a control and a real E0133 file through the same `_verus`:

```
  good   flags=[]  verified=2 errors=0  suppressed=False
  bad    flags=[]  verified=None errors=None  suppressed=True
          | verification results:: 2 verified, 0 errors
          | error[E0133]: access to union field is unsafe ...
_VERUS_RC_ANOMALIES: 1
== 5e. every Verus run's EXIT CODE, not just its summary =============
    FAIL [verus-exit] .temp/r98/e5_bad.rs []: verus_run.py exited 1 while
    reporting `2 verified, 0 errors`. ...
stage 5e rep.failures: 1
```

✅ **Fires on the real thing, silent on 28 healthy runs including 16 dying
mutants. Not a tautology.** `check_verus_exit_codes` is reached unconditionally
at `check.py:7310`, after every Verus-facing stage.

⚠ **One residual I am reporting and not fixing.** The new `_verus` creates a
*new* way for a mutant site to receive `(None, None)`: a mutant that Verus
accepts (`errors == 0`) while rustc rejects. At `check.py:4446`
(`if mv is not None and me == 0: rep.fail`) and at `_run_taut_battery`'s
`continue`, that mutant now **stops producing its own local failure** — the run
is still red, but via `[verus-exit]` rather than via `[clause-mut]`, so the
diagnostic names the compiler and not the surviving mutant. Latent on this tree
(0/28), correct in outcome, and worth one sentence in the docstring.

### §4C — the tree's p03 gate record: it makes no difference, and here is the proof

TASK_097 left *the sweep's* `results/gate/p03-bounded-stack.json` in the tree and
warned that its byte-identity to HEAD's `synthesis.md` is not evidence about the
tree. **The warning is right about the reasoning and the outcome is that nothing
published depends on the choice**, because the diagnostic runs (the ±7 side)
were never committed. Leaf-by-leaf diff of the committed record across the two
commits:

```
marginal keys: 96   moved 9f8fa9d->711d9c7: 0
total leaf diffs: 31
[('adversarial', 27), ('sanitizer', 2), ('source_sha256', 2)]
```

**Zero of 96 `marginal_ir_per_call` keys moved.** The record has carried
`unsafe/O3/isolated/small.bin = 3059.0` and `verus/... = 3065.0` since at least
`f5d5880`, and `git log` shows the file last moved at `711d9c7`, `9f8fa9d`,
`6e36f31`, `bce8aa8`, `5883909`. The 27 `adversarial` + 2 `sanitizer` leaves are
TASK_097's own documented UB-stdout nondeterminism; the 2 `source_sha256` are
`check.py` and `limbs.py`.

**Which state is committed:** `3059 / 3065` is the pad-0 state, giving
`R5−R4 = +6.00`. Under the 32-pad sweep that state holds on 14 of 32 pads and
`−8.00` on 14. So the committed record is a valid draw and not a corrupted one —
it is just one of two equally-supported draws.

### §4D — `harness/limbs.py::TWIN_BANNED` is missing `"external_body"`: CONFIRMED, and demonstrated live

`harness/limbs.py:71` vs `harness/check.py:5006-5007`:

```
set difference check.py - limbs.py: ['external_body']
```

and the regex claim holds — `re.search(r'\bexternal\b', '#[verifier::external_body] fn t(){}')`
is `False` (`_` is a word character). Run on a real twin body that **nests** an
`external_body` item, which is the only shape where the two tuples can disagree
(the outer case is caught by both files' `if tw.external:` limb):

```
check.py::_TWIN_BANNED  n=6  hits=['external_body']
limbs.py::TWIN_BANNED   n=5  hits=[]
```

✅ **TASK_097's report is correct.** The divergence is **latent, one shape wide**,
and `limbs.py`'s own header says staleness *is* the alarm — so this is the alarm
firing. One token.

---

## Clean negatives — named attacks that did NOT land

1. **"The kernel-exclusive column is only accidentally invariant."** Refuted by
   attribution: the ±7 is 100% inside a libc callee, so a caller's *exclusive*
   count cannot contain it. 0 of 288 triples, both blobs, all 24 patterns.
2. **"p01's `+4…+5` / p16's single integer / p46's `0.00000` are dead."** All
   three swing **0.00** over 32 pads. p46's `R5−R4` is exactly `0.0` at every pad.
3. **"The gate's derived anti-collapse floor moves."** `d_ir_d_work` is invariant
   to 12 decimal places on all 8 exposed cells — the ±7 is per-call and cancels
   in every slope.
4. **"A plain `mod helper;` escapes `_scan_unsafe_sites`."** It does not;
   `_path_includes:3316` covers it and the gate fails with `[tcb-unsafe]`.
5. **"`include!` inside `verus! {}` is a route."** It is not — `include!`
   splices after `verus!` parses, so Verus syntax in the included file is a
   parse error. Only the *outside* form works.
6. **"Stage 5e is a tautology / fires on the mutants."** Neither: 0 anomalies
   over 28 real runs including 16 dying mutants, and it fires on a real E0133.
7. **"`layout_gen` holds path length fixed, so the populations are a clean
   control for this."** It does not hold it fixed — cell-name and tag lengths
   vary — but the term is far inside every published noise floor, so finding 16
   is unaffected.
8. **"Two pads are enough."** Enough for a *cell*, not for a *pair*: p03's
   `R3−R4` reads `+359.00` at pads 0 **and** 16 while its true range is
   `{352, 359, 366}`.

---

## Unsure / not done

- **I did not disassemble p38's or p46's Rust rungs** to show the `memset`
  inlined. MAJOR 3 rests on the measured absence of movement across 32 pads and
  both blobs, not on the codegen. If the manager wants the mechanism as well as
  the number, that is one `asm.py` call each.
- **I probed the pad space 0…31 (one full period).** The two-state /
  half-period-16 structure is measured on p03 and p04 only; I assert it
  structurally (16-byte stack alignment × 32-byte AVX2 granularity) for the
  rest. A pattern with a *differently sized* stack array could in principle hit
  a third `memset` path; I did not look for one.
- **I did not probe `-O0` or `-O3 whole`.** Everything here is `-O3 isolated`.
  The docstring's claims about those classes are untested by me.
- **I did not re-run `synthesize.py` or `licence.py`**, so the exact new band
  counts under a flipped p03/p04 are TASK_097's (`120→122`, `22→20`), not mine.
  My `audit.py` recomputes the *current* split (22 `?` / 36 bold) from the
  committed records only.
- **MAJOR 4's subdirectory variant (`include!("h/x.rs")`) is reasoned, not
  run.** I verified the sibling case is hashed by `pdir/*.rs`; I did not build
  the subdirectory case.
- **I did not attempt a full `p35` through a real gate run**, because that means
  planting into `patterns/` and the task forbids fixing anything. The evidence
  is `_scan_unsafe_sites` driven directly on a synthetic pdir plus
  `verus_run.py`, which is the same method TASK_097 used.
- **`.temp/r98/cg/` and `.temp/r98/argv/`** hold re-derivable callgrind blobs
  and binary copies; `probe.py` / `sweep.py` / `treescan.py` / `argv_axis.py`
  rebuild every one. They should be deleted; the `.py`, `.json`, `.log` and
  `NOTES.md` are the evidence.

---

## Memory updates

`.memory/` is manager-only, so **none written.** What I would land, in priority
order:

1. **`.memory/03-measurement.md`, the `-O3 isolated` section — add the SYMBOL
   and the CONVENTION SPLIT.** The ±7 is entirely inside
   `__memset_avx2_unaligned_erms` (`libc+0x189480`), a callee, so
   `kernel_exclusive_ir` is **structurally** immune (0/288 measured) and every
   `-O3 isolated` kernel-exclusive figure in the tree survives. The exposed
   surface is `marginal_ir_per_call` and, through it, **the whole `corrected
   (derived)` column** — whose printed figure is algebraically `ma − mb`.
2. **The exposed set is `p03` and `p04`, not four patterns.** p38 and p46 do
   **not** move at `-O3 isolated`; p46's `c-clang` does. Correct
   `check.py:2556` / `:2586`, `.memory/03-measurement.md` and RECAP together.
3. **Withdraw p03's and p04's `R5−R4` `corrected (derived)` cells.** Range
   `{−8.00, −1.00, +6.00}`; the reproducible content is `−1.00` (`main`), the
   opposite sign to what is published. Publish the decomposition instead.
4. **The protection, stated as a rule:** *a SLOPE is exactly immune where a
   LEVEL is not* — `d_ir_d_work` moves `0.000000000000` on all 8 exposed cells,
   because the term is per-call and identical on both probe blobs.
5. **The instrument is a 32-pad sweep, not a layout population.** ~2 min per
   pattern for both blobs against ~12 min for a layout population that would
   return **zero** (callgrind is layout-blind: `modesim2.py`, ≤6 events in 10⁸).
   ⚠ **The argv axis and the envp axis are ONE axis** — binary path length and
   input path length flip the same ±7, measured — which is the same *family* as
   RECAP settled answer 1 but a **different variable**: settled answer 1 is a
   build-time property of the binary, this is a run-time property of the process
   image at identical binary bytes.
6. **`.memory/02-bench-rules.md` / `04-verus.md` — `_scan_unsafe_sites` has a
   fifth hole: `include!`.** `_path_includes` covers `#[path]` and `mod X;` and
   not `include!`; the x1 shape verifies `1 verified, 0 errors` with the gate
   reporting 0 failures. `p35` still does not ship, but the recorded *reason*
   must change. One regex; `check.py` is not measurement-hashed.
7. **`limbs.py::TWIN_BANNED` divergence confirmed and demonstrated** (one shape:
   an `external_body` item nested inside a twin body).

---

## Contradictions, counted (291 → 299)

1. **292 — `check.py::check_marginal_ir`'s FOUR-PATTERN list** (`:2556`,
   `:2586`), inherited by `.memory/03-measurement.md` and RECAP. *"p03, p04,
   p38 and p46 all `memset` a stack scratch buffer per call"* — **at `-O3
   isolated` p38 and p46 do not move at all**: 32-pad sweeps read swing `0.00`
   on every pair, and the 24-pattern scan finds zero moving cells in p38 and one
   in p46 (`c-clang`). The exposed set is **two** patterns and **7 of 144** cells.
2. **293 — the task file's and `.memory/`'s framing that the ±7 threatens the
   published headlines.** It threatens **one column**. The ±7 is a callee's, so
   `kernel_exclusive_ir` — synthesis §1 and both `small`/`large` columns of all
   four §2 tables — is **structurally** immune, measured 0 of 288 triples.
3. **294 — `results/synthesis.md:172`'s `< 2.00` band, *"safe: nothing real
   hides below the floor"*.** p04's `R3−R4` derived correction is `0.00` at the
   committed environment and `±7.00` at other pads: a term 3.5× the floor,
   invisible at this draw, inside the band called safe.
4. **295 — `results/synthesis.md:180`'s *"a second sweep under a 64-byte-longer
   environment block reads `152 / 14 / 0 / 10`"*.** `64 mod 32 == 0`, so a
   64-byte pad is the **same phase as pad 0 on every binary** — measured. Its
   difference from the first sweep was not produced by the pad length alone.
5. **296 — TASK_097's / the manager's §A refusal as a COMPLETE argument.** *"a
   twin is structurally never `_is_trusted`, so `_scan_unsafe_sites` hard-fails
   any `unsafe` token in one"* is a complete refusal only if
   `_scan_unsafe_sites` sees every `unsafe`. `include!("h.rs")` outside
   `verus! {}` gives `1 verified, 0 errors` with `_scan_unsafe_sites` reporting
   **0 failures** and `_path_includes` returning `[]`. **The conclusion (the
   catalogue closes) is upheld; the reason is not.**
6. **297 — `patterns/p03-bounded-stack/NOTES.md:199-207`.** `43` and `50` are
   presented as the `unsafe` and `verus` memset costs; at pad 16 they are `50`
   and `43`. Both binaries take both values.
7. **298 — `results/tables/*.md:84-86` (generated, all 24 files).** *"only the
   marginal is comparable across rungs"* sends a reader, on p03 and p04, to the
   one column that does not reproduce — and contradicts the same file's own
   *"the whole-program total is deliberately absent: it moves with the size of
   the environment block"*.
8. **299 — my own §2 method, corrected mid-task and recorded so nobody repeats
   it.** Two pads 16 apart flip every exposed **cell** and are therefore an
   exhaustive detector for a cell — but **not for a pair**: p03's `R3−R4` reads
   `+359.00` at pad 0 *and* pad 16 while its true range is `{352, 359, 366}`. A
   pair needs a full period.

**Upheld rather than contradicted, and worth saying so:** the ±7 effect is real,
bistable, and exactly as the manager's one-variable experiment describes — I
reproduced `3059/3066` and `3065/3058` to the instruction. `results/synthesis.md`
limit 2's *"kernel-exclusive `Ir`/call moved in 0 of 348 triples"* is **right**,
and is now right for a stated reason. `patterns/p03-bounded-stack/NOTES.md` §3b
is the one place in the tree that already had the mechanism, the symbol and the
right conclusion about which column to quote. TASK_097's `_verus` fix is sound
in both directions, its `limbs.py` finding is correct, and its `p35` conclusion
stands.
