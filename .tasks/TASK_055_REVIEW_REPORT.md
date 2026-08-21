# TASK_055_REVIEW report — Probe 2, the `raw_ptr` feasibility claim

**Role:** research reviewer. **Scope:** Probe 2 of `.tasks/TASK_055_REPORT.md`
(§2.1–§2.8) and the `.memory/` records made from it. Probe 1 not under review.

**Nothing was fixed.** No tracked file was modified (`git status --porcelain`
empty at start and end of the measurement phase). All probes, logs and the
repro script are under `.temp/p55rev/`; `bash .temp/p55rev/repro.sh [all|a1|a2|a3|a4|a5|census]`
regenerates every number below. Binaries and callgrind blobs (103 MB) deleted
after the green run per `CLAUDE.md` constraint 6; `.temp/p55rev` is now 96 KB.

## Headline

**The probe's central claim survives, and the reason it is blocked does not.**

- **A1 lands for the report, against my expectation.** I wrote the ghost loop
  the report says it did not write. It verifies — **7 verified, 0 errors** — with
  **zero project-local `external_body`, zero `assume`, zero `assume_new` and
  zero `unsafe` tokens**. §2.5's TCB alarm is real, not scaffolding. The
  SMT cost is negligible *and n-independent*, which refutes the report's own
  stated worry.
- **A2 does not land as posed, and lands harder in a place nobody looked.**
  Callgrind agrees with native exactly. But the §2.7 fix is **insufficient**:
  the offset-16 checksum is a function of the **optimisation level**, and
  `build.py:67` puts both levels in one matrix. That is a blocker, and
  `.memory/03-measurement.md:807` records the insufficient rule as durable.
- **A3's feared build blocker does not exist**, and §2.6's mechanism is wrong for
  the formulation §2.8 proposes.
- **A4 does not land.** §2.4's identity survives a path-length change.
- **A5 lands.** The representation split cannot be normalised by the driver diff.

**PROTOCOL rule 3.** The §2.8 formulation is the engineer's and I attacked it
(A2, A5 are findings against it). The **`tcb_reach` proposal is the manager's,
and I am NOT clearing it** — see the section at the end. I am clearing §2.1–§2.5
and §2.6's *conclusion* (not its mechanism).

---

# Blockers

## B1 — §2.7's reproducibility fix is insufficient: the checksum is a function of `-O` level

`.tasks/TASK_055_REPORT.md:468-497` (§2.7) and
`.memory/03-measurement.md:807-818` (recorded, marked *measured; unreviewed*).

The recorded rule is: *"**Fold from offset 16** and gcc, clang and rustc all
print the same value on every run at `-O3`."* True — and it is the wrong
invariant. The value is stable across runs; it is **not** stable across
optimisation levels, and the gate builds **both**.

Measured on the probe's own `p2h_uaf16.c` / `p2h_rust.rs`:

```
gcc    -O0 : stale=2582767925679282152     gcc    -O3 : stale=6789584477807083544
gcc    -O1 : stale=2582767925679282152     clang  -O1 : stale=6789584477807083544
gcc    -O2 : stale=2582767925679282152     clang  -O2 : stale=6789584477807083544
gcc    -Os : stale=2582767925679282152     clang  -O3 : stale=6789584477807083544
clang  -O0 : stale=2582767925679282152     rust   -O1 : stale=6789584477807083544
rust   -O0 : stale=2582767925679282152     rust   -O2 : stale=6789584477807083544
                                           rust   -O3 : stale=6789584477807083544
```

`harness/build.py:67` — `OPTS = ["O0", "O3"]`. `harness/check.py:1264` iterates
`built.items()` keyed by `(cell, opt, mode)`, so **both values enter one
agreement set**, and `check.py:1289-1290` fires:

```
rep.fail("checksum", f"{name}: cells disagree: {sorted(vals)}")
```

Every cell also has to equal `model.py`'s single checksum (`check.py:1273`), and
`model.py` can only encode one of the two. **Stage 2 fails twice over.**

**Mechanism** (PROTOCOL rule 12 — not "it moved"). Disassembly of
`p2h-gcc-O3`'s `main`:

```
10e5: call malloc@plt           <- the first slab
1191: movups %xmm1,0x10(%rax)   <- a[16..31] = 16..31
123d: movups %xmm1,0x20(%rax)   <- a[32..47]
12e9: movups %xmm1,0x30(%rax)   <- a[48..63]      (the 0x00 store is dead, DSE'd)
1389: call free@plt
1393: call malloc@plt           <- the recycled slab
13ca: movzbl (%rdx),%edx        <- the fold loop: a REAL load
13f3: call free@plt
```

There is **no store loop into the second allocation at all.** `b[k] = 200-k` is
dead-store-eliminated: `b` is freed without a read the compiler can see, and
the stale reads carry the *first* allocation's provenance, so they are assumed
not to alias `b`. The stale read therefore returns the **original pre-free
bytes** (`6789584477807083544` = fold of `j` for `j∈[16,64)`, verified
arithmetically). At `-O0` the writes to `b` happen, and the stale read returns
the **recycled record's** bytes (`2582767925679282152` = fold of `200−j`).

Two consequences the report does not carry:

1. **The `-O3` row does not model the bug the pattern is about.** §2.8's bug is
   *"a stale handle reads a record that has been recycled"*. At `-O3` there is no
   recycled record — the compiler deleted it. The `-O3` cell models "reading your
   own freed bytes back", which is a strictly weaker phenomenon. The one cell the
   project publishes performance from is the one where the bug is optimised away.
2. Not constant-folding, which is the reviewer-checklist question I asked first
   and which came back **clean**: the literal `6789584477807083544` appears in
   none of the three binaries and the fold loop does real `movzbl (%rdx)` loads.

**The fix exists, and it is in the engineer's own notes, dropped from both the
report and `.memory/`.** `.temp/p55/NOTES.md:389-393`, inside the *withdrawn*
[P2-7]:

> The escape is precedented: put the UAF **only on adversarial inputs**, whose
> stdout is recorded rather than compared […] The perf inputs then exercise the
> *lifetime-safety machinery* and not the bug — which is the number worth having
> anyway.

That is correct and I verified both halves:

- `check.py:4933` calls `check_checksums(built, rep, good_models, indir)` —
  **`good_models`, not `all_models`.** Adversarial inputs never enter the
  agreement set.
- The precedent is shipped and measured: `results/gate/p06-rotate.json`,
  `adversarial-past48.bin/c-clang` records **four different behaviours across
  four cells** (`""`, `11406004536867057005`, `3987011862919846528`, `497`) and
  stage 4 records them with `rep.note`, not `rep.fail`.

[P2-9] withdrew [P2-7]'s *mechanism* (Vec growth) and, in doing so, took the
*correct conclusion* down with it. This is PROTOCOL rule 9's failure mode
exactly: the correction was one section away from the headline that got copied.

**What to change.** `.memory/03-measurement.md:807-823` should say: a UAF rung's
output is a function of the optimisation level as well as the allocator, so
**the UAF belongs on adversarial inputs only**; the offset-16 constraint is a
true but insufficient sub-fact and must not be recorded as the fix. Stated as
now, a future agent will build the pattern, pass the offset-16 check, and fail
stage 2 on the first `harness/check.py` run.

---

# Major

## M1 — a representation split cannot be normalised by the driver diff (§2.8 caveat 2)

`.tasks/TASK_055_REPORT.md:542-547` says the `driver.call_args` / `idiom`
machinery "assumes the rungs differ in one spelling" and leaves it there. It is
worse than that, and the mechanism is precise: **`driver.aliases` and
`driver.call_args` are keyed by *language*, not by rung**
(`harness/check.py:4405`, `:4415`), so every Rust rung shares one table, and
`harness/dloop.py:361-364` refuses a table whose highest kept position exceeds
the call's arity.

Measured on two minimal driver regions — R4 `kernel(handles, k)` vs R2
`kernel(slab, handles, k)`. **Ten alias/`call_args` combinations, none works:**

```
aliases=None                       call_args=None            -> identical? False
aliases=None                       call_args={'kernel':[0,1]}-> identical? False
aliases=None                       call_args={'kernel':[0]}  -> identical? False
aliases=None                       call_args={'kernel':[1]}  -> identical? False
aliases={'slab':'A','handles':'A'} call_args=None            -> identical? False
aliases={'slab':'A','handles':'A'} call_args={'kernel':[0,1]}-> identical? False
aliases={'slab':'A','handles':'A'} call_args={'kernel':[0,2]}-> ValueError: keeps position 2 but the call has 2 argument(s)
aliases={'slab':'handles'}         call_args={'kernel':[0,1]}-> identical? False
aliases={'slab':'handles'}         call_args={'kernel':[1,2]}-> ValueError
aliases=None                       call_args={'kernel':[1,2]}-> ValueError
```

**There is exactly one escape and it has a price:** R4/R5's driver must pass a
**dead `slab` argument** purely to match R2/R3's arity, after which
`call_args[rust][kernel] = [1,2]` normalises both to the same token sequence
(measured: `identical? True`). That is a live design constraint on §2.8 that the
probe does not name, and it collides with
`.memory/02-bench-rules.md`'s anti-partial-evaluation section — a dead argument
at R4/R5 is precisely the shape that section exists to police, and whether it
survives `-O3` is unmeasured.

**Answer to A5's actual question.** A functional-equivalence *argument* is not
what `.memory/02-bench-rules.md` asks for and is not needed: the gate already
**derives** equivalence on the measured domain, mechanically, via stage 2
(every cell's stdout equals an independent `model.py`) — and
`.memory/02-bench-rules.md:6-32` makes semantics criterion #1 with the checksum
column as its evidence. So a representation split **is** admissible, on one
condition: *R2/R3 and R4/R5 must agree with `model.py` on every non-adversarial
input.* What the argument would have to establish for `R2 − R4` to mean anything
is narrower than "functional equivalence": that the two representations compute
the same function **and do the same amount of work per record** — otherwise the
difference includes the extra indirection's cache behaviour and is not "the price
of a lifetime guarantee". The blocker is not the argument; it is the driver diff
above.

## M2 — §2.6's mechanism is wrong for the formulation §2.8 proposes

`.tasks/TASK_055_REPORT.md:439-457` concludes:

> **That is rustc's own move checker acting on a ghost token.** No Verus
> obligation fails […] Every existing R5 in this tree fails an SMT obligation
> instead; this is a structurally different R5 story and deserves its own
> paragraph wherever it lands.

**Measured false in the realistic shape.** `.temp/p55rev/a3_uaf_real.rs` is my
verified ghost-loop pattern (real permission map, real `deallocate`) with the
kernel call moved *after* the `deallocate`:

```
error: precondition not satisfied
   --> a3_uaf_real.rs:173:14
 40 |         wf(d@, *perms, n as int),
    |         ------------------------ failed precondition
173 |     let r2 = kernel(d.as_slice(), n, Tracked(&perms));
verification results:: 6 verified, 1 errors
```

**No E0382 anywhere.** The catcher is an ordinary failed Verus precondition, the
same as every other R5 in the tree.

**Mechanism.** §2.6's E0382 is an artefact of `p2b_uaf.rs`'s hand-unrolled
two-element shape, where `p0` is a bare local and `p0.into_raw()` moves it. In a
loop-shaped kernel the permissions live in a `Map<int, PointsTo<u8>>`, and the
join-back loop empties it with `tracked_remove` — a *mutation*, not a move. `d`
and `perms` are both still live at the call; what is false is
`perms.dom().contains(j)`, which is an SMT fact. Linearity still does the work
one level down (inside `Map`'s axioms), but it surfaces as an obligation.

Consequence: **this is not a new R5 story and does not deserve its own
paragraph.** It is also not "p08 wearing a different hat" — p08's catcher is a
spatial `requires`, this one is a *liveness* fact about a permission's domain.
The class is new; the *mechanism* is the tree's usual one. §2.6 as written would
have gone into `.memory/` as a false generalisation.

---

# Minor

## m3 — the just-landed recount fix overshoots by double-counting p01

`.memory/04-verus.md:248-280`. TASK_058 correctly caught that the original
command returned on the **first** `tcb_items` and dropped p01's `get_unchecked`
— I reproduced that independently (see clean negative 13). The replacement sums
**every** occurrence, and that is not right either:

```
shipped find() (first match): 65   <- the number 3a0458d shipped
R5 rung only  (verus.rs)    : 66   <- the sum of the patterns' PUBLISHED TCBs
every Verus file summed     : 68   <- the number now in .memory/04-verus.md
```

p01 is the only pattern with two verified files, and
`patterns/p01-array-sum/safe_naive_verus.rs:44,53` declares **its own
`load_input` and `emit`** — the *same two infra items* as `verus.rs`. The
corrected command counts them twice, so p01 contributes 5 while its own
`NOTES.md:452` publishes *"TCB: 6 lines across 3 items"* and
`results/gate/p01-array-sum.json`'s `verus.verus.rs.tcb_items` is 3.

**66 is the number consistent with what every pattern publishes.** Both the old
and new commands are wrong, in opposite directions, and the file's own rule —
*"check yours against one pattern by hand before trusting the total"* (`:271`) —
would have caught it against p01.

## m4 — §2.7's `same_chunk` fiat is attributed to the wrong cause

`.tasks/TASK_055_REPORT.md:492-494`: *"for the same addresses gcc prints `1`
while clang and rustc print `0`, because the pointer comparison folds
differently under UB."* At `-O0` **all three print `1`/`1`/`true`**; the split
appears at `-O1` and above for clang/rustc and only at `-O3` for gcc (see B1's
table). It is an optimisation-level artefact, not a compiler-identity one. The
operative advice ("never print or branch on it") is right and unaffected.

## m5 — what a `spec.md` can carry, and what the gate does with a fiat

Asked in the task file. `.memory/02-bench-rules.md:851`: *"A declared pin is
acceptable only for something a reviewer can check by reading `spec.md`
alone."* Neither §2.7 fiat qualifies — "the stale read window must begin at
least 16 bytes into the freed chunk" is checkable only against a specific
glibc's `malloc`, and `same_chunk` non-portability only by building at four
optimisation levels. A fiat in `spec.md` is **inert**: no stage reads it, so it
is a comment with a pin's authority. Given B1, writing the 16-byte fiat would
enshrine a constraint that is true and insufficient. **Recommendation: no fiat.
Put the UAF on adversarial inputs and the question does not arise.**

---

# The manager's `tcb_reach` proposal — attacked, and NOT cleared

Proposal: publish `tcb_reach ∈ {safe, local-external-body, vstd-axiom}` beside
`tcb_items`; p01 → `2 / safe`, p02 → `4 / local-external-body`, a `raw_ptr`
pattern → `2 / vstd-axiom`.

**(a) Is it decidable from the source? No — and it fails on the manager's own
worked example.** `local-external-body` *is* decidable and the gate already
computes it (`check.py:2514` `_mutation_targets`, `check.py:1897` `_is_trusted`).
`safe` vs `vstd-axiom` is not. **p01 is not `safe`**: its own
`NOTES.md:481` lists the vstd axioms it rests on — `slice::group_slice_axioms`,
`Vec::len`, `Vec::as_slice`, and the `assume_specification`s for
`u64::wrapping_add`/`wrapping_mul`. Every rung in the tree reaches memory
through *some* vstd axiom; `.memory/04-verus.md:200` already measured the scale
(**272 `external_body` items and 545 `broadcast` proof fns across 44 files**) and
concluded the second column *"does not discriminate, and it measures the wrong
thing."* The discriminator the manager actually wants is not "does it use a vstd
axiom" but "does the vstd axiom license an **unchecked memory access**" — and
that is a judgement per item, which is **the exact property that killed the
two-number proposal by census.** The proposal reintroduces it under a new name.

There is one mechanical proxy — *does the vstd item's body contain `unsafe`?*
(`raw_ptr::ptr_ref` at `raw_ptr.rs:620` is `external_body` wrapping
`unsafe { &*ptr }`; `Vec::len` is an `assume_specification` over a safe fn). But
computing it means running `vparse` over `~/tools/verus/vstd/` and re-deriving on
every pin bump. That is a large new harness surface for a reporting field.

**(b) Harness work / "could this happen by accident?"** The manager is right that
the accident test does not apply to a reported field. But the alternative — a
`spec.md` declaration — fails `.memory/02-bench-rules.md:851` for the reason in
(a): `tcb_reach: vstd-axiom` cannot be checked by reading `spec.md` alone.
**So the field is either underivable or an illegitimate pin.**

**(c) A cheaper answer that is only prose — yes, and it is half-landed.** The
defect is not the number; it is that `tcb_items` is read as a *safety ranking*
when it is a *count of this project's own axioms*. One sentence in
`results/tables/*.md` and `.memory/04-verus.md` — "`tcb_items` counts
project-local axioms; it is not a safety ranking and is not comparable across
patterns that reach unchecked memory by different routes" — costs nothing, adds
no pin and no stage. `.memory/04-verus.md:219-229` already carries the warning;
it just needs to reach the published tables. **This is what I recommend.**

**(d) Does the idle twin regime need a separate fix regardless? YES — and it is
worse than §2.5 says.** §2.5 says stage 5a *"prints the same sentence the macro
bypass produces"*. Reading `check_trusted_twins` (`check.py:3432-3437`):

```python
if not trusted:
    print(f"    {src}: no trusted item with an `ensures` or an `unsafe` body ...")
    continue
```

The `continue` precedes **both** `out[src] = …` assignments (`:3528`, `:3532`),
and both verdict arms (`:3722`, `:3735`) require `out` to be truthy. So for a
zero-trusted-item pattern the stage emits **no `rep.ok`, no `rep.fail`, no
`rep.shout`** — it is not "the same sentence", it is *silence*, and
`results/gate/*.json`'s `verified_twins` is `{}`. This is the one place the
threat model's test is passed cleanly: **could zero trusted items happen by
accident? Yes — TASK_009_REVIEW's macro bypass IS that accident**, which is the
whole reason `_is_trusted` was rewritten. The fix belongs in `check.py`, not in a
column: when a pattern pins `verus.obligations` and `_is_trusted` finds zero
items across every pinned file, that must be a `rep.shout` (or require a
`spec.md` `verus.no_trusted_items: "<why>"` string printed in the verdict), so
"no twin required" becomes a **declared** state rather than an inferred silence.

**Verdict on the manager's design: do not build `tcb_reach`.** Take (c) and (d).
(d) is required whether or not a `raw_ptr` pattern is ever built.

---

# Clean negatives — 21 named attacks that did not land

1. **A1: "the ghost loop cannot be written."** It can.
   `.temp/p55rev/a1_ghostloop.rs` — `allocate(n,1)` → split the `PointsToRaw`
   `n` times under a loop invariant into a `Map<int, PointsTo<u8>>` → build the
   `Vec<*mut u8>` descriptors → run p2d's kernel verbatim → **join all `n` back**
   → real `deallocate`. **7 verified, 0 errors.**
2. **A1: "it needs a project-local `external_body`."** It does not.
   `grep -n 'assume\|external_body\|assume_specification\|unsafe'` on the file
   returns hits in **comments only**. §2.5's `tcb_items = 2` claim survives.
3. **A1: "the SMT cost of a 4096-slot map is prohibitive."** The premise is
   wrong. 150 ms `smt-run`, **711,948 rlimit**, 1.3 s wall.
4. **A1: n-dependence.** Raising the bound from `n <= 4096` to `n <= 1_000_000`
   gives **the identical rlimit (711,948)** and the same 7/0. The loop is proved
   symbolically; the map's size never reaches the solver. The report's
   "unmeasured 4096-slot map" worry does not exist.
5. **A1: the join-back is the hard half.** It is not. `tracked_remove` +
   `leak_contents` + `into_raw` + `join` under `back.is_range(a0+k, n-k)`
   verifies. Two cheap gotchas: `into_typed` needs
   `broadcast use vstd::layout::align_of_u8` **restated inside the loop body's
   `proof` block** (the function-level `broadcast use` does not reach it), and
   `tracked_remove`'s `dom().contains(key)` needs one term-mentioning `assert`
   to fire the invariant's trigger at `j == k-1`.
6. **A2 as posed: callgrind replaces the allocator, so the checksum will move.**
   It does not. Offset 16, three runs each under
   `~/tools/valgrind/bin/valgrind --tool=callgrind`: gcc, clang and rustc all
   print `6789584477807083544`, **identical to native**. Stage 2's cross-cell
   agreement is not broken by valgrind.
7. **A2: valgrind's allocator is irrelevant.** Also false, and the control proves
   the tool was actually exercised: at **offset 0** native gives three different
   values per run while callgrind gives `5067115129635832889` ×3 — stable and
   different from every native run. Valgrind does replace the allocator; it just
   does not matter at offset 16, because at `-O3` those bytes never came from the
   allocator.
8. **A2: ASLR.** `setarch -R` vs not: identical (`6789584477807083544`).
9. **A2: the environment block** (`.memory/03-measurement.md:1122`).
   `SLB_PAD` at 0 / 400 / 800 bytes: identical. Also argv at 0 / 2 / 32 bytes:
   identical.
10. **Reviewer checklist: "did anything get constant-folded?"** No. The literal
    `6789584477807083544` appears in **none** of the gcc/clang/rustc `-O3`
    binaries, and the fold loop does real `movzbl (%rdx)` loads through the stale
    pointers.
11. **A3: "a linearity-caught bug cannot produce a failing proof mutant."**
    Refuted with the gate's own machinery (`vparse.delete_conjunct`), on a
    zero-trusted-item file: deleting `kernel.ensures[0]`
    (`r == fold_perms(*perms, n as int)`) → **6 verified, 1 errors**; deleting
    `kernel.requires[0]` (`wf(d@, *perms, n as int)`) → **6 verified, 1 errors**.
    **Two mutants, both fail.** The mutation stages test clause
    load-bearingness, not the bug, so the bug's catcher is irrelevant to them.
12. **A3: stage 5c would certify nothing at zero trusted items.** It would not.
    `_mutation_targets` (`check.py:2514`) returns `verified` extras from
    `verus.clause_deletion_extra_items`, which **defaults to `[kernel_item]`**,
    so `n = 1 > 0` and the `n == 0` hard failure at `check.py:2745` does not
    fire.
13. **The manager's `3a0458d` recount arithmetic.** Re-ran the shipped command
    against the tree as it stood at that commit: **62 items / 16 patterns**,
    exactly as claimed. The arithmetic was right; the *command* was not — and
    TASK_058 had already caught that independently before I got here (see m3 for
    what its fix got wrong).
14. **A4: "the byte-identical claim is a draw of size one that a path-length
    change will break."** It does not break. Source path 61 → 164 bytes:
    `p2c` **exact/exact**, `p2d` **exact (`-O3`) / norel (`-O0`)** at *both* path
    lengths, same `md5_fn` throughout (`20be44aa70de`, `bf2e77403da6`/
    `211f72a4dd0f`). §2.4's identity claim is robust.
15. **A4 sub-attack that partly landed, as a confirmation not a finding.** The
    R5↔R4 kernel **address offset** does move with path length (`p2c -O0`:
    −192 → −304), confirming `.memory/03-measurement.md:839`'s
    "the offset is a SOURCE-PATH-LENGTH artefact". So §2.4 licenses a *structural*
    identity claim and still licenses **no timing null** built on the pair.
16. **§2.1 reproduces.** `SharedReference::new` and `as_ptr` are private
    (two `E0624`s). The stack-local route really is closed.
17. **§2.2 reproduces.** `p2b_heap.rs` → 2 verified, 0 errors.
18. **§2.4's loop probe reproduces.** `p2d_loop.rs` → 3 verified, 0 errors.
19. **§2.6's E0382 reproduces on the file it was measured on.** `p2b_uaf.rs`
    gives `error[E0382]: borrow of moved value: p0`. The observation is real; only
    its generalisation is wrong (M2).
20. **Stage 7 blocks a UAF C rung.** It does not. `gcc -O1
    -fsanitize=address,undefined` on the probe gives
    `ERROR: AddressSanitizer: heap-use-after-free`, exit 1 — exactly what
    `model.py`'s `sanitizer_expect: "fires"` declares (`check.py:4568`), and the
    `got != want_out` comparison at `:4585` is scoped to non-adversarial inputs,
    so an aborting adversarial cell is fine.
21. **The withdrawn `Vec`-growth explanation.** The withdrawal is **complete**.
    `.temp/p55/NOTES.md:429` states it is WRONG with the counter-measurement,
    §2.7's parenthetical carries it, and `.memory/03-measurement.md:815` says
    *"not allocator growth (that first explanation was measured and withdrawn)"*.
    No surviving copy anywhere in `.memory/`, `.tasks/` or `RECAP.md`.

---

# Recommendation

**The pattern is buildable and should be built — but not as §2.7 specifies it.**

1. **Fix B1 before anything else.** `.memory/03-measurement.md:807-823` must
   say: put the UAF on **adversarial inputs only** (precedent:
   `results/gate/p06-rotate.json`'s `adversarial-past48.bin/c-clang`, four
   behaviours in four cells, recorded not required). The offset-16 constraint is
   a true sub-fact and must not stand as *the fix*.
2. **Land (d) in `check.py`** — zero trusted items must shout, not fall silent.
   Required regardless of whether this pattern is built.
3. **Take the prose fix (c); do not build `tcb_reach`.**
4. Correct §2.6's mechanism (M2) before any of it reaches `.memory/`.
5. Budget for M1's dead-argument constraint in the R4/R5 driver, and measure
   whether it survives `-O3`.
6. Fix m3's double-count to **66**.

§2.5's alarm is real and now measured rather than asserted: a `raw_ptr` pattern
does publish `tcb_items = 2` with a fully verified permission-splitting loop and
no project-local axiom at all.
