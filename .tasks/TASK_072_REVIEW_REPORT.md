# TASK_072_REVIEW_REPORT — p36-vtable-dispatch

Reviewer, adversarial. Nothing under `patterns/`, `harness/`, `common/`,
`pilot/` or `.memory/` was edited. `harness/check.py p36` was re-run; it
rewrote `results/gate/p36-vtable-dispatch.json` and **I restored it with
`git checkout -- results/gate/p36-vtable-dispatch.json`** — `git status` is
clean apart from my scratch under `.temp/p36rev/` (gitignored). `.temp/p36/`
was read, never written; every control was regenerated into `.temp/p36rev/`
by importing p36's own generators with `OUT`/`BIN` rebound.

**48 named attacks. 5 landed hard (2 blocker, 5 major, 7 minor); 36 are clean
negatives and are listed with their outcome so nobody re-runs them.**

---

## Did

- Re-ran the gate and `measure.py --check-stale`; reproduced all 8 rung laws,
  all 7 control `Ir` figures, all 4 proof mutants, all 3 Verus twins, the
  `v_specfirst` vtable finding, the input-generator determinism claim and the
  out-of-scope MSan probe.
- Built **four new controls the delivery did not**: three in-contract R3
  respellings (`r3_window`, `r3_hdr4`, `r3_iter`, plus `r3_window_flat` and
  `r3_window_split`), the **`v_r4_reslice` Verus twin** that `NOTES.md` §11c
  says was not built, a **permuted-`TABLE`** identity attack, and a
  **`mixrand6`** blob (six different permutations of one multiset) that tests
  §7's disclosed direction claim.
- Re-measured both wall-clock bands under an **interleaved** protocol and
  measured **four** independent noise floors (two protocols × two blobs).
- Measured the **callee** `Ir` every published figure excludes, per cell.
- Measured the **vtable layout** of R4 vs R5 and the emitted ghost function.

Scratch, all re-runnable: `.temp/p36rev/{NOTES.md, ir_totals.py, wall_rr.py,
r3_search.py, run_controls.py, mk_v_r4_reslice.py, mix6.py, callee_ir.py,
riprel_sweep.py, norel_attack.log, ...}`.

---

## Problems

### BLOCKER B1 — the R3 side was never searched, and `R3 − R4 = +15.00 flat` is +7.00 (or +2.00)

`patterns/p36-vtable-dispatch/controls/gen_controls.py::c_r3_idx` is p36's
**only** R3-side lever and it moves R3 the *dearer* way (2232/17464 against
1710/13358). The R4 side got two levers plus an inadmissibility probe and every
candidate went through Verus (§8b). `NOTES.md` §8b nevertheless states *"The
shipped R3 is the **cheapest found** in contract, on **both** blobs"*.

**Measured, it is not.** One in-contract respelling of
`patterns/p36-vtable-dispatch/safe_tuned.rs::kernel` — reslice the window once
at the top and index the header inside it — is cheaper on both blobs:

```
-- r3_window  n_fn=71 bytes=249            (.temp/p36rev/r3_search.py)
   small.bin  checksum=195445626134389610     Ir/call=  1702.0000
   large.bin  checksum=471216819055512592     Ir/call= 13350.0000
-- r3_hdr4    1704.0000 / 13352.0000
-- r3_iter    1705.0000 / 13353.0000
   shipped R3 1710.0000 / 13358.0000
```

`13·nrw + 38` against the shipped `13·nrw + 46`; identical checksums on both
blobs; **zero `unsafe`**. Contract-conformance checked with the gate's own
oracle (`.temp/p36rev/r3_window_contract.log`, `harness/check.py::spelling_matches`):
**11 of 11 required backticked rust spellings match exactly as the shipped R3
does — 0 divergences — and 0 forbidden hits.**

Mechanism, zero fitted parameters, from the two listings: the shipped R3's
prologue bounds-checks `buf[off]`, `buf[off+1]`, `buf[off+2]`, `buf[off+3]`
separately (11 instructions: `cmp %rsi,%rdx; jae` then 3× `lea/cmp/jae`).
Reslicing the window first makes `w.len() == len >= 4` visible, and LLVM
collapses all four into the single reslice test (`mov %rcx,%rax; add %rdx,%rax;
jb; cmp %rsi,%rax; ja`). The loop body is unchanged, 13 instructions, identical.

**So the published safety column is a biased difference and the bias points the
way p36's story wants**, exactly as `TASK_072_REVIEW.md` A2 predicted:

| pair | law | small | large |
|---|---|---:|---:|
| **published** `R3ship − R4ship` | `+15` flat | +15 | +15 |
| `r3_window − R4ship` | `+7` flat | +7 | +7 |
| `R3ship − r4_reslice` (the pair `gen_controls.py::c_r4_reslice`'s own docstring calls *"the matched-spelling safety number"*) | `+10` flat | +10 | +10 |
| `r3_window − r4_reslice` | `+2` flat | +2 | +2 |

Failure scenario: `.memory/` records *"p36's safety column is 15.00 Ir per call,
flat"* as ladder finding 23. The next task quotes it against p16/p17's
per-call constants. It is 2× to 7.5× too large, and the one-line R3 that shows
it is the same respelling any reviewer would try first — this is p22's
`+2.00`-against-`+125/+1021` miss in the other direction.

⚠ There is also a **live internal contradiction** in the same commit:
`controls/gen_controls.py::c_r4_reslice` says `r4_reslice` is the matched pair
and its difference from R3 is the matched-spelling number (+10); `NOTES.md` §8b
says *"the shipped R4 is R3's loop structure with the checks removed, which
makes `R3 − R4` a matched-spelling difference"* (+15). Both cannot be the
matched-spelling number, and the one that ships as the headline is the larger.

### BLOCKER B2 — every published `Ir` is kernel-EXCLUSIVE on the one pattern whose kernel *is* a call, and the excluded work is NOT equal across cells

`controls/sweep_ir.py::counters` and `controls/gen_controls.py::ir_per_call`
report the callgrind **exclusive** cost of the kernel symbol.
`.memory/03-measurement.md`'s p13 rule (*"the kernel-exclusive column is
comparable only when the rungs call the SAME routines … it is the wrong column
when the rungs dispatch DIFFERENT work outward"*) is the governing rule and it
was not applied — `NOTES.md` states the exclusion in its header and never
checks its consequence.

Measured (`.temp/p36rev/callee_ir.py`, `-O3 isolated`, 20 000 calls):

```
cell                  kern-excl/call  dispatch targets   TOTAL/call     (small.bin)
c-gcc                      1319.0000          512.0000    1855.3740
c-gcc-h                    1574.0000          512.0000    2110.3749
c-clang                    1439.0000          384.0000    1846.2514
safe_tuned  (R3)           1710.0000          384.0000    2126.1998
unsafe      (R4)           1695.0000          384.0000    2111.1905
r_fnptr                    1311.0000          384.0000    1727.1863
r_match                    2035.7726            0.0000    2067.9569
c_switch                   2411.5795            0.0000    2435.9527
```

The dispatch targets are **not** equal: **4.00 Ir/record for gcc, 3.00 for
clang and rustc, 0.00 for `r_match`/`c_switch`.** Cause, disassembled:
Debian gcc defaults to `-fcf-protection=full`, so every `opN` begins with
`endbr64`; clang's and rustc's do not (49 `endbr64` in the `c-gcc` binary
against 5 in every other). Rebuilding the C rung with `-fcf-protection=none`
moves the target column 512 → 384 and the total 1855.37 → 1726.33.

Three published claims move:

1. **`r_match` is DEARER reverses.** `NOTES.md` §6b: *"⚠ **And it is DEARER,
   which was not the expected direction.**"* — and that sentence is quoted
   inside `spec.md`'s hashed `slb-contract` `idiom.why` as the justification
   for `forbidden[0]`. On the comparable column (kernel + what it dispatches
   to) `r_match` is **cheaper** than the shipped R3 by **58.23 / 507.00** Ir per
   call; program totals agree exactly (2067.96 vs 2126.20; 15958.79 vs
   16465.81). The `match` spelling has no callees at all, so the kernel column
   credits the table spelling for 384 / 3072 Ir it moved outward. `c_switch` on
   the C side stays dearer (+325.6 / +2677), so the direction claim survives for
   C and reverses for Rust.
2. **The gcc-vs-clang C difference vanishes.** `10.00000` vs `11.00000`
   kernel-exclusive becomes `14.00000` vs `14.00000` on kernel+targets. The
   whole gap is gcc's `endbr64`.
3. **§8a's C-vs-Rust figure is understated by 1 Ir/dispatch.** *"Against the
   hardened C rung `c-gcc-h` (12.00000·nrw + 38), a guarded Rust `fn`-pointer
   table is **2.00000 Ir per dispatch cheaper**"* → on kernel+targets
   `c-gcc-h` is `16·nrw + 38` and `r_fnptr` is `13·nrw + 31`, i.e. **3.00000**
   cheaper. The ordering against clang (`14`/`18`) still holds.

✅ **What does NOT move: the 3.00000 Ir per dispatch of §8a.** `r_fnptr` and the
shipped R4 both dispatch 3 Ir outward, so the difference is 3 on either column.
See the clean-negatives list.

Failure scenario: `.memory/` records *"the idiomatic `match` spelling is dearer
than a dispatch table"*, which is the load-bearing justification for p36's most
important `forbidden` entry, and it is false on the column the rule says to use.
Second scenario: a cross-pattern C-vs-Rust table quotes p36's `10` for gcc and
`13` for Rust and attributes 3 instructions to Rust when 1 of them is gcc's CFI
flag pointing the other way.

⚠ **The rule that governs this is also too narrow as written.**
`.memory/03-measurement.md` says *"list the `@plt`/`@GLIBC` calls of every cell"* —
p36 is the first pattern where the outward-dispatched work goes to the
pattern's **own** functions, so the rule as spelled would not have fired.

### MAJOR M1 — `r4_reslice`'s Verus twin builds first try, in four `assert` lines

`NOTES.md` §8b and §11c: *"`r4_reslice`'s Verus twin was NOT built … it needs
`vstd::slice::slice_subrange` and the subrange-indexing proof that goes with it,
which is real work this task did not do. **Its number is therefore reported and
NOT counted in the span.**"*

`~/tools/verus/vstd/slice.rs::slice_subrange` exists at the pin. Derived from
`patterns/p36-vtable-dispatch/verus.rs::kernel` by exact-string substitution
(`.temp/p36rev/mk_v_r4_reslice.py`), first attempt:

```
wrote .temp/p36rev/controls/v_r4_reslice.rs
verification results:: 12 verified, 0 errors
[exit 0]
```

Same obligation count as the shipped R5 (12), **8 `external_body` items — the
same 8 as `verus.rs`, no new trusted item**, and compiled it satisfies p36's own
`identity` pin:

```
v_r4_reslice (R5 twin)  n_fn=65 nopad=64 bytes=229 norel=331866716dd75a12ed735fc73b20e938
r4_reslice   (R4 ctrl)  n_fn=65 nopad=64 bytes=229 norel=331866716dd75a12ed735fc73b20e938
identity: md5_fn_norel eq = True ; checksums equal on small.bin and large.bin
```

So `r4_reslice` **is** an admissible R4. The R4-side span has **three** verified
members, not two; 1700/13348 is interior so the endpoints do not move, but the
matched-spelling pair becomes admissible-to-admissible at **+10.00 flat** and
§11c's "what was NOT done" item is done. The added proof is:
`assert(off + 4 + 2*nw <= buf@.len()) by { assert(2*nw <= len - 4); }`, two
`invariant` lines and two subrange-index `assert`s.

### MAJOR M2 — the hashed contract and `verus.rs` describe the SUPERSEDED R4

`patterns/p36-vtable-dispatch/spec.md`'s `identity[…].why` — **inside the
`slb-contract` block whose sha256 is the whole §11a disclosure artefact** — says

> *"Measured: the two kernels are **60 instructions and 193 bytes** each … and
> EXACTLY ONE INSTRUCTION of the sixty differs — `lea 0x3f6ad(%rip),%rsi`
> against `lea 0x3f7ed(%rip),%rsi`"*

and `patterns/p36-vtable-dispatch/verus.rs`'s `trait Op` comment repeats *"same
60 instructions, same 193 bytes"*. `controls/mkcontract.py` carries the same
text, so regenerating reproduces it.

The shipped rungs are **55 / 54 / 170** and the instruction is
`lea 0x3f6af(%rip),%r12` against `lea 0x3f70f(%rip),%r12`. The gate's own record
in the same commit says `counts_a: [55, 54, 170]`. **60 instructions / 193 bytes
and `%rsi` are `r4_cursor`'s** — the R4 that §8b says was replaced:

```
-- r4_cursor  n_fn=60 n_fn_nopad=59 bytes=193
   lea    0x3f6ad(%rip),%rsi
```

`NOTES.md` §5 and §5a have the correct numbers, so this is a stale copy the
§8b rung change did not reach. Failure scenario: a reader checks the `identity`
pin's justification against the binaries, finds no 60-instruction kernel and no
`%rsi`, and cannot tell whether the pin or the disassembler is wrong. §11a's
direction test asserts *"Four entries gained measured numbers where they had
promises"* — one of those numbers is from a rung that no longer exists.

### MAJOR M3 — *"p36 is the first pattern here whose kernel REFERENCES A GLOBAL OBJECT at all"* is false

That sentence is the stated **cause** for `identity: O3 norel`, and it appears
in both `NOTES.md` §5a and the hashed `spec.md` `identity.why`. Swept
(`.temp/p36rev/riprel_sweep.py`, `harness/asm.py`'s pipeline, `-O3 isolated`
`unsafe` kernels): **ten other patterns' kernels carry rip-relative operands** —
p02 1, p03 1, p04 1, p06 5, p08 16, p12 1, p13 2, p14 3, p27 5, p38 1, against
p36's 1 — and p06, p08 and p14 take the **address** of a `.data.rel.ro` object
with exactly p36's instruction form:

```
p08   unsafe-O3-isolated   lea 0x3f579(%rip),%rcx -> 0x54ea8 in .data.rel.ro
p06   unsafe-O3-isolated   lea 0x3f4dd(%rip),%rcx -> 0x54e98 in .data.rel.ro
p36   unsafe-O3-isolated   lea 0x3f6af(%rip),%r12 -> 0x54f98 in .data.rel.ro
```

All of those hold `exact` because **their R4 and R5 displacements are equal** —
the object moves with the kernel. p36's do not (`0x3f6af` vs `0x3f70f`, 96 bytes
apart). The true statement is *"p36 is the first pattern whose kernel references
a global that R4 and R5 place at different distances"*, and the mechanism is
M4 below. Failure scenario: `.memory/` records *"a kernel that references a
global cannot hold `exact`"* and the next pattern relaxes its pin on a false
premise, when in fact three patterns do it today at `exact`.

### MAJOR M4 — finding 1 needs a scope clause: a `spec fn` in a trait is NOT erased, and it costs 64 bytes

`NOTES.md` §5 concludes *"finding 1 … **survives**: 55 = 55 instructions,
170 = 170 bytes, in both orders."* That is true of the kernel **function**.
It is not true of the binary. Measured on the shipped pair
(`.temp/p36rev/vtable_size.log`):

```
unsafe-O3-isolated: TABLE@0x54f98  vtable addrs 0x54e98 … 0x54f78  gaps 32,32,…  -> vtable = 32 bytes
verus -O3-isolated: TABLE@0x55108  vtable addrs 0x54fc8 … 0x550e0  gaps 40,40,…  -> vtable = 40 bytes

verus vtable[0] 0x54fc8..0x54ff0:
  0x54fe0 -> 0x15b70  <verus::OpTag<0> as verus::Op>::apply
  0x54fe8 -> 0x15b50  <verus::OpTag<0> as verus::Op>::spec_apply       <-- the GHOST item
unsafe vtable[0] 0x54e98..0x54eb8:
  0x54eb0 -> 0x15a40  <unsafe::OpTag<0> as unsafe::Op>::apply
```

All eight R5 vtables' slot 4 point at one folded **26-byte emitted
`<OpTag<0>>::spec_apply`**. So in the **shipped** configuration — `apply`
declared first, `identity` green — the proof costs **64 bytes of
`.data.rel.ro` (8 types × 8 bytes) plus 26 bytes of `.text`** that R4 does not
have, and that 64 bytes is most of the 96-byte displacement shift that forced
`norel` (M3). RECAP finding 1 / `.memory/01-ladder.md` finding 1 says *"ghost
code fully erases"* and *"the proven binary is byte-identical to the unproven
one"*: on p36 the first clause is **false** and the second is false at
`md5_fn` (`60e41a42…` vs `244e6712…`).

**Recommended scope clause:** *a Verus proof costs zero executed instructions
and zero instructions in the kernel symbol; ghost code erases from executable
paths, but a `spec fn` declared in a **trait** is codegenned as a stub and
occupies a vtable slot in every implementing type — 8 bytes per type of
`.data.rel.ro`, and its declaration position is part of the vtable ABI.*
This is strictly stronger than p36's *"a ghost declaration moved a byte of the
object code"*, which is only observable when the ghost is declared first.

### MAJOR M5 — the `identity` pin is blind to p36's dispatch table at **every** level, `exact` included

The task asked whether an R5 could differ from R4 in a way `norel` accepts and
`exact` catches. The answer is worse and more useful: **on p36 neither level
sees the table.** `.temp/p36rev/norel_attack.log`, `unsafe.rs` with `TABLE`'s
eight entries reversed and nothing else changed:

```
A_ship            n_fn=55 bytes=170 md5_fn=60e41a42f72a8d80143b5494d8b267a9  checksum=195445626134389610
B_permuted_table  n_fn=55 bytes=170 md5_fn=60e41a42f72a8d80143b5494d8b267a9  checksum=11308767923991984952
A vs B: md5_fn(EXACT) eq=True  md5_fn_norel(NOREL) eq=True  checksum eq=False
```

The kernel is **byte-identical** and the program computes a different answer,
because the whole dispatch mechanism is *data* outside the kernel symbol.
✅ The gate is **not** unsound: stage 2 compares checksums against `model.py`
and fails immediately. But `NOTES.md` §5's *"the `identity` pin caught it"* and
§5a's *"`norel` is the level that says so precisely"* need the scope clause
**"of the kernel function's bytes"** — on this pattern the pin's coverage of the
thing the pattern is about is zero, and the checksum stage is what carries it.

### Minors

- **m1 — §7's stated reason for `Ir`-constancy does not apply to the metric it
  quotes.** *"⚠ The `t` band does **not** hold the opcode multiset fixed, so this
  is not true by construction — it holds because all eight op bodies are the same
  size (§6)."* The quoted number is kernel-**exclusive**, which excludes the
  eight callees entirely, so for that number it **is** true by construction.
  ✅ The stronger statement is true and I measured it: **program-total `Ir` is
  also identical across `sweep-t1/2/4/8` — 8,635,685 in all four**, with
  `callees/call = 768.0000 = 256 × 3` on all four (`.temp/p36rev/ir_totals.py`).
  §6's size measurement is load-bearing for *that*, not for the published figure.
- **m2 — the 4.19% noise floor is not reproducible and is ~14× too pessimistic.**
  Four independent floors, 5 byte-identical copies × 31 reps each:
  interleaved on `sweep-t1` **0.31%**, interleaved on `sweep-t8` **0.19%**,
  blocked on `sweep-t1` **0.55%**, blocked on `sweep-mixrand` **0.79%**.
  Direction is conservative — §7's *"51.7 times the noise floor"* is really
  ~400–1100× — but 4.19% is the denominator of p36's only significance claim.
  ⚠ `controls/sweep_ir.py::main` times **all reps of one blob, then all reps of
  the next** — blocked by blob, which is what RECAP finding 16's methodology rule
  forbids. It did not change any ordering here (clean negative, below), but the
  script is the wrong shape for the next pattern that copies it.
- **m3 — `inputs/gen.py`'s residue-class documentation is wrong, in two places.**
  Its module docstring and `gen.py::sweep`'s band-n comment both say band n's
  `nrw mod 8` residues span `{0, 2, 4, 6}`. The true set is `{0, 1, 2, 5, 6, 7}`
  — which is what `gen.py`'s own printed rows say and what `NOTES.md` §4 says.
  ("both parities of `nrw mod 3`" is also not a thing.) The measurement is
  unaffected; the coverage is better than the generator claims. This is the one
  file the RESIDUE-CLASS rule exists to make checkable.
- **m4 — `NOTES.md` §11a's heading says *"⚠ IT MOVED TWICE"* and then lists
  five edits** (`f8d00370… → 57b16147… → 430c64b9… → f00aeb26… → de149ffb… →
  ffb7fc4a…`). The shipped-hash arithmetic is right: I recomputed
  `sha256(slb-contract block + "\n") = ffb7fc4a68e73342b3efe0c2e17b44ea0df5542c83822737a580d42991b3b1d2`,
  matching `results/gate/p36-vtable-dispatch.json::contract_sha256`. Only the
  heading is wrong. (The four intermediate hashes are unverifiable in principle
  on a one-commit pattern; `NOTES.md` §11a says so correctly and does **not**
  cite the vacuous `git show HEAD:` command — that instruction was followed.)
- **m5 — six new instances of the live "finding 14 / finding 15" citation
  collision.** `.memory/01-ladder.md`'s numbering warning names this collision
  explicitly (*"finding 14 is p13 here and 'every rung is a spelling' in
  RECAP.md … two task files have already sent an agent to the wrong finding"*).
  p36 writes `.memory/01-ladder.md` **finding 14** in `unsafe.rs`, `verus.rs`
  (×2), `safe_naive.rs`, `NOTES.md` §0a and §8a, and `spec.md`'s `idiom.why`
  (that last one is the shared paragraph, already in p22/p27/p38/p47 — not
  p36's doing), and `.memory/01-ladder.md` **finding 15** in `NOTES.md` §7 and
  `controls/clayout.py`. In that file 14 is **p13** and 15 is **p06**; the
  intended entries are RECAP's 14 (*every rung is a spelling*) and RECAP's 15
  (**p07**, whose ladder number is **8**). ⚠ **`TASK_072_REVIEW.md` itself
  repeats both mis-citations** in its reading list.
- **m6 — `controls/mkmutants.py::m2`'s docstring over-claims.** It says the
  mutant exists *"to show … that `op_fold` really is pinned to the dynamic types
  in `TABLE`"*. Measured, it fails at `OpTag::apply`'s own postcondition and the
  kernel is never reached, so it shows nothing about `op_fold`'s tie to `TABLE`.
  `NOTES.md` §10/m2 records this honestly; the generator's docstring does not.
  ✅ **`m3` is the mutant that does establish it** (shift the trusted `ensures`
  by one slot → `invariant not satisfied` in the `run` relation), so the
  property is demonstrated — by a different mutant than the one that claims it.
- **m7 — `harness/vparse.py::duplicate_names` keys items by bare name although
  `vparse.parse` already computes each item's enclosing `impl`** (`in_impl` /
  `inner_impl` are built there from `impl_spans`). That is what refuses eight
  `impl Op for OpN` blocks and forced p36's const-generic spelling. It is a
  real `harness/` limitation rather than a soundness requirement — Rust has no
  ambiguity between `Op0::apply` and `Op1::apply`; the gate's name→item map
  does. Reported, not fixed; note it would also require `spec.md`'s
  `verus.obligations` keys to be qualified, so it is not a one-liner and
  PROTOCOL rule 5's "could this happen by accident?" test applies.

---

## Evidence

### Reproduction (everything below re-run from the committed tree)

```
$ harness/check.py p36                                        -> check.py: PASS
   verdict PASS, failures [], complete_run true
   diff against the committed JSON: TWO fields, both the ASLR address inside
   sanitizer diagnostics. Restored: git checkout -- results/gate/p36-vtable-dispatch.json
$ harness/measure.py --check-stale
   FRESH  results/p36-vtable-dispatch.json   18 source(s) + 7 input(s)
   44 record(s) examined, 0 STALE
$ sha256(spec.md slb-contract block + "\n") = ffb7fc4a68e7…  == gate contract_sha256
$ inputs/gen.py --sweep into two scratch dirs: diff -r empty, and every one of
   the 31 committed .bin files is byte-identical to the regeneration
```

### The controls table (`NOTES.md` §8) — all seven reproduce exactly

```
c_switch    2411.5795 / 19099.0000      r4_reslice  1700.0000 / 13348.0000
r2_nodead   3498.0000 / 27690.0000      r_fnptr     1311.0000 / 10271.0000
r3_idx      2232.0000 / 17464.0000      r_match     2035.7726 / 15923.0000
r4_cursor   2717.0000 / 21533.0000
checksums:  195445626134389610 / 471216819055512592 on every one
```

### The 3.00000 Ir per dispatch — mechanism, instruction by instruction

```
r_fnptr loop body (10):  movzbl ; xor ; mov %rax,%rdi ; call *(%r12,%rcx,8) ;
                         add $0x2 ; dec ; je ; movzbl ; cmp $0x8 ; jb
dyn    loop body (13):  movzbl ; shl $0x4,%ecx ; mov 0x8(%rcx,%r12,1),%rcx ;
                         xor ; mov $0x1,%edi ; mov %rax,%rsi ; call *0x18(%rcx) ;
                         add $0x2 ; dec ; je ; movzbl ; cmp $0x8 ; jb
```
Prologue, epilogue and sentinel arm are instruction-identical; both intercepts
are 31; `n_fn` 52 vs 55. The 3 are the fat-pointer index scale, the vtable load
and the ZST `self` (`mov $0x1,%edi`) against the `fn` pointer's `mov %rax,%rdi`.
**Survives the B2 column change**: 13 vs 16 on kernel+targets, still +3.

### The vtable finding (`v_specfirst`) — reproduced

```
./verus_run.py --compile v_specfirst.rs ... -C opt-level=3   ->  12 verified, 0 errors
R4 unsafe  n_fn=55 nopad=54 bytes=170 md5_fn_norel=d2cea805…  call *0x18(%rcx)
R5 verus   n_fn=55 nopad=54 bytes=170 md5_fn_norel=d2cea805…  call *0x18(%rcx)
specfirst  n_fn=55 nopad=54 bytes=170 md5_fn_norel=2155d310…  call *0x20(%rcx)
```

### Wall clock, re-measured INTERLEAVED (`.temp/p36rev/wall_rr.py`, 31 reps, `taskset -c 3`)

```
band t   : t1 424.15   t2 610.38   t4 1198.34   t8 1320.48   -> 3.11x  (§7: 3.17x)
band mix : rand 792.50  run001 458.10  run002 464.70  run004 456.77
           run008 444.21  run016 609.08  run032 507.69
floors   : t1 copies interleaved 0.31% | t8 copies interleaved 0.19%
           t1 copies blocked     0.55% | mixrand copies blocked 0.79%
```

### The mechanism §7 does not give — and the alternative it does not exclude

`TASK_072_REVIEW.md` A1 asks whether an I-cache/DSB **footprint** effect is
excluded. **It is, by p36's own inputs, with zero fitted parameters:**

- `sweep-mixrun008` touches **all eight** callees (multiset fixed, 32 of each
  per window) and runs at **444.21 ns**;
- `sweep-t1` touches **one** callee and runs at **424.15 ns**.

Same binary, same blob shape (3120 bytes, 6 windows, 256 records, stride 516),
same `n_iters`. 8 targets vs 1 target costs **4.7%**; the effect is **3.11×**.
So footprint is not the mechanism. `sweep-mixrun001` (all eight targets, a
period-8 cycle, a *switch on every single dispatch*) is 458.10 ns — so
switching **frequency** is not the mechanism either. What is left is
**predictability**, and it is quantitative: taking ~9–10 ns (≈20 cycles at
2.1 GHz) per real mispredict and 256 dispatches per call,

| blob | last-value mispredicts/call | predicted Δns | measured Δns vs the 444–458 floor |
|---|---:|---:|---:|
| `run001…run008` | 256/R, but a *period ≤ 64* history the ITA learns | ≈0 | 0 |
| `run016` (period 128) | 16 | ≈155 | **+165** |
| `run032` (period 256) | 8 | ≈78 | **+63** |

That is the **non-monotone middle** §7 leaves unattributed: `run032` is faster
than `run016` because once the history predictor fails, the last-value fallback
is right `(R−1)/R` of the time, so a *longer* run mispredicts *less*. The
crossover sits between R=8 and R=16, i.e. at a learnable period of about 64.
The non-monotonicity **reproduces under the interleaved protocol** (609.08 vs
507.69), so it is not a protocol artefact.

### `mixrand6` — §7's disclosed direction is right, and it hides a better headline

`NOTES.md` §7 discloses that `sweep-mix*`'s six windows share one 256-opcode
sequence while `sweep-t*`'s six differ (1536 positions), and asserts this makes
the mix band **understate**. Built the missing control (`.temp/p36rev/mix6.py`):
six *different* permutations of the *same* multiset, so `Ir` is still fixed by
construction.

```
                 kern-excl/call   PROGRAM TOTAL     Bi       Bim    Bim/Bi   min ns/call
mixrand6            3359.0000        8635672      513089   447918   0.8730     1845.33
sweep-mixrand       3359.0000        8635721      513089   444415   0.8662      785.67
sweep-mixrun008     3359.0000        8635739      513089    64415   0.1255      444.21
sweep-t8            —                —            —        —        —          1318.58
sweep-t1            —                —            —        —        —          422.83
```

- The disclosure is **confirmed and its magnitude is 2.35×**.
- **A stronger headline exists in p36's own design space**: on the band where
  `Ir` is constant *by construction* (multiset fixed), the wall-clock spread is
  `mixrand6 / mixrun008 = 4.15×`, against the published 3.17× on the band where
  `Ir`-constancy has to be argued.
- **And it sharpens §7's clean negative about `Bim` enormously**: `mixrand6`
  and `mixrand` have simulated indirect-mispredict rates **0.8730 and 0.8662** —
  0.8% apart — and differ **2.35×** in wall clock. §7's version of this negative
  compares 0.9987 against 0.8662 across 1.75×; this pair holds `Bim` all but
  constant and moves time by more.

### A0(c) — is the headline p07's finding in a costume?

Both are "one binary, vary the input, `ns` and `Ir` disagree", so the **shape**
is p07's (RECAP finding 15 = `.memory/01-ladder.md` finding **8**, p07). Three
differences are real and I checked each:

1. p07's `Ir` **moves** (+7.84%); p36's is **exactly constant** — verified to
   the instruction on the reported kernel-exclusive column **and** on program
   totals (8,635,685 across all four `sweep-t*`), which p36 did not measure.
2. p07's mechanism is a **conditional** branch (`Bc`/`Bcm`), where callgrind's
   simulator **does** order wall clock. p36's is **indirect** (`Bi`/`Bim`) and
   the simulator does **not** — that is a scoping correction to
   `.memory/00-environment.md`'s standing claim and it is new.
3. p07's divergence has the two effects in **opposite** directions (+Ir, −ns);
   p36's holds `Ir` fixed and moves only `ns`.

**Verdict: not a restatement.** The novel content is (2), and it is about the
instrument, not about p36. The right `.memory/` sentence is *"callgrind
`--branch-sim`'s `Bi` counts and its `Bim` does not predict — established on
indirect branches at p36, where two blobs 0.8% apart in simulated mispredict
rate differ 2.35× in wall clock"*, not *"p36 found a new `Ir`/`ns` divergence"*.

### A0(a) — the catcher finding, and the converse

All four legs verified: UBSan/ASan name the **array read** (gate stage 7 output
in `results/gate/p36-vtable-dispatch.json::sanitizer`); `-fsanitize=function` is
**unrecognised by gcc 13.3.0** and accepted by clang; it is **defeated** here
(`SEGV on unknown address 0xfffffffffffffff9`, the signature word at
`target − 7`); `-fsanitize=cfi-icall` names the transfer at `9.00000·nrw − 2`.

**The converse the write-up does not state, and it matters:** on p36 there is
**no** input on which the array read is in bounds and the call is wrong.
`TABLE[op]` for `op < 8` is always a correctly-typed `uint64_t(*)(uint64_t)`,
so ASan/UBSan and CFI fire on **exactly the same input set**. The CFI column is
therefore honest about **vocabulary** and adds nothing in **coverage**.
That makes (a) a finding about the **checker set**, and it should be stated
that way: *the checkers this project runs can name a control-flow bug only as
the data read that precedes it; on this bug class that costs no coverage, and
the reason it costs no coverage is that the two events are the same event.*

⚠ **And p36's C column is already paying for a CFI mitigation it does not
price.** §8d says *"the real-world hardened answer … is a compiler mitigation
this matrix cannot price"*. gcc's default `-fcf-protection=full` puts an
`endbr64` IBT landing pad on all eight dispatch targets, at **1.00 Ir per
dispatch** (512 → 384 target Ir/call with `-fcf-protection=none`; total
1855.37 → 1726.33). So the matrix prices **two** points of the CFI curve
already — IBT landing pads at 1.00 Ir/dispatch in gcc's column only, and
`cfi-icall` at 9.00 — and neither is mentioned.

### Verus, re-run

```
v_r4_cursor  12 verified, 0 errors                 v_specfirst  12 verified, 0 errors
v_r_fnptr    `does not yet support ... function pointer types` x3, exit 1
v_r4_reslice 12 verified, 0 errors   (REVIEW, new)
m1  11 verified, 1 errors  -> TWO errors: `invariant not satisfied` (run) AND
                              `precondition not satisfied: i < NOPS`
m2  11 verified, 1 errors  -> postcondition, at OpTag::apply
m3  11 verified, 1 errors shipped ; 13 verified, 1 errors --cfg slb_twin (both fail)
m4  12 verified, 0 errors shipped (SILENT) ; 13 verified, 1 errors --cfg slb_twin
    -> `precondition not met: index in bounds for this access`  = genuinely twin-only
```

TCB recount: `verus.rs` has **4** `#[verifier::external_body]` items
(`buf_get_unchecked`, `tab_get_unchecked`, `load_input`, `emit`), 2
contract-bearing, both with verified twins, 0 `assume`, 0 `assume_specification`,
0 `admit`. `grep -n 'assume\|external_body\|external\b\|assume_specification'`
returns those four plus comments. **The §7bis tally is accurate.**
`v_r4_reslice` adds none.

### MSan spot-check (out of scope for TASK_072, and correct)

```
$ ~/tools/llvm/bin/clang -std=c99 -O1 -g -fsanitize=memory \
      -fsanitize-memory-track-origins=2 .temp/p48probe/msan.c -o msan
$ ./msan
==3808107==WARNING: MemorySanitizer: use-of-uninitialized-value
  Uninitialized value was created by an allocation of 'buf' in the stack frame
$ /usr/bin/gcc -std=c99 -O1 -fsanitize=memory msan.c -o x
gcc: error: unrecognized argument to '-fsanitize=' option: 'memory'
```
Both halves reproduce. One omission: the probe exits **1**, which
`.temp/p48probe/NOTES.md` does not record and p48's `sanitizer_expect` will need.

---

## Clean negatives — 36 named attacks that did NOT land

**Reproduction / bookkeeping**
1. Gate re-run diverges from the committed record — **no**, only the ASLR
   address inside two diagnostic strings.
2. `measure.py --check-stale` shows p36 STALE after the doc edits — **no**,
   44 records, 0 STALE.
3. The committed `.bin` blobs are not what `gen.py` produces — **no**, all 31
   byte-identical, twice.
4. `contract_sha256` in the gate JSON does not match the shipped `slb-contract`
   block — **no**, `ffb7fc4a68e7…` both.
5. `spec.md` is not what `mkcontract.py` produces (generator/artefact skew) —
   **no**, `--check` is in the README recipe and the hash matches.
6. `.temp/p36/` left undeletable blobs — **no**; `bin/` is gone,
   `rebuild_bin.sh` is present, only `.rs`/`.c`/`.py`/`.log`/`.md` remain.
7. §11a cites the vacuous `git show HEAD:` disclosure command — **no**, it
   explicitly refuses to and says why.

**Benchmark validity**
8. Constant folding / no real loop — **no**, every rung has a real backward
   branch and the marginal `Ir` is linear in `nrw` with zero residual.
9. A constant leaked in instead of file data — **no**, `Ir` moves 8× across the
   `n` band and the checksums track the blob.
10. The result is not consumed — **no**, `driver::emit(acc)` and stage-4 stdout
    matches `model.py` on all seven inputs.
11. A rung quietly changed the algorithm — **no**, all eight rungs agree with
    `model.py` on every non-adversarial input and the two adversarial ones.
12. The C rung is Rust-in-C-syntax written to lose — **no**, `c/kernel.c` is a
    textbook `static uint64_t (*const TABLE[N])(uint64_t)` interpreter, and it
    is the *cheapest* cell in the matrix.
13. R2 is deliberately pessimised — **no**; its 27 vs 13 is 6 panic sites and
    whole-blob indexing, and `r2_nodead` isolates the table check at exactly 0.
14. R3 is not actually check-free in the loop — **confirmed check-free**; the
    disassembly of `safe_tuned.rs::kernel` has no length `cmp`/`jae` in the loop
    body, exactly as §4 prints it.
15. A perf claim rests on an `O0` row — **no**, every published figure is `-O3`.
16. A C-vs-Rust claim without a clang column — **no** in `NOTES.md` §4/§8a
    (both compilers, both hardened and not). ⚠ `README.md`'s rung table lists
    gcc only, but the clang laws are one file away and B2 is the real issue.
17. Inline mode unlabelled — **no**; `NOTES.md`'s header, §7's tables and
    `README.md`'s rung table all say `-O3 isolated`.
18. `sweep-t*` does not hold the record count / window shape fixed — **it
    does**: all four are 3120 bytes, stride 516, 6 windows, `nrw = 256`,
    `n_iters = 2000`. (It does vary the operand seed with `k`, `71·w + k` in
    `gen.py::sweep` — undisclosed, but operands feed no branch and `Ir` is
    identical, so it does not bite.)
19. `sweep-mix*` does not really hold the multiset fixed — **it does**;
    `gen.py::mix_orders` asserts it, and `Bi` is 513089 on every blob of the band.
20. The `sweep-mix*` non-monotone middle is a blocked-protocol artefact —
    **no**, it reproduces interleaved (`run016` 609.08 > `run032` 507.69).
21. The blocked floor protocol manufactured the 3.17× — **no**; interleaved
    gives 3.11× and both floors are under 1%.
22. The "no layout population" argument is unsound — **it is sound, and say so
    loudly.** One binary on several inputs holds code layout fixed by
    construction; the byte-identical-copies floor is the *right* control for
    what is left (the file name/path and the run-to-run environment), and it
    measures 0.19–0.31% interleaved. A layout population would answer a question
    p36 does not ask. `controls/clayout.py` is shipped for the day it does, and
    its `OUT` really does point at `.temp/p36/`, not `.temp/p14/`.
23. `Ir` is not exactly constant across `sweep-t*` — **it is**, on both the
    kernel-exclusive column and program totals.
24. The `Ir` floor is vacuous — **no, but it is slack**: `work_per_call =
    stride`, default `0.25` Ir/byte, measured ≈6.5 Ir/byte, so ~26× margin. It
    could only have caught near-total elimination of the kernel.
25. `r_match`'s non-integer `Ir` is a measurement artefact — **no**, it is real
    (2035.7726 on `small`) and the stated cause (arms of different length →
    opcode-dependent instruction count) is right; the shipped rungs are exact
    integers on every blob.

**Verus**
26. An unjustified `assume` / `external` / `assume_specification` — **none**;
    4 `external_body`, each justified in a comment, 2 with contracts.
27. The TCB tally is wrong — **no**, recounted: 4 items, 2 contract-bearing,
    2 V-gap, 2 infra, 0 U-license.
28. The trusted `requires` are vacuous or the call site is dead — **no**; the
    gate's `requires_strength` shows 3 conjuncts probed and none a tautology
    under bare Z3, `nonlinear_arith` or `bit_vector`, and `verified_call_site`
    is `{main: 5, kernel: 2}`.
29. R5's exec code drifted from R4's — **no**: 55/54/170 both, `md5_fn_norel`
    equal, and the only differing instruction is the `TABLE` `lea`.
30. The mutants fail on a different obligation than claimed — **no**, all four
    match `NOTES.md` §10 verbatim, including m1's honestly-disclosed *two*
    errors and m3's honestly-disclosed wrong prediction.
31. `m4` is not really twin-only — **it is**: `12 verified, 0 errors` shipped,
    `precondition not met` under `--cfg slb_twin`.
32. `m2` is a no-op — **no**, it is live (`11 verified, 1 errors`); only its
    generator docstring over-claims what it demonstrates (m6).
33. A cheaper *admissible R4* was missed — **no**. `r4_reslice` at 1700 is
    *dearer* than the shipped 1695, `r4_cursor` at 2717 much dearer, and
    `r_fnptr` at 1311 is inadmissible (`is not supported` ×3, reproduced).
    The R4-side endpoint does not move. The miss is on the **R3** side (B1).
34. `required_absent: 2` are the "backticks the replacement" or substring
    false-positive shapes — **no**, both are genuine scoped absences on
    `c/kernel.c` (`op < SLB_P36_NOPS`, `acc * 31 + SLB_P36_SENT;`), which is the
    pattern's bug, and `required_pins_nothing` is 0 with
    `forbidden_unaudited_entries` 0 over 11 forbidden spellings.
35. §0d's "0 of 534" is wrong — **no**; the classifier separates GOT-indirect
    from computed-target correctly, and `README.md` and `NOTES.md` both state
    the narrowed claim rather than the task file's false one.
36. §0c's "24/24 SIGSEGV" is not what the matrix records — **it is**; the gate's
    `adversarial` block shows `exit -11` for `c-gcc` and `c-clang` on both
    out-of-table blobs in all four (opt × mode) cells, and the hardened C and
    all four Rust rungs return the model's checksum.

---

## Unsure / not done

- **I did not construct a cheaper *admissible R4*.** Attack 33 is a negative,
  not a proof of minimality; `13·nrw + 31` may not be the floor.
- **B2's corrected column is "kernel + the eight dispatch targets", which is not
  a column the harness records** (`results/p36-vtable-dispatch.json` carries
  only `kernel_exclusive_ir`; `total_ir` is absent). I computed it by summing
  `callgrind_annotate` rows. Whether the project should add a totals column, or
  just a per-cell callee marginal, is a `harness/` decision I am not taking.
- **The 9–10 ns-per-mispredict constant** in my branch model is fitted from two
  points (`run016`, `run032`); the *shape* (last-value fallback right `(R−1)/R`,
  history learnable to period ≈64) is zero-parameter and predicts the ordering,
  but the absolute penalty is not independently measured — this box has
  `perf_event_paranoid = 3`.
- **I did not re-run the `sweep-n` band across all eight cells**; I took §4's
  twelve-point laws on the strength of the small/large endpoints reproducing
  exactly for every cell and control.
- **`r3_window` is my spelling, measured but not proof-checked as an R3** — R3
  needs no proof, but I did not run the full gate against a tree with it
  substituted in, so I cannot say the gate is green with it, only that it
  satisfies every pinned spelling under `check.py::spelling_matches` and
  produces identical checksums.
- **I did not verify the four intermediate `contract_sha256` values.** On a
  one-commit pattern they are unverifiable in principle and `NOTES.md` §11a says
  so correctly; I checked only the shipped hash and the internal consistency of
  the five edit descriptions against the shipped text.

---

## Memory updates

None — reviewers do not write `.memory/`. What the manager should land, in
descending order of value:

1. **B1 and B2 before any p36 finding reaches `.memory/`.** The two numbers
   most likely to be written up — `R3 − R4 = +15.00 flat` and *"the idiomatic
   `match` is dearer than a dispatch table"* — are the two this review breaks.
2. **A scope clause on finding 1** (M4), stated as the *measured* fact: a
   `spec fn` declared in a trait is codegenned and occupies a vtable slot in
   every implementing type — 64 bytes of `.data.rel.ro` and 26 bytes of `.text`
   on p36 — so "ghost code fully erases" is scoped to executable paths and to
   the kernel symbol's bytes.
3. **Widen `.memory/03-measurement.md`'s p13 kernel-column rule** from
   `@plt`/`@GLIBC` calls to *any* work the kernel dispatches outward, and record
   the p36 instance (gcc's `endbr64` at 1.00 Ir/dispatch; `match`'s zero).
4. **Correct M3's causal claim** before it becomes *"a kernel that references a
   global cannot hold `exact`"* — three patterns do, today.
5. **The `Bim` scoping correction**, in the sharper `mixrand6` form: 0.8730 vs
   0.8662 simulated, 2.35× in wall clock.
6. **`identity` covers the kernel function's bytes only** (M5) — worth one line
   in `.memory/02-bench-rules.md`, since the checksum stage is what actually
   carries p36's table.
