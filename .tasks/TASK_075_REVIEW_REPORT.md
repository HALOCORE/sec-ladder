# TASK_075_REVIEW_REPORT — the synthesis, and a tool that grades its own homework

**1 blocker · 6 majors · 7 minors · 41 named clean negatives.** Every attack run
is listed with its outcome at the end. Scratch and probes: `.temp/p75rev/`
(`NOTES.md` there carries the raw output; the callgrind `.out` blobs and compiled
probes were deleted after the checks, re-derivable from the `.py`/`.c` files kept
beside them).

**Verified first, as asked:** `synthesis/` **is** outside every hashed glob.
Evaluating `harness/check.py::main`'s eleven globs literally (they are
`<pdir>/*.rs`, `<pdir>/c/*`, `<pdir>/*.md`, `<pdir>/model.py`,
`common/driver.*`, `harness/*.py`, `<pdir>/inputs/gen.py`,
`<pdir>/controls/*.py`, `common/*.py`, `common/layout/*.py`, `verus_run.py` —
41 files for p13) and `harness/measure.py::measurement_sources` against every
path under `synthesis/` and `results/synthesis.md` returns **zero hits**. No
stage of `check.py` validates one number in the artefact. The gate is not behind
this one.

**I re-ran `synthesis/synthesize.py` and `synthesis/licence.py --emit`.** Both
rewrote their tracked files **byte-identically** (`results/synthesis.md` md5
`24f7ee4ee78f716da388df32447a404a` before and after; `synthesis/licence.json`
`639d68085cb815bc8b8c033eb244d6f7`), so `git status` was clean afterwards and
**no `git checkout --` was necessary**. I did not re-run `outward_ir.py --emit`;
instead I ran my own independent 348-triple sweep and compared (§A1). I ran
`harness/measure.py --check-stale` (read-only): **44 records, 0 STALE.**

---

## blocker

### B1 — `synthesize.py::LICENCE_NOTE` (printed as `results/synthesis.md` §2): *"The licence is not in the committed records and cannot be derived from them"* is false, and it is the sentence the whole delivery rests on

The artefact states, as measured fact:

> **The licence is not in the committed records and cannot be derived from them.**
> … the only callee information any record carries is `static.bulk_calls`, which
> is a **whitelist of recognised bulk routines**.

`results/gate/pNN.json` carries **`marginal_ir_per_call`** for every
`(cell, opt, mode, input)` — the whole-program `n_iters` 200-minus-100
construction, which is *symbol-independent* and therefore contains exactly the
callee work the kernel-exclusive column drops. For a pair of cells built by the
same front end the driver term cancels, so

```
moves_by_hat = (marg[A] - marg[B]) - (kex[A] - kex[B])
```

is the callee correction from committed records alone. `.temp/p75rev/marginal_licence.py`,
all 22 patterns × 2 blobs × 4 pairs = 176 rows, scored against
`synthesis/outward_ir.json` as the oracle:

```
threshold 2.0 Ir: {'hit': 162, 'miss(false OK)': 0, 'false alarm': 14}
threshold 3.0 Ir: {'hit': 166, 'miss(false OK)': 0, 'false alarm': 10}
threshold 5.0 Ir: {'hit': 167, 'miss(false OK)': 0, 'false alarm':  9}
```

**Zero misses at every threshold** — the same "never wrong in the dangerous
direction" property claimed for the static licence — *and* it produces the
magnitude, which the licence explicitly cannot. It reproduces every large
correction the delivery attributes to the new sidecar:

| pair | callgrind sidecar | committed records only |
|---|---:|---:|
| p11 `R3-R4` small / large | +9821.15 / +7124.34 | +9815.56 / +7116.78 |
| p08 `gcc-clang` small / large | −4153.84 / −4489.97 | −4152.92 / −4488.90 |
| p09 `gcc-clang` small / large | +378.00 / +2625.00 | +379.00 / +2626.00 |
| p13 `R2-R4` small / large | −190.00 / −264.00 | −190.00 / −264.00 |
| p27 `R2-R4` small / large | +120.33 / +130.95 | +120.33 / +130.95 |
| p47 `R2-R4` small / large | +88.27 / +166.00 | +88.37 / +166.00 |
| p36 `gcc-clang` small / large | +128.00 / +1024.00 | +129.00 / +1025.00 |

The residual is *structured*, not noise: a constant **+1.00** on every
`gcc-clang` row (the gcc-vs-clang driver-codegen term) and **−1.00** on every
`R5-R4` row — which is the driver term `.memory/03-measurement.md` already
records for p16 (*"`R5 − R4` going 0 → −1.00 … The −1.00 is the driver's"*).

This is not a new idea. It is **`.memory/03-measurement.md`'s own "author-checkable
test, which needs no disassembly"** — *"rung-to-rung ratios of the kernel-exclusive
column must agree with the same ratios of `marginal_ir_per_call` … Where they
disagree, the marginal is the one to publish"* — and it is **already the
generated boilerplate in 22 of 22 `results/tables/*.md`**, the same boilerplate
the delivery quotes for p11. The delivery cited that boilerplate as proof that
p11's defect was already published, and then wrote a paragraph saying the
information is not in the records.

**Failure scenario.** The manager reads §0's answer, schedules the five-item
`check.py` batch with a new callee stage, and lands two sidecars that sit outside
every hash and therefore rot undetectably — on the strength of a sentence that a
two-line arithmetic over files already in `git` refutes. Meanwhile the *cheapest*
correct answer, and the only one that survives a `.temp/` clean, is never
proposed: **`synthesize.py` should read `marginal_ir_per_call` and print the
kernel-vs-marginal disagreement as a column derived from committed records**,
with the licence and the callee sidecar as refinements rather than as the source.

**Scope, stated honestly:** this invalidates the provenance argument and the §0
recommendation's premise, **not** a number in the tables. The marginal route has
a ~±2 Ir floor (and ±16 on p07/p22, whose per-call work is data-dependent), so it
cannot resolve the ±7.00 `memset` or the +2.00 PLT thunk. That is an argument for
keeping the sidecars as a *refinement*; it is not an argument for the sentence
that is printed.

---

## major

### M1 — `.temp/p75/reproducibility.py` (quoted verbatim into `results/synthesis.md` limit 2, `licence.py`'s docstring and `synthesis/README.md`): the perturbation knob is **inert**, so the "reproducibility test" did not test what it says; the result survives a knob that works, and **"6 of 348" is a floor**

The delivery's mechanism: *"The two sweeps differ only in the
`--callgrind-out-file=` path, which is part of **valgrind's** argv and therefore
shifts the client's stack."* Valgrind strips its own options before building the
client's initial stack. Measured (`.temp/p75rev/perturb.py`, `perturb.txt`):

```
pat  cell        knob     kernel-excl/call   outward/call
p03  safe_tuned  A1              3361.0000        50.0000    baseline
p03  safe_tuned  A2              3361.0000        50.0000    repeat, same out-file
p03  safe_tuned  B               3361.0000        50.0000    out-file path +40 chars
p03  safe_tuned  C0              3361.0000        43.0000    +1 env var
p03  safe_tuned  C64             3361.0000        43.0000    +1 env var, 64 B
p03  safe_tuned  D               3361.0000        50.0000    cwd depth 5
```

and, decisively, an **exact-length replica of the delivery's own two paths**
(97 chars `…/p75/cg/cg.p03-safe_tuned-O3-isolated-small.bin.out` against 99 chars
`…/synth-cg/…`) gives **identical kernel-exclusive and identical outward**. The
knob that moves p03/p04 is the **environment block**, non-monotonically — which
is what `.memory/03-measurement.md` and `check.py::check_marginal_ir`'s own
docstring already say (*"changing only the length of the environment block …
it is SCATTER, not a trend"*).

Re-running the whole comparison with the environment as the knob
(`.temp/p75rev/envsweep.py`, 696 callgrind runs, 9m19s):

```
348 (pattern, input, cell) triples compared across TWO ENV SWEEPS
  kernel-EXCLUSIVE Ir/call moved in 0 of 348
  OUTWARD          Ir/call moved in 11 of 348
  p03 small/large safe_tuned  50.00 -> 43.00 (-7.00)
  p04 small/large safe_tuned  50.00 -> 43.00 (-7.00)
  p08 small  c-clang c-clang-h safe_naive safe_tuned unsafe verus  +0.0627 / +0.0676
  p08 large  unsafe                                               +0.0065
```

**The headline result is confirmed and hardened** — `0 of 348` on the
kernel-exclusive column under a perturbation that demonstrably moves the outward
column. **But the delivery's `6 of 348` is a floor and its class of exposed
patterns is short by one: p08 is a third.** p08's shift is uniform within a
language, so it cancels in every scored pair and moves no verdict; p03/p04's does
not, and the published score is one draw:

```
sweep A (baseline env):  {'hit': 156, 'false LICENSED': 10, 'false alarm': 0, 'abstain': 10}
sweep C (+64 B env var): {'hit': 152, 'false LICENSED': 14, 'false alarm': 0, 'abstain': 10}
```

So `156 / 10 / 0 / 10` should be quoted as *"10–14 depending on the environment,
all of the excess being the same p03/p04 `memset` term"*. **`0 false alarms`
survives both sweeps.**

A **third** sweep (mine, baseline environment) against the committed
`synthesis/outward_ir.json`: **348 triples, kernel-exclusive moved in 0, outward
moved in 0** — the sidecar is bit-reproducible in the same environment.

**Failure scenario.** `.memory/` inherits *"the `--callgrind-out-file=` path
shifts the client's stack"*, a later agent uses that knob as a reproducibility
control on a new pattern, gets 0/N by construction, and publishes a "reproduces
exactly" that tested nothing.

### M2 — `licence.py::verdict` / `licence.py::survey`: **`UNDEC` conflates three different conditions**, and `results/synthesis.md` defines it as only one of them

`results/synthesis.md` limit 2: *"`UNDEC` means a cell dispatches through a
pointer with no static target and the question cannot be settled from the
disassembly."* But `verdict()` returns `None` (→ `TAG[None] = "UNDEC"`) for
**three** cases, and `synthesize.py::main` prints the tag and **discards the
`why`**:

```
$ synthesis/licence.py p01 --mode whole
  R2-R4 ... UNDEC  cannot decide: safe_naive=no kernel symbol (inlined; the column is None here)
>>> licence.verdict("unsafe","nonexistent_cell", …) -> (None, 'cannot decide: … NOT BUILT')  TAG -> UNDEC
```

**Failure scenario.** `synthesis/README.md` documents re-emitting `licence.json`
as a one-liner. Someone runs it on a tree where `.temp/build/` has been cleaned
(it is gitignored, and CLAUDE.md rule 1 tells agents to delete exactly those
blobs). Every pair becomes `UNDEC`, `results/synthesis.md` regenerates with 88
`UNDEC`s, and the file's own legend asserts that all 88 dispatch through an
unresolvable pointer. Nothing in the pipeline fails, because nothing here is
gate-checked. Minimum repair: a distinct tag for "not built" / "no kernel
symbol", and print the `why`.

### M3 — `licence.py::is_noreturn`: the diverging-callee filter names a **returning** routine, under a docstring that calls the filter a proof

```python
_NORETURN = re.compile(
    r"panic|slice_index_fail|…|_Unwind_Resume"
    r"|core.*9panicking|copy_from_slice")
```

The docstring justifies the filter as *"This is an argument, not a heuristic —
all of them are `-> !`."* `core::slice::<impl [T]>::copy_from_slice` **returns**,
and it is the routine that does the copy. Anything whose mangled name contains
`copy_from_slice` is silently deleted from the live set before the multiset
comparison — the one place the licence can emit a **silent false LICENSED**,
which is the direction the delivery itself calls dangerous.

Measured: it fires on **0 of the 31 distinct outward target names** in
`licence.json` today, so it is inert; and `len_mismatch` (already in the regex)
covers `copy_from_slice::len_mismatch_fail`, which is presumably what it was
aimed at. So the token is both **redundant and unsound** — one-word fix.

**Failure scenario.** A future pattern's R3 calls `copy_from_slice` out of line
(p02, p12 and p13 all call `memcpy` from inside the kernel today; one `-C
opt-level` or `#[inline(never)]` change moves it out) while R4 does not. The
licence prints `LICENSED`, the synthesis prints a blank in the `corrected`
column, and its caption says *"blank means measured-and-equal"*.

Same function, harmless direction: `\babort\b` does **not** match
`_RNvNtCs2AWtUsOyxgP_3std7process5abort` (no word boundary after the v0 length
prefix), so p27's Rust rungs carry a never-executing `abort` in their live set.

### M4 — `licence.py::outward` + `verdict`: **two of the seven `gcc-clang` `NOT-LIC` verdicts are right for reasons the measurement contradicts**, so *"0 false alarms"* is not evidence that the criterion is sound in the alarming direction

*p27 `gcc-clang`* — `why`: `only c-gcc calls ['kernel.cold  [tail/outlined]']`.

```
0000000000001200 <kernel.cold>:
    1200:  call   1130 <abort@plt>
```

That is a diverging block that executes **zero** times in any accepted run — the
licence filters `abort@plt` itself and does not filter a `.cold` block whose
entire body is a call to it. Worse, `kernel.cold` matches **`measure.py`'s own
kernel regex** `(?:^|::)kernel(?:$|\W)`, so if it ever executed its cost would
land *inside* `kernel_exclusive_ir`, not outside it. It cannot make the column
incomparable in either state. The row moves by **+40.02** and every instruction
of that is the PLT thunk the licence cannot see (20 libc calls × 2.00).

*p47 `gcc-clang`* — `why`: `only c-gcc calls ['memcmp@plt']; only c-clang calls
['bcmp@plt']`. Measured with call counts:

```
p47 c-gcc     kernel -> PLT 0x4001160  calls=80000  incl 1,925,065
              PLT    -> 0x188320       calls=80000  incl 1,765,065
p47 c-clang   kernel -> 0x188320       calls=79999  incl 1,765,042
p47 safe_naive kernel-> 0x188320       calls=80000  incl 1,763,165
```

**`memcmp` and `bcmp` are literally the same address `0x188320`.** p47's own
reviewed `NOTES.md:100` says so (*"clang rewrites `memcmp(...) == 0` into
`bcmp`"*). The row moves by **+7.96**, all of it the thunk (4 calls × 2.00 minus
the 0.036 resolver).

So the licence's *reasoning* produces two alarms that its own criterion should
not have produced, and both survive the score only because an unrelated term the
licence is blind to happens to move the same rows. `0 false alarms` is a
statement about the sweep, not about the rule.

### M5 — `results/synthesis.md` §2: **p27's mechanism is wrong**, and all four "adjacent findings" are already disclosed by the patterns they name

The file asserts *"`p27`'s `unsafe` dispatches through `call *%r12`; neither is a
bulk routine and neither appears anywhere in a record"* as the cause of the
+120.33 / +130.95. The measurement says otherwise:

```
p27 small, outward per call
  unsafe      __rust_alloc 593.20  __rust_dealloc 917.33  shim 10.01
  safe_naive  __rust_alloc 593.20  __rust_dealloc 280.93  shim 10.01  drop_glue 756.73
  (280.93 + 756.73) - 917.33 = +120.33
```

The cost is the out-of-line `core::ptr::drop_glue::<[Option<Box<u8>>; 32]>` on
the **safe** side, not the indirect call on the unsafe side; the `call *%r12` is
a second call to `__rust_dealloc`, which is already in the unsafe cell's outward
list. **`patterns/p27-handle-table/NOTES.md` §5e publishes exactly this**, as a
*closed* decomposition:

```
| drop_glue::<[Option<Box<u8>>; 32]> | 120.4218 | — | **+120.4218** | **+131.0938** |
| **SUM over EVERY function**                    | **+230.0694** | **+792.7458** |
```

against the delivery's `+230.30 (+120.33) / +792.77 (+130.95)`. Same numbers,
different mechanism, and the pattern's version is the reviewed one.
`.memory/03-measurement.md` already carries the warning this is an instance of:
*"A right answer with a wrong justification propagates exactly like a wrong
answer."*

**Disclosure status of all four, as the task file asked** — none is a new defect:

| claim | already disclosed? | where |
|---|---|---|
| p27 `R3-R4`/`R2-R4` understated 120.33/130.95 | **yes, with the numbers** | `p27/NOTES.md` §5e (closed decomposition) |
| p09 gcc carries `__popcountdi2` 378/2625 | **yes, with the rule** | `p09/NOTES.md` §2: *"Quote `marginal_ir_per_call` for anything involving a gcc cell"*, +393.72 table |
| p47 `R2-R4` moves (`bcmp`) | **yes** | `p47/NOTES.md` §1 "The call targets, resolved by GOT relocation and `nm`" |
| p11 `R3-R4` reverses | **yes, twice** | `p11/NOTES.md:143` (*"wrong for four of eight cells … by up to 9830"*) and 22 of 22 generated tables |
| p27 `gcc-clang` reverses on `small` | **no** — new (confirmed: −25.02 → +15.00) | |

So **three of the four are citation fixes, not corrections**, and none needs a
gate re-run. What is genuinely new and does need work is the **record**
misdescription: `asm.is_bulk_symbol('bcmp') = False` (confirmed), so
`results/p47-ct-compare.json` records `c-gcc: ['memcmp@plt']`, `c-clang: []`,
`safe_naive: []` for three cells that call the same glibc entry point; p09's
eight cells all record `[]`; and p11's four plain C cells record `[]` while
calling `strlen@plt` (only the two `-h` cells are populated — the delivery's
correction to RECAP "Owed" 6's follow-up is **upheld**).

### M6 — `synthesize.py::SEARCH` and `results/synthesis.md` §6: the provenance block for the one hand-maintained column is wrong in **three** checkable ways

> *"…because **nothing committed records it**: control registries are
> heterogeneous and only **8 of 22** patterns expose a `--list` (RECAP "Owed" **12**).
> Every entry quotes its source…"*

1. **Wrong citation.** RECAP "Owed" 12 is about decayed `check.py:NNNN` line
   citations. The `--list` census is RECAP **"Owed" 6**, `RECAP.md:1847-1852`.
2. **Stale number, re-denominated without recounting.** RECAP says *"**8 of 20**
   patterns have a `--list`"* — a figure from when the tree had 20 patterns. The
   synthesis reprints it as "8 of **22**": the denominator was updated, the
   numerator was not. Measured:
   `grep -l -- '--list' patterns/*/controls/*.py` = 11 files across **10**
   patterns (p03 p04 p06 p09 p10 p12 p22 p36 p38 p47). This is the exact rot the
   paragraph predicts, present on delivery, in the sentence that predicts it.
3. **`SEARCH["p47"] = "R4 searched, six levers"` cites `.tasks/TASK_075.md`** —
   the manager's own unreviewed task prose — and I cannot reproduce six from
   anything. p47's reviewed `NOTES.md` §8e ("The R4 side, SEARCHED") lists
   **four** candidates (`u_winu`, `u_end`, `u_win`, `u_ptr`);
   `gen_controls.py --list` shows **five** `from unsafe.rs` controls. This is the
   only SEARCH entry whose source is not a reviewed artefact and it is the only
   one whose number does not check out.

**And there is a derivable proxy, answering A4's question directly.**
`patterns/p47-ct-compare/controls/gen_controls.py --list` already prints the
R3-side / R4-side split the table hand-codes:

```
  t_split        from safe_tuned.rs        (rs)     <- R3 lever
  ...
  u_base         from unsafe.rs            (rs)     <- R4 lever
  u_win / u_ptr / u_winu / u_end            (rs)
```

p36's `--list` gives `r3_hdr4 r3_idx r3_iter r3_window` (= SEARCH's "4 R3
levers", exactly) and `r4_cursor r4_reslice`. So: **derive the lever count from
`--list` where it exists (10 of 22), print `undeclared` for the other 12, and
delete the hand table.** That is strictly more than the 8 hand entries, it cannot
rot, and it puts the number in the file that owns it.

---

## minor

- **m1 — `synthesis/README.md` and `licence.py`'s docstring: *"~2 s for the tree"* is ~2 s for ONE pattern.**
  `time synthesis/licence.py --all` → **43.4 s / 43.7 s** (twice);
  `licence.py p13` → 2.1 s, `licence.py p01` → 2.0 s. The figure also appears in
  `.tasks/TASK_075_REVIEW.md`'s closing paragraph. 43 s is still cheap, so the
  §0 decision is unaffected — but this is a constant in three files.
- **m2 — `synthesis/README.md` (a′): *"The probe blobs are `small.bin` with `n_iters` rewritten"* understates its own recommendation.**
  Every one of the 22 patterns declares `"probe_inputs": ["small.bin", "large.bin"]`,
  and `.temp/check/p13/` holds **64 `small` + 64 `large`** `cg.*.out` files. The
  engineer's own `gate_reuse_demo.py` prints `large.bin` rows. (a′) would cover
  both blobs, which matters because most of the large corrections are `large` rows.
- **m3 — `synthesize.py::main`, claim 1: *"`norel` … differs only in pc-relative displacement fields, which cannot change how many instructions execute"* is over-strong as a general entailment.**
  `md5_fn_norel` zeroes branch displacement *fields*, so `je +0x10` and `je
  +0x20` normalise equal — a `norel` pair *can* differ in control flow. I checked
  p36 directly: the six differing instruction texts are five branches with
  **identical relative offsets** (`+0xa7 +0x64 +0x8d +0x40 +0x64`) plus one
  rip-relative `lea` to the dispatch table, so the conclusion holds *for p36* —
  but by a check the file does not make. The `exact` half of the argument is
  sound. (Clean negative on the mode: `check_identity` compares `isolated`
  builds, matching the table.)
- **m4 — the six PLT-thunk rows carry an unnamed third term.**
  `results/synthesis.md` says p11's is *"+299.87 (150 `strlen` calls × 2.00)"*.
  150 × 2.00 = 300.00. The missing 0.1273 is a **one-off lazy-binding/IFUNC
  resolver call** (`0x15220`, 725–794 Ir per process, present in clang's and
  rustc's binaries and not gcc's), worth 0.0065 … **0.5293** Ir/call and scaling
  as `1/n_iters`. It is a per-process constant inside a per-call column — the
  shape `.memory/03-measurement.md` already condemns for `ns` — and it is why the
  large-blob rows are noisier than the small ones.
- **m5 — `outward_ir.py::parse_cg` discards the `calls=<n>` count**, keeping only
  the inclusive cost. So the sidecar cannot be used to *check* a per-call
  attribution: I had to re-run callgrind to verify "150 calls × 2.00". One extra
  dict, and the record becomes self-checking.
- **m6 — `synthesize.py::main`'s identity classification uses the wrong key.**
  `norel` is `any(e["opt"]=="O3" and e["level"] != "exact")` over **all** O3
  identity entries, and §3's column is `next(e["level"] for e in identity if
  e["opt"]=="O3")` — the *first* O3 entry. p01 ships **two** O3 identity pairs
  (`unsafe vs verus` and `safe_naive vs safe_naive_verus`). Both are `exact`
  today so nothing is wrong; the moment a pattern's R2-side twin drops to
  `norel`, the R5−R4 tautology argument silently reclassifies that pattern.
  Filter on `pair == "unsafe vs verus"`.
- **m7 — two undocumented notations in published tables.** §1 prints `-` for
  p01's `c-gcc-h`/`c-clang-h` (p01 ships no hardened cells) with no legend; §4's
  cells read `31/x` and nothing says `/x` is the first letter of each entry in
  `static.vector_regs`.

---

## The four questions the task file named, answered

**A0 — is `outward_ir.py` a sound oracle?** **Yes**, tested with two purpose-built
probes where the answer is known independently (`.temp/p75rev/tailcall/`).
*(i) Tail calls:* a kernel that tail-`jmp`s into a helper — callgrind records it
as a `calls=` edge anyway (`fn=kernel / cfn=helper / calls=1000 / 0 609000`), so
the blind spot I predicted **does not exist**. *(ii) Double counting and transitive
attribution:* kernel → A at two call sites, A → B, kernel → B directly:
`kernel exclusive 15,000`, `outward {A: 626,000, B: 309,000}`, sum **950,000** —
**exactly** `callgrind_annotate --inclusive=yes`'s figure for `kernel`, with B's
927,000 total attributed once (618,000 under A, 309,000 direct). No double count,
no transitive miss.

**A0 — does the attribution exhaust the 10 false LICENSED?** **Yes for the 10
measured rows, and no as a class.** Verified with call counts: p02 `1.00 call ×
2.00`, p11 small `150.00 × 2.00`, p11 large `41.00 × 2.00 − 0.5293 + 0.02 =
81.4907` exactly, p12 `6.00 × 2.00 × 2 routines − 0.0065 = 23.9937` exactly,
p47 thunk `1,925,065 − 1,765,065 = 160,000 / 80,000 = 2.00` exactly; p03/p04's
±7.00 reproduced on demand by the environment knob. **But the count is a floor by
construction**: the licence compares *static call sites* and predicts *dynamic
cost equality*, and nothing excludes a third mechanism — equal static call-site
multisets with different dynamic trip counts. A fourth is already inside these
same rows and unnamed (m4).

**A0 — the 10 abstains.** **8 of 10 are a closeable gap; 2 must stay.**
Measured `moves_by`: p27 `R5-R4` 0.0000 / +0.0027, p36 `R2-R4`/`R3-R4`/`R5-R4`
0.0000 ×6, p36 `gcc-clang` **+128.00 / +1024.00**.
- p27's `call *%r12` is resolvable from `licence.py`'s **own** `got_map`: two
  instructions earlier the binary does `mov 0x4139a(%rip),%r12 # 56c20
  <_DYNAMIC+0x240>`, and slot `0x56c20` is already resolved to `__rust_dealloc`
  by the direct call at `157df`. One backward register-def scan closes it.
- p36's targets live in a `const TABLE: [&dyn Op; NOPS]` in `.data.rel.ro`; the
  binary has 600 `R_X86_64_RELATIVE` relocations and `got_map` already resolves
  that relocation type.
- ⚠ **p36's `gcc-clang` must NOT be closed that way.** Outward is gcc
  **512 / 4096** against clang and all four Rust rungs **384 / 3072** — i.e.
  `+1.00 Ir per dispatch`, gcc's default `-fcf-protection=full` `endbr64`. Both
  compilers call the **same named functions**, so a name-enumerating licence
  returns `LICENSED` on the only two abstains that move. Abstention is right
  there, and right for a reason the file does not give: it is
  cost-behind-an-equal-name across compilers, the *same class* as the PLT thunk —
  not "the question cannot be settled from the disassembly".

**A2 — is the refutation too strong?** **No.** Verified independently, from
committed records, without `outward_ir.py`: p10, p12, p13 and p18's `R3−R4`
callee correction is **exactly 0.00** (the marginal difference equals the
kernel-exclusive difference to the last digit), and p11's is +9815.56 / +7116.78
against the sidecar's +9821.15 / +7124.34 (0.08%). The p13 reading is upheld:
`.memory/03-measurement.md`:1272-1283 does group `R3/R4/R5` in the cited sentence
and does name **gcc-vs-clang** and **`R2 − R4`** as the two figures that moved.
The `gcc-clang` census is upheld for **all seven** NOT-LIC rows, not just three
(p06 −63/−189, p08 −4154/−4490, p09 +378/+2625, p13 −307/−540, p14 −74/−189,
p27 +40/+128, p47 +8.0/+15.5), each corroborated by the independent
committed-records route with a constant +1.00 driver residual.

**A4 — the search objection.** **Sound, and it does not difference two
differently-scoped searches.** p13's `−177/−1054 → +44/+77` and p10's
`−323/−603 → −129/−241` are both `R3ship − R4alternative` on the same corrected
tree and the same column, i.e. the R3 side is held fixed and the R4 side is
searched — the *opposite* asymmetry from the one the paragraph complains about,
which is what makes it a correction rather than a second artefact. The
`R5 − R4 = 0.00` tautology scoping is right (with m3's caveat), and nothing else
in the file presents an entailment as a finding.

---

## Every attack, with outcome

**Landed (14):** B1 marginal derivability · M1 inert knob / "6 of 348" a floor /
p08 exposed / score is run-dependent · M2 `UNDEC` conflation · M3
`copy_from_slice` in `_NORETURN` · M4 `kernel.cold` and `memcmp`≡`bcmp` ·
M5 p27 mechanism + all four adjacent findings pre-disclosed · M6 §6 provenance
×3 · m1 "~2 s" · m2 probe blobs · m3 `norel` entailment · m4 resolver term ·
m5 `calls=` discarded · m6 identity key · m7 undocumented notations.

**Clean negatives (41) — named, run, did not land:**
1. `synthesis/` in `check.py::main`'s glob — no.
2. `synthesis/` in `measure.py::measurement_sources` — no.
3. `results/synthesis.md` in either glob — no.
4. Score `156/10/0/10` not reproducible independently — it reproduces exactly.
5. `0 false alarms` an artefact of the 5e-3 tolerance — no; the smallest NOT-LIC
   |moves_by| is **7.96**, so it holds to any tolerance below ~7.9.
6. `0 false alarms` breaks under a different sweep — no; holds under my
   environment sweep too.
7. `outward_ir.py` misses a tail-called callee — no (probe).
8. `outward_ir.py` double-counts a callee reached from two call sites — no (probe).
9. `outward_ir.py` misses a transitively-reached callee — no; edge costs are
   inclusive, verified against `callgrind_annotate --inclusive=yes`.
10. `outward_ir.py` mis-sums a kernel split across several `fn=` ids — no.
11. `KERNEL_RE` picks up a non-kernel symbol (`kernel_helper`) — no.
12. `kernel.part.0` / `kernel.cold` excluded from `kex` — no; both match, and
    `measure.py` uses the same convention, so the two agree.
13. Recursive kernel double-counted as outward — no pattern has one.
14. Sub-position-compressed cost lines mis-parsed — no.
15. `licence.json` stale against the gate — no; `gate_source_sha256` matches for
    all 22, and no pattern owns two gate files.
16. `synthesize.py` not idempotent — it is; byte-identical re-run.
17. `licence.py --emit` not idempotent — it is; byte-identical re-run.
18. Delivery moved a measurement record — no; `git show --numstat d9ef651` is
    seven **added** files.
19. Tree gone stale — `measure.py --check-stale`: 44 records, **0 STALE**.
20. `.memory/` written before review (PROTOCOL rule 9) — not written; the commit
    message says so and `git show --stat` confirms.
21. whole-mode census wrong — 350 / 334 / 16 exactly, all `kernel.part.0`, all
    `c-gcc`/`c-gcc-h`, on p03/p04/p08/p38.
22. A survivor with more than one `kernel_functions` entry hidden by `[0]` — none.
23. §3 totals wrong — recount gives 283 / 90 / 188 exactly.
24. §3's `R4=R5 @O3` column picks the wrong identity pair — right today (p01's
    first O3 entry is `unsafe vs verus`); see m6 for the latent half.
25. Identity pinned in `whole` mode while the table is `isolated` — no;
    `check_identity` uses `isolated`.
26. p36's `norel` is a real control-flow difference — no; five branches with
    identical relative offsets.
27. `R5-R4 = 0.00` not actually 0 on some row — 0 of 44 differ.
28. p11's 30.2% / 21.3% wrong — both correct to 0.05 pp.
29. Boilerplate not really in 22 of 22 tables — it is (the grep needs the
    markdown italics: `reads 30% *cheaper*`).
30. p13's `R3-R4` correction non-zero after all — 0.00 by two routes.
31. p27 `gcc-clang` reversal overstated — confirmed, −25.02 → +15.00 on `small`.
32. p09's `__popcountdi2` figure wrong — 378.00 / 2625.00 confirmed, gcc only.
33. p47's `R2-R4` correction wrong — −166 → −77.73 and −194 → −28.00 confirmed.
34. `asm.is_bulk_symbol('bcmp')` actually True — **False**, confirmed.
35. RECAP "Owed" 6's follow-up about p11's `bulk_calls` actually right — it is
    wrong as the delivery says; only the two `-h` cells are populated.
36. (a′) not actually feasible — it is: `check_marginal_ir` writes
    `cg_files[(c,o,m,nm,n)]` and `_check_region_runs` already re-parses them.
37. `results/synthesis.md` uses the word "minimum" — only to forbid it.
38. It publishes a pair interval — it does not.
39. It publishes a wall-clock column — it does not.
40. It prints "not measured" where it means blank — it does not; `corrected()`
    distinguishes the two and every row today is measured.
41. A cell silently dropped from §1 without a reason — none dropped; all 44 rows
    print (the `if unsafe is None: continue` guard never fires).

---

## Running count

The task file's premises are sound except where noted. Five entries this review
would add — the count lives in the newest `.tasks/TASK_NNN*.md` and only the
manager increments it (**174 → 179**):

1. *"The two sweeps differ only in the `--callgrind-out-file=` path, which … shifts
   the client's stack"* — the knob is **inert**; the environment is the knob (M1).
2. *"The licence is not in the committed records and cannot be derived from them"*
   — it can, with zero misses on 176 rows (B1).
3. *"only 8 of 22 patterns expose a `--list` (RECAP 'Owed' 12)"* — wrong number
   (10), wrong denominator lineage (RECAP says 8 of 20), wrong citation (Owed 6) (M6).
4. *"~2 s for the tree"* — 43.5 s; 2 s is one pattern (m1).
5. *"p27's `unsafe` dispatches through `call *%r12`"* as the cause of +120.33 —
   the cause is the safe side's out-of-line `drop_glue`, and p27's own NOTES §5e
   already says so (M5).
