# TASK_155 review report — `p34`, attacking the `0.00` gradient first

**Role: research reviewer.** Adversarial. I did not fix anything; nothing under
`patterns/`, `.memory/`, `RECAP.md` or `results/` was left modified. Every
command below was run; `git status --porcelain` is empty at the end of this
report and was verified empty after each of the four plants.

⚠ **`p34` STANDS as a row.** Nothing here is a reason to refuse, shrink or
retire it (`CLAUDE.md` rule 6), and item 1's C-mechanism distinction survives on
the only ground that could kill it. **What falls is a set of SENTENCES, and four
of the five worst are the MANAGER's, not the engineer's.**

---

## 0. Verdict per item

| # | item | verdict |
|---|---|---|
| 1 | the C-mechanism distinction | **SURVIVES, NARROWED** — but `CAVEATS["p34"]`'s *"ONLY THE ACQUIRE can be repaired"* is **FALSE**: I built a destroy-path repair that is checksum-identical to R1h on 8/8 inputs and ASan-clean. **M1** |
| 2 | `0.00 Ir` | **SURVIVES as a MEASUREMENT** — the plant moved the cell 34×, so it is not a plumbing tautology. **But *"0.00 BY CONSTRUCTION, not by measurement"* (commit `dd46507`, `CAVEATS["p34"]`) is refuted**: dead code on the never-taken DUP path moved the `-O3` marginal by −14.22 Ir/call. **M2** |
| 3 | no benign input executes the safety line | **SURVIVES**, now exhaustively: 33 628 000 streams + 200 000 random, zero counterexamples in either direction |
| 4 | the safe-arena / `Rc` claim | **branch B SURVIVES; branch A HALF FALLS.** `E0507`/`E0502` are non-distinguishing, `arm_safe_rc_borrow.rs` fails on the **NEW** path and fails identically with the DUP body deleted, and the hashed `why`'s *"a borrow cannot be stored in the stack array"* is **false — I stored one and ran it**. **B1** |
| 5 | the novelty derivation | **SURVIVES, NARROWED** — the engineer's derivation reproduces exactly. **The manager's `p38` is a filter artefact and the `75 cells across 20 patterns` figure is a different unit from the engineer's `31`.** **M3** |
| 6 | the flattering-direction trap | **SURVIVES a doubled search.** Two more in-contract R3 levers measured; the published `-O3` figure does not move. §5c's "the R4 side is the weaker endpoint" is at odds with §5d's "the C endpoint is the weakest". **m1** |
| 7 | `model.py` and entry 19 | **SURVIVES.** The six-cell arm reports rather than crashes when broken in **both** directions, and item 3's enumeration independently closes the engineer's own unreviewed LIFO argument |
| 8 | the R5 | **SURVIVES; one cross-row sentence FALLS.** Battery reproduces 6/6 byte-identical. **`X1 is p35's arm … on p35 it VERIFIED` is wrong**: p35's arm that verified is a *trusted-`requires`* deletion, and p34 **VERIFIES 24/0 on that too**. **M5** |
| 9 | `identity: norel` | **SURVIVES.** Layout, not drift — measured |
| 10 | positive controls and Miri | **SURVIVES.** Both controls fire only in their own detector on 4/4 lines; the Miri invocation has its `--` and the record's 8 runs carry real stdout |

**Severity roll-up: 0 blockers · 7 major (M1–M6, B1) · 8 minor (m1–m8).**
⚠ **Four of the seven majors are the MANAGER's and three are the engineer's.**
Manager: **M1, M2, M3** (all three in `composition.py`'s `CAVEATS["p34"]` and/or
`dd46507`'s message) and **M6** (the unwritten handoff). Engineer: **M4, M5,
B1**. ⚠ On M1, M2 and M3 the engineer's own text in
`spec.md`/`NOTES.md`/`README.md` is the *correct* version that the manager's
write-up strengthened or replaced — PROTOCOL rule 9's mechanism exactly.

---

## 1. Item 2 — the `0.00` gradient. It is NOT a tautology, and the manager's version of it is wrong

### 1a. Baseline reproduces exactly

`.temp/t155/marg.py`, the same difference-of-two-runs method
`check.py::check_marginal_ir` uses:

```
small.bin  O0 isolated  c-gcc       marginal=     3143.94
small.bin  O0 isolated  c-gcc-h     marginal=     3143.94
small.bin  O0 isolated  c-clang     marginal=     3130.64
small.bin  O0 isolated  c-clang-h   marginal=     3130.64
small.bin  O3 isolated  c-gcc       marginal=     2207.05
small.bin  O3 isolated  c-gcc-h     marginal=     2207.05
small.bin  O3 isolated  c-clang     marginal=     2226.78
small.bin  O3 isolated  c-clang-h   marginal=     2226.78
```

`NOTES.md` §5a to the last decimal.

### 1b. The static counts are exactly as reported — the binaries genuinely differ

`harness/asm.py stat`, pad-excluded:

| | R1 | R1h | Δ | NOTES §4b |
|---|---:|---:|---:|---|
| gcc `-O3` | 286 | 287 | +1 | +1 ✅ |
| clang `-O3` | 135 | 136 | +1 | +1 ✅ |
| gcc `-O0` | 218 | 223 | +5 | +5 ✅ |
| clang `-O0` | 203 | 208 | +5 | +5 ✅ |

### 1c. THE PLANT — three arms, `.temp/t155/plant.py`

Each plant edits `c/kernel_hardened.c`, rebuilds **only** `c-gcc-h`
(`--cell c-gcc-h --mode isolated`), re-measures, and restores in a `finally:`.
Restore verified **by bytes against `git show HEAD:`** on every arm
(`RESTORE: bytes == HEAD ? True`, `git status --porcelain: ''`).

| arm | what was planted | `c-gcc-h` small `-O0` | `-O3` |
|---|---|---:|---:|
| — | baseline | 3143.94 | 2207.05 |
| `hot` | a 500-iteration `volatile` loop **on the fold**, which every op runs | **87287.94** | **74287.83** |
| `dup` | the same loop **on the DUP path**, which no matrix input runs | 3143.94 | **2192.83** |
| `dup2` | ONE extra dead statement of the safety line's shape (`t->len = t->len + 1;`) | 3143.94 | 2207.05 |

**✅ CLEAN NEGATIVE — the `0.00` is not a fallback measuring `c/kernel.c` twice.**
The `hot` arm moves the cell by **34×**, so `c-gcc-h` really is built from
`c/kernel_hardened.c` and really is the binary whose `Ir` the record carries.
Do not re-run this attack.

### M2 (major) — *"0.00 BY CONSTRUCTION, not by measurement"* is refuted

`harness/tools/composition.py:193-196` and the commit message of `dd46507`:

> *"AND ITS BENIGN COST GRADIENT IS 0.00 **BY CONSTRUCTION, not by
> measurement**"*

The `dup` arm is the counterexample: a statement on the DUP path that **no
matrix input executes** moved the measured marginal of the *executed* paths from
`2207.05` to `2192.83` — **−14.22 Ir/call, −0.64 %**, at `-O3`. The construction
argument establishes that the *statement* is not executed; it establishes nothing
about the *number*, which is a codegen outcome.

⚠ **The engineer got this right and the manager made it stronger.** `spec.md`'s
own `why` says *"⚠ `0.00` IS STILL MEASURED AND NOT ASSUMED — R1h is a different
compiled function and a never-executed statement can still move layout, register
allocation and inlining"*, and `README.md:58` says *"`0.00` is a PREDICTION until
it is measured"*. **`composition.py` is the artefact the synthesis renders, and
it deletes the caveat.** This is PROTOCOL rule 9's exact shape — *the manager's
write-up made the claim STRONGER than the engineer had.*

✅ The `dup2` arm is the fair one and it reads **exactly baseline**, so the zero
is robust under a same-shape dead statement. The sentence that is true is the
engineer's: *predicted from the proof, then measured, and it held.*

---

## 2. Item 1 — the C-mechanism distinction

### ✅ It survives the only test that could kill it

`CLAUDE.md` rule 6 admits a kill on **C-side duplication of a BUILT row** alone.
Checked against the three nearest:

* **`p28`** — no reference count anywhere. Its free is *authorised* by the
  ownership (eviction) list and the dangling name lives in a **different**
  structure (the hash chain / `bucket[]`). `p34`'s free is **unauthorised** — a
  live entry of the **same** stack still names the object. Different C programs.
* **`p32`** — allocates nothing at all; no `malloc`, no `free`. Furthest row in
  the tree.
* **`p25`** (admitted, unbuilt, `.temp/mgr155/`) — **no duplication.** `p25`'s
  stale pointer is an *interior* pointer invalidated by a `realloc` **move**;
  there is no reference count and no explicit `free()` in the kernel, and its
  safety line is a **conjunct on the READ** (`curbase == toks`), i.e. `p27`'s
  repair site. `p34`'s is a **maintaining write on the ACQUIRE**. Build both.

### M1 (major) — *"ONLY THE ACQUIRE can be repaired"* is false

`harness/tools/composition.py:192-193`:

> *"p34's read path is correct by construction … so **ONLY THE ACQUIRE can be
> repaired**, an unbounded distance from the harm."*

I built the counterexample: `.temp/t155/csite/kernel_destroyfix.c` is
`c/kernel.c` with **the DUP path untouched** (still publishing an uncounted
reference, still no increment anywhere in the kernel) and the **release path**
deciding by a live-name scan instead of by `rc`:

```c
ntop = ntop - 1;
o = stk[ntop];
for (j = 0; j < ntop; j++)
    if (stk[j] == o)
        still = 1;
if (!still)
    free(o);
```

```
input                                      R1                    R1h          R1_destroyfix
adversarial-blind.bin     5576862673510090752    5576862673510090752    5576862673510090752  ==R1h
adversarial-blindread.bin 12442434272084377600  12442434272084377600   12442434272084377600  ==R1h
adversarial-many.bin       5628475829885786112    2893199866468423680    2893199866468423680  ==R1h
adversarial-recycle.bin   16102462438644451328    7544618244297525248    7544618244297525248  ==R1h
adversarial-stride3.bin                     0                      0                      0  ==R1h
degenerate.bin            12018165609759525888   12018165609759525888   12018165609759525888  ==R1h
large.bin                  7726184805965551230    7726184805965551230    7726184805965551230  ==R1h
small.bin                 13533250923909195085   13533250923909195085   13533250923909195085  ==R1h

ASan, adversarial inputs:  destroyfix rc=0 hits=0   on all five
                           R1 (bug)   rc=1 hits=1   on the four that fire
```

**A repair at exactly `p28`'s site works.** So the distinction is not *which
site can repair it* — it is **which site can repair it for free**:

```
  small.bin  kernel               marginal=     2207.05
  small.bin  kernel_hardened      marginal=     2207.05      <- acquire-side: +0.00
  small.bin  kernel_destroyfix    marginal=     2367.69      <- destroy-side: +160.64  (+7.28 %)
  large.bin  kernel               marginal=    11106.93
  large.bin  kernel_hardened      marginal=    11106.93
  large.bin  kernel_destroyfix    marginal=    13510.76      <- +2403.83  (+21.6 %)
```

⚠ **This is a BETTER headline than the one it replaces, and it is measured.**
*The acquire is the only site at which this program can be repaired at zero
benign cost; the destroy-side repair that achieves the same behaviour costs
7–22 % of the kernel* — because the scan runs on **every release** while the
retain runs only on a **DUP**, which no benign input contains. That also
explains *why* the acquire is idiomatic, which "only the acquire can be
repaired" asserted rather than explained.

⚠ The sentence appears **only** in `composition.py` — `spec.md` and `NOTES.md`
say the narrower and defensible *"no test the READ could grow would repair this
without becoming a liveness table"*, which stands.

---

## 3. Item 3 — the manager's own proof (PROTOCOL rule 3). It SURVIVES, exhaustively

`.temp/t155/dupproof.py` transcribes `c/kernel.c`'s R1 semantics — guards
included — and enumerates op streams, counting any read or write of a
freed object as a touch (`POP`'s `o->rc`, `READ`'s `o->data[0]`, the epilogue).
`READ`'s operand is enumerated over four reachable indices, so no READ shape is
missed, and `CAP` is varied so the `ntop < P34_CAP` guard is actually exercised:

```
cap= 2 done   cumulative streams=6725600
cap= 3 done   cumulative streams=13451200
cap= 4 done   cumulative streams=20176800
cap= 6 done   cumulative streams=26902400
cap=16 done   cumulative streams=33628000

streams examined: 33628000
COUNTEREXAMPLES  (executed DUP, zero freed-object touches): 0
COUNTEREXAMPLES  (no DUP but a freed-object touch): 0
random streams (200000, len<=60, cap=16): counterexamples = 0
```

✅ **CLEAN NEGATIVE, in both directions.** Every shape the task named was
covered and none of them lands: the `ntop < P34_CAP` guard (four small CAPs), an
early `break` on a short stream (every prefix is enumerated), a DUP whose object
is never released (impossible — the epilogue releases every written entry
exactly once, and an entry can only be overwritten *after* it is released),
stack exhaustion and `nops` overflow (both truncate the stream, which the
enumeration already covers). **Do not re-run this.**

✅ **`controls/no_dup.py` is a real derivation over the SHIPPED blobs**, not a
restatement of `gen.py`: it opens each `.bin` with `slb.read`, takes the stride
out of the payload, and walks with `model.py::window_ops` — the *rungs'* cursor,
`nops` and `len - p < 2` break included. Re-run: byte-identical output, and
`no_dup.json` differs from `HEAD` only in `measured_utc` (reverted).

---

## 4. Item 4 — the safe-Rust arms

### ✅ Branch B (the index arena) SURVIVES

The arena arm is an honest port, not a transliteration built to match: the two
properties that make it reproduce — a **LIFO** free list and `data` never
cleared on free — are both disclosed in the arm's own header (*"A FIFO free list
would not reproduce it and would be measuring a different allocator"*) and in
`NOTES.md` §8. The bit-for-bit table is corroborated independently by my own
build of `c/kernel.c` (§2 above): `16102462438644451328` for
`adversarial-recycle` under gcc `-O3`.

### B1 (major) — branch A's error codes are non-distinguishing, and one arm fails on the wrong line

The task asked for a control that **cannot** have the bug. Three, all built and
run:

**(a) The error CODES carry no information about reference counting.**

```
.temp/t155/ctl/e0507_nothing.rs   (12 lines, no Rc, no container, no refcount)
  error[E0507]: cannot move out of `*r` which is behind a shared reference
.temp/t155/ctl/e0502_nothing.rs   (a Vec, an immutable borrow, a push)
  error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
```

Both are the **same code and the same message shape** that
`safe_arms.py` records for the two arms, and `safe_arms.py` asserts `E0507`
explicitly (`want_code`). This is p25's `E0502` and p28's `E0382`/`E0499` for
the third time.

**(b) `arm_safe_rc_borrow.rs` fails on the NEW path, not the DUP path.** rustc
points at lines 68–69:

```
error[E0502]: cannot borrow `objs` as mutable because it is also borrowed as immutable
68 |   objs.push(Obj { rc: 1, len: DLEN, data: d });   <- mutable borrow occurs here
69 |   stk[ntop] = Some(&objs[objs.len() - 1]);       <- immutable borrow occurs here
```

**(c) With the DUP body DELETED it fails identically.**
`.temp/t155/ctl/arm_borrow_nodup.rs` replaces the whole DUP arm with the `SENT`
fallback — a program that publishes **no second reference at all** and therefore
cannot have `p34`'s bug — and produces the **same `E0502` at the same line 68**.

**(d) And the DUP line itself compiles.** `.temp/t155/ctl/borrow_dup_ok.rs`
takes `arm_safe_rc_borrow.rs`'s DUP body character-for-character —
`let t = stk[ntop - 1]; stk[ntop] = t;` — over a pre-built arena, and it
**compiles and runs** (`2 1`).

**So the hashed `why` is false where it says:**

> `spec.md`'s `slb-contract` `why`: *"…there is no way to obtain a second
> `Rc<Obj>` without it, and **a borrow cannot be stored in the stack array
> because the borrow checker ties it to the array it came from**."*
> `NOTES.md` §8 repeats it.

A shared borrow **can** be stored in the stack array, twice, and safe Rust is
happy. What safe Rust refuses is *mutating the owner while the borrows are
live* — which is a different fact, is what the arm actually measures, and is
arguably a **stronger** statement: the borrow route is closed not at the
duplication but at the point where any owner mutation (a `push`, and by
extension a free) would have to happen.

⚠ **This is PROTOCOL rule 6's known hole again (`p46`'s shape): the
`contract_sha256` disclosure verifies, and the hashed sentence is still false.**

⚠ **What SURVIVES, and it is most of branch A.** `arm_safe_rc_move.rs` is tight:
comment-stripped, its code diff against `safe_naive.rs` is **two lines**, the
DUP body, plus `#![forbid(unsafe_code)]`. The claim *"`Rc::clone` publishes and
counts in one operation and there is no way to obtain a second `Rc<Obj>` without
it"* is untouched by any of the above.

### M4 (major) — two "X measures Y" claims in measurement-hashed sources with no artefact behind them

1. **`controls/storage_arms.py` DOES NOT EXIST** and is cited twice, both times
   as the evidence for a claim:
   * `patterns/p34-refcount-stack/c/kernel.h:112` — *"…is what makes the storage
     choice load-bearing rather than incidental, and `../controls/storage_arms.py`
     **measures both sides of it**."*
   * `patterns/p34-refcount-stack/model.py:143` — *"`../controls/storage_arms.py`
     **measures that the real allocator agrees**."*

   `ls controls/*.py` → `detectors no_dup proof_mutants rust_bug safe_arms
   safety_line spellings`. Both files are in the gate record's
   `source_sha256`; `c/kernel.h` is also **measurement**-hashed.
   `harness/tools/temp_citations.py` cannot see this — it only audits `.temp/`
   paths — which is why it reports `OK`. The intended target is almost certainly
   `controls/safe_arms.py`.

2. **`controls/arm_safe_arena.rs:34` and `:92`** — *"`safe_arms.py` **records the
   high-water mark** so the headroom is a measured claim rather than an
   assumption."* `grep -n 'high-water\|high_water\|nfree' controls/safe_arms.py
   controls/safe_arms.json` → **no hits.** It is not recorded anywhere.

   ✅ The underlying claim is TRUE, and I measured it so the next agent does not
   have to (`.temp/t155/ctl/arena_hw.rs`, an instrumented copy):

   ```
   adversarial-blind/-blindread/-many/-recycle  max slots in use = 1
   adversarial-stride3                          max slots in use = 0
   degenerate, large                            max slots in use = 16
   small                                        max slots in use = 11
   ```

   `ARENA = 32`, worst case 16 = `CAP`, so the free list cannot underflow — with
   16 slots of margin.

---

## 5. Item 5 — the novelty derivation

### ✅ The engineer's half SURVIVES and reproduces

`.temp/t154/novelty.py`, re-run unmodified:

```
HALF 1 (fires & diverges & reproducible):  33 cells in the tree
  of which on a BUILT TEMPORAL row other than p34: 5
  [('p27','adversarial-uaf.bin'), ('p28','adversarial-many.bin'),
   ('p28','adversarial-uaf-head.bin'), ('p28','adversarial-uaf-read.bin'),
   ('p28','adversarial-uaf-write.bin')]
HALF 2 (the detector-ONLY pair):  6 cells in the tree
  of which NOT p34: 4 -> [('p18','adversarial-sat.bin'),
   ('p42','adversarial-mixed.bin'), ('p42','adversarial-notag.bin'),
   ('p42','adversarial-win1.bin')]
```

⚠ The report says `31`; it now reads `33`. That is **not** a defect: the
engineer's run predates `p34`'s own two triples. Worth a one-word note when the
number is quoted.

✅ **`p29` and `p32` fall out for the RIGHT reasons**, checked against the
records rather than assumed: `p29`'s three firing inputs each carry **4** distinct
behaviours across opt × mode, so they are not reproducible (which is `p29`'s own
published headline); `p32` has `fired=False` on every input, because it never
calls the allocator. Neither is a filter artefact.

### M3 (major) — the manager's `p38` is a filter artefact, and the `75` is a different unit

`harness/tools/composition.py:199-204` and the commit message of `dd46507`:

> *"…the other three rows holding such a cell are **p18, p38 and p42**"* and
> *"that combination holds in **75 cells across 20 patterns**"*.

**(a) `p38` does not have a detector-only cell.** It enters the list only if the
filter is applied **per (input × compiler) cell** — and then only through its
`c-clang` cell. Read straight out of the record:

```
p38  adversarial-huge.bin  fired=True  gcc:n=2 div=[True, False]        clang:n=1 div=[False]
p38  adversarial-oob.bin   fired=True  gcc:n=3 div=[True, True, False]  clang:n=1 div=[False]
```

**Under gcc, the checksum DOES discriminate on both inputs.** "The detector is
the only discriminator" is exactly what is false there. The per-cell filter lets
one compiler's agreement mask the other's divergence, and `len(rows) == 1` then
admits the clang cell and excludes the gcc one. The correct answer is the
engineer's: **`p18` and `p42`, two rows, not three.**

**(b) The `75` is a per-ROW count, the `31` is a per-INPUT count.** I reproduced
the manager's definition: counting `(input × compiler-cell)` pairs with
`len(rows) == 1` as the reproducibility proxy gives **74 across 20 patterns** —
one off the published 75, and 2.3× the engineer's figure for the same
derivation. Both are in the record; neither artefact says the denominator
changed. This is the "TWO DENOMINATORS" trap the engineer's own `NOTES.md` §10
flags for the TCB tally, one section over.

**(c) The `len(rows) == 1` proxy is weaker than the engineer's** and it changes
the answer: it is per-cell, so it never requires the two compilers to agree.
Engineer's definition → 33 inputs / 19 patterns; manager's → 41 inputs /
20 patterns.

✅ **What survives is exactly what the engineer published:** *`p34` is the first
TEMPORAL row with a detector-only cell, and it has two; the other rows holding
one are `p18` (`ub-not-mem`, UBSan) and `p42` (`resource`, LSan).*

---

## 6. Item 6 — the flattering-direction trap. ✅ The corrected figure SURVIVES a doubled search

`controls/spellings.py` varied **one** R3 lever. The `why` names the R3 walk as
free; two more levers are equally unpinned — nothing in `required`/`forbidden`
quotes them — and I searched both (`.temp/t155/r3spell.py`, `spellings.py`'s own
build/measure method, every variant checked against `model.py` on all 8 inputs):

| R3 variant | small `-O0` | small `-O3` | large `-O0` | large `-O3` | model |
|---|---:|---:|---:|---:|---|
| `r3_shipped` (calibration) | 8,243.33 | **2,558.38** | 38,129.31 | **12,623.43** | ok |
| `r3_read_unwrap` (R2's `as_ref().unwrap()` READ) | 8,342.87 | 2,558.38 | 38,653.11 | 12,623.43 | ok |
| `r3_take_none` (`stk[ntop] = None;` instead of `.take()`) | **8,231.11** | 2,562.99 | **38,060.57** | 12,656.30 | ok |
| `r3_both` | 8,330.65 | 2,562.99 | 38,584.37 | 12,656.30 | ok |

`r3_shipped` reproduces `NOTES.md` §5c to the decimal, which calibrates the run.

✅ **At `-O3` the shipped R3 is still the cheapest found over FOUR spellings**, so
the published `R3 − R4 = 193.79 / 716.71` figure **stands**. At `-O0`
`r3_take_none` beats shipped by 12.22 / 68.74 but is still far dearer than
`r3_cursor` (6,133.33 / 28,339.31), so the cheapest-found `-O0` figure does not
move either. **Clean negative — do not re-run.**
⚠ The in-contract R3 **span** widens at `-O0`: dearest-found is now
`r3_read_unwrap`'s 8,342.87 / 38,653.11, not the shipped cell.

### m1 (minor) — the two "weakest endpoint" sentences disagree

`NOTES.md` §5c: *"Which endpoint is the weaker-searched one: **THE R4 SIDE**"*.
`NOTES.md` §5d: *"the **C endpoint** is the weakest-searched of the four"*.
By lever count the R4 side was the **better**-searched of the two Rust endpoints
before this review (2 variants against R3's 1); §5c's answer is a *structural*
argument (an R4 candidate must also verify), not a count, and it does not say
so. A reader who stops at §5c gets the wrong endpoint.

### m2 (minor) — the `why` names an R3 lever that `required[6]` pins

`why`: *"WHAT IS DELIBERATELY NOT PINNED is how R3 walks the op stream —
`chunks_exact(2).take(nops)` against R2's cursor, **and `match c % 4` against
R2's `if` chain**."* `idiom.required[6].rust` in the same block: *"the opcode,
`c % 4`, in all four Rust rungs — spelled `c % 4 == 0` in R2, R4 and R5 and
**`match c % 4 {` in R3**, which is the R3 lever."* One says the dispatch form is
free, the other quotes it as R3's pinned spelling. The gate is green either way;
the two sentences cannot both be the reading.

### m3 (minor) — the cross-language ladder is `-O3` only and inverts at `-O0`

`NOTES.md` §5d publishes `C < R4 < R3 < R2` with three percentages, correctly
labelled `-O3`. At `-O0` the order is `C(3,143.94) < R4(5,631.32) <
R2(6,265.40) < R3(8,243.33)` — **R2 and R3 swap**, so *"`safe_naive` 8.87 %
dearer than `safe_tuned`"* becomes *24 % cheaper*. §5b states the reversal;
§5d does not cross-reference it, and §5d is the table a reader quotes.

---

## 7. Item 7 — `model.py`. ✅ SURVIVES, and the engineer's unreviewed argument is now closed

**The must-fire arm reports rather than crashes, in both directions.** Two
mutated copies of `model.py` under `.temp/t155/model/`:

```
arm "dead"  (Pool.touch never fires):
  detector_selftest returned 2 problem(s):
   - MUST-FIRE ARM DEAD: the `DUP POP POP` probe did NOT make the detector fire ...
   - MUST-FIRE ARM DEAD: the `DUP POP READ` probe did NOT make the detector fire ...
arm "loud"  (Pool.touch fires on everything):
  detector_selftest returned 4 problem(s):
   - fired on the `no-DUP` probe under the HARDENED semantics ...
   - the detector fired on the `no-DUP` probe under the BUGGY semantics, and that
     probe contains no DUP ...
shipped model:  detector_selftest -> []
```

**The engineer's flagged-as-unreviewed argument** — *"a window with a successful
DUP always fires because releases exceed credits by the DUP count; that argument
is mine and has not been reviewed"* — **is now proved**, by item 3's
enumeration. And the proof shows the argument does not depend on the LIFO
recycling at all: the *second* release of a DUP'd object reads `o->rc` out of a
freed block whatever the allocator does with the storage. Recycling decides
**which** access and **what value**; it cannot decide **whether**. So the
model/ASan-quarantine mismatch the engineer worried about affects only the part
the flag never claimed.

---

## 8. Item 8 — the R5

### ✅ Reproduces

* shipped `verus.rs`: `24 verified, 0 errors` (`./verus_run.py`, no flags).
* `controls/proof_mutants.py` re-run: **6 of 6 as expected, and
  `proof_mutants.json` is IDENTICAL to `HEAD` apart from `measured_utc`** —
  same verified/errors counts, same diagnostics. Reverted.
* `harness/vparse.axiom_decls` on `verus.rs` → `[]`; the record's
  `axiom_decls: {}`; `blocked []`, `failures []`, `verdict PASS`,
  `complete_run True`, read out of the record.
* `check.py::_assume_keyword_hits(verus.rs)` → `{}`, so *"no `assume(` or
  `admit(` anywhere in p34"* is verified with the gate's own scanner.

### M5 (major) — *"`X1` is `p35`'s arm … on `p35` it VERIFIED"* is false

`NOTES.md` §6c and `controls/proof_mutants.py`'s `X1` docstring:

> *"**`X1` is `p35`'s arm.** Strike the central obligation out of the invariant
> … **On `p35` the equivalent deletion VERIFIED** at the pinned obligation count,
> and only the `verus.items` pin caught it. **On `p34` it FAILS.**"*

Read out of `patterns/p35-tagged-union/controls/proof_mutants.json`:

| p35 arm | what it mutates | result |
|---|---|---|
| `M3-bug-order-both` | exec + the abstract machine | **15 / 1 — FAILS** |
| `M6-weaken-invariant` | **`wf_cell` weakened to `true`** — the invariant | **15 / 1 — FAILS** |
| `X1-delete-variant-requires` | **the correct-variant conjunct out of the three trusted readers' `requires`** | **16 / 0 — VERIFIES** |

**p35's invariant weakening FAILED too.** The arm that verified on p35 is a
deletion from a **trusted item's `requires`**, which is a different mutation
from p34's `X1`. So I ran p34's true analogue
(`.temp/t155/rmut.py`, `Z1`): delete `i < v@.len()` / `i < old(v)@.len()` from
**all three** trusted accessors, `buf_get_unchecked`, `arr_get_unchecked` and
`arr_set_unchecked`:

```
  Z1-delete-trusted-requires     24/0 rc=0 []
```

**p34 VERIFIES at the pinned obligation count on p35's actual arm.** The two
rows behave the *same*, not differently. The published sentence claims a
difference that does not exist for the arm it names.

⚠ **This is not a soundness hole in p34** — `verus.items` pins the clause text
and stage 5c-twin re-derives that each conjunct, deleted alone, makes its twin
fail; both catch `Z1`. It is a **wrong cross-row comparison in the pattern's
durable record**, and it is the kind that gets quoted.

⚠ **`X2` is loosely mapped too.** `p32`'s `M4-spec-weaken` weakens the exec code
and the **abstract machine `step`** — the SPECIFICATION. `p34`'s `X2` weakens the
exec code and the **loop invariant `wf`**. The *conclusion* (p32 verifies at
`15/0`, verified from `p32`'s own sidecar; p34 fails at `22/2`) is sound and the
mechanism the row gives for it is right — `run` has no reference count, so no
spec weakening can rescue the mutant and the failure is a linear-resource one.
But "X2 is p32's arm" is not literally true and §6c should say which object each
row weakened.

### m4 (minor) — p34's battery lacks the `assume(false)` arm that p35 ships

```
  Z2-assume-false                24/0 rc=0 []
```

`proof { assume(false); }` at the top of the kernel body verifies at the
**pinned** count, exactly as `p35`'s `M5-assume-false` does — invisible to the
obligation count, the clause pins and the identity pin. `p35` ships `M5` **and**
`M5b-gate-sees-it`; `p34`'s six-arm battery has neither.

✅ The gate does close it: `_assume_keyword_hits` on my mutant returns
`{'assume(': [827]}` and `spec.md` declares no `verus.assumptions`, so the run
would fail. **Clean negative on the soundness question; a real gap in the
battery.**

✅ **`Z3` — a `requires` nothing can discharge** (`len == 0, len == 1` added to
`kernel`) — correctly **fails**: `23 / 1`, `precondition not satisfied` at the
call site. The kernel is not dead or vacuous.

### m5 (minor) — `global layout` IS a gate hole, and rustc is the only net

Confirmed: `axiom_decls` matches `axiom fn`, `uninterp spec fn`,
`assume_specification`, `external_trait_specification`,
`external_type_specification` — and not `global layout`. p34 carries
`global layout Obj is size == 24, align == 8;`.

I pushed the engineer's defence harder than the engineer did — *does rustc check
a `global layout` on a type that is never used?* — with
`.temp/t155/verus/layout_unused.rs`, which declares a **lie** about a struct that
is never constructed:

```
verification results:: 1 verified, 0 errors
error[E0080]: evaluation panicked: does not have the expected size
```

✅ **rustc does check it, even for a dead type.** ⚠ **But Verus reports
`1 verified, 0 errors` and proves `size_of::<Dead>() == 999` from the lie.** So
the net is the *compiler*, and it is absent from every **verify-only** stage the
gate runs (`--verify-function` censuses, `--cfg slb_twin`, the clause-mutation
stages). Defensible on p34 because the `verus` cell is compiled and measured;
the engineer's "manager's call" framing is right and the answer should be
recorded with that scope.

---

## 9. Item 9 — `identity: norel`. ✅ Layout, not drift

```
                     n_raw  n_nopad  md5_raw   md5_raw_norel  md5_fn_norel  md5_norm
unsafe -O0-isolated   339     332    71e6bf08   48cb12fb       62654b4b      f83b7e28
verus  -O0-isolated   339     332    ea626e60   48cb12fb       62654b4b      f83b7e28
unsafe -O3-isolated   190     179    96a41f7b   a8fabad6       9f714c0f      353ee8b4
verus  -O3-isolated   190     179    4d791caa   a8fabad6       9f714c0f      353ee8b4

harness/asm.py diff (O3):  identical by raw bytes: False
                           identical with pc-rel fields masked: True
                           (normalised text identical)
```

The raw disassembly diff at `-O3` is **entirely** branch/call targets whose
symbol-relative offsets are identical (`+0x5a`, `+0x5e`, `+0xa7`, `+0xaa`, `+0xfe`
on both sides), the mangled symbol name, and **one** rip-relative field —
`lea -0xde08(%rip)` against `lea -0xdde8(%rip)`, **both resolving to `0x78f0`**.
The two kernels are `0x20` apart (`156ca` vs `156aa`), exactly as the pin's `why`
says. At `-O0` the calls still go to `core::slice::get_unchecked` on **both**
sides, so the exec code has not drifted. **The checklist question "does R5's
exec code actually match R4's" is answered: yes.**

### m6 (minor) — the `why` and the record quote two byte conventions

The `identity` pin's `why` says *"the same **688** bytes"*; the gate record's
verdict line says `678`. Both are right — `n_bytes` is the raw objdump extent and
`fn_bytes` the declared one (`688` / `678`, `pad_bytes = 10`) — but neither text
names its convention, which is the one thing `asm.py`'s own docstring asks for.

---

## 10. Item 10 — positive controls and Miri. ✅ SURVIVES

`controls/detectors.py` re-run in full; `detectors.json` is **IDENTICAL to
`HEAD` apart from `measured_utc`** (reverted). The licensing rows:

```
  ctl_asan.c     asan_gcc_O0 / asan_gcc_O3 / asan_clang_O0 / asan_clang_O3   rc=1 hits=3   FIRES 4/4
  ctl_asan.c     ubsan_* (4 lines)                                           rc=0 hits=0   silent
  ctl_asan.c     plain_* (4 lines)                                           rc=0 hits=0   silent
  ctl_ubsan.c    ubsan_gcc_O0/O3  hits=1     ubsan_clang_O0/O3  hits=2       FIRES 4/4
  ctl_ubsan.c    asan_*  (4 lines)                                           rc=0 hits=0   silent
  ctl_ubsan.c    plain_* (4 lines)                                           rc=0 hits=0   silent
```

**Each control fires in exactly the detector whose column it licenses and in no
other, on both compilers at both levels**, and clang has eliminated neither
(both fire under clang). This is the `p35`/`p25` gap closed properly.

**Miri is well-formed.** Both `check.py:8841` and `controls/rust_bug.py:155` pass
`... spath, "--", probe`; the `--` is present. The record's
`miri.runs` has **8** entries, one per input, each with a real `stdout` equal to
`model_stdout` and 0.1–0.3 s wall time — these are runs, not non-runs.
`required: true`, `ran: true`, `available: true`, no blocked row.

---

## 11. Deliverable 2 — **is `p34` FINISHED? NO.** M6 (major)

Gate-green is not finished; a pattern is finished when a reader can find its
result (PROTOCOL rule 1). Three artefacts say otherwise:

1. **`results/synthesis.md` (generated) does not carry `p34`.** Its own header
   reads **`Patterns: 30. Gate records: 30.`** while `ls results/gate/p*.json`
   is **31**, and `grep -o '\bp[0-9][0-9]\b'` over it lists every pattern
   *except* `p34`. It needs `synthesis/synthesize.py` re-run.
2. **`results/SYNTHESIS.md` (hand-written) does not mention `p34` at all** —
   `grep -n p34` → no hits. Its "⚠ A NOTE ON THE COUNT" block names the four
   rows landed since the 26-kernel corpus (`p29`, `p32`, `p28`, `p35`) and the
   temporal axis as *"one row to FOUR"*. It is one row stale, and commit
   `accc0bb` ("SYNTHESIS.md reconciled to 30 patterns") predates `dd46507`.
   The engineer was forbidden from touching it; it is owed.
3. **`RECAP.md` was not touched by `dd46507` at all**, and three of its
   statements are now false:
   * `RECAP.md:12` (the **START HERE box**) — *"⚠⚠⚠ **THE NEXT ACTION: WRITE AND
     LAUNCH THE `p34` BUILD (reference counting). Its task file does NOT yet
     exist.**"*
   * `RECAP.md:15` — *"Outcome 4 is `p34`, **still UNBUILT**"*
   * `RECAP.md:16` — *"FOUR of the seven are built and FOUR remain (`p34`,
     `p25`, and the two CVEs)"*

⚠⚠ **AND PROTOCOL RULE 1'S OWN CHECK GIVES A FALSE PASS HERE.** I ran the loop
verbatim and it prints nothing — no `MISSING: p34`. It passes because `p34`
appears **six times inside the findings section already**, in the *catalogue
re-adjudication* findings written while the row was still unbuilt
(`RECAP.md:3960` is `p34 — REFUSAL STANDS`, an entry that is itself retracted).
The check greps for a *mention*, and a row that was discussed for forty tasks
before being built is mentioned whether or not its result was ever written. It
caught `p19` and `p46` because those had **no** mention at all.
✅ **The check needs an anchor, not a mention** — e.g. require a findings-section
line that matches `p34` **and** a result token, or maintain the finding number
per pattern. Worth a line in PROTOCOL rule 1 beside the `basename` warning it
already carries.

✅ **The published table is current**: `harness/report.py p34 --stdout` diffed
against `results/tables/p34-refcount-stack.md` is identical apart from one
trailing newline the `--stdout` path adds.

---

## 12. Deliverable 4 — the engineer's disclosed gaps

### ✅ The `NOTES.md` revert is byte-complete

```
results/gate/p34-refcount-stack.json  n=49  MISMATCHED: []  MISSING: []
results/p34-refcount-stack.json       n=18  MISMATCHED: []  MISSING: []
```

`patterns/p34-refcount-stack/NOTES.md` is one of the 49 hashed sources and it
re-derives. The §14 slip is fully reverted. Re-derived again **after** all four
of my plants; both records still clean and `git status` empty.

### ✅ CLOSED: the two admissible R4 variants DO pair with their R5s

The engineer's open item 6 — *"'admissible' here means 'verifies', not 'verifies
AND pairs'"*. `.temp/t155/r4pair.py` applies `spellings.py`'s own substitutions
to **both** `unsafe.rs` and `verus.rs`, builds the R4 with `rustc` and the R5
with `verus_run.py --compile` at `harness/build.py`'s exact flags, and compares
with `harness/asm.py`:

```
  shipped        O0  identity=norel  raw=False norel=True fn_norel=True norm=True  n_raw=339/339  n_nopad=332/332
  shipped        O3  identity=norel  raw=False norel=True fn_norel=True norm=True  n_raw=190/190  n_nopad=179/179
  r4_checked     O0  identity=norel  raw=False norel=True fn_norel=True norm=True  n_raw=363/363  n_nopad=360/360
  r4_checked     O3  identity=norel  raw=False norel=True fn_norel=True norm=True  n_raw=204/204  n_nopad=192/192
  r4_readdirect  O0  identity=norel  raw=False norel=True fn_norel=True norm=True  n_raw=341/341  n_nopad=326/326
  r4_readdirect  O3  identity=norel  raw=False norel=True fn_norel=True norm=True  n_raw=190/190  n_nopad=179/179
```

**Both variants reach the SHIPPED pin's identity level (`norel`) at BOTH
optimisation levels, with identical instruction counts on each side.** So
`NOTES.md` §5c's caveat can be lifted: `p34` has **three** R4 spellings shown
admissible in the full sense — *verifies AND pairs* — and the measured R4-side
width (`53.02` / `267.42` at `-O3`, `404.00` / `2,009.60` at `-O0`) is a width
over genuinely admissible rungs. ⚠ `r4_readdirect` at `-O3` has the **same**
190/179 shape as shipped, which is why its marginal ties exactly.

### m7 (minor) — the contract-move disclosure is not independently verifiable

`python3 harness/tools/contract_diff.py p34` → `UNCHANGED`, block sha256
`f1537d7f…` on both sides. That confirms the *shipped* hash and nothing about
the move, exactly as the engineer said (`git show HEAD:` is vacuous on a
one-commit pattern).

I tried to verify the `1fa98c8a… → f1537d7f…` move by reconstruction: re-insert
the deleted conjunct `pt.0.addr() + size <= usize::MAX + 1` at **vstd's own
position** (`raw_ptr.rs:918`, second of five) in `rec_alloc` alone, in
`slb_twin_rec_alloc` alone, and in **both** (which `.temp/t154/NOTES.md:136` says
is what happened), at both span conventions — **six candidates, none matches**:

```
 +rec_alloc                     98e0f40d…   (span-1) c0c0f1b6…
 +slb_twin_rec_alloc            82d1f440…   (span-1) 86764837…
 +rec_alloc+slb_twin_rec_alloc  e813f0b0…   (span-1) 9af99dea…
 target                         1fa98c8a…   (span-1) 7216cbf1…
```

⚠ **This is NOT evidence of an undisclosed edit** — the block is ~30 KB of prose
and any character anywhere changes the hash, and several of its own fields
(`identity.why`, `miri.reason`, `obligations_note`) quote figures that may have
been reworded in the same pass. **It is evidence that PROTOCOL rule 6's snapshot
cannot be checked when the declaration moves**: a hash of a 30 KB blob is not
diffable and the preimage was not kept. ✅ **Cheap fix for the next pattern:
write the pre-edit block itself (or the `diff -u`) into `.temp/tNNN/`, not only
its hash.** Rule 6 already demands the hash *"the moment you first write it"*;
saving the text alongside costs one `cp`.

### Confirmed as disclosed, not re-run

* **No C-side spelling search.** Confirmed: the C endpoint has zero variants, and
  it is the weakest-searched of the four (`NOTES.md` §5d says so).
* **No `-O1` column.** Confirmed; the tree measures `-O0` and `-O3` and `-O1`
  appears only in `.temp/t154/repro_t154.log`.
* `harness/tools/composition.py --check` → **rc=0**, `OK: published composition
  table matches the tree (31 patterns, 10 classes)`. (Run without a pipe, per
  the task's warning.) `harness/tools/temp_citations.py` → rc=0,
  `OK (new=0 unclassified=0 resolved=6)`.

---

## 13. ✅ CLEAN NEGATIVES — attacks that did NOT land

Do not re-run these.

1. **`0.00` is not a plumbing artefact.** The hot plant moved `c-gcc-h` 34×
   (2,207.05 → 74,287.83). `c-gcc-h` is built from `c/kernel_hardened.c` and is
   the measured binary.
2. **The static `+1 / +1 / +5 / +5` deltas are exactly right** on both compilers.
3. **The no-benign-DUP proof is exhaustively true** — 33.6 M streams over five
   `CAP` values plus 200 k random streams to length 60; zero counterexamples in
   *either* direction. The `CAP` guard, the short-stream break, `nops` overflow
   and the never-released-DUP shape were all covered.
4. **`controls/no_dup.py` is a derivation over the shipped blobs**, using the
   rungs' cursor via `model.py::window_ops`, not a restatement of `gen.py`.
5. **`controls/proof_mutants.py` reproduces 6/6, byte-identical.**
6. **`controls/detectors.py` reproduces, byte-identical**, and both positive
   controls license exactly their own detector on 4/4 lines, both compilers,
   both levels, neither eliminated by clang.
7. **The Miri invocation is well-formed** and the record's 8 runs are real runs
   with `stdout == model_stdout`.
8. **`identity: norel` is link layout, not R4/R5 exec drift**, at both levels.
9. **The `-O3` `R3 − R4` figure survives a doubled R3-side search** (4 in-contract
   spellings instead of 2).
10. **`arm_safe_rc_move.rs` is a tight arm** — two code lines against
    `safe_naive.rs`.
11. **`p29` and `p32` fall out of the novelty lists for correct reasons**, not
    filter artefacts.
12. **`p34` does not duplicate `p25`, `p28` or `p32` on the C side.**
13. **`rec_alloc`'s remaining four `ensures`, the twin regime, `blocked []`,
    `axiom_decls {}`, 7 items / 5 in the regime / 5 twins** — all as reported,
    read out of the record.
14. **`model.py`'s six-cell arm reports rather than crashes** when the detector
    is killed *or* made to fire on everything.
15. **The published table matches a fresh `report.py --stdout` render.**

---

## 14. Findings, ranked

### blocker
None.

### major

* **M1 — `harness/tools/composition.py:192-193`.** *"ONLY THE ACQUIRE can be
  repaired"* is false; `.temp/t155/csite/kernel_destroyfix.c` repairs `p34` on
  the **destroy** path, matches R1h on 8/8 inputs and is ASan-clean, at
  **+7.28 % / +21.6 %** marginal `Ir`. Replace with the measured statement:
  *the acquire is the only ZERO-COST repair site.*
  **Failure scenario:** the sentence is what distinguishes `p34` from `p28` in
  the artefact the synthesis renders; a reader who checks it finds a
  counterexample in twenty minutes and disbelieves the row.
* **M2 — `harness/tools/composition.py:194-196` and commit `dd46507`.**
  *"0.00 BY CONSTRUCTION, **not by measurement**"* contradicts `spec.md`'s own
  hashed caveat and `README.md:58`, and is refuted by the `dup` plant
  (−14.22 Ir/call at `-O3` from dead code on the never-taken path).
  **Failure scenario:** the next pattern with a rarely-executed safety line
  quotes `p34` as licence to *declare* a zero instead of measuring one.
* **M3 — `harness/tools/composition.py:199-208` and commit `dd46507`.** `p38`
  is not a detector-only row (its `c-gcc` rows diverge on both firing inputs);
  it enters only under a per-cell filter that lets clang's agreement mask gcc's
  divergence. And `75 cells across 20 patterns` is a per-ROW count published
  beside the engineer's per-INPUT `31` with no note that the denominator moved
  (my re-derivation of the manager's definition gives **74/20**).
  **Failure scenario:** the synthesis's type/temporal axis discussion inherits a
  third row that does not have the property.
* **M4 — `c/kernel.h:112`, `model.py:143`, `controls/arm_safe_arena.rs:34,92`.**
  Three doc comments in **measurement-hashed** sources cite measurements that do
  not exist: `controls/storage_arms.py` is not a file (×2), and `safe_arms.py`
  records no high-water mark. `temp_citations.py` cannot see either because it
  audits `.temp/` paths only.
  **Failure scenario:** a reviewer who trusts the citation *instead of
  re-checking* — which is the whole point of a citation — accepts an unmeasured
  claim. The high-water claim happens to be true (I measured it: 16 of 32); the
  storage claim has no artefact at all.
* **M5 — `NOTES.md` §6c and `controls/proof_mutants.py`'s `X1` docstring.**
  *"`X1` is `p35`'s arm … on `p35` it VERIFIED … on `p34` it FAILS"*. `p35`'s
  invariant-weakening arms (`M3`, `M6`) both **FAILED** at `15/1`; the p35 arm
  that verified deletes a **trusted item's `requires`**, and on that arm **`p34`
  verifies too — `24/0`** (`.temp/t155/rmut.py Z1`). The cross-row difference the
  row publishes does not exist for the arm it names.
  **Failure scenario:** a three-row R5 comparison in the durable record is
  wrong, and it is the sentence `p34` uses to claim its proof is stronger than
  `p35`'s.
* **M6 — `results/synthesis.md`, `results/SYNTHESIS.md`, `RECAP.md:12,15,16`.**
  `p34` is **not FINISHED**: the generated synthesis still says
  `Patterns: 30. Gate records: 30.` against 31 records and omits `p34`; the
  hand-written one never mentions it; and the START HERE box still names writing
  the `p34` build task as the next action. ⚠ **PROTOCOL rule 1's own check gives
  a FALSE PASS**, because `p34` is already mentioned six times in the findings
  section by the *pre-build* catalogue entries.
  **Failure scenario:** exactly `p19`'s and `p46`'s — the gate is green, the
  reports exist, and the artefact a reader opens has no entry — except this time
  the loop that was added to catch it does not fire.

* **B1 — `spec.md`'s hashed `why`, `NOTES.md` §8, `controls/safe_arms.py`.**
  Three separate defects in branch A, detailed in §4:
  (a) the hashed `why`'s *"a borrow cannot be stored in the stack array because
  the borrow checker ties it to the array it came from"* is **false** —
  `.temp/t155/ctl/borrow_dup_ok.rs` stores a second `&Obj` into the stack array
  and runs;
  (b) `arm_safe_rc_borrow.rs`'s `E0502` is raised at lines 68–69, the **NEW**
  path, and is **byte-identical with the DUP body deleted**
  (`.temp/t155/ctl/arm_borrow_nodup.rs`) — a program that cannot have `p34`'s
  bug prints the same error;
  (c) `E0507` and `E0502` are printed by 12-line programs with no `Rc`, no
  container and no reference count, so `safe_arms.py`'s `want_code = "E0507"`
  assertion carries no information about reference counting.
  **Failure scenario:** the row's safe-Rust headline is *"both branches of the
  law in one row"*, and half of branch A rests on an error code that a `Vec`
  push produces. This is the third time this project has published a
  non-distinguishing rustc error (`p25`'s `E0502`, `p28`'s `E0382`/`E0499`), and
  the first time on a **hashed** sentence — PROTOCOL rule 6's known hole
  (`p46`'s shape) again.
  ✅ What survives: `arm_safe_rc_move.rs` is tight (two code lines against
  `safe_naive.rs`) and the `Rc::clone`-publishes-and-counts claim is untouched.

### minor

* **m1** — `NOTES.md` §5c vs §5d name different "weakest-searched endpoints".
* **m2** — the `why` calls `match c % 4` a free R3 lever; `required[6].rust`
  quotes it as R3's pinned spelling.
* **m3** — `NOTES.md` §5d's cross-language ladder inverts at `-O0` (R2 and R3
  swap) and does not cross-reference §5b, which says so.
* **m4** — the mutation battery lacks the `assume(false)` arm and its gate-side
  half that `p35` ships (`M5`, `M5b`). Measured: `p34` verifies `24/0` with it,
  and the gate scanner does catch it.
* **m5** — `global layout` is a sixth body-less axiom-exporting form
  `vparse.axiom_decls` cannot see. rustc checks it *even on a never-constructed
  type* (measured), but **Verus itself accepts the lie and reports
  `1 verified, 0 errors`**, so the net is absent from every verify-only gate
  stage. Manager's call, as the engineer said — with that scope.
* **m6** — the `identity` `why` quotes `688` bytes (raw extent) where the record
  quotes `678` (declared extent); neither names its convention.
* **m7** — the `1fa98c8a… → f1537d7f…` contract move is not independently
  verifiable; six reconstructions fail. Keep the pre-edit **text**, not only the
  hash.
* **m8 (tree-wide hygiene, not `p34`'s)** — `controls/*.json` sidecars are
  tracked and carry a `measured_utc`, so **running any control dirties the
  working tree** with a timestamp-only diff. Three of mine did
  (`no_dup`, `detectors`, `proof_mutants`); all reverted, and all were otherwise
  byte-identical. A reviewer who does not notice can leave a spurious diff, and
  a reviewer who does notice cannot tell it from a real one without diffing.

---

## 15. What I did NOT do

* **No full `harness/check.py p34` run.** I re-derived the stages that carry the
  row's claims — the mutation battery, the detector battery, the identity pin,
  the marginal `Ir`, `no_dup`, the Miri record, `axiom_decls`, the `assume`
  scan, `composition.py --check`, `temp_citations.py`, `contract_diff.py`,
  both records' `source_sha256` — rather than spending 30+ minutes re-running a
  gate whose record I would then have had to restore. **A full re-gate is still
  owed by someone** and is the one thing here that is unmeasured end to end.
* **`controls/spellings.py` was not re-run as a whole** (Verus runs plus
  callgrind). Its shipped-R3 row is reproduced exactly by `.temp/t155/r3spell.py`
  and its two R4 variants are re-derived and extended by `.temp/t155/r4pair.py`.
* **No C-side spelling search.** Out of scope for a review; it remains the
  weakest endpoint and the engineer says so.
* **No sweep-input work, no wall-clock work.** Every number here is `Ir` or a
  digest.
* **`.memory/`, `RECAP.md`, `results/SYNTHESIS.md`, `patterns/p34-*/` and
  `pilot/` were not edited.** No `git add`, no `git commit`. Earlier
  `.temp/t*/` and `.temp/mgr*/` directories were read and copied from, never
  modified.

**Everything under `.temp/t155/`**: `NOTES.md` (the running log), `marg.py`,
`plant.py`, `dupproof.py`, `rmut.py`, `r3spell.py`, `r4pair.py`, the `ctl/`,
`csite/`, `model/`, `mut/` and `verus/` probe sources, and the `.json`/`.log`
evidence. Every binary and `.bin` is deleted and re-derivable from the scripts
beside it (`CLAUDE.md` rule 1).

---

**PROTOCOL rule 2 running count: launched from 882, and this review adds SEVEN
claims contradicted by measurement** — *"only the acquire can be repaired"*
(refuted by a built, measured C program), *"0.00 by construction, not by
measurement"* (refuted by the `dup` plant), *"p18, p38 and p42"* (p38 is a
filter artefact), *"a borrow cannot be stored in the stack array"* (refuted by a
compiling, running program), *"on p35 the equivalent deletion VERIFIED"* (p35's
invariant arms failed; p34 verifies on p35's real arm), *"`safe_arms.py` records
the high-water mark"* (it does not — I measured it instead), and
*"`controls/storage_arms.py` measures both sides of it"* (the file does not
exist). **Running count: 889.** ⚠ Five of the seven are the manager's, two the
engineer's. **Reconciliation across branches is the manager's job, not mine.**
