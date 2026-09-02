# TASK_166 — the 33-pattern numbers pack

**Role: research engineer.** `results/SYNTHESIS.md` (CAPITALS) **was not touched**
— `git status` proves it. Everything below is measured; nothing is asserted from
a grep.

---

## Did

| path | what |
|---|---|
| `synthesis/outward_ir.json` | **re-emitted at 33 patterns / 524 cells** (was 26 / 416). 0 skipped, 0 unpinned, 0 stale. |
| `synthesis/licence.json` | re-emitted (`--emit <path>`, 1 m 07 s). **Byte-identical** — it was already fresh at 33. |
| `synthesis/synthesize.py` | **item D** — `global` published as its own column + total, and the *"the author wrote none of their own"* sentence replaced. **item E** — 7 `SEARCH_REVIEWED` entries + `SEARCH_NONE`, and the split published. **item C** — the band-provenance comment replaced with the re-scored table; **neither constant moved**. |
| `results/synthesis.md` | regenerated (`+92 / −70`), idempotent on a second run (`md5 a152f09d…` both times). |
| `common/census/README.md` | denominators `26 → 33` and `103 → 131`; new §3 recording the `0 of 255 → 0 of 464` bound-site denominator and the re-computed `p`. |
| `.temp/t166/` | `PREDICTION.md`, `f_rederive.py`, `f2_dist.py`, `oblig33.py`, `hyp.py`, `hyp2.py`, `bands33.py`, `bands_subset.py`, `typeaxis.py`, `t129rerun/`, `t131rerun/`, `emit.log`. |

**Not touched:** `results/SYNTHESIS.md`, `.memory/`, `RECAP.md`, `harness/`, any
earlier `.temp/t*/` or `.temp/mgr*/`. No `git add`, no `git commit`.

---

## 1. THE HYPOTHESIS — **FALLS.** Three unrelated facts.

> *"all three are the same property — the kernel CALLS OUT OF ITSELF"*

**Verdict: `FALLS`, on all three arms, with a counterexample for each and a
measured mechanism for the one the manager named wrongly.**

The decisive table (`.temp/t166/hyp.py`, `hyp2.py`; `-O3 isolated`, per pattern:
`outward_ir_per_call` maxed over cells, `outward_calls_per_kernel_call` summed
over callees, R3−R4 licence, `identity@O3`, and the R5−R4 derived null):

```
pat   id@O3  R3-R4 lic   outw/call small  outw/call large  calls/kcall sm    lg    null sm   null lg
p01   exact  LICENSED               0.00             0.00        0.000   0.000     -1.00     -1.00
p03   exact  LICENSED              50.00            50.00        1.000   1.000     +6.00     +6.00
p04   exact  LICENSED              50.00            50.00        1.000   1.000     +6.00     +6.00
p08   exact  LICENSED            4309.87          5410.07        6.000   6.000     +0.02      0.00
p09   exact  LICENSED             378.00          2625.00       18.000 125.000     -1.00     -1.00
p11   exact  NOT-LIC             9821.15          7124.34      150.000  41.000     -1.00     -1.00
p13   exact  LICENSED             515.03           924.08       39.000  72.000     -1.00     -1.00
p25   norel  NOT-LIC              491.73          1290.49        5.499   8.374      0.00   +269.52
p27   exact  NOT-LIC             1640.87          5379.93       30.017  96.000      0.00     +0.50
p28   norel  NOT-LIC             1417.01          6111.21       27.966 107.562      0.00     +1.01
p29   norel  NOT-LIC             1974.17          5902.67       31.599  95.871      0.00     -0.02
p34   norel  NOT-LIC             1608.29          7948.47       30.044 144.253      0.00     -0.10
p35   exact  UNDEC                  0.00             0.00        0.000   0.000     -1.00     -1.00
p36   norel  UNDEC                512.00          4096.00      128.000 1024.000     0.00      0.00
p42   exact  NOT-LIC              296.01          4540.00        3.000   3.000      0.00    -31.00
p49   exact  NOT-LIC                0.00             0.00        0.000   0.000     -1.00     -1.00
```

(full 33-row table in `.temp/t166/hyp.py` output.)

```
kernel CALLS OUT (any cell, any blob): 21  p02 p03 p04 p06 p08 p09 p11 p12 p13 p14 p23
                                           p25 p27 p28 p29 p34 p36 p38 p42 p46 p47
kernel calls NOTHING                 : 12  p01 p05 p07 p10 p16 p17 p18 p19 p22 p32 p35 p49
```

### Arm (b) — *"work outside the kernel symbol → `NOT-LIC`"*: **FALSE, both directions.**

* ⚠ **`p35` and `p49` are `UNDEC` / `NOT-LIC` with a kernel that calls NOTHING** —
  `outward_ir_per_call == 0.00` and `outward_calls_per_kernel_call == 0.000` on
  **every cell, both blobs**.
* ⚠ **13 of the 23 `LICENSED` R3−R4 rows have a kernel that calls out**, several
  by thousands of `Ir`: `p08` reads **5409.88 `Ir`/call outward on BOTH cells of
  the pair** and its measured `moves_by` is **0.00**.
* And `NOT-LIC` does not even mean the callees move the difference: **4 of the 8
  `NOT-LIC` R3−R4 rows measure `moves_by == 0.00`** (`p25`, `p28`, `p42`, `p49`).

**The mechanism, read out of `licence.json`'s own `why`:** the licence is a
**static multiset-symmetry** verdict between two cells, not a non-emptiness test.
`p49 R3-R4 = "only safe_tuned calls ['memmove@GLIBC_2.2.5']"` — a call site that
**executes zero times** on the shipped blobs, which is exactly why the dynamic
figure is `0.00`. `p08 R3-R4 = "identical live set: memcpy, memmove ×4, memset"` —
six live callees on both sides, hence `LICENSED`. **Calling out is orthogonal to
the licence; SYMMETRY is the licence.**

### Arm (c) — *"`call rel32` displacements that differ → `norel`"*: **FALSE, and the named mechanism is not the mechanism.**

* 16 patterns whose kernel calls out are **`exact`** at `-O3`, including `p11`
  at **150 outward calls per kernel call** and `p27` — the direct structural twin
  of p28/p29/p34, same `__rust_alloc`/`__rust_dealloc` callees, 5379.93 `Ir`/call
  outward — which is **`exact`** while they are `norel`.
* ⚠⚠ **There is no `call` in the diff.** `harness/asm.py diff --sym kernel`
  reports `identical with pc-rel fields masked: True` on all five; the raw-text
  diff (`.temp/t166/p{25,34,36}.{ur,vr}.txt`) shows what actually differs:

```
p25   < je   15728 <..unsafe6kernel+0x68>      > je   15708 <..verus6kernel+0x68>
      < jmp  157ae <..unsafe6kernel+0xee>      > jmp  1578e <..verus6kernel+0xee>
      < lea  -0xde51(%rip),%rcx # 7910 <GCC_except_table142+0x20>
      > lea  -0xde31(%rip),%rcx # 7910 <GCC_except_table142+0x20>
p34   < je   156ca <..unsafe6kernel+0x5a>      > je   156aa <..verus6kernel+0x5a>
      < mov  0x4151e(%rip),%r14  # 56c60 <_DYNAMIC+0x240>
p36   < jb   158f0 <..unsafe6kernel+0x40>      > jb   15a00 <..verus6kernel+0x40>
```

  **Every differing instruction is an INTRA-KERNEL BRANCH at an IDENTICAL relative
  offset** (`+0x68` vs `+0x68`, `+0xee` vs `+0xee`, `+0x5a` vs `+0x5a`, …) **plus a
  rip-relative `lea`/`mov` into a data section at the SAME absolute address.** The
  two kernels are simply **laid out at different link addresses** because the crate
  is called `unsafe` in one binary and `verus` in the other. **`norel` here is a
  LINK-LAYOUT property, not a call property**, and `p36`'s own published note
  already said so (*"five branches at identical relative offsets plus one
  rip-relative `lea`"*) — nobody had checked the other four.
* Also worth having: **at `-O0`, 30 of 33 rows are `norel`** (`p08` `exact`, `p28`
  and `p29` `differ`). `norel` is the *norm* one level down.

### Arm (a) — *"callees inside the whole-program slope → a non-zero R4/R5 null"*: **FALSE at the published cell.**

Using entry 23's four-axis form (`-O3 isolated`, per input), never a single number:

* **The three biggest callers in the tree have nulls indistinguishable from noise.**
  `p28` `+1.01`, `p29` `−0.02`, `p34` `−0.10` on `large` — at 95–144 outward calls
  per kernel call and 5900–7950 `Ir`/call of outward work.
* **The two rows that DO clear 16.00 are not the big callers.** `p25` `+269.52`
  (large only; `0.00` on small in all four cells) at **8.37 calls/kernel call**, and
  `p42` `−31.00` (large; `0.00` small isolated, `−2.00` at `O3/whole/small`) at
  **3.00 calls/kernel call**.
* **`p03` and `p04` read `+6.00` on BOTH blobs with EXACTLY ONE outward call per
  kernel call** — one `memset`, and the mechanism is the documented glibc
  alignment tail, not call volume.
* **`p49` reads `−1.00` with ZERO calls**, the same as `p01`/`p05`/`p07`/… — the
  tree-wide driver-codegen term.

### Does anything survive?

Only two one-way implications, and **neither is significant**:

| implication | holds | but |
|---|---|---|
| silent kernel ⇒ `exact@O3` | 12 / 12 | base rate is 28/33; `P(0 of 12 silent rows is norel \| chance) = 0.086` — hypergeometric, not significant |
| silent kernel ⇒ `\|null\| ≤ 1.00` | 12 / 12 | same rows, same weakness |
| silent kernel ⇒ `LICENSED` | **10 / 12** | ⚠ **`p35` and `p49` break it** |

> **The three facts have three different generators.** `NOT-LIC` is a *static
> asymmetry between two cells' outward multisets* (or an unresolvable indirect
> dispatch). `norel` is a *link-address difference* between two byte-identical
> kernels. A non-zero null is a *whole-program slope artefact* with a documented
> per-symbol cause on each of the two rows that carry one. **They intersect
> because kernels that allocate tend to do all three, not because one causes the
> others — and the intersection is small: `{p25, p28, p29, p34}` out of 33.**

---

## 2. THE BAND VERDICT — **NEITHER CONSTANT MOVES, and the JUSTIFICATION for `FLOOR` is a published falsehood that predates the seven new rows.**

`.temp/t166/bands33.py`, `.temp/t166/bands_subset.py`. Corrected scoring —
`truth = |moves_by| >= 5e-3`, **not** `truth = |correction| >= threshold`.

```
population        2.00 Ir            3.00 Ir            5.00 Ir
TASK_076's 22     156 / 4 / 16       158 / 6 / 12       159 / 6 / 11
SYNTHESIS's 26    188 / 4 / 16       190 / 6 / 12       191 / 6 / 11
all 33            236 / 5 / 23       240 / 7 / 17       245 / 7 / 12
published (22)    162 / 0 / 14       164 / 2 / 10       165 / 2 / 9     <- does NOT reproduce
```

⚠⚠⚠ **`2.00 Ir → 0 misses` DOES NOT REPRODUCE ON ITS OWN 22 PATTERNS.** It is
**4 misses**, and they are `p03`/`p04` `R3−R4` on both blobs: callgrind measures
`−7.00` where the derived route computes **exactly `+0.00`**, so **no positive
threshold can catch them** (finer sweep: `0.01 → 4 misses`, `0.10 … 2.00 →
5 misses`, `2.50+ → 7`). The 33-population adds one more, `p34 large R5−R4`
(truth `+0.0065`, derived `−0.10`).

⚠ **The oracle did not move.** Committed 26-pattern sidecar vs today's re-emit:
**0 of 208 pair rows and 0 of 824 cell figures differ** (`≥5e-3`). The
environment phase is the same draw. **What moved is the DERIVED side — the
committed `marginal_ir_per_call` records — and nothing re-scored the table when
it did.** So the seven new rows contribute **1 of the 5 misses**; the other four
were already there.

**The constants, re-fitted:**

* **`FLOOR = 2.00` stands.** It **minimises misses (5)** and has the **fewest
  false alarms of every threshold that does** (`1.50 → 5/24`, `2.00 → 5/23`,
  `2.50 → 7/20`). Only `≤ 0.10` catches `p34`, at **98** false alarms.
  ⚠ **The value survives; the sentence *"the only threshold that misses
  nothing"* is retracted** — landed in `synthesize.py`'s band comment and in the
  generated §2 prose.
* **`CONFIDENT = 16.00` stands, unmoved and better supported.** The `≥ CONFIDENT`
  band at 33 is **57 rows, 57 real, 0 spurious, smallest `|correction| =
  17.0027`** — the same `17.00` the 22-row fit found, with 23 more rows in it.

**Band populations** (published 22-row fit → 33):

```
< 2.00      120 rows, 0 real / 120 spurious   ->  175 rows, 5 REAL / 170 spurious
2.00..16.00  22 rows, 8 real /  14 spurious   ->   32 rows, 9 real /  23 spurious
>= 16.00     34 rows, all real, smallest 17.00 ->  57 rows, all real, smallest 17.00
```

⚠⚠ **The low band is no longer empty of real corrections.** *"Nothing real hides
here"* is false on 5 rows. **And `classify()` returns `low` BEFORE it consults the
null**, so those five are dropped **silently**, not `refused` — `TASK_159`'s
CONFIDENT-band refusal rule never sees them.

**Arms: no re-pinning needed, and they were re-run.** Because neither constant
moved, the 9 planted arms are unchanged and all fired in the regenerated file —
3 must-fire `refused`, 6 silent (`high ×4`, `low`, `mid`), plus the live arm
**`p25 large gcc-clang` FIRED** (`results/synthesis.md:249-262`).
`null_rule_selftest` raises rather than publishing; it did not raise.

**A small published-sentence correction found on the way.** `CALLEE_NOTE` says
the derived route and the sweep disagree on p03/p04 **`R2−R4`**. Measured today it
is `R2−R4` **and** `R3−R4` **and** `R5−R4`: **8 of p03/p04's 16 pair/blob rows
disagree.** Landed in the generated prose.

**Licence-tag score also moved** (recomputed live, not a claim of mine):
`179/17/2/10` → **`209 hit / 17 false LICENSED / 14 false alarm / 24 abstain`**.
The **dangerous** direction (false `LICENSED`) is **unchanged at 17** — the seven
new rows added none. The 12 new false alarms are all `NOT-LIC` rows the sweep says
do not move, which is the safe direction.

---

## 3. ITEM F — the completed table

| § | published (26) | manager's (33) | **mine (33)** | agree? |
|---|---|---|---|---|
| §1 | `identity: exact` 25 of 26 | `exact` 28 / `norel` 5 | **`exact` 28 / `norel` 5** — `p25 p28 p29 p34 p36` | ✅ |
| §1 | `24 PASS + 2 PWBR` | `30 PASS + 3 PWBR` | **`30 PASS + 3 PWBR`** — `p01` (1 miri), `p35` (3 twin), `p42` (1 miri), read out of the RECORD's `blocked`/`verdict` | ✅ |
| §1 | `52 measurement records` | 33 records / 66 examined | **33 measurement records; `measure.py --check-stale` prints `66 record(s) examined, 0 STALE`** | ✅ |
| §1 | `8 434`-line gate | ⚠ moving | **`10 048` lines**, clean against `HEAD` (`fb7cdb0`) | — |
| §2 | 22 licensed | 23 licensed, 10 NOT-LIC/UNDEC | **23 / 10** — `p11 p25 p27 p28 p29 p34 p42 p49` NOT-LIC, `p35 p36` UNDEC | ✅ |
| §2 | buckets `9 / 4 / 9` | `9 / 4 / 10` | **`9 / 4 / 10`**, `p32` the only entrant, `p18` in two, `p16` in none | ✅ |
| §2 | R2/R3 median `7.26×`, 17 rows | `6.75×`, 18 rows, `p05` 10th | **`6.75×`, n=18, `p05` 10th** | ✅ |
| §2 | median unmoved by substitution | still `6.75×`, 20 rows | **still `6.75×`, n=20, `p05` 11th**, range `−1.37×`(p47) … `3536.19×`(p08) unmoved | ✅ |
| §2 | "3 not overstatements" | **4** — `p47 p09 p32 p14` | **4** — `p47 −1.37×`, `p09 0.74×`, `p32 0.83×`, `p14 0.86×` | ✅ |
| §4 | pearson(oblig, `verus.rs` lines) `0.795` | `0.805` | **`0.805`** (n=33) | ✅ |
| §4 | pearson(oblig, syntactic size) `0.894` | ⚠ not re-derived | **`0.920`** — see below | **settled** |
| §6 | "**Five** flattering-direction" | **SEVEN** | **SEVEN**, corroborated by two independent artefacts | ✅ |
| §7 | `129 / 58 / 0` | `166 / 85 / 0` | **`166 / 85 / 0` by the published method; `166 / 83 / 0` by the COMMITTED instrument** — see below | ⚠ **method split** |
| §7 | `ptr_offset` 0 over 26 | 0 over 33, all four guards | **`33` kernels `2/2/0/0`; `131` `c/*.{c,h}` `9/7/2/0`** — all eight counts identical | ✅ |
| §7 | `14 of 26` undeclared | **21 of 33** | **21 of 33 before my edit, 14 of 33 after** — split below | ✅ then fixed |
| §7 | `0 of 255` bound sites | ⚠ not re-derived | **`0 of 464`**, 40 site-carrying functions, 33 files | **settled** |

### F.1 — `0.894` "syntactic size" IS recoverable, and the quantity is named

`.temp/t130/oblig_model.py`'s `units = (exec_fn − tcb_items) + proof_fn +
loop_decreases`, counted by `.temp/t130/count_burden.py` on a frozen copy of
`harness/vparse.py` (`git show df14f4f:`). **Not committed anywhere** — it lives in
gitignored `.temp/t130/`. Re-run at 33 (`.temp/t166/oblig33.py`):

```
n = 33 patterns
corr(verified, units (exec-tcb+proof+loops)) = 0.920      (was 0.894 at 26)
corr(verified, ghost clauses)                = 0.834      (was 0.820)
corr(verified, verus.rs LINES)               = 0.805      (was 0.795)
```

⚠ **Run twice — with the frozen `df14f4f` parser and with today's
`harness/vparse.py` — and the two agree to the digit on all 33 rows.** No parser
drift. **Result 3's size-proxy claim SURVIVES and strengthens.** (Also confirmed
in passing: `p49` 34 obligations / 1128 lines is the largest obligation count;
`p28` 23 / **1709** is the longest `verus.rs`. Two quantities, as `TASK_163` said.)

### F.2 — the `0 of 255` denominator, and the `p ≈ 0.06` caveat

`TASK_129`'s classifier **is** re-runnable — `.temp/t129/census.py` +
`REBUILD.sh` + `ladder_extract.sh`, gitignored but present. I copied it to
`.temp/t166/t129rerun/` (never modified `.temp/t129/`), extracted from `git HEAD`,
and ran `census.py selftest` → `SELFTEST PASS`.

| population | bound sites | `ptr_offset` | site-carrying fns | files |
|---|---:|---:|---:|---:|
| the 26 (**control**) | **255** | **0** | **30** | 26 |
| all 33 | **464** | **0** | **40** | 33 |

The 26-row **reproduces the published `255` / `30` / `26` exactly**, so the 33-row
is the same instrument. Operator split at 33: `index 441, mem_call 21,
str_call 1, cast_deref 1, ptr_offset 0`.

⚠⚠ **The `p ≈ 0.06` caveat needs RE-COMPUTING, not re-wording — and it gets ~5×
STRONGER.** `.temp/t131/howsure.py` also runs (re-pointed as
`.temp/t166/t131rerun/howsure33.py`); the original at 26 reproduces `0.0612`
exactly:

```
                        FUNCTION unit (the honest one), size-matched to cgnu
26 kernels, 30 fns:     expected walkers 2.66   P(zero) = 0.0612   <- the published "p ~ 0.06"
33 kernels, 40 fns:     expected walkers 4.12   P(zero) = 0.0123
```

php `0.0047 → 0.0006`, coreutils `0.0499 → 0.0149`; the SITE unit (rejected by
the review as non-independent) runs `1.2e-05 → 5.0e-11`. Recorded in
`common/census/README.md` §3.

### F.3 — ⚠ THE CONTROL ARM: the two methods differ by 2, and the COMMITTED instrument is the one that is wrong

The manager asked me to re-derive `166 / 85 / 0` "with the original method".
**There are two methods and they disagree.**

```
$ python3 .temp/t124/A/rung_split_census.py        # the COMMITTED instrument
adversarial inputs across all built patterns: 166
  ... on which ANY pair of rungs diverges           : 83
  ... on which the FOUR RUST RUNGS take >1 value    : 0
```

```
all 33:      pairs=166  ANY-div LAST-run=83  ANY-div SET-of-runs=85  rust-split 0/0
the OLD 26:  pairs=129  ANY-div LAST-run=56  ANY-div SET-of-runs=58  rust-split 0/0
```

**The published `129 / 58 / 0` is the SET-of-runs number.** `.temp/t124/A/rung_split_census.py`
writes `by[inp][rung] = (exit, signal, stdout)` **inside the loop over runs**, so it
keeps only the **LAST** run per `(input, rung)` and prints `56` — the figure in
`TASK_124_REPORT.md`. The manager's `rederive.py` takes the **set** of all runs and
gets `58`, matching what was published.

⚠⚠ **The two rows the committed instrument drops are `p38 adversarial-huge.bin`
and `p38 adversarial-oob.bin`** — where `c-gcc` has two runs, one `signal 11` and
one clean:

```
adversarial-huge.bin/c-gcc
    {'exit': -11, 'signal': 11, 'stdout': ''}
    {'exit': 0,   'signal': None, 'stdout': '15963742333423663363'}
```

**So the committed instrument is blind to exactly the one row in the tree whose
harm is selected by optimisation level.** The manager's `166 / 85 / 0` is right and
reproduces the published method at both 26 and 33. ✅ **The `0` is
method-independent** — both methods give 0 Rust-rung splits at 26 and at 33, and
the MUST-FIRE arm reports `OK`.

### F.4 — §6's "Five" is SEVEN, corroborated twice

`RECAP.md`'s standing trap row names `p10 · p27 · p38 · p22 · p36 · p35 · p34`
(**seven**), and `patterns/p25-realloc-growth/NOTES.md:359` independently says *"the
trap has now fired seven times"*. ⚠ §6 trap 1 says **"Five"** and then names only
**four** (`p10`, `p38`, `p22`, `p36`) — it was already internally inconsistent
before `p35` and `p34` landed.

---

## 4. ITEM D — the published falsehood, fixed

**Verified the digest claim myself before relying on it, two ways:**

* source read — `check.py::main`'s `srcs` globs `pdir/*.rs`, `pdir/c/*`,
  `pdir/*.md`, `pdir/model.py`, `pdir/inputs/gen.py`, `pdir/controls/*`,
  `common/driver.*`, `harness/*.py`, `common/*.py` (**non-recursive**),
  `common/layout/*.py`, `verus_run.py`. `measure.py::measurement_sources` reaches
  none of `synthesis/` or `common/census/`.
* empirically — over all 33 gate records and all 33 measurement records:
  `keys mentioning synthesis/: []`, `keys mentioning common/census: []` (the one
  `census` hit is `patterns/p46-bignum-mac/controls/census.py`, a pattern-local
  control). **Confirmed: `synthesis/*.py` and `common/census/*` are in NEITHER
  digest.** One edit + one run, no gate, no re-measure.

**Landed (reporting half only — the `verus.axioms` COUNT is untouched):**

```
| pattern | obligations | errors | TCB items | TCB lines | axioms | global | R4=R5 @O3 | verdict |
| p10-fir-stencil | 10 | 0 | 3 | 6 | 0 | 1 | exact | PASS |
...
| **total**       | **497** | | **152** | **333** | **0** | **10** | | |

**Trusted base, all 33 rows: 152 items (333 lines), 0 axioms and 10 `global`
directives on 10 rows.** Quote all three; there is no single one.
```

The 10 are exactly `p10 p19 p22 p28 p29 p34 p36 p38 p46 p47` — `global layout` on
`p28 p29 p34`, `global size_of` on the other seven, one each, all in `verus.rs`,
none `path_included`. The *"a `0` says this pattern's author wrote none of their
own"* sentence is **deleted** and replaced by a warning that names the count and
says why the gate partitions `global` out (rustc const-checks it; `E0080`; stage
5e catches the rejection). **I did not conclude the count itself must change**, so
no sweep was started.

---

## 5. ITEM E — the split, and one entry the obvious detector would have got WRONG

**`14 of 26 → 21 of 33` is 100% bookkeeping and 0% search state.** The 14 rows
undeclared among the old 26 are *still* exactly the 14 undeclared among those 26
today (`SEARCH_REVIEWED` has 12 keys, all inside the old 26). **The entire growth
is the seven new rows.**

Of the seven, read from each row's `NOTES.md` and `controls/` (not inferred):

| row | state | evidence |
|---|---|---|
| **p34** | ⚠ **WRONG** — BOTH sides searched | `NOTES.md` §5 + `controls/spellings.py`, reviewed TASK_155. `r4_readdirect` ties R4 at `-O3`, beats it by `116.13 / 611.10` at `-O0`, **and verifies at the pinned obligation count**. First pattern with >1 admissible R4 spelling and a measured R4-side width. Caught its own `-O0` headline overstated **2.88×/3.36×** |
| **p35** | ⚠ **WRONG** — R4 searched, **sign reverses** | `NOTES.md` §1(iii), TASK_152 M1 → TASK_153 four-arm rig with both shipped rungs as reproducing controls. Matched on the op-walk, **R4 WINS by 203.05 `Ir`/call (6.63%) on `large`** |
| **p28** | ⚠ **WRONG** — R2-vs-R3 searched | `NOTES.md` §8, TASK_149 del. 4 / TASK_150. Three variants, identical checksums; **un-hoisting the walk recovers 72%** of the gap — a **fourth** lever `safe_tuned.rs`'s header omits |
| **p25** | ⚠ **WRONG, partially** — repair SITE searched (three) | `NOTES.md` §3c, TASK_158 §4b: a ternary R1h spelling and a `*(toks + curi)` `rederive` spelling both **equal to the hundredth at every cell**. GROWTH-site repair spelling still unsearched |
| **p29** | ✅ `undeclared` was right in substance | `NOTES.md` §8: *"Neither side was searched"*, no cost axis published |
| **p32** | ✅ right in substance | `NOTES.md` §7: *"THE ABSENCE IS DECLARED, NOT A MEASURED ZERO … That search was not done, on either side"* + four named unmeasured levers |
| **p49** | ✅ right in substance | `NOTES.md` §5: only ONE in-contract R3 spelling built, so no spread |

**So: 4 of the 7 were bookkeeping losses of a REAL search; 3 were reviewed
declarations of NO search that `undeclared` also cannot express.** All seven now
have entries; the three no-search ones are marked `⊘` in their text and listed in
a new `SEARCH_NONE` set, and the generated file publishes the split:
**`14 of 33` undeclared, `19` declared = `16` search results + `3` declared-no-search.**

✅ **Direction: this defect runs AGAINST the flattering direction** — it
under-reports the project's own search effort.

⚠⚠ **Could a check tell a missing entry from a true `undeclared`? The obvious one
CANNOT, and it would have fired wrongly.** *"A pattern shipping
`controls/spellings.py` with no `SEARCH_REVIEWED` entry"* flags `p34` (correct)
**and `p49` (WRONG)** — `p49/controls/spellings.py` is the
`cow`-vs-`provenance` **repair-site** control on `c/kernel.c`, not a rung-spelling
search at all. `p25`, `p28` and `p35` ship no `spellings.py` and all three DO have
a search, so the detector's recall is 1 of 4 and its precision 1 of 2. **A working
check has to read the pattern's `NOTES.md`, not its file list.** No `check.py`
change proposed (out of scope, and it would fail the *"could this happen by
accident"* test).

---

## 6. ITEM G — the type axis. **§5's `6.00 Ir`/call law IS STILL A ONE-ROW LAW.**

Re-derived by RUNNING the built binaries (`.temp/t166/typeaxis.py`), 4
`(compiler × level)` C cells against the R5 rung as reference, every shipped input:

```
p38 (39 inputs)                        which cells disagree with R5
  adversarial-huge.bin                 c-gcc/O3          (SIG11)
  adversarial-oob.bin                  c-gcc/O3          (silent wrong value)
  adversarial-stale.bin                c-gcc/O3          (silent wrong value)
  the other 36 inputs                  none
  => c-gcc/O0, c-clang/O0, c-clang/O3 equal R5 on ALL 39 inputs

p35 (24 inputs)
  adversarial-dbl-confusion.bin        c-gcc/O0, c-gcc/O3, c-clang/O0, c-clang/O3
  adversarial-exhaust.bin              c-gcc/O0, c-gcc/O3, c-clang/O0, c-clang/O3
  adversarial-ptr-confusion.bin        all four  (SIG11)
  adversarial-ptr-deep.bin             all four  (SIG11)
  the other 20 inputs                  none
```

✅ **§7's sentence is exactly right, and it is now measured rather than cited:
`p38` harms in ONE of four cells; `p35` harms in ALL FOUR, identically, on both
compilers. `p35` sits BESIDE §5's law, it does not corroborate it. Anything
written about the type axis must say so.**

---

## 7. WHICH RESULTS SURVIVE, SCOPE, OR FALL

| | verdict | the run behind it |
|---|---|---|
| **Result 1 (§2)** — the tax is a property of a pair of spellings | ✅ **SURVIVES, needs three number swaps and one structural caveat** | buckets `9/4/10` (only `p32` enters, and it is a TEMPORAL row joining `>100`); median `7.26× → 6.75×` with the **robustness property intact** (identical across shipped and substituted arms, n 18→20); "3 not overstatements" → **4**. ⚠⚠ **The structural caveat is the headline**: the unlicensed fraction went **4/26 (15%) → 10/33 (30%)**, and **6 of the 7 new rows are in it**, so §2's apparatus *structurally cannot see* six of the seven. `p32` is the only new row §2 can price. |
| **Result 2 (§3)** — where safe Rust does not help | ✅ **SURVIVES and is the one that GROWS** | the temporal axis is 6 rows and §7 already records that they **disagree** (`p32` reproduces the bug bit-for-bit, `p28` cannot reproduce it, `p34` shows both branches in one row by storage representation). `p49` is a §3 entry that does not exist yet. **§3 has the rule and §7 has the evidence; nothing joins them.** No number of mine contradicts §3. |
| **Result 3 (§4)** — a proof discharges what it says; `obligations` is a size proxy | ✅ **SURVIVES, STRENGTHENED** | `0.795 → 0.805` (lines) and `0.894 → 0.920` (syntactic units) at 33, on the two largest proofs in the tree, with two independent parsers agreeing. ⚠ **And it needs one addition: the `0 axioms` figure it quotes was FALSE on 10 rows** — item D. |
| **Result 4 (§5)** — what the instrument can price | ⚠ **SCOPE, DO NOT TOUCH THE TYPE LAW** | the `6.00 Ir`/call type-based-aliasing law is **STILL A ONE-ROW LAW** (item G, measured). `p35` adds a second row to the type *axis* and **not** to that law. ⚠ `p49` is the second `aliasing` row and has **no UB at all**, which bears on §5's title question — I ran nothing on it and it is not folded in. |
| **The `ptr_offset` census (§7)** | ✅ **SURVIVES, out of sample, and the `p` improves ~5×** | 8 of 8 guard counts identical at 33; `0 of 464` sites in 40 functions; function-unit `p 0.0612 → 0.0123`. `p28`/`p29`/`p34` are pointer-structure rows and contributed **zero** cursor sites. |
| **The Rust-rung control arm (§7)** | ✅ **SURVIVES** | `129/58/0 → 166/85/0`, the `0` reproduced by **two independent methods**. ⚠ the number to publish is `85`, not the committed instrument's `83`. |
| **The band calibration (§1/§2)** | ⚠ **SCOPE** | constants unmoved; **the low band's *"nothing real hides here"* is retracted (5 real)** and the floor's stated reason is retracted. Already landed in the generated file. |
| **§6 trap 1** | ⚠ **SCOPE** | "Five" → **SEVEN**, and the trend is the finding (disclosed after review → before being asked → changed which rung ships → **shipped a control that makes the search re-derivable**). |
| **§1's apparatus page** | ⚠ **four number swaps** | `25 of 26 exact` → `28 exact / 5 norel`; `24 PASS + 2 PWBR` → `30 + 3`; `52 records` → `66 examined, 0 stale` (33 measurement records); `8 434` → **`10 048`**. ⚠ **And §1's *"Four of the 26 `R3−R4` rows are not licensed"* → TEN of 33.** |

---

## 8. CLEAN NEGATIVES — named, so nobody re-runs them

1. **The oracle is stable.** Old committed sidecar vs today's re-emit over the 26
   common patterns: **0 of 208 pair rows and 0 of 824 cell figures moved.** The
   `±7.00` environment-phase term did **not** flip between sweeps. *Do not
   re-emit hoping the phase moved.*
2. **`licence.json` was already fresh at 33** — 0 stale before my re-emit, and the
   re-emit is byte-identical (`git diff` empty). *The 1-minute run buys nothing but
   the confirmation.*
3. **Neither band constant moves.** `2.00` and `16.00` both survive a 33-pattern
   re-fit with the corrected scoring. *Do not re-fit them again unless the
   records move.*
4. **No parser drift in the obligation counter.** The frozen `df14f4f` `vparse.py`
   and today's `harness/vparse.py` give **identical** counts on all 33 patterns.
   *Do not re-audit `count_burden.py` against the new rows.*
5. **`ptr_offset` did not appear.** All four guard variants, both corpora slices,
   unchanged from 26 to 33. *That test is done.*
6. **The `spellings.py`-presence detector for item E does not work** — precision
   1/2, recall 1/4. *Do not propose it as a `check.py` stage.*
7. **`norel` is not a `global layout` effect.** `p25` is `norel` with no `global`
   at all; `p10 p19 p22 p36 p38 p46 p47` carry a `global size_of` and six of the
   seven are `exact`. The `global`-set and the `norel`-set intersect in
   `{p28, p29, p34, p36}` and neither contains the other.
8. **`norel` is not about calls.** Raw-text diff on three of the five: zero `call`
   instructions differ; every difference is an intra-kernel branch at an
   **identical relative offset** plus a rip-relative reference to a fixed address.
9. **Adding `global` to the reporting cost nothing.** `synthesis/*.py` and
   `common/census/*` are in neither digest — verified by source read **and** by
   scanning all 66 committed `source_sha256` key sets.
10. **`synthesize.py` is idempotent after my edits** — `md5 a152f09d…` on two
    consecutive runs.

---

## Problems

1. ⚠⚠ **`.temp/t124/A/rung_split_census.py`, the committed instrument for §7's
   most-quoted defensive result, does not reproduce the published number and is
   blind to `p38`'s level-selected harm** (F.3). It is under `.temp/`, so it is
   not in any digest and I did not touch it — **but it is cited as the derivation
   of a published figure and it prints a different one.** The manager should
   decide whether to fix it in place or record the two methods. *I changed
   nothing there: `.temp/t124/` is cited evidence.*
2. ⚠ **`CALLEE_NOTE`'s p03/p04 disagreement is on three pairs, not one.** Corrected
   in the generated prose; the `synthesize.py` `CALLEE_NOTE` string itself still
   says `R2-R4` in one place (I left the historical sentence and annotated the
   live figure beside it, rather than rewriting a quoted provenance claim).
3. ⚠ The band table's provenance says *"chosen from this table against the
   **26**-pattern oracle"* in `.temp/mgr164/NOTES.md` and in `TASK_166.md`. It is a
   **22**-pattern, 176-row table (`.temp/p76/derived_score.txt`). Minor, but the
   task file states it as fact.
4. Nothing failed. No build, no gate, no re-measure was run or needed.

## Unsure / not done

1. **I did not audit the 14 OLD undeclared rows** (`p02 p04 p05 p07 p09 p14 p16
   p18 p19 p23 p27 p38 p42 p46`). Item E scoped me to the seven new ones. Given
   that 4 of 7 new rows were wrong, **the 14 are worth an audit** and I have not
   done it — so `14 of 33` is an upper bound on the true undeclared count.
2. **I did not re-derive §7's *"36 of 129 adversarial inputs make ZERO kernel
   calls"*** at 33. The gate record carries no call count; it needs `model.py` per
   pattern. Still owed.
3. **I did not touch §5's Result-4 dispute or fold `p49` into it.** `p49` is the
   second `aliasing` row with no UB at all and it bears on *"what this instrument
   can price"*; I ran nothing on that question.
4. **The `norel` mechanism is stated as *link layout*, and I checked 3 of the 5**
   (`p25`, `p34`, `p36`). `p28` and `p29` were checked only to
   `identical with pc-rel fields masked: True`. I would call the mechanism
   **OPEN-but-strongly-indicated** rather than closed, per PROTOCOL rule 9's
   conclusion-vs-mechanism split. **The CONCLUSION — arm (c) falls — rests on the
   16 `exact` counterexamples and needs no mechanism at all.**
5. **`0.920` is the syntactic-size correlation for the quantity TASK_130 used.**
   If "syntactic size" in §5 meant something else, I have not found a second
   candidate — but the two figures `0.894` and `0.795` appear together in exactly
   one place (`TASK_130_REPORT.md:343-345`) and reproduce there, so I am confident.
6. **The `p ≈ 0.012` figure is mine and unreviewed.** It reproduces the published
   `0.0612` at 26 exactly as a control, but the 33-value has not been attacked.
7. **The three `⊘ NO SEARCH` `SEARCH_REVIEWED` entries are a judgement call.** They
   make `undeclared` fall from 21 to 14 while only 4 rows had a real search. I
   published the split explicitly in the generated file for exactly that reason,
   but a reviewer may prefer those three to stay `undeclared`.

## Memory updates

**None written — subagents are forbidden from touching `.memory/` and `RECAP.md`.**
What the manager should land, in priority order:

| file | what |
|---|---|
| `.memory/03-measurement.md` **entry 23** | ✅ **The four-axis table is CORRECT and I re-derived it independently.** Add: **the non-zero null is NOT a "kernel calls out" property** — `p28 +1.01`, `p29 −0.02`, `p34 −0.10` at `-O3 isolated` on `large` despite 95–144 outward calls per kernel call, while `p03`/`p04` read `+6.00` with **one** call. Entry 23's own `-O3 isolated` list (`p25 269.52 · p42 31.00 · p04 6.00 · p03 6.00 · p02 2.00`) is the right one and it is **anti-correlated** with call volume. |
| `.memory/03-measurement.md` | ⚠ **New: `norel` at `-O3` is a LINK-ADDRESS property, not a call property.** All five `norel` R4/R5 pairs differ only in intra-kernel branch targets at **identical relative offsets** and rip-relative references to fixed addresses; zero `call` instructions differ. At `-O0`, `norel` is the norm (30 of 33). ⚠ Mark the mechanism **OPEN** (3 of 5 diffed); the conclusion (`norel` ⊥ calling out) rests on 16 `exact` counterexamples. |
| `.memory/03-measurement.md` | ⚠⚠ **`2.00 Ir → 0 misses` never reproduced against the committed records** — it is `4` on its own 22 patterns and `5` at 33, and **the oracle did not move** (0 of 208 / 0 of 824). The constant survives on a different argument (miss-minimising, fewest false alarms). **The low band contains 5 REAL corrections; *"nothing real hides here"* is retracted.** |
| `.memory/02-bench-rules.md` or `03` | ⚠⚠ **`.temp/t124/A/rung_split_census.py` keeps only the LAST run per `(input, rung)`** and therefore prints `56`/`83` where the published method prints `58`/`85`. The two rows it drops are `p38 adversarial-{huge,oob}.bin` — **the one row whose harm is selected by optimisation level.** The `0` is method-independent. |
| `RECAP.md` findings | ⚠ **The unifying hypothesis FALLS.** `NOT-LIC`, `norel` and a non-zero null are three unrelated properties with three generators. Counterexamples: `p49`/`p35` are unlicensed with a kernel that calls **nothing**; `p08` is LICENSED at **5409.88 `Ir`/call** outward; `p11` is `exact` at **150 calls per kernel call**; `p27` is `exact` with p28/p29/p34's exact callee set. |
| `.memory/01-ladder.md` (per pattern) | the four search-state facts item E landed — `p34` both sides, `p35` R4 (sign reverses), `p28` R2-vs-R3 (walk hoist 72%), `p25` repair site — are already in the patterns' `NOTES.md` and are now in `synthesize.py`; `.memory/01-ladder.md` is where the column's own preamble says they should live. |
| `common/census/README.md` | ✅ **already landed by me** — denominators, and §3 recording `0 of 464`, 40 functions, and `p 0.0612 → 0.0123`. |
| `results/SYNTHESIS.md` | the whole of §3 and §7 of this report. ⚠⚠ **§7's type-axis sentence is CORRECT and must not be softened: `p38` harms in 1 of 4 C cells, `p35` in 4 of 4, measured. §5's `6.00 Ir` law is STILL A ONE-ROW LAW.** |
| `RECAP.md` queue | ⚠ **new item**: the 14 OLD `undeclared` rows have never been audited the way the 7 new ones just were, and 4 of 7 were wrong. |
| `RECAP.md` queue | ⚠ **new item**: `TASK_129`'s classifier and `TASK_131`'s size probe produce two PUBLISHED numbers and live only in gitignored `.temp/`. They both still run; promoting them is the `common/census/` precedent and costs no sweep. |

**PROTOCOL rule 2 running count: launched from 929 → 933.** Four manager claims
refuted by measurement: (1) the unifying hypothesis, all three arms;
(2) *"`2.00` is the only threshold that misses nothing"* — false on its own 22
patterns; (3) *"`p49` ships a `controls/spellings.py` too"* used as evidence its
`undeclared` is wrong — it is a repair-site control and `p49`'s `undeclared` was
right; (4) *"the `0 of 255` denominator has no re-runnable instrument"* — it has
one, it reproduces the published `255`/`30`/`26` exactly, and the dependent
`p ≈ 0.06` caveat re-computes to `0.0123`.
⚠ Reconciliation across branches is the manager's job, not mine.
