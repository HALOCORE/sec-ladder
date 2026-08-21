# p27 — handle table over per-record allocations: measurements and arguments

**The one TEMPORAL bug class in this project.** Every other pattern's bug is
spatial (an index outside an allocation) or logical (a wrong answer inside a live
one). p27's read is through a pointer whose record has been `free`d, so the
address is inside **no live allocation at all** — and it is the one class safe
Rust rejects at *compile* time.

Read `spec.md` first; it carries the contract and the pins. This file carries the
measurements, the arguments the gate cannot judge, and the things that turned out
not to be true.

**Contract hash.** The `slb-contract` block's sha256, as first written before any
cell of the shipped matrix was measured, was
`b1f2dbb3e48542af48d444c69f4bbc80402363fcec05a8b4ded37b50da1f8dea`.
**It moved once, to `a0e83e2f2ee2e3bb756b2985a3ca9c718f6c5a13dbf7a91e7b0ebc446e23beb5`,
and the reason is recorded here rather than left to be noticed**: the gate's
clause-mutation stage (5c) found two of `rec_alloc`'s `ensures` clauses **not
load-bearing** — `pt.0.addr() + size <= usize::MAX + 1` and
`pt.0.addr() as int % align as int == 0`, both copied verbatim from
`vstd::raw_ptr::allocate` — and the same run found that `rec_free`'s
`Tracked(pt)` destructuring parameter pattern made the tautology probe
*unsynthesisable*, so six of its `requires` conjuncts were not judged at all. The
clauses were dropped and the parameters made plain identifiers; `verus.items` is
a mechanical dump of `verus.rs` through `harness/vparse`
(`controls/mkspec.py`, which regenerates `spec.md` byte-identically), so the
pin followed. **No `required` or `forbidden`
entry moved**, and the direction of both edits is *toward* a stricter gate.

---

## 0. The bug class, settled before anything was built

`.memory/06-catalogue.md` rates p27 *"singly linked list (build, traverse, free)
— use-after-free, leak"*. **The class is upheld; the shape is not.** Two
candidates were priced (`.temp/p27/NOTES.md` §0):

**Candidate A, the textbook list free** — `for (p = head; p; p = p->next)
free(p);`. Rejected, and the reason is not taste:

- Where the `next` field sits decides whether the bug is observable at all, and
  the answer is a **glibc implementation detail**. At offset 0 the freed chunk's
  first 16 bytes are the tcache `next`/`key`, safe-linked and therefore
  ASLR-dependent, and the traversal walks a scrambled pointer — a segfault, not
  a measurement. At offset ≥ 16 glibc does not touch the field and the traversal
  is *correct on every input on every build*, so R1 and R1h print the same
  checksum and the bug is invisible to the entire checksum column.
- The bug fires on **every** input, so it cannot be confined to adversarial
  rows — and TASK_055_REVIEW blocker B1 requires exactly that (see 7 below).
- Safe Rust cannot write it at all, so R2/R3 would not be a *spelling* of R1's
  program but a different program, and the reviewer checklist's "did a rung
  quietly change the algorithm" would have no good answer.

**Candidate B, the handle table** — chosen. An op stream from the file drives
OPEN/CLOSE/READ against a table of individually `malloc`'d records; the bug is
one conjunct on the READ path; it fires only on inputs that read a closed handle.

### 0b. What R1 KEEPS, and why the comparison is one program against its guard

Three things are in R1 that a lazier construction would have taken out, and each
is what makes R1-vs-R1h a guard rather than a rewrite:

1. **R1 keeps the slot bound `h < ntab`.** So `tab[h]` is always an entry some
   OPEN wrote, the table read itself is in bounds, and the bug is temporal and
   not spatial.
2. **R1 keeps `live[]` and maintains it** — CLOSE writes `live[h] = 0` in both C
   rungs, character for character. Only the READ path differs. This is not
   generosity: if R1 did not maintain it, CLOSE would not be idempotent and the
   epilogue could not tell a closed slot from a live one, so **R1 would
   double-free** on any input with two CLOSEs of the same handle, and that is a
   different bug in a different class. The measured difference would then be
   between two different programs rather than between one program and its guard.
   *This is also why the liveness bit cannot be "the pointer is NULL":* the
   handle is an integer, so nulling `tab[h]` would turn the stale read into a
   NULL dereference — a crash, not a use-after-free — and would leave the
   epilogue with nothing to consult.
3. **R1 keeps the epilogue**, so neither C rung leaks and **the allocator's state
   at the end of a call is its state at the start.** That is what makes a kernel
   that allocates legal in this benchmark at all — the driver calls it 200 000
   times and every call must return the same value — and it is *measured*, not
   assumed: all eight cells agree with `model.py` on `small` (200 000 calls, 8
   windows, 24 ops each) and on `large` (20 000 calls, 64 windows, 120 ops), and
   a kernel whose answer drifted with allocator state would not.

### 0a. What TASK_055 §2.8 predicted, and what actually happens

§2.8 predicted that safe Rust would be forced onto `(slot, generation)` and would
pay *"a wider handle plus an indirection plus a generation compare"*, i.e. that
the pattern's axis would be a **representation split** between the rungs.

**That is not what happens, and the reason is structural: the handle comes out of
a file, so it is an integer in every rung.** An op stream cannot name a pointer.
So there is no pointer-handle rung, no `(slot, gen)` rung, and no representation
split — and, as a direct consequence, **none of TASK_055_REVIEW M1's arity
problem arises** (see 1 below).

What safe Rust *is* forced into is `Option<Box<u8>>`, and the finding that
replaces §2.8's is better:

- **`Option<Box<u8>>` is niche-optimised to one pointer word**, `None` *is* the
  null pointer. The safe rung's table is byte-for-byte the hardened C rung's
  `tab[]` **minus** C's separate `live[]` array. The safe representation *is* the
  hardened representation, arrived at by construction rather than by discipline.
- **`tab[h] = None` frees the record and invalidates the handle in ONE
  operation.** C does those two things in two statements — `free(tab[h]);
  live[h] = 0;` — and R1's bug is that the *third* thing, asking, is missing.
- **At R4 the invalidation is a hand-written line, and at R5 the proof forces
  it.** Delete `arr_set_unchecked(&mut live, h, 0u8)` from `verus.rs` and the
  loop invariant cannot be re-established, because `rec_free` has consumed slot
  `h`'s permission while the liveness array still claims the record exists. That
  is mutant **M2** in 10 below, and it is the pattern's sentence made checkable.

**The sentence p27 exists for: the free and the invalidation are one operation in
safe Rust and two in C, and the bug is the third one — the asking — going
missing.**

---

## 1. §0.1 — the dead `slab` argument, measured, and why p27 does not need it

TASK_055_REVIEW M1 measured that `driver.aliases` / `driver.call_args` are keyed
by *language*, so all four Rust rungs share one table, and that
`harness/dloop.py:361` raises when the declared positions exceed a call's arity.
Its one escape — a **dead `slab` argument** at R4/R5 — was left unmeasured at
`-O3`, and TASK_060 made measuring it the gating deliverable.

**Probe:** `.temp/p27/deadarg/` — two programs identical but for an extra
`_slab: &[u8]` parameter the kernel never reads and the corresponding extra
argument at the call site. `build.py`'s own flags, both opt levels, both inline
modes.

| | `kernel` `md5_raw` | `main` `md5_raw` |
|---|---|---|
| `-O0 isolated` | **differs** (the three arg spills move `rdi,rsi,rdx` → `rdx,rcx,r8`) | **differs** |
| `-O0 whole` | **differs** | **differs** |
| `-O3 isolated` | **identical** | **identical** |
| `-O3 whole` | (inlined away) | **identical** |

```
cell                        kernel/call    main/call     k+m/call
bin-2arg-O0-isolated          1227.0000      25.0000    1252.0000
bin-3arg-O0-isolated          1227.0000      28.0000    1255.0000
bin-2arg-O0-whole             1227.0000      25.0000    1252.0000
bin-3arg-O0-whole             1227.0000      28.0000    1255.0000
bin-2arg-O3-isolated           372.0000      13.0000     385.0000
bin-3arg-O3-isolated           372.0000      13.0000     385.0000
bin-2arg-O3-whole                     -     399.0000     399.0000
bin-3arg-O3-whole                     -     399.0000     399.0000
```

**The dead argument is free at `-O3` — exactly, to the last digit, in both
inline modes — and costs `+3.0000` Ir/call at `-O0`, all of it at the call site
and none of it in the kernel.** LLVM's dead-argument elimination deletes it
outright at `-O3`; at `-O0` nothing is eliminated and the call site pays two
extra loads and a register move. The kernel's own `1227.0000` is unchanged even
at `-O0`, because an *unused* parameter is never spilled — the three spills are
the three live arguments in both builds and only the register assignment moves,
which is why `md5_raw` differs while `Ir` does not.

**So the escape survives `-O3`. And p27 does not use it**, because the shape that
needed it is not p27's shape: the driver loop is pinned identical across all
seven rungs, so there is nowhere rung-specific to build a slab, and the slab
therefore lives inside the kernel exactly as p14's scratch and field table do.
Every Rust rung is `kernel(buf, off, len)`; both C rungs are
`kernel(buf, buf_len, off, len)`; the gap is closed by **p14's existing
`driver.call_args` pin, unchanged**. No new harness surface and no `harness/`
change.

---

## 2. The equivalence argument, in writing

`.memory/02-bench-rules.md` and the reviewer checklist ask whether the rungs are
semantically equivalent or whether one quietly changed the algorithm. Because p27
is *not* a representation split (0a), the question is the ordinary one, and it
has two answers:

**Mechanically**, `harness/check.py` stage 2 derives it: every cell's stdout
equals `model.py`'s on every non-adversarial input, and all cells agree with each
other. That is the evidence `.memory/02-bench-rules.md` names.

**And it is measured, not only argued**: callgrind's per-function table gives
`malloc` `421.1211` Ir/call and `free` `310.2635` Ir/call **identically** for
`safe_tuned` and for `unsafe` on `small.bin` (5e), and the sweep's `R3 − R4`
regression puts `nopen`'s coefficient at `−0.0157`, zero to within a residual of
2.92 over 80 blobs (9c). *The two representations make the same allocator calls,
in the same number, of the same size.*

**Structurally**, per record, every rung does:

- **one allocation of `RECSZ` bytes from the same allocator.** Rust's default
  global allocator calls `malloc` for `align <= 8`, so `Box::new(a)` (R2/R3),
  `std::alloc::alloc` (R4/R5) and `malloc(1)` (R1/R1h) are the same glibc call in
  the same size class;
- **one `free` of it**, and every record is freed before the kernel returns;
- **per READ: one slot-bound test, one liveness test, one load of the record.**

**What the argument does NOT establish** is that the two representations have the
same *cache* behaviour. They have the same layout — one pointer word per slot,
plus C's and R4/R5's extra `TABCAP` liveness bytes — but not necessarily the same
addresses. Any `ns` claim therefore needs the layout population
(`.memory/05-layout.md`) and is not carried by this argument.

**And there is one asymmetry that is deliberate and is a result rather than an
oversight: R2 and R3 have no epilogue.** Dropping the table frees every record
still alive, so the loop the other five rungs write by hand is written by the
language. See 3.

---

## 3. `Ir` per call, and where the safety cost is

`-O3 isolated`, from `results/p27-handle-table.json` (kernel-exclusive) and from
`controls/ir_table.py --marginal` (whole-program marginal). `small.bin` is 8 windows of
24 operations at `n_iters` 200000; `large.bin` is 64 windows of 120 operations at
20000.

| rung | cell | kernel Ir/call small | large | **whole-program** Ir/call small | large |
|---|---|---:|---:|---:|---:|
| R1 | `c-gcc` | 844.5685 | 3440.0865 | 2291.6035 | 8414.6716 |
| R1 | `c-clang` | 869.5913 | 3641.8189 | 2275.7692 | 8487.3326 |
| R1h | `c-gcc-h` | 864.4959 | 3530.8879 | 2311.4302 | 8505.6792 |
| R1h | `c-clang-h` | 874.5739 | 3645.2917 | 2280.7224 | 8491.0960 |
| R2 | `safe_naive` | 1041.1426 | 4562.3795 | 2697.4293 | 9955.1610 |
| R3 | `safe_tuned` | 1031.6288 | 4530.3795 | 2687.9135 | 9923.1610 |
| R4 | `unsafe` | 928.4304 | 3879.0121 | 2464.6514 | 9140.9146 |
| R5 | `verus` | **928.4304** | **3879.0121** | **2464.6514** | 9140.9278 |

### 3a. ⚠ TWO DENOMINATORS, and on p27 they are not interchangeable

**58–62% of this kernel's work is inside `malloc` and `free`, which are in glibc
and therefore inside no symbol `harness/measure.py`'s `_sum_rows` matches.**
`1 − 928.4304/2464.6514 = 62.33%` on `small` and `57.56%` on `large`. Every
kernel-exclusive figure above is therefore *the part of an operation that is not
the allocation*, and every whole-program figure is the operation.

Both are honest and neither is "the" number; **what is not honest is comparing
across the two**, and one control in this pattern does exactly that if you let
it (5d). Where a single figure is wanted below, it is the **whole-program**
marginal, because the allocator is what p27 is about.

### 3b. What the table says

- **`R5 − R4 = 0.0000` kernel-exclusive on both inputs, and `0.0000` /
  `+0.0132` whole-program.** Finding 1 reconfirmed on the first kernel in this
  project that allocates and frees — and it took the two source lines in 5 to
  get there. The `large` whole-program `+0.0132` Ir/call is 132 instructions
  over a 5000-call increment against a byte-identical kernel and an identical
  checksum; it is below the resolution of the marginal and is quoted rather than
  rounded away.
- **`R1h − R1 = +19.83` (gcc) / `+4.95` (clang) on `small`, `+91.01` / `+3.76`
  on `large`** (whole-program). **The two compilers disagree by 4× on `small`
  and by 24× on `large`** for one added conjunct — which is finding 5's shape
  ("static instruction counts are not a cost model") arriving on the *hardening*
  column. Kernel-exclusive the same pair reads `+19.93` / `+4.98` and `+90.80` /
  `+3.47`, so the disagreement is in the kernel and not in the allocator.
- **`R2 − R3 = +9.52` on `small` and `+32.00` on `large`**, whole-program, and
  the same to four decimals kernel-exclusive — the two R3 levers of 8, and they
  are *exactly* `nread + nclose` per call on each blob.

⚠ **What must NOT be read off this table is "the cost of safe Rust's lifetime
guarantee".** `R3 − R4` is `+223.26` / `+782.25` whole-program, and **it is not
a safety number**: 5e decomposes it per function and **54% of it is the epilogue
asymmetry** — the safe rungs' out-of-line drop glue over all `TABCAP` slots
against the unsafe rungs' inline loop over `ntab` — while the allocator
contributes **exactly 0.0000**, `malloc` and `free` costing the two rungs the
same to the last digit.

### 3c. Wall clock — recorded, not published

`results/p27-handle-table.json` carries `min_s` for all 16 `-O3` cells on both
inputs (`c-gcc` 0.03544 / 0.02699, `unsafe` 0.03741 / 0.03025, `safe_tuned`
0.03939 / 0.02974, …). **No `ns` claim is made from them and none may be**, for
two reasons that are each sufficient: they are whole-process **levels** and
carry the per-process constant (`.memory/03-measurement.md` finding 20a), and
**there is no layout population for this pattern yet** — `controls/clayout.py`
is ported and ready, and until it has been run the shipped binaries are one draw
of unknown width. p27 additionally has a reason no earlier pattern had: its wall
clock is a function of the *allocator's* state, and the allocator's state is not
a property of the code.

### 3d. Panic pads, checked before anything is called a safety cost

`.memory/03-measurement.md` trap: tail padding and landing pads inflate a static
count. `harness/asm.py stat`, `-O3 isolated`, kernel symbol:

| cell | `n_fn` | `n_fn_nopad` | `pad_insns` | `pad_bytes` |
|---|---:|---:|---:|---:|
| `c-gcc` | 154 | 146 | 0 | 0 |
| `c-gcc-h` | 155 | 149 | 0 | 0 |
| `c-clang` | 147 | 141 | 1 | 9 |
| `c-clang-h` | 146 | 142 | 1 | 9 |
| `safe_naive` | 210 | 206 | 15 | 15 |
| `safe_tuned` | 213 | 209 | 15 | 15 |
| `unsafe` | 156 | 151 | 2 | 2 |
| `verus` | 156 | 151 | 2 | 2 |

⚠ **`c-clang-h` has one FEWER static instruction than `c-clang`** (146 vs 147,
142 vs 141 unpadded) while executing **more** — finding 5's inversion, on the
hardening column, inside one compiler. The safe rungs' 15 pad instructions are
`int3` tail padding, not landing pads; the landing pads themselves are the
`_Unwind_Resume` block and the two `drop_glue` call sites, and they are counted
in `n_fn_nopad`. **`bulk_calls` is empty on all eight kernels**, so no rung is
winning or losing on a `memcpy`/`memset` idiom: gcc and clang inline the two
`memset`s of the table and the liveness array at `-O3`, and the Rust rungs'
`[const { None }; 32]` / `[0u8; 32]` are stores.

### 3e. Reproducibility control, taken for free

`harness/measure.py p27` was run **twice**, the second time after `inputs/gen.py`
had been edited (9b's band-S bug) in a way that leaves every matrix blob
byte-identical. **Every `kernel_exclusive_ir`, every `main_exclusive_ir` and
every `md5_fn` in the record is identical between the two runs**, on all 32
cells and both inputs, while `source_sha256` for `gen.py` moved from
`070c92ad0cace1d3…` to `19c9fe676bc074ef…`. So the `Ir` column is exactly
reproducible on this box, and `--check-stale`'s two-hash design
(`measure.py:238`) did the thing it is for: it said "the generator moved, the
blobs did not".

## 4. The table bounds check — a claim this pattern made and then refuted

The first draft of `unsafe.rs` and `verus.rs` indexed the handle table
**checked**, with a comment asserting that `h < ntab` together with
`ntab <= TABCAP` already deletes rustc's bounds check, so a `get_unchecked`
accessor would buy nothing and cost two trusted items.

**That was written without measuring it and it is false.** Three
`core::panicking::panic_bounds_check` call sites survive in the checked kernel
at `-O3` (8 `call`s in the kernel symbol against 5 in the unchecked one), and the
control `r4_tabchecked` — the draft itself, regenerated by
`controls/gen_controls.py` from the shipped rung by exact-string substitution —
measures (`controls/ir_table.py --marginal`):

| | kernel Ir/call small | large | whole-program small | large |
|---|---:|---:|---:|---:|
| `unsafe` (shipped, unchecked, `-O3 isolated`) | 928.4304 | 3879.0121 | 2464.6514 | 9140.9146 |
| `r4_tabchecked` | 970.1321 | 4044.4534 | 2506.2728 | 9306.5702 |
| **difference** | **+41.7017** | **+165.4413** | **+41.6214** | **+165.6556** |

**+41.62 Ir/call on `small` and +165.66 on `large`, whole-program** — and note
that the two denominators agree here to within 0.09, because a bounds check is
entirely inside the kernel and touches no allocator.

Per operation that is `41.62 / 24 = 1.73` on `small` and `165.66 / 120 = 1.38` on
`large`. So the shipped R4 and R5 index the table through `arr_get_unchecked` /
`arr_set_unchecked`, at the cost of two trusted items; 6 records what that does
to the TCB column.

**This is the sort of claim `.memory/01-ladder.md` finding 14 is about.** It was
plausible, it was p03's seeding mechanism applied by analogy, it was written in a
comment as though it had been measured, and it was wrong on the first thing that
could check it. `r4_tabchecked` is **not** an admissible R4 and is not offered as
one — it is the measurement that justifies two trusted items.

## 5. The `identity` pin, and the two lines it cost

`identity` is pinned `O3: exact`, `O0: norel` — the levels p08 and p14 pin.
Getting there needed two decisions, both measured, and **both are new to this
project because p27 is the first pattern whose kernel calls a vstd function that
is not `#[inline(always)]`.**

### 5a. vstd's allocation API cannot be called from a rung

`vstd::raw_ptr::ptr_ref`, `ptr_mut_write` and `ptr_mut_read` all carry
`#[inline(always)]` (`raw_ptr.rs:577`, `:601`, `:619`), which is why TASK_055
§2.4 measured byte-identity on a kernel that only *reads* through pointers.
**`allocate` and `deallocate` carry no `#[inline]` at all** (`raw_ptr.rs:908`,
`:948`). A rung that calls them emits

```
15a2f: call *0x41493(%rip)        # 56ec8 <_DYNAMIC+0x2d0>
```

— a **GOT-indirect cross-crate call**, whose target `nm` resolves to
`vstd::raw_ptr::allocate` at `0x15c10`. `unsafe.rs` is compiled by plain rustc
against no vstd and cannot produce that instruction; with vstd's own API the pair
measures **`differ` at both opt levels**, and at `-O3` the difference is not only
the call form but two extra `mov $0x1` argument set-ups, because the cross-crate
call cannot have its constants propagated into the callee.

So `verus.rs` carries `rec_alloc` and `rec_free`: `vstd::raw_ptr::allocate` and
`deallocate` copied into the crate, `#[inline(always)]`, **with vstd's own
`allocate` and `deallocate` as their verified twins**.

**The vstd-pure rung is built, verified and measured** —
`controls/gen_controls.py` emits it (`r5_vstdpure.rs`), and it additionally
deletes `rec_alloc`, `rec_free` and their twins, which are dead once the exec
code calls vstd directly:

```
verification results:: 15 verified, 0 errors
vstd-pure control tcb_items = 5 ['arr_get_unchecked', 'arr_set_unchecked',
                                 'buf_get_unchecked', 'emit', 'load_input']

r5_vstdpure vs unsafe, O3 isolated
  identical by raw machine-code bytes : False
  identical with pc-rel fields masked : False        <-- `differ`, not `norel`
```

**Two fewer trusted items, the same checksum on every input, and it is not a
rung.** `differ` rather than `norel` because the difference is not only the call
target: the cross-crate call cannot have its constants propagated into the
callee, so the call site also materialises `mov $0x1,%edi` / `mov $0x1,%esi`
that the local copy does not need.

### 5b. `*base = v` and not `core::ptr::write(base, v)`

`vstd::raw_ptr::ptr_mut_write`'s body is `core::ptr::write(ptr, v)`, but it is
`#[inline(always)]` over a **precompiled, already-optimised** vstd, so at `-O0`
R5 gets a bare store. `core::ptr::write` is `#[inline]` and not
`#[inline(always)]`, so in `unsafe.rs` at `-O0` it survives as

```
call 16590 <core::ptr::write::<u8>>
```

One instruction of difference, and `-O0` identity drops from `norel` to
`differ`. `unsafe.rs` writes `*base = v`, which is the same operation for a `u8`
and inlines at every level.

### 5c. What the pin measures now

```
O0/isolated    md5_raw: False   md5_raw_norel: True
O0/whole       md5_raw: False   md5_raw_norel: True
O3/isolated    md5_raw: True    md5_raw_norel: True
```

At `-O0` the crate names differ in length so call displacements differ — link
layout, not codegen. **This is the first pattern here where the `identity` pin
has a stated price in the TCB column**, and 6 argues that the price is a
relocation rather than an addition.

### 5d. What the vstd-pure rung costs, and the attribution trap in the middle of it

⚠ **Measured kernel-exclusive, `r5_vstdpure` looks 30.02 / 96.00 Ir/call CHEAPER
than the shipped pair. That reading is an artefact and it is the exact trap
3a exists to name.**

```
-O3 isolated     kernel Ir/call            whole-program Ir/call
                small       large           small        large
verus (shipped) 928.4304   3879.0121      2464.6514    9140.9278
r5_vstdpure     898.4134   3783.0121      2594.7618    9556.9250
difference      -30.0170    -96.0000       +130.1104    +415.9972
```

The kernel-exclusive column falls because the work **left the `kernel` symbol**:
`vstd::raw_ptr::allocate` is a separate function, so its layout construction and
null check stop being attributed to the kernel. Whole-program, the vstd-pure rung
is **130.11 / 416.00 Ir/call DEARER** — a cross-crate GOT-indirect call, twice
per record, that the local `#[inline(always)]` copy does not make.

**Both signs are real and they are of the same quantity.** Quoting the first
would have published "calling vstd is cheaper" out of a measurement that says
the opposite. It is `.memory/03-measurement.md`'s warning about
`kernel_exclusive_ir` in its sharpest available form, because here the two
columns disagree in **sign** rather than in magnitude.

### 5e. The epilogue asymmetry, priced — and the allocator contributes ZERO to the safe-vs-unsafe gap

R2 and R3 have no epilogue: dropping `[Option<Box<u8>>; TABCAP]` frees every
record still alive. R4, R5 and both C rungs walk `0..ntab` by hand.

**The clean measurement is not a control at all — it is callgrind's own
per-function table**, because rustc emits the drop as an out-of-line
`core::ptr::drop_glue::<[Option<Box<u8>>; 32]>` and glibc's `malloc` and `free`
are their own symbols. Marginal per call, `small.bin`, `n_iters` 20000 → 40000,
from `controls/ir_table.py --functions`:

| function (`-O3 isolated`) | `safe_tuned` | `unsafe` | difference |
|---|---:|---:|---:|
| `kernel` | 1031.1904 | 928.3500 | **+102.8404** |
| `malloc` | **421.1211** | **421.1211** | **0.0000** |
| `free` | **310.2635** | **310.2635** | **0.0000** |
| `drop_glue::<[Option<Box<u8>>; 32]>` | 120.4218 | — | **+120.4218** |
| whole program | 2687.9135 | 2464.6514 | +223.2621 |

**`malloc` and `free` are equal to the last digit between the safe and the
unsafe rung.** The two representations make *the same allocator calls*, in the
same number, of the same size — the equivalence argument of 2, measured rather
than asserted, and the strongest form of it available.

**And the `R3 − R4` gap decomposes exactly**: `+223.2621 = +102.8404` inside the
kernel `+ 120.4218` of drop glue `+ 0.0000` of allocator. **54% of it is the
epilogue asymmetry** — the safe rungs' scope-exit drop, which walks all `TABCAP`
slots out of line, against the unsafe rungs' inline loop over `ntab`. That is
not a safety cost; it is what the language does with the table on the way out.

The control `r2_epilogue` (R2 plus an explicit loop, on top of the drop glue)
measures `+115.4983` / `+324.9026`, which brackets the same quantity from the
other side and agrees with the 120.4218 above on `small` to within 5%. ⚠ It is
an **upper** bound and not the asymmetry itself, because it pays the drop glue
as well; the per-function table is the number to quote.

## 6. The TCB, and what the number does not rank

`tcb_items = 7` for `verus.rs`:

| item | class | what it licenses |
|---|---|---|
| `buf_get_unchecked` | U-license | the unchecked window read |
| `arr_get_unchecked` | U-license | the unchecked table read (4) |
| `arr_set_unchecked` | U-license | the unchecked table store (4) |
| `rec_alloc` | **relocation** | `vstd::raw_ptr::allocate`, verbatim, twin = vstd's own |
| `rec_free` | **relocation** | `vstd::raw_ptr::deallocate`, verbatim, twin = vstd's own |
| `load_input` | infra | argv, file I/O, LE decode; no `ensures` |
| `emit` | infra | `println!`; no `ensures` |

**Not one of the seven is the temporal property.** The whole lifetime
argument — a `PointsTo<u8>` consumed by a deallocation, a `Map<int,
PointsTo<u8>>` and a `Map<int, Dealloc>` maintained across open and close, and a
stale read that has no permission to present — rests on items that are
`external_body` *inside vstd* (`ptr_ref`, `ptr_mut_write`) or vstd `axiom fn`s
(`into_typed`, `into_raw`, `leak_contents`, the `Map` operations). p27 adds
**zero** project-local axioms for it.

### 6a. TASK_055 §2.5's alarm: confirmed in substance, wrong in its number

§2.5 predicted that a `raw_ptr` pattern would publish **`tcb_items = 2`** —
fewer than p01's array sum — while doing manual allocation, and that the TCB
column would therefore rank a raw-pointer kernel *safer* than a bounds-checked
one.

**The number is wrong and the concern is right.** A real pattern also indexes a
table and reads a window, so p27 publishes **7**, more than p01's 3 and more
than p14's 6. What survives, and is the honest form of the alarm, is this:

> **The part of p27 that does manual allocation contributes nothing to
> `tcb_items`.** Five of the seven items are the spatial accessors and the infra
> every pattern here ships, and the other two are a codegen device whose twins
> are vstd's own API. If p27 had been allowed to call vstd's `allocate`
> directly, it would publish **5** — and would not be a rung, because the
> `identity` pin would read `differ`.

So the two-column proposal's failure mode is real: **`tcb_items` counts this
project's own axioms and is not a safety ranking.** It is also, on this pattern,
**in tension with the `identity` pin** — a fact no previous pattern could
exhibit, and one worth stating plainly rather than burying: *you can have the
smaller trusted base or the byte-identical R4/R5 pair, not both.*

⚠ Do not compare p27's 7 with p01's 3 as if it meant p27 is less trustworthy.
The comparison that means something is 5 of p27's 7 against p01's 3, plus the
sentence above.

---

## 7. The adversarial rows

A use-after-free has no magnitude axis — there is no "one byte past". What it has
is a **recycling** axis, and that decides whether the harm is disclosure or
noise. Measured, `-O3 isolated`, three runs each:

```
adversarial-uaf        c-gcc   : 1402190519230396416 1402190519230396416 1402190519230396416
adversarial-uaf        c-clang : 1402190519230396416 1402190519230396416 1402190519230396416
adversarial-noreuse    c-gcc   : 11043762887674013696 8077780024137721856 8060306882998740992
adversarial-noreuse    c-clang : 11096182311090956288 6147053158150809600 11078709169951975424
```

against the checked rungs' `4295919549966416896` and `3390747988282288128`, which
`c-gcc-h`, `c-clang-h`, `safe_naive`, `safe_tuned`, `unsafe` and `verus` all
print.

**`adversarial-uaf` is the row the pattern exists for**: OPEN, CLOSE, OPEN — the
tcache is LIFO, so the second OPEN gets the freed chunk back and writes the new
record into it — then READ the *closed* handle. R1 returns **the newer record's
byte under the older record's handle**: one record's contents delivered under
another record's name. It is deterministic across runs *and identical on gcc and
clang*, which is what makes it a measurement rather than an anecdote.

**`adversarial-noreuse` is the row that shows the harm is not always a
disclosure**: with no OPEN between the CLOSE and the READ the chunk is still in
the tcache, so R1 reads glibc's own safe-linked `next` word, which is a function
of the heap address and therefore of ASLR. ⚠ **Its `c-gcc` and `c-clang` cells
are deliberately not reproducible, and their recorded stdout in
`results/gate/p27-handle-table.json` changes on every gate run.** Stage 4 records
adversarial behaviour rather than requiring it, so this is a note and not a
failure — and it is the measurement behind `.memory/03-measurement.md`'s
constraint that a naked use-after-free is not a reproducible number.

### 7a. What catches it, and what does not

`harness/check.py` stage 7, `gcc -O1 -fsanitize=address,undefined` on
`c/kernel.c`, from `results/gate/p27-handle-table.json`:

```
adversarial-many.bin       expect=fires  fired=True  exit=1
adversarial-noreuse.bin    expect=fires  fired=True  exit=1
adversarial-stride3.bin    expect=clean  fired=False exit=0
adversarial-uaf.bin        expect=fires  fired=True  exit=1
degenerate.bin             expect=clean  fired=False exit=0
large.bin                  expect=clean  fired=False exit=0
small.bin                  expect=clean  fired=False exit=0

ERROR: AddressSanitizer: heap-use-after-free on address 0x502000000010
  READ of size 1 at 0x502000000010 thread T0
    #0 ... in kernel .../patterns/p27-handle-table/c/kernel.c
```

**Three for three on the adversarial rows and clean on all four benign ones**,
with the expectation *derived* by `model.py` from the simulated run rather than
tabulated per file. ⚠ **This is the opposite of p02's result**, where idiomatic C
was silent in seven of eight builds: a use-after-free of a *freed chunk* is
exactly what ASan's quarantine is built to see, where p02's one-byte heap
overflow was absorbed by glibc's chunk rounding. **The interesting silence here
is not the sanitiser's, it is the CHECKSUM's**: on `adversarial-uaf` R1 exits 0,
prints a plausible 19-digit number, and prints *the same one on gcc and on
clang* — so a differential test against a second C implementation would not
catch it either. It takes a sanitiser, Miri, or a type system.

Miri is required and ran (`miri.required: true`, `ran: true`), over `unsafe.rs`
at `n_iters = 4`. It is the **only** tool in the matrix that checks the temporal
property on the *unsafe Rust* rung: ASan covers the C rungs, the proof and the
`identity` pin cover R5, and a wrong trusted body in `rec_free` — one that freed
a different pointer, or nothing at all — would satisfy every `ensures` in
`verus.rs` because `rec_free` has none to satisfy. See its
`SLB-TRUSTED-ARGUMENT` section below.

### 7b. Why the UAF is on adversarial rows only

Two independent reasons, either sufficient:

1. Stage 2 requires every non-adversarial cell to agree with `model.py` **and
   with every other cell**. R1 reading a freed record agrees with nothing.
2. **What a stale read returns is a function of the `-O` level**, and
   `build.py:67` puts both levels in one agreement set. TASK_055_REVIEW blocker
   B1 measured it: `gcc -O0..-O2` print `2582767925679282152` and `gcc -O3`
   prints `6789584477807083544`, because at `-O3` the stores into the recycled
   record are dead-store-eliminated — **the `-O3` binary does not contain the
   recycled record at all**, so that row would not have executed the bug it
   claimed to model.

`inputs/gen.py` enforces the rule by running a copy of the checked kernel over
every window of every blob it writes and refusing to emit a benign blob in which
any READ names a closed slot. **It fired on the first draft of
`degenerate.bin`**, which contained a `READ 0` after a `CLOSE 0`.

---

## 8. The R3 side: two in-contract spellings

`spec.md`'s `idiom` block pins the *operations* and deliberately leaves the
*spelling of the liveness test* free, exactly as p14 leaves its fold loop
unpinned. Two in-contract R3 spellings, both zero `unsafe` and zero TCB:

- **shipped**: CLOSE is `tab[h].take().is_some()` — one visit does the free, the
  invalidation and the test; READ is `match &tab[h] { Some(rec) => .., None =>
  .. }` — one discriminant test.
- **`r3_issome`** (`controls/`): R2's spelling — `is_some()` then
  `tab[h] = None`, and `is_some()` then `unwrap()` — two visits and two
  discriminant loads on each path.

```
-O3 isolated     whole-program Ir/call     small        large
safe_tuned (shipped)                      2687.9135    9923.1610
r3_issome                                 2697.4293    9955.1694
safe_naive                                2697.4293    9955.1610
```

**`r3_issome` is `safe_naive` — to the last digit on `small` and to within
0.0084 on `large`.** That is not a coincidence and it is worth stating: p27's R2
and R3 differ in *exactly* these two spellings and in nothing else, so the
control reproduces R2 from R3 and confirms that the whole `R2 − R3` gap is the
two fused tests.

**The cheapest R3 found is the shipped one**, on both inputs, by **9.52** on
`small` and **32.00** on `large`. ⚠ The word is "cheapest **found**", on a named
input, and never "minimum": three published floors on this project have been
refuted by the first lever the next agent pulled
(`.memory/01-ladder.md` finding 12). Two spellings is a two-lever search and is
not evidence of a floor.

**The fixed-R4 bound.** `R3ship − R4ship` is `+223.26` / `+782.25`
whole-program, and per finding 14 it bounds `inf(in-contract R3) − R4ship` and
nothing else — a bound only because R4 is held fixed **by fiat**. ⚠ And on p27
it is a bound on something that is **not the safety tax**, because of the
epilogue asymmetry in 5e. No pair interval is reported: the R4 side was searched
once (`r4_tabchecked`, which is dearer and inadmissible) and no admissible
cheaper R4 was found, so the R4 endpoint is **degenerate as far as this task
searched** — which is falsifiable, where "unavailable" would not be.

## 9. The sweep: what fits, what does not, and the DOMAIN

`inputs/gen.py --sweep` writes 80 blobs in three bands;
`controls/sweep_ir.py measure` takes the **whole-program** marginal Ir per call
over each (`(Ir(4000) − Ir(2000)) / 2000`, interleaved by cell, per-PID
scratch), and `... fit` does the regression. **Every number in 9a–9c is `-O3`,
inline mode `isolated`** — `sweep_ir.py`'s defaults, and named here because p10
fitted both modes and its regressors *swapped roles*
(`.memory/03-measurement.md`), so a mode-free per-call `Ir` is under-specified.
The `whole` mode was not swept. Four regressors, all computed from
the file with zero fitted parameters: `nopen`, `nclose`, `nread` (operations
*accepted*) and `nrej` (rejected on any path, folding `SENT`).

- **band O** — mix fixed, op count swept 8…128 in steps of 4 (31 blobs). Every
  regressor scales together, so this band alone cannot separate them.
- **band R** — op count held at 96, read fraction swept 0…0.80 (17 blobs). The
  allocator traffic falls exactly as the reads rise; this is what breaks band
  O's collinearity.
- **band S** — op count and mix held, the generator's live-record working set
  swept 1…32 (32 blobs).

### 9a. The LEVELS are not a law, and the number says so

```
c-gcc          nopen= 205.5226  nclose=  16.6407  nread=  22.4160  nrej=  24.2276  const= -72.2877   max|resid| 164.5959  n=80
c-gcc-h        nopen= 205.4624  nclose=  18.4425  nread=  24.3568  nrej=  24.1926  const= -72.9441   max|resid| 162.7976  n=80
safe_tuned     nopen= 223.1133  nclose=  25.5964  nread=  33.7158  nrej=  33.9437  const=  -4.1873   max|resid| 153.3527  n=80
unsafe         nopen= 223.1289  nclose=  12.6104  nread=  26.7182  nrej=  28.9679  const=-117.0504   max|resid|-153.6308  n=80
```

**A max residual of ~154–165 Ir/call on levels of 6 000–10 000 is 2%, and 2% is
not a law.** It is a fit with a missing column, and the residual has no band
structure (band means −1.4, +19.1, −8.8 for `unsafe`), so it is not a band
offset either. **This is not published as a law and the word is not used for
it.**

### 9b. The missing column is partly identified, and identifying it does not close the gap

Split `nopen` into tcache **hits** and **misses** — an OPEN reuses a chunk iff a
CLOSE has put one in the bin since the last OPEN took it out, which is
computable from the file with a 7-deep LIFO simulation and no fitted parameter:

```
              nopen (one rate)   ->   hit / miss
c-gcc         205.52                  178.11 / 221.96     max|resid| 164.60 -> 142.16
c-gcc-h       205.46                  177.88 / 222.01     max|resid| 162.80 -> 140.03
safe_tuned    223.11                  194.26 / 240.41     max|resid| 153.35 -> 126.89
unsafe        223.13                  194.35 / 240.39     max|resid| 153.63 -> 127.22
```

**A recycled allocation is ~44 Ir cheaper than a fresh one, consistently on all
four rungs** — and the split cuts the residual by only 17%. So the op *order*
is a real column, it is now measured rather than hypothesised, and **it is not
the only one left**. This is p10's 3 → 4 → 6 arc arriving on the first try: the
domain is a list of missing columns, and the list is not closed.

### 9c. The DIFFERENCES, which is what may be quoted

The allocator is 58–62% of every level (3a) and **cancels exactly** in a
matched-spelling difference, which is why these residuals are two orders of
magnitude smaller:

```
  R1h - R1  (gcc)      nopen=  -0.0601  nclose=   1.8017  nread=   1.9408  nrej=  -0.0350  const=  -0.6564   max|resid|   6.4487
  R3 - R4              nopen=  -0.0157  nclose=  12.9860  nread=   6.9976  nrej=   4.9758  const= 112.8630   max|resid|   2.9232
  R3 - R1h (gcc)       nopen=  17.6508  nclose=   7.1539  nread=   9.3590  nrej=   9.7510  const=  68.7568   max|resid|  33.5069
  R4 - R1h (gcc)       nopen=  17.6665  nclose=  -5.8321  nread=   2.3614  nrej=   4.7752  const= -44.1062   max|resid|  32.5159
```

Three things are worth reading off this, and one thing must not be:

1. **`R3 − R4`'s `nopen` coefficient is `−0.0157` — zero to within the
   residual.** *The allocation itself costs the two representations the same.*
   That is the equivalence argument of 2, confirmed by measurement rather than
   asserted: `Box::new(a)` and `std::alloc::alloc(layout)` are the same
   `malloc(1)` and the fit cannot tell them apart. The `R3 − R4` gap is
   `nclose`, `nread`, `nrej` and a constant — i.e. **the per-operation
   bookkeeping and the epilogue asymmetry (5e), not the allocation**.
2. **`R1h − R1`'s `nread` coefficient is `1.9408`, with `max|resid| 6.4487` over
   80 blobs** — the liveness conjunct costs gcc about **2 Ir per READ**, and the
   attribution is mnemonic by mnemonic off the listing, not inferred from the
   fit. `harness/asm.py diff` on the two gcc kernels at `-O3`, on the READ path:

   ```
   R1                              R1h
   cmp    %r15,%rsi                cmp    %r15,%rcx          ; h < ntab
   jae    TGT                      jae    TGT
                                   cmpb   $1,(%rsp,%rcx,1)   ; <-- live[h] == 1
                                   je     TGT                ; <--
   mov    (%rsp,%rsi,8),%rax       mov    (%rsp,%rcx,8),%rdi
   movzbl (%rax),%r14d             ...
   ```

   **Exactly two instructions, one `cmpb` against the liveness byte and one
   `je`**, executed once per READ that passes the slot bound. `1.9408` fitted
   against `2` off the listing, with the shortfall in the `nclose` term below.
   Static counts agree: `n_fn_nopad` 146 → 149, `+3`.
3. ⚠ **But `R1h − R1` also carries `1.8017·nclose`, and R1's and R1h's CLOSE
   paths are character-identical** — the listing diff above shows gcc
   re-allocating registers across the whole function (`%rsi` → `%rcx`, `%rcx` →
   `%r8`) and moving its alignment padding (`xchg %ax,%ax` → `cs nopw`), which
   is where a per-CLOSE difference between two identical source paths can come
   from. That coefficient cannot be the conjunct; it
   is gcc's codegen shifting elsewhere in the function when the conjunct is
   added. **So "the hardening costs 2 Ir per protected read" is not what this
   fit says** — it says the two programs differ by about 2 Ir per read *and*
   about 1.8 per close, and only the first has a mechanism. Constraining the fit
   to `nread` alone gives `2.2180·nread + 13.8198` with `max|resid| 26.4193`,
   four times worse: the `nclose` term is carrying real signal.
4. **`R4 − R1h` and `R3 − R1h` carry `17.67·nopen`** — unsafe Rust's allocation
   is ~18 Ir/record dearer than C's `malloc(1)`, identically on both Rust rungs.
   That is `__rust_alloc`'s wrapper around `malloc`, not a safety cost, and it
   is why the C-vs-Rust rows of 3 must not be read as a safety column.

**Not measured in this sweep: `c-clang` and `c-clang-h`.** The sweep ran four
cells; the clang pair's difference is quoted only at the two matrix inputs (3b),
where it is `+4.95` / `+3.76` against gcc's `+19.83` / `+91.01`. **A four-fold
and twenty-four-fold compiler disagreement on one added conjunct deserves the
band and did not get it** — see "not done" in the report.

### 9d. The DOMAIN

⚠ **A law owes its domain, and the domain here is a list of MISSING COLUMNS.**
Four are known missing, one of them now measured (9b):

1. **`RECSZ`** — one byte per record, everywhere. glibc rounds `malloc(1)` to a
   32-byte chunk, so the entire sweep sits in **one size class and inside the
   tcache**. A record that crossed into another bin, or a workload that
   exceeded the tcache's 7-entries-per-bin, is a different allocator.
2. **`TABCAP`** — 32 slots, in every rung and every blob. It sets the table's
   extent, R2/R3's drop-glue trip count and R4/R5's epilogue trip count.
3. **the allocator** — glibc 2.39. Its tcache *is* the recycling mechanism the
   adversarial row depends on.
4. **the op ORDER** — swept in mix and count, not in interleaving. **Measured to
   matter (9b): ~44 Ir per record between a recycled and a fresh allocation.**

**The list is not closed**, and 9a's 2% residual is the standing evidence that
it is not.

## 10. The proof mutants

Two, both of which **fail**, and both aimed at the temporal property rather than
at a bound:

`controls/proof_mutants.py --run` regenerates both from `verus.rs` by exact-string
substitution and runs them; the levers are asserted to fire, so a mutant that
silently matched nothing cannot look like a measured null.

**M1 — delete the liveness conjunct from the READ path** (`if h < ntab &&
arr_get_unchecked(&live, h) == 1u8` → `if h < ntab`), *and the two ghost
`assert`s above the borrow with it*, so the failure is the real obligation and
not an assertion the author wrote. This is c/kernel.c's bug, written in the rung
that has to prove it:

```
verification results:: 14 verified, 1 errors
error: precondition not satisfied      <-- perms.tracked_borrow(h): dom().contains(h)
error: precondition not satisfied
```

**M2 — delete `arr_set_unchecked(&mut live, h, 0u8)` from the CLOSE path.** The
line the C programmer forgot:

```
verification results:: 14 verified, 1 errors
error: invariant not satisfied at end of loop body
```

**M2 is what makes "the proof forces the line C forgot" a fact rather than a
slogan.** `rec_free` has consumed slot `h`'s permission; the liveness array
still says the record exists; `wf` cannot be re-established. Note *which*
obligation fails: not a precondition at the deletion site, but the **loop
invariant** — the temporal property is a global fact about the table, and that
is why forgetting the line is invisible locally, in C as in Rust.

⚠ **The catcher is an ordinary `precondition not satisfied` / invariant failure,
NOT rustc's move checker.** TASK_055_REPORT §2.6's `E0382` is an artefact of a
hand-unrolled two-element probe and was retracted at TASK_055_REVIEW M2; with a
real permission map the permissions live in a `Map` and are removed with
`tracked_remove`, which is a *mutation* and not a move.

---

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's body is `v[i]` on the
same `&[u8]` with the same parameters and the same clause text. `v[i]` is the
*checked* form of the identical operation — `<[u8] as Index<usize>>::index`
performs the bounds test `i < v.len()` that `get_unchecked` requires the caller
to have performed — so a `requires` too weak to license the unchecked read is too
weak to license the indexed one, and Verus sees the second. Nothing else can be
substituted: there is no other safe expression whose value is `v@[i as int]`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs exactly one operation, a read of one element,
and returns it. `r == v@[i as int]` names that element and its value. There is no
second read, no write, no aliasing and no interior mutability: `v` is `&[u8]`, so
the item cannot modify anything, and `u8` has no padding or niche that could make
"the value read" ambiguous. The completeness question TASK_009_REVIEW raises — a
body that *also* reads `i + 1` — would be invisible to this contract, and that is
why Miri is mandatory on this pattern and runs over `unsafe.rs`, which contains
the same expression inline.

**(c) Does each clause mean the same in both configurations?** There is one
`requires` and one `ensures` and both are written in terms of `v@`, `i` and `r`
only. `v@` is `<[u8]>::view`, `i` is a `usize` parameter and `r` is the return
binding; none of the three is `#[cfg]`-dependent, none mentions a constant that
`slb_twin` could redefine, and `harness/check.py` separately rejects the token
`slb_twin` anywhere except in a twin's own attribute.

## SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[T; N]`; the twin's body is `v[i]` on the
same `&[T; N]` with the same parameters and the same clause text. For a
fixed-size array `v[i]` is the checked form of the identical operation — rustc
emits the bounds test `i < N` that `get_unchecked` requires the caller to have
performed — so a `requires` too weak to license the unchecked read is too weak to
license the indexed one. **It is generic over `T: Copy` and `N` on purpose**: the
pointer table `[*mut u8; TABCAP]` and the liveness array `[u8; TABCAP]` are the
same operation on two element types, and one item is one axiom instead of two.
Genericity does not weaken the argument, because the body is `T`-independent and
`vstd::array`'s `array_len_matches_n` supplies `v@.len() == N` for every `N`.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
read of one element, and returns it; `r == v@[i as int]` names that element and
its value. `v` is `&[T; N]`, so nothing can be modified. **For `T = *mut u8` the
value is a POINTER, and "the value read" means the pointer's address *and* its
provenance** — `PtrData` carries both and `Seq<*mut u8>` equality is equality of
both, so the clause is complete in the sense the permission map needs: the
invariant `perms[j].ptr() == tab[j]` would not survive a body that returned a
pointer with the same address and different provenance. A body that also read
`i + 1` would be invisible here, which is why Miri is mandatory and runs over
`unsafe.rs`, whose `arr_get_unchecked` is the same expression.

**(c) Does each clause mean the same in both configurations?** One `requires` and
one `ensures`, both in terms of `v@`, `i` and `r` only, none `#[cfg]`-dependent
and none mentioning a constant `slb_twin` could redefine. `TABCAP` does appear in
the *call sites*' types, but not in this item's clauses.

## SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }`; the twin's is `v[i] = x`, the checked
form of the identical store, with the same parameters and the same clause text.
Weaken the shared `requires` and Verus rejects the indexed store.

**(b) Is the `ensures` complete?** This is the harder of the two and the answer
is the whole-sequence form: `final(v)@ == old(v)@.update(i as int, x)` says both
*"slot `i` became `x`"* and *"nothing else moved"*. A trusted body that also
wrote `i + 1` would violate the second half and Verus would reject it **if it
could see the body** — it cannot, which is exactly TASK_009_REVIEW's x4 and
exactly why `miri.required` is `true` on this pattern and runs over `unsafe.rs`,
which performs the same store inline. There is no read, so there is nothing else
to state. **`x` is a pure VALUE parameter** — stored, never used as an address,
an index or a length — so it carries no precondition; that is the
parameter-coverage false positive `.memory/04-verus.md` names, `spec.md`'s
`verus.unsafe_justifications` declares it, and the gate shouts it every run.

**(c) Does each clause mean the same in both configurations?** `old(v)@`,
`final(v)@`, `i` and `x` only; no `#[cfg]`, no redefinable constant.

## SLB-TRUSTED-ARGUMENT verus.rs rec_alloc

**(a) Is the twin's body the right checked stand-in?** **The twin's body is
`allocate(size, align)` — `vstd::raw_ptr::allocate` itself.** That is the
strongest stand-in available anywhere in this project: the checked
implementation of the trusted item is the very API the item is a copy of, so
what step 5c-twin proves is that this crate's contract is **no stronger than the
one vstd already discharges**. If any `requires` here were weaker than vstd's, or
any `ensures` stronger, the twin would not verify.

The item exists for **codegen and not for trust** (NOTES 5a): vstd carries no
`#[inline]` on `allocate`, so calling it emits a GOT-indirect cross-crate call
that `unsafe.rs` cannot produce and the `identity` pin drops to `differ`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs one operation — `std::alloc::alloc(layout)`
after `Layout::from_size_align_unchecked(size, align)`, aborting on null — and
returns the pointer plus two tracked permissions. The three clauses state exactly
what a caller may conclude: the `PointsToRaw` covers `[addr, addr+size)`, the
`Dealloc` records the address, size, align and provenance the eventual
`rec_free` must match, and the returned pointer's provenance is the
`PointsToRaw`'s. ⚠ **Two further clauses were copied from vstd and then
DROPPED** — `addr + size <= usize::MAX + 1` and `addr % align == 0` — because
the gate's clause-mutation stage found them **not load-bearing**: this kernel
allocates at `align == 1`, where `addr % 1 == 0` is a tautology and the
`usize::MAX` bound is never used. Dropping them makes the item strictly weaker
and the twin still verifies, which is the direction the gate asks for. The
`requires` — `valid_layout(size, align)` and `size != 0` — is vstd's own, and the
second is deliberately not a tautology (`RECSZ` is 1, but the item is generic in
`size`).

**(c) Does each clause mean the same in both configurations?** Every clause is in
terms of `size`, `align` and the return binding `pt` only, and all three of
`PointsToRaw::is_range`, `Dealloc::view` and `DeallocData` are vstd items that
`slb_twin` cannot redefine. The shipped item and the twin sit in the same module
with the same imports and the same `opens_invariants none`.

## SLB-TRUSTED-ARGUMENT verus.rs rec_free

**(a) Is the twin's body the right checked stand-in?** **The twin's body is
`deallocate(p, size, align, pt, dealloc)` — `vstd::raw_ptr::deallocate`
itself**, for the same reason and with the same force as `rec_alloc`: the gate
proves this crate's copy is no stronger than vstd's original. Same codegen
motivation (NOTES 5a).

**(b) Is the `ensures` complete?** There is no `ensures`, and that is correct
rather than lazy: the item's whole semantic content is that it **consumes** the
`PointsToRaw` and the `Dealloc`. Linearity is the postcondition. A caller that
has given up slot `h`'s permission cannot later present it to `rec_read`, and
that is the temporal property this pattern is about — it is carried by the type
system rather than by a clause, which is why deleting `live[h] = 0` fails the
*invariant* rather than a precondition (NOTES 10, mutant M2). The `requires` is
vstd's own, six conjuncts, and covers every parameter: `p`, `size` and `align`
through the four `dealloc@.*` equalities, and both permissions through
`pt@.is_range(..)` and the provenance equality. **The body performs one
operation**, `std::alloc::dealloc(p, layout)`.

⚠ **Note what a wrong body here would do and what would catch it.** A body that
deallocated a *different* pointer, or that did nothing at all, would satisfy this
contract — there is nothing to satisfy. Nothing in Verus can catch it; **Miri
can**, and does, over `unsafe.rs`'s identical `rec_free`: a leak or a
mismatched free is a Miri error, and `miri.required` is `true` for exactly this
reason. This is the sharpest instance in the tree of `.memory/04-verus.md`'s
point that an `external_body` `ensures` is an axiom about a body no verifier
reads.

**(c) Does each clause mean the same in both configurations?** Every conjunct is
in terms of `p`, `size`, `align`, `pt@` and `dealloc@` only; `Dealloc::addr`,
`size`, `align`, `provenance` and `PointsToRaw::is_range`/`provenance` are vstd
items `slb_twin` cannot redefine. Both items sit in the same module with the same
imports and the same `opens_invariants none`.

---

## 11. What is NOT done, and what a reviewer should attack first

- **No layout population has been run.** `controls/clayout.py` is ported from
  p14 and takes p27's cells, but `--build`/`--time`/`--modes` have not been run,
  so **every `ns` number in `results/p27-handle-table.json` is one draw of
  unknown width** and none is quoted here (3c). p27 needs it more than p14 did,
  because its wall clock is a function of the allocator's state as well as of
  the code.
- **The sweep measured four cells, not six.** `c-clang` and `c-clang-h` were not
  swept, so the compiler disagreement in 3b (`+4.95` / `+3.76` against gcc's
  `+19.83` / `+91.01` for one added conjunct) has **no band behind it**. That is
  the single most interesting unexplained number in this pattern and it is the
  first thing to attack.
- **The level fit is not a law and is not offered as one** (9a): max residual
  ~2% after the tcache hit/miss column is added (9b). At least one column is
  still missing.
- **`R2` was not searched.** Two in-contract R3 spellings were priced (8) and
  one R4 lever (4); no attempt was made to find a cheaper R2, and none to find a
  cheaper *admissible* R4. The R4 endpoint is reported as degenerate **as far as
  this task searched**, not as a floor.
- **`RECSZ` is 1 and was never varied** (9d). Everything here is one glibc size
  class inside the tcache.
- **The `adversarial-noreuse` R1 cells are not reproducible across runs**, by
  design (7). The gate JSON's recorded stdout for those two cells changes on
  every run; that is a note, not a failure, and it is the row's point — but a
  reviewer diffing two gate runs will see it and should not read it as churn.
- **`c/kernel.c`'s `abort()` on allocation failure is unreachable at `RECSZ = 1`
  on this box** and is present so that all seven rungs agree with
  `vstd::raw_ptr::allocate`'s own behaviour, not because it fires.
