# TASK_124 — `CVE-2021-23017`: the four-way split is a property of the PORT. **REFUSE.**

**Role: research engineer. Deliverable: a decision with a measurement behind it.**
Scratch, generators and every log: `.temp/t124/` (`A/BUILD.sh` rebuilds
everything and prints the run order). Nothing under `.memory/`, `RECAP.md`,
`results/`, `synthesis/` or `patterns/` was touched; `git status` was clean at
start and at finish.

---

## HEADLINE

⚠⚠ **§A OUTCOME 2, MEASURED: the four-way split is a property of the PORT, and
it is worse than that — TWO of its four cells are cells this project's rungs
CANNOT OCCUPY.** I re-ported R3 to the fixed-capacity destination and re-measured,
as outcome 2 requires. The split collapses to the shape `p02` / `p12` / `p13`
already ship.

⚠⚠⚠ **AND THE ROW DIES A SECOND TIME, INDEPENDENTLY, ON THE LIMB IT WAS
ADMITTED FOR.** Limb 2 is *"a new SOURCE of the bound"*. I built the control the
census could not: hold the kernel fixed and change the bound's provenance from a
**prior-pass count** to an **input extent** (`p02`'s / `p42`'s class, which the
tree already has). **Every published difference moves by exactly `+0.00`, and all
six decode kernels are the same instructions.** The distinction the census
measures is invisible to every instrument the ladder publishes.

✅ **The manager's stated least-sure call #1 was RIGHT.** I was asked to prove it
wrong and could not; the measurement backs it. Below is the measurement, not the
reasoning.

---

## §A — IS THE FOUR-WAY SPLIT A PROPERTY OF THE BUG OR OF THE PORT?

### A0 — one correction to the task file's framing, made before measuring

`TASK_055_REPORT.md` §2.8 caveat 2 says **"a different data structure"**, not
"a different representation", and ⚠ **the surrounding paragraph carries the load
the task file dropped**: §2.8's third bullet says *"R2/R3 **cannot hold the
pointer at all**, so the `(slot, gen)` representation is **forced**"*. **That
forcing is exactly why §2.8 calls it the pattern's whole point rather than a
defect.** The candidate has no such forcing: safe Rust *can* write into a
fixed-size `Vec<u8>` — that is literally what `d.rs`'s own R2 does. **So the
`p27` precedent does not transfer, and the trap the task file names is the right
trap.**

### A1 — the upstream fact (read, not guessed)

`../LearnVeri/microbench/CVE-2021-23017/lib.c:144` — the C destination is a
per-name `malloc(sz)` sized by the sizing pass. ✅ `TASK_123`'s C port is honest.

⚠ `../LearnVeri/microbench/CVE-2021-23017/rust/src/lib.rs` — **the corpus's own
`#![forbid(unsafe_code)]` safe-Rust port does NOT use `Vec::push` for the name.**
It reserves a fixed region, `self.arena.resize(name_off + sz, 0)`, and writes into
it with `dst[w] = n as u8` through `name_decode_into(…, dst: &mut [u8], …)`.
**That is R2's shape.** The growable `push` occurs in exactly one place in the
whole evidence chain: `.temp/t123/C/d.rs`, written by `TASK_123`'s engineer. Not
in the CVE, not in nginx, not in the corpus. **Evidence, not yet proof — proof
follows.**

### A2 — THE PERTURBATION CONTRAST (`.temp/t124/A/matrix.log`)

Predictions written into `.temp/t124/NOTES.md` **before** the run. Perturb the
sizing pass's count by `+8`; ask whose behaviour changes.

| rung | delta = 0 (the bug) | delta = +8 | changed? |
|---|---|---|---|
| R1 C gcc + clang | `acc=185727`, ASan **`heap-buffer-overflow`, `WRITE of size 1`** | `acc=5757583`, ASan silent | ✅ MUST-FIRE fired |
| R2 `naive` | **PANIC** rc 134, *"index out of bounds: the len is 4 but the index is 4"* | `acc=5757583` | ✅ |
| R3 `copyfs` — fixed cap, per-label `copy_from_slice` | **PANIC** rc 134, same message | `acc=5757583` | ✅ |
| R3 `splitmut` — fixed cap, `split_at_mut` cursor | **PANIC** rc 134, *"mid > len"* | `acc=5757583` | ✅ |
| R3 `getmut` — fixed cap, checked-and-drop | `acc=185727` **silent truncation** | `acc=5757583` | ✅ |
| R4 `unsafe` | `acc=185727` silent OOB, **Miri UB** | `acc=5757583`, Miri clean | ✅ |
| **R3 `push` — TASK_123's** | `acc=5757583`, **capacity 4 → 8** | `acc=5757583` | ❌ **UNCHANGED** |
| **R3 `pushfill` — push, fill controlled** | `acc=5757583`, **capacity 4 → 8** | `acc=5757583` | ❌ **UNCHANGED** |

**Six of eight arms had to change and did. The two `push` arms did not.**

⚠ **The sizing pass's count is a BOUND in six rungs and a HINT in one, and the
one is the cell the row was proposed for.** The mechanism is measured, not
inferred: `alloc0=4 → alloc1=8`. **The `Vec` reallocated.** `push` does not
survive the bug, it **deletes the bug's precondition** — and it allocates a
different-sized heap block than C does, so the two rungs are not the same
program.

⚠ `pushfill` is `push` with `vec![0u8; cap]` + `clear()`, i.e. the *identical*
allocation and fill the slice rungs get. It grows 4 → 8 too. **So the growth is
not an artefact of `with_capacity`; it is the `push` idiom.**

Must-not-fire arms silent: benign packet — all eight rungs `acc=171522973473`;
attack + the nginx fix — all eight rungs `acc=5757583`, ASan **0** `ERROR` lines.

Miri (`.temp/t124/A/miri.summary.log`; invocation mirrors `check.py:8138`,
`MIRIFLAGS` removed from the child): `v=5 attack delta=0` → **UB**,
*"slice::get_unchecked_mut requires that the index is within the slice"*;
`v=5 attack delta=8` **clean**; `v=5 benign` clean; `v=1 attack delta=0` and
`delta=8` clean.

### A3 — the R3 cell takes THREE values across admissible zero-`unsafe` spellings

At `delta=0` on the attack packet, with the destination held at the sizing pass's
count, four zero-`unsafe` decode spellings give **three different answers**:

- `push` → `acc=5757583` (**the FIXED C's output** — bug deleted)
- `copyfs` / `splitmut` → **PANIC**
- `getmut` → `acc=185727` (**the BUGGY C's output**, silently, in bounds)

while R1 and R4 are pinned to one value each. ⚠ **A cell that moves when you
change the spelling is not a measurement of the bug.** (Honest weakening: `getmut`
is zero-`unsafe` and fixed-capacity but it is **not a tuning** — it adds a branch
per byte. It is the weaker of my two §A arguments; `copyfs` and `splitmut` are
the ones that carry it, and both are named in `.memory/01-ladder.md`'s own R3
spelling list.)

### A4 — ⚠⚠ AND THE DECISIVE ONE: NO BUILT PATTERN HAS *ANY* RUST-RUNG SPLIT

`.temp/t124/A/rung_split_census.py`, reading `results/gate/*.json`'s
`adversarial` block across all 26 built patterns:

```
adversarial inputs across all built patterns: 129
  ... on which ANY pair of rungs diverges           : 56
  ... on which the FOUR RUST RUNGS take >1 value    : 0

distinct-value histogram, ALL rungs   : {1: 73, 2: 44, 3: 12}
distinct-value histogram, RUST rungs  : {1: 129}

MUST-FIRE ARM: the ALL-rungs census must see >1 somewhere -> OK
```

⚠⚠ **Zero. Not one adversarial input in the whole tree makes `safe_naive`,
`safe_tuned`, `unsafe` and `verus` disagree.** Every divergence the project
records is among the **C** variants (`c-gcc` / `c-clang` / the hardened twins).
Read from the sources rather than inferred: `p12`'s **C** kernel omits
`dlen + slen <= DST_CAP`; **`p12/unsafe.rs:81` carries it**. The bug lives at R1.
And `results/gate/*.json` records **194 Miri runs and 0 UB**.

**So `TASK_123`'s matrix has two cells this project's rungs cannot occupy:**

1. **`R3 = CORRECT`** — it is `push`'s, and it deletes the bound (A2, A3).
2. **`R4 = silent OOB write, Miri UB`** — ⚠ **not an admissible R4 at all.**
   `.memory/01-ladder.md`'s R4 row: *"Unsound-by-inspection is not allowed: it
   must be **correct**, just unverified."* An R4 with UB also has no verifying R5
   twin, which breaks the `identity` pin **26 of 26** patterns carry
   (`grep -l identity patterns/*/spec.md | wc -l` → 26 of 26).

**Built the project's way, R2 / R3 / R4 / R5 all carry the fix and there is NO
split. Built `TASK_123`'s way, R4 is inadmissible and R5 cannot exist. The
four-way split is not available under either convention.**

### §A VERDICT

⚠⚠ **OUTCOME 2 — A PROPERTY OF THE PORT.** I took the branch outcome 2 offers
(*"re-port R3 to the same fixed-capacity destination and RE-MEASURE"*) and did it
twice, with `copyfs` and `splitmut`. The re-measured matrix is
**C OOB / R2 panic / R3 panic / R4 correct-and-unchecked** — `p02`'s and `p12`'s
shape exactly. It is not outcome 3: the fixed-capacity destination **can** be
written, and doing so does not make the row `p02` by *construction* — it makes
it `p02`-shaped by *measurement*, which is a stronger and cheaper reason.

---

## §B — LIMB 2 DOES NOT SURVIVE CONTACT EITHER, AND THIS IS INDEPENDENT OF §A

§A alone would leave a defender saying *"fine, the split was oversold, but limb 2
still stands: no built kernel is bounded by a prior-pass count."* The task file
put the objection precisely: **that is a census of what EXISTS, not proof that
the ladder can PRICE it.** So I built the control.

### B0 — the bound-provenance control (`.temp/t124/A/extent_gen.py`)

`split_extent.rs` is `split.rs` with exactly one thing changed: the destination
size arrives as an **INPUT EXTENT** from `argv` — `p02`'s and `p42`'s class,
which the tree already has — instead of from the sizing pass. **Every decode
kernel is untouched.** Must-fire arm: the two binaries must differ (they do,
by the sizing pass).

| instrument | result |
|---|---|
| probe 2, symbol extent from `readelf -sW` | all six kernels the SAME SIZE; **`k_dec_unsafe` BYTE-IDENTICAL** (`2117abed…` — and that is also `.temp/t123`'s md5 for the same symbol, a free cross-probe check) |
| mnemonic diff, operands stripped | **0** on all six. Must-fire arm `k_dec_naive` vs `k_dec_copyfs` = **152** |
| byte level, file name + every line number held identical | safe kernels **still differ** → my panic-`&Location` hypothesis **REFUTED**, recorded rather than quietly dropped |
| raw `objdump` diff of `k_dec_naive` (`A/kn.diff.txt`) | every differing line is (a) a branch to an absolute address whose `<k_dec_naive+0xNN>` **offset is identical on both sides**, (b) `lea 0x…(%rip),%rdx` for a panic `&Location`, or (c) `call *0x…(%rip)` through a GOT slot |
| normalise exactly those three (`provenance_reloc.py`) | **0 diffs on all six kernels** — *the same code at a different link address* |

⚠ **The normaliser has two arms of its own, because a normaliser aggressive
enough to erase a real difference would make everything look identical:**
`k_dec_naive` vs `k_dec_copyfs` still shows **164** diffs, and `mutarm.py` plants
`0xC0 → 0xE0` in `k_dec_naive` only — the normaliser sees it (**1** diff in
`k_dec_naive`, **0** in `k_dec_unsafe`).

### B1 — **and every published difference moves by exactly `+0.00`**

`.temp/t124/A/ir_extent.log`, marginal `Ir`/call, benign packet:

```
rung           PRIOR-PASS  INPUT-EXTENT   abs diff        published difference
R2 naive           662.00        599.00     -63.00   R2−R4  +71.00 -> +71.00  moved +0.00
R3 copyfs          625.00        562.00     -63.00   R3−R4  +34.00 -> +34.00  moved +0.00
R3 splitmut        613.00        550.00     -63.00   R3−R4  +22.00 -> +22.00  moved +0.00
R3 getmut          608.00        545.00     -63.00   R3−R4  +17.00 -> +17.00  moved +0.00
R3 push            579.00        516.00     -63.00   R3−R4  -12.00 -> -12.00  moved +0.00
R3 pushfill        715.00        652.00     -63.00   R3−R4 +124.00 ->+124.00  moved +0.00
R4 unsafe          591.00        528.00     -63.00
MUST-FIRE ARM: the two binaries must differ in absolute cost -> -63.00, OK
```

⚠⚠ **The provenance shifts a term COMMON TO BOTH ARMS of every difference — the
sizing pass, `63.00 Ir`/call — and therefore cancels out of everything the
project publishes.** By the time the decode kernel sees the bound it is a
`usize` with no history, and nothing in the toolchain, the prover or the gate can
ask where it came from.

⚠ **Coincidence worth flagging so nobody conflates them: the sizing pass costs
`63.00 Ir`/call and `TASK_123`'s (contaminated) `R2 − R4` was also `+63.00`.
They are unrelated numbers.**

**So limb 2 is a distinction the ladder cannot carry. The census is correct and
it measures something the instruments cannot see.**

### B2 — Verus. ⚠ **NOT SPENT, deliberately.**

§A refuses the row, so one probe on an obligation for a pattern that will not be
built is a probe spent on nothing. Recorded as not-run rather than guessed at.
For a future re-opener: the obligation would be *the sizing pass's count bounds
the writing pass's writes*, a relation between two traversals of the same input
— and note that under the project's actual convention (A4) R4 and R5 carry the
**fix**, so the obligation is the fixed kernel's, not the buggy one's.

### B3 — the R4 spelling was never a problem

⚠ **The task file treats probe 4's *"`get_unchecked` 0 hits at the pin"* as a
constraint. It is the NORMAL situation.** `get_unchecked` appears **269** times
and `get_unchecked_mut` **30** times across the tree's `unsafe.rs`, and the R5
twin wraps it in an `external_body` accessor — `buf_get_unchecked` (17 patterns),
`dst_set_unchecked`, `arr_set_unchecked`, `ring_set_unchecked`, … The spelling is
named and shipped 26 times.

### B4 — ⚠ **the task file's §B.1 premise is FALSE, and it is cheap to say so**

> *"A sizing pass and a writing pass that must agree is a two-call kernel, and
> every built pattern is one call."*

**A two-pass structure does not need two calls.** `p42`'s kernel does
`dig = malloc(len)` **inside** `kernel()`, and four patterns already define
helper functions in the kernel TU: `p09` (`load_u32`, `load_u64`), `p36`
(`op0`…`op7`), `p38` (`rec_len`, `rec_set_len`), `p46` (`slb_p46_ld64`). All 26
driver loops make exactly one `kernel(` call and a two-pass kernel would too.
**The driver is not a blocker, and there is no finding here.**

---

## §C — RE-RUNNING `TASK_123`'s ARMS, AND A DEFECT IN ITS PUBLISHED NUMBER

### C1 — the arms reproduce

`.temp/t123/C/REBUILD.sh` re-run in full (`.temp/t124/t123_rebuild.log`): ASan
fires with `heap-buffer-overflow` / `WRITE of size 1`; probe 2 gives the same
three md5s **and** the same sizes (`602` / `470` / `515`); the `bound_census.py`
must-fire arm fires on the candidate; C bug/fix behaviour matches. Its probe 3
reproduces **to five decimals**: `677.00 / 614.00 / 590.00 / 409.00 / 421.00`.

### C2 — ⚠⚠ but `+63.00` is contaminated by `TASK_123`'s OWN defect 2

`.temp/t123/C/d.rs:114,120` evaluates **`rung.starts_with("tuned")` and
`rung.starts_with("unsafe")` INSIDE the measured loop**, on a `String`. That is a
per-iteration dispatch whose cost differs per arm — *"per-iteration `match`
dispatch making byte-identical kernels read `43/50/37`, which changed a sign"* is
`TASK_123`'s own disclosed instrument defect 2, fixed in its §A probe and left in
the §C one.

`.temp/t124/C/d_hoist.rs` is `d.rs` with **only** that hoisted (a `bool` and an
`extern "C" fn` pointer computed once); every other byte is `d.rs` verbatim, and
the behaviour matrix is unchanged.

| | `TASK_123` `d.rs` | `d_hoist.rs` | in-loop dispatch cost |
|---|---|---|---|
| R2 naive | 677.00 | 667.00 | 10.00 |
| R4 unsafe | 614.00 | 596.00 | **18.00** |
| R3 tuned | 590.00 | 579.00 | 11.00 |
| **R2 − R4** | **+63.00** | **+71.00** | |

✅ **My independent probe (`A/split.rs`, dispatch hoisted from the start) also
reads `+71.00`. Two probes agree.** ⚠ **`+63.00` is 11 % low and the cause is the
defect the report itself named.** The arms differ because `"naive"`(5) vs
`"unsafe"`(6) makes one `memcmp` exit on the length and the other not.

### C3 — the `R3 − R4` figure the project publishes, with the fill controlled

`TASK_123` disclosed that its `R3` used `Vec::with_capacity` (unfilled) while
`R2`/`R4` used `vec![0u8; n]`, so `590.00` was not comparable. Controlled:

| pair | Ir/call | note |
|---|---|---|
| **`R3 copyfs` − `R4`** | **+34.00** | fixed capacity, bulk `copy_from_slice`. ⚠ **the honest `R3 − R4`** |
| **`R3 splitmut` − `R4`** | **+22.00** | fixed capacity, `split_at_mut`. Cheapest in-contract R3 found |
| `R3 getmut` − `R4` | +17.00 | zero-`unsafe` but not a tuning |
| `R2 naive` − `R4` | +71.00 | corrected from `+63.00` |
| `R3 push` − `R4` | −12.00 | ⚠ **not the same program; do not publish** |
| `R3 pushfill` − `R4` | +124.00 | `push` with the fill controlled |
| C-gcc fix − C-gcc bug | +12.00 | the nginx fix, unchanged from `TASK_123` |

⚠ **The R4 side was searched only at `get_unchecked_mut`.** I did not search it
further, because §A had already refused the row; **`+22.00` and `+34.00` are
R3-side bounds against one R4, not a safety tax.** Stated per
`.memory/01-ladder.md`'s standing rule.

### C4 — ⚠⚠ TWO INSTRUMENT CORRECTIONS, BOTH MEASURED, BOTH TRANSFERABLE

1. ⚠⚠ **`.memory/03-measurement.md`'s zero-iteration control is WRONG for a
   kernel that ALLOCATES.** That file recommends *"run the probe with the
   iteration count set to zero and subtract"*, and calls it **"the technique"**.
   Measured error against the honest two-non-zero-count marginal:
   **`+0.82 Ir`/call (C-gcc), `+1.51` (C-clang), `+0.42` (all seven Rust rungs)**.
   Two mechanisms, both absent from the marginal: the `n = 0` run performs **zero
   `malloc`s** so it never pays glibc's one-time arena initialisation, and it
   prints a **shorter line** (`acc=0` vs `acc=171522973473`) — the file's own
   `println!` trap, arriving through the control it recommends.
   ✅ **`p40`'s `21` is not affected** — that was re-derived against a
   zero-iteration control on a kernel made byte-equal, which is a different
   construction. ⚠ **The scope of the correction is: allocating kernels only.**
   **Rule 9 split: the CONCLUSION (do not baseline an allocating probe at n=0)
   stands on the numbers above; the relative WEIGHT of the two mechanisms is
   OPEN — I did not separate them.**
2. **My own ARM 1 tolerance was wrong and I say so rather than quietly relaxing
   it.** First threshold `1e-9` failed on all ten arms at a residual of ≤0.01.
   `A/arm1.py` characterises it before the threshold moved: the same binary and
   argv give **BIT-IDENTICAL** totals, and the marginal oscillates around the
   integer by **±0.007** with **no drift in n**
   (`411.9934 / 412.0072 / 411.9928`; `661.9986 / 662.0030 / 661.9970`) —
   glibc malloc/free bookkeeping. Tolerance is now `0.02`, and the comment in
   `ir.py` says it was **set after measuring**.

---

## ANSWERING THE THREE "LEAST SURE" CALLS

1. ⚠⚠ **"`R3 = CORRECT` is PROBABLY an artefact of a growable `Vec`." — YOU ARE
   RIGHT, and it is now measured.** I was asked to prove it wrong and could not.
   Perturbing the bound by `+8` changes six of eight rungs and leaves both `push`
   arms untouched; the `Vec` grows `4 → 8` even with the fill controlled; three
   more zero-`unsafe` spellings give two *other* answers; and no built pattern has
   any Rust-rung split in 129 adversarial inputs.
2. **"Is the row worth building even if §A comes out clean?" — MOOT, and the
   answer would have been NO ANYWAY.** §B is independent of §A: even with a clean
   §A, the provenance control kills limb 2, and the row would then meet **no
   limb** — limb 1 was never claimed, limb 3 has no isolation by `TASK_123`'s own
   disclosure. ⚠ **Your framing *"admissible but it will publish nothing"* is the
   right one, and here it is stronger: after measurement it is not admissible.**
3. ⚠ **"Should the project build a 27th pattern at all?" — I will not convert this
   into a reason to stop, and finding 41 is why.** This row dying is one row
   dying. What I can offer instead of an opinion is **a reusable instrument**:
   `extent_gen.py` + `provenance_reloc.py` + `ir_extent.py` are a **general
   pre-screen for any limb-2 claim** — hold the kernel fixed, change the property
   the claim is about, and ask whether any published number moves. It cost about
   twenty minutes here and it refuted a limb a 26-kernel census had supported.
   ⚠ **Offered as a suggestion, not wired up — `CLAUDE.md` rule 3.**

---

## WHAT SURVIVES, AND IS WORTH A SENTENCE SOMEWHERE

⚠ **Do not lose this in the refusal.** The `push` observation is real, it is now
**measured** rather than asserted, and `TASK_123` was right to flag it while
correctly declining to claim it as limb 3:

> **Safe Rust's idiomatic escape from a two-pass sizing bug is `Vec::push`, which
> does not CHECK the bound — it DELETES it.** Measured: perturbing the sizing
> pass's count by `+8` changes the observable behaviour of the C rung, the naive
> rung, two tuned rungs, a checked-and-drop rung and the unsafe rung, and changes
> **nothing** in the `push` rung, whose `Vec` reallocates `4 → 8` regardless.

⚠ **That is a sentence about a Rust IDIOM, not a ladder row** — the thing it
describes is precisely a rung that is no longer running the same program, so it
can never be a cell in a five-rung comparison. It belongs in prose
(`results/SYNTHESIS.md`), if anywhere.

Also worth keeping: `getmut` — a zero-`unsafe`, fixed-capacity spelling that
reproduces **the buggy C's output** silently and in bounds. That is `p04`'s
in-bounds-wrong-data class arriving from the *safe* side, and `p04` / `p13` /
`p19` already carry it.

---

## PROBLEMS / NOT DONE

- **B.2 not run** (see §B2). "R5 is open" is not claimed either way for this row.
- **The R4 side was not searched in contract** (§C3). `+22.00` / `+34.00` are
  R3-side bounds only.
- **`getmut` is not a tuning** and I flag it as the weaker §A argument.
- **My panic-`&Location` hypothesis was refuted by my own byte-level test**, and
  the byte-level difference is closed only at the *relocation-normalised* level.
  Every differing byte is accounted for by (a)/(b)/(c) in §B0, but I did not
  disassemble all six kernels line by line — only `k_dec_naive`, whose full diff
  is in `A/kn.diff.txt`. **The other five are closed by the normaliser plus its
  two arms, not by eye.**
- **I did not re-check whether a fixed-capacity `push` variant exists** that
  panics on overflow (e.g. via a hand-written capacity assert). It would be a
  fifth spelling and could not change §A4, which is the load-bearing measurement.

## TREE STATE

- `git status` **clean** at start and finish. No `git add` / `git commit` run.
- `harness/check.py` and `harness/build.py` **were not run**. I read
  `results/gate/*.json` only.
- `harness/measure.py --check-stale`: **52 record(s) examined, 0 STALE** —
  identical to the state at launch.
- `.temp/t123/` restored: `REBUILD.sh`'s four binaries deleted after re-running
  its arms; every source, log and generator it had is untouched.
- `.temp/t124/` is **432 K**, binaries deleted, `A/BUILD.sh` regenerates all of
  them and prints the run order.

## BRANCH DELTA

Zero tracked files changed. One new file: `.tasks/TASK_124_REPORT.md`. Everything
else is under `.temp/t124/` (gitignored).

## RUNNING COUNT

`526 → 536`. ⚠ **Reconciliation is the manager's job, not mine; I am carrying,
not re-adding.** The ten:

1. the four-way split is a property of the PORT (§A2);
2. two of its four cells are inadmissible rungs (§A4);
3. no built pattern has any Rust-rung split — 0 of 129 (§A4);
4. limb 2 is invisible to every published instrument (§B0/B1);
5. `TASK_123`'s `+63.00` is contaminated by its own defect 2 → `+71.00` (§C2);
6. `.memory/03-measurement.md`'s zero-iteration control is wrong for allocating
   kernels (§C4.1);
7. the task file's §B.1 two-call premise is false (§B4);
8. probe 4's `get_unchecked` finding is a non-issue, not a constraint (§B3);
9. `TASK_055` §2.8's forcing argument does not transfer, and the task file's
   paraphrase dropped it (§A0);
10. three self-caught defects in my own instruments — the ARM-1 tolerance, the
    panic-`&Location` hypothesis, and a `\b`-after-`0x` regex that left eight
    residual diffs (§C4.2, §B0).
