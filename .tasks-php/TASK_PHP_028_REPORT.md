# TASK_PHP_028 — report

**Role:** research engineer, alone. **Rows dispatched: three (`ph03`, `ph16`,
`ph29`). Rows completed: ONE — `ph16-fdset-index`.** `ph03` and `ph29` are
untouched and need their own task; §6 says why, and §5.1 says why the reason
given for `ph03` in the task file is not the real one.

**Brackets.** `harness/measure.py --check-stale` → **66 / 0** and
`harness-php/gate.py --tool measure --check-stale` → **10 / 0**, first (before
anything was touched) and last. ⭐ **No measurement record moved**:
`spellings.py`, `NOTES.md` and `README.md` are none of them in `measure.py`'s
19 pinned sources, so this task cost **ONE gate round on `ph16`, green first
try, and no re-measure and no re-render.** `results-php/gate/ph16-fdset-index.json`
is `verdict: PASS`, `failures: []`, `complete_run: true`, and stage 9c reports
the published table **byte-identical to a fresh render** — because
`controls_json` went to `{"spellings.json": "FRESH"}` and `report.py` renders a
line only for a *non*-`FRESH` entry, so the table did not move.

⚠⚠ **THE TREE WAS NOT MINE ALONE, AND THE BRIEF SAID IT WOULD BE.** At the
start of the session `git status` showed ` M .tasks-php/TASK_PHP_028.md` with
HEAD at `8c96021`; HEAD is now `a87d3e9` *"Dispatch _028 and _031"*, and
`.tasks-php/TASK_PHP_031_REPORT.md` — **not mine** — appeared untracked while I
was working. So the manager committed during my run and `TASK_PHP_031` ran
alongside me. **Both brackets agreed at both ends, which is the agreed detector,
and `TASK_PHP_031` is a survey task that touches no `phNN` row, so I did not
stop** — but the *"one agent works at a time"* assumption in the brief did not
hold and the next task should not assume it did. Also present at dispatch and still present,
**not mine**: the untracked short-name preflight records
`results-php/preflight/ph07.preflight.json` and `ph29.preflight.json` (open item
42 / F55). ⭐ **I used the full row name throughout, so my gate run updated
`ph16-fdset-index.preflight.json` and added no second short-name file.**

**What landed**

| | |
|---|---|
| `patterns-php/ph16-fdset-index/controls/spellings.py` | **NEW.** The second `controls/spellings.py` in `patterns-php/`, cloned from `ph07`'s. 17 variants. |
| `patterns-php/ph16-fdset-index/controls/spellings.json` | its sidecar, `problems: []`, `verus_checked: true`, `attributed: true`, `reproduces_shipped_record: true` |
| `patterns-php/ph16-fdset-index/NOTES.md` | **§8e** (the result), **§8b-RETRACTED** (see §5.2), §8c and §11 rewritten |
| `patterns-php/ph16-fdset-index/README.md` | the "no figure here is a `fixed-R4 bound`" pointer replaced |
| `.temp/php28/negatives_spellings.py` | **the §H validator attack — 54 cases (36 must-FIRE, 18 must-NOT-fire), 0 failed; 9 of them drive the whole pipeline over a mutated configuration** |
| `.temp/php28/probe_exec.py` | the exec-only pricing probe that kept four losing candidates from costing Verus time |
| `.temp/php28/asm/remake.py` | rebuilds the deleted `asm/` blobs — **and finding a defect was a side effect of writing it**, §4.1 defect 3 |
| `.temp/php28/NOTES.md` | the scratch index |

**Not touched:** `spec.md` (no `spec.md` edit was needed — the hashed block and
its `contract_sha256` are unchanged), any rung `.rs`, `harness/`, `common/`,
`patterns/`, `results/`, `pilot/`, `.web/`, `RECAP_PHP.md`, `.memory-php/`,
`ph07/`. No `git add`, no `git commit`.

---

## §1 THE TWO NUMBERS, LABELLED — `ph16-fdset-index`

⚠ **Three statistics are in circulation on this row and they do not agree to the
digit, so all three ship.** `.memory-php/02-ladder.md` quotes `ph07`'s discharge
as `+11.98 %`, which is the **marginal** figure (`Ir` per window byte, the slope
through the two probe points). `TASK_PHP_028.md`'s own table quotes `ph16` at
`-1.22 %`, which is the **`small.bin` per-call** figure, i.e. the published
table's own ratio. On `ph07` the two agree to 0.6 pp and nobody had to choose.
See §5.4.

| | `small.bin`/call | `large.bin`/call | Ir/window byte |
|---|---:|---:|---:|
| **`fixed-R4 bound`** — `R3ship − R4ship`, both held by fiat | **−1.22 %** | **−1.84 %** | **−1.94 %** |
| **cheapest-found in-contract** — `inf(R3 found) − R4ship`; spelling **`r3_split_at`**, inputs **`small.bin` + `large.bin`** | **−1.42 %** | **−1.87 %** | **−1.94 %** |

**AND NO PAIR INTERVAL.** `min(R3 found) − min(R4 found)` is not computed, not
printed and not in the sidecar.

**NO RUNG IS RE-SHIPPED.** `safe_tuned.rs` and `unsafe.rs` are byte-identical to
what they were at dispatch. `r3_split_at` moves the *published bound* and ships
as a control, per `.memory/02-bench-rules.md`.

⚠ **`r3_split_at`'s win is entirely in the FIXED term** — 138.3 → 131.3 Ir/call,
i.e. **−7.0 Ir/call** — and the marginal is 6.2121 vs 6.2122, a difference of
**0.0016 %**, forty times under `TIE_PCT`. **So on the marginal statistic the R3
endpoint is degenerate too.** The bound moves on the per-call statistic and not
on the slope. Both are stated above rather than the flattering one.

### 1.1 ⭐ The R4 side was searched and it is DEGENERATE

Four independent respellings of the index the mechanism blames (§2), plus the
fold:

| variant | slope vs R4ship | `kernel` | twin | verdict |
|---|---:|---|---|---|
| `v0_shipped` | +0.000 % | 426 insn `9148de644fa1` | 15/0 | SHIPPED |
| `r4_hoistbase` — `let b = 6+2*base;`, `j = b+2*i` | +0.000 % | **the same 426 insn `9148de644fa1`** | **14/1 — FAILS** | **INADMISSIBLE** |
| `r4_fold_index` — `s[i]` for `aget_unchecked(s, i)` | +0.000 % | **the same 426 insn `9148de644fa1`** | 15/0 | **TIE, and one fewer trusted-item use** |
| `r4x_subslice` — the arm as a SUBSLICE, i.e. R3's own spelling | **+1.798 %** | 484 insn | exec-only | dearer |
| `r4_cursor` — cursor `j` beside `i` | **+3.743 %** | 455 insn | 15/0 | dearer |
| `r4_cursor_fold` | +3.743 % | 455 insn | 15/0 | dearer |
| `r4x_endcursor` — cursor with `i` deleted, bounded by `end` | **+4.344 %** | 446 insn | exec-only | dearer |

**Nothing cheaper than a tie.** `ph16` is the **13th of 21** rows where an
R4-side search found nothing, which is the tally `.memory-php/02-ladder.md`
carries at 12 of 20 for `ph07`.

⭐ **`r4_fold_index` is the third kind of result the bench rule has no name
for**, and it is `ph07`'s `r4_index0` reproduced exactly: **byte-identical
machine code**, verifies 15/0, and it **removes one of two uses of
`aget_unchecked`** — a smaller trusted surface at the same price. Neither a
cheaper spelling nor a re-ship.

⚠ **`r4_hoistbase` is a shape I have not seen recorded**: a respelling that is
**byte-identical machine code** to the shipped rung — so `identity: unsafe ==
verus, O3 exact` would have held — **and whose Verus twin does not verify** (the
solver loses `b == 6 + 2*base` across the loop head; the invariant it needs is
the one `r4_cursor` carries, and `r4_cursor` costs +3.7 %). *The prover, not the
compiler, is what refuses it.* On this row the R4 side is chained to the prover
in a way that costs nothing at all in machine code.

### 1.2 The R3 side, all eight

| variant | `small.bin`/call | slope vs R4ship | `kernel` |
|---|---:|---:|---|
| `r3_split_at` — three range slicings → one `split_at` pair | **3548.0** | −1.94 % | 458 insn |
| `r3_prologue` — `r3_split_at` + `r3_head_array` | 3548.0 | −1.94 % | 458 insn (they do **not** compose) |
| `v0_shipped` | 3555.0 | −1.94 % | 487 insn `d0091b202786` |
| `r3_head_array` — six header reads behind one `&win[0..6]` | 3555.0 | −1.94 % | 487 insn, **different code, identical cost** |
| `r3_u16` — `u16::from_le_bytes([c[0], c[1]])` | 3555.0 | −1.94 % | **byte-identical** |
| `r3_guard_r2` — R2's guard spelling (see §5.2) | 3555.0 | −1.94 % | **byte-identical** |
| `r3_index_walk` — subslice kept, walked by index | 3820.2 | +6.29 % | 470 insn |
| `r3_absindex` — R4's `(win, base, n)` signature | 4730.8 | +34.12 % | **byte-identical to `safe_naive.rs`** |

---

## §2 THE MECHANISM, EXACT, AND WHY IT IS THE ANSWER TO §4.1

`spellings.py --attribute` runs callgrind with `--dump-instr=yes` on both shipped
rungs and decomposes `R4ship − R3ship` **by execution-count class** — exact, not
thresholded, because the two rungs run the same control flow on the same data,
so a block's execution count identifies it in both binaries.

```
R4 CHEAPER off the entry loops   -450 686 Ir   -18.0 /call
    R3's four range-slicings and its header index reads carry bounds tests that
    R4's get_unchecked does not.  THIS IS THE SAFETY SAVING AND IT IS THE ONLY
    PLACE R4 IS AHEAD.
R4 DEARER in ARM 2's entry loop +1 550 414 Ir  +62.0 /call
    ONE extra `lea (%rsi,%rdx,1),%rcx` per entry.  6 insns become 7:
      R3: add $0x2,%r12 | add $-2,%rdx | je | movzbl 0x1(%r12),%edi | test | jns
      R4: inc %rdx | cmp %r8,%rdx | jae | lea (%rsi,%rdx,1),%rcx
          | movzbl 0x7(%r14,%rcx,2),%r10d | test | jns
    `to_fd_set(win, base, n)` indexes `win` ABSOLUTELY and LLVM could not fold
    the runtime `base` into the addressing mode in ONE of three inlined copies:
    arm 1 has base == 0, arm 3 is strength-reduced to a pointer, arm 2 is not.
------------------------------------------------------------------------------
net                             +1 099 728 Ir  +44.0 /call
  = 89 974 452 - 88 874 724, EXACTLY the unsafe minus safe_tuned cell of
    results-php/ph16-fdset-index.json.
```

### 2.1 ⭐⭐⭐ THE ANSWER TO §4.1, FOR `ph16`: IT IS A RESULT, NOT A SPELLING ARTEFACT

**I predicted the opposite and the measurement refuted me.** The mechanism above
made me expect the `lea` to be removable, the R4 side to move, and the sign to
flip. It does not:

* every respelling of that index is **dearer or byte-identical** (§1.1) —
  including `r4x_subslice`, which is **R3's own spelling**, at +1.80 %;
* and the **mirror control** is what turns this from a complaint about R4 into a
  statement about the ladder. **`r3_absindex` — R3 given R4's signature — is
  byte-identical machine code to `safe_naive.rs`** and measures **+33.07 %**
  against the shipped R3. So:

| | subslice signature | absolute-index signature |
|---|---:|---:|
| in the **safe** rung | **3555.0** | 4730.8 (`= safe_naive`) |
| in the **unsafe** rung | 3664.2 | **3599.0** |

**The subslice is worth −24.9 % in safe Rust and +1.8 % in unsafe Rust.** It
hoists a bounds test out of the loop where there is one to hoist, and buys a
pointer-plus-length where there is not. **The two rungs' cheapest spellings are
different spellings, and R3's minimum (3555.0) sits below R4's minimum
(3599.0).** That is a non-monotone ladder **with both endpoints searched**, and
it is a mechanism and not an accident.

⚠⚠ **n = 1 row, and the manager's instruction stands: do NOT report this as an
effect.** `ph29`'s negative spread has **not** been searched and this task says
nothing about it. What is now established is one row, and what it establishes is
that on *that* row the negative sign is not an unsearched-endpoint artefact. The
honest headline is:

> **On `ph16`, safe-tuned Rust is cheaper than every admissible unsafe spelling
> found — 17 variants in all: 8 R3 spellings (the shipped one and 7
> respellings), 5 R4 spellings each with a Verus twin, 2 exec-only R4 controls
> and 2 exec-only R2 controls — and the mechanism is that the two rungs are
> cheapest under DIFFERENT spellings of the same loop.**

---

## §3 HOW THE CANDIDATE SET WAS CHOSEN, AND HOW I WOULD KNOW IF IT WERE TOO NARROW

The manager named this as the thing the report would be read for hardest, so it
is answered mechanically rather than with an assurance.

**How they were chosen: from the instruction attribution, not from intuition.**
The order of work was (1) build the two shipped rungs, (2) callgrind them with
`--dump-instr=yes`, (3) attribute the difference per machine instruction, (4)
*then* write candidates, one per term the attribution says costs something.
`r4_cursor` / `r4_hoistbase` / `r4x_endcursor` / `r4x_subslice` all target the
`+1 550 414` term; `r3_split_at` / `r3_head_array` / `r3_prologue` all target the
`−450 686` term. **No candidate in the file was written before the attribution
existed, and no term in the attribution is without a candidate.**

**How I would know the set were too narrow — four independent answers, three of
them mechanical:**

1. ⭐ **The decomposition would not close.** It sums to the measured net
   difference **exactly** (`+1 099 728`, `CLOSES`), and `spellings.py` appends a
   `problems` entry — which fails the gate — if it ever stops closing. A term
   nobody wrote a candidate for cannot hide: it would appear as a class with a
   non-zero delta and no variant aimed at it. There is no residue.
2. **The parser could be lying about the decomposition.** It cannot silently:
   the per-instruction sum is asserted equal to `callgrind_annotate`'s figure —
   *`measure.py`'s own statistic, imported* — for both rungs, and it is
   (`AGREE`, twice, to the digit).
3. ⚠ **The set contains LOSERS on two axes and they are the calibration.**
   `r3_index_walk` (+6.29 %), `r3_absindex` (+34.12 %), `r4_cursor` (+3.74 %)
   and `r4x_endcursor` (+4.34 %) all move, and move in the direction the
   mechanism predicts. **A search where nothing moves is a search whose
   substitutions did not apply**; four movers is evidence the machinery is live.
   Three variants also came back **byte-identical** and one came back
   **different code at identical cost**, which are two more distinguishable
   outcomes the set produced.
4. **The residual, named rather than left implicit.** The set does *not* contain
   any R4 candidate that would need a **new trusted item** or a **rewrite of
   `walk`'s spec functions** — `spec.md`'s `verus.items` pins those, and a
   candidate that grows the TCB is `p16`'s `r4_hdr` precedent for
   inadmissibility, not a rung. **`r4x_subslice` is the closest such candidate
   and it was priced anyway, exec-only: it is DEARER, so no amount of proof work
   could have moved the bound with it.** That is the honest limit of the search
   and it is arithmetic rather than charitable — a candidate dearer than
   `R4ship` cannot move a quantity whose denominator is `R4ship`.

**What would still change the answer, and I am not claiming otherwise**: an R4
spelling nobody has thought of that removes arm 2's `lea` *without* paying for a
slice. Four attempts did not find one; a fifth might. That is what
"cheapest-**found**" means and it is why the label ships with the number.

---

## §4 §H — THE MUST-FIRE NEGATIVES, RUN, WITH OUTPUT

`.temp/php28/negatives_spellings.py`. **`spellings.py` is a validator and the
gate hashes `controls/*.py` and never RUNS them**, so this file is the only
thing between it and a silent wrong number. 8 groups, **54 cases (36 must-FIRE,
18 must-NOT-fire), 0 failed** — 45 without `--e2e`, which adds 9. ⚠ **Run
`spellings.py` and `.temp/php28/asm/remake.py` first**: groups D5 and G read the
variant binaries and the real callgrind dump, and without them they SKIP and the
fast suite reports **34**. A suite whose case count depends on what is on disk
says so rather than quietly shrinking.

⚠ **The block below is the FINAL run**, i.e. after all four defects in §4.1
were fixed; group D's `cfn=` case did not exist in the runs that preceded it.

```
MUST-FIRE NEGATIVES for patterns-php/ph16-fdset-index/controls/spellings.py
  PROTOCOL_PHP.md §H -- the gate hashes controls/*.py and never RUNS them.

A. THE SPELLING AUDIT (`audit`)
  PASS  must-FIRE     forbidden `volatile`       expect=True                         got=True   1 hit(s)
  PASS  must-FIRE     forbidden `& 1023`         expect=True                         got=True   1 hit(s)
  PASS  must-FIRE     forbidden `% FD_SETSIZE`   expect=True                         got=True   1 hit(s)
  PASS  must-FIRE     forbidden `[0u64; 32]`     expect=True                         got=True   1 hit(s)
  PASS  must-FIRE     forbidden `forbidden`      expect=True                         got=True   1 hit(s)
  PASS  must-NOT-fire same tokens in a COMMENT   expect=[]                           got=[]   exec_code blanks comments -- a real hole, check.py's rule
  PASS  must-NOT-fire required miss not fatal    expect=(True, True)                 got=(True, True)   4 absent, 0 forbidden
  PASS  must-NOT-fire shipped R3 in contract     expect=(True, 2)                    got=(True, 2)
  PASS  must-FIRE     audit witnesses the swap   expect=(True, True)                 got=(True, True)   misses `w < NW` and now satisfies `this_fd < FD_SETSIZE`

B. THE SUBSTITUTION ENGINE (`apply_subs`)
  PASS  must-FIRE     old string absent          expect=True                         got=True   the shipped rung moved under a variant
  PASS  must-FIRE     hit count too high         expect=True                         got=True   the substitution matches once, the variant claims twice
  PASS  must-FIRE     hit count too low          expect=True                         got=True   the substitution matches many times, the variant claims one
  PASS  must-NOT-fire all 17 lists apply         expect=[]                           got=[]

C. THE VERDICTS (`cheapest_in_contract`, `cheaper_than_shipped`)
  PASS  must-FIRE     out-of-contract cheaper R3 expect='v0_shipped'                 got='v0_shipped'
  PASS  must-FIRE     unpriced R3 candidate      expect='v0_shipped'                 got='v0_shipped'
  PASS  must-FIRE     R4x cannot be cheapest     expect=None                         got=None
  PASS  must-FIRE     R2x cannot be cheapest     expect=None                         got=None
  PASS  must-NOT-fire cheaper in-contract R3 wins expect='nx_good'                    got='nx_good'
  PASS  must-FIRE     sub-TIE_PCT is a tie       expect=[]                           got=[]   -0.01% against TIE_PCT=0.05%
  PASS  must-NOT-fire 1% cheaper R4 is reported  expect=['nx_win']                   got=['nx_win']
  PASS  must-FIRE     out-of-contract cheaper R4 expect=[]                           got=[]
  PASS  must-FIRE     no R4 baseline             expect=[]                           got=[]

D. THE CALLGRIND PARSER (`per_instruction`)
  PASS  must-FIRE     name compression           expect=1000                         got=1000   a literal-string parser gives 300 (the first block only)
  PASS  must-NOT-fire   and not the sibling      expect=False                        got=False
  PASS  must-FIRE     cfn= introduces the name   expect=300                          got=300   an fn=-only name table gives 0 for the hot function
  PASS  must-NOT-fire   and main is not counted  expect=False                        got=False
  PASS  must-FIRE     calls= is inclusive        expect=300                          got=300   counting it gives 5 000 300
  PASS  must-FIRE     relative subpositions      expect={4096: 50, 4100: 50}         got={4096: 50, 4100: 50}   a literal parser reports addresses 4 and 8
  PASS  must-NOT-fire   total is still right     expect=100                          got=100
  PASS  must-FIRE     fl= naming kernel          expect=0                            got=0   a line-oriented `'kernel' in line` test gives 777
  PASS  must-NOT-fire real dump == the record    expect=88874724                     got=88874724   results-php/ph16-fdset-index.json safe_tuned/small.bin

E. THE STATISTIC (`harness/measure.py::_sum_rows`, IMPORTED)
  PASS  must-FIRE     split across two rows      expect=16000000                     got=16000000   first-match-and-break gives 10 000 000
  PASS  must-FIRE     sibling kernel_prologue    expect=9100000                      got=9100000   names=['demo::kernel']
  PASS  must-NOT-fire no kernel row -> None      expect=None                         got=None

F. THE MEASUREMENT WRAPPER (`kernel_ir`)
  PASS  must-FIRE     nonzero exit is an ERROR   expect=(None, True)                 got=(None, True)   callgrind exit 1 on neg.false: in
==3956268==
==3
  PASS  must-FIRE     no kernel symbol is an ERROR expect=(None, True)                 got=(None, True)   callgrind_annotate named no `kernel` function for

G. THE FINGERPRINT (`kernel_fingerprint`)
  PASS  must-NOT-fire layout shift ignored       expect=True                         got=True   crate names 1 vs 30 chars: (487, 'd0091b202786') / (487, 'd0091b202786')
  PASS  must-NOT-fire R3_r3_guard_r2 == its rung expect=True                         got=True   (487, 'd0091b202786')
  PASS  must-NOT-fire R3_r3_u16 == its rung      expect=True                         got=True   (487, 'd0091b202786')
  PASS  must-NOT-fire R2x_r2x_guard_r3 == its rung expect=True                         got=True   (483, '5950ba114532')
  PASS  must-NOT-fire R4_r4_hoistbase == its rung expect=True                         got=True   (426, '9148de644fa1')
  PASS  must-NOT-fire R4_r4_fold_index == its rung expect=True                         got=True   (426, '9148de644fa1')
  PASS  must-FIRE     R3_r3_head_array != its rung expect=True                         got=True   (487, '262806d8bde0') vs (487, 'd0091b202786')
  PASS  must-FIRE     R3_r3_split_at != its rung expect=True                         got=True   (458, '42884623e2ac') vs (487, 'd0091b202786')
  PASS  must-FIRE     operands are kept          expect=True                         got=True   an opcode-only digest would call these EQUAL

H. THE PIPELINE (--e2e; 3 variants, HERE redirected)
  PASS  must-FIRE     answer-changing variant    expect=True                         got=True   R3 nx_answer changes the answer on ['adversarial-redzone.bin', 'advers
  PASS  must-FIRE     doctored record            expect=True                         got=True   stage 3 compares against the record at run time
  PASS  must-FIRE     exit code follows problems expect=1                            got=1
  PASS  must-FIRE     mutant marked out of contract expect=False                        got=False
  PASS  must-FIRE     mutant not published       expect='v0_shipped'                 got='v0_shipped'
  PASS  must-FIRE     no --verus                 expect=True                         got=True   rc=1
  PASS  must-FIRE       and it is recorded       expect=False                        got=False
  PASS  must-FIRE       and the run exits 1      expect=1                            got=1
  PASS  must-NOT-fire clean subset run           expect=(0, [], True)                got=(0, [], True)
54 case(s): 36 must-FIRE, 18 must-NOT-fire; 0 FAILED
```

Full logs: `.temp/php28/negatives_fast.log`, `.temp/php28/negatives_e2e.log`
(the latter includes the three mutated pipeline runs' complete stage output).

### 4.1 ⚠⚠ THE NEGATIVES CAUGHT TWO REAL DEFECTS, AND ONE OF THEM HAD ALREADY BEEN PUBLISHED

This is the §H argument in miniature, so it is stated in full rather than
summarised.

**Defect 1 — `kernel_fingerprint` was LAYOUT-SENSITIVE.** Its first version
stripped everything after the first `<` in a disassembly line, which removes the
crate hash in `<_RNvCs…6kernel+0x1a0>`. But an **absolute jump target is printed
BEFORE that bracket**, and objdump's resolved `# 553b0` for a rip-relative
operand comes after the operand and after no bracket at all. So two builds of
**the same source** under crate names of different lengths fingerprinted
differently. Live symptom: `r2x_guard_r3` printed as *not* byte-identical to
`r2x_shipped` when **65 of its 483 lines differed and every one of them was an
address** — 51 jump targets and 14 resolved rip comments, every displacement
identical.

**Defect 2, which is the one that matters — THE FIRST DEFECT HAD ALREADY PUT A
WRONG CLAIM IN THE ARTEFACT.** On the strength of it, `spellings.py`'s docstring
and its `r4_fold_index` `why` both read *"NOT byte-identical, unlike `ph07`'s
`r4_index0`"*. With addresses normalised away, **`r4_fold_index` IS
byte-identical** — it is `ph07`'s result exactly, not a weaker cousin. A
validator with no negatives had already published a false comparison against
another row.

⚠ **`r4_hoistbase`'s "byte-identical" claim was on the same footing** and only
survived because its crate name happened to give the same layout.

**Both are fixed**; `kernel_fingerprint` now normalises control-transfer targets
to signed offsets and strips objdump's `#` comment, keeps operands and
displacements, and carries the failure in its docstring. **Group G's
`layout shift ignored` case is deliberately built with crate names of 1 and 30
characters** — an earlier draft used equal-length names and let the defect
through, which is itself worth recording: *a negative that does not vary the
thing it is testing is not a negative.*

**Defect 3 — `per_instruction` DID NOT LEARN NAMES FROM `cfn=` LINES, and this
one was found by a script written to regenerate a deleted blob.** `fn` and `cfn`
share callgrind's name-compression namespace, so a function whose name is
introduced as a **callee** (`cfn=(5004) R3::kernel`) is thereafter referred to as
a bare `fn=(5004)`. A parser that learns names from `fn=` alone never resolves
it and returns **ZERO** for the hot function.

⚠⚠ **The `ph16` dumps are not stable in this respect across builds.** The dump
taken while `spellings.py` was being written introduced `R3::kernel` on an `fn=`
line; the dump `.temp/php28/asm/remake.py` produced hours later, from the same
source and the same flags, introduced it on a `cfn=` line. **So the parser
worked on one dump and returned 0 on the other, and nothing about the row or the
statistic had changed.**

⭐ **It failed LOUDLY, and that is the whole design of stage 6.** The
per-instruction sum is asserted equal to `callgrind_annotate`'s figure, so the
run printed `*** DISAGREE`, appended a `problems` entry and exited non-zero —
*a stopped measurement, not a wrong number.* Probe rule 1, working. **Fixed**
(names are now recorded from both `fn=` and `cfn=`, `cur` is still set only by
`fn=`), with a must-fire negative (group D, `cfn= introduces the name`) built
from the exact shape of the real dump, and the sidecar and the negatives re-run
afterwards.

⚠ **This is the case for `--attribute` being in the shipped control rather than
in scratch.** Had the attribution lived only in `.temp/`, the row would carry a
mechanism nobody could re-derive, and this defect would have been found by
nobody — the attribution is *the* justification for the candidate set (§3), so a
version of it that cannot be re-run is a justification that cannot be checked.

**Defect 4, cosmetic but the same class.** Stage 5's degenerate-R4 message
hardcoded *"FOUR respellings … including `r4x_subslice`"*. The end-to-end
negatives run a 3-variant subset, and the message printed that sentence verbatim
while one variant had been tried. It is now derived from the variant table
(`6 R4 respelling(s) priced here: …`). A count narrated beside a table it does
not read is `.tasks/PROTOCOL.md` rule 13 inside a control's own output.

**Also corrected by the negatives, in the docstring rather than the code:** I had
written that a variant *"that so much as writes the word `forbidden` in a
comment is refused."* **False.** `spelling_matches` matches against
`exec_code(src)`, which blanks comments, string literals, Verus ghost code and
cfg-gated code, so the ban is on the program and not on the file — and a variant
**could** smuggle `volatile` past the audit in a comment. That is `check.py`'s
own rule, this file does not invent a stricter one, and the hole is now stated
in the docstring instead of the opposite claim. Group A carries both arms.

---

## §5 WHAT CONTRADICTS A PREMISE — INCLUDING THE MANAGER'S

### 5.1 ⚠⚠⚠ `TASK_PHP_028.md` §4.3 IS A MISATTRIBUTION. `ph03` IS SEARCHABLE; the row with the vacuous audit is `ph29`

§4.3 says:

> ⚠ **`ph03`'s declaration backticks nothing**, so `spellings` is 0 and
> admission is decided by prose plus one grep — the exact condition that made
> PAT's `p05` audit **unable to settle its own row**.

**`ph03`'s declaration backticks eleven things.** From the gate records' own
`idiom_audit` — not my count:

| row | `spellings` | of which `forbidden` | ⇒ `required` | `present` |
|---|---:|---:|---:|---:|
| `ph03-uudecode-bound` | **11** | 6 | **5** | 12 |
| `ph07-strcut-cursor` | 27 | 10 | 17 | 28 |
| `ph16-fdset-index` | 23 | 10 | 13 | 33 |
| **`ph29-recvfrom-alloc`** | **4** | **4** | **0** | **0** |
| `p05-index-flatten` (PAT) | **0** | 0 | 0 | 0 |

* **`p05-index-flatten` is the row with `spellings: 0`**, and it is where the
  sentence comes from — **verbatim**. `ph16`'s own hashed `why` quotes it: *"14
  also measured that this audit CANNOT settle p05 — its declaration backticks
  nothing, so `spellings` is 0 and admission is decided by prose plus one
  grep"*. The task file transposed `p05` → `ph03`. The provenance is exact and
  the claim is simply about a different row.
* **`ph03` therefore does NOT have the blocker §4.3 gives it.** It backticks 5
  `required` spellings — including a per-language pair, `(int) floor(len * 1.33)`
  (C) against `(ln * 133) / 100` (Rust) — and 3 distinct `forbidden` ones, all of
  which are exactly the kind of spelling a search must respect. **`ph03` can be
  searched without any `spec.md` edit.** The stop condition §4.3 offers does not
  apply, and the reason `ph03` was not done in this task is time (§6), not
  searchability.
* ⚠⚠ **The row that genuinely has the `p05` condition is `ph29`.** Its `idiom`
  `required` half backticks **nothing at all** (`spellings: 4`, all four in
  `forbidden`, and `present: 0` — *not one required spelling is present in any
  rung, because there are none*). Its two banned tokens are `calloc` and
  `#undef _FORTIFY_SOURCE`, neither of which any Rust rung could plausibly
  spell. **So on `ph29` the `ph07`/`ph16` audit machinery would report every
  candidate `IN CONTRACT` while checking nothing**, and a search there rests on
  prose alone. ⭐ **That is the row that may need spellings pinned in its
  contract before it can be searched, and that is the manager's call.**

### 5.2 ⚠⚠⚠ `ph16`'s OWN `NOTES.md` §8b NAMES THE WRONG RESPELLING, AND IT WAS WRONG IN BOTH DIRECTIONS

§8b is this row's published mechanism for the R2→R3 gap:

> The R2→R3 lever is one respelling … in R2 the guard bounds `this_fd` and the
> index is `this_fd / 64`, and rustc emits a *second* bounds check on `fds[..]`;
> in R3 the guard bounds the index itself and there is nothing left to check.

**Measured, in both directions, and the guard respelling emits BYTE-IDENTICAL
MACHINE CODE either way round:**

| variant | what it is | `kernel` | Ir |
|---|---|---|---:|
| `r3_guard_r2` | R2's guard spelling put into **R3** | 487 insn `d0091b202786` = **the shipped R3's own fingerprint** | **±0** |
| `r2x_guard_r3` | R3's guard spelling put into **R2** | 483 insn `5950ba114532` = **`safe_naive.rs`'s own fingerprint** | **±0** |

**rustc elides the second bounds test under BOTH spellings at `-O3`.** It cannot
be what separates R2 from R3.

**What the gap actually is:** item **2** of `safe_tuned.rs`'s module comment —
the entry run taken as a **subslice** and walked with `chunks_exact(2)`.
`r3_index_walk` (subslice kept, walked by index) is **+6.15 %**; `r3_absindex`
(R4's signature and an absolute index) is **+33.07 %** and is **byte-identical
to `safe_naive.rs`**. Roughly one part iterator to four parts subslice, and
**item 1 is worth zero instructions.**

⚠ **This does NOT touch §8a.** That number is R1-vs-R1h, read off two gcc cells'
disassembly, and guard (b) really is two instructions in the C loop. What is
retracted is what the same guard costs **in Rust**.

⚠⚠ **AND THE TWO RUNG SOURCES SAY IT TOO, AND I DID NOT TOUCH THEM.**
`safe_naive.rs`'s module comment (*"pays a bounds check on `fds[this_fd / 64]`
that R3's spelling makes provable — that difference is this row's R2→R3
gradient"*) and `safe_tuned.rs`'s item 1 both carry the retracted mechanism.
**Both files are pinned into `measure.py`'s `source_sha256`, so editing either
comment costs a 28-cell re-measure of `ph16`.** The correction is in `NOTES.md`
(not measure-pinned) as **§8b-RETRACTED**, and `README.md` points at it. **A
reader who starts from either `.rs` still meets the wrong mechanism first, and
whether that is worth a re-measure is the manager's call, not mine.**

⭐ Worth noting for the protocol: this defect was invisible to every check in the
tree. It is a *mechanism* claim, it is prose, the numbers beside it are right,
and the only thing that could falsify it was building the counterfactual — which
is precisely what a `spellings.py` does. **`controls/spellings.py` is not only a
bound-widener; it is a mechanism checker, and on this row it caught the row's own
published mechanism being wrong.** That is an argument for building it on every
row that states an R2→R3 or R3→R4 mechanism at all.

### 5.3 On trap §3.2 — pinning `spec.md` as a FILE is the wrong design, and I copied it anyway

`ph07`'s sidecar is the only one in the tree that pins `spec.md`
(`TASK_PHP_024` §4.2, 47 PAT sidecars checked). **I copied it, deliberately, so
that the two php sidecars are comparable** — and it is the wrong design.

* **What the sidecar actually depends on** is the `slb-contract` block, and
  specifically `idiom` — that is the only part `contract()` parses and `audit()`
  reads.
* **What it pins** is the whole 57 KB file, of which the block is a fraction.
  `ph16`'s `spec.md` carries the row's prose, the `why`, the `provenance` notes.
  **An edit to any of that stales `controls/spellings.json` and fails the gate on
  `[tables]`, for a change that cannot affect a single number in it.**
* **The repair is one line**: pin `sha256(the contract block)` under a key like
  `patterns/<row>/spec.md#slb-contract`, extracted with the gate's own regex.
  ⚠ **But `check.py` stage 9b resolves `derived_from_sha256` keys as PATHS**
  (`os.path.exists` / `sha256_file`), so a `#fragment` key would be reported
  `MISSING-SOURCES` — a `shout`. **So the repair needs either a harness change
  (forbidden here, and it would cost a 33-pattern re-gate) or a second key name
  the gate ignores plus the file pin kept.** It is not a one-line change after
  all, and that is why I did not attempt it.
* **My recommendation:** keep pinning the file, and treat the false staleness as
  a known cost — **but only until a php row's `spec.md` actually moves for a
  non-`idiom` reason, at which point two sidecars re-run for nothing and it is
  worth the harness conversation.** `spellings.json`'s `pin.note` on both rows
  now says this in terms.

### 5.4 ⚠ WHICH STATISTIC IS "THE BOUND" IS UNDECIDED, AND `ph07` HID IT

`.memory-php/02-ladder.md` publishes `ph07`'s `fixed-R4 bound` as `+11.98 %`.
That is the **marginal** figure. `ph07`'s per-call figures are `+11.40 %`
(`small.bin`) and `+11.90 %` (`large.bin`) — a 0.6 pp spread, so nobody had to
choose. **`TASK_PHP_028.md`'s own table quotes `ph16` from the per-call figure
(`-1.22 %`) while `.memory-php/02` quotes `ph07` from the marginal one
(`-1.94 %` here).** Two rows' headline numbers are currently computed by two
different statistics and the difference on `ph16` is 0.72 pp — **59 % of the
figure itself.**

Nothing in this task's conclusions turns on the choice: all three are negative,
all three move the same way, and the R4 side is degenerate on all three.
**`spellings.py` therefore publishes all three, labelled, and `NOTES.md` §8e
tabulates all three.** ⚠ **But `.memory-php/03-numbers.md` should say which one
"the bound" means before a third row is published**, or the programme will have
two conventions and one name. That is a manager decision and I have not made it.

### 5.5 Two smaller reconciliations, so nobody re-derives them

* **`kernel` instruction counts.** My fingerprint reports 487 / 483 / 426 for
  `safe_tuned` / `safe_naive` / `unsafe`, where the published table says 474 /
  479 / 425. **Not a discrepancy:** those are `asm.py`'s `n_raw` (487 / 483 /
  426, matching to the digit) versus its `n_fn` (the function-extent count, which
  drops trailing pad). `asm.py`'s own record carries both, plus `n_fn_nopad`.
* **The `--attribute` opcode view was replaced.** A first version bucketed the
  difference **by opcode**, and it was useless: the table was dominated by
  cosmetic loop-counter idiom (`add $2` + `je` versus `inc` + `cmp` + `jae`,
  ±4.5 M Ir each) that cancels to nothing. The **execution-count** decomposition
  is exact and reads as one line: 6 insns become 7 in one block. Kept in
  `.temp/php28/asm/` if anyone wants to see the bad view.

---

## §6 WHAT I DID NOT DO, AND WHY

1. ⚠⚠ **`ph03` and `ph29` — NOT SEARCHED. Neither side. The debt stands on
   both.** The task authorised stopping after one row and `ph16` took the whole
   task: 17 variants, 34 callgrind runs, 5 Verus runs, an instruction-level
   attribution, a validator, **54 negatives, FOUR defects found in the validator
   by its own negatives**, a retraction of the row's published mechanism, and
   three gate rounds (all green; rounds 2 and 3 were mine, for later edits to
   `NOTES.md` and `spellings.py`, not repairs of a refusal). **One row done
   properly.** ⭐ **The largest single reason it took the
   whole task is §5.2**: the mechanism the row published was wrong, which meant
   the candidate set could not be derived from it and had to be derived from the
   disassembly instead.
2. ⚠ **`ph29` should be next, and it needs a decision first, not a search**
   (§5.1): its `idiom` `required` half backticks nothing, so the audit stage of a
   cloned `spellings.py` would pass every candidate while checking nothing. **A
   search there is not well-defined until spellings are pinned in its contract —
   which is a `spec.md` edit in a hashed block, and the manager's call.** ⭐ That
   is the stop condition §4.3 describes; it is just on the other row.
3. **`ph03` is ready to search as it stands** — 5 `required` and 3 `forbidden`
   backticked spellings, no `spec.md` change needed — and it is the one with a
   *positive* spread, so it is the row where a two-sided search produces a real
   upper bound on the cost of safety rather than a non-monotonicity result.
4. **No Verus twin for `r4x_subslice` or `r4x_endcursor`.** Both are dearer than
   `R4ship`, so admissibility cannot change the published bound. `r4x_subslice`'s
   twin would need `run@ =~= win@.subrange(…)` threaded through `walk`'s spec —
   a spec rewrite, not a substitution, and `spec.md`'s `verus.items` pins those
   items. Named in the sidecar and in §8e as the search's limit.
5. **No correction to `safe_naive.rs` / `safe_tuned.rs`** — §5.2. A re-measure.
6. **No `.memory-php/` or `RECAP_PHP.md` edit** — manager-only for writing. The
   entries this task implies are: `02-ladder.md`'s *"AND SO DOES `ph16`,
   DELIBERATELY … whether that is a real non-monotone ladder or a spelling
   artefact is **unknown**"* is now **answered for `ph16`** (§2.1); its 12-of-20
   R4 tally becomes **13 of 21**; and `ph16`'s §8b retraction is a finding.
7. **No `CATALOGUE.md` edit** (`ph16` is still listed `verbatim` where the row
   says `narrowed`) — pre-existing, manager-owned, and untouched here.

---

## §7 REPRODUCE

```
python3 patterns-php/ph16-fdset-index/controls/spellings.py --audit-only
python3 patterns-php/ph16-fdset-index/controls/spellings.py --verus --attribute
python3 .temp/php28/asm/remake.py               # groups D5 and G need this
python3 .temp/php28/negatives_spellings.py --e2e
python3 .temp/php28/probe_exec.py
python3 harness-php/gate.py ph16-fdset-index    # FULL row name -- open item 42
```

Logs kept: `.temp/php28/spellings_final.log` (and `run1`/`run2`, which are the
evidence for §4.1's defects 1 and 2), `.temp/php28/negatives_fast.log`,
`.temp/php28/negatives_e2e.log`, `.temp/php28/probe_exec.log`,
`.temp/php28/gate{1,2,3}.log`, `.temp/php28/asm/R{3,4}.annot.asm` (the mechanism,
readable), and `.temp/php28/NOTES.md` as the index. **Binaries, `.o` and `.cg`
blobs are deleted — 144 MB down to 828 KB — and every one has a generator**
(`spellings.py`, `probe_exec.py`, `asm/remake.py`).
