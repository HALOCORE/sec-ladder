# TASK_093 — `p28` §0: REFUSED, with the measurement

**Role: research engineer.** **UNREVIEWED.** Nothing written outside
`.temp/t93/` and this file. No `check.py`, no `measure.py`, no `--cargo`, no
`git add`, no `.memory/` edit, no `.temp/p28/` write. **No rung, no `spec.md`,
no `model.py`, no `inputs/gen.py` was written** — §0 gates them and §0 refused.

**PROTOCOL rule 2 running count: 261 → 264.** Three of the manager's calls are
contradicted with measurements (§3's ranking, §2's confound magnitude, and the
`p27`-distinctness premise the row was scheduled on). The count it asked me to
verify — *"fourteen `index >= len` and one temporal"* — is **CORRECT**, with one
caveat below.

---

## VERDICT

**REFUSE `p28` as pitched.** All three of the manager's candidate shapes are
`p27`'s use-after-free in a costume, and the one that is *not* is not temporal at
all. The refusal does **not** rest on the detector alone (which is what killed
`p25`); it rests on a structural fact that was not known when the row was
written:

> **Safe Rust cannot express an intrusive doubly linked list with owned nodes.**
> So `p28`'s safe rungs have exactly three spellings, and **each one destroys a
> different half of the pattern**: the index arena never frees anything (the
> temporal class is structurally *absent*), and both spellings that *do* free
> catch the bug **by `p27`'s exact mechanism**, so they republish `p27`'s
> sentence.

And the cost side is worse than the confound the manager warned about, by 20×
and with the opposite sign.

---

## §0.1 — the detector test (`p25`'s standard), run

`.temp/t93/c/dll.c` — one intrusive DLL over `malloc`'d nodes, six variants,
`gcc -O1 -g -fsanitize=address,undefined` and plain `gcc -O2`.
⚠ **`env -u LD_PRELOAD` is required on this box** — `libstdbuf.so` is preloaded
and ASan refuses to start behind it (*"ASan runtime does not come first in
initial library list"*). This cost a full round of silent false negatives.

| variant | plain `gcc -O2` | ASan **first** report |
|---|---|---|
| `ok` correct | exit 0 `acc=985242876` | clean |
| **`c1`** stale NEIGHBOUR, victim **not** freed | exit 0 `acc=1912427208` (**silent wrong**) | **nothing fires** |
| **`c1f`** stale neighbour, victim **is** freed | SIGSEGV 139 | `heap-use-after-free` READ of size 8 |
| **`c2a`** double unlink, links read from victim | SIGSEGV 139 | `heap-use-after-free` READ of size 8 |
| **`c2b`** double unlink from a **cached triple** | glibc `double free detected in tcache 2`, abort 134 | **`attempting double-free`** |
| **`c3`** unlink-then-traverse via saved cursor | exit 0 `acc=954337800` (**silent wrong**) | `heap-use-after-free` READ of size 8 |

**Control, same compiler, same flags** — `p27`'s own bug reduced
(`.temp/t93/c/p27shape.c`: OPEN, OPEN, CLOSE 0, OPEN, `if (h < ntab)` only):

```
==652374==ERROR: AddressSanitizer: heap-use-after-free on address 0x502000000010
READ of size 1 at 0x502000000010 thread T0
```

That is the line `patterns/p27-handle-table/NOTES.md:999` publishes and the line
`TASK_083_REVIEW` quoted when it refused `p25` — **same message, same address.**

**Candidates 1′, 2a and 3 print it too.** So the manager's candidates **1 and 3
are refused at the detector**, on exactly `p25`'s ground.

## §0.2 — Miri, on the rung the ladder is actually about

`.temp/t93/rs/rawdll.rs`, the same six variants as unsafe Rust, run through the
pinned Miri (`miri 0.1.0 (d453bdd8f0 2026-08-14)`):

```
ok   exit 0
c1   exit 0   acc=1912427208            <- WRONG ANSWER, MIRI CLEAN
c1f  exit 1   in-bounds pointer arithmetic failed: alloc1429 has been freed, so this pointer is dangling
c2a  exit 1   memory access failed:      alloc1429 has been freed, so this pointer is dangling
c2b  exit 1   memory access failed:      alloc1429 has been freed, so this pointer is dangling
c3   exit 1   in-bounds pointer arithmetic failed: alloc1429 has been freed, so this pointer is dangling
```

⚠⚠ **Miri does not distinguish `c2b` either.** The double free collapses to the
same *"has been freed, so this pointer is dangling"* string, reported inside
`dealloc`. **So candidate 2's one distinguishing feature exists on the C rung
only and vanishes on the unsafe-Rust rung** — and `p27`'s `NOTES.md` 7a records
that Miri is *"the only tool in the matrix that checks the temporal property on
the unsafe Rust rung."*

## §0.3 — the structural fact, which is what actually kills the row

`.temp/t93/rs/boxdll.rs`, `#![forbid(unsafe_code)]`, rustc 1.97.1:

```
error[E0382]: use of moved value: `n`
error[E0499]: cannot borrow `b.next` as mutable more than once at a time
error: aborting due to 2 previous errors
```

`E0382`: the successor's `next` and the list's `tail` would both have to own the
node. `E0499`: an `O(1)` unlink needs `&mut` to **both** neighbours *through* the
victim. **There is no safe owned intrusive DLL.** `p27` did not face this — its
`Option<Box<u8>>` table is byte-for-byte the hardened C rung's `tab[]` minus
`live[]` (`NOTES.md` 0a), so R1-vs-R2 there is *one program against its guard*.

`p28`'s three options, all measured (`.temp/t93/rs/arena.rs`, `rcdll.rs`,
`cost.rs`):

| safe rung | frees per node? | temporal class | mechanism |
|---|---|---|---|
| `Vec<Node>` + `u32` links | **NO** — measured: `len` 5→5, `cap` 8→8, **0 heap blocks released by unlink** | **structurally absent** | none |
| `Vec<Option<Box<Node>>>` + index links | yes | present | **`p27`'s** — `a[b] = None` frees *and* invalidates in one operation; the stale link is `None`; the ASKING is the `unwrap` |
| `Rc<RefCell<Node>>` + `Weak` | yes | present | **`p27`'s** — dropping the last strong `Rc` frees *and* invalidates every `Weak`; the ASKING is `upgrade()` |

**And the index arena does not even prevent the bugs.** Under
`#![forbid(unsafe_code)]`:

```
a1_bug  fwd=30785058 bwd=958090410 allocs=5 frees=1     <- stale neighbour COMPILES, silent wrong answer, Miri clean
a2      x=2 y=2 aliased=true x.val=1200 y.val=1200 fwd=18446744073709551615
                                                        <- DOUBLE FREE COMPILES; becomes ALIASING + NON-TERMINATION, Miri clean, exit 0
a3      before len=5 cap=8 | after len=5 cap=8 | allocs=5 frees=5 | heap blocks released by unlink = 0
```

`a2` is the answer to *"but candidate 2b is distinct."* In the arena the double
free is a double push onto the free list, two future allocations return **the
same slot**, and the harm is `p04`'s (*"invisible to a memory-safety proof"*)
plus `p22`'s (non-termination). **Safe Rust prevents neither of the manager's
candidates in the only representation that keeps the rungs comparable.**

**And `Rc`/`Weak` — candidate 4, mine, the shape the manager did not list —
reproduces `p27`'s published sentence verbatim** (`.temp/t93/rs/rcdll.rs`):

```
ok   fwd=30785058 bwd=30906078  victim_alive_after=false
bug  fwd=30785058 bwd=32127     victim_alive_after=false
```

`32127 == 1004*31 + 1003` — the backward walk **truncates** at the stale link
because `upgrade()` returns `None`; the node really was deallocated. That is
*"the free and the invalidation are one operation in safe Rust and two in C, and
the bug is the third — the ASKING — going missing"* with `upgrade()` in place of
`live[h] == 1`. **`p27` in a costume at the RUNG BOUNDARY, which is worse than
at the detector.**

## §0.4 — verdict per candidate

| candidate | survives? | why not |
|---|---|---|
| **1** stale neighbour, no free | **NO — not temporal** | nothing is freed; ASan, UBSan and Miri all silent; safe Rust permits it. `p04`'s shape + `p22`'s silence. Re-pitch, do not relabel — the manager anticipated this in §0 and it is what happened |
| **1′** stale neighbour + free | **NO** | `p27`'s ASan line, `p27`'s Miri line |
| **2a** double unlink, read-first | **NO** | the victim's links must be *read* before they can be written through, so the UAF read always precedes the second free |
| **2b** double unlink, cached triple | **NO, and it is the closest call** | the **only** candidate distinct at the C detector (`attempting double-free`, abort 134 not SIGSEGV) — and `p27 NOTES.md` 0b agrees it is *"a different bug in a different class"*. **But** Miri is blind to the difference, the safe arena permits it silently, and the safe rungs that *do* prevent it prevent it by `p27`'s mechanism. Distinct at the detector, identical at the rung boundary |
| **3** unlink-then-traverse | **NO** | `p27`'s ASan line. The distant-harm-site framing is real but it is `p13`'s axis, and `p13` ships it |
| **4** `Rc`/`Weak` (mine) | **NO** | `p27`'s sentence verbatim |

---

## §2 — THE CONFOUND IS 20× BIGGER THAN THE MANAGER'S AND POINTS THE OTHER WAY

**Convention declared in `.temp/t93/rs/cost.rs`'s header before any run:**
marginal **whole-program** `Ir` per node lifecycle, callgrind `I refs:` total,
differenced across list length `n`; `rustc -O -C codegen-units=1`, every kernel
`#[inline(never)]` (**inline mode `isolated`**), `n` from `argv` at run time.
Whole-program and **not** kernel-exclusive, deliberately — every rung here
allocates, and `.memory/06-catalogue.md`'s `p48` and `p13` rows both record the
kernel-exclusive column erasing or reversing a comparison on a pattern that
allocates. ⚠ **These are PROBE-SHAPE numbers**; there is no shipped `p28`, so
`TASK_092`'s lesson is not controlled for.

All six kernels print **the same checksum** at `n=2048`
(`330333705960196096`). **Probe 2, from the LINKED binary** (`TASK_086`'s
instrument fix): **6 distinct md5s of 6.**

```
kernel               1k->2k    2k->4k    4k->8k
arena_checked            -     59.008        -      safe Vec, u32 links, bounds-checked
arena_unchecked          -     50.008        -      unsafe get_unchecked, same links
rawptr_bump          33.965    34.005    34.010     unsafe ptrs, ONE bulk slab
rawptr              352.729   355.005   355.036     unsafe ptrs, malloc/free per node
box_arena           407.965   408.078   472.050     SAFE Vec<Option<Box>>, index links
rc                  473.728   476.078   476.073     SAFE Rc<RefCell> + Weak
```

**Reproducibility control**, taken from an independent re-invocation via
`.temp/t93/build.sh`: the **intercept** moves `+19 Ir` on all three kernels
(argv/env length — the project's source-path-length artefact,
`.memory/01-ladder.md`) and the **slope is identical to four decimals**
(`59.0078`, `355.0054`, `34.0054`). **Only slopes are quoted anywhere in this
report.**

**Closed decomposition, exact, R3 → R4, 2048→4096 band:**

```
  remove the bounds check      arena_checked   -> arena_unchecked     -9.00
  index -> pointer             arena_unchecked -> rawptr_bump        -16.00
  bulk slab -> per-node malloc rawptr_bump     -> rawptr            +321.00
  -----------------------------------------------------------------------
  R4(rawptr) - R3(arena_checked)                                    +296.00   (exact)
```

⚠⚠ **A `p28` with R3 = safe index arena and R4 = raw-pointer DLL publishes
`355.0 / 59.0` = "safe Rust is 6.02× CHEAPER than unsafe Rust", and 321/296 =
108.4% of that gap is THE ALLOCATOR.** The bounds check is `9.00` — **3.0% of
the magnitude and the opposite sign.** That is `p10`'s trap at 6×, and RECAP
records five patterns that have already published a headline wrong in the
flattering direction. This one would be the sixth and the largest.

**The manager's named confound is real and is the SMALLER of the two.**
`.memory/06-catalogue.md` warns *"4.0 of the 12.5 `R3→R4b` gap is INDEX
SCALING"* = 32%. Measured here on the only pair where the comparison is
internally consistent — `arena_checked 59.008` vs `rawptr_bump 34.005`,
`+25.00` — the split is **9.00 bounds check (36%) and 16.00 index scaling
(64%)**. **Index scaling is twice the share the row predicts.**

⚠ **And that pair is the kill in one sentence:** the only `p28` ladder in which
R3 and R4 are the same program with the same allocation behaviour is the arena
one — **and neither of its rungs frees anything, so the only class its rungs
differ on is the bounds check.** *The only internally consistent `p28` is an
`index >= len` pattern, the fifteenth.*

**The numbers are not zero-parameter either.** `box_arena` is `408.078` on
2048→4096 and **`472.050`** on 4096→8192, while `rawptr_bump`, `rawptr` and `rc`
are flat to three decimals across every band. So `box_arena`'s **+68.00**
advantage over `rc` **collapses to +4.02 one band over** — `p26`'s situation, and
`p28` could not be costed until its input band was designed. **I did not identify
the mechanism of that jump.**

For the record, since `p27` measured its lifetime guarantee at exactly `0.00`:
the two safe rungs that preserve the temporal class cost **+53.07 (+14.9%)** and
**+121.07 (+34.1%)** against `rawptr` on 2048→4096. ⚠ **Do not quote either as
"the lifetime guarantee":** each is a composite containing the `9.00` bounds
check and the `16.00` index-vs-pointer term, and subtracting them is an
**additivity extrapolation across kernel families** — the one out-of-sample test
this project has, and it has already failed once (`p38`).

---

## §3 — "p28 IS NOT EXPOSED" IS REFUTED, BY A MECHANISM THAT IS NOT `p46`'s

`.memory/03-measurement.md` ranks `p28` *"not exposed"* to the probe-shape
defect. **Three of the manager's four rankings in that table are now refuted.**

✅ **Clean positive first — `TASK_091`'s probe is CORRECT where it is
comparable.** Its bounds-check tax `k28_checked − k28_unchecked = 20.003 −
11.503 = 8.50 Ir/victim` reproduces here at **9.00** on an independent kernel
pair. Its *checking* axis transfers.

⚠⚠ **What does not transfer is the axis `p28` claims.** `TASK_091`'s own report
says its probe *"drops `Tracked<Dealloc>` and LEAKS — there is NO `deallocate`
anywhere in it"* and ranks that as `p28`'s remaining risk. **The temporal class
lives in the free**, and once the free is present the sign of the published
comparison inverts:

```
TASK_091, no deallocate :  R3 - R4 = 20.003 - 7.507 = +12.50 Ir/victim   (R3 DEARER)
here,     with the free :  R3 - R4 = 59.008 - 355.005 = -296.00 Ir/node  (R3 CHEAPER)
```

So the probe does **not** merely lose the intercept, and not merely the slope as
in `p46` — **it reports the wrong SIGN for the comparison the pattern would
publish**, and the cause is an **omitted operation**, not a lost range fact.
That is a *third* probe-shape failure mechanism and it belongs beside the other
two.

⚠ **Honest limit:** I built an independent kernel family; I did **not** re-run
`.temp/t91/`'s own binaries. The refutation is by construction, not by
re-measuring their artefacts.

---

## §0.5 — THE COUNT, VERIFIED

**`index >= len` = 14**, and the manager is right: `p01 p02 p03 p05 p07 p11 p12
p13 p14 p16 p17 p19 p36 p46`, enumerated in `patterns/p46-bignum-mac/NOTES.md:26`
and `spec.md:29` — and `p46` is a **reviewed** pattern, so this is not an
unreviewed count.

⚠ **One caveat worth landing:** that list includes **`p01`, whose own catalogue
bug-class column reads `none (calibration)`.** So **14 patterns carry the axis;
13 model a bug on it.** Three files in the tree now assert an ordinal built on a
list containing a pattern that models no bug.

**temporal = 1** (`p27`). `grep -rl -i temporal patterns/*/NOTES.md` returns
`p08`, `p22`, `p27`; `p08`'s hit is *"the non-temporal one"* (a `memcpy`
threshold) and `p22`'s is a table row saying the borrow checker is *blind* to
temporal/aliasing. Neither is a temporal bug class.

**So the scarcity argument the row was scheduled on is TRUE, and it is not
enough** — nothing `p28` can build is a second temporal class.

---

## What a re-pitch would have to stand on — NOT probed, do not schedule on this

One thing survived that is genuinely absent from the tree, and it is **not** the
bug class: **`p28` is a REPRESENTATION SPLIT.** `p27 NOTES.md` 0a records that
`TASK_055` §2.8 predicted one for `p27` and it did not happen (*"the handle comes
out of a file, so it is an integer in every rung"*). `p28` is the case where it
is forced — `E0382`/`E0499` are the proof — and the tree has **zero**
representation-split patterns.

⚠ **Its kill risk is named and I have not probed it:** a representation split
means R1 and R2 are **not the same program**, which is the reviewer checklist's
*"did a rung quietly change the algorithm"* and fails `p27`'s own §0b standard
(*"one program against its guard"*). **That trades one refusal ground for
another**, and per RECAP #4 the manager should probe it before scheduling
anything — my measurements do not settle it.

---

## Problems

- **ASan silently no-ops behind this box's `LD_PRELOAD`.** The first full round
  of detector runs returned *"ASan runtime does not come first in initial library
  list"* and `exit=1` with **no report**, which reads exactly like a clean run if
  you only check the exit code. `env -u LD_PRELOAD` fixes it. `harness/check.py`
  uses `-static-libasan`, so **the gate is not affected**; a hand-run probe is.
- `box_arena`'s 4096→8192 band jump (+64 `Ir`/node) is unexplained.
- `rcdll.rs`'s `stale_backlinks_seen` counter reads 0 — my `Weak` liveness
  heuristic is wrong. It is decoration; the evidence is `bwd=32127` and
  `victim_alive_after=false`, both of which are sound.

## Unsure / not done — explicitly

- **No `p28` artefact of any kind was written.** No rung, `spec.md`, `model.py`,
  `inputs/gen.py`, `NOTES.md`, `README.md`. **§4 not started, by instruction.**
- **§1 IS COMPLETELY UNTOUCHED. Verus was not run at all.** The `deallocate`
  question — does `wf` survive removing a key from the permission map, given
  `TASK_091`'s key-discipline conjunct — **is exactly as open as it was.** If the
  manager overrules this refusal, §1 is still the first thing to budget.
- No C rung, no clang column, no `-O0`, no wall clock, no `-O3`-vs-`-O2` sweep.
- The `Ir` numbers are **probe shape**, and I say so rather than controlling for
  it — there is no shipped kernel to take a signature from.
- The `+28.07` residual for "the ASKING" is an **extrapolation**, not a
  measurement; I did not build the control that would isolate it.
- I did not re-run `.temp/t91/`'s binaries (they are still there).
- I did not check whether a *C* rung could be written whose temporal bug the
  index arena reproduces — I concluded from `a3` that it cannot, which is an
  argument from a measurement, not a measurement.

## Memory updates owed (manager applies, after review)

1. ⚠ **`.memory/03-measurement.md`: `p28` is NOT "not exposed".** A probe missing
   an **operation** the bug class requires can invert the **sign** — a third
   mechanism beside `p46`'s lost range facts and `p26`'s length dependence.
2. `.memory/06-catalogue.md` `p28`: **REFUSED**, with §0.1–§0.4 above. The row's
   own bug-class *column* already says **"aliasing, ownership"**; the word
   **"temporal"** appears only in the status prose, added at `6798f3a`
   (`TASK_086`) from a **source read with nothing run** — the exact failure mode
   RECAP #4 names, third instance.
3. **Safe Rust has no owned intrusive DLL** (`E0382` + `E0499`), so any linked
   pattern's safe rung is an arena that never frees, or `p27`'s representation.
4. ⚠ **Hand-run ASan needs `env -u LD_PRELOAD` on this box.** Worth
   `.memory/00-environment.md` — it fails *silently to the exit code*.
5. The `index >= len` count of **14** includes **`p01`**, which models no bug.
