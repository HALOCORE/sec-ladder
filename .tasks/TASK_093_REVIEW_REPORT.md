# TASK_093_REVIEW — report: uphold the `p28` refusal, REJECT its reason

**Role: research reviewer.** Ran concurrently with `TASK_094`. Nothing written
outside `.temp/r93/`; no `check.py`, no `measure.py`, no `--cargo`, no `git add`,
no `.memory/` / `patterns/` / `pilot/` / `harness/` edit, no write to
`.temp/t93|t91|p28|p12|p36`. `.temp/r93/build.sh` regenerates every number.

**PROTOCOL rule 2 running count: 264 → 270.** Six measured contradictions,
listed at the end.

## VERDICT

**Uphold the REFUSAL of `p28` as a second temporal row. Reject `§0.3`'s reason
and `§2`'s kill sentence.** The reusable reason is `D` below.

⚠ **Do not land owed memory updates #1 (category error) or #3 (false as
stated).** #2, #4 and #5 are sound — #4 should also record that the gate is
unaffected *and* that clang links ASan statically, so `p12`'s control is immune.

---

## BLOCKER 1 — `§0.3`'s structural claim is a ONE-SPELLING result, not a class result

`TASK_093_REPORT.md:24-25` / `.temp/t93/rs/boxdll.rs`. Three independent defects.

**(a) The `E0382` is a plain double move in the probe.**
`.temp/t93/rs/boxdll.rs:22-29` writes `Some(n)` in *both* match arms and then
`l.tail = Some(n)`. Control (`.temp/r93/rs/e0382_control.rs`), no data structure
at all:

```
fn take(_s: String) {}
fn main() { let s = String::from("x"); take(s); take(s); }
-> error[E0382]: use of moved value: `s`
```

Same diagnostic. It is about a double move, not about lists.

**(b) The `E0499` gloss — *"an O(1) unlink needs `&mut` to BOTH neighbours
through the victim"* — is refuted by four compiling spellings, all
`#![forbid(unsafe_code)]`, rustc 1.97.1.**

`.temp/r93/rs/a_cell_arena.rs` is a **fully intrusive** DLL, both links inside
the node, `Cell<Option<&'a Node<'a>>>`, O(1) unlink reaching both neighbours;
`Cell` means no `&mut` exists, so `E0499` cannot arise:

```
built  len=5 fwd=954336810 bwd=958090410
unlink len=4 fwd=30785058 bwd=30906078
victim val still readable = 1002
```

`.temp/r93/rs/a_splitborrow.rs`:

```
s1 sequential-&mut      fwd=30785058 bwd=30906078
s2 split_at_mut         fwd=30785058  (two &mut alive simultaneously)
s3 Box + REAL free      fwd=30785058 bwd=30906078 live_slots=4
```

`s2` is the manager's named spelling and holds two `&mut` **simultaneously**.
`s3` frees per node. (`fwd`/`bwd` match `.temp/t93/rs/rcdll.rs`'s own `ok` line —
same list.)

**(c) The headline is self-contradicted by its own table two lines below it.**
`§0.3` row 3 (`Rc<RefCell<Node>>` + `Weak`, *"frees: yes"*) **is** an intrusive
DLL with owned nodes in safe Rust.

**What is actually true, measured:** every safe spelling that frees *per node*
does so through a discriminant/refcount test (= `p27`'s mechanism); every
spelling that avoids that never frees per node. `a_cell_arena.rs` is a **fourth**
spelling `§0.3`'s three-row table does not contain (it lands in the never-frees
bucket via `Box::leak`, which also makes it illegal under the 200k-call rule).

**Failure scenario:** owed memory update #3 lands in `.memory/` as *"Safe Rust
has no owned intrusive DLL (E0382 + E0499), so any linked pattern's safe rung is
an arena that never frees, or p27's representation."* The next agent scheduling
`p29` (BST) or `p30` (chained hash) refuses on a premise that four programs on
this box disprove. **This is `p31`'s failure mode verbatim: right verdict, wrong
reason, reason goes into the authoritative layer.**

## BLOCKER 2 — `§2`'s kill sentence is FALSE, and the engineer's own kernel refutes it

> *"the only `p28` ladder in which R3 and R4 are the same program with the same
> allocation behaviour is the arena one — and neither of its rungs frees
> anything … The only internally consistent `p28` is an `index >= len` pattern,
> the fifteenth."*

`.temp/r93/rs/cost2.rs`: R3 = the engineer's `k_box_arena` verbatim; R4 =
`k_box_arena_unchecked` (`get_unchecked` + `unwrap_unchecked`). Same program,
same `Vec<Option<Box<BNode>>>`, **one `Box` alloc + one free per node in both**,
same `u32` index links. Checksums identical (`330333705960196096` @2048,
`2003388499204575232` @4096); **6 distinct md5s of 6** kernel bodies from the
**linked** binary.

```
R3 box_arena            (bounds check + ASKING)   408.078
bc_only                 (ASKING only)             396.078   bounds check = +12.000
ask_only                (bounds check only)       397.078   THE ASKING   = +11.000
R4 box_arena_unchecked  (neither)                 384.078   TOTAL        = +24.000
residual (non-additivity)                                        +1.000
ALLOCATOR CONTRIBUTION TO THE DIFFERENCE                          0.000
```

A **closed decomposition with a `0.00` allocator term** — the exact form `p27`
published (`230.07 = 109.65 + 120.42 + 0.00`). **`p28` can do what `p27` did.**
So the manager's question C is answered: **the cost half of the refusal does not
follow.** It is still `p27`'s *mechanism* (the ASKING is the `Option`
discriminant), so the bug-class half is untouched — but *"an allocator term makes
the ladder dishonest"* is refuted by measurement.

## MAJOR 1 — `§3`'s *"the probe reports the WRONG SIGN"* is a CATEGORY ERROR

`.temp/t91/p28probe.rs:54-95`: `k28_checked` and `k28_rawptr` **both** work on a
pre-built arena — there is **no `alloc`/`dealloc` in any `TASK_091` kernel**. Its
`+12.50` has the allocator absent from **both** sides. The report's `−296.00`
puts a per-node `malloc` on **one** side only. **That is a different RUNG PAIR,
not a probe-shape defect** (probe shape = same rungs, different harness).
Comparing like with like (Blocker 2, free present in both rungs) gives
**`+24.00`, R3 dearer — the same sign as `TASK_091`'s `+12.50`.**

**The proposed "third probe-shape failure mechanism" is not established.**

## MAJOR 2 — the `box_arena` band jump is `malloc_consolidate`, not `p26`'s situation

Not `Vec` growth doubling (`with_capacity(n)`, no reallocation).
`callgrind_annotate`: a libc symbol at `+0xa9bb0` carrying **262,010 `Ir` appears
only at n=8192**, absent at 2048/4096; `262010/4096 = 63.97` = the whole
*"+64 `Ir`/node"*. Its body is the `xchg %rbx,0(%r13)` / `add $0x8,%r13`
fastbin-array sweep — glibc `malloc_consolidate`. The kernel symbol
`cost::k_box_arena` is **exactly 99.0 `Ir`/node at every n**. Decisive control:

```
n=8188 vec_bytes=65504 Ir=3659465
n=8189 vec_bytes=65512 Ir=3659903
n=8190 vec_bytes=65520 Ir=3922410   <- +262,507 Ir for ONE more node
n=8191 vec_bytes=65528 Ir=3922880
n=8192 vec_bytes=65536 Ir=3923290
```

`free()` of the `Vec` backing store crosses `FASTBIN_CONSOLIDATION_THRESHOLD`
(65536-byte chunk) between 8189 and 8190. Below it `box_arena` is flat:
`(3659903−1989775)/4093 = 408.045` vs `408.078`. So it is **not** `p26`'s
situation, *"`p28` could not be costed until its input band was designed"* does
not follow, and `box_arena`'s advantage over `rc` is a stable **+68.00**, not
*"collapses to +4.02"*.

## D — the manager's family generalisation: REFUTED for 3 of the 5 rows

There is a **third** and a **fourth** outcome besides *"arena that never frees"*
and *"`p27`'s mechanism"*:

- **`p33` / `p32` — THE TYPE SYSTEM IS SILENT.** `.temp/r93/rs/a_freelist.rs`,
  `#![forbid(unsafe_code)]`, slot free list with real recycling:

  ```
  uar   stale=2 fresh=2 SAME SLOT=true
  uar   read-through-stale-index val=9999 (expected 1002, actually 9999)
  df    x=2 y=2 ALIASED=true x.val=8888 y.val=8888
  ```

  Miri UB count: `ok 0, uar 0, df 0`. **Use-after-recycle AND slot double-free
  are writable in safe Rust, silently wrong, Miri-clean.** That is `p04`'s
  finding, not `p27`'s, and it kills `p33` and `p32` for a *different* reason
  than `p28`.
- **A generation tag does not rescue it.** `.temp/r93/rs/a_gen.rs`:
  `gok get(stale) = None <- CAUGHT`; `gbug get(stale) = Some(val=7777) <- NOT
  CAUGHT`. Both compile under `forbid(unsafe_code)`, both Miri-clean. The gen
  bump is a hand-written second store C can write identically. ⚠ **`RECAP.md`'s
  p14-cycle `(slot, gen)` proposal therefore yields a `p04`-shaped row, not a
  temporal one.**
- **`p34` — the safe rung is WORSE than C.** `.temp/r93/rs/a_leak.rs`: `Rc` both
  ways = cycle = leak; `Weak` for `prev` = no leak; same checksum (954336810).
  Miri default flags: `cycle` → 5 × `error: memory leaked: allocNNNN (Rust heap,
  size: 48, align: 8)`, `weak` → clean.

**Operative rule, and this is the replacement for `§0.3`'s sentence:**

> **Safe Rust's temporal guarantee is a guarantee about the ALLOCATOR. A
> structure that recycles its own storage gets no guarantee at all.**

## Does a `p28` survive? Two candidates, both with named limits

1. **A cost row** (Blocker 2): `box_arena` vs `box_arena_unchecked`, publishing
   `+24.00 = 12.00 bounds check + 11.00 THE ASKING + 1.00 interaction, 0.00
   allocator`. **The ASKING at `11.00 Ir`/node is a number `p27` has no
   counterpart for** (it published `0.00` for the lifetime guarantee). But it is
   `p27`'s mechanism — a replication with a new number, not a new class. Probe
   shape.
2. **The leak row — `p34`'s, not `p28`'s.** The `Rc` cycle. Genuinely absent from
   the tree, an inversion the tree does not have, and `p27` explicitly does
   **not** model a leak (`p27/NOTES.md` 0b point 3). ⚠ **Named kill:**
   LeakSanitizer is live on this box under the gate's flags
   (`.temp/r93/c/lsan_min.c`, `-O0 -static-libasan` → `ERROR: LeakSanitizer:
   detected memory leaks`, exit 1; `check.py`'s `"ERROR:" in se` would catch it)
   — **but it is `-O`-dependent on a leaked linked list**, `.temp/r93/c/leak3.c`
   at the gate's exact stage-7 flags:

   ```
   -O0  leak=1 -> exit=1  reports=1
   -O1  leak=1 -> exit=0  reports=0
   -O2  leak=1 -> exit=0  reports=0
   ```

   `__lsan_do_recoverable_leak_check()` also returns 0 at `-O1` (stale
   register/stack reachability). ⚠⚠ **THE GATE BUILDS STAGE 7 AT `-O1`.**
   Valgrind memcheck **cannot run on this box at all** (`Cannot continue`, needs
   `libc6-dbg`; callgrind is fine), so the C side has **no working leak detector
   here. Miri is the only one.**

## Clean negatives — named attacks that did NOT land; do not re-run these

- **Attack B, Miri on `c2b`.** Full output, both borrow models.
  `-Zmiri-tree-borrows` gives **identical** kind, message and site to stacked
  borrows for both `c2a` and `c2b`. The kind string genuinely is the same
  (`memory access failed: … dangling`; no *"double free"* diagnosis, unlike
  ASan's `attempting double-free`). The **site** differs — `c2b`'s UB is at
  `rawdll.rs:30` inside `free_node`/`dealloc`, and its *"occurred here"* line
  equals its *"deallocated here"* line, the self-loop signature of a double free
  — but `§0.2` already says *"reported inside `dealloc`"*. **The engineer's
  ground 1 survives.**
- **The C detector table reproduces exactly, under the GATE's flags** (`-O1
  -static-libasan -static-libubsan`, not the shared build the engineer used):
  `ok`/`c1` no report, `c1f`/`c2a`/`c3` `heap-use-after-free`, `c2b` `attempting
  double-free`, plain exits 0/0/139/139/134/0. **Every `§0.1` row.**
- **`rawptr`'s `+321` is a real allocator price; the `p31` *"malloc/free pair
  deleted"* artefact does not apply.** `k_alloc_pair24` — nothing but
  `alloc(24)`/read/`dealloc`, same liveness profile — costs **340.823 `Ir`/node**
  (16-byte version identical; glibc rounds both to a 32-byte chunk). **Nothing
  was deleted.**
- **All six slopes reproduce on the 2k→4k band to 3 dp** on an independent
  invocation, and the `−9.00 / −16.00 / +321.00 = +296.00` decomposition
  reproduces **exactly**.
- **All of `§2`'s arithmetic is correct**: `355.005/59.008 = 6.0162`;
  `321/296 = 108.45%`; `9/296 = 3.04%`; `16/25 = 64.0%` against the catalogue's
  `32.0%`.
- **`p01` in the count of 14: VERIFIED.** `patterns/p46-bignum-mac/NOTES.md:26`,
  `spec.md:29` and `c/kernel.h:13` all enumerate the same thirteen + `p46`;
  `.memory/06-catalogue.md` gives `p01`'s bug class as `none (calibration)`.
  **14 carry the axis, 13 model a bug. Three tracked files.**
- **`LD_PRELOAD` exposure elsewhere: essentially none.** The only tracked
  `controls/` script that builds ASan without `-static-libasan` is
  `patterns/p12-strcat-fixed/controls/threshold_probe.py:117-118` — and it uses
  **clang, which links the ASan runtime statically by default**, so it is immune
  (measured: `ldd` shows no `libasan`; the report prints with `LD_PRELOAD` set).
  `p08`/`p18`/`p22`/`p38`/`p46` all pass `-static-libasan`; `harness/` has exactly
  one `-fsanitize` site, static. **UBSan-only is unaffected** — gcc + shared
  `libubsan.so.1` with `LD_PRELOAD` set still prints `runtime error:`. **The
  exposure is ASan-specific.**

## Problems

- **MINOR 1 — the reproducibility control's scope is narrower than stated.** The
  **1k→2k band does not reproduce**: `rawptr` mine `354.960` vs published
  `352.729`, `rc` `475.960` vs `473.728` (≈2.23 `Ir`/node, one extra `brk`-class
  event at n=1024). 2k→4k is exact on all six. **Only slopes were quoted, so
  nothing published is wrong** — but *"the slope is identical to four decimals"*
  is a statement about one band.
- **MINOR 2 — candidate 3 was refused at its weakest reading**
  (`TASK_093_REPORT.md:152`): *"the distant-harm-site framing is real but it is
  `p13`'s axis, and `p13` ships it."* `p13`'s is a **spatial** bug; the pitch was
  *"applied to a temporal bug for the first time"*, and no measurement addresses
  that combination. Candidates 1, 1′, 2a, 2b and 4 **are** steelmanned.
- **MINOR 3 — one hand-run probe is `LD_PRELOAD`-exposed**:
  `.temp/p36/run_c_probe.sh:36-42` builds gcc + **shared** ASan with no `env -u`.
  Re-running it today yields a silent false negative. The output
  `patterns/p36-vtable-dispatch/NOTES.md:141-150` quotes **does** contain the
  ASan report, so nothing published is wrong — **re-derivability hazard only.**

## Unsure / not done

- Did **not** run `check.py` or `measure.py` (prohibited, `TASK_094` concurrent);
  touched nothing tracked; planted nothing. Git clean.
- **Did NOT run Verus at all** — `§1`'s `deallocate` / `wf`-after-key-removal
  question is exactly as open as the engineer left it.
- Did **not** re-run `.temp/t91/`'s binaries. The MAJOR 1 refutation is by
  **reading** `.temp/t91/p28probe.rs:54-118` (no `alloc`/`dealloc` in any kernel)
  plus an independent kernel family — **the same limitation the engineer
  disclosed, inherited.**
- Numbers are **probe shape**, same as the engineer's; no shipped `p28` exists to
  take a signature from, so `TASK_092`'s lesson is uncontrolled on both sides.
- `bc_only`/`ask_only` split the tax by **deletion**, so the `+1.00` residual is
  real non-additivity, unchased.
- ⚠ **The `+11.00` ASKING is NOT shown to contradict `p27`'s `0.00`** — `p27`'s
  zero is about a different comparison (R3−R4 on the shipped handle table). **Do
  not publish them as a contrast without re-measuring `p27`'s shape.**
- **`p29` (BST) and `p30` (chained hash) are UNPROBED**; D is refuted for
  `p32`/`p33`/`p34` only.
- The leak candidate is measured for **detectability**, not built. Whether an
  adversarial-only leak row is legal under the driver's `n_iters` is **argued,
  not demonstrated**.

## Memory updates owed (manager applies)

1. **Safe Rust's temporal guarantee is a guarantee about the ALLOCATOR**, so
   recycling structures get none (kills `p28`, `p32`, `p33` by one rule, and
   `p34` by a different one).
2. **`E0499` is not a barrier to a safe O(1) unlink** — `Cell`, sequential `&mut`
   and `split_at_mut` all compile.
3. **`malloc_consolidate` fires when a freed chunk reaches 64 KiB** and can add
   ~64 `Ir`/node to a whole band — a probe-container artefact any `Ir` sweep
   crossing that size will hit.
4. **LeakSanitizer is live under the gate's `-static-libasan` but SILENT at
   `-O1`/`-O2` on a linked list**, and **valgrind memcheck cannot run on this
   box.**

## The six contradictions

| # | contradiction |
|---|---|
| 265 | `E0499` refuted by three compiling spellings |
| 266 | the *"only internally consistent `p28`"* sentence refuted by a `p27`-style ladder on the engineer's own kernel |
| 267 | `§3`'s sign inversion is a **rung-pair change**, not a probe-shape mechanism |
| 268 | the `box_arena` band jump is `malloc_consolidate` at a 64 KiB `Vec`, not `p26`'s situation |
| 269 | **the manager's own family generalisation (D) is refuted** for `p32`, `p33` and `p34` |
| 270 | the 1k→2k band does not reproduce for `rawptr` and `rc` |
