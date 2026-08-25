# TASK_091 — `p28`'s `wf` is ESTABLISHABLE: report

**Role: research engineer (probe).** Ran concurrently with `TASK_089`.
**UNREVIEWED.** Nothing written outside `.temp/t91/`; no `check.py`, no
`measure.py`, no `--cargo`.

**PROTOCOL rule 2 running count: 256 → 257.**

---

## ✅ IT CLOSES, FIRST ATTEMPT, AND THE BAR IS THE REAL ONE

```
u1u2                   3 verified, 0 errors
v28_base               4 verified, 0 errors    <- TASK_086 reproduces
v28_ctor               8 verified, 0 errors    <- FIRST ATTEMPT
ctrl_A_main_false      7 verified, 1 errors
ctrl_B_push_false      7 verified, 1 errors
ctrl_C_alloc_false     7 verified, 1 errors
```

**`main` is `new()` → `push_front`×3 → `assert(ptrs@ =~= seq![pa,pb,pc])` →
`step_next`×2 → `unlink(&mut d, pb, Ghost(1))`** — a **3-node list with the
MIDDLE node unlinked**, and `unlink`'s three `requires` discharged **from
`push_front`'s postcondition alone**. It also **compiles and runs**
(`--compile` → 8/0; prints `30` then `20`, both correct). **TCB grep over
`v28_ctor.rs` → zero hits.** 355 lines, 1.62–1.68 s.

## ⚠⚠ The load-bearing clause — p28's `is_heap`-multiset analogue

**Delete the injectivity conjunct** and `fake3` passes: **ONE node with
`prev = next = itself`, declared `len = 3`, `ptrs@ = [p,p,p]`** satisfies every
remaining conjunct, and `main` discharges `unlink`'s **entire** precondition from
it. Both verify.

```
ctrl_inj_off   5 verified, 1 errors   <- fake3 PASSES
ctrl_inj_on    5 verified, 1 errors   <- fake3 FAILS
```

**Third instance of the same shape**, after `TASK_085`'s
`ensures res ==> P` with a body of `false` (2/0) and `TASK_090`'s deleted
multiset clause letting a body that zeroes the array satisfy `is_heap`.

## ⚠⚠ THE MANAGER'S PREDICTION IS CONTRADICTED — 0 FOR 3

**Injectivity was NOT the hard part.** It cost **one 8-line `proof fn` with a
single `if`, no loop, no induction** — reduce it to *"the fresh address is not a
KEY of the permission map"*, which `PointsTo::is_disjoint` settles in one call.

**The real difficulty, in order:**

1. ⚠ **`Dll` needs EXEC fields — a CONTRACT CHANGE, not a proof step.**
   `push_front` must branch on *"is the list empty?"*, and `TASK_086`'s `Dll`
   knew the length only in **ghost**. `head: *mut Node` + `len: usize` added;
   `wf` gains two conjuncts. **Budget this in `spec.md`.**
2. ⚠⚠ **THE NAIVE INJECTIVITY ROUTE IS STRUCTURALLY IMPOSSIBLE** —
   `is_disjoint` takes **`&mut self`**, so it **cannot be called per-`i` inside
   `assert forall|i| … by`**. **Not a hint problem; a goal-reformulation
   problem.** ⚠ **"This is the trap that would have burned a session."**
3. One extra `wf` conjunct (key discipline,
   `m.dom().contains(a) ==> m[a].ptr().addr() == a`) makes step 2 legal. It
   **STRENGTHENS `wf`, so `unlink` got HARDER, not easier** — it needed
   `d.len -= 1` plus one `dom =~= dom` assert to survive.

## Probes 2 and 3 — new; `TASK_086` ran neither

From the **LINKED** binary, all reproduced byte-identical by `build.sh`:

| kernel | size | md5 | `Ir`/victim | static instrs |
|---|---|---|---|---|
| `k28_checked` (safe index arena) | 138 | `1dd30e47…` | **20.003** | 20 |
| `k28_unchecked` | 202 | `32fa3aaf…` | **11.503** | 11.5 |
| `k28_rawptr` (field stores) | 129 | `cf2018c3…` | **7.507** | 7.5 |
| `k28_rawptr_rmw` (whole-struct RMW) | 129 | `7490834e…` | **7.507** | 7.5 |

**Zero-parameter: each `Ir`/victim IS the static loop-body count, to three
decimals**, and holds at N = 1024 / 4096 / 8192.

- ✅ ⚠ **THE WHOLE-STRUCT READ-MODIFY-WRITE THAT VERUS FORCES IS FREE.**
  `vstd::raw_ptr` has **no field-level mutator**, so R5 must
  `ptr_mut_read` → edit → `ptr_mut_write` the whole 24-byte `Node`. Cost against
  the natural R4 field store: **1.00 `Ir` per CALL out of 50 232** — and a swap
  test (reordering the driver's `match` arms) **flips the sign to −3.00**,
  proving it is **driver string-dispatch, not kernel**. Bounded at **≤0.0015
  `Ir` per unlink**. ⚠⚠ **So R5 needs NO local `external_body` field-store
  wrapper to stay identical to R4** — which is the feasibility question p28's
  R4/R5 pair turns on.
- **The safe tax is 8.5 `Ir`/victim (1.74×) — but *"the bounds check costs
  8.5"* would be WRONG:** 6 are the three `cmp/jbe`, ~1 is the unroll the panic
  exits block, ~1.5 is register pressure (`push/pop %rbx` for the panic paths).
  **Same shape as p35 and p05.**
- ⚠ **The CHECKED kernel is SMALLER — 138 B against 202 B** — because the
  unchecked one is 2× unrolled. **Do not read size as cost.** (p19 showed the
  same thing at 76 B vs 173 B.)
- ⚠ **4.0 of the 12.5 R3→R4b gap is INDEX SCALING, not checking** — three
  `shl $0x4` that the pointer list does not pay. **A p28 whose R3 is a safe
  index arena would misattribute it.** **A design warning for whoever builds
  it.**

## Problems

None blocking. Two dead ends, one minute each: `print_u64` needs an explicit
`use vstd::pervasive::print_u64`, and `Ghost(seq![…])` in a struct literal fails
with *"unexpected ghost block attribute None"* — use
`let ghost s = seq![…]; Ghost(s)`.

## ⚠ Unsure / not done — and the first item is p28's remaining risk

- ⚠⚠ **NO `deallocate`. `alloc_node` drops the `Tracked<Dealloc>`; the probe
  LEAKS.** Verus permits it and the proof is sound, **but a shipped p28 must
  thread `Dealloc` like p27 — and THAT IS WHERE p28's TEMPORAL BUG CLASS
  ACTUALLY LIVES, not in `unlink`.** `unlink` currently keeps the victim's
  `PointsTo` in the map forever. **Ranked by the probe as p28's remaining risk,
  and it is untested.**
- `push_front` is the only growth mutator; no `push_back` / `pop` / cursor. `wf`
  says nothing about `val`.
- ⚠ `v28_base.rs`'s `unlink` and `v28_ctor.rs`'s are **not the same function** —
  the second runs against a **strictly stronger** `wf`.
- Probes 2/3 are **throwaway kernels, not rungs**: no C rung, no clang column, no
  `-O0`, no Miri, no ASan/UBSan harm run. **The temporal bug class was not
  demonstrated at C level** (TASK_086 did not either).
- **Only the SLOPE transfers; every intercept above is a property of this
  binary.**

## Memory updates owed (manager applies, after review)

1. `global layout` works on `#[repr(C)]` structs with raw-pointer fields.
2. `is_disjoint`'s `ptr() as int` ensures yields `.addr()` distinctness with a
   one-line body.
3. ⚠ **`&mut`-taking tracked axioms cannot be called inside
   `assert forall … by`**, so quantified freshness must be reformulated as a
   single `dom` fact.
4. **`raw_ptr`'s whole-struct RMW is free after SROA.**
