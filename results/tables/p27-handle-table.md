# p27-handle-table — results

Generated 2026-08-21T19:01:07Z from `results/p27-handle-table.json` (git `f03e6c5e9238`, working tree dirty).

## Toolchain

- **gcc**: gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
- **clang**: clang version 22.1.6 (https://github.com/llvm/llvm-project fc4aad7b5db3fff421df9a9637605b9ca5667881)
- **rustc**: rustc 1.97.1 (8bab26f4f 2026-07-14)
- **rustc_llvm**: LLVM version: 22.1.6
- **verus**: verus binary : /home/apt/tools/verus/verus
- **valgrind**: valgrind-3.27.1
- **objdump**: GNU objdump (GNU Binutils for Ubuntu) 2.42
- **host**: Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz, governor `powersave`

## Inputs

| file | n_iters | declared payload | present | truncated | model |
|---|---:|---:|---:|---|---|
| adversarial-many.bin | 200,000 | 204 | 204 | False | n_iters=200000 stride=196 n_blob=196 nwin=1 calls=200000 work/call=196B san=fires truncated=False expected=6582356636790626304 |
| adversarial-noreuse.bin | 200,000 | 36 | 36 | False | n_iters=200000 stride=28 n_blob=28 nwin=1 calls=200000 work/call=28B san=fires truncated=False expected=3390747988282288128 |
| adversarial-stride3.bin | 200,000 | 38 | 38 | False | n_iters=200000 stride=3 n_blob=30 nwin=0 calls=0 work/call=0B san=clean truncated=False expected=0 |
| adversarial-uaf.bin | 200,000 | 72 | 72 | False | n_iters=200000 stride=64 n_blob=64 nwin=1 calls=200000 work/call=64B san=fires truncated=False expected=4295919549966416896 |
| degenerate.bin | 200,000 | 102 | 102 | False | n_iters=200000 stride=94 n_blob=94 nwin=1 calls=200000 work/call=94B san=clean truncated=False expected=8089868669041868800 |
| large.bin | 20,000 | 15,624 | 15,624 | False | n_iters=20000 stride=244 n_blob=15616 nwin=64 calls=20000 work/call=244B san=clean truncated=False expected=15348810832415442499 |
| small.bin | 200,000 | 424 | 424 | False | n_iters=200000 stride=52 n_blob=416 nwin=8 calls=200000 work/call=52B san=clean truncated=False expected=1331635740038472661 |

## Declared idiom — what these numbers are numbers *of*

Every delta below is a difference between rungs that are meant to be spellings of one kernel. The pattern's hashed `slb-contract` block declares which spellings that means; **a rung that deviates is a different benchmark and its numbers are not comparable to these.**

- **required** — *per language:*
  - `c` — THE SAFETY LINE, and the only thing c/kernel.c omits: the liveness conjunct on the READ path, `if (h < ntab && live[h] == 1) {` in c/kernel_hardened.c. c/kernel.c writes `if (h < ntab) {` there and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.
  - `rust` — THE SAFETY LINE: the liveness test on the READ path, `if h < ntab && arr_get_unchecked(&live, h) == 1u8 {` in unsafe.rs and verus.rs. In the safe rungs it is the `Option` discriminant instead -- `tab[h].is_some()` in safe_naive.rs and the `Some(rec)` arm in safe_tuned.rs -- because safe Rust has no separate liveness array to test: `Option<Box<u8>>` is niche-optimised to one pointer word and IS the hardened-C representation. That is the pattern's whole subject; see the why key.
- **required** — *per language:*
  - `c` — THE LINE THE C RUNG MUST NOT FORGET, present in BOTH C rungs: `live[h] = 0;` immediately after the `free`. R1's bug is NOT that it skips this -- it does not -- it is that its READ path never asks. Splitting the free from the invalidation is what makes forgetting possible at all.
  - `rust` — the same line in the unsafe rungs, `arr_set_unchecked(&mut live, h, 0u8);` in unsafe.rs and verus.rs -- and at R5 the proof FORCES it: without it the loop invariant cannot be re-established, because `rec_free` has consumed slot h's permission while the liveness array would still claim it exists. In the safe rungs there is no such line, because `tab[h] = None` and `tab[h].take()` free the record and invalidate the handle in ONE operation.
- **required** — *per language:*
  - `c` — THE REAL `free`, in both C rungs: `free(tab[h]);`. Not a freelist push into a slab -- see the why key.
  - `rust` — THE REAL free, in all four Rust rungs: `std::alloc::dealloc(p, layout);` inside rec_free in unsafe.rs and verus.rs (character-for-character `vstd::raw_ptr::deallocate`, whose verified twin in verus.rs is vstd's own `deallocate`), and the drop of `Option<Box<u8>>` in safe_naive.rs and safe_tuned.rs.
- **required** — *per language:*
  - `c` — ONE ALLOCATION PER RECORD, in both C rungs: `malloc(RECSZ)`.
  - `rust` — ONE ALLOCATION PER RECORD, in all four Rust rungs: `std::alloc::alloc(layout)` inside rec_alloc in unsafe.rs and verus.rs, and `Box::new(a)` in safe_naive.rs and safe_tuned.rs. Rust's default global allocator calls `malloc` for `align <= 8`, so all seven rungs hit the same glibc, in the same size class, once per record.
- **required** — *per language:*
  - `c` — the handle table's extent is a COMPILE-TIME CONSTANT and the capacity guard is in every rung including R1: `if (ntab < TABCAP) {` in both C rungs.
  - `rust` — the capacity guard, in all four Rust rungs: `if ntab < TABCAP {`.
- **required** — *per language:*
  - `c` — the SLOT BOUND is in every rung including R1, so the bug is TEMPORAL and not spatial: `h < ntab` in both C rungs.
  - `rust` — the slot bound, in all four Rust rungs: `h < ntab`.
- **required** — *per language:*
  - `c` — the EPILOGUE frees every record still alive, so neither C rung leaks and the allocator state at the end of a call is the state at its start: `for (j = 0; j < ntab; j++) {` in both C rungs.
  - `rust` — the epilogue, in unsafe.rs and verus.rs: `while j < ntab {`. **safe_naive.rs and safe_tuned.rs deliberately do NOT have one** -- dropping the table is the epilogue, written by the language -- and that asymmetry is a measured result rather than an oversight (../NOTES.md 3).
- **required** — *per language:*
  - `c` — the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.
  - `rust` — the cursor guard, subtraction-first, in all four Rust rungs: `if len - p < 2 {`.
- **required** — *per language:*
  - `c` — the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.
  - `rust` — the opcode, in all four Rust rungs: `c % 4 == 0`.
- **required** — *per language:*
  - `c` — a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `acc = acc * 31 + SENT;` in both C rungs.
  - `rust` — the sentinel fold, in all four Rust rungs: `.wrapping_add(SENT)`.
- **required** — *per language:*
  - `c` — the fold is a serial Horner chain over `acc`, spelled with the literal multiplier: `acc = acc * 31 +` in both C rungs.
  - `rust` — the fold, in all four Rust rungs, spelled with the literal multiplier: `.wrapping_mul(31)`.
- **required** — the slot count is folded last so that a rung which opened a different number of records cannot produce the same checksum: `ntab` appears in the return expression of all seven rungs.
- **FORBIDDEN** — `memset(tab`
- **FORBIDDEN** — `realloc(`
- **FORBIDDEN** — `calloc(`
- **FORBIDDEN** — `Vec::with_capacity`
- **FORBIDDEN** — `Rc<`
- **FORBIDDEN** — `RefCell`
- **FORBIDDEN** — `ManuallyDrop`
- **FORBIDDEN** — `mem::forget`
- **FORBIDDEN** — `Box::leak`
- **FORBIDDEN** — `Box::into_raw`

> **Why**: POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. Here that clause is load-bearing and it IS the pattern. THE FREE AND THE INVALIDATION ARE ONE OPERATION IN SAFE RUST AND TWO IN C: `tab[h] = None` frees the record and invalidates the handle together, and `free(tab[h]); live[h] = 0;` is the same thing written twice, which is what makes forgetting the second half possible. So the safe rungs have no `live[]` array and cannot be asked to spell one, and the unsafe rungs have no `Option` and cannot be asked to spell that. THE HANDLE IS AN INTEGER AND THAT IS WHY NULLING IS NOT A DEFENCE: the op stream comes out of a file and a file cannot name a pointer, so the READ has an index and must consult something to learn whether the record is there. Nulling `tab[h]` on close would make a stale read a NULL DEREFERENCE -- a crash, a different bug class -- rather than a use-after-free, and it would leave the epilogue unable to tell a closed slot from a live one without the very bit it is trying to avoid carrying. `live[]` is a generation counter with slot reuse removed, and every real handle table carries one. THE FREE MUST BE A REAL `free`: if the slab were one allocation and 'close' were a freelist push, the stale read would be IN BOUNDS OF A LIVE ALLOCATION -- Miri would not flag it, `PointsTo` would license it, and the bug would be LOGICAL, which is p17's class and the tree already has one (TASK_055 §2.8 caveat 1). That is what `Box::into_raw`, `ManuallyDrop`, `mem::forget` and `Box::leak` are forbidden for: each is a route to holding a record past its free without the allocator knowing, i.e. to turning the temporal bug back into a logical one. `realloc`/`calloc`/`Vec::with_capacity` are forbidden because they change the allocator traffic and the pattern's fairness argument is that every rung makes exactly one allocation and one free per record; `Rc`/`RefCell` because they would move the liveness decision to run time inside the library and delete the comparison. WHAT IS DELIBERATELY NOT PINNED is how the liveness test is SPELLED -- `is_some()` in R2, a `match` arm in R3, `take().is_some()` in R3's CLOSE -- exactly as p14 leaves its fold loop unpinned: those are the R3-side levers, they cost zero TCB, and the pattern reports the cheapest one FOUND on a named input rather than a minimum (../NOTES.md 8).

> The gate checks that this declaration is **present** and hashes it into `contract_sha256`. It never checks that a rung honours it — that check would have to be textual and would fail open, and the threat model is honest mistake, not malicious author. TASK_016_REVIEW forked p05 with a **forbidden** R3 and got a complete green run with an unchanged `contract_sha256`. So this section is a claim about intent that a reader must check against the rung sources, not a verified property of the numbers below.


### Spelling audit (stage `0b`, reporting only)

Measured by the gate, not by this file — from `results/gate/p27-handle-table.json`, contract `a0e83e2f2ee2`.

`62` backticked spelling(s) over `6` rung(s) → **194** (spelling, rung) pair(s), **88** present — not the product, because a per-language entry is read against its own language's rungs only. Matching is `check.spelling_matches`: comments, string literals and Verus ghost clauses blanked, then all whitespace deleted.

- **FORBIDDEN — 2 hit(s)** of 20 spelling(s). *Decidable*: no rung may spell a forbidden token, in any language the entry names, so this number needs no reading of the entry's English. It is the only number here that a non-zero makes wrong.
  - `memset(tab` — **c/kernel.c** (c)
  - `memset(tab` — **c/kernel_hardened.c** (c)
- **required — 3 spelling(s) pin nothing**, 36 scoped-absent pair(s). *Not decidable*, and **a non-zero here is normal**: a `required` entry may quote a span in order to say it is absent, may quote a file name or a digest, and may scope itself to some rungs in prose ("R1 omits only …"). Read each line against the entry above it.
  - pins nothing — `vstd::raw_ptr::deallocate` (required[2], rust, 0 of 4 rungs)
  - pins nothing — `malloc` (required[3], rust, 0 of 4 rungs)
  - pins nothing — `align <= 8` (required[3], rust, 0 of 4 rungs)
  - absent — `if (h < ntab) {` (required[0], c, **c/kernel_hardened.c**)
  - absent — `if h < ntab && arr_get_unchecked(&live, h) == 1u8 {` (required[0], rust, **safe_naive.rs**)
  - absent — `if h < ntab && arr_get_unchecked(&live, h) == 1u8 {` (required[0], rust, **safe_tuned.rs**)
  - absent — `Option` (required[0], rust, **unsafe.rs**)
  - absent — `Option` (required[0], rust, **verus.rs**)
  - absent — `tab[h].is_some()` (required[0], rust, **safe_tuned.rs**)
  - absent — `tab[h].is_some()` (required[0], rust, **unsafe.rs**)
  - absent — `tab[h].is_some()` (required[0], rust, **verus.rs**)
  - absent — `Some(rec)` (required[0], rust, **safe_naive.rs**)
  - absent — `Some(rec)` (required[0], rust, **unsafe.rs**)
  - absent — `Some(rec)` (required[0], rust, **verus.rs**)
  - absent — `Option<Box<u8>>` (required[0], rust, **unsafe.rs**)
  - absent — `Option<Box<u8>>` (required[0], rust, **verus.rs**)
  - absent — `arr_set_unchecked(&mut live, h, 0u8);` (required[1], rust, **safe_naive.rs**)
  - absent — `arr_set_unchecked(&mut live, h, 0u8);` (required[1], rust, **safe_tuned.rs**)
  - absent — `rec_free` (required[1], rust, **safe_naive.rs**)
  - absent — `rec_free` (required[1], rust, **safe_tuned.rs**)
  - absent — `tab[h] = None` (required[1], rust, **safe_tuned.rs**)
  - absent — `tab[h] = None` (required[1], rust, **unsafe.rs**)
  - absent — `tab[h] = None` (required[1], rust, **verus.rs**)
  - absent — `tab[h].take()` (required[1], rust, **safe_naive.rs**)
  - absent — `tab[h].take()` (required[1], rust, **unsafe.rs**)
  - absent — `tab[h].take()` (required[1], rust, **verus.rs**)
  - absent — `std::alloc::dealloc(p, layout);` (required[2], rust, **safe_naive.rs**)
  - absent — `std::alloc::dealloc(p, layout);` (required[2], rust, **safe_tuned.rs**)
  - absent — `deallocate` (required[2], rust, **safe_naive.rs**)
  - absent — `deallocate` (required[2], rust, **safe_tuned.rs**)
  - absent — `deallocate` (required[2], rust, **unsafe.rs**)
  - absent — `Option<Box<u8>>` (required[2], rust, **unsafe.rs**)
  - absent — `Option<Box<u8>>` (required[2], rust, **verus.rs**)
  - absent — `std::alloc::alloc(layout)` (required[3], rust, **safe_naive.rs**)
  - absent — `std::alloc::alloc(layout)` (required[3], rust, **safe_tuned.rs**)
  - absent — `Box::new(a)` (required[3], rust, **unsafe.rs**)
  - absent — `Box::new(a)` (required[3], rust, **verus.rs**)
  - absent — `while j < ntab {` (required[6], rust, **safe_naive.rs**)
  - absent — `while j < ntab {` (required[6], rust, **safe_tuned.rs**)
- **no rung — 0 per-language entry/entries** name a language this pattern ships no rung for; rungs here are `c`, `rust`. Such a key used to be dropped silently, so the declaration read as constraining rungs that do not exist.


## Static + executed instructions

`Ir` is **callgrind per-function exclusive** for the kernel symbol. The whole-program total is deliberately absent: it moves with the size of the environment block and does not reproduce across shells (`.memory/03-measurement.md`). Static counts are given raw and padding-excluded; quote the padding-excluded one, and never quote either without the `Ir` beside it.

`Ir(kernel)` and `Ir(main)` are separate columns and are never merged: a `main`-exclusive count is not a kernel measurement wearing a different hat, and pairing one with a static count taken from the *other* symbol is two halves of two different measurements. **`Ir(main)` counts whatever else was inlined into `main`, and that is not the same set in every language**: the Rust rungs inline the whole payload decoder, while the C rungs leave it in `common/driver.c`'s own symbols. On `large` that is ~12.4 M instructions the Rust `main` rows carry and the C ones do not (~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is comparable **between Rust rungs only** — never Rust-vs-C, and never to an `isolated` row.

**Do not try to rescue it by subtraction.** A difference of two large numbers, each containing language-specific inlining, is not a measurement — `.memory/03-measurement.md` records the arithmetic that went wrong when TASK_002 tried.

**And the `isolated` kernel-exclusive figure is not a correction-free alternative — it is right only when every rung does its own work inside its own symbol.** This column counts instructions *inside the kernel symbol*, so whatever a rung calls out to — a libc routine, a standard-library function, an out-of-line helper — lands in no column of this table at all. Measured over the eight shipped patterns at `O3 / isolated / small`: on five of them the column ranks the rungs exactly as the whole-program marginal does (worst ratio disagreement 0.0052), on `p02-buffer-copy` it distorts a ratio by 0.19 without reordering anything, and on **`p08-overlap-move` and `p11-nul-scan` it reverses real rung comparisons** — p08's `c-gcc` reads 58% *dearer* than `c-clang` here and 33% *cheaper* on the marginal; p11's `safe_tuned` reads 30% *cheaper* than `unsafe` here and 21% *dearer* on the marginal and the wall clock.

**The check needs no disassembly.** Every rung runs the same input the same number of times, so rung-to-rung *ratios* of this column are directly comparable with the same ratios of `marginal_ir_per_call` in `results/gate/<pattern>.json`, which is a whole-program slope and therefore symbol-independent. Agreement means the kernel-exclusive figure is the whole cell; disagreement means it is not, and then only the marginal is comparable across rungs. **Where a pattern's rungs do call out, its `NOTES.md` is where the convention its published numbers are in is stated** — `p11-nul-scan` §3 and `p08-overlap-move` §2b are the worked examples. Read that before differencing two rows of this table.

### O3 / isolated — static counts are for the `kernel` symbol

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 154 | 146 | 0 | 638 | 168,913,692 | 68,801,730 | 3,000,056 | 300,056 | `a3b91914` | `a3b91914` | yes | xmm |
| c-clang | 147 | 141 | 1 | 599 | 173,918,253 | 72,836,379 | 2,800,055 | 280,055 | `e828ef00` | `84240989` | yes | xmm |
| safe_naive | 210 | 206 | 15 | 897 | 208,228,514 | 91,247,591 | 2,800,275 | 280,275 | `079519b5` | `b6620e25` | yes | xmm |
| safe_tuned | 213 | 209 | 15 | 913 | 206,325,767 | 90,607,591 | 2,800,275 | 280,275 | `05dbebfc` | `edff3df5` | yes | xmm |
| unsafe | 156 | 151 | 2 | 638 | 185,686,077 | 77,580,242 | 2,800,275 | 280,275 | `87ced153` | `087e3fd4` | yes | xmm |
| verus | 156 | 151 | 2 | 638 | 185,686,077 | 77,580,242 | 2,800,270 | 280,270 | `87ced153` | `087e3fd4` | yes | xmm |
| c-gcc-h | 155 | 149 | 0 | 646 | 172,899,171 | 70,617,758 | 3,000,056 | 300,056 | `3ec8a3fc` | `3ec8a3fc` | yes | xmm |
| c-clang-h | 146 | 142 | 1 | 599 | 174,914,776 | 72,905,833 | 2,800,055 | 280,055 | `f785f3fc` | `6777646c` | yes | xmm |

### O0 / isolated — static counts are for the `kernel` symbol

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `kernel` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 221 | 220 | 0 | 1,095 | 300,823,006 | - | 7,200,066 | - | `6cf0fa4a` | `6cf0fa4a` | yes | - |
| c-clang | 174 | 174 | 1 | 922 | 304,554,831 | - | 4,200,052 | - | `4039a8dd` | `263be7b7` | yes | - |
| safe_naive | 434 | 434 | 10 | 2,486 | 480,165,220 | - | 5,000,077 | - | `0a101c20` | `fad7694f` | yes | - |
| safe_tuned | 392 | 392 | 11 | 2,245 | 452,364,506 | - | 5,000,077 | - | `8498eb21` | `1cfb3c1c` | yes | - |
| unsafe | 277 | 277 | 6 | 1,466 | 467,171,168 | - | 5,000,077 | - | `dd5d146b` | `46718247` | yes | - |
| verus | 277 | 277 | 6 | 1,466 | 467,171,168 | - | 5,000,056 | - | `89480b10` | `9e5371fa` | yes | - |
| c-gcc-h | 227 | 226 | 0 | 1,116 | 309,962,380 | - | 7,200,066 | - | `1eeae974` | `1eeae974` | yes | - |
| c-clang-h | 178 | 178 | 1 | 942 | 310,647,747 | - | 4,200,052 | - | `386c75f5` | `4ad20858` | yes | - |

### O3 / whole — static counts are for the `main` symbol; the kernel was inlined away, so it has no symbol and no static count of its own here

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 379 | 375 | 1 | 1,578 | - | - | 160,994,054 | 64,476,670 | `3b2cd545` | `213679d9` | yes | - |
| c-clang | 385 | 376 | 0 | 1,627 | - | - | 178,061,497 | 75,087,507 | `6542cee2` | `6542cee2` | yes | xmm |
| safe_naive | 843 | 833 | 1 | 4,015 | - | - | 215,721,552 | 95,089,770 | `287489e7` | `0dfb2d56` | yes | xmm |
| safe_tuned | 845 | 835 | 1 | 3,999 | - | - | 213,172,995 | 94,018,823 | `791cf7ee` | `72ca70d8` | yes | xmm |
| unsafe | 796 | 785 | 1 | 3,711 | - | - | 197,814,198 | 83,534,536 | `1f5f1f52` | `93e8d001` | yes | xmm |
| verus | 812 | 798 | 1 | 3,727 | - | - | 196,858,874 | 83,365,482 | `75c1941c` | `c059e339` | yes | xmm |
| c-gcc-h | 381 | 377 | 1 | 1,595 | - | - | 166,512,673 | 66,909,590 | `232ea324` | `1f142ff9` | yes | - |
| c-clang-h | 381 | 373 | 0 | 1,633 | - | - | 181,160,767 | 75,816,961 | `58d2925d` | `58d2925d` | yes | xmm |

### O0 / whole — static counts are for the `main` symbol; the kernel symbol **survived** at this opt level, so nothing was inlined and the `Ir(kernel)` column is the real kernel cost

> `O0` rows exist to read the lowering. **No performance claim may rest on one** (`.memory/02-bench-rules.md`). Rust here is `opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to C `-O0`; the `O0d` axis (overflow checks on) is a separate build.

| rung | `main` instrs (nm extent) | pad-excl | trailing pad (insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| c-gcc | 100 | 100 | 0 | 426 | 300,823,006 | - | 7,200,066 | - | `d1c57d4e` | `d1c57d4e` | yes | - |
| c-clang | 67 | 67 | 0 | 277 | 304,754,831 | - | 4,200,051 | - | `73d6d3a7` | `73d6d3a7` | yes | - |
| safe_naive | 123 | 123 | 12 | 612 | 480,165,220 | - | 5,000,077 | - | `4d648185` | `2e75a48b` | yes | xmm |
| safe_tuned | 123 | 123 | 12 | 612 | 452,364,506 | - | 5,000,077 | - | `647bd6e5` | `fafdf07d` | yes | xmm |
| unsafe | 123 | 123 | 12 | 612 | 467,171,168 | - | 5,000,077 | - | `b32ec5df` | `c2e2e477` | yes | xmm |
| verus | 86 | 86 | 7 | 329 | 467,171,168 | - | 5,000,056 | - | `a331919f` | `c27df4da` | yes | - |
| c-gcc-h | 100 | 100 | 0 | 426 | 309,962,380 | - | 7,200,066 | - | `29c7be96` | `29c7be96` | yes | - |
| c-clang-h | 67 | 67 | 0 | 277 | 310,847,747 | - | 4,200,051 | - | `5078de89` | `5078de89` | yes | - |

## Structural identity — does a proof cost anything?

Compared in `isolated` builds, where the kernel is its own symbol, and on the **declared symbol extent** (`nm --print-size`), which is the function proper. `md5_raw` is objdump's grouping and also covers the alignment padding that follows the function, so two genuinely identical kernels at different alignments disagree on it and agree on `md5_fn` — the padding is reported separately rather than folded in. `md5_fn_norel` is the same bytes with pc-relative displacement fields zeroed, which is the honest (weaker) oracle when two binaries link the kernel's callees at different addresses — that happens at `O0`, where the Rust kernel still calls `Iterator::next`.

| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | counts (fn / pad-excl) | padding |
|---|---|---|---|---|---|---|
| unsafe vs verus | O0 | no | **yes** | no | 277/277 vs 277/277 | 6 B vs 6 B |
| unsafe vs verus | O3 | **yes** | **yes** | **yes** | 156/151 vs 156/151 | 2 B vs 2 B |

## Wall clock (secondary)

> taskset -c 3, interleaved round-robin, 30 reps, min and median; frequency scaling on, shared box. Frequency scaling is on and cannot be disabled without root; the box is shared and containerised. Wall clock is a sanity check on `Ir`, never the headline. Times include process start-up and reading the input file.

| rung | mode | large.bin min (ms) | large.bin median (ms) | large.bin spread | small.bin min (ms) | small.bin median (ms) | small.bin spread |
|---|---|---:|---:|---:|---:|---:|---:|
| c-gcc | isolated | 26.75 | 27.14 | 1.5% | 35.41 | 35.86 | 1.3% |
| c-gcc | whole | 27.95 | 28.25 | 1.1% | 36.26 | 36.56 | 0.8% |
| c-clang | isolated | 27.81 | 28.09 | 1.0% | 33.65 | 34.19 | 1.6% |
| c-clang | whole | 29.77 | 30.09 | 1.1% | 34.01 | 34.52 | 1.5% |
| safe_naive | isolated | 29.68 | 29.89 | 0.7% | 39.98 | 40.41 | 1.1% |
| safe_naive | whole | 31.44 | 31.90 | 1.5% | 40.07 | 40.62 | 1.4% |
| safe_tuned | isolated | 29.69 | 30.05 | 1.2% | 39.51 | 40.02 | 1.3% |
| safe_tuned | whole | 31.23 | 31.60 | 1.2% | 39.78 | 40.33 | 1.4% |
| unsafe | isolated | 30.23 | 30.55 | 1.1% | 37.42 | 37.77 | 1.0% |
| unsafe | whole | 31.16 | 31.68 | 1.7% | 38.17 | 38.64 | 1.2% |
| verus | isolated | 29.54 | 29.94 | 1.4% | 37.57 | 37.94 | 1.0% |
| verus | whole | 31.30 | 31.61 | 1.0% | 38.08 | 38.56 | 1.3% |
| c-gcc-h | isolated | 27.55 | 27.74 | 0.7% | 35.84 | 36.31 | 1.3% |
| c-gcc-h | whole | 28.49 | 28.83 | 1.2% | 36.74 | 37.12 | 1.0% |
| c-clang-h | isolated | 27.64 | 27.95 | 1.1% | 34.03 | 34.47 | 1.3% |
| c-clang-h | whole | 28.21 | 28.60 | 1.4% | 34.33 | 34.61 | 0.8% |

Every wall-clock cell is within the 10% min-to-median spread threshold.


## Cells and metrics not measured

Every cell in the matrix built, ran and produced static counts, digests and a checksum.

No `Ir` was collected for 6 (opt, mode, input) combination(s) — callgrind runs to a fixed plan (`harness/measure.py: CG_PLAN`), not exhaustively:
- `O0 / isolated` on `degenerate.bin`
- `O0 / isolated` on `large.bin`
- `O0 / whole` on `degenerate.bin`
- `O0 / whole` on `large.bin`
- `O3 / isolated` on `degenerate.bin`
- `O3 / whole` on `degenerate.bin`
