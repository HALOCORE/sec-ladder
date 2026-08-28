# TASK_113 — review of the debt, starting with the one the synthesis rests on

**Role: research reviewer.** Scratch and every artefact: `.temp/r113/`
(`REBUILD.sh`, `EVIDENCE.log`, `normcmp.py`, `p37_probe.rs`, `lever.rs`,
`div_pin.rs`, `c3_verus.rs`, `c3_verus2.rs`; **all binaries deleted**, every one
rebuilt and re-run by `sh .temp/r113/REBUILD.sh`, which regenerates
`EVIDENCE.log` verbatim). **No `git add`, no `git commit`.** `.memory/`,
`RECAP.md`, `results/`, `synthesis/`, `harness/`, `pilot/` and every
`patterns/*/` file untouched. The only harness script run was
`harness/measure.py --check-stale` (**52 records examined, 0 STALE**).

**Running count: launched from 414.** Reconciliation is the manager's job; the
itemised list I add is at the end.

---

## HEADLINE — finding 37 does not survive. **Both halves fail, and the counterexamples are inside the project's own reviewed record.**

> **This benchmark can price a safety property IF AND ONLY IF some rung emits it
> as a compare-and-branch and another rung omits it.**

**The manager's doubt was right but too kind.** It is not an "only if" wearing an
"iff". **The only-if half is false too**, and the pattern that falsifies it is
`p38` — shipped, reviewed (no blocker, 3 majors, 8 minors, **35 clean
negatives**), and its *quotable result is a price*.

**And the report that produced the generalisation contains the counterexample,
two sections below the boxed claim.** `TASK_102_REPORT.md:578` lists
*"`p06`'s division instead of a compare"* among the fourteen rows that satisfy
the replacement bar — 64 lines after `:513` asserts the fourteen are *"all
compare-and-branch"*. This is PROTOCOL rule 9's documented failure mode
(*"the engineer's own `NOTES.md` sometimes contained the correction one paragraph
below the headline the manager copied"*), except the two halves are in one
report, and the headline went into `RECAP` finding 37 and `SYNTHESIS.md` §5.

---

## §A — the attack

### A1 (blocker) — the ONLY-IF half is FALSE. `p38` prices an aliasing property at exactly `6.00 Ir`/call, five independent ways, with no compare-and-branch in any rung.

`patterns/p38-alias-pun/NOTES.md:962-966`, the pattern's own measured table:

| control | what it changes | `Ir` delta |
|---|---|---|
| `c_symset` | `rec_set_len` puns too — a symmetric pair | **−6.00** |
| `c_once` | `rec_len` called once, clamp via a local | **−6.00** |
| `c_nosa` | identical source, `-fno-strict-aliasing` | **−6.00** |
| `c_memcpy` | `memcpy(&v, r, 4)` | **−6.00** |
| `c_union` | the union spelling | **−6.00** |

The safety property is **type-based aliasing**. Not one of the five fixes is a
compare or a branch: a symmetric setter, a folded read, a *compiler flag*, a
`memcpy`, a `union`. Finding 37 says a property enforced by anything other than a
compare-and-branch *"has no machine-code footprint at all"*. This one has a
footprint of exactly **6.00 `Ir`/call**, exact, five ways agreeing to the unit,
and `RECAP` finding 32 publishes it as **the** quotable p38 result
(*"the UB buys nothing and costs 6, so no optimising programmer arrives here"*).
`TASK_102_REPORT.md:522` files p38 under *"what it CANNOT price"*. That is false
about a shipped pattern whose headline **is** a price.

### A2 (blocker) — the IF half is unsupported by TASK_102, and non-diagnostic where it does apply.

**Nothing in TASK_102 supports sufficiency, and its one test of it came back
negative.** The report says so itself: C3 (division by an attacker-controlled
divisor) is *"the only candidate of the eight that passes probe 2"* — and it was
**refused**. I re-ran it (`EVIDENCE.log` §A4). The boundary is textbook:

```
c3_rust_O3=k_safe    insns=28  norm=03f9f7ce367d      k_safe, in-loop:
c3_rust_O3=k_guard   insns=28  norm=81c5a2ff61b2        mov 0x4(%rdi,%rsi,8),%r9d
c3_rust_O3=k_unsafe  insns=25  norm=7979d80a82c4        test %r9d,%r9d
  k_safe != k_guard != k_unsafe   (three rungs)          je   <panic>   <-- twice, unrolled x2
                                                         div  %r9d
                                                       k_unsafe, in-loop:
                                                         divl 0x4(%rdi,%r9,8)   <-- no test, no je
```

So finding 37's antecedent is satisfied, and by its own "if" half the instrument
**can** price division-by-zero checking — which contradicts the scheduling
consequence drawn from the same paragraph. **B2 (VLA stack clash) satisfies it
too**, and was also refused: gcc's default `-fstack-clash-protection` emits a
probe loop with **2 `cmp …,%rsp`** in `f_vla`, and both
`-fno-stack-clash-protection` and clang-default emit **0** (`EVIDENCE.log` §B1).
**Two of the eight satisfy the antecedent; zero support it.**

**And where the antecedent *is* satisfied the criterion does not say WHICH
property the compare belongs to.** My `p37` probe (§A5 below) is the clean case:
the ladder has a real, isolated compare-and-branch worth `+3` static
instructions, and it belongs to the **dispatch table's `index >= len`**, not to
the type confusion the row is about. `p06` is the same failure in the cost
direction: its safety line `if (m != 0) r %= m; else r = 0;` does contain a
compare — and the `d_cmp` control puts **91.6% of gcc's `+88.08 ns` on the
divide** (`RECAP` finding 26). The criterion is satisfied by a term carrying
8.4% of the effect. `patterns/p06-rotate/c/kernel_hardened.c:8` says it outright:
*"Every earlier pattern's hardened cell adds a compare and a branch. **This one
adds a hardware `div`**."*

### A3 (major) — *"probe 2 says so, in normalised disassembly, every time"* is wrong about five of the eight rows.

I re-ran the three probe-2 kills with `.temp/t104/probe2.py` (which keeps
`<SELF+0xNN>`), as instructed. **All three reproduce — no refused row comes
back.** That is a clean negative and it is worth stating first:

```
b4.so=k_double_fetch  insns=22 norm=7c10d0059428  ==  b4.so=k_single_fetch  (22, same)
c2_gcc_O2=k_cast      insns=19 norm=b61faafb9e30  ==  c2_gcc_O2=k_memcpy    (19, same)
b3_rust_O3=k_safe_naive == k_safe_tuned == k_unsafe  (19 insns, 924b1bafd753, three ways)
                                                     != k_hardened (7ddaf4d05068)
```

But the generalisation is over eight rows and probe 2 was the kill in **three**.
Reading `RECAP` finding 37's own table back:

| candidate | what actually killed it | probe 2? |
|---|---|---|
| recursion depth | ICF-merged callee, R2=R3=R4 | ✅ |
| unaligned load | `k_cast ≡ k_memcpy` | ✅ |
| TOCTOU double fetch | CSE'd to one load | ✅ |
| **division by zero** | **behaviour matrix has one column** (a *harm* criterion) | ❌ **passes** |
| **format string** | **ASLR-nondeterministic harm; cost axis inside glibc** | ❌ |
| **stack use-after-return** | **both compilers warn by default** | ❌ |
| **VLA stack clash** | **`witness_dirty=0` in 24/24** | ❌ |
| **`qsort` comparator** | **glibc 2.39 is a mergesort** | ❌ |

Five refusals rest on harm-matrix, compiler-diagnostic, ASLR-determinism,
cost-attribution and libc-version criteria. **None of those five criteria appears
anywhere in finding 37.** The finding does not explain even the refusals it
claims to generalise.

### A4 (major) — *"no machine-code footprint at all"* is false on the project's own second compiler.

The reviewer checklist asks *"any C-vs-Rust claim without a clang column?"*
C2's clang column moves on **all four** pairs (`EVIDENCE.log` §A2):

```
c2_clang_O2=k_cast     insns=55 norm=9aa3f079c266   != k_memcpy (58, 0349fc9a6409)
c2_clang_O2=k_cast_sum insns=40 norm=e40a8089e9a2   != k_memcpy_sum (40, a94d52a36dda)
```

`TASK_102_REPORT.md` disclosed the 55/58 pair honestly; **`RECAP` finding 37's
table and `SYNTHESIS.md` §5 print only the gcc row.** And B1's footprint is
`+162 Ir`/call, measured by callgrind in the same report. The footprints exist.
What is true is a claim about **attribution** — they are not *safety* footprints
— and that is a different and weaker sentence than the one that shipped.

### A5 (major) — the refusal set is biased, in exactly the direction TASK_111 found.

**All eight candidates were selected for BUG-CLASS NOVELTY** — recursion depth,
division UB, alignment UB, format string, stack-use-after-return, stack clash,
comparator contract, double fetch. **Zero were in the `index >= len` family the
instrument demonstrably prices.** The project's own replacement bar, written in
the same finding, says novelty of the bug class *"predicts neither way"*. So the
eight were drawn on the criterion the project says does not predict, and the
"hit rate of zero on two independent lists" is a property of the sampling frame,
not of the instrument.

The control is in the tree: **`p23`, the fifteenth `index >= len`**, was admitted
under the new bar and built as the 25th pattern, and produced a genuinely new
result — `RECAP` finding 38, *the safety tax is a function of the data's shape*,
`R3 − R4` running `227.00 → 706.37 Ir`, **a factor of 3.11**. A row from the
family the eight excluded was live and productive. *"The catalogue is measured
out"* is a claim about a pool the eight probes never sampled.

### A6 (major) — C3's R4 refusal reason is refuted by measurement. `unreachable_unchecked` and `get_unchecked` are the same machine code.

TASK_102 refused C3's R4 because *"the only stable lever is
`unreachable_unchecked`, which is an **annotation, not an operation** — an R4
that is 'the safe program plus an assumption' prices the assumption, not the
unsafe idiom."* I ran it (`.temp/r113/lever.rs`, `EVIDENCE.log` §A5), with `n`
taken from `argv` so LLVM cannot constant-propagate it (with a literal, all three
bodies fold together and **probe 2 passes vacuously** — I hit that first):

```
r4_operation   (unsafe { *v.get_unchecked(i) })        insns=47 ordered=bb0eb8f177d2
r4_annotation  (unreachable_unchecked(); then v[i])    insns=47 ordered=bb0eb8f177d2   ==
r3_safe        (v[i])                                  insns=52 ordered=f95ac4da4907   !=
all three print 14626866063295383552
```

**The "inadmissible" lever and the lever every shipped pattern uses are
normalised-identical.** And `get_unchecked` is the R4 lever in **26 of 26**
patterns (`grep` over `patterns/*/unsafe.rs`, from 2 to 21 occurrences each). The
distinction has no machine-code content.

✅ **What I did NOT overturn, and this matters:** C3's **second** reason stands —
the behaviour matrix genuinely has one column (C `rc=136` SIGFPE, safe Rust
`rc=101` panic, unsafe Rust `rc=136`; no silent case anywhere). **C3 stays
refused. Only its first reason falls.** The point is that the reason that *does*
hold is a harm criterion finding 37 never mentions.

Two facts for the record while I was there: **Verus at the pin carries a
first-class division-by-zero obligation** — `error: possible division by zero`,
discharged by `requires cnt != 0`, control firing (`c3_verus2.rs`, `2 verified,
1 errors`) — and **`p06` already ships a division-by-zero guard**
(`patterns/p06-rotate/verus.rs:189,621`), so that obligation is not novel either.

### A7 (major) — probe 2 has a FIFTH defect, and it is a false negative on the kill criterion.

`.memory/06-catalogue.md:1164` says probe 2 has been wrong four times. Here is
the fifth, found while re-running C2 on clang:

```
k_cast_sum    insns=40  ordered=e40a8089e9a2  multiset=14dfaae3fdc9
k_memcpy_sum  insns=40  ordered=a94d52a36dda  multiset=14dfaae3fdc9
  ordered !=  multiset ==   <- SAME INSTRUCTION MULTISET, DIFFERENT ORDER
```

The complete normalised difference is the placement of one `xor %esi,%esi`. **Two
identical programs, differently scheduled, report `!=`** — the direction the
catalogue's own block calls dangerous, because *"probe 2 saying 'these differ' is
what KEEPS a row alive"*.

⚠ **And the signal that would have caught it was present and was removed twice.**
`.temp/t94/knorm.py:79-82` computes and prints a **mnemonic-multiset** column
alongside the normalised text. `.temp/t102/b4_norm.py` dropped it. `.temp/t104/probe2.py`
dropped it. Each successive repair deleted the one column that distinguishes
*"different program"* from *"same program, rescheduled"*. The catalogue already
records the phenomenon without naming it as a probe-2 defect — its p16 note says
the shipped pair is *"23 instructions on each side, the same multiset, a
different order"*. Fix: print both and report them separately;
`.temp/r113/normcmp.py` does it in 25 lines.

### A8 — the sentence that survives

Both halves fail, so replace it rather than weaken it. What the evidence
supports, one-directionally and with the term defined:

> **A NONZERO, ATTRIBUTABLE safety tax appears in this benchmark only where some
> rung emits the property as machine work another rung omits — usually a
> compare-and-branch, sometimes a divide (`p06`), sometimes a load the aliasing
> rule forces (`p38`, `6.00 Ir`/call). Where the property is enforced at compile
> time, the tax is `0.00` by construction — and that is a publishable result, not
> a failure: `p08`, `p22` and `p27` each shipped on it.** ⚠ **The converse does
> not hold. A compare-and-branch boundary is not sufficient for a row, and the
> criteria that actually decide are the ones finding 37 omits: does the harm
> matrix have more than one column, does the C rung exhibit the bug without a
> flag, and is the measured gap attributable to safety rather than to the
> allocator, to libc or to dispatch representation.**

---

## §B — the debt is smaller than it looks. **Three tasks, not fifteen.**

⚠ **First, the count is wrong. There are fifteen unreviewed tasks, not fourteen**
— `TASK_113.md` omits `TASK_098`, which `RECAP.md:12` and `SYNTHESIS.md` §7 both
list.

Dependency weight, counted rather than guessed (`grep -c` over each artefact):

| task | RECAP | SYNTH | `.memory/` | `patterns/` | `harness/` |
|---|---|---|---|---|---|
| 100 | 11 | 4 | 10 | 0 | 0 |
| 092 | 8 | 1 | 5 | 24 | 2 |
| 090 | 6 | 0 | 5 | 0 | 0 |
| 088 | 5 | 1 | 5 | 4 | 8 |
| 102 | 4 | 2 | 3 | 0 | 3 |
| 109 | 3 | 3 | 2 | 38 | 0 |
| 106 | 2 | 0 | 7 | 18 | 0 |
| 097 | 2 | 0 | 4 | 6 | 6 |
| 111 | 2 | 3 | 0 | 0 | 0 |
| 110 | 1 | 1 | 1 | **65** | 0 |
| 098 | 1 | 1 | 4 | 0 | 9 |
| 091 | 1 | 0 | 4 | 0 | 0 |
| 112 | 1 | 2 | 0 | 0 | 0 |
| 107 | 0 | 0 | 5 | 0 | **19** |
| 095 | 0 | 0 | 4 | 0 | 0 |

### Worth a task each — three, in this order

**1. `TASK_107` — the instrument. ⚠ This is my argument against the manager's
least-sure call #2.** The manager chose the plan over the instrument and was
right *for the first review* — attacking `TASK_102` paid, above. But `107` should
be **next**, ahead of `100` and `111/112`. Its three results are now **rules**,
embedded in `harness/` (19 citations) and `.memory/03`, and a wrong rule
mis-measures silently and forward, where a wrong plan only forgoes rows you can
re-open at any time. Concretely: *"`MIRIFLAGS` presence costs 4.6×"* is why the
gate pins **no** Miri seed, `TASK_102`'s own correction says an alignment row
would then be *"a coin flip"*, and that caveat is now **shipped published text**
inside `patterns/p42-goto-cleanup/spec.md:336`. A single unreviewed measurement
is load-bearing for a caveat in a pattern's pinned contract.

**2. `TASK_110` — the only unreviewed task that shipped NEW MEASURED CELLS into a
published pattern**, and it landed the corrections of an unreviewed review
(`109`). Fold `109` into it; reviewing the landing covers the review's substance.
⚠ **Do not aim the review at the number** — I checked it and it reproduces
exactly from the committed record:

```
p42, -O3 isolated, kernel-exclusive Ir/call:
  safe_tuned  small 1263.00  large 50745.00
  unsafe      small 1251.00  large 50734.00      R3 - R4 = +12.00 / +11.00
  verus       small 1251.00  large 50734.00      unsafe == verus to the unit
                                     (TASK_110 claims +12.00 / +11.00 — exact)
```

Aim it at the **ghost-ledger R5**, which is a proof encoding nobody has attacked:
`TASK_109` established that `Tracked<Dealloc>` is **affine, not linear** — a proof
may simply drop it — and `110`'s escrow encoding is the fix for that, unreviewed,
carrying `verus.obligations 15 → 18` and a `contract_sha256` move. `p42` is
already the first pattern whose R5 did not cover its own bug class; the claim
that it now does is exactly the kind this project keeps finding defects in.

**3. `TASK_106` — cheapest of the three, and explicitly owed.** `RECAP` finding 38
carries *"PROVISIONAL where it rests on `TASK_106`, which is unreviewed"*, and
finding 38 is a published headline (`3.11×`). The commit log records the manager
writing a wrong sign into `.memory/` from that report (`d9a0b3e`,
*"it caught me writing a wrong sign into .memory/ from a report"*), so the
handoff is known-defective at least once.

### Superseded or self-checking — nine of the fifteen. **Close them.**

- **`TASK_090`** — **superseded**. Its headline (`≈7.9 Ir`/element for `p24`) was
  **retracted at `TASK_092`** and the catalogue carries the replacement measured
  at shipped shape (`ship_safe` and `ship_unsafe` **byte-identical**,
  `md5_fn 3d37ca7b…`). What survives ships its own vacuity control (the 8th
  mutant).
- **`TASK_091`** — **superseded by `p28`'s refusal.** `wf`-establishability is a
  dead-row detail: 1 RECAP citation, 0 in `patterns/`, 0 in `SYNTHESIS.md`.
- **`TASK_095`** — **nothing rests on it.** 0 RECAP, 0 SYNTH, 0 `patterns/`.
  `p29` is refused.
- **`TASK_088` / `TASK_092`** — both are *corrections-landing* tasks for patterns
  (`p19`, `p46`) that **already had a review**; the reviewed content is the
  reviewer's. `092` is additionally the task that corrected `090` **and**
  PROTOCOL rule 6's budget table, both manager-verified.
- **`TASK_097`** — harness item, covered in practice: the tree is green and
  `--check-stale` reports **52 records, 0 STALE** after `TASK_104`'s and
  `TASK_107`'s full-gate runs.
- **`TASK_098`** — a review report; reviewing a review, and its subject (the ±7
  blast radius) is re-exercised by every FRESH record.
- **`TASK_100`** — a review report, and I re-ran the arm that `SYNTHESIS.md` §5
  cites. **It reproduces exactly** (`EVIDENCE.log` §C2): `v37_callback` →
  *"does not yet support … function pointer types"* on both sites; `v37_sub` →
  `4 verified, 0 errors`; `v37_sub2` → `3 verified, 0 errors`; `v37_sub2_mut`
  (the anti-vacuity control) → `2 verified, 1 errors`, *"precondition not
  satisfied"*. **Close it by re-running the `p34` leak arm — one command against
  `.temp/r100/b/p34_leak.rs` — not by spending a task.**
- **`TASK_111` / `TASK_112`** — reviewing a review, twice; not worth it, and I
  checked the landing instead of asserting it. **All nine restored results are
  present in `SYNTHESIS.md`**: *"seven of eight"* (2 hits), *"sawtooth"* (2),
  *"next_pow2"* (2), *"both ends"* (1), *"3.00000"* (5), and the
  R4-chained-to-the-prover constraint at lines **54, 58, 185**. `112` verifies.

**So: three tasks, and `109` folds into `110`. The debt is an accounting artefact
of a fast session, with three real items in it.**

---

## §C — `p37`, stated precisely

**Status, exactly.** `p37` is **not** a refusal with a standing reason. Its first
limb reproduces (Verus at the pin rejects `fn` pointer types); its second limb
was an argument with nothing run and is measurably false (re-run above, four
files, exact reproduction). `TASK_100` did **not** overturn the verdict — it
established that the verdict has **no surviving justification**. Nobody has
re-triaged it since.

**Is `SYNTHESIS.md` §5's *"15 rows are refused, each on a measurement"* honest
with `p37` in it? No — and the number is not reconstructible from the
catalogue.** The catalogue's 48 rows decompose as:

```
26 built  +  6 `planned` (p20 p21 p25 p26 p40 p41)
        +  p24  PROBED, not refused — "needs a new reason to be built"
        +  p35  BLOCKED by check.py::_scan_unsafe_sites, NOT refused,
                and its scheduling premise is recorded REFUTED
        +  p37  REFUSED-REASON-REFUTED
        + 13 refused with a standing reason              = 48
```

Fifteen requires either `13 + p35 + p37`, or `13 + p40 + p41` — and `p40`/`p41`
still read **`planned`** in the catalogue while `RECAP.md:13` says they were
*"adjudicated REFUSE at `TASK_086` with measurements that **never reached the
catalogue**"*. **Under every membership, "each on a measurement" fails**:
`p37`'s measurement refuted its reason, `p35` is blocked by a gate rule rather
than a measurement, and `p40`/`p41`'s measurements are not in the record they
would have to be checked against. Also note `p32`+`p33` are **one row** by the
catalogue's own text and count as two.

**A measured re-triage, so the row does not stay open.** I built the cheapest
decisive probe — where is the rung boundary in a callback ladder?
(`.temp/r113/p37_probe.rs`; safe `Box<dyn Op>` with typed userdata, unsafe raw
`extern "C"` fn pointer with `*mut c_void` userdata, plus a third **isolation**
rung: raw fn pointer with the bounds check kept.)

```
k_safe            insns=42  ordered=dd6c4dc74687     (dyn, checked)
k_unsafe_checked  insns=42  ordered=f7667751ecfa     (raw fn ptr, checked)   <- isolation
k_unsafe          insns=39  ordered=1a53de1bca3d     (raw fn ptr, unchecked)
all three print 16336633730550651637
```

The isolation decomposes the gap exactly:

- `k_unsafe_checked − k_unsafe` = **+3** — `cmp %rbp,(%rsp)` / `je <panic>` plus
  the panic block. This is `tab[sel]`, an **`index >= len` on the dispatch
  table**. `p16`'s check in `p16`'s place.
- `k_safe − k_unsafe_checked` = **0 net static instructions** — the fat-pointer
  stride and vtable load (`shl $0x4`; `mov 0x8(%r12,%rcx,1),%rcx`;
  `call *0x18(%rcx)`) against the thin one (`shl $0x3`;
  `call *0x0(%r13,%rcx,1)`). Dispatch **representation**, not safety, and it
  needs a dynamic `Ir` run to price properly — I did not do that.
- **The type confusion contributes nothing.** Both rungs reach the userdata with
  a plain `mov` and dispatch with `call *reg`. There is no compare, no branch and
  no rung boundary anywhere near the property the row is named for.

> **`p37` should be REFUSED, on a new and measured reason: the only thing a `p37`
> ladder measures is the dispatch table's `index >= len` — `p16` verbatim, the
> duplication `p43` was already refused for — while the property the row exists
> to price is enforced by the type system and is `0.00` by construction.** ⚠ **It
> is `p08`'s shape, and the catalogue's own open question (*"does a
> `PointsTo<u64>` R5 make the confusion UNREPRESENTABLE rather than CHECKED?"*)
> answers YES on the exec side.** ⚠ **Scope: probe-2 and static counts on a
> probe-shape kernel, no C rung, no harm matrix, no gate. It is a REFUSE
> recommendation with its reason measured, not a verdict through a gate** — which
> is what the row has been missing since `TASK_100`.

---

## Clean negatives — named attacks that did NOT land

Per PROTOCOL rule 6, so nobody re-runs them.

1. **The three probe-2 kills all survive `.temp/t104/probe2.py`.** B4
   (`22 == 22`, `7c10d0059428`), C2-gcc (`19 == 19`, `b61faafb9e30` at `-O2`,
   `42a9c292829a` at `-O3`), B3 (`k_safe_naive == k_safe_tuned == k_unsafe`,
   19 insns, `924b1bafd753`, and `!= k_hardened`). **No refused row comes back.**
   I also confirmed the ICF mechanism directly: `nm` shows `g_tuned` and
   `g_unsafe` do not exist, and `k_unsafe+0x27` is
   `call 14c80 <…7g_naive>`.
2. **`unchecked_div` really is absent at the pin.** rustc 1.97.1 →
   `error[E0599]: no method named 'unchecked_div' found for type 'u32'`, while
   `unchecked_add` in the same file compiles.
3. **`TASK_100`'s `p37` Verus evidence reproduces exactly**, including the
   anti-vacuity control.
4. **`TASK_110`'s headline reproduces exactly from the committed record** —
   `R3 − R4 = +12.00 / +11.00`, `unsafe ≡ verus` to the unit.
5. **`TASK_112`'s restoration verifies** — all nine dropped results present.
6. **`harness/measure.py --check-stale`: 52 records examined, 0 STALE.**
7. **C3's second refusal reason stands.** I attacked the behaviour matrix and did
   not move it; C3 remains REFUSED.
8. **I did not find a `/tmp` write, a stale citation, or a `contract_sha256`
   mismatch anywhere I looked.**

---

## What I did NOT do, and what I am unsure about

- **I ran no `check.py`, `build.py` or `measure.py`** (other than
  `--check-stale`), created no pattern directory, and edited nothing outside
  `.temp/r113/` and this report.
- **No number here is gate-grade.** Every probe-2 result is byte-level normalised
  disassembly; the `+3` and `+0` in §C are **static** instruction counts on a
  probe-shape kernel. Per `TASK_102`'s own caution and `p46`'s sign lesson, a
  probe can be wrong in sign; every claim above rests on identity or on a
  reviewed record, never on a probe-3 number.
- **§A1 rests on `p38`'s `NOTES.md` table, not on a re-run.** I read the
  committed numbers; I did not re-measure p38. If the manager wants that
  hardened, `results/p38-alias-pun.json` is FRESH and the controls are shipped.
- **I did not price `p37`'s fat-pointer term dynamically.** "0 net static
  instructions" is not "0 `Ir`"; a `dyn` call can cost more at run time than its
  instruction count suggests.
- **`p06` is a *mispredicts-the-mechanism* counterexample, not a
  *falsifies-the-antecedent* one.** Its hardened rung does contain a compare.
  I have flagged it as such rather than counting it with `p38`.
- **I did not review `TASK_107`, `110` or `106`** — that is the recommendation,
  not the work. **§B's rankings are argued from citation counts and from what a
  defect would cost, not from having read those tasks' evidence.**
- **`RECAP` finding 37's companion rule (`p23`, isolation-owed) is untouched by
  all of this** — it is a separate, later result and I found nothing against it.
  Indeed my `p37` isolation is that rule being applied.

## Corrections owed to the authoritative layer (manager to apply)

1. ⚠⚠ **`RECAP` finding 37 and `SYNTHESIS.md` §5: the "iff" must go.** Both
   halves fail (§A1, §A2). §A8 has a replacement sentence. **Do not strike —
   annotate as DISPUTED with the evidence on both sides, per PROTOCOL rule 9.**
2. **`SYNTHESIS.md` §5: *"15 rows are refused, each on a measurement"* is not
   reconstructible and is wrong under both memberships** (§C). The honest figure
   is **13 refused with a standing reason**, plus `p35` (blocked, not refused),
   `p37` (reason refuted), and `p40`/`p41` whose adjudication never reached the
   catalogue.
3. **`.memory/06-catalogue.md` probe-2 block: a FIFTH defect** — a pure
   instruction-scheduling permutation reports `!=`; the multiset column that
   catches it was in `knorm.py` and was dropped by **both** successor tools.
   `.temp/r113/normcmp.py` restores it.
4. **`.memory/06-catalogue.md` `p37`: re-triage settled — REFUSE, on the measured
   reason in §C**, replacing the reason `TASK_100` refuted.
5. **`.memory/06-catalogue.md` `p40`/`p41` say `planned` while `RECAP.md:13` says
   REFUSE.** One of the two is wrong; the measurements are cited as missing.
6. **`TASK_102`'s C3 R4 reason (*"an annotation, not an operation"*) is refuted**
   — the two levers are normalised-identical (§A6). C3's verdict stands on its
   other reason.
7. **Verus at the pin carries a division-by-zero obligation** (`error: possible
   division by zero`), and **`p06` already ships a division-by-zero guard** —
   worth a line beside the `unchecked_div` entry, because together they close any
   future arithmetic row's "novel obligation" argument.
8. ⚠ **`RECAP.md:12`'s "Do NOT start a 27th pattern" is now justified by a
   finding that does not stand.** The *decision* may still be right — the
   synthesis is the higher-value work — but it needs a different reason, and
   `p24` (*"needs a new reason to be built"*) and `p37` are the two rows a reader
   will point at.
9. **`TASK_113.md` says fourteen unreviewed tasks; there are fifteen** (`098`).

**Refutations this task produced: 11**, itemised — (1) finding 37's only-if half,
`p38` at `6.00 Ir`; (2) its if half, C3 and B2 satisfying the antecedent and
refused; (3) the criterion is non-diagnostic — `p37`'s boundary is the wrong
property, `p06`'s is 8.4% of the effect; (4) *"probe 2 says so every time"* — 3 of
8; (5) *"no machine-code footprint at all"* — false on clang and on B1; (6) the
refusal set is selected on the criterion the project says does not predict;
(7) C3's *"annotation, not an operation"*; (8) probe 2's fifth defect and the
twice-deleted multiset column; (9) *"15 rows refused, each on a measurement"*;
(10) `p40`/`p41` catalogue-vs-RECAP disagreement; (11) *"fourteen unreviewed"*.
**414 → 425.** ⚠ **Reconciliation is the manager's job; I was launched from 414
and have not attempted a global total across any concurrent task.**
