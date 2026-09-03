# TASK_172 — the masked gate failure, and two free repairs

**Role: research engineer.** Three items. Item A is answered with a run before
anything was priced or edited; B and C are landed.

---

## HEADLINE

⚠⚠⚠ **THE MANAGER'S FRAMING IS RIGHT IN ITS CONCLUSION AND WRONG IN ITS
MECHANISM, AND THE MECHANISM IS THE PART A FUTURE AGENT WOULD REUSE.** The task
file predicted *"stage 3a is asking a `-O3` question at `-O0`"*. **`-O0` is not
the discriminating variable**: measured over all 1052 built windows, **261 of
263 `-O0 isolated` kernels carry their own backward branch**, and the first cell
this class ever bit was `-O3` (p02, gcc, `memcpy`, TASK_003_REVIEW). Gating the
structural test on the optimisation level would relax the predicate on **526**
windows to fix **1**.

✅ **What is actually wrong is narrower, older and already half-fixed in the
tree**: stage 3a conflates *"the loop collapsed"* with *"the loop is one static
call away"*, and it has an escape hatch for exactly that — `bulk_calls` — which
is **a list of NAMES**. `asm.py::_V0_BULK_RES`'s own comment describes p01's
situation verbatim, about **p02's `safe_tuned` at `-O0`**:

> *"it false-failed p02's `safe_tuned` at O0, where the copy and the fold are
> still out-of-line calls and the kernel symbol therefore has no loop of its
> own."*

p01's callee is `<core::slice::Iter<u64> as Iterator>::fold::<…,
safe_tuned::kernel::{closure#0}>`. **It is not a bulk-memory routine and can
never be in a list of them.** So: **the masked failure is a FALSE POSITIVE, p01
is clean, and the disposition is a `check.py` repair** — but the repair is to
replace a NAME LIST with a DERIVED structural fact, not to switch a check off at
a level.

⚠⚠ **AND THE ONE THING THE TASK FILE DID NOT ASK, WHICH I THINK MATTERS MOST:
the `check.py` repair is a NO-OP ON TODAY'S TREE.** `asm.py` still hands stage
3a the `fold` window, so the new disjunct is unreachable. Its entire value is
**pre-emptive** — it is the precondition that makes the eventual `asm.py` fix
cost a re-measure and *not* a red gate. Measured on the p01 smoke run: **5 of
1086 record leaves moved**, and one of them is `check.py`'s own hash. **That is
why it ships with ten must-fire arms, all ten SEEN TO FAIL** — a green sweep
says nothing about a branch nothing reaches.

⚠⚠ **A SECOND REFUTATION, THIS ONE OF A PUBLISHED SENTENCE.**
`results/SYNTHESIS.md:1619-1620` prices the item as *"the obvious repair
(exact-match-first) **moves 266 windows**"*. **266 is candidate B's blast
radius, and candidate B is the repair `TASK_170` §43e explicitly said not to
ship.** Re-derived here: candidate B collapses all 266 `whole`-mode Rust windows
onto the **8/11-instruction libstd C-ABI `main` shim**, which fails stage 3a on
**both** conditions (`no backward branch and no bulk-memory call`, `body 11 <
floor 20`) — **so it would turn 266 windows RED, not mis-measure them.** The
repair that is actually correct — candidate C — **moves 33 windows in 31
patterns.** ⚠ **The published limitation quotes the price of the wrong repair,
and it overprices the right one by 8×.**

---

## Did

| path | what |
|---|---|
| `harness/check.py` | stage 3a's **third disjunct** (`callee_loop_witness`, `_direct_call_targets`), a 40-line block comment carrying the measurement that bounds it, and **10 must-fire arms** (`_CALLEE_LOOP_CASES`) wired into `check_selftests` |
| `synthesis/synthesize.py` | item B: `BULK_REGIME` described and PRINTED as the whitelist it is; `unclassified_bulk_candidates` + `sidecar_callee_peak` (new, derived); the marker's reason string fixed; the inline-blindness statement added. Item C: `UNDECLARED_AT_26`, `WEAKER_ENDPOINT`, `weaker_endpoint_rows` (fail-closed), `backlog_cited`; both hand-typed counts replaced by `len()` of a printed list; the declared-rows split corrected from **two** buckets to **three** |
| `results/synthesis.md` | regenerated: **889 → 938 lines, `+58/−9`** |
| `patterns/p35-*/controls/{proof_mutants,union_oracle}.json` | **re-emitted** — they pin `check.py`'s hash and my gate-only edit staled them, hard-failing p35's stage 9c. `2 +/2 −` each: the pin and the timestamp; **no measured figure moved**. See *SWEEP RESULT* |
| `synthesis/licence.json` | re-emitted (`licence.py --emit`, it pins the gate `source_sha256`) |
| `patterns/p05-index-flatten/NOTES.md` | §1a: `19 of 32 → 20 of 32`, *"three"* → **four** `O0 whole` hits, the `verus` row `—` → `xmm (2)`, and the **invented mechanism struck** with the `objdump` that refutes it. Rides item A's sweep |
| `.temp/t172/` | 6 probes + `sweep.sh` + logs (all re-runnable; see *Artefacts*) |

**NOT touched, deliberately:** `harness/asm.py`, `.memory/`, `RECAP.md`,
`results/SYNTHESIS.md`, `harness/tools/composition.py`,
`patterns/p16-tlv-walk/NOTES.md`. No `git add`, no `git commit`.

---

## A. THE MASKED STAGE-3a FAILURE

### A1. The blast radius — **CONFIRMED, and both halves of the claim hold**

`.temp/t172/stage3a_sweep.py`, `asm.py` imported read-only. Candidate C
(TASK_170 §43e: the needle must be a whole v0 identity component) as the "true"
resolution, evaluated against `check.py::check_no_collapse`'s predicate
re-implemented as a pure function:

```
$ python3 .temp/t172/stage3a_sweep.py
windows enumerated: 1052   built: 1052   missing: 0

MIS-RESOLVED (picked != true): 33
  by (opt,mode,cell): {('O0', 'isolated', 'safe_tuned'): 1,
                       ('O0', 'whole', 'verus'): 31,
                       ('O0', 'whole', 'safe_naive_verus'): 1}
  by opt: {'O0': 33}
  patterns: ['p01','p03','p04','p05','p06','p07','p08','p09','p10','p11','p12',
             'p13','p14','p16','p18','p19','p22','p23','p25','p27','p28','p29',
             'p32','p34','p35','p36','p38','p42','p46','p47','p49']

stage 3a FAILS today (picked window):  0
stage 3a FAILS on the TRUE window:    1
    p01 safe_tuned O0 isolated ['no backward branch and no bulk-memory call']
      n_nopad=40 back=0 bulk=[]

NEWLY FAILING: 1
TRUE resolution returns None on: 0
```

* ✅ **33 cells — confirmed.** ✅ **`-O0` only — confirmed** (`by opt: {'O0': 33}`).
* ⚠ **It is 31 patterns, not 33.** `p02` and `p17` resolve their
  `verus -O0 whole` correctly, so their records are clean. **The re-measure
  price is 31 patterns, not 33** — `RECAP.md:30` and `TASK_170` §43f both say
  33.
* ⚠⚠ **AND THE TWO CLEAN ONES ARE CLEAN BY ACCIDENT, BY SEVEN INSTRUCTIONS.**
  `pick="largest"` decides this, and the margin is tiny
  (`.temp/t172/p02_p17_clean.log`):

  ```
  p01 verus-O0-whole   93  …driftsort_main…          <- WINS, mis-resolves
                       (the crate's own `verus::main` is 86)
  p02 verus-O0-whole  124  _RNvCs5wP2qveqZnT_5verus4main   <- wins by 31
  p17 verus-O0-whole  101  _RNvCs5wP2qveqZnT_5verus4main   <- wins by 8
  ```

  **Nothing structural protects `p02` and `p17`** — their drivers just happen to
  lower to a few more instructions than `core::slice::sort::stable::
  driftsort_main`'s 93. **A one-line driver edit could move either of them into
  the defect, silently.** That is an argument for fixing `asm.py`, and it is not
  in the record anywhere.
* **Exactly ONE window would newly fail.** The 32 `whole`-mode mis-resolutions
  change *which* symbol is measured but not the verdict: `driftsort_main` and
  the real `main` both loop and both clear the `whole` floor of 20.

### A2. **Is the loop in a callee? — YES, proven by disassembly**

`objdump -d --disassemble=_RNvCs86OlWC8CPt8_10safe_tuned6kernel
.temp/build/p01/safe_tuned-O0-isolated` — the whole body, 40 non-pad
instructions, no backward branch:

```
  17389: jb   173b9 <…+0x59>          <- forward (the sub-slice bounds check)
  173b5: jbe  173d9 <…+0x79>          <- forward
  173b7: eb 02  jmp 173bb             <- forward
  173d3: call *0x4398f(%rip)          <- INDIRECT (the panic thunk)
  173ec: call 17450 <…core5sliceSy4iter…>
  173fb: call 16e70 <_RINvXs2J_…core5slice4iter…Iterator4fold…
                       NCNvCs86OlWC8CPt8_10safe_tuned6kernel0…>
  17404: ret
```

The three callees, resolved:

```
_RNvCs86OlWC8CPt8_10safe_tuned6kernel     nopad=  40  back=0  loop=False  bulk=[]
_RINvXs2J_…Iterator4fold…6kernel0…        nopad=  69  back=4  loop=True   bulk=[]
_RNCNvCs…10safe_tuned6kernel0B3_          nopad=   3  back=0  loop=False  bulk=[]
```

⚠⚠ **The looping callee is `Iterator::fold` MONOMORPHISED AT p01's OWN CLOSURE**
— the `NCNvCs…10safe_tuned6kernel0` suffix is `safe_tuned::kernel::{closure#0}`.
**It is not somebody else's loop that happens to be nearby; it is p01's loop,
one direct call away.** And at the level p01 publishes, the kernel has its own:

```
p01 safe_tuned O3 isolated:  picked = …10safe_tuned6kernel   nopad=44  back=2
```

**`synthesis/outward_ir.json` could not answer this.** It is `-O3 isolated`
only — `outward_ir.py:502-503` defaults `--opt O3 --mode isolated`, and the JSON
does not record the level at all (`json.dumps(doc).count("O3") == 0`). ⚠ **So
the instrument the task named was blocked. What was NOT blocked, and is what I
used, is `objdump` on the already-built `-O0` binaries: zero builds, zero
callgrind, ~4 minutes for all 1052 windows.**

### A3. **Does the dynamic check already pass? — YES, with an 84× margin**

Read from the record (`results/gate/p01-array-sum.json`), not from a log:

```
safe_tuned/O0/isolated/small.bin     10622.3   floor 0.25 * 501  = 125.25   84.8x
safe_tuned/O0/isolated/large.bin     86117.3   floor 0.25 * 4096 = 1024.0   84.1x
safe_tuned/O0/isolated/d_ir_d_work      21.0   ALPHA_IR_PER_WORK = 0.25     84.0x
```

and `check_marginal_ir`'s own docstring says why this is the right instrument
for exactly this cell:

> *"Measured as a slope … which is symbol-independent (so it works in `whole`
> mode, **and at O0 where a rung's work lives in `core::iter` symbols rather
> than in `kernel`**)."*

**The harness already documents p01's situation as expected, in the docstring of
the check that covers it.** That is the strongest single piece of evidence that
the structural test is the one asking the wrong question.

### A4. **How much could a "loop in a direct callee" hatch excuse? — MEASURED**

`.temp/t172/callee_loop_probe.py`, 1052 windows, one `objdump` each:

```
windows with NO back edge in the window itself: 2
  p01 safe_tuned O0 isolated  bulk=[]              looping_callees=[…Iterator4fold…IterY…6kernel0…]
  p02 safe_tuned O0 isolated  bulk=[copy_from_slice] looping_callees=[…Iterator4fold…Iterh…6kernel0…]

windows where the hatch is REACHABLE (no back edge AND no bulk call): 1
  p01 safe_tuned O0 isolated
    callees        : ['_DYNAMIC', '…core5sliceSy4iter…', '…Iterator4fold…6kernel0…']
    looping callees: ['…Iterator4fold…6kernel0…']

windows with >=1 LOOPING direct callee: 444 of 1052
looping callees whose name mentions panic/unwind/abort/assert: 0 occurrences, 0 distinct
```

Four things this settles:

1. **The hatch is reachable on 1 window of 1052.** It cannot silently relax
   anything else.
2. ⚠ **p02's window has the IDENTICAL looping callee** — the same
   `Iterator::fold` monomorphisation, over `Iter<u8>` instead of `Iter<u64>`.
   **The derived rule subsumes the name-based one on the one window the
   name-based one was built for.** That is the argument for replacing the list
   rather than extending it.
3. **The panic path is not a loophole on this tree**: 0 of the 444 windows with
   a looping direct callee have a panic/unwind/abort/assert callee.
4. **`-O0` is not the variable**: 261 of 263 `-O0 isolated` windows carry their
   own back edge (`(O0,isolated,has_loop=True)` = 131 + 130).

### A5. **DISPOSITION — a `check.py` repair, and what it is**

`check.py`'s stage 3a gains a **third disjunct**, `callee_loop_witness`:

> a kernel with no backward branch and no bulk call also passes if it makes a
> **DIRECT call** (depth 1) to a symbol **defined in the same binary** that
> **itself contains a backward branch** — and only in **`isolated`** mode.

What bounds it, each stated in the code and each measured rather than asserted:

| bound | why | measured |
|---|---|---|
| only consulted when there is no back edge AND no bulk call | it cannot weaken any window that passes today | **1 of 1052** reaches it |
| `isolated` only | in `whole` the window is `main`, whose callees include the driver's `arg_path`/`load`, both of which loop over I/O that is not the kernel's work — a witness there would be free and mean nothing | all **526** `whole` windows already pass on the first disjunct, so the restriction costs nothing |
| DIRECT calls only, depth 1, symbol defined in this binary | a constant-folded kernel has no such call; a PLT stub has no body | the indirect panic thunk in p01's own kernel is correctly **not** a target |
| no name requirement on the callee | `v[a..b].iter().sum::<u64>()` monomorphises to `<u64 as Sum<&u64>>::sum::<Iter<u64>>`, which does **not** name the kernel — *"a census that can only find the phrasings you thought of"* is this project's own named defect | — |

It reports rather than passing silently: `rep.note`, which lands in the gate
record's `notes` and is **not** in `RENDER_INPUT_KEYS`, so it costs no re-render
(`rep.shout` would have — `PROTOCOL` rule 6's `TASK_170` row). ⚠ **I considered
a shout and rejected it**: the fact is about a `-O0` window and the four Results
are `-O3`. **That is a reversible call the manager can overrule for +1 render
and +1 gate on p01.**

**End-to-end demonstration on the real binary** (`.temp/t172/p01_witness.py` —
`asm.py` untouched, the true window resolved by candidate C in the probe):

```
=== p01 safe_tuned O0 isolated
  asm.py PICKS : _RINvXs2J_NtNtCs4NRVxsYgnAr_4core5slice4iterINtB7_4IteryENtNtNtNtBb_4i
  TRUE window  : _RNvCs86OlWC8CPt8_10safe_tuned6kernel
    n_fn_nopad=40  back_edges=0  bulk=[]
  THIRD DISJUNCT witness: …Iterator4fold…10safe_tuned6kernel0… (4 back edges)
  stage 3a BEFORE TASK_172: FAIL ['no backward branch and no bulk-memory call']
  stage 3a AFTER  TASK_172: PASS

=== p02 safe_tuned O0 isolated
    n_fn_nopad=102  back_edges=0  bulk=['…copy_from_slice…']
  THIRD DISJUNCT witness: …Iterator4fold…10safe_tuned6kernel0… (4 back edges)
  stage 3a BEFORE TASK_172: PASS       (via the NAME list)
  stage 3a AFTER  TASK_172: PASS       (either disjunct)

=== p01 safe_tuned O3 isolated
    n_fn_nopad=44  back_edges=2
  THIRD DISJUNCT witness: NONE
  stage 3a BEFORE / AFTER: PASS        (its own loop; the disjunct is not used)
```

### A6. **THE MUST-FIRE ARMS — ten, and all ten SEEN TO FAIL**

The disjunct is **prospective**: nothing on today's tree reaches it, so a green
33-pattern sweep is evidence about nothing. `.temp/t172/arm_break.py` uses
`TASK_170`'s method — copy the source, ONE asserted string substitution, import
the copy fresh so mutations do not compose, read the table it builds at import:

```
$ python3 .temp/t172/arm_break.py                                    rc=0
BASE: 10 arms, failing = []

M1 the `isolated`-only guard is dropped                     -> 1 arm FAILS
M2 the self-call guard is dropped                           -> 1
M3 an interior target `<sym+0x10>` is no longer stripped     -> 1
M4 any callee counts -- `has_loop` no longer required        -> 2
M5 a callee with no body in this binary counts as a witness  -> 1
M6 the DIRECT-CALL restriction is lost (every symbol)        -> 2
M7 the witness is never recorded (the positive arms)         -> 3

=== per-arm: which mutation was SEEN to break it ===
  SEEN   a DIRECT call to a callee with a backward branch IS a witness  M7
  SEEN   two looping callees are both reported                          M7
  SEEN   an INTERIOR target `<sym+0x10>` resolves to `sym`              M3,M7
  SEEN   a callee with NO backward branch is NOT a witness              M4
  SEEN   a callee whose only branch is FORWARD is NOT a witness         M4
  SEEN   a call to a symbol NOT DEFINED in this binary is NOT a witness M5
  SEEN   an INDIRECT call is not a call target at all                   M6
  SEEN   a SELF-call is not a witness                                   M2
  SEEN   a collapsed kernel -- no calls at all -- has no witness        M6
  SEEN   `whole` mode has NO witness even when a callee loops           M1

arms never seen to fail: 0 of 10
```

⚠ **One arm was mis-built and the mutation harness caught it, which is the
point of writing the harness.** The first `_ARM_LOOP` was a constant list with
an absolute branch target `jne 2000`, so the *second* callee in the two-callee
arm was laid out at `0x2100` and its branch was no longer backward — the arm
would have passed while testing nothing. The bodies are now functions of the
base address, and the reason is a comment in `check.py`.

### A7. **THE PRICE OF THE `asm.py` FIX — for the manager, and not taken**

`.temp/t172/candidates.py`, both candidates as pure functions over
`asm.symbols()`, `asm.py` never modified:

```
windows: 1052

candidate B (exact-match-first, TASK_169 §3f): moves 266 windows in 33 patterns
  by (opt,mode,cell): every `whole` Rust cell at BOTH levels
    (O0,whole,safe_naive) 33 . (O3,whole,safe_naive) 33 . safe_tuned 33+33 .
    unsafe 33+33 . verus 33+33 . safe_naive_verus 1+1
  example: p01 safe_naive O3 whole
    A(today) _RNvCsaBH6GJeUSWJ_10safe_naive4main       (nopad 703)
    B        main                                       (nopad  11)

candidate C (whole v0 identity component, TASK_170 §43e): moves 33 in 31 patterns
  by (opt,mode,cell): {('O0','isolated','safe_tuned'): 1,
                       ('O0','whole','verus'): 31,
                       ('O0','whole','safe_naive_verus'): 1}
```

⚠⚠ **Candidate B is not merely wrong, it is FATAL, and nobody had said so.**
The shim it collapses onto is 8 instructions at `-O0` and 11 at `-O3`, against a
`whole` floor of **20**:

```
candidate B window on p01 safe_tuned O3 whole:
  nopad= 11  has_loop= False  bulk= []
  stage 3a -> ['no backward branch and no bulk-memory call', 'body 11 < floor 20']
```

**So `results/SYNTHESIS.md`'s *"the obvious repair (exact-match-first) moves 266
windows"* understates it: it would turn 266 windows RED on two conditions each.
And it prices the wrong repair — the right one moves 33.**

**What the 33 windows WOULD change, and whether a published figure is among
them:**

| artefact | affected? | evidence |
|---|---|---|
| the four **Results** (`results/SYNTHESIS.md` §2–§5) | ⚠ **NO** | all four are `-O3`; the mis-resolution is `-O0`-only |
| `results/synthesis.md` | ⚠ **NO** — checked positively, not assumed | `grep -c '"O0"' synthesis/synthesize.py` → **0**; §4's static census filters `(c["cell"], c["opt"], c["mode"]) == (r, "O3", "isolated")`; the one other `opt`/`mode` filter is `"O3"/"whole"` and reads `kernel_exclusive_ir`, not `static` |
| `results/SYNTHESIS.md` | ⚠ **NO** | its only `-O0` figures are `Ir` (p34's `+164.70/+2953.27`, p35's `+6035.46`), not statics |
| `results/pNN-*.json` | ✅ **YES — 33 windows in 31 records** carry a wrong `static.symbol`/`n_*`/`md5_*` | measured; e.g. `p01 safe_tuned O0 isolated` records `_RINvXs2J_…Iterator4fold…` |
| `results/tables/pNN-*.md` | ✅ **YES — 33 rendered rows in 31 tables** | `report.py:474` renders `c["static"]` for every `(cell, opt, mode)` including both `-O0` sections. `results/tables/p01-array-sum.md` publishes `safe_tuned O0/isolated` as **69 instrs / 274 B / `33f80521` / loop yes** where the kernel is **40 / 165 / loop NO**, and `verus O0/whole` as **86 / 329 / vec `-`** where `main` is **76 / 391 / `xmm`** |

**Price, per `PROTOCOL` rule 6's corrected cost chain
(`re-measure → report.py → gate`), for candidate C:**

* **31 re-measures** (not 33 — p02 and p17 are clean). p19's took **1 m 17 s**
  and p46's moved 111 of 1371 leaves, none of them `Ir`; so ≈ **40 minutes**.
* **31 `report.py` renders.**
* **≥ 31 gate runs**, and this is the expensive half: p01's gate run took
  **341 s** on this box (measured, `.temp/t172/gate/sweep.progress`), so **≈ 3.5 hours** for 31 —
  and any pattern whose `controls_json` also moves owes a second.
* **Plus** whatever `licence.py --emit` costs (a disassembly pass, ~1 min) and
  one `synthesize.py`.
* ✅ **The `check.py` repair landed here is a precondition, not a substitute:
  with it in place the re-measure is arithmetic and produces no red gate.
  Without it, `p01`'s stage 3a goes RED the moment `asm.py` is fixed.**

⚠ **I did not start it. `asm.py` was not touched.**

---

## B. THE `§` MARKER'S CENSUS

### B1. `BULK_REGIME` **is** a whitelist, and it is now printed as one

`results/synthesis.md` said *"The marked rows are DERIVED, not listed"*. It now
says **"The marked ROWS are derived; the ROUTINE SET is a WHITELIST"**, and
prints it:

```
| callee key | routine | forced VECTOR below | forced BYTE-WISE above | cells |
| `0x0000000000188a80` | glibc `memmove` (`__memmove_avx_unaligned_erms`) |  852.00 | 8192.00 | 82 |
| `0x0000000000189480` | glibc `memset`  (`__memset_avx2_unaligned_erms`) |  300.00 | 4000.00 | 68 |
| `__rustc::__rust_alloc_zeroed` | `__rust_alloc_zeroed`'s fill           |  300.00 | 4000.00 |  2 |
```

⚠ **And it names WHAT makes it a whitelist, which is not the names.** It is the
pair `(lo, hi)` — the routine's own byte-count crossover. **The sidecar carries
`Ir` per call and no byte count, so a routine-independent signature rule is not
available from it.** That is stated in the document and in the code comment,
because *"widen it if the widening is derivable"* has a real answer and the
answer is **no, not from this sidecar** — and saying so is the honest form.

### B2. What the whitelist does **not** decide — **DERIVED, and it settles TASK_171's open question with a measurement**

New: `synthesize.py::unclassified_bulk_candidates` (every callee **not** in
`BULK_REGIME` contributing asymmetrically ≥ `FLOOR` on a published pair) and
`sidecar_callee_peak`. Both print on every run.

```
69 distinct callee keys across 221 published rows
scored against min(lo) = 300.00 and min(hi) = 4000.00:
  0 clear the byte-wise bound
  6 clear even the vector bound
       3246.60  core::ptr::drop_glue::<[Option<Box<safe_naive::Rec>>; 32]>   p29
       3246.60  core::ptr::drop_glue::<[Option<Box<safe_tuned::Rec>>; 32]>   p29
       1505.75  core::ptr::drop_glue::<[Option<Rc<safe_naive::Obj>>; 16]>    p34
       1505.75  core::ptr::drop_glue::<[Option<Rc<safe_tuned::Obj>>; 16]>    p34
       1252.36  core::ptr::drop_glue::<[Option<Box<u8>>; 32]>                p27
        414.87  0x0000000004001190                                           p02
```

and the two routines `TASK_171` named as *"silence, not a decision"*:

```
0x0000000000188080  __memchr_avx2  peak Ir/callee-call = 41.51  at p11/large/c-clang-h  (6 cells)
0x000000000018b7c0  __strlen_avx2  peak Ir/callee-call = 33.06  at p11/large/c-clang    (6 cells)
```

✅ **`41.51` and `33.06` against a `min(lo)` of `300.00` — 7× and 9× under the
figure that FORCES the vector path under every crossover this project has
resolved. They are VECTOR on every cell they appear in, so they cannot trigger
the mark, and adding them to the whitelist would change NO ROW.** That is
`TASK_171`'s *"probably would not clear the regime test … but that judgement has
not been made anywhere"*, **made, from the measurement, without a name**.

✅ **And the point from the other side, also printed**: the single biggest
callee in the whole sidecar — `0x15220`, `ld.so`'s
`_dl_runtime_resolve_xsavec`, **4828.00 `Ir`/callee-call**, above the byte-wise
bound — **does not appear in the census at all**, because it is invoked once per
program and its contribution to every published difference is under the 2.00
floor. **No rule had to know its name.** (`TASK_171` clean negative 9 resolved
the symbol; this makes the exclusion a printed consequence of the floor rather
than an unstated judgement.)

⚠ **The limit is printed too**: the scoring uses the crossovers of routines this
project has *resolved*; a bulk routine whose own crossover sat far below every
resolved one would be byte-wise while reading under 300, and a sidecar with no
byte count cannot tell. **Nothing on this tree is near it** — the largest
unclassified figure is a Rust `drop_glue` over a 32-element array, which has no
size regime at all (≈101 `Ir`/element, linear in the array, not in a byte
count).

### B3. The reason string — **fixed, and the artefact is now printed as such**

*"while the other side does not call it at all"* is gone. Re-derived on the
marked pattern itself (`.temp/t172/regime_probe.py`):

```
p08 small c-gcc    0x0000000004001160=156.00(39.0/c)
p08 small c-clang  0x0000000000015220=0.19(4828.0/c)
                   0x0000000000188a80=196.81(39.4/c)   <- BULK_REGIME's memmove
                   0x0000000000189480=4112.84(4113.0/c)
```

**`c-gcc` carries the SAME `memmove` at 39.0 `Ir`/callee-call against clang's
39.4 — the delta is the extra thunk — under a client PLT key.** So the clause is
now key-relative and **branches on the pair**:

* `gcc-clang` → *"`c-gcc` reports NO CALLEE EDGE UNDER THIS KEY — which on a
  `gcc-clang` pair is **NOT** the same as not calling it, because the key space
  is compiler-dependent"*, plus a full caption below the table with the 39.0 vs
  39.4 numbers;
* a rung pair → *"both cells here are rustc-built, so the key space is common
  and this one **does** mean no call"*.

⚠ **The first draft printed the `gcc-clang` caveat on `p42 R2-R4`, which is two
rustc cells. Caught by reading my own generated output and fixed.**

### B4. The inline blindness — **it now SAYS it does not cover inline bulk**

A new paragraph names `p27 gcc-clang` explicitly: gcc `rep stos` = 32 `Ir`
inside `<kernel>`, clang 18 `movaps` + 1 `xorps` = 19, **both inline**, 13 of a
`−25.02` row = **52%**, no callee edge, structurally invisible. And it says the
same of the marked pattern's own gcc side — **`p08 gcc-clang` is marked only
because clang calls out**, so a pair where both sides inlined would be silently
unmarked.

---

## C. TWO FALSE COUNTS IN A GENERATED FILE

Both are now `len()` of a list the same paragraph prints. A count and a list
that come from one object cannot disagree.

### C1. *"every entry cited to a reviewed artefact — except one, `p06`"*

`synthesize.py::backlog_cited` derives the exception set from the citation
itself (`c.lstrip().startswith("RECAP")`), **and prints the boundary of the rule
so a reader can see where it stops**:

```
backlog_cited (primary, mentions): (['p01', 'p03', 'p08'], ['p01', 'p03', 'p08', 'p18'])
```

The published sentence is now **"4 of 33 are NOT cited to a reviewed
measurement"**, with `p06`'s `⊘` and then `p01 p03 p08` quoting their own
verdicts (*"R3 span OWED"*, *"R3 span 1 unreviewed measurement; the +5 constant
NEVER searched"*, *"R3 span OWED"*), plus: *"4 entries **mention** the queue …
and 3 cite it and nothing else; `p18` cites a `NOTES.md` and a review as
well, which is a different state."*

⚠⚠ **And the second half of `TASK_171` §3d — the residual — is fixed too.**
`n_found` was `len(declared) - len(SEARCH_NONE)`, so `p01` and `p08`, whose
entries say the span is **OWED**, were counted inside *"report a SEARCH
RESULT"*. **The split is now THREE buckets, each a set:**

```
before:  33 DECLARED = 30 SEARCH RESULT + 3 NO SEARCH
after :  33 DECLARED = 27 SEARCH RESULT + 3 NO SEARCH (p29 p32 p49)
                                        + 3 SEARCH STILL OWED (p01 p03 p08)
```

✅ **`30 → 27` collides with nothing**: `grep` over `results/SYNTHESIS.md`,
`RECAP.md` and `.memory/` finds no quotation of *"30 report a SEARCH RESULT"* or
of *"30 of them declare a search that was reviewed"*.

### C2. *"Seven of the fourteen"* over a list of six

Now `UNDECLARED_AT_26` (data, so *"fourteen"* is `len()`) and `WEAKER_ENDPOINT`
(a dict keyed to a **verbatim substring of the row's own entry**). The published
sentence reads **"8 of the 14 …"** and prints the eight with their own words:

```
- p02 — "The R4 side is explicitly UNsearched"
- p09 — "The R4 half is the weaker one"
- p14 — "The R4 side was never searched"
- p18 — "⊘ The R4 side is NOT searched, declared"
- p19 — "only the review re-measured them"
- p27 — "R3 searched twice; R2 never"
- p38 — "the R4 side is disclosed but NOT established, and it flatters SAFE"
- p46 — "Those widths are TASK_092's UNREVIEWED re-measure"
```

`TASK_171` named six + `p18` + `p38` = **eight**; the typed word said *seven*
and the printed list had *six*, so **three numbers disagreed in one sentence**.

⚠ **One more of the same shape, found while doing this and fixed**: `n_none`
was scored as `SEARCH_NONE & set(SEARCH_REVIEWED)` while its denominator is
`declared = SEARCH_REVIEWED.keys() & set(meas)` — an entry for an unmeasured
pattern would have inflated the *"reviewed declaration of NO search"* bucket and
deflated the residual. All three buckets are now scored on `declared`.

**`weaker_endpoint_rows` FAILS CLOSED** — silently dropping a row is the
flattering direction and is how the old sentence got there:

```
(.temp/t172/itemC_arms.log)
  normal: ['p02','p09','p14','p18','p19','p27','p38','p46']
  ok    a DRIFTED quote raises rather than dropping the row
          -> WEAKER_ENDPOINT has rotted away…: p18: the anchoring quote … is no longer in its entry
  ok    a key with an ENTRY but OUTSIDE the population raises
          -> …p01: not in the population [...]
  ok    a key with NO entry at all raises
          -> …p99: not in the population [...]
  arms failing: 0
```

⚠ **The membership is a judgement and is labelled as one.** The code names what
it deliberately excludes and why: `p04 p05 p07 p16 p42` report a
**searched-and-degenerate** endpoint (a result, not a gap), and `p23`'s one
disclosure is about probe durability while its floor correction was found and
settled *by* a review.

---

## Evidence — the gates

```
$ python3 harness/measure.py --check-stale                       (BEFORE the sweep)
   rc=1   66 record(s) examined, 32 STALE
   32 x results/gate/pNN.json  harness/check.py
    1 x results/gate/p05-index-flatten.json  patterns/p05-index-flatten/NOTES.md
   (p01 already re-gated by the smoke test; exactly the predicted set, no measurement stale)

$ python3 harness/tools/composition.py --check                   rc=0
   OK: published composition table matches the tree (33 patterns, 10 classes)

$ python3 synthesis/synthesize.py                                rc=0
   wrote results/synthesis.md  (139722 bytes, 803 lines)
   outward-pin must-fire arms: 7/7 pass
```

**p01 smoke run — the prediction, and the record diffed leaf by leaf**

```
$ python3 harness/check.py p01                                   rc=0
   verdict: PASS-WITH-BLOCKED-ROWS   failures: []
   blocked: [('miri', 'unsafe.rs on large.bin')]
   3a: ok  28 cells   3b: ok 56 cell/probe pairs, tightest margin 7.0x

leaves: 1086 -> 1086   MOVED: 5
  /source_sha256/harness/check.py   ae040b91… -> eeb7ffa7…
  /marginal_ir_env/bytes            3267 -> 3280
  /marginal_ir_env/envp_stack_bytes 3651 -> 3664
  /miri/runs[3]/seconds             0.1 -> 0.2
  /miri/runs[7]/seconds             1.0 -> 1.1
```

**ZERO `Ir`, zero md5, zero identity, zero verdict, zero `notes`.** The two
`marginal_ir_env` figures are the environment-block length, which
`check_marginal_ir`'s docstring names as an inter-run effect and not a code
change; **no `marginal_ir_per_call` value moved at all.** `notes: []` confirms
the third disjunct is unreached on today's tree, exactly as predicted.

**33-pattern sweep** — see *SWEEP RESULT* below.

---

## SWEEP RESULT

**33 patterns, 6985 s of gate (116 min). One pattern failed on the first pass,
was diagnosed, fixed and re-gated. Final census, read from the RECORDS:**

```
$ python3 .temp/t172/verdicts.py                                       rc=0
=== from the 33 RECORDS ===
verdicts : {'PASS-WITH-BLOCKED-ROWS': 3, 'PASS': 30}
blocked  : {'p01': 1, 'p35': 3, 'p42': 1}
failures : NONE

=== each check.py's OWN exit status (.temp/t172/gate/pNN.rc) ===
rc files : 33   non-zero: NONE

=== notes/loud carrying the new third disjunct ===
                                    (empty -- the disjunct is unreached, as predicted)

EXPECTED: {'PASS': 30, 'PASS-WITH-BLOCKED-ROWS': 3} {'p01': 1, 'p35': 3, 'p42': 1} 0 failures, 33 rc=0
MATCH   : True
```

### ⚠⚠ THE ONE FAILURE, AND IT IS A COST `PROTOCOL` RULE 6 DOES NOT LIST

**`p35` came back `rc=1`.** Not the third disjunct, not `p05`'s doc edit —
**two of `p35`'s `controls/*.json` sidecars pin `harness/check.py`'s HASH in
their own `derived_from_sha256`**, so a gate-only `check.py` edit staled them,
which added two `STALE` lines to the render, which **hard-failed stage 9c**:

```
FAIL [tables] patterns/p35-tagged-union/controls/proof_mutants.json is STALE:
     1 of 4 pinned source(s) moved under it (['harness/check.py'])
FAIL [tables] patterns/p35-tagged-union/controls/union_oracle.json is STALE:
     1 of 5 pinned source(s) moved under it (['harness/check.py'])
FAIL [tables] results/tables/p35-tagged-union.md is STALE IN ITS CONTENT: 2 line(s) differ
     @@ -152,0 +153,2 @@
     +- **`controls/proof_mutants.json`** — `STALE`: ...
     +- **`controls/union_oracle.json`**  — `STALE`: ...
```

⚠⚠ **`PROTOCOL` rule 6's cost table says a `check.py` change costs "a gate
re-run", and `TASK_170` widened that to "+ a render and a re-gate per pattern
whose `loud` moves". NEITHER covers this: `p35`'s sidecars pin `check.py`
DIRECTLY, so the cost is +2 CONTROL-GENERATOR RUNS, both of which run Verus.**
✅ **Blast radius, measured rather than guessed:**

```
$ grep -l "harness/check.py" patterns/*/controls/*.json
patterns/p23-partition/controls/controls_pin.json
patterns/p28-intrusive-lists/controls/repro.json
patterns/p35-tagged-union/controls/proof_mutants.json
patterns/p35-tagged-union/controls/union_oracle.json

# but only p35's two pin the HASH, in `derived_from_sha256`:
patterns/p35-tagged-union/controls/proof_mutants.json /derived_from_sha256/harness/check.py ae040b91af8bca292923
patterns/p35-tagged-union/controls/union_oracle.json  /derived_from_sha256/harness/check.py ae040b91af8bca292923
$ sha256sum harness/check.py  ->  eeb7ffa7b0346724d4fc…
```

`p23` and `p28` only *mention* the path in prose, and both gated `rc=0`. **So
the rule is: 4 sidecars name `check.py`, 2 pin it, 1 pattern pays.**

**The repair, and it needed no `report.py`:**

```
$ python3 patterns/p35-tagged-union/controls/union_oracle.py    rc=0   9/9 cell(s) as designed
$ python3 patterns/p35-tagged-union/controls/proof_mutants.py   rc=0   9/9 arm(s)  as designed
$ python3 harness/check.py p35                                  rc=0
```

⚠ **`results/tables/p35-tagged-union.md` did NOT move** (absent from
`git status`), because the render only differed *while the sidecars were stale*;
and the record's `controls_json` is byte-identical to `HEAD`'s
(`{"detectors.json": "FRESH", "proof_mutants.json": "FRESH", …}`), so no `loud`
and no `RENDER_INPUT_KEYS` moved either. **The two sidecars' own diffs are
`2 +/2 -` each — their pinned `check.py` hash and their timestamp; every measured
figure in them is unchanged.**

### What the sweep moved, all 33 records, leaf by leaf

```
$ python3 .temp/t172/record_diff.py   (and .temp/t172/record_diff2.log for the breakdown)
records: 33   leaves compared: 40755   moved: 462

  209  adversarial (stdout / exit / cells / hung / diverges)
   66  marginal_ir_env  (the environment-block length)
   63  sanitizer diagnostic strings
   47  marginal_ir_per_call
   39  miri seconds
   34  source_sha256   (33 x harness/check.py + 1 x p05's NOTES.md)
    3  notes
    1  derived_contract/collapse_tightest_margin  (p38, derived from a moved marginal)
```

✅ **AND NOT ONE CERTIFYING VALUE MOVED. Checked positively, by key, not
assumed** (`.temp/t172/record_diff3.log`):

```
CERTIFYING keys among the 462 movers:
      0  md5 / digest              0  checksum              0  identity
      0  verdict                   0  failures              0  blocked
      0  contract_sha256           0  verus verified/errors
      0  kernel_exclusive/inclusive Ir                      0  static instr counts
      0  published_table / table_render                     0  controls_json
      0  loud                      0  idiom_audit           0  input_sha256
      0  miri VERDICTS (not seconds)
TOTAL certifying movers: 0
```

⚠ **The 47 `marginal_ir_per_call` movers are the documented environment-block
effect and they land where `check_marginal_ir`'s own docstring says they will —
with ONE pattern the docstring's list does not name.** The docstring: *"if p08's
12 cells move by a few hundredths, or p03/p04's `-O3 isolated` cells or
p03/p04/p38/p46's `whole` cells move by exactly 7 (14 for p46), or any `-O0`
cell moves in either mode, between gate runs, that is this effect."* Observed:

| pattern | cells | magnitude | in the docstring's list? |
|---|---:|---|---|
| `p08` | **12** | 0.02 … 0.10 (hundredths) | ✅ and the count matches exactly |
| `p03` | 8 (`whole`) | ±7.00 | ✅ |
| `p04` | 4 (`O3 whole`) | −7.00 | ✅ |
| `p38` | 5 (`O3 whole`) | −7.00 / −6.98 | ✅ |
| `p46` | 14 | −7.00 and **−14.00** | ✅ ("14 for p46") |
| **`p28`** | **4 (`O3 whole`)** | **−7.00** | ⚠ **NOT LISTED** |

⚠ **`p28` is a fifth member of the `±7` `whole`-mode family and the docstring's
census does not name it.** Same magnitude, same mode, same mechanism (a per-call
stack array's alignment moved by the environment block); it is an extension to a
documented list, not a new effect — but the list is quoted as if closed.
**Manager-owned `.memory/03-measurement.md` / `check_marginal_ir` addition.**

⚠ **The 3 `notes` movers are adversarial non-determinism, not a code change**:
`p03 adversarial-underflow.bin/c-clang` 3 → 4 distinct behaviours,
`p25 adversarial-lateread.bin/c-gcc` 4 → 3, `p29 adversarial-succ.bin/c-clang`
4 → 3. `.memory/` already records that an R1 adversarial rung is not
deterministic and that nothing gates on a divergence (p29's precedent).
**0 of the 272 adversarial/sanitizer movers is a non-output field** — no `exit`
code, `cells`, `hung` or `diverges` moved except as part of a stdout that moved.

### The step-4 gates, each rc read from its own `.rc` file

```
check_stale2   rc=0     66 record(s) examined, 0 STALE
licence_emit   rc=0     wrote synthesis/licence.json: 33 patterns, 132 pair verdicts
synth_final    rc=0     wrote results/synthesis.md (140390 bytes, 807 lines)
                        outward-pin must-fire arms: 7/7 pass
temp_cit2      rc=0     OK (new=0 unclassified=0)  ·  --lines: OK (new=0 unclassified=0 resolved=6)
composition2   rc=0     OK: published composition table matches the tree (33 patterns, 10 classes)
verdicts       rc=0     MATCH: True
```

### Final diff

```
$ git diff --numstat
212      1  harness/check.py
442     29  synthesis/synthesize.py
 58      9  results/synthesis.md                      (889 -> 938 lines)
 44     11  patterns/p05-index-flatten/NOTES.md
 34     34  synthesis/licence.json                    (the re-emitted check.py pin)
  2      2  patterns/p35-tagged-union/controls/proof_mutants.json
  2      2  patterns/p35-tagged-union/controls/union_oracle.json
 + 33 x results/gate/pNN.json
```

⚠ **DISCLOSURE ABOUT THE SWEEP ITSELF: it ran in two parts.** The harness killed
the first background job while `p28` was mid-Verus (22 patterns done, all
`rc=0`); `patterns/p28-intrusive-lists/` was untouched (`git diff --stat` empty
— `check.py` mutates a COPY under `.temp/clausemut/`), and
`.temp/t172/sweep2.sh` finished `p28…p49` **detached with `setsid`** so a second
kill could not reach it. **Every pattern was gated exactly once against the final
tree, and `--check-stale` reports `0 STALE` over all 66 records, which is the
independent check that no record is from a stale input.**

---

## Problems — ranked

| # | severity | finding |
|---|---|---|
| 1 | **major** | **`results/SYNTHESIS.md:1615-1620` prices the wrong repair.** *"the obvious repair (exact-match-first) moves 266 windows"* is candidate **B**, which `TASK_170` §43e said not to ship; it collapses onto an 8/11-instruction shim and **hard-fails stage 3a on 266 windows**. The correct repair (candidate C) moves **33 windows in 31 patterns**. Manager-owned. |
| 2 | **major** | **The re-measure price is 31 patterns, not 33.** `p02` and `p17` resolve `verus -O0 whole` correctly. `RECAP.md:30` and `TASK_170` §43f both say 33; `results/SYNTHESIS.md:1615` says *"33 cells"*, which is right for CELLS and is being read as patterns. |
| 3 | **major** | **`patterns/p16-tlv-walk/NOTES.md:577-582` still publishes the mis-resolved figures** — *"`vector_regs` is `[]` for **23 of the 32 cells**"*, *"The 9 exceptions"*, *"quote 23/32"* — where it is **22 and 10** (re-derived here, `.temp/t172/p05_vec.log`). `.memory/01-ladder.md:920-928` is already corrected and says p05 is not; after this task p05 **is**, and p16 is the last copy. ⚠ **NOT IN MY SCOPE** (the task named `p05` only), and it would have been **free on this sweep**. Exact replacement in *Memory updates*. |
| 4 | **major** | **`.memory/01-ladder.md:926-928` is now stale in the good direction**: it says *"`p05/NOTES.md` §1a is NOT yet corrected: it is a gate-hashed pattern doc, so the fix costs a sweep"* and *"say the source doc still disagrees"*. It is corrected and the sweep is paid. Manager-owned. |
| 5 | **minor** | **`RECAP.md:28`'s restored-limitation census does not add up**: *"only **10 of 33** rows have BOTH endpoints searched; **17** declare one side or an owed span; **2** declare NO SEARCH on either"* — 10 + 17 + 2 = **29**, and `SEARCH_NONE` has **3** members (p29 p32 p49), not 2. ⚠ **I did not re-derive the census**; I am reporting the arithmetic only. |
| 5b | **major** | **A gate-only `check.py` edit costs TWO CONTROL-GENERATOR RUNS on `p35`, and `PROTOCOL` rule 6's cost table does not say so.** `patterns/p35-*/controls/{proof_mutants,union_oracle}.json` pin `harness/check.py` in their own `derived_from_sha256`, so the edit staled them and **hard-failed stage 9c**. Found by the sweep, not predicted. **4 sidecars name `check.py`, 2 pin its hash, 1 pattern pays.** Rule-6 addition in *Memory updates*. |
| 5c | **minor** | **`check_marginal_ir`'s environment-block census names `p03 p04 p38 p46` for the `±7` `whole`-mode family and `p28` is a fifth member** — 4 `O3 whole` cells at exactly `−7.00` across this sweep. Same mechanism; the list is quoted as if closed. |
| 6 | **minor** | **`check.py::_clw` builds an `addrs` dict it never reads** — a leftover from the arm-layout fix in §A6. Harmless and test-only, and I did **not** fix it: `check.py` is gate-hashed, so a cosmetic edit made after the sweep started would stale all 33 records and cost the whole sweep again. **Fix it with the next `check.py` change.** |
| 7 | **minor** | The 40-line block comment I added to `check.py` cites `.temp/t172/callee_loop_probe.py` for its measured bounds. `.temp/` is gitignored, so a fresh clone cannot re-run it. The generator is committed-in-spirit only; `temp_citations.py` treats such citations as this repo's own and checks existence, which passes here. **Naming the alternative: the numbers are also in this report, which is committed.** |

---

## ✅ Clean negatives — attacks that did NOT land

1. **"The widening lets a panic path excuse a collapsed kernel."** Measured: **0
   of the 444 windows with a looping direct callee** has a
   panic/unwind/abort/assert callee. And p01's own panic path is an **indirect**
   `call *0x4398f(%rip)`, which is not a call target at all.
2. **"The widening lets `driver::load`'s I/O loop excuse a `whole` window."** It
   would — which is why the disjunct is `isolated`-only, and why that costs
   nothing (all 526 `whole` windows pass on the first disjunct).
3. **"A `rep.note` stales the rendered tables."** It does not: `RENDER_INPUT_KEYS
   = ("contract_sha256", "controls_json", "idiom_audit", "loud")`. `notes` is in
   the record and read by nobody (`grep` over `harness/` and `synthesis/`:
   `report.py:375` reads `loud`, never `notes`).
4. **"The `check.py` edit stales `synthesis/outward_ir.json`."** It does not —
   `TASK_170` re-pinned it to BUILD determinants; the run prints
   `outward-pin must-fire arms: 7/7 pass` and no STALE.
5. **"The `check.py` edit stales a measurement."** It does not:
   `--check-stale` reports **32 gate** records and **zero** measurement records
   (`check.py` is not in `measure.py::measurement_sources`).
6. **"`synthesize.py`'s `-O3 isolated` static census could be reading an `-O0`
   row."** It cannot: `grep -c '"O0"' synthesis/synthesize.py` → **0**, and the
   census filters `(c["cell"], c["opt"], c["mode"]) == (r, "O3", "isolated")`.
7. **"The `30 → 27` split change contradicts a published number."** It does not
   — nothing in `results/SYNTHESIS.md`, `RECAP.md` or `.memory/` quotes it.
8. **"The mis-resolution touches the `Ir` column."** It does not
   (`TASK_170` §43b, not re-derived here; `measure.py::_sum_rows` matches
   `(?:^|::)main(?:$|[^A-Za-z0-9_])` on demangled names and `driftsort_main` has
   `_` before `main`). ⚠ **Stated as inherited, not as my measurement.**

---

## Unsure / not done

1. ⚠ **The `check.py` repair is a NO-OP on today's tree and I landed it anyway.**
   The argument is in §A5/§A6: it is the precondition for the `asm.py` fix, it
   replaces a name list with a derived fact, and it ships with ten arms seen to
   fail. **A reviewer who thinks a prospective relaxation should not land before
   the fix it enables is making a defensible argument and I want it made.**
2. **Everything in step 4 ran, twice** — once at the end of the sweep and again
   after the `p35` repair, because `p35`'s records moved under it. Both passes'
   per-step `rc` files are in `.temp/t172/*.rc`; the second pass is the one
   quoted, and all six are `0`.
3. ⚠ **The `p35` failure was NOT predicted and my smoke test could not have
   found it** — I smoke-tested `p01`, which has no `controls/*.json` pinning
   `check.py`. `PROTOCOL` rule 6 says *"smoke-test one pattern before committing
   a tree-wide sweep"*; **it does not say which**, and one pattern cannot cover
   a per-pattern pin. ✅ **The cheap check that WOULD have found it is one
   `grep`** — `grep -l "harness/check.py" patterns/*/controls/*.json` — and it is
   now in *Memory updates* as a rule-6 row.
4. ⚠ **The sweep ran in two parts because the harness killed the first
   background job mid-`p28`.** Disclosed in full in *SWEEP RESULT*. Nothing was
   corrupted (`git diff --stat patterns/p28-intrusive-lists/` is empty) and
   `--check-stale` returns `0 STALE` over all 66 records, which is the
   independent evidence that every record is against the final tree.
5. **`outward_ir.json` is `-O3 isolated` only and I did not re-emit it.** 352
   callgrind runs, out of scope, and item A did not need it.
6. **I did not attempt a signature-based `BULK_REGIME` widening beyond the
   scoring in §B2.** My conclusion is that a routine-independent rule is not
   derivable from this sidecar (no byte count, per-routine crossovers). ⚠ **If
   that is wrong, the place to attack it is the claim that `(lo, hi)` cannot be
   inferred** — the sidecar does carry `outward_calls_per_kernel_call`, which I
   used only to check that the `_dl_runtime_resolve_xsavec` exclusion is by
   measurement (4e-05 calls/kernel-call) rather than by name.
7. **`WEAKER_ENDPOINT`'s membership is a judgement**, labelled as one in the
   code with its exclusions named. `p16` (*"THE R4 MOVER IS NOT A RUNG"*) and
   `p23` (*"the probes are gitignored scratch"*) are the two nearest misses and
   a reviewer could reasonably include either.
8. **I did not verify `TASK_170`'s claim that the `Ir` column is unaffected by
   the mis-resolution.** Inherited; clean negative 8 says so.
9. **`p16/NOTES.md` is left wrong** (problem 3). Scope, not judgement.

---

## PROTOCOL rule 2 — what this task refutes

**Launched from 948; reconciliation is the manager's job, not mine.** What I
refute, each with a run behind it:

1. **The call the task file named for attack** — *"the likely answer is that
   stage 3a is asking a `-O3` question at `-O0`"*. ⚠ **The CONCLUSION stands
   (the repair is in `check.py`); the MECHANISM does not.** `-O0` is not the
   discriminating variable — 261 of 263 `-O0 isolated` kernels carry their own
   back edge, and the class first bit at `-O3`. Acting on the stated mechanism
   would have relaxed the predicate on 526 windows to fix 1.
2. **`results/SYNTHESIS.md`'s *"the obvious repair … moves 266 windows"*** —
   that is candidate **B**, which `TASK_170` said not to ship and which
   **hard-fails stage 3a on all 266**. The correct repair moves **33**.
3. **`RECAP.md:30` / `TASK_170` §43f's *"33 re-measures"*** — it is **31
   patterns**; `p02` and `p17` are clean.

⚠ **Flagged, NOT re-derived, so not counted as a refutation:** `RECAP.md:28`'s
restored-limitation census sums to 29 over 33 and calls `SEARCH_NONE` two rows
where it has three.

---

## Memory updates

Nothing written to `.memory/` — subagents may not. The manager owes:

1. **`.memory/01-ladder.md:926-928`** — strike *"`p05/NOTES.md` §1a is NOT yet
   corrected: it is a gate-hashed pattern doc, so the fix costs a sweep"* and
   *"say the source doc still disagrees"*. It is corrected at TASK_172 and the
   sweep is paid. **Keep *"Quote the 22/32"*** — re-derived independently here:
   p16 is **10 of 32** with a vector register, 22 without.
2. **`patterns/p16-tlv-walk/NOTES.md:577-582`** — the last copy of the
   mis-resolved figures. Replacement, ready to paste:
   *"`vector_regs` is `[]` for **22 of the 32 cells** … The **10** exceptions
   are `['xmm']` and are all `whole`-mode `main` … quote 22/32."* ⚠ **It is
   gate-hashed, so it needs a p16 gate run** (≈7 min) — it would have been free
   on this task's sweep.
3. **`results/SYNTHESIS.md:1615-1620`** — the *"266 windows"* price is candidate
   **B**'s, and candidate B **hard-fails stage 3a on all 266**. The correct
   repair moves **33 windows in 31 patterns**; the re-measure is **31 patterns**,
   not 33.
4. ⚠⚠ **`PROTOCOL` rule 6's cost table — A NEW ROW, MEASURED HERE.** It says a
   `check.py` change costs *"a gate re-run"*, and `TASK_170` widened that to
   *"+ a render and a re-gate per pattern whose `loud` moves"*. **Neither covers
   a `controls/*.json` that pins `check.py`'s HASH.** Proposed row:

   > ⚠ **AND A `check.py` EDIT CAN COST A CONTROL-GENERATOR RUN, WHICH IS A
   > VERUS RUN.** `patterns/p35-*/controls/{proof_mutants,union_oracle}.json`
   > carry `harness/check.py` in their own `derived_from_sha256`, so a
   > gate-only edit stales them and **stage 9c hard-fails** on the two `STALE`
   > lines the render then adds. ✅ **Blast radius, measured at TASK_172:
   > `grep -l "harness/check.py" patterns/*/controls/*.json` returns FOUR
   > sidecars in three patterns, but only `p35`'s TWO pin the hash — `p23`'s
   > `controls_pin.json` and `p28`'s `repro.json` only mention the path, and
   > both gated `rc=0`.** Budget `+2 control-generator runs on p35` for any
   > `check.py` change; **no `report.py` is needed** — the render only differs
   > while the sidecars are stale.

5. **`.memory/03-measurement.md` / `check_marginal_ir`'s docstring** — the
   `±7` `whole`-mode census names `p03 p04 p38 p46`; **`p28` is a fifth
   member** (4 `O3 whole` cells at exactly `−7.00`, this sweep). The `p08`
   *"12 cells, a few hundredths"* figure reproduced **exactly, at 12**.

6. **`.memory/03-measurement.md`** — a new durable fact, if the manager wants
   it: *stage 3a has a THIRD disjunct, `check.py::callee_loop_witness` — the
   loop may be one DIRECT CALL away, `isolated` only, depth 1, symbol defined in
   the same binary. Reachable on 1 of 1052 windows today and unreachable until
   `asm.py`'s needle is fixed, which is why it carries 10 must-fire arms.
   `-O0` is NOT the discriminating variable: 261 of 263 `-O0 isolated` kernels
   carry their own back edge.*
7. **`RECAP.md:28`** — problem 5's arithmetic (10 + 17 + 2 = 29 over 33, and
   `SEARCH_NONE` has 3 members).
8. **`RECAP.md` finding 67(e) / the START HERE box** — item 43's `p05` half and
   the masked stage-3a failure are both closed; what remains open is the
   `asm.py` mis-resolution itself, now priced at **31 patterns**, and `p16`.

---

## Artefacts (`.temp/t172/`, all re-runnable)

| file | what |
|---|---|
| `stage3a_sweep.py` / `.json` / `.log` | the 1052-window resolution + stage-3a sweep |
| `callee_loop_probe.py` / `.json` / `.log` | the direct-callee-loop census that bounds the third disjunct |
| `candidates.py` / `.json` / `.log` | candidate B vs C blast radius |
| `candidateB_harm.log` | the 8/11-instruction shim and its stage-3a failure |
| `p01_witness.py` / `.log` | the end-to-end demonstration on the real binary |
| `arm_break.py` / `.log` | the 7 mutations; every arm seen to fail (`mut/` deleted — it is derived and `arm_break.py` rebuilds it) |
| `record_diff*.log`, `verdicts.log`, `finish.log` | the sweep's leaf-by-leaf diff, the verdict census and the step-4 rc table |
| `p35_union_oracle.log`, `p35_proof_mutants.log`, `p35b.done` | the p35 sidecar repair |
| `sweep2.sh` | the detached resume of the sweep after the harness killed the first job |
| `regime_probe.py` / `.log`, `regime_cut.log`, `avx2_peaks.log` | item B's derived censuses |
| `p05_vec.log` | p05's 20/32 and p16's 10/32, re-derived on the true windows |
| `p02_p17_clean.log` | why `p02` and `p17` escape the mis-resolution — a 7-instruction margin |
| `record_diff.py` | all 33 gate records, `HEAD` → tree, leaf by leaf, categorised |
| `verdicts.py` | verdicts/`blocked`/`failures` read from the 33 RECORDS + each `check.py`'s own rc |
| `sweep.sh`, `finish.sh` | the 33-pattern sweep and the step-4 gates, each rc captured separately |
| `itemC_arms.log` | item C's fail-closed arms |
| `check_stale.log`, `composition.log`, `synth*.log`, `gate/` | the gates |

⚠ **`mut/`** (the mutated `check.py` copies `arm_break.py` writes) is deleted
after the run — it is a derived artefact and `arm_break.py` regenerates it.
