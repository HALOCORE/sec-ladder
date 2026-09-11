# TASK_PHP_035 — report

**Role:** research engineer, alone.

> ## HEADLINE — **THE TWIN VERIFIES, AND IT IS BYTE-IDENTICAL.**
>
> `r4_fold_iter` has a Verus twin that verifies at the pinned Verus and the
> pinned vstd — **`10 verified, 0 errors`**, the same obligation count the
> shipped rung verifies at — with **no `assume`, no new trusted item and no
> `is not supported`**. Compiled at `O3`/isolated its `kernel` is
> **byte-identical** to the unsafe variant's: **209 instructions,
> `d71669d3c0e6`, both**. So `spec.md`'s `identity: unsafe == verus, O3 exact`
> would hold for the candidate.
>
> ▶ **`ph29`'s R4 SIDE WAS UNSEARCHED**, the published `fixed-R4 bound` is a
> bound over an unsearched endpoint, and the candidate is **cheaper AND one
> trusted call site smaller** — two claims, stated separately, both verified.
>
> ⚠ **The shipped rung does NOT move.** `.memory/02-bench-rules.md` holds R4
> fixed by fiat and that fiat is what makes the bound a bound.
>
> ⚠⚠ **The gate verdict is read out of `results-php/gate/ph29-recvfrom-alloc.json`**
> — `verdict: PASS`, `failures: []`, `complete_run: true`,
> `controls_json: {"spellings.json": "FRESH"}` — **and not out of a log.**

**Brackets.** `harness/measure.py --check-stale` → **66 / 0** and
`harness-php/gate.py --tool measure --check-stale` → **12 / 0**, first (before
anything was touched) and last. Both agree with the task file. **No measurement
record moved and no re-measure was needed**: nothing this task touched is in
`measure.py`'s pinned sources.

**What landed**

| | |
|---|---|
| `patterns-php/ph29-recvfrom-alloc/controls/spellings.py` | the control. 9 variants, both sides searched, **both halves of `identity` checked** |
| `patterns-php/ph29-recvfrom-alloc/controls/spellings.json` | its sidecar. `problems: []`, `verus_checked: true`, `r4_endpoint_degenerate: false` |
| `patterns-php/ph29-recvfrom-alloc/NOTES.md` | §0's **sixth** `contract_sha256` move + §3.1's finding; new **§8b** (the answer); §8 and §14's "was not built" repaired |
| `results-php/gate/…json`, `results-php/preflight/…json` | the gate's own outputs |
| `../LearnVeri/PITFALLS.md` | the durable Verus fact (PROTOCOL rule 4's channel, since `.memory/` is manager-only) |
| `.temp/php35/` | scratch: 3 probes, the hand-written Verus sources, the logs, `NOTES.md` as the index |

**Not touched:** any rung `.rs`, `spec.md`, `model.py`, `inputs/`, `README.md`,
`harness/`, `common/`, `patterns/`, `results/`, `pilot/`, `.web/`,
`RECAP_PHP.md`, `.memory-php/`, `.memory/`, `ph03`, `ph07`, `ph16`, `ph64`,
`ph00-smoke`, **`ph45` and `.temp/php34/`** (TASK_PHP_034 was running). No
`git add`, no `git commit`, no `/tmp`.

---

## §1 THE VERDICT, AND HOW THE PROOF CLOSED

`_033` left the plumbing discharging under `assume(false)` and named the
obstacle: *inside the body `it.index()` is the pre-`next` value*. Its advice was
to re-read `VerusForLoopWrapper::next`'s `ensures` first. **That was the right
advice and it was not quite the whole obstacle — there were two, and the second
is why the first attempt after it would also have failed.**

I measured both rather than reasoning about them, with **one question per
`fn`** (`.temp/php35/v/diag2.rs`) — because **Verus ASSUMES an `assert` after
checking it**, so in a single function a failed `assert` silently answers every
later one. `_033`'s attempt 6 read eight asserts in one body and reported three
failures; three of the five "passes" were consequences of the failures.

| | question | |
|---|---|---|
| Q1 | `sub.len() == n` inside the body, from the `requires` | **FAILS** |
| Q2 | `it.index() >= 1` | **FAILS** |
| Q3 | `it.index() < n` | passes |
| Q4 | `*x == sub[it.index()]` | passes |
| Q5 | `*x == sub[it.index() - 1]` | **FAILS** |
| Q6 | `it.history().len() == it.index()` | passes |

▶ **Q2/Q4/Q5 confirm `_033`: the body's `it` is PRE-`next`.** The free fact is
`sub[it.index()]`, not `sub[it.index() - 1]`.
▶ ⭐ **Q1 is the second obstacle and `_033` does not name it: a Verus `for` loop
runs under LOOP ISOLATION.** The enclosing `requires` and everything proved
above the loop are invisible inside it, so `recvd <= read_buf@.len()` has to be
restated as an invariant even though it follows from a line four above. This is
`PITFALLS.md`'s existing `while`-loop bullet, which nothing said also applies to
`for`.

The third obstacle was mine and the probe located it exactly. Attempt B's
unfold assert **passed** and only the join failed, which says `h` after
`h.wrapping_mul(31).wrapping_add(*x as u64)` was not syntactically the term
`foldb` recurses on — I had written the spec with `add(mul(acc, 31), ..)` while
`verus.rs` spells it `acc.wrapping_mul(31).wrapping_add(..)`. Spelling the spec
the way the shipped file already spells it closed it.

```
$ ./verus_run.py .temp/php35/v/fold_c.rs
verification results:: 4 verified, 0 errors

$ ./verus_run.py .temp/php35/v/twin.rs --multiple-errors 20      # the FULL verus.rs twin
verification results:: 10 verified, 0 errors
```

⚠ **F52 guard on that probe, because a verifying file proves nothing if its
`ensures` is vacuous.** Two mutations, both must fire and both do: seed the fold
at `1` instead of `0` → `postcondition not satisfied`; fold by `33` instead of
`31` → `invariant not satisfied`.

### 1.1 The identity half, which `ph07`'s and `ph16`'s controls do not check

`spec.md` says `O3 exact`, so a twin that verifies and compiles differently is
not a rung either. Measured, same pipeline as `harness/build.py::build_verus`:

```
  R4_v0_shipped      rustc   183 insn  05d6b672b204      <- the shipped R4
  R5_v0_shipped      verus   183 insn  05d6b672b204      <- the pin, reproduced
  R4_r4_fold_iter    rustc   209 insn  d71669d3c0e6
  R4_r4_fold_iter0   rustc   209 insn  d71669d3c0e6      <- §5.1 re-derived: `..n` == `0..n`
  R5_twin_fold_iter  verus   209 insn  d71669d3c0e6      <- ⭐ THE QUESTION: IDENTICAL
```

✅ The `R4 == R5` control comes back identical on the **shipped** pair too, so
the pipeline reproduces a pin whose answer is known before it is used on one
whose answer is not.
ⓘ `spec.md`'s `identity.why` says *182 instructions*; this control counts
**183**. Not a discrepancy: `asm.py` records `n_raw: 183` and `n_fn: 182` on the
same binary — `n_fn` drops one padding instruction. Both are self-consistent and
`md5_fn a7adc5d4e32f` matches.

### 1.2 What it is worth, and the two claims are separate

| | `vget_unchecked` | `get_unchecked` | total unchecked reads |
|---|---:|---:|---:|
| `verus.rs`, shipped | 1 | 13 | **14** |
| `r4_fold_iter` twin | 0 | 13 | **13** — one FEWER |
| `r4_fold_slice` twin | 0 | 14 | **14** — MOVED, not removed |

⚠ **`r4_fold_slice` moves a call site between two trusted items; only
`r4_fold_iter` removes one.** The task file's §5.2 claim — *"replaces
`vget_unchecked`'s only call site"* — is verified for `r4_fold_iter` and would
be an over-read applied to `r4_fold_slice`. Neither removes a *declaration*, so
the TCB item count stays at 6.

---

## §2 ⚠ THE TASK FILE'S "6.5 % CHEAPER" IS THE OTHER STATISTIC — §5 item 7

§1 of the task file says the candidate is *"6.5 % cheaper AND one trusted call
site smaller"*. §3 of the same file decides the headline statistic is **A1**.
**On A1 the candidate is −5.63 %, not −6.51 %.** −6.51 % is the two-point slope,
which is what `_033` §4.2's table is in. Both are right; the sentence mixes
them. The control prints both columns, labelled, and names A1 as the headline.

⚠⚠ **And this row is a sharper instance of open item 52 than `ph16` was.** On
`ph16` the two statistics differed by 0.72 pp. Here they differ by 0.45 pp on
the headline — but on `r3_copy_loop` **they do not agree on the SIGN**:

```
                        Ir/call   A1 vs R4ship   slope vs R4ship
R3 r3_copy_loop          1048.8        +5.08 %          -0.99 %     <- SIGN FLIP
```

A statistic choice that flips a variant's sign is not a presentational
preference. ▶ **The manager's §3 decision is not contradicted by anything I
measured** — the null-control argument is about `verus − unsafe`, which is 0 on
both rows here — but the reason to name the statistic is stronger than §3 makes
it sound.

---

## §3 ⚠⚠ TRAP 5 — `_033` §4.1 ATTACKED. ONE ATTACK LANDS.

`.temp/php35/falsify_41.py`.

**T1 LANDS. *"CLOSES, no residue"* IS AN ARITHMETIC IDENTITY, NOT EVIDENCE.**
`.temp/php33/probe_b.py::attribute` sums `R4 − R3` over the execution-count
classes **where the two differ**. Classes where they agree contribute exactly
zero, so

```
net = SUM_{k : a_k != b_k} (b_k - a_k) = SUM_{all k} (b_k - a_k)
    = tot_R4 - tot_R3 = meas
```

**for any pair of per-instruction dictionaries whatsoever.** The probe prints
`CLOSES` on four synthetic pairs, including one built from no mechanism at all
and one where R3 and R4 share not a single class. ▶ **The line tests the
PARSER, not the attribution** — and `probe_b.py` already tests the parser
separately and explicitly, on the line above it (`AGREE`). §4.1's *"CLOSES, no
residue"* should be withdrawn as evidence; the disassembly is what is left, and
it stands on its own.

**T2 DOES NOT LAND — THE MECHANISM SURVIVES, WITH A CORRECTED NUMBER.** Two
controlled swaps exist and the shipped control measures both:

```
CONTROLLED SWAP, R4 side (index -> iterator)    -1,404,508
CONTROLLED SWAP, R3 side (iterator -> index)    +1,416,792
§4.1's attributed FOLD term                     +1,376,079
R4 swap vs §4.1                                    +28,429   (+2.07 %)
R3 swap vs §4.1                                    +40,713   (+2.96 %)
the two swaps against EACH OTHER                   +12,284   (+0.875 %)
```

The two swaps agree with **each other** to 0.875 %, so the effect really is very
largely a property of the fold spelling and §4.1's unroll mechanism survives.
⚠ But the disassembly attribution is **2–3 % SHORT** of the controlled
measurement, and that shortfall was invisible *because the residual class
absorbed it by construction* (T1). ▶ **§4.1's "91.1 % of the gap" should be read
as 93.0 %** — the controlled R4-side swap over the measured gap — which is a
stronger claim than the one it replaces, arrived at by a method that can fail.

⚠ **The 0.875 % between the two swaps is itself a small finding**: the fold
spelling is not *exactly* transplantable, and ~12 k `Ir` of the effect is
context.

---

## §4 THE CONTROL, AND WHAT ITS NEGATIVES FOUND

`controls/spellings.py`, 9 variants, exit **0**, `problems: []`. Stage 3
reproduces all four shipped cells to **0.0000 %** against
`results-php/ph29-recvfrom-alloc.json`, so the variants are about this row's
benchmark and not another.

```
                        Ir/call   A1 vs R4ship   slope     kernel
R3 v0_shipped             937.6        -6.06 %   -6.51 %   218 fed2bdbf41eb
R3 r3_fold_index          994.3        -0.38 %   +0.00 %   199 dbfd867a9ba1
R3 r3_fold_fold           994.7        -0.34 %   +0.00 %   200 5fef264578b5
R3 r3_copy_loop          1048.8        +5.08 %   -0.99 %   236 10c4ee77ba68
R3 r3_head_shift          954.0        -4.41 %   -6.50 %   236 8e28d056f4e4
R4 v0_shipped             998.1        +0.00 %   +0.00 %   183 05d6b672b204
R4 r4_fold_iter           941.9        -5.63 %   -6.51 %   209 d71669d3c0e6   ADMISSIBLE, CHEAPER
R4 r4_fold_slice          998.1        +0.00 %   +0.00 %   183 05d6b672b204   admissible, TIE
R4 r4_head_array          989.1        -0.90 %   -0.00 %   173 cf1c7d5c1aee   INADMISSIBLE
```

⭐ **THE MIRROR IS SYMMETRIC AND IT SETTLES THE ROW.** Put R4's index walk into
R3 and R3 measures **−0.38 %** instead of −6.06 %; put R3's `for` over a
subslice iterator into R4 and R4 measures **−5.63 %**. **Neither rung's
`unsafe`-ness contributes anything measurable to this row's R3/R4 gap.**
⚠ `.iter().fold(..)` is **not** the same spelling as a `for` over `.iter()` — it
measures `R4ship` exactly.

`r4_head_array` is the one refusal and it is the documented one: `from_le_bytes`
is `is not supported` at the pinned vstd. **The control reproduces that error
text rather than inheriting `spec.md`'s claim of it.**

### 4.1 §H's negatives — 75 cases, 44 must-FIRE, 31 must-NOT-fire, ALL PASS

`.temp/php35/negatives_spellings.py`, groups A–H (`ph16`'s bar was 54). **Two
found real defects, both in machinery this file inherited.**

1. ⭐ **`kernel_fingerprint` returned `(0, 'd41d8cd98f00')` — the md5 of the
   empty string — for a binary that does not exist**, because `disasm` ignores
   objdump's return code. **Two such compare EQUAL**, on the one function in the
   file whose entire job is to decide *byte-identical*. Present in
   `patterns-php/ph16-fdset-index/controls/spellings.py` and in
   `.temp/php33/probe_b.py`. Guarded in `ph29`'s copy; **`ph16` NOT edited** —
   out of this task's scope, and every `ph16` call site is downstream of a build
   whose success is checked, so it is a latent hole and not a live wrong number.
2. ⭐ **`disasm`'s needle is a bare substring**, so any symbol whose mangled name
   merely contains `kernel` is folded into the digest. Measured: a crate called
   `nokernel` has a `main` that mangles to `…_8nokernel4main`, and the loose
   reading fingerprints it. `harness/measure.py::_sum_rows` does **not** have
   this hole — it matches on the function field — and `TASK_PHP_022` §3.2
   measured what the looser reading costs on the `Ir` side. `ph29`'s copy uses a
   bounded needle; group D pins all six deciding shapes.

⚠ **And one of my own must-fire cases fired for the WRONG REASON on its first
run.** The "false postcondition" Verus negative returned the right verdict off
`error: expected curly braces` — I had written `ensures` before `requires` and
Verus would not parse it. Fixed, and a second case now asserts the message
really carries a `verification results::` line. **A must-fire case that fires
for the wrong reason is worth nothing**, which is F52 inside the file that
exists to hunt F52.

⚠ Group G drives `harness/check.py::control_json_verdict` directly and confirms
the **gate itself** would refuse a sidecar regenerated without `--verus`
(`FAILED`), that the shipped one reads `CLEAN`, and that its
`derived_from_sha256` covers `spellings.py` and matches this tree.

---

## §5 THE GATE, READ OUT OF THE RECORD

**Four rounds, and each verdict below is read out of
`results-php/gate/ph29-recvfrom-alloc.json`, not out of a log.**

| | command | what had changed | verdict |
|---|---|---|---|
| 1 | `harness-php/gate.py ph29-recvfrom-alloc` | `controls/spellings.py` + `.json` added, `NOTES.md` §0/§8/§14 | **PASS** |
| 2 | `--tool report`, then gate | — | table re-rendered **byte-identical**; **PASS** |
| 3 | gate | `NOTES.md` §8b's trusted-call-site table | **PASS** |
| 4 | gate | `NOTES.md` section restructure (§6.6) | **PASS** |

```
verdict           PASS
failures          []
complete_run      True
contract_sha256   a5dfc7d473a223251e8c8c5e7e9a06e714679291447b3efe6b3ace19db20c38f
controls_json     {'spellings.json': 'FRESH'}
source_sha256     39 files          (38 before -- `controls/spellings.py` is the 39th)
loud              5 entries         (all pre-existing; none is mine)
```

⭐ **Round 1 did NOT fail on `[tables]`**, unlike `_033`'s chain, because
`contract_sha256` did not move — I did not touch `spec.md`. I ran `--tool
report` anyway per `PROTOCOL_PHP.md` §E and **the re-rendered table came back
byte-identical** (`md5 d957472fba6e…` before and after), which confirms the
staleness check rather than merely trusting it. `results-php/tables/…md` is
therefore unmodified in `git status`.

⚠ Stage 9b reads the new sidecar as **`FRESH`** and
`control_json_verdict` reads it as **`CLEAN`** — both independently re-checked
by negatives group G, which also confirms the gate would have said `FAILED` had
the sidecar been regenerated without `--verus`.

**Closing bracket, immediately after round 4:** `harness/measure.py
--check-stale` → **`66 record(s) examined, 0 STALE`**;
`harness-php/gate.py --tool measure --check-stale` → **`12 record(s) examined,
0 STALE`**. Identical to the opening bracket.

**Final `git status --porcelain`** — exactly five paths, and `.temp/` is
gitignored:

```
 M patterns-php/ph29-recvfrom-alloc/NOTES.md
 M results-php/gate/ph29-recvfrom-alloc.json
?? .tasks-php/TASK_PHP_035_REPORT.md
?? patterns-php/ph29-recvfrom-alloc/controls/spellings.json
?? patterns-php/ph29-recvfrom-alloc/controls/spellings.py
```

(plus `PITFALLS.md` in the separate `../LearnVeri` repo.)

⚠ `.temp/php35/` is **792 KB**, down from 118 MB: every binary, `.bin` and
callgrind dump deleted, every remaining file a generator, a hand-written Verus
source or a log, and `.temp/php35/NOTES.md` carries a regenerate command for
each.

---

## §6 ⚠ WHAT THIS CONTRADICTS — §5 item 7

1. ⚠⚠ **`.memory/02-bench-rules.md`'s reason 2 has a counterexample here, and
   the RULE it supports does not.** Reason 2 reads: *"R4 is a spelling too, and
   the R4 side is chained to the prover … so it usually cannot move."* On `ph29`
   the R4 side **can** move: `r4_fold_iter` verifies, is byte-identical, and is
   5.63 % cheaper. The *rule* (never re-ship) is untouched — indeed this row is
   the strongest argument for it, because a cost-selected R4 here would have
   silently shrunk the published gap by 5.63 pp. **What is weakened is the
   empirical premise**, and the task file's own §1 predicted the opposite branch
   (*"the row is reason 2 in its purest form"*). It is reason 2's
   **counterexample**, not its illustration.
2. ⚠ **`.memory-php/02-ladder.md`'s *"`ph29`'s negative spread is unexplained —
   nothing has been searched on that row"* is now stale**, and the explanation
   is **NOT** `ph16`'s F67 mechanism. F67 is *the two rungs are cheapest under
   DIFFERENT spellings, and the R4 side is degenerate*. On `ph29` the two rungs
   are cheapest under the **SAME** spelling and the R4 side is **not**
   degenerate. ▶ **F67 remains n = 1.** `ph29` is a second negative row with a
   second, different mechanism.
3. ⚠ **`ph29` is the first php row whose R4-side search found a cheaper
   ADMISSIBLE spelling.** `ph07`'s and `ph16`'s were degenerate; `ph03` and
   `ph64` are unsearched.
4. ⚠ **The two authorities phrase the second published quantity differently.**
   `.memory/02-bench-rules.md`'s table says *cheapest-found in-contract bound*,
   `inf(R3 found) − R4ship`; `spec.md`'s hashed `why` and the task file say *the
   R3-side span, cheapest-found to dearest-found*. The control publishes the
   **span**, whose low endpoint **is** `inf(R3 found) − R4ship` (here −6.06 %,
   the shipped R3 being the cheapest found), so both are satisfied — but a
   reader diffing the two documents will find them differently worded.
5. ⚠ **`NOTES.md` §0 said *"IT HAS MOVED TWICE"* while its own table listed
   five moves.** The count was never re-read as moves 3, 4 and 5 were appended.
   Corrected to six, **with the failure recorded rather than quietly fixed** —
   it is the disclosure failing in exactly the way the sentence it sits in warns
   about.
6. ⚠ **Two defects of my own, found by re-reading the rendered section rather
   than the diff, and repaired in the same re-gate**: my new section was
   numbered `§8a` when `NOTES.md` already had one, and the insert split §8's
   closing *"TWO THINGS IN THAT TABLE"* warning from §8's table. Renumbered
   `§8b` and moved after the pre-existing `§8a`
   (`.temp/php35/fix_notes_sections.py`, which refuses to run unless the file is
   in the shape it repairs). A third: *"nine variants, every one in contract"*
   was loose — all nine pass the token audit, but `r4_head_array`'s
   `in_contract` is **false** in the sidecar after the Verus stage refuses it.

---

## §7 WHAT I DID NOT DO, AND WHAT I AM UNSURE OF

1. **I did not re-ship a rung, and did not edit `spec.md`.** `contract_sha256`
   is unchanged at `a5dfc7d473a2…`. Verified against `git`: `a1cad85^` hashes to
   `28a92facffb3…` and `a1cad85` to `a5dfc7d473a2…`, exactly what §0's new row
   claims (PROTOCOL rule 6's addendum).
2. **No `.memory-php/` or `RECAP_PHP.md` edit** — manager-only. The entries this
   task implies are §6 above, plus: `ph29`'s spellings debt is **DISCHARGED**
   (so *"`ph03`, `ph29` and `ph64` REMAIN UNDISCHARGED"* becomes `ph03` and
   `ph64`), and `02-ladder.md`'s `ph29` audit numbers are still stale at
   `4 / 4 / 0` (the manager already owes that; the record says `12 / 4 / 8`,
   `present` 22).
3. ⚠ **The R4 side is searched but not exhaustively.** Four spellings, one of
   which is the shipped rung. `ph16`'s search ran seven from two agents. A fifth
   candidate nobody has tried could move it again, and the honest statement is
   *"an admissible cheaper R4 exists"*, not *"this is the cheapest R4"*.
4. ⚠ **Only two input shapes**, so the slope is a two-point fit exactly as
   `ph07` and `ph16` compute it. §2's A1-vs-slope disagreement is *caused* by a
   fixed term that a two-point fit cannot separate from noise, so a third shape
   would be worth more on this row than on either of theirs.
5. ⚠ **The unroll factor is an LLVM heuristic, not a language property.**
   `_033` §7.6 flags this and I did not test another toolchain either. Every
   number here is about `rustc 1.97.1 / LLVM 22.1.6`.
6. ⚠ **I did not edit `ph16`'s `controls/spellings.py`** despite finding two
   defects in it (§4.1). Both are latent there. It is a different row, it is
   gate-hashed, and editing it would re-gate `ph16` inside a task scoped to
   `ph29`. **Recommend a follow-up.**
7. ⚠ **`.temp/php33/probe_b.py` carries both defects too** and I did not fix it;
   `.temp/php35/twin_probe.py` imports it and wraps the fingerprint rather than
   correcting it in place, so `_033`'s evidence stays reproducible as written.
8. ⚠ **Unsure: whether `r4_fold_slice` should count as a result at all.** It is
   byte-identical to the shipped R4 and moves a trusted call site from one item
   to another without reducing the total. I recorded it as a tie with the
   movement spelled out, because `ph07`'s `r4_index0` is recorded as *"a third
   kind of result the bench rule has no name for"* and this is a fourth: **the
   trusted surface changes shape and not size.**
9. ⚠ **Unsure: whether my `_KERNEL_SYM` needle is right for a C rung.** Every
   variant here is Rust. A C binary's plain `kernel` symbol matches (group D
   pins it), but I did not run the control over a C cell and this row's control
   never needs to.
