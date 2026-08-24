# TASK_086 — batched row selection: report and RANKED QUEUE

**Role: research engineer (selection probe).** Ran concurrently with `TASK_084`,
`TASK_085_REVIEW` and `TASK_084_REVIEW`. **UNREVIEWED** except where marked
manager-verified. Nothing written outside `.temp/t86/`; no `check.py`, no
`measure.py`, no `--cargo`, no `git add`.

**11 rows probed** (10 chosen + `p23`'s assigned loop probe). **Every ranked row
carries at least one thing that was RUN.**
**PROTOCOL rule 2 running count: 237 → 241.**

**Declared `Ir` convention, in advance (probe 3):** marginal **whole-program**
`Ir` per kernel call, `n_iters` 100↔200, callgrind `I refs:` program total,
`rustc -O -C codegen-units=1`, every kernel `#[inline(never)]` (**inline mode
`isolated`**), payload from `argv` at run time. **Whole-program, not
kernel-exclusive — deliberately**, because the catalogue records two measured
cases (p13, p48) of that column erasing or reversing a comparison.

---

## ⚠⚠ THE INSTRUMENT DEFECT — read this before using probe 2 again

**#238 — PROBE 2 AS WRITTEN HAS A FALSE-POSITIVE MODE, AND IT PRODUCES EXACTLY
`p45`'s VERDICT.** ✅ **MANAGER-VERIFIED on an independent minimal case**
(`.temp/mgr86/reloc.rs`, `README.md`): two `#[inline(never)]` kernels whose only
difference is **which function they call**:

```
 .o     k_calls_a  d96e2a3350186ba3f3e7f13dcde2fe2e
 .o     k_calls_b  d96e2a3350186ba3f3e7f13dcde2fe2e   <- IDENTICAL
linked  k_calls_a  9fd9563c2de5747d7883758f234d8b5c
linked  k_calls_b  9a346d637748fbb3640af34ec205e7ba   <- differ
```

The relocated field is **zero in the object file**. The agent found it on
`k24_heapify_checked` / `k24_heapify_unchecked` (62 B, identical md5 in the `.o`;
58 B and distinct once linked).

**So two rungs differing only in a call target, a global address or a
jump-table base WILL COLLIDE and be reported as "one rung wearing two names."**

✅ **`p45`'s kill still stands** — `.temp/p45pat/cost_rs.rs`'s `k_plain` /
`k_unchecked` are leaf arithmetic folds over `&[i32]` with **no call and no
global**, so they have no relocations to hide a difference in.
✅ **`p15`'s refusal is unaffected** — a false-*positive* collision mode cannot
turn a PASS into a FAIL, and p15's probe 2 **passed** (206 B vs 146 B).
✅ **This report's own probe-2 numbers are sound** — all taken **from the linked
binary**.

**The fix is one word in the recipe: LINK FIRST, or read `readelf -rW`.**

⚠ **A first attempt at verifying this was wrong and looked right.** Both symbols
live at **address 0 of their own section**, so extracting by address returned the
same 550 bytes for both by construction. **Extract per SECTION
(`objcopy --only-section=`), not by address, in an object file.**

---

# THE RANKED QUEUE

### 1. `p19` — protocol state machine — **BUILD**

- **Probe 1 — boundary, and there are two:** R3-vs-R4 *and* **inside the safe
  class** (p47's shape): `table[st*256+b]` against `table[(st&7)*256+b]`.
- **Probe 2 (linked):** `k19_masked` 193 B `b2b052c3…` · `k19_unchecked` 173 B
  `19c603ad…` · `k19_checked` 76 B `758b20ed…` · `k19_rows` 73 B `5837f4b0…`.
  **No collision.**
- **Probe 3 — a per-byte SLOPE, not a level:** `45102 / 40994 / 27695 / 23604`
  marginal `Ir`/call at n=4096 → against the same R4: naive **+5.25 `Ir`/byte**,
  2-D rows **+4.25**, masked **+0.999**. Mechanism from `objdump`:
  `k19_checked` carries `cmp $0x8,%r9 / jae <panic>` **inside** the loop — `st`
  is loop-carried and data-dependent so it cannot be hoisted, and the exit edge
  blocks unrolling; the panic body is out of line, which is why the *checked*
  section is **76 B against 173 B — smaller code, 1.91× the instructions**.
  `k19_masked` is 4× unrolled with exactly one extra `and $0x7` per byte, and
  **+0.999 measured is that one instruction**.
- **Probe 4:** `::get_unchecked` → **0 hits** in the pinned vstd. Ordinary
  `external_body` route; the twin (`table[i]`) is writable. **Not p15's
  obstacle.**
- **Bug class:** OOB table read from an out-of-range state = `index >= len`;
  nearest sibling **p36**. The masked rung is **p09's `q & 31` used as the FIX
  rather than the bug**, and the three-way behaviour matrix (panic /
  silent-remap / OOB) is not p09's.
- **Harm, RUN** (gate stage-7 recipe): `gcc -O2` **exit 139 SIGSEGV**;
  ASan/UBSan **`harms.c:55: runtime error: index 200 out of bounds for type
  'uint8_t [8][256]'`**; the non-adversarial run is clean 18/18 on both, so the
  harm is **adversarial-only**.
- ⚠ **Kill risk:** the memory-unsafe framing may be contrived — a textbook
  "state confusion" CVE is a *logic* bug with no OOB, and if §0 settles on that
  shape the row loses its boundary and dies **p31's death**. The harm as built
  needs a table entry naming a nonexistent state.

### 2. `p46` — bignum limb add/mul — **BUILD**

- **Probe 1:** R3-vs-R4 on the schoolbook inner step; three bounds checks per MAC
  (`b[j]`, `out[i+j]` read, `out[i+j]` write).
- **Probe 2:** `k46_checked` 296 B `a73eda77…` vs `k46_unchecked` 126 B
  `daca171e…`.
- **Probe 3:** N=64 limbs → 4096 MAC steps/call. `62400.00` vs `41720.00` →
  **+20680 = +5.05 `Ir` per MAC step, +49.6%**. Slope in `n·m`.
- **Probe 4:** `unchecked_mul` / `carrying_add` / `widening_mul` → **0 hits**.
  Wrapper route, twin writable.
- ✅ **R5, RUN: `7 verified, 0 errors`** (`v46_carry.rs`). `lemma_mac_fits`
  (`by (nonlinear_arith)` + `by (compute)`) plus `mac` with a **value-level**
  postcondition `lo + hi·2⁶⁴ == a·b + c + carry` — ⚠ **stronger than any
  `ensures` currently in the tree, all of which are bounds facts.** Two traps:
  both casts need `#[verifier::truncate]`, and the `nat`-cast spelling of the
  split **fails** `by (bit_vector)` while the `u128` + `requires` spelling
  passes.
- **Bug class:** limb-bound/carry → `index >= len` on `out[i+j]`; shares with
  **p05**.
- ⚠ **Kill risk:** the *full product* postcondition needs a nested-loop
  invariant over partial sums; **the step and the inner loop's length invariant
  were proved, the product was not.** If §0 promises functional correctness of
  the multiply it may not close in one session.

### 3. `p23` — quicksort partition — **BUILD; its kill risk is now DEAD**

⚠ **The manager's least-sure call, answered: the loop invariant is not the risk
it was assumed to be.**

- ✅ **Assigned probe, RUN: `4 verified, 0 errors`, FIRST ATTEMPT**
  (`v23_partition.rs`). Two moving indices, `decreases j - i`, invariant =
  multiset preserved + `∀k<i: v[k] ≤ pivot` + `∀k≥j: v[k] ≥ pivot`,
  postcondition = multiset preserved + both sides partitioned. Only
  `external_body` is `print_u64`. **No `assume`, no `admit`.**
- Two gotchas cost two runs: `broadcast use group_to_multiset_ensures` needs an
  explicit `use vstd::seq_lib::group_to_multiset_ensures;`, and postconditions
  need `final(v)@`.
- **Probe 2:** `k23_checked` 200 B `900854fd…` vs `k23_unchecked` 81 B
  `547aa4a5…`.
- **Probe 3:** `63247.00` vs `57756.00` → **+5491 = +1.34 `Ir`/element**
  (n=4096, includes a common clone).
- **Probe 4:** `ptr::swap` 0 hits, `::get_unchecked` 0 hits. ⚠ `core::mem::swap`
  **is** spec'd (`std_specs/core.rs:140`) but it is **safe**, so it leaves no
  `unsafe` token — harmless.
- **Bug class:** the unsentinelled scan running off the range = `index >= len`;
  shares with **p07**. ⚠ **The *proof* obligation (a multiset) is not a bound.**
- ⚠ **Kill risk:** the verified spelling is the **single-loop two-index form**,
  not the **nested-scan Hoare form** the cost kernels implement. The shipped
  kernel must declare which; the nested-scan inner loops need their own
  invariants and termination measures. **That spelling was not run.**

### 4. `p24` — binary heap sift — **BUILD (second tier: R5 unprobed)**

- **Probe 2:** `k24_checked` 217 B `8036932e…` vs `k24_unchecked` 138 B
  `725b65bb…`; heapify wrappers 58 B `4ed437e9…` vs `c5cd5172…` — ⚠ **this is
  the pair that exposed #238.**
- **Probe 3 — ⚠ measure heapify, not one sift.** One sift is `+34.00` (O(log n)
  work, the clone dominates). Full heapify: `177437.00` vs `145273.00` →
  **+32164 = +7.85 `Ir`/element, +22.1%**.
- **Probe 4:** `::get_unchecked` 0 hits. Wrapper route.
- **Bug class:** `2*i+2 <= n` instead of `<` = `index >= len`; shares with
  **p04** and **p05**.
- **Harm, RUN:** silent at `gcc -O2` (exit 0), and **only UBSan sees it**
  (`load of address … with insufficient space for an object of type
  'uint64_t'`). **ASan did NOT report a heap-buffer-overflow for the same
  read.**
- ⚠ **Kill risk:** **R5 was not probed.** The interesting obligation is the
  heap-order invariant `∀i: v[i] ≥ v[2i+1] ∧ v[i] ≥ v[2i+2]` re-established
  after a swap — a non-bound obligation like p23's, and **unlike p23's it is
  untested. Probe it before scheduling.**

### 5. `p28` — intrusive doubly linked list — **BUILD, and the catalogue's prediction is CONTRADICTED**

⚠ `.memory/06-catalogue.md`: *"Expect p28/p30 to defeat R5 within budget."*
**Measured false for the structural obligation.**

- ✅ **RUN: `4 verified, 0 errors`** (`v28_dll.rs`).
  `Dll { ptrs: Ghost<Seq<*mut Node>>, perms: Tracked<Map<usize, PointsTo<Node>>> }`;
  `wf()` = domain/`is_init` + **address injectivity** + the `next` chain + the
  `prev` chain. Verified: `get_val`, `step_next`, and the hard one —
  **`unlink`**, which reads the victim's own links out of memory (exec, no ghost
  reads), rewrites **both** neighbours through
  `tracked_remove`/`ptr_mut_read`/`ptr_mut_write`/`tracked_insert`, and
  re-establishes `wf` for `ptrs.remove(i)`. ~25 lines of ghost proof, two
  `assert forall … by` blocks with a three-way index-shift split. **No lemma, no
  `assume`, no `external_body`.**
- **Probe 4 / gate:** `scan_unsafe_probe.py` → *"no `unsafe` token at all — the
  rule cannot fire"*. ⚠ **`vstd::raw_ptr`'s exec API is SAFE Verus, so p28's R5
  is the OPPOSITE of p15/p35:** `_scan_unsafe_sites` is trivially satisfied.
- **Bug class:** dangling `prev`/`next` after an unlink = **temporal**; shares
  with **p27**, the only temporal pattern in the tree.
- ⚠ **Kill risk, and it is the honest one:** `wf` was proved **PRESERVED**, not
  **ESTABLISHABLE**. There is no constructor, so nothing discharges `unlink`'s
  `requires`, and a 0- or 1-node list satisfies `wf` **vacuously**. Building a
  ≥3-node list needs `raw_ptr::allocate` plus a disjointness argument for
  injectivity. p27 already ships `allocate`/`deallocate`, so the machinery
  exists — **but it was not run, and this is exactly the reviewer checklist's
  "is the function dead/vacuous?"**
- **Probes 2 and 3 NOT run** (no rung pair built). **That gap is why it is 5 and
  not 2.**

### 6. `p26` — RLE decode expansion — **BUILD (third tier: the mechanism is p13's)**

- **Probe 2:** `k26_tuned` 141 B `60548539…` vs `k26_unchecked_bulk` 309 B
  `8f2823aa…`; naive pair 247 B / 221 B, also distinct.
- **Probe 3:** naive `495454.00` vs `92942.00` = **5.33×** — ⚠ **but that is a
  PESSIMISED R3.** Matched pair (hoisted capacity check + `fill` against
  `write_bytes`): `105195.00` vs `84727.00` → **+20468 `Ir`/call**. **Publish
  the matched pair; the 5.33× is a spelling spread, not a tax.**
- **Probe 4:** `write_bytes` 0 hits, `::get_unchecked` 0. ⚠ **`Vec::set_len` has
  NO spec** — a first grep said 19 hits and every one was
  `to_multiset_len` / `spec_btree_set_len`. **Corrected by the agent itself.**
- **Bug class:** output-buffer overflow driven by an input run length =
  `index >= len` **write**; shares with **p12** and **p02**.
- **Harm, RUN:** `gcc -O2` **exit 134, glibc `malloc(): corrupted top size`**;
  UBSan names the store.
- ⚠ **Kill risk:** the finding would be *"the bounds check costs a bulk
  lowering"* — **p13's finding, second instance.** Worth building only if §0 can
  say what is **not** p13's.

### 7. `p35` — tagged union / type confusion — **BUILD, BLOCKED on the same gate rule as `p15`**

⚠⚠ **The highest-value single item in the report: `p15` and `p35` share ONE
blocker, and it is one gate policy.**

- **Probe 1:** compile-time, **p08's shape** — safe Rust's `enum` makes the
  tag/payload mismatch **unrepresentable**; a `union` field read reintroduces it
  exactly.
- **Probe 2:** `k35_enum` 155 B `fb0d2540…` vs `k35_tagged` 406 B `cffe42c3…`
  (layout-matched 16-byte elements) vs `k35_union` 458 B `1b4fd32a…`.
- **Probe 3:** `56012.00` vs `52615.00` → **+3397 = +0.829 `Ir`/element,
  +6.5%**; the two unsafe spellings agree to **13 `Ir` in 52k**. Mechanism
  (`objdump`): ⚠ **both rungs execute the same tag test** — the union loop is 2×
  unrolled and the enum loop is not. **The gap is UNROLLING, not the check.**
- ⚠⚠ **Probe 4 as written FAILS here, which is finding #239.**
  `grep -w union ~/tools/verus/vstd` → 318 hits, **all `Set::union`**; the Rust
  `union` keyword is **not in vstd at all**. The task file reads a miss as *"the
  ordinary wrapper route"*. **That reading is wrong.** Verus supports `union`
  **natively**: declared inside `verus!`, `error: requirement not met: to access
  this field, the union must be in the correct variant` → `1 verified, 1
  errors`; with `requires v is i` → **`2 verified, 0 errors`.** The
  tag/payload obligation is **first class in the type system**, no vstd spec
  involved — **and the read is still `unsafe { v.i }` in a VERIFIED fn.** Driven
  through HEAD's own rule: `scan_unsafe_probe.py` → `unsafe at line 17:
  host=NONE -> rep.fail(tcb-unsafe)`.
  **So an operation can carry a Verus-native obligation with zero vstd hits and
  hit p15's obstacle anyway. Grep is necessary, not sufficient; the test that
  decides it is "does an `unsafe` token end up in a verified body".**
  Three spelling traps: the union must be declared **inside** `verus!` (outside,
  Verus prints `external_type_specification` — TASK_083_REVIEW blocker 1's
  uncounted body-less declaration); `#[derive(Clone, Copy)]` on it fails
  (`core::clone::AssertParamIsCopy` not supported); `v->i` in an `ensures` is
  `no method named arrow_i` — use `v is i`.
- **Bug class:** type confusion — ⚠ **absent from the built tree.** Nearest are
  p38 and p36.
- **Harm, RUN, with a magnitude axis like p12's:** through the `double` arm →
  **silent wrong value, NO detector fires at all** (`gcc -O2` and ASan+UBSan both
  print `2.000000`, exit 2); through the **pointer** arm → **exit 139 SIGSEGV**,
  ASan `DEADLYSIGNAL`.
- ⚠ **Kill risk:** `_scan_unsafe_sites`. **If it stays, p35 is blocked
  identically to p15; if it is fixed, TWO rows unblock, not one.**

### 8. `p20` — length/offset pair (Heartbleed) — **DEFER**

- **Probe 2:** `k20_checked` 251 B `056e9912…` vs `k20_unchecked` 235 B
  `e6f559dc…`. No collision.
- **Probe 3, with its zero named in advance:** `22070.00` vs `22060.00` →
  **+10.00 `Ir`/call, FLAT** — **`0.0024` `Ir`/byte at n=4096 and falling.**
  Mechanism: the whole check is six instructions at the top
  (`add;setb;cmp;seta;or;jne`) and the loop body is the identical 8×-unrolled
  fold. **A length/offset check is O(1) and does not scale.** The finding rides
  on the **level**; the per-byte rate is a **real zero with a mechanism**, not
  p45's artefact.
- **Probe 4:** `slice::from_raw_parts` **0 hits**. Wrapper route, twin writable.
- **Bug class:** trusted length → OOB **read** = `index >= len`; shares with
  **p16** and **p02**. **p16's headline is already *"R3 is still 0/byte"* — p20
  would reproduce it.**
- **Harm, RUN:** ASan `heap-buffer-overflow READ of size 4096`; `gcc -O2` exit 0
  with `leaked_secret_bytes=1616`. ⚠⚠ **Kill risk, MEASURED: with `secret`
  malloc'd BEFORE `buf` the identical run leaked 0 bytes.** The leak *magnitude*
  is **allocation-order dependent** — **p48's lesson, and the reason to defer.**

### 9. `p21` — CSV/field splitter with escapes — **DEFER**

- **Probe 2:** 210 B `fb463072…` vs 213 B `9c45103b…`. Distinct.
- **Probe 3:** `26862.00` vs `26788.00` → **+74.00 `Ir`/call** — and the tax is
  **per FIELD, not per byte** (the `buf[i]` check is hoisted; what remains is
  `nf < 64` on ~74 commas).
- **Probe 4:** `::get_unchecked` 0 hits.
- **Bug class:** unbounded field count against a fixed descriptor table —
  **p14's bug class verbatim, and p14's row already says so.** Harm: `gcc -O2`
  exit 9, silent wrong `nf`; UBSan `index 8 out of bounds for type '<unknown>
  [8]'`.
- ⚠ **Kill risk:** the quote-state adds a data-dependent branch but **no new
  bound**; the row is p14 with a different delimiter rule.

### 10. `p41` — flexible array member — **REFUSE, with the measurement**

- ⚠⚠ **Probe 3 kills it:** `k41_checked` `23614.00`, `k41_tuned` **`2387.00`**,
  `k41_unchecked` `2404.00`. **The tuned SAFE rung BEATS the unsafe rung by
  17.00 `Ir`/call.** The apparent 9.6× was **100% R3 spelling** —
  byte-at-a-time `from_le_bytes([buf[o],…])` against a `chunks_exact(4)` walk.
  **That is p10's error exactly (*"60% of the margin was R4 spelling"*), and
  here it is 100%.**
- ⚠ **The bug class is unreachable in the natural spelling.**
  `sizeof(hdr) + n*sizeof(uint32_t)` in `size_t` does not wrap for any `n` a
  wire format can express; the harm only fires with the product cast to
  `uint32_t`. **That is p07's finding verbatim, and p07 already ships the
  reachable 32-bit-check version as `adversarial-width.bin`.**
- Probes 1, 2 and 4 **pass** (285 B / 244 B / 175 B, all distinct). **The row
  dies on probe 3 and on duplication, not on the ladder test.**

### 11. `p40` — SoA vs AoS — **REFUSE, with the measurement**

⚠ **The row's own axis is invisible in the project's primary metric.**
N=1048576, 3 iterations, `callgrind --cache-sim=yes`:

| kernel | `Ir` | D1 misses | LLd misses (read) |
|---|---:|---:|---:|
| `k40_aos` | 360,114,293 | 3,481,161 | 1,912,884 |
| `k40_soa` | 360,114,314 | 2,301,516 | 454,953 |

**21 `Ir` out of 360 million (5.8e-8) while LLd read misses differ 4.20×.**
**And the safety axis is zero too:** `k40_soa_idx` 360,114,467 vs
`k40_soa_unchecked` 360,114,274 = **+193 `Ir` in 360M** for the bounds check over
3M elements. **Wall clock cannot rescue it:** best-of-7 spreads **2.8%–32.7%**,
over the project's own 10% discard threshold on **3 of 4** rungs.
The catalogue's own bug column is *"none — pure perf axis"*, so nothing
distinguishes the rungs but a bounds check costing **6.4e-5 `Ir`/element** —
**p01's axis with p31's problem.** **Refuse.**

---

## The four contradictions

- ✅ **#238 — probe 2's false-positive mode.** MANAGER-VERIFIED (above).
- **#239 — probe 4 as stated is NOT sufficient.** *"A miss means it takes the
  ordinary wrapper route"* is **false for p35**.
- **#240 — the `index >= len` count is over the BUILT tree by two.** The task
  file said *"now FOURTEEN"*. `.memory/06-catalogue.md` calls **p36 the
  TWELFTH**, and **no pattern has been built since p36**. The 13th and 14th are
  **p45's and p15's would-be ones — both REFUSED rows, never built.** ⚠ **Twelve
  built patterns carry it.** The preference itself stands; **its premise should
  say twelve.**
- **#241 — the catalogue's `p28` prediction is contradicted** (above), with the
  scope caveat that this is the *structural* obligation, not the whole pattern.

**One error the agent found and corrected in itself before it reached a
headline:** `k35_tagged` first measured **2.12×** dearer than `k35_enum`; the
entire gap was the `Vec<TaggedRaw>` being constructed **inside** the measured
loop. Hoisted, it is `+0.829 `Ir`/element`.

⚠ **One memory-update claim in the agent's report is WRONG:** it says the
`final(v)@` note *"is still not there"* in `.memory/04-verus.md`. **It is —
twice**, at `:98` (`&mut` postconditions need `old(x)` / `*final(x)`) and at
`:1516` (*"use `old(v)` / `final(v)`. Costs a run to rediscover"*). Manager-
checked. **The note existed and was not found; that is a discoverability problem,
not a missing fact.**

---

## Rows NOT probed, and why — so the next selection task does not re-derive it

- **`p15`, `p42`, `p25`** — out of scope per the task file; **nothing found that
  disturbs p42's refusal or p25's defer.**
- **`p29` (BST), `p30` (chained hash), `p32` (free-list), `p33` (object pool),
  `p34` (refcount)** — Family E/F pointer-backed rows whose feasibility question
  is the one **`p28` answers**; the Family-E budget went to p28 because it is the
  row the catalogue predicted would fail. `p30` is explicitly *"combines p22 +
  p27"*, both built.
- **`p37` (callback with `void*`)** — p35's type confusion through a function
  parameter, so it inherits **p35's gate blocker plus p36's measured *"Verus at
  the pin cannot type `fn(u64) -> u64` at all"***. Probing it before the
  `_scan_unsafe_sites` decision would be wasted.
- **`p39` (bitfield pack/unpack)** — `shift/mask off-by-one` is p09's `q & 31`
  shape and p18's harm.
- **`p43` (CRC over untrusted length)** — the catalogue states it is p16's shape,
  and the p20 measurement (a hoisted O(1) length check, `+10.00` flat) is the
  same mechanism, **which makes that claim more likely, not less**.
- **`p44` (fixed-point)** — p45's contract question with a scaling factor, and
  p45 is refused.

## Unsure / not done

- **`p24`'s R5 is unprobed** — the heap-order invariant. **The single cheapest
  thing the next task could add.**
- **`p28` proves preservation, not establishability**; no probe 2 or 3 (no rung
  pair).
- **`p46`'s full product postcondition is unproved.**
- **`p23`'s verified spelling is not the spelling its cost kernels implement.**
- **All probe-2 kernels are throwaway pre-checks**, not built rungs — now with a
  known false-positive mode attached.
- **`p20`'s `leaked_secret_bytes=1616` counts coincidental `0x53` bytes** as well
  as the planted secret; it is not an oracle.
- **9 rows were not surveyed**, so *"p19 beats the other 18"* is **not
  established** — only *"p19 beats the ten probed and clears all four probes"*.
- ⚠ **Nothing here has been through `check.py`**, by instruction. **Every number
  is from throwaway kernels, not from the gate.**
- `~/tools/valgrind/bin/valgrind` works for callgrind; **`/usr/bin/time` does not
  exist on this box** (`p40_wall.py` uses `time.perf_counter`).

## Memory updates owed (manager applies, after review)

1. **Probe 2: link the binary or read `readelf -rW` before md5-ing.** ✅ Already
   landed — manager-verified.
2. **Probe 4: the vstd grep is necessary, not sufficient** (p35).
3. `.memory/04-verus.md`: `broadcast use group_to_multiset_ensures` needs an
   explicit `use vstd::seq_lib::…`; `by (bit_vector)` rejects the `nat`-cast
   spelling of a u128 hi/lo split and accepts the `u128` + `requires` form;
   `#[verifier::truncate]` on both casts.
4. `.memory/06-catalogue.md` `p28`/`p30`: the *"expect R5 to be defeated"*
   prediction is contradicted for the structural obligation.
5. `.memory/06-catalogue.md` `p35`: **Verus supports `union` natively** with a
   first-class correct-variant obligation, discharged by `requires v is i`.
6. **The `index >= len` count is twelve BUILT, not fourteen.**
