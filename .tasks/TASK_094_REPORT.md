# TASK_094 — batched probe of the nine unprobed rows: report and RANKED QUEUE

**Role: research engineer (selection probe).** Ran concurrently with
`TASK_093_REVIEW`. **UNREVIEWED.** Nothing written outside `.temp/t94/` and this
file. No `check.py`, no `measure.py`, no `--cargo`, no `git add`, no `.memory/`
edit, no write into `.temp/p29|p32|p34|p37|p39|p43probe|p44/` (all `ls`'d first;
`.temp/t94/` did not exist).

**All nine rows probed. Every ranked row carries at least one thing that was RUN.**
**PROTOCOL rule 2 running count: 264 → 270.**

**The headline:** of the nine, **one is a BUILD and eight are REFUSALS** — and
the one that survives is the row the manager's structural hypothesis predicted
would die with the rest.

---

## Declared conventions, IN ADVANCE (probe 3), written into `.temp/t94/NOTES.md` before any run

Marginal **whole-program** `Ir` per kernel call: `(Ir(N2) − Ir(N1)) / (N2 − N1)`,
callgrind's own program-total `I refs:`, `rustc -O -C codegen-units=1`, every
kernel `#[inline(never)]` (inline mode **isolated**), payload from `argv` at run
time, `N1=100 N2=200`, `n=4096`, `SEED=12345`. **Whole-program, not
kernel-exclusive**, deliberately (p13, p48).

**Probe 5 exposure, blanket:** every cost number below is **PROBE SHAPE**. There
is no shipped kernel for any of these nine rows, so `TASK_092`'s defect cannot
be controlled for. Each row states its own signature / input-band / omitted-
operation exposure; **the two I am least comfortable with are named in the rows
themselves** (p29's lookup kernel omits the free; p39's cost is measured on a
benign input band).

---

## ⚠⚠ INSTRUMENT DEFECT — #265, and it is probe 2's SECOND one

**PROBE 2's LINKED FORM HAS A FALSE-NEGATIVE MODE, SYMMETRIC TO THE OBJECT
FILE'S FALSE POSITIVE. `TASK_086` #238 fixed one end and opened the other.**

`.memory/06-catalogue.md` now says: *"LINK FIRST, OR READ `readelf -rW`"*, then
md5 the linked kernel bytes; a collision means one rung. Measured on three
kernels that **are provably the same program** — `a[i] * b[i]` at `-O` with
debug-assertions off **is** `a[i].wrapping_mul(b[i])` by Rust's own definition,
and `unchecked_mul` compiles to the same `imul`:

```
kmd5.py cost   (LINKED binary, the prescribed form)
k44_plain     size=270 md5=170cc7c2ca8c91d045b4430041f72123
k44_unchecked size=270 md5=5b06d19b91e54ebca94fbff55ccb6e83   <- "different rung"
k44_wrapping  size=270 md5=e14bf3deca93f05d6d77bce3d80a0dc7   <- "different rung"
```

`diff` of the raw disassembly — **the complete list of differing lines** — is 7
self-relative jump targets (each printing its own kernel's name), one
`lea 0x…(%rip)` to a panic-location string and one `call *0x…(%rip)`. 67
instructions each, identical mnemonic multiset.

**In a linked binary every kernel sits at its own address, so every `jXX`
displacement and every `%rip`-relative reference differs BY CONSTRUCTION. Any
kernel containing a branch or a global reference CANNOT collide, and probe 2
passes vacuously.**

✅ **p45's kill still stands, and for the reason `TASK_086` already gave**: its
`k_plain`/`k_unchecked` are leaf arithmetic folds with **no call, no global and
no branch**, and its md5s were of the **object file**, where per-function
sections start at address 0. **p45 is the only shape probe 2's md5 can catch.**

**The repair is in `.temp/t94/knorm.py`** — normalise away the address column,
self-relative targets, `%rip` displacements and objdump's `#` comments, then
compare the *text*:

```
k44_plain     insns=67 mnemonic-multiset=f815d5d3b2f4 normalised-text=fed7c19bd69d
k44_wrapping  insns=67 mnemonic-multiset=f815d5d3b2f4 normalised-text=fed7c19bd69d
k44_unchecked insns=67 mnemonic-multiset=f815d5d3b2f4 normalised-text=fed7c19bd69d
  k44_plain == k44_wrapping == k44_unchecked   <-- ONE RUNG
```

✅ **Independently corroborated by probe 3**: under the fixed driver all three
read **`12849.00` marginal Ir/call, identical to the unit.**

---

# THE RANKED QUEUE

### 1. `p29` — BST insert/lookup — **BUILD, and it is the ONLY one of the nine**

⚠⚠ **THE MANAGER'S LEAST-SURE CALL #1 IS CONTRADICTED (#268). `TASK_093`'s
structural finding does NOT generalise to the family.** p29 answers **(a) YES**
and **(b) YES** — the configuration the task file calls *"the most valuable
thing left in this catalogue"*.

- **(a) does the safe representation FREE? YES, MEASURED.** `struct5.rs`, a
  counting `GlobalAlloc`, kernels under `#![forbid(unsafe_code)]` (the whole
  crate compiles under the forbid with the allocator `cfg`'d out):

  ```
  p29 build+drop      allocs=  2001 frees=  2000 live_bytes_delta=+32  depth=25
  p29 remove_leaf x1  ... removed=true frees_during_remove=1 bytes_released=24
  ```

  2000 `Box<Node>` in, 2000 out. `remove_leaf` releases **one block of exactly
  24 bytes** = `sizeof(Node)` (4+4+8+8). Against p28's arena, *"heap blocks
  released by unlink = 0"*. (The constant `+1 alloc / 0 free` skew in every band
  is the `format!` String the band returns.)

- **(b) is the mechanism p27's? NO — `E0502`, at COMPILE TIME.**
  `p29_borrow.rs` is `detect.c`'s `p29uaf` transcribed as literally as safe Rust
  allows:

  ```
  error[E0502]: cannot borrow `*t` as mutable because it is also borrowed as immutable
  50 |     let saved = t.find(10).unwrap();   -- immutable borrow occurs here
  52 |     t.remove_leaf(10);                 ^^ mutable borrow occurs here
  53 |     let after = saved.val;             --------- immutable borrow later used here
  ```

  p27's mechanism is a **runtime** one — the safe rung RUNS and *"the ASKING
  goes missing"*. **p29's safe rung does not compile at all.** Same bug class,
  a different boundary — **p08's kind**, which probe 1 explicitly admits.

- **Probe 1 — the boundary, NAMED:** **compile time**, R1/R4 against R2/R3. Not
  R3-vs-R4.
- **Probe 2 (linked + normalised):** `k29_safe_lookup` 92 B `807bd209…` 31 insns
  vs `k29_raw_lookup` 90 B `1b084927…` 32 insns, normalised-text **distinct**.
  Checksums agree: `1991537573` both.
- **Probe 3 — a REAL ZERO with a mechanism, axis declared in advance:**
  `438479.00` vs `438480.00` marginal Ir/call over 4096 lookups =
  **−0.00024 `Ir`/lookup.** Mechanism: **a tree walk has no index, so there is
  no bounds check to remove**, and `Option<Box<T>>`'s niche **is** the null
  pointer — `while let Some(n)` and `while !cur.is_null()` are the same
  `test/je`. **The axis that carries the row is the behaviour matrix and the
  compile-time expressiveness, NOT cost.** Say so in `spec.md` §0 before
  building, or this becomes p45's *"safety is free"*.
- **Probe 4 / the real rule:** the R5 below contains **no `unsafe` token at
  all** — `_scan_unsafe_sites` is trivially satisfied, as with p28. **Not p15's
  obstacle.**
- ✅ **R5, RUN: `4 verified, 0 errors`** (`v29_bst.rs`), **TCB 0** —
  `grep -c 'assume\|external_body\|admit\|assume_specification'` = **0**.
  `enum Tree { Leaf, Node(Box<Tree>, u32, Box<Tree>) }`, `spec fn keys() ->
  Set<u32>`, `spec fn bst()`, and `contains` with the **full functional**
  postcondition `res == self.keys().contains(key)` under `requires self.bst()`.
  Six proof lines: two `=~=` extensionality hints, two `!keys().contains` facts
  unfolded from `bst()`. ⚠ **This contradicts the catalogue twice** (#269): p29
  is rated *"hard"* with nothing run, and Family E's blanket *"Expect p28/p30 to
  defeat R5 within budget"* is now contradicted for a **third** row.
- **Harm, RUN, C rung** (`detect.sh`, `env -u LD_PRELOAD`, `grep` not `head`):
  `p29uaf` at `gcc -O2` → **exit 0, `before=100 after=5`, silent wrong answer**;
  ASan on **gcc and clang** → `heap-use-after-free`, **the same report the
  `p27ctl` control prints**.
- **Bug class:** use-after-free = **temporal**; shares with **p27**, and it
  would be the tree's second.
- ⚠ **Kill risks, three, and I did not close any of them:**
  1. **The bug class IS p27's** — same ASan line, verified side by side. What is
     new is the *rejection mechanism* (compile-time vs runtime), not the class.
     §0 must carry that distinction or the row is p27 with branches.
  2. **The cost kernel omits the free** — my `k29_*_lookup` pair does not
     `remove`, which is `TASK_091`'s p28 defect exactly. The `remove` cost was
     **not measured** and it is where the temporal class lives.
  3. **The proved `contains` is not the proved `remove`.** `insert` and
     `remove` (especially the two-child case, which needs the in-order
     successor) were **not attempted**, and a `remove` proof must re-establish
     `bst()` and relate `keys()` across the mutation. That is the real budget.

---

### 2. `p43` — CRC over an untrusted length — **REFUSE, and the catalogue's own claim is CONFIRMED with a measurement**

The catalogue says *"p43 is p16's shape"*. It is, exactly, and the mechanism is
p20's.

| kernel | marginal `Ir`/call, n=4096 |
|---|---:|
| `k43_naive` (indexed, per-element check) | **26664.00** |
| `k43_unchecked` (indexed, `get_unchecked`) | **26661.00** |
| `k43_tuned` (one hoisted slice, iterator) | **23593.00** |

- **naive − unchecked = `+3.00 Ir`/call = `+0.00073 Ir`/byte.** Flat, and
  falling with n.
- ⚠ **tuned − unchecked = `−3068.00` = `−0.749 Ir`/byte: the SAFE TUNED RUNG
  BEATS THE UNSAFE ONE.** p41's finding, second instance.
- **Mechanism, from `objdump`, and it is not "it vanished":** the entire check
  is **hoisted to the top of `k43_naive`** —
  `lea -0x1(%rdx),%rax ; cmp %rax,%rsi ; jbe <panic>` (i.e. `len−1` against
  `buf.len()`, **once**) — and the loop body is **2× unrolled with no check in
  it at all**. **A length-vs-buffer check is O(1) and does not scale**, which is
  p20's `+10.00` flat and p16's published *"R3 is still 0/byte"*.
- **Probe 2 passes** (149 / 203 / 119 B, three distinct normalised texts), and
  probe 1 has a boundary. **The row dies on duplication, not on the ladder
  test** — p41's death.
- **Exposure (probe 5):** probe shape; `len` arrives through `black_box`, which
  is what a header-derived length looks like — a shipped kernel would be the
  same or cheaper. Kernel omits no operation. One input band.
- ⚠ **What survives, and it is small:** p43 is the cheapest row in the catalogue
  to build (Verus difficulty *"easy"*, no allocation, no temporal class), so if
  the project ever wants an explicit **replication** of a published finding
  rather than a new one, this is the row. **The catalogue does not currently
  price replication, so I am refusing it.**

---

### 3. `p44` — fixed-point arithmetic — **REFUSE, and it is `p45`'s verdict reproduced on a second row**

**The manager's instruction to "ask p45's question FIRST" was right and it took
one compile.**

- **Contract A, *"caller guarantees no overflow"* — THE LADDER IS ONE RUNG.**
  `k44_plain`, `k44_wrapping` and `k44_unchecked` are **normalised-identical**
  (67 insns, one mnemonic multiset, one normalised text) and measure
  **`12849.00 / 12849.00 / 12849.00`** marginal `Ir`/call — **identical to the
  unit**. `unchecked_mul` deletes nothing: all three keep the same two index
  bounds checks and the same `imul`.
- **Contract B, *"detect overflow"* — THERE IS NO ADMISSIBLE R4.**
  `k44_checked` **40991.00**, `k44_widen` **39473.00**, `k44_widen_checked`
  **53279.00** — and `unchecked_mul` **cannot implement the contract**, so the
  only unsafe rung available would price a *bounds* check, i.e. p01's axis.
  **p45's finding 2, verbatim.**
- ⚠ **And the idiomatic spelling removes the bug class entirely.** Q16.16 is
  written `((a as i64) * (b as i64)) >> 16`, which **cannot overflow**. It costs
  `+26624.00 Ir`/call (**+207%**) over the wrapping `i32` form at n=4096 — real
  money, but it means the row's bug is **unreachable in the natural spelling**,
  which is **p41's other finding**.
- ⚠ **p44 is the row that exposed #265** — probe 2's linked md5 called it three
  rungs.

---

### 4. `p33` — object pool / use-after-recycle **and** `p32` — free-list allocator — **REFUSE. THEY ARE ONE ROW, MEASURED, AND IT IS `p04`'s.**

⚠ **The manager's least-sure call #2 is HALF refuted (#270-adjacent).** The
*detector* prediction is **exactly right** — nothing fires anywhere. The *class*
prediction is **wrong**: it is not a class the tree lacks.

**The same observable, reached two ways** (`struct5.rs`, safe Rust,
`#![forbid(unsafe_code)]`):

```
p32 DOUBLE FREE        walk=33 cycle=true x=0 y=1 z=0 aliased=true slot[z]=1111
p33 USE AFTER RECYCLE  h=0 h2=0 same_slot=true owner7_read_before=7000
                       owner7_read_after=9000 (owner9 wrote 9000) checked=None
```

Two logical objects on one slot. `checked=None` is the generation counter — the
fix — firing.

**Every detector, both compilers, C rung** (`detect.sh`):

```
PLAIN  gcc -O2      p32df    exit=0  aliased=1 slot[z]=1111
PLAIN  gcc -O2      p33uar   exit=0  before=7000 after=9000
ASAN+UBSAN gcc      p32df    exit=0  (no detector line)
ASAN+UBSAN gcc      p33uar   exit=0  (no detector line)
ASAN+UBSAN clang    p32df    exit=0  (no detector line)
ASAN+UBSAN clang    p33uar   exit=0  (no detector line)
ASAN+UBSAN gcc      p27ctl   exit=1  heap-use-after-free   <- THE CONTROL FIRES
```

Pinned **Miri: exit 0, clean** on both safe-Rust cases.

- ⚠⚠ **PROBE 1 KILLS THEM: THERE IS NO RUNG BOUNDARY ANYWHERE.** The bug
  compiles and produces the identical wrong answer at **C, safe naive, safe
  tuned and unsafe** — measured on both sides. The only place an obligation
  could live is R5, and the `identity` pin forces `R4 ≡ R5` as machine code, so
  a boundary there is not admissible. **That is `p31`'s death, the ladder test's
  one fatal condition.**
- **The class is `p04`'s** — its catalogue column reads *"a wrap that stays IN
  BOUNDS … every index still `< CAP`, no OOB access, and both guards are
  invisible to a memory-safety proof."* **The harm framing is `p48`'s** — *"in
  bounds, live, owned"* — **and `p48` is REFUSED.**
- ⚠⚠ **AND THE TASK FILE'S (a) TEST IS CATEGORY-WRONG FOR THESE TWO ROWS
  (#266).** *"Count released heap blocks"* — `detect.c`'s **C** free-list
  allocator calls `free()` **exactly once, at teardown**, the same as the safe
  Rust arena. **The test reads 0 on BOTH SIDES.** It is not measuring the safe
  rung's weakness; it is measuring what an allocator *is*. For `p29` the test
  discriminated perfectly (2000/2000 against p28's 0); for `p32`/`p33` it cannot
  fire. **The (a) test is sound for CONTAINERS and vacuous for ALLOCATORS.**
- ✅ **`TASK_093`'s `a2` result INDEPENDENTLY REPRODUCED** on a different kernel
  family — its DLL index arena, mine a free-list allocator: double free in safe
  Rust compiles, becomes aliasing, Miri clean, exit 0.

---

### 5. `p34` — reference counting — **REFUSE, with one half that is real and belongs to `p42`**

- **Premature-free half:** `TASK_093`'s result reproduced independently —
  `p34 Weak breaks cycle: upgrade_before_drop=true upgrade_after_drop=false`.
  That is **p27's published sentence with `upgrade()` in place of
  `live[h] == 1`**.
- ✅ **Leak half, MEASURED and it is not nothing:**

  ```
  p34 Rc CYCLE (leak)  allocs=3 frees=0 live_bytes_delta=+324 strong_a=2 strong_b=2
  ```

  **Three allocations, zero frees, 324 bytes leaked — in safe Rust, under
  `#![forbid(unsafe_code)]`, with both handles dropped.** A `Drop`-based ladder
  cannot claim it away.
- ⚠ **But probe 1 has no boundary for the leak either:** C leaks on a missed
  decref, safe Rust leaks on a cycle, unsafe Rust leaks. **Every rung leaks**,
  which is `p31`'s condition again. And the row that owns *"leak"* in the
  catalogue is **`p42` (`goto cleanup` — leak on error path), still `planned`**.
- **Recommendation: fold the measurement into `p42`'s triage, do not build
  `p34`.** `p42` at least has a boundary candidate (RAII/`Drop` against a
  hand-written cleanup path) that `p34` does not.

---

### 6. `p30` — chained hash table — **REFUSE, and the catalogue's own description is HALF WRONG (#267)**

The status column says *"combines p22 + p27"*. **The `p22` half is structurally
absent.**

- `p22` is non-termination from probing a **full open-addressed** table. **A
  chained table cannot fill.** Measured:
  `p30 flood  maxchain=4096 of 4096 keys in 1024 buckets` — every key in one
  bucket, and it **terminates**. The harm is an O(n) lookup: a complexity
  attack, not a hang.
- The `p27` half is present and is p27's: `(a)` YES trivially
  (`allocs=921 frees=920`), and `remove`-then-`get` returns `None` cleanly.
- The only spelling that *would* hang is an **intrusive** chain with a node
  linked into two buckets — and `TASK_093` measured that safe Rust cannot
  express an owned intrusive list (`E0382` + `E0499`). **So `p30`'s
  non-termination half is `p28`'s refusal, not `p22`'s finding.** The cycle
  itself is reproduced here in the index spelling
  (`p32 SELF free  walk=33 cycle_or_overlong=true`).
- **So `p30` is p27 + p28's-refusal + a terminating complexity attack.** Three
  rows deep, none of them new. ⚠ **The manager's least-sure call #3 is upheld
  for `p30` — but for a different reason than the catalogue gives**, and the
  catalogue's own bug-class column should be corrected rather than cited.

---

### 7. `p39` — bitfield pack/unpack — **REFUSE; it is `p09`'s sentence with the mask on the other side**

- ⚠ **My first kernel was WRONG and my own checksum control caught it**: the
  off-by-one sat on the TOP field, which occupies the top 12 bits of a 32-bit
  word, so `mask(13)` was a **no-op** and all three kernels printed `4181210`.
  Moved to the `id` field (9 bits at offset 5, indexing a 512-entry op table).
- **The bug fires**, safe Rust, adversarial input:
  `panicked at cost.rs:193: index out of bounds: the len is 512 but the index is 585`.
- ⚠⚠ **THE BUG COSTS EXACTLY ZERO.** `k39_id_masked` and `k39_id_offbyone` are
  30 instructions each and **the complete normalised diff is one line**:

  ```
  10c10
  < and    $0x1ff,%r8d
  ---
  > and    $0x3ff,%r8d
  ```

  Marginal `Ir`: **36895.00 vs 36895.00.** **That is `p09`'s published sentence
  — *"one character between a bug everything catches and one nothing does"* —
  with a wire-format mask in place of `q & 31`.**
- **The CHECK costs `+4.25 Ir`/word** (`36895.00` vs `19496.00`), **and the
  mechanism says it is not all check** (`objdump`): the masked loop is
  **rolled**, 9 insns/word, of which the check is exactly `cmp %r8,%rcx /
  jbe <panic>` = **2.00**; the unchecked loop is **4× unrolled**, ≈4.76
  insns/word. So ≈2.00 is the compare pair and ≈2.25 is **the unroll the panic
  exit edge forecloses**. ⚠ **That is `p35`'s and `p28`'s mechanism, third
  instance — worth `.memory/` on its own, independent of this row.**
- **Bug class:** `index >= len`, which would be the **13th**. The shift-count
  sub-case is **`p18`'s** (*unbounded shift*), already built.
- **Exposure (probe 5):** cost taken on a **BENIGN** input band (bit 14 cleared
  so all three kernels agree) — stated, not hidden. Signature: the table length
  is an ABI value here; a shipped kernel with a compile-time-known 512 could
  delete the check entirely, which is **p24's shipped-shape collapse**.

---

### 8. `p37` — callback with `void*` userdata — **REFUSE. Strictly worse than `p35`, and blocked by Verus itself, not by a gate policy.**

- ✅ **`p36`'s claim REPRODUCED verbatim** at the pin (`v37_callback.rs`):

  ```
  error: The verifier does not yet support the following Rust feature: function pointer types
    --> v37_callback.rs:17:1     <- on the STRUCT FIELD DECLARATION
    --> v37_callback.rs:22:5     <- and on the call
  ```

- **Probe 4, pinned vstd:** `c_void` **0 hits**, `dyn Any` **0 hits**, `::any::`
  **0 hits**.
- **The row collapses on the substitution.** With fn pointers inadmissible, R5
  must use `dyn Trait` (p36's `[&'static dyn Op; NOPS]`) — **and then the
  userdata rides inside the trait object, TYPED, so the erasure that IS the bug
  disappears.** That is `p36`'s finding (*"C's own dispatch mechanism is not an
  admissible rung"*) composed with `p35`'s (*"safe Rust's `enum` makes the
  mismatch unrepresentable"*).
- ⚠ **The distinction from `p35` matters for scheduling:** `p35` is blocked by
  `check.py::_scan_unsafe_sites`, **a gate policy this project controls**.
  `p37` is blocked by **Verus at the pin**, which is a pin bump — and
  `CLAUDE.md` forbids bumping it without a crates.io check. **Fixing
  `_scan_unsafe_sites` unblocks p15 and p35 and does NOT unblock p37.**

---

## The six contradictions (264 → 270)

- **#265 — probe 2's LINKED form false-negatives**, symmetric to `TASK_086`
  #238's false positive. Any kernel with a branch cannot collide. Measured on
  three kernels that are the same program; repaired by `.temp/t94/knorm.py`.
  **p45's kill is unaffected** (leaf arithmetic, object file).
- **#266 — the task file's (a) test is CATEGORY-WRONG for allocator rows.**
  A C free-list allocator calls `free()` once at teardown too, so *"count
  released heap blocks"* reads 0 on **both** sides. Sound for containers
  (`p29`: 2000/2000 vs `p28`: 0), vacuous for `p32`/`p33`.
- **#267 — `p30` is NOT "p22 + p27".** A chained table cannot fill; the flood
  terminates (`maxchain=4096 of 4096`). The catalogue's own bug-class column has
  now been wrong about a row's class a **fifth** time.
- **#268 — `TASK_093`'s structural finding does NOT generalise to the family.**
  `p29` answers **(a) YES** (2000 allocs / 2000 frees; 24 bytes released per
  `remove_leaf`) **and (b) YES** (`E0502` at compile time, not p27's runtime
  ask). This is the manager's own least-sure call, and it was the right one to
  name.
- **#269 — `p29`'s R5 CLOSES, `4 verified, 0 errors`, TCB 0, with a full
  functional postcondition.** The catalogue rates it *"hard"* with nothing run,
  and Family E's *"Expect p28/p30 to defeat R5 within budget"* is contradicted
  for a third row.
- **#270 — the manager's least-sure call #2 is HALF right.** `p33`'s detector
  prediction is **exactly** right (nothing fires, anywhere, on either compiler,
  plus Miri). Its *class* prediction is wrong: the class is **`p04`'s** and the
  harm framing is **`p48`'s**, which is refused.

## Clean negatives — attacks that did NOT land, so nobody re-runs them

- **I tried to kill `p29` on the Verus side and failed.** A recursive
  `Box<Tree>` datatype is admissible at the pin; `keys()`, `bst()` and
  structural recursion all verify.
- **I tried to kill `p29` on probe 2 and failed** — 92 B / 90 B, distinct
  normalised text, checksums agree.
- **I tried to make `p43`'s zero into `p45`'s artefact and failed** — the three
  kernels are 55 / 45 / 64 insns with three distinct normalised texts, and the
  hoisted check is visible in the disassembly. It is a real zero with a
  mechanism.
- **`p27ctl` control fires in every sanitiser configuration** in which
  `p32df`/`p33uar` are silent, so the silence is the bug's, not the harness's.
- **`env -u LD_PRELOAD` was used for every hand-run sanitiser invocation and
  every log was `grep`'d, never `head`'d** (TASK_086's four half-shown rows).

## One error I found and corrected in myself before it reached a headline

**My probe-3 driver put the `match kernel.as_str()` INSIDE the measured loop**,
so per-iteration string-dispatch cost varied with the kernel **name**: three
kernels that are the same program read `12871 / 12857 / 12862`. **A 14 `Ir`/call
noise floor under every number, and it is exactly the size of the `p44` signal.**
Fixed by hoisting dispatch into a `Box<dyn FnMut>` chosen before the loop; the
same three then read **`12849.00` three times**. Both driver versions and both
logs are kept (`cost_n4096.log`, `cost_v2_n4096.log`).

## Problems

- **`p39`'s first kernel measured nothing** (off-by-one on the top field of a
  32-bit word is a no-op). Caught by the cross-rung checksum control, not by
  reading.
- **`p29`'s sorted-key depth sweep hit a 60 s timeout at n=200000** — that is my
  **O(n²) iterative builder**, not a stack overflow. n=100000 built a
  depth-100000 chain and dropped cleanly. **Whether recursive `Drop` overflows
  the stack at larger depth is UNANSWERED.**
- **Verus's postcondition error location is misleading on a `match` tail
  expression**: it pointed at the **first arm** (`Tree::Leaf`) while the real
  obligations were in **both `Node` arms**. Cost 3 runs; `v29_min.rs` isolates
  the Leaf case and verifies `4 verified, 0 errors`, which is the proof that the
  reported location was wrong.

## Unsure / not done — explicitly

- **No pattern artefact of any kind was written.** No rung, `spec.md`,
  `model.py`, `inputs/gen.py`, `NOTES.md`, `README.md`, for any row.
- **`p29`'s cost kernel OMITS THE FREE.** The lookup pair does not `remove`, so
  the temporal class is absent from the number. **This is `TASK_091`'s p28
  defect and I am naming it rather than hiding it.** The `remove` cost is
  unmeasured and could invert the sign, as it did for p28.
- **`p29`'s `insert` and `remove` were NOT proved** — only `contains`. The
  two-child `remove` (in-order successor) is the real Verus budget and it was
  not attempted.
- **`p29`'s C rung is one shape** (leaf removal). I did not test the two-child
  removal bug, the double-free-of-a-shared-subtree bug, or the rotation bug.
- **No clang column for any `Ir` number, no `-O0`, no `-O3` sweep, no wall
  clock.** Everything is `rustc -O`, one opt level.
- **`p34`'s cost side was not measured** — `TASK_093` has it (`rc 476` vs
  `rawptr 355`) and it is **unreviewed**; I did not re-derive it.
- **`p30`'s flood used a trivially-constructed collision set** (keys with
  `hash & 1023 == 0`), not a realistic seed-independent flooding attack. The
  conclusion — a chained table terminates — does not depend on that.
- **I did not run `p39`'s C harm** through the detector matrix; the safe-Rust
  panic and the disassembly are what the refusal rests on.
- **Nothing here has been through `check.py`**, by instruction. Every number is
  from throwaway kernels.
- **`.temp/t94/build.sh` rebuilds every deleted artefact** (`cost`, `struct5`,
  `forbid_check.rlib`, the detector binaries) and re-prints every table. 152 KB
  of text remains; all binaries deleted.

## Memory updates owed (manager applies, after review)

1. ⚠⚠ **`.memory/06-catalogue.md` probe 2: the LINKED md5 form false-NEGATIVES
   on any kernel containing a branch or a global reference (#265).** Both ends
   of probe 2 are now known broken in opposite directions. **The form that
   works is normalised-disassembly text comparison** —
   `.temp/t94/knorm.py`. `p45`'s kill is unaffected and the reason is worth
   keeping: it is the only shape the md5 can catch.
2. **`.memory/06-catalogue.md`: `p44` REFUSED** — one rung under contract A
   (`12849.00` ×3, normalised-identical), no admissible R4 under contract B,
   and the idiomatic widening spelling makes the bug class unreachable. **p45's
   verdict, second instance.**
3. **`.memory/06-catalogue.md`: `p32` and `p33` REFUSED as ONE ROW**, on
   **probe 1** — the bug compiles identically at C, safe naive, safe tuned and
   unsafe; no boundary anywhere; `p31`'s death. Class is `p04`'s, harm framing
   is `p48`'s (refused). Detector matrix and Miri attached.
4. **`.memory/06-catalogue.md`: `p30`'s bug-class column is wrong** — *"combines
   p22 + p27"* is half false; a chained table cannot fill, so `p22`'s
   non-termination is structurally absent.
5. **`.memory/06-catalogue.md`: `p34` REFUSED**; fold the measured `Rc`-cycle
   leak (3 allocs, 0 frees, 324 bytes, `forbid(unsafe_code)`) into **`p42`'s**
   triage.
6. **`.memory/06-catalogue.md`: `p37` REFUSED**, and it is **not** unblocked by
   fixing `_scan_unsafe_sites`. `p36`'s *"Verus cannot type fn pointer types"*
   re-verified at the pin.
7. **`.memory/06-catalogue.md`: `p39` and `p43` REFUSED** as `p09`'s and
   `p16`/`p20`'s findings respectively, each with the measurement.
8. **`.memory/06-catalogue.md` `p29`: BUILD**, with (a)/(b) both YES, `R5 4/0
   TCB 0`, a `0.00` cost axis that must be declared in advance, and the three
   named kill risks.
9. ⚠ **The structural-question (a) test is sound for CONTAINERS and vacuous for
   ALLOCATORS (#266)** — worth `.memory/02-bench-rules.md` beside the threat
   model.
10. **`.memory/03-measurement.md`: the "check tax is partly a foreclosed unroll"
    decomposition now has a THIRD instance** (`p39`: 2.00 of 4.25 is
    `cmp/jbe`, ≈2.25 is the unroll the panic exit edge blocks), after `p35` and
    `p28`. It is a rule, not a coincidence.
11. **`../LearnVeri/PITFALLS.md`: Verus reports a `match` tail expression's
    postcondition failure at the FIRST arm**, regardless of which arm is
    unproved. Minimise by isolating one arm into its own `fn`.
12. ✅ **`.memory/00-environment.md`: `env -u LD_PRELOAD` for hand-run ASan is
    confirmed a third time** — without it every case in the matrix reads exit 1
    with zero report lines.
