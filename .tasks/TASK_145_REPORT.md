# TASK_145 — review of `p32`/`p33` (`patterns/p32-free-list-pool/`, built at `TASK_144`)

**Role: research reviewer.** I did not fix anything. `patterns/p32-free-list-pool/`,
`.memory/`, `RECAP.md` and `results/SYNTHESIS.md` were **not edited** — verified by
`git diff --stat HEAD -- patterns/p32-free-list-pool/ .memory/ RECAP.md` (empty). No
`git add`, no `git commit`. Scratch is `.temp/t145/` only; no `/tmp` file was written.
Verus ran only via `./verus_run.py`, single-file, never `--cargo`. Every sanitiser run
had `LD_PRELOAD` unset (it is set on this box:
`LD_PRELOAD=/usr/libexec/coreutils/libstdbuf.so`) and no sanitiser log was truncated.

---

## VERDICT

**`p32` STANDS. No blocker. The row is not refusable on any ground available to me:
its C mechanism is the only free list in the tree, and it is the only row that can
double-free.** Four **major** findings, all of them **claims about evidence rather than
wrong measurements** — every headline number in the pattern reproduced, three of them
against implementations I wrote myself.

⚠ **The sharpest one: `model.py` does NOT derive the sanitiser silence. The check that
is supposed to derive it cannot fire.** That sentence is inside the **hashed** contract
fence, in `README.md`, in `NOTES.md` 2a, in the property's own docstring, in
`TASK_144_REPORT` §4 **and in `RECAP` finding 55**.

---

## 0. ⚠⚠ PROCESS: THE TREE CHANGED UNDER ME, MID-REVIEW

`git status --porcelain` was **clean** at the start of this task. It now reads:

```
 M results/SYNTHESIS.md          <- NOT MINE
```

`stat` puts the modification at **2026-08-30 07:03:57 UTC**, roughly 13 minutes after my
gate run finished and while I was reading `model.py`. The diff is 27 added lines of
hand-written §0/§7 prose about `p32`, including the sentence *"Its review (`TASK_145`)
had not reported when this paragraph was added"* — so it is **the manager writing
`SYNTHESIS.md` concurrently with the review it is waiting on**. Nothing I measured reads
that file (my `synthesis.md` freshness check is the **lower-case, generated** one, last
written 05:58 and untouched), so **no result here is affected**. But my task file's first
hard constraint is *"You are the ONLY agent running"*, `PROTOCOL.md` says *"Only one
agent works at a time"*, and this is the configuration `PROTOCOL` rule 11 already has a
scar from. **I did not revert it — I am forbidden to edit that file.** Recording it
because a reviewer who cannot trust the tree to hold still cannot certify a byte
comparison, and I made four of them.

The one file I did modify, `results/gate/p32-free-list-pool.json` (a necessary
consequence of running the gate), was **restored and byte-verified against HEAD**:

```
git show HEAD:results/gate/p32-free-list-pool.json | sha256sum
38c461ae39cad37e4821ee45eccdc8e64ad8ad2e6577b4f2737f7e4b76a3cb52  -
38c461ae39cad37e4821ee45eccdc8e64ad8ad2e6577b4f2737f7e4b76a3cb52  results/gate/p32-free-list-pool.json
```

Before restoring it I diffed my run's record against the committed one leaf by leaf:
**2 of 1318 leaves differ, both `/miri/runs/N/seconds`.** The gate record reproduces.

---

## 1. THE C-MECHANISM DISTINCTION — **SURVIVES**

**Attacked as instructed. It does not fall, and the tree-wide greps are one line each.**

```
grep -l 'free list\|freehead\|free_list' patterns/*/c/kernel.c   -> p32 ONLY
grep -c 'free('                          patterns/*/c/kernel.c   -> p27:2  p29:2  p42:2
```

**`p32` is the only row in 28 with a free list, and the only row that recycles.** p27's
`ntab` and p29's `ntab` are monotonic by construction.

**The decisive measurement is the detector families the two built temporal rows can
produce.** Read out of their own committed gate records:

```
p27-handle-table      {'heap-use-after-free': 3}
p29-bst-delete        {'heap-use-after-free': 3}
p32-free-list-pool    {}                       (its malloc CONTROL: attempting double-free)
```

**Neither built row has ever produced a double free, on any input, in any recorded run.**
p27 cannot: `live[h] == 1` is on its FREE path (`p27/c/kernel.c:91`). p29 cannot: every
walk that reaches the `free(tab[cur])` at `p29/c/kernel.c:198` is guarded by
`live[cur] == 1`, and the epilogue frees only `live[j] == 1`.

**And I confirmed the harm exists in the shipped tree rather than taking the prose for
it.** `.temp/t145/alias_probe.py` is an independent replay of `c/kernel.c`'s R1 semantics
written from the C source (not from `model.py`), instrumented with a proper liveness test
— *two DISTINCT registers `q1 != q2` with `regs[q] != NIL` and `regg[q] == gen[regs[q]]`
naming the SAME slot* — plus a visited-set walk of `nx[]`:

```
input                        win  R1 vs R1h  cyclic  aliasing  round-trip
adversarial-alias.bin          1    DIVERGE    1/1      1/1        1/1   slot 0, regs (2,3)
                                     WRITE via r2 -> READ via r3 = 245  matches
                                     WRITE via r3 -> READ via r2 = 210  matches
adversarial-doublefree.bin     1    DIVERGE    1/1      1/1        0/1
adversarial-many.bin           1    DIVERGE    1/1      1/1        1/1
adversarial-recycle.bin        1    DIVERGE    0/1      0/1        0/1
adversarial-stale-read.bin     1    DIVERGE    0/1      0/1        0/1
degenerate / large / small          identical  0        0/73                <- benign: NONE
```

**The aliasing is real, it is on the shipped inputs, it reaches the checksum through a
write/read round trip, and it never happens on a benign input.**

### ⚠ The narrowing, and it is the honest half

**The task file's suspicion is correct about the READ arm.** *"Two bug classes, one
omitted conjunct, selected by the input"* is `p29`'s sentence, and `p32`'s
**use-after-recycle** half **is** `p29`'s recycle half as an abstract harm — in bounds,
storage the program still owns, occupant changed, every detector silent.
`NOTES.md` 2 concedes this in terms (*"that is `p29`'s recycle class arriving on
unrelated code"*), which is the right way to ship it.

**What is NOT duplicated, and what the row therefore rests on:**

| | `p29` | `p32` |
|---|---|---|
| the OTHER bug class | a dangling read, ASan-visible | **a double PUSH → a self-looping list → two live handles on one block.** No analogue. |
| what selects the class | the SHAPE OF THE TREE (0/1 vs 2 children) | the **OPCODE** (FREE vs READ) |
| R1 reproducibility | **20 distinct in 20 runs** on three inputs | **1 distinct in 20** on all nine (§6) |
| what is corrupted | one saved pointer | **the ALLOCATOR's own invariant** |

⚠ **And the closest genealogical link is in neither file's comparison.** `p27`'s own
`c/kernel.c:24` says *"Real handle tables carry a generation counter for exactly this
reason; `live[]` is that counter **with slot reuse removed**, which reduces it to one
bit."* **`p32` is that sentence run backwards.** The relationship is real, it is the
strongest form of the duplication attack, and `p32`'s "why it is not p27" block does not
mention it. It still does not carry: restoring reuse adds an intrusive free list, an
unbounded counter, pool storage with no allocator call, a FREE path that is itself a bug
site, and a harm p27 cannot reach. **But the argument would be stronger for saying so.**

---

## 2. THE HEADLINE'S CONTROL — **SURVIVES, NARROWED**

**The headline reproduces, on a re-run from `.temp/t145/ctl/` so the shipped sidecar was
not rewritten: `safe Rust == the C arena rung on 10 of 10 (input, arm) cells`, positive
control FIRED in 10 of 10 C builds.**

### 2a. ⚠ The two cells do NOT differ only in storage — measured, not argued

`cc -E -P` of `arm_malloc.c` with and without `-DP32_ARENA`
(`.temp/t145/arena.i` vs `.temp/t145/malloc.i`, 592 vs 628 lines). The **complete**
difference, per arm:

1. `uint8_t pool[8*4]` → `uint8_t *blk[8]`;
2. init: zero the pool → `blk[j] = NULL`;
3. ALLOC: `+ blk[s] = malloc(4); if (blk[s] == NULL) abort();`
4. the payload accessor, `&pool[s*4]` → `blk[s]`;
5. FREE: `+ free(blk[h]);`
6. ⚠ **a 17-line TEARDOWN BLOCK with no arena counterpart**, which itself calls `free`.

The free list, the generations, the handle registers, the guard chain, the fold and the
safety line are byte-identical — **the enumerated claim in `NOTES.md` 2 is exactly true.**
The shorthand *"storage the only variable"* (`storage_arms.py`'s title, `README.md`,
`c/kernel.h`) is not, and item 6 is the one that could have mattered, because the
teardown's own comment says it *"frees them a SECOND time"* under the buggy arm.

### 2b. ✅ The `malloc` arm's abort IS the bug — ASan frames, read whole

```
adv-doublefree / adv-alias
  ERROR: AddressSanitizer: attempting double-free
    #1 k_bug .../arm_body.inc:112        <- free(blk[h]) IN THE OP LOOP, the stale FREE
  freed by thread T0 here:
    #1 k_bug .../arm_body.inc:112        <- the same line, the first FREE
adv-stale-read
  ERROR: AddressSanitizer: heap-use-after-free
    #0 k_bug .../arm_body.inc:119        <- v = P32_PAY(h)[1], the stale READ
```

`arm_body.inc:148` is the teardown's `free(blk[j])` and **appears in no trace**. The
aborting runs never reach it. **The abort is the safety line's absence and nothing else.**

### 2c. ⚠ `storage_arms.py`'s docstring says its `c-arena` arm is something it is not

> *"`c-arena` — **the SHIPPED C kernels, R1 and R1h, exactly as `harness/build.py` builds
> them**"*

`build()` compiles `arm_malloc.c` with `-DP32_ARENA` and **never compiles
`c/kernel.c`**. An inline comment 100 lines lower says the truth; the docstring a reader
starts at does not. That is `PROTOCOL` rule 13's *"only the body gets maintained"* shape,
and it matters because the headline is a claim about **the shipped rung**.

**I closed the gap by measurement** (`.temp/t145/shipdrv/main_hex.c` drives the SHIPPED
`c/kernel.c` and `c/kernel_hardened.c` on the control's own op streams):

```
input             shipped c/kernel.c    control c-arena bug     shipped hardened   control c-arena fix
benign             72356755880000075     72356755880000075     72356755880000075   72356755880000075  OK
adv-stale-read                 32521                 32521                 38535               38535  OK
adv-recycle                 29797947              29797947              30032431            30032431  OK
adv-doublefree           28444101123           28444101123           35593523088         35593523088  OK
adv-alias               895071855618          895071855618        7765691657627       7765691657627  OK
mismatches: 0
```

**10 of 10. The headline transitively holds for the shipped rung. Only the docstring is
wrong.**

### 2d. ✅ `NOT REPRO` is confirmed, and a fifth value

My re-run's `adv-stale-read / c-malloc / plain` cell is **35962**. The record so far:
`33172 / 33203 / 34629` (the engineer), **`35094` (the manager, RECAP 55)**, `35962`
(me). See §9.

---

## 3. VACUITY AND THE ATTACK ARM — **SURVIVES**, and I found a cell the battery lacks

**`M1` and `M4` replicated with my own substitutions** (`.temp/t145/replicate_m1_m4.py`,
so `controls/proof_mutants.json` was not rewritten):

```
R-M1-exec-only        expect=fail   got=fail   OK  14/1  ['assertion failed']
R-M4-exec-and-spec    expect=verify got=verify OK  15/0  []
```

**The R5 headline stands: deleting the conjunct from the exec code AND from `step`
verifies `15/0`.**

**The arms the battery does not have** (`.temp/t145/extra_mutants.py`, all at
`--rlimit 200`, ~2 s each):

| arm | what it is | expect | got | diagnostic |
|---|---|---|---|---|
| `X0-control` | the shipped file | verify | **verify** `15/0` | — |
| `X1-requires-false` | ⚠ **a `requires` nothing can discharge** | fail | **fail** `14/1` | `precondition not satisfied` **at `main`'s call site** |
| `X2-ensures-true` | ⚠ **a postcondition true of every program** | fail | **fail** `14/1` | `assertion failed` — `main`'s ghost consumer |
| `X2b` | the same, **plus** `main`'s ghost `assert` deleted | fail | ⚠ **verify** `15/0` | — |
| `X3-spec-only-weaken` | ⚠ **a postcondition true of the WRONG program**: delete `st.gen[h] != g` from `step` ONLY, exec code intact | fail | **fail** `14/1` | `assertion failed` |
| `X4-assume-false` | ⚠ **an unreachable body**: `assume(false)` at the top of `kernel` | fail | ⚠ **verify** `15/0` | — |
| `X5-disjunctive-ensures` | `M2`'s constant body + `ensures … \|\| r == 0` | fail | **fail** `12/1` | `assertion failed` |

**Three results:**

1. ✅ **The shipped R5 is NOT vacuous.** An unsatisfiable `requires` is caught **at the
   call site**, and a trivialised `ensures` is caught by `main`'s ghost
   `assert(r == pool_fold(…))`. Both were open questions; both are clean negatives.
2. ✅✅ **`X3` is the third cell of `M1`/`M4` and it completes the finding.** Delete the
   conjunct from exec → **fail**. From spec → **fail**. From **both** → **verify**. So
   `step`'s conjunct is **not inert** and the two sides are genuinely tied to each other;
   `M4` is not "the proof does not care", it is exactly *"the safety line is load-bearing
   against the specification and against nothing else"*. **The report's wording is
   right, and this is the missing arm that proves it rather than asserting it.**
   Recommend `controls/proof_mutants.py` gain this arm.
3. ⚠ **`X2b` and `X4` both verify at `15/0` — the SAME counts as the shipped file — so
   the obligation count is not a discriminator.** What stops each in the shipped tree:
   * `X2b` → **`check.py` FAILS it**: `spec.md` pins `verus.items["verus.rs"]["kernel"]["ensures"]`
     and drift is `rep.fail("proof-pin", …)` (`harness/check.py:4655–4700`). Defended.
   * `X4` → **`check.py` only SHOUTS.** `_axiom_keyword_shout` (`check.py:4453`) prints
     `[tcb-axiom] … assume( appears 1x` and the gate still PASSES. **Not a p32 defect —
     `grep -c 'assume(\|admit(' verus.rs` is 0 — but it is the engineer's own
     `TASK_144_REPORT` defect 4 in a second shape: *vacuity is a shout, not a failure*.**

---

## 4. `model.py`'s INDEPENDENCE — **SURVIVES, NARROWED**, and one MAJOR claim falls

### 4a. ✅ The independence itself is real, and I proved the model right a third way

The simulation decides staleness by **Python object identity**
(`handle is pool.live[handle.slot]`), the rungs by an integer compare, and the free list
is a **successor map** walked with a visited set. That is a genuine second shape.

**And I did not take the model's word for the answers.** `.temp/t145/driver_replay.py`
replays `spec.md`'s driver loop over my own from-the-C kernel — a **third**
implementation — for all nine inputs:

```
adversarial-alias.bin        R1=4541033225001543680   R1h=8618832246808763392   DIVERGE
adversarial-doublefree.bin   R1=2953773168956931072   R1h=7694399416035917824   DIVERGE
adversarial-many.bin         R1=18212399140656900096  R1h=15810558800354073600  DIVERGE
adversarial-recycle.bin      R1=3411532910145854464   R1h=408677925675887616    DIVERGE
adversarial-stale-read.bin   R1=3149539478886544384   R1h=16295453347298233344  DIVERGE
degenerate.bin               R1=R1h=9306778758387801088
large.bin                    R1=R1h=12301318280131401366
small.bin                    R1=R1h=7818319352111584483
```

**Every one matches the gate record's `stdout` (R1) and `model_stdout` (R1h) exactly.**
And the record shows the six non-R1 rungs agreeing with `model.py` **on the adversarial
inputs too** — those rows are recorded, not skipped (`skipped_inputs: []`).

### 4b. ⚠⚠ MAJOR — `sanitizer_expect` is NOT a derivation. The check cannot fire.

The claim, in the **hashed** `idiom.why`, in `README.md`, in `NOTES.md` 2a, in
`sanitizer_expect`'s own docstring, in `TASK_144_REPORT` §4 and in **`RECAP` finding 55**:

> *"`model.py` **DERIVES** that silence rather than declaring it: its simulation computes
> **every index the buggy rung would compute** and reports whether one escapes."*

`.temp/t145/touch_probe.py`:

```
1. 20000 random buggy windows: Pool.oob fired 0 times
2. `Block(` construction sites in model.py: 1   (`blk = Block(s)` in Pool.alloc, s = self.pop())
   `_touch(` call sites: 2 -- both `self._touch(blk.slot)`, in Pool.read and Pool.write
3. Pool().read(Block(255)) RAISED IndexError: list index out of range
   `_touch` had set oob = True, but the very next line indexes `self.mem[255]` and throws,
   so `sanitizer_expect` never gets to return 'fires' -- the model CRASHES instead.
4. an empty handle register is `None`, never slot 255, so M3-nil-test's failure mode is
   outside this simulation's state space.
```

**Four ways this is not a derivation:**

* `_touch` only ever sees `blk.slot`; a `Block` is constructed at **exactly one site**,
  from `pop()`, which draws from a successor map over `0..SLOTS-1`. **The guard
  `0 <= s < SLOTS` is a tautology of the simulation's own representation.**
* It is **not** called on ALLOC's own `pool[s*BLK]` write, and `gen[h]`, `nx[h]` and
  `regs[r]` are not indexes this simulation computes at all — so *"every index the buggy
  rung would compute"* is false three times over.
* The single case that could set `oob` **crashes the model before `sanitizer_expect` is
  read**.
* ⚠ **The one memory-safety failure this pattern's own R5 battery finds — `M3-nil-test`,
  where `h == NIL` is disabled and slot 255 is indexed into an 8-element array — is
  unrepresentable here**, because the simulation stores `None` for an empty register.

**The conclusion is still TRUE** — ASan/UBSan/Miri really are silent on all nine inputs;
the gate ran them, `p27`/`p29` fire on the same machinery, and my own reading of
`c/kernel.c` agrees. **What is false is that `model.py` establishes it.** This is
*"a control that cannot fire proves nothing"* — the rule `storage_arms.py` states, two
files away, about clang eliminating `p31`'s malloc pair.

⚠ **Cost of repair: the sentence is inside `contract_sha256`, so it is a hash move plus
`report.py` plus a re-gate.**

### 4c. ⚠ `Pool`'s docstring contradicts its own `__init__` three lines later

```python
129:    """The pool, with no generation counter anywhere.
144:        self.rel = [0] * SLOTS    # releases so far: the incarnation, counted
191:        return blk, (s + 8 * (self.rel[s] & M32)) & MASK      # ALLOC's fold
195:        self.rel[blk.slot] = self.rel[blk.slot] + 1           # FREE bumps it
```

`rel[]` **is** a per-slot generation counter, bumped by every FREE and folded as
`8 * rel[s]` **exactly as every rung folds `8 * gen[s]`**. `TASK_144_REPORT` §4 repeats
the stronger form — *"its simulation **has no generation counter at all**"* — and the
module docstring shouts `NO GENERATION COUNTER AT ALL`. **The true and sufficient claim
is narrower: no counter in the STALENESS TEST**, which is the axis that matters and which
the report's own table states correctly one row below the sentence.

### 4d. Disclosed and fine

`pool_fold`/`_run_spec` **is** a transliteration — of `verus.rs`'s `run`, and the module
docstring says so in terms. That is the right design (the gate re-derives the `ensures`
against it) and the independence is carried by the simulation. `TASK_144_REPORT` §4's
header *"TWO implementations, structurally different"* is loose about which one.

---

## 5. THE R1/R1h CONSTRUCTION — **SURVIVES**

**The engineer deviated from the task file's ✅ instruction (include-twice in the rungs)
and the replacement is stronger. I verified that it is stronger rather than taking the
argument.** `controls/safety_line.py` on the shipped files:

```
preprocessed kernel.c          235 line(s)
preprocessed kernel_hardened.c 237 line(s)
diff  +2 / -0
    + } else if (gen[h] != g) {
    + v = 251;
rc=0
```

**Then I planted three mutations into a COPY (`.temp/t145/sl/`) to prove the control is
not decorative — all three fire:**

```
MUT-a  an extra line in kernel.c        rc=1  "the diff is not a pure ADDITION: 1 line(s) REMOVED"
MUT-b  a SECOND `gen[h] != g` site      rc=1  "adds `gen[h] != g` 2 time(s), expected exactly 1"
MUT-c  an unrelated statement added     rc=1  "added line(s) outside the safety line: ['acc = acc + 0;']"
```

**The include-twice construction cannot fail; this one does.** The claim is now a
measurement. The raw `diff` of the two sources also localises to the safety-line site
alone (plus the two files' header comments).

### ⚠ `+9/−0` vs `+2/−0`, and the one place the old figure left a scar

`+9/−0` is `TASK_143`'s **demonstration**, which had three handle-consuming sites.
The shipped row has **one** — FREE, READ and WRITE share the decode — hence `+2/−0`.
`RECAP` 54 still carries `p32 +9/−0` with no forward pointer; 55 records the change.

⚠ **MAJOR — `c/kernel.h` still describes the demonstration, twice:**

```
c/kernel.h:73   **ONE OMITTED CONJUNCT, `gen[h] == g`, AT THREE SITES, …**
c/kernel.h:143  c/kernel.c  R1 -- `if (h == NIL)` alone at all three sites. THE BUG.
```

Against **ONE SITE** in `c/kernel.c:10`, `c/kernel.c:139`, `c/kernel_hardened.c:3`,
`c/kernel_hardened.c:129`, `README.md:15`, `NOTES.md:447`, **and twice inside the hashed
`slb-contract`**, and against a control that FAILS if the count is not exactly 1. **The
one file the gate prints as the kernel contract is the one file that is wrong about the
row's central number.** `c/kernel.h` is in `measurement_sources`, so the repair costs a
re-measure (cheap — `p19` 1 m 17 s, `p46` moved zero `Ir`).

⚠ **Minor, same origin, and inside `contract_sha256`:** `spec.md:107` and the hashed
`why` say the forgeable variant breaks *"on an input of **four** operations"*.
`NOTES.md:100`, `README.md:98`, `c/kernel.h` and the control's own transcript all say
**five**, and the control runs `op0..op4`.

---

## 6. POSITIVE CONTROLS — **SURVIVES, NARROWED**

**Every control in the shipped tree executes, and I made each one fail on purpose where
that was possible:**

| control | fires? | how I checked |
|---|---|---|
| `storage_arms.py` `k_ctl` | ✅ **10 of 10** C builds | re-run; `arena-plain` `free(): double free detected in tcache 2`, `malloc-asan` `attempting double-free`, etc. The `volatile void *slb_sink` really is load-bearing (clang) |
| `safety_line.py` | ✅ all three failure modes | three planted mutations, §5 |
| `forgeable.py` | ✅ | I **fixed** the forgeable variant (added an "already on the list?" test); `rc=1`, *"the forgeable variant did NOT break"* |
| `proof_mutants.py` M0 / M1 / M4 | ✅ | replicated independently, §3 |
| `repro.py` | ⚠ **no negative control** — see below |
| `model.py` `Pool._touch` | ❌ **CANNOT FIRE** — §4b |

### 6a. ⚠ `controls/repro.py` ships with no negative control. I supplied one; the claim holds.

*"Every cell is 1 distinct value in 20 runs"* is **vacuous if ASLR is off**, and
`repro.py` never checks. The manager itself demanded exactly this for `p28`
(`.memory/06-catalogue.md`: *"against a NEGATIVE CONTROL that gives 20 distinct values,
so the test is not blind and ASLR is on"*). `.temp/t145/repro_check.py`, run over the
gate's own binaries:

```
randomize_va_space = 2

p32 (the claim)                        p29 R1 (the NEGATIVE CONTROL)
  adversarial-alias      R1=1/20         adversarial-uaf      R1=20/20
  adversarial-doublefree R1=1/20         adversarial-succ     R1=20/20
  adversarial-many       R1=1/20         adversarial-many     R1=20/20
  adversarial-recycle    R1=1/20         adversarial-recycle  R1= 1/20
  adversarial-stale-read R1=1/20         degenerate/large/small 1/20
  stride3/degenerate/large/small 1/20
  (R1h = 1/20 everywhere; all five adversarial DIVERGE)
```

**The negative control fires 20/20 on the same box in the same minute, so `p32`'s
1-of-20 is a real property and not a dead instrument.** Recommend `repro.py` gain the
arm; the claim itself is upheld.

### 6b. ⚠ `arm_forgeable.c`'s aliasing flag is a false positive, and its line is quoted as evidence

```c
for (i = 1; i < nal; i++) if (allocs[i] == allocs[i - 1]) alias = 1;
...
printf("  two ALLOCs returned the same slot: %s\n",
       alias ? "YES <<< TWO LIVE HANDLES ALIAS ONE BLOCK" : "no");
if (simple && !alias) { …; return 1; }        /* the C-side self-check */
```

*"Consecutive ALLOCs returned the same slot"* is **true of a correct LIFO free list with
an intervening FREE**. My fixed variant printed `free list simple: YES` and
**`two ALLOCs returned the same slot: YES <<< TWO LIVE HANDLES ALIAS ONE BLOCK`** in the
same breath — so the C-side self-check `simple && !alias` is decided by `simple` alone,
and the printed line, which `NOTES.md` 1b, `README.md`, `c/kernel.h` and
`TASK_144_REPORT` §3a all quote verbatim, does **not** test liveness. In the real
transcript the conclusion is nevertheless correct (`op3` and `op4` both return slot 0
with no FREE between them, so both handles are live), and the Python-side
`broke = "SELF-LOOP" in log and "ALIAS ONE BLOCK" in log` did catch my fix. **The control
fires; its label overstates what it decides.** My §1 probe uses a proper liveness test on
the shipped kernel and confirms the underlying claim.

### 6c. ✅ ASan really is running where the row's "silence" result depends on it

`check.py` stage 7 builds `-static-libasan -static-libubsan` (sidestepping the
`LD_PRELOAD` blindness by construction), and the same stage fires `heap-use-after-free`
×3 on `p27` and ×3 on `p29`. **`storage_arms.py`'s positive control also fires in the
`arena-asan` and `arena-asan-clang` builds** — the same binaries whose bug arm is silent.
So *"silent on all nine inputs"* is a measurement, not a dead detector.

---

## 7. IS `p32` FINISHED? — **YES**

**Gate-green is not finished; I checked what a reader can find.**

```
harness/check.py p32                verdict PASS  failures []  blocked []  complete_run true
                                    (record diff vs HEAD: 2 of 1318 leaves, both miri seconds)
record.table_render                 render_sha256 == published_sha256   FRESH
record.published_table              cited ['80059fefdd89']              FRESH
record.contract_sha256              80059fefdd89a443f1393e5e5ae2cbc18ce969c13d3ad80e61fea091bb365f26
synthesis/synthesize.py --out …     diff vs committed results/synthesis.md: 0 lines  (BYTE-IDENTICAL)
results/synthesis.md                "Patterns: 28. Gate records: 28", p32 in 9 tables
results/SYNTHESIS.md                composition block updated: "temporal 3   p27 p29 p32"
harness/tools/composition.py --check OK, 28 patterns / 10 classes, p32 temporal + CAVEATS entry
harness/measure.py --check-stale     56 record(s) examined, 0 STALE
PROTOCOL rule 1 findings loop        no MISSING lines -> every pattern has a RECAP finding (p32 = 55)
PROTOCOL rule 10 citation check      only TASK_145_REPORT / TASK_146_REPORT / the TASK_NNN placeholders
```

**⚠ Read `blocked` out of the record, as instructed — `blocked: []`, not a `grep`.**

Ir and identity in `TASK_144_REPORT` §8 reproduce against the committed measurement
record exactly (`59,875,957 / 62,745,528 / 63,708,087 / 66,385,766 / 82,445,887 /
85,276,910 / 68,745,766 / 68,745,766`), and `identity` is `norel` at `-O0`, **`exact` at
`-O3` with `md5_fn cf0875f0cafb` on both sides**. The wall-clock rows quoted in the
report match the published table, including its one ✗-marked discarded cell — and **no
claim rests on any of them, because `p32` publishes no cost headline at all.** That
abstention is declared in five places and I agree with it.

---

## 8. SEVERITY

**Blocker: none.**

**Major**

| # | where | what |
|---|---|---|
| **M1** | `model.py:129–215`, `spec.md` hashed `why`, `README.md`, `NOTES.md` 2a, `TASK_144_REPORT` §4, **`RECAP` 55** | *"`model.py` DERIVES the sanitiser silence"* is **false**: `Pool.oob` cannot be set (tautological guard, 0 firings in 20 000 fuzzed buggy windows), the one case that would set it **crashes the model**, and the R5 battery's own memory-safety failure mode is unrepresentable in the simulation. The conclusion is true; the evidence claim is not. **Inside `contract_sha256`.** |
| **M2** | `c/kernel.h:73`, `c/kernel.h:143` | the safety line is at **THREE SITES** — contradicted by six other places including the hashed contract twice, and by a control that fails at ≠1. Stale text from `TASK_143`'s three-site demonstration. In `measurement_sources`. |
| **M3** | `controls/storage_arms.py` docstring | the `c-arena` arm is described as *"the SHIPPED C kernels … exactly as `harness/build.py` builds them"*; `build()` never compiles `c/kernel.c`. **I closed it by measurement, 10/10 — the conclusion is unharmed, the description is wrong.** |
| **M4** | `RECAP` finding 55's table | publishes `adv-stale-read / c-malloc = 35094` as a bare figure. See §9. |

**Minor**

* `Pool`'s docstring says *"no generation counter anywhere"* over an `__init__` that
  declares one (§4c); `TASK_144_REPORT` §4 repeats the stronger form.
* `controls/repro.py` has no negative control (§6a). Supplied; claim upheld.
* `arm_forgeable.c`'s `alias` flag is true of a correct allocator (§6b).
* `spec.md` prose + hashed `why`: *"four operations"* where everything else says five (§5).
* `NOTES.md` §10: *"The gate requires one per trusted item … **Three** items here, against
  `p27`'s and `p29`'s **seven**"* — the gate required **3** sections for p32's **5**
  trusted items (`grep -c '^#\[verifier::external_body\]'`: p27 **7**, p29 **7**, p32
  **5**), so the sentence both misstates the rule and compares twinned-item count against
  total-trusted count. §4's *"TCB: FIVE items … `p27` and `p29` ship SEVEN"* is correct.
* `RECAP` 54 still carries `p32 +9/−0` with no forward pointer to `+2/−0` (§5).
* **Gate, not p32:** `assume(false)` verifies `15/0` and `check.py` only shouts
  `[tcb-axiom]` (§3, arm `X4`). Same family as `TASK_144_REPORT`'s finding 4.

---

## 9. ⚠ WHAT THE MANAGER OVERSTATED (deliverable 3)

**Re-running a script checks the arithmetic, not the experiment design — and that is
exactly where the two overstatements are.**

1. ⚠⚠ **`RECAP` 55's table publishes `adv-stale-read / c-malloc = 35094` with the same
   typographic status as every reproducible cell in it, and drops the caveat.** The
   engineer's report prints **`NOT REPRO`** there and says *"no number from that cell is
   a fact"*; `NOTES.md` 2 and `README.md` say it twice more. The manager re-ran the
   control, **got a different number, and wrote the number down**. My re-run gives a
   fifth: `33172 / 33203 / 34629 / 35094 / 35962`. **The re-run confirmed the
   non-reproducibility and was published as a measurement of it.** The rest of that
   table is reproducible and correct.
2. ⚠⚠ **`RECAP` 55 repeats M1 verbatim** — *"`model.py` DERIVES that silence by checking
   every index the buggy rung computes rather than declaring it"* — carried straight from
   the engineer's report, with a ✅. **It is the manager's own rule 9 failure mode: the
   claim was re-run (the gate agrees the answer is `clean`) but the DESIGN was not
   attacked, and the design is where it fails.**

**Everything else in 55 and in the catalogue cells checks out**, and I looked: `PASS /
failures [] / blocked [] / complete_run true`; all five control JSONs FRESH; `15/0` and
twin `18/0`; **TCB 5 against p27's and p29's 7 — counted, correct**; `R4 == R5` `exact`
at `-O3`, `norel` at `-O0`, `Ir` identical; *"the invariant that makes R1h correct as an
allocator is neither proved nor needed"* — confirmed, `wf_ranges` has no acyclicity and
no uniqueness clause, and my `X3` shows why the conjunct is still not inert; the temporal
classification and its `CAVEATS` entry; the `p29` `spec.md` correction. ✅ **`RECAP` 55's
`adv-recycle` emphasis is the strongest thing in it and it is right** — with real
`malloc` storage and ASan running, the use-after-recycle harm is bit-identical and silent
in both arms (`29797947` in every build, reproduced).

---

## 10. CLEAN NEGATIVES — named attacks that did NOT land (`PROTOCOL` rule 6)

**Do not re-run these.**

1. **"p32 is p29's mechanism"** — no. Only p32 has a free list (1 of 28 by grep); p29
   cannot double-free (`live[cur]==1` guards every walk to its `free`); its gate record
   holds `heap-use-after-free` ×3 and zero double-frees.
2. **"p32 is p27's mechanism with a counter"** — the *closest* attack, and it still
   fails: p27 mallocs per record, never recycles, cannot double-free, and has no list.
3. **"the aliasing is asserted, not exhibited"** — no. Independently replayed: cyclic
   list + two current registers on slot 0 + a WRITE/READ round trip in the checksum, on
   `adversarial-alias`, `-doublefree` and `-many`, and on **no benign input**.
4. **"the malloc arm's abort is the teardown, not the bug"** — no. ASan frames put both
   `attempting double-free` at `arm_body.inc:112` (the op loop's stale FREE) and the
   `heap-use-after-free` at `:119` (the stale READ). The teardown's `free` at `:148`
   appears in no trace.
5. **"the R5 is vacuous"** — no. `requires false` fails at `main`'s call site;
   `ensures true` fails at `main`'s ghost consumer; a spec-only weakening fails; a
   disjunctive `ensures` with a constant body fails.
6. **"the ensures could be silently weakened"** — no. `spec.md` pins it and `check.py`
   `rep.fail("proof-pin", …)`s on drift.
7. **"1 distinct in 20 is just ASLR being off"** — no. `randomize_va_space = 2`, and
   p29's R1 gives 20/20 on the same box in the same minute.
8. **"the gate record or the published artefacts are stale"** — no. Gate record
   reproduces to 2 of 1318 leaves; `results/synthesis.md` is byte-identical to a fresh
   render; `table_render` and `published_table` both FRESH; `0 STALE`; composition OK;
   every pattern has a RECAP finding.
9. **"safe Rust's bit-identity is a control-file artefact"** — no. The shipped
   `c/kernel.c` and `c/kernel_hardened.c` reproduce the control's `c-arena` numbers on all
   five op streams, both arms, 10 of 10.

---

## 11. WHAT I DID NOT DO

* **I did not re-run `controls/proof_mutants.py`'s M2/M3/M5/M6.** I replicated M0, M1 and
  M4 with my own substitutions and added seven arms of my own. The four I skipped are
  deletion arms whose expected outcome (fail) is the cheap direction.
* **I did not re-run `harness/measure.py p32`.** `--check-stale` reports the record
  FRESH and the report's numbers reproduce against it; a re-measure moves only wall clock.
* **I did not gate any other pattern**, and I did not run the tree sweep.
* **I did not attempt an R5 that proves the free-list well-formedness invariant.** The
  engineer names it as the most valuable follow-up and I agree — `X3` is the evidence
  that the proof would have something to say.
* **I did not test the `sweep-*` bands** (not generated in the tree, nothing published
  from them).
* ⚠ **I could not independently verify `PROTOCOL` definition-of-done item 6.** The
  engineer discloses honestly that the contract hash was recorded at the END of the task
  and that the check the rule exists for is unavailable for a new pattern. **That
  disclosure is correct and I confirm the diff is vacuous** (`git show HEAD:… | diff -`
  is silent on a clean tree, and a pattern lands in one commit). The weaker check the
  disclosure offers — that the `68ea7c9f58ce → 80059fefdd89` move is fourteen sets of
  backticks and nothing else — **I did not reproduce**, because it needs
  `.temp/t144/spec/mkspec.py`'s pre-edit output and the gate logs, which are gitignored
  and were not preserved. **That is a real gap in the evidence chain and it is the
  engineer's own disclosed one, not a new finding.**
* **I am unsure about one thing:** whether `c/kernel.h`'s "three sites" is worth a
  re-measure on its own, or should be batched with the `model.py` docstring, the
  `storage_arms.py` docstring and the `spec.md` "four operations" into one pass.
  `PROTOCOL` rule 6's budget table says batch them — the `spec.md` edit forces a
  `contract_sha256` move and a re-gate anyway, and `c/kernel.h` forces a re-measure, so
  doing all four at once costs one of each.

---

## 12. EVIDENCE

```
.temp/t145/NOTES.md              an index of everything below
.temp/t145/alias_probe.py        the independent R1 replay + aliasing/cyclicity instrumentation
.temp/t145/driver_replay.py      the same, end to end through spec.md's driver loop
.temp/t145/run_safety_line.py    + sl/  the safety-line control and its three planted mutations
.temp/t145/ctl/                  storage_arms.py + forgeable.py run from .temp (sidecars untouched)
.temp/t145/extra_mutants.py      + mut/X*.rs + .log   the seven arms the battery does not have
.temp/t145/replicate_m1_m4.py    + mut/R-*.rs + .log  M1 and M4 re-derived independently
.temp/t145/repro_check.py        20 runs/cell + the negative control repro.py lacks
.temp/t145/touch_probe.py        proof that model.py's `oob` derivation cannot fire
.temp/t145/shipdrv/main_hex.c    the SHIPPED C rungs on the control's own op streams
.temp/t145/arena.i malloc.i      cc -E -P of both storage cells; the measured difference
.temp/t145/asan_traces.log       the whole ASan reports, never truncated
.temp/t145/gate1.log             harness/check.py p32 -> PASS
.temp/t145/synthesis_fresh.md    synth.diff is EMPTY
```

Binaries are deleted; `storage_arms.py`, `forgeable.py`, `harness/build.py`,
`extra_mutants.py`, `replicate_m1_m4.py` and the one `gcc` line recorded in
`shipdrv/main_hex.c`'s header rebuild every one of them.

---

**PROTOCOL rule 2 running count: launched from 720 (`TASK_144_REPORT.md`'s closing
paragraph), carried to 733** — branch delta **+13**:

1. **`model.py`'s `sanitizer_expect` "derivation" cannot fire** — the guard is a
   tautology of the simulation's own representation, and the one case that would trip it
   crashes the model. *(major; inside the hashed contract and inside `RECAP` 55)*
2. `c/kernel.h` says the safety line is at THREE SITES, twice, against six other places
   and a control that fails at ≠1. *(major)*
3. `storage_arms.py`'s docstring says its `c-arena` arm is the shipped C rungs; `build()`
   never compiles them. Closed by measurement, 10/10. *(major)*
4. `RECAP` 55 publishes `35094` for a cell its own sources call not-a-fact; my re-run
   gives a fifth value. *(major)*
5. `Pool`'s docstring denies the generation counter its `__init__` declares three lines
   below. *(minor)*
6. `controls/repro.py` has no negative control; supplied, and the claim survives at
   `randomize_va_space = 2` against p29's 20/20.
7. `arm_forgeable.c`'s `alias` flag is true of a correct LIFO allocator, and its printed
   line is quoted as evidence in four files.
8. `spec.md`'s hashed `why` says "four operations" where the control runs five.
9. `NOTES.md` §10 misstates the trusted-argument rule and mixes two denominators.
10. **`assume(false)` verifies `15/0` and the gate only SHOUTS** — the "vacuity is a
    shout, not a failure" family again, one file over from where `TASK_144` found it.
11. **`X3-spec-only-weaken` FAILS** — the third cell M1/M4 were missing, and it converts
    "the safety line is load-bearing against the specification" from an assertion into a
    three-cell result.
12. `X1`/`X2` are clean negatives the project did not have: `main`'s ghost
    `assert(r == pool_fold(…))` is what makes a trivialised `ensures` detectable, and the
    call site is what makes an unsatisfiable `requires` detectable.
13. ⚠ **`results/SYNTHESIS.md` was modified by another agent at 07:03 UTC, mid-review**,
    against this task's "you are the ONLY agent running".

⚠ **A rigour signal, not a ledger — reconciliation across branches is the manager's job,
not mine.**
