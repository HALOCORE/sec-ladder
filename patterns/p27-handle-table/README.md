# p27 — handle table over per-record allocations

**The one TEMPORAL bug class in this project, and the only one safe Rust rejects
at compile time.** Every other pattern's bug is spatial (an index outside an
allocation) or logical (a wrong answer inside a live one). Here the address is
inside **no live allocation at all**: the record the handle names was `free`d.

```
window:  nops:u32 LE, then ops of  c:u8 (opcode) ; a:u8 (operand)
kernel:  tab[32] = {NULL} ; live[32] = {0} ; ntab = 0 ; p = 4
         for each declared op
             if len - p < 2: break
             c = buf[off+p] ; a = buf[off+p+1] ; p += 2 ; h = a
             c%4 == 0  OPEN : if ntab < TABCAP:                <<< in EVERY rung
                                  q = malloc(1) ; *q = a
                                  tab[ntab]=q ; live[ntab]=1 ; ntab++
             c%4 == 1  CLOSE: if h < ntab && live[h]:          <<< in EVERY rung
                                  free(tab[h]) ; live[h] = 0
             c%4 >= 2  READ : if h < ntab && live[h]:          <<< R1 omits the
                                  acc = acc*31 + *tab[h]           SECOND conjunct
         for j in 0..ntab: if live[j]: free(tab[j])            <<< the epilogue
         return acc*31 + ntab
```

## What is new here

- **The bug is temporal, and three things keep it that way.** `free` is a real
  `free` of a real per-record `malloc`, so the stale read leaves the allocation
  and Miri, ASan and `PointsTo` all see it — a slab-and-freelist spelling would
  have put it *inside* a live allocation, which is p17's LOGICAL class and the
  tree already has one. R1 keeps the slot bound `h < ntab`, so the bug is not
  spatial. And the liveness bit cannot be "the pointer is NULL", because the
  handle is an **integer** — the op stream comes out of a file and a file cannot
  name a pointer.
- **The free and the invalidation are ONE operation in safe Rust and TWO in C,
  and the bug is the third one — the asking — going missing.**
  `Option<Box<u8>>` is niche-optimised to a single pointer word, so the safe
  table *is* the hardened-C table minus C's separate `live[]` array; `tab[h] =
  None` frees the record and invalidates the handle together. C writes
  `free(tab[h]); live[h] = 0;` and then has to remember to ask.
- **The proof forces the line the C programmer forgot.** Deleting
  `live[h] = 0` from `verus.rs` does not fail a precondition — it fails the loop
  *invariant*, because `rec_free` has consumed slot `h`'s permission while the
  liveness array still claims the record exists. `NOTES.md` 10, mutant M2.
- **`R5 − R4 = 0.00000` kernel-exclusive on the first kernel in this project
  that allocates and frees** — and it took two source lines to get there. `vstd::raw_ptr::allocate`
  and `deallocate` carry no `#[inline]`, so an R5 that called them emits a
  GOT-indirect cross-crate `call` that R4 cannot produce and the pair measures
  `differ`; and `core::ptr::write` survives as a call at `-O0` where vstd's
  `#[inline(always)]` `ptr_mut_write` does not. `NOTES.md` 5.
- **The disclosure is deterministic and the noise is not, and both ship.**
  `adversarial-uaf` recycles the chunk before reading it, so R1 returns *the
  newer record's byte under the older record's handle* — the same number on
  every run and on both compilers. `adversarial-noreuse` **and
  `adversarial-many`** do not recycle before reading, so R1 reads glibc's
  safe-linked tcache `next` word and prints a **different number every run** — 24
  of 24 values distinct across 8 C cells × 3 runs, on each of the two inputs, and
  the gate prints four notes about it. Those rows are the measurement behind
  `.memory/03-measurement.md`'s constraint that a naked use-after-free is not a
  reproducible number, and `NOTES.md` 11a is their measured churn scope.
- **A claim this pattern made and then refuted.** The first draft indexed the
  handle table *checked*, asserting that `h < ntab` with `ntab <= TABCAP`
  already deletes rustc's bounds check. Three `panic_bounds_check` call sites
  survive at `-O3` — resolved by symbol through the GOT relocation, not by
  counting `call`s — and the checked spelling costs **41.62 Ir/call** on
  `small`. `NOTES.md` 4.
- **None of `R3 − R4` is the lifetime guarantee, and that is measured twice.**
  The gap is `+230.07 / +792.75` whole-program. A CLOSED per-function
  decomposition — the sum over *every* function equals the whole-program delta,
  so nothing else moved — puts `120.42` of it in the safe rungs' out-of-line drop
  glue and **`0.0000` in the entire allocator stack**; and an unsafe rung that
  keeps R3's five surviving bounds checks costs `+153.51` in the kernel where
  R3's whole in-kernel excess is `+109.65`, so **R3 pays 43.86 Ir/call LESS of
  the spatial tax than an unsafe rung carrying the same checks.** `NOTES.md` 5e
  and 5f.
- **The R4 side moved, in the direction that makes safe Rust look worse.** The
  unsafe epilogue was carrying a **dead** liveness store that R3 has no
  counterpart to — `−6.81 / −10.49 Ir/call`, one instruction per record alive at
  scope exit, confirmed independently by the 80-blob regression moving by
  `−1·nopen +1·nclose`. Deleting it raises the published `R3 − R4` by that much.
  `.memory/01-ladder.md` finding 18 is the blocker it avoids. `NOTES.md` 8a.

## What it is NOT

- **Not a representation split.** TASK_055 §2.8 predicted safe Rust would be
  forced onto `(slot, generation)` and would pay a wider handle plus an
  indirection plus a generation compare. It is not: the handle is a file byte, so
  it is an integer in every rung. As a direct consequence **TASK_055_REVIEW M1's
  arity problem does not arise** and p27 needs no `harness/` change — though the
  dead-argument escape was measured anyway, and it is free at `-O3` and costs
  `+3.0000` Ir/call at `-O0` (`NOTES.md` 1).
- **Not a `tcb_items = 2` pattern.** §2.5 predicted one; p27 publishes **7**,
  because a real pattern also indexes a table and reads a window. What survives
  of the alarm — and is the sharper claim — is that **none of the seven is the
  temporal property**. Calling vstd's allocation API directly would publish 5 —
  and **that is not a choice p27 has**: 18 of 18 shipped `spec.md` files pin
  `O3: exact`, so the vstd-pure configuration is not a rung, on the pattern with
  the largest ghost state in the tree. p27 **ships 7**, and the two extra items
  are a codegen device whose verified twins are vstd's own API. `NOTES.md` 6, 6b.
- **Not a perf row for the bug.** The use-after-free lives on `adversarial-*`
  inputs only, for two independent reasons: stage 2 requires benign cells to
  agree, and at `-O3` the stores into the recycled record are
  dead-store-eliminated, so an `-O3` perf row would not have executed the bug it
  claimed to model (TASK_055_REVIEW B1).

## Files

| | |
|---|---|
| `spec.md` | the kernel contract and every machine-readable pin |
| `NOTES.md` | the measurements, the trusted-item arguments, and what was refuted |
| `c/kernel.c` | R1 — no liveness conjunct on the READ path. THE BUG |
| `c/kernel_hardened.c` | R1h — the same file plus `&& live[h] == 1` |
| `safe_naive.rs` `safe_tuned.rs` | R2, R3 — `[Option<Box<u8>>; 32]`, no epilogue |
| `unsafe.rs` `verus.rs` | R4, R5 — `[*mut u8; 32]` + `[u8; 32]`, explicit epilogue |
| `model.py` | the independent reference model, two implementations |
| `inputs/gen.py` | deterministic generator; refuses a benign blob that reads a closed handle |
| `controls/` | the levers, the sweep fitter, the closed decomposition and the layout population |
