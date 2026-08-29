# TASK_133 — re-adjudicating the five unreviewed TEMPORAL refusals against the AMENDED bar

**Role: research reviewer.** Reviewing the *manager's* adjudications, not an
engineer's build.

Everything below was **run**. Evidence in `.temp/t133/` (220 K, sources + logs,
zero binaries); `bash .temp/t133/run.sh` rebuilds and re-runs every number here.
No `harness/check.py`, no `harness/measure.py`, no `git add`/`commit`, nothing
written under `.memory/`, `RECAP.md` or `results/SYNTHESIS.md`.

---

## VERDICTS, in one table

| row | verdict | the reason that decides it |
|---|---|---|
| **`p29`** | ⚠⚠ **RE-OPENED — ADMISSIBLE ON LIMB 4** | but **NOT on the manager's reason**, which is struck by the manager's own `.memory/`. It re-opens on limb 4 clause 3, measured today: **on the inputs where C aborts under ASan, both independent safe spellings return a silently wrong answer; on the other inputs the safe rung reproduces buggy C bit-for-bit.** |
| **`p30`** | **REFUSAL STANDS, REASON CORRECTED** | limb 1 stands. The surviving limb (*"what remains is p27's half alone"*) was an argument; it is now a **measurement** — a chained table's UAF fires on an ordinary chain walk with **no saved pointer**, which is p27's retained-pointer sentence with the pointer moved from the table into the chain. |
| **`p32`/`p33`** | **REFUSAL STANDS, REASON CORRECTED** — and the corrected reason is much stronger | ⚠ **this is the manager's least-certain call and the answer is neither of the two offered.** The silence is **not** "temporal" and **not** "logical": it is a function of **where the storage lives**, and both storage choices are already shipped **bit-identically** — safe slab `==` buggy C, safe `Option<Box>` `==` hardened C, on every input, with no hardening line written. |
| **`p34`** | **REFUSAL STANDS, REASON CORRECTED** | ⚠⚠ **both the manager's stated reason AND `p34`'s own headline fall to one measurement.** `Weak` is *not* an alternative spelling (it changes the published checksum), **and** C's own refcount rung leaks identically while Rust's arena rung is leak-free at the same checksum. **There is no inversion.** |

**One row re-opened, as instructed.** Ranking and why the loser loses: §6.

---

## 0 — ⚠⚠ THE MANAGER'S STATED BASIS FOR `p29` IS CONTRADICTED BY `.memory/`

The task file says:

> **`p29`** — **outcome 5, the only *good* outcome of the four-outcome law.**

`.memory/01-ladder.md`, the authoritative layer, says the opposite, in a
strikethrough that reads as settled:

> ⚠⚠ **p29 — REFUSED at TASK_095, and ~~the fifth outcome~~ IS STRUCK.** … **a
> shipped p29 lands in outcome 2 or outcome 3 like everything else.**

and `.memory/06-catalogue.md`'s `p29` cell agrees: *"So a shipped p29 is
**outcome 2** … or **outcome 3**."*

⚠ **This is PROTOCOL rule 13's shape** — the header of the manager's own pitch
asserts what the body of the authoritative layer denies — and it matters more
than usual, because *"outcome 5"* is the entire stated reason to prefer `p29`.
**I re-opened `p29` anyway, on a different and measured reason.** If the
manager lands this re-opening while still believing "outcome 5", the row will be
built to prove something that was struck three tasks ago. **`p31`'s failure mode,
in the re-opening direction rather than the refusing one.**

---

## 1 — THE LOAD-BEARING SENTENCE, RE-DERIVED. It is stale, it is a COMPRESSION, and its CONCLUSION IS FALSE.

`.memory/06-catalogue.md`'s `p29` cell:

> ⚠ **And 22 of 24 patterns take their payload from a file blob, so the shipped
> kernel cannot host a pointer** — p27's own hashed `why` says exactly that.

Three separate claims. **All three fail.** (`.temp/t133/a_census/census.py`,
`logs/a1-census.log`.)

### 1a — the count is stale AND it merges two different counts

`TASK_095_REPORT.md` §E3, the source it compresses, says something else:

> **22 of 24 patterns DECLARE `kernel(buf: &[u8], off: usize, len: usize) -> u64`;
> all 24 take their payload from a file blob.**

Two counts. The catalogue kept the **weaker numerator** and attached it to the
**stronger predicate**, which turns a universal into a 92 % and invites the
reader to hunt for the two patterns that escape. **There are none.** Measured
today:

```
patterns on disk                                   : 26
declare EXACTLY  kernel(buf: &[u8], off, len) -> u64 : 23/26
   the three that do not: p01 (&[u64]), p42 (&[u64]), p02 (extra &mut [u8] out-param)
take their payload from a FILE BLOB                : 26/26     <- UNIVERSAL
   the ones that do not: []
```

### 1b — the CONCLUSION does not follow, and two shipped patterns refute it

```
KERNELS THAT HOST A POINTER / OWNING ALLOCATION INSIDE THE KERNEL:
  p27: c/kernel.c [cptrarr, alloc, free]   unsafe.rs/verus.rs [rawptr, alloc, free]
                                           safe_naive.rs/safe_tuned.rs [Box]
  p42: c/kernel.c [alloc, free]            unsafe.rs/verus.rs [rawptr, alloc, free]
  p36: c/kernel.c [rawptr]                 (a `static uint64_t (*const TABLE[N])(uint64_t)`)
```

`patterns/p27-handle-table/unsafe.rs:156` is literally
`let mut tab: [*mut u8; TABCAP] = [core::ptr::null_mut(); TABCAP];` — **32 raw
pointers hosted inside a kernel whose payload is a file blob.**
(`p46` also matched my regex; that one is a **false positive**, `(unsigned
__int128)ai * bl[j]`, and is disclosed here rather than counted.)

### 1c — what `p27`'s hashed `why` actually says, and it is a DIFFERENT sentence

> *"THE HANDLE IS AN INTEGER AND THAT IS WHY NULLING IS NOT A DEFENCE: **the op
> stream comes out of a file and a file cannot name a pointer**, so the READ has
> an index and must consult something to learn whether the record is there."*

**"A file cannot name a pointer"** is about what the **op stream** can *say*.
**"The shipped kernel cannot host a pointer"** is about what the **kernel** can
*hold*. The compression swapped one for the other, and the swapped version is
the one that has been carrying three refusals.

⚠ **The correct sentence, and it should replace the cell's:**

> **A file cannot name a pointer — but it can name an OPERATION that saves one.**
> The kernel may hold any pointer it likes; what it may not do is *receive* one.

Every one of the five structures is expressible under that rule. §2 measures it.

---

## 2 — DELIVERABLE 2: EXPRESSIBILITY, MEASURED. All five fit. The boundary is one step further in.

Every probe below uses the **shipped C signature**
`uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)`,
the **shipped Rust signature** `fn kernel(buf: &[u8], off, len) -> u64`, and a
**driver loop identical across every probe** (`.temp/t133/b_express/drv.h`,
transcribed from `p27`'s). The blob is p27's: `u32 nops`, then 2-byte
`(opcode, operand)` ops. `gen.py` regenerates every input.

| row | structure | hosted in the pinned shape? | how the file reaches it |
|---|---|---|---|
| `p29` | BST, `malloc` per node, pointer-returning `find` | ✅ **yes — ASan `heap-use-after-free`, rc=1** | the file names an **op** (`FIND`) that saves the pointer |
| `p30` | chained hash table, `malloc` per entry | ✅ **yes — ASan `heap-use-after-free`, rc=1** | the **chain itself** retains the freed pointer; no saved pointer needed |
| `p32`/`p33` | slab + free list / per-object `malloc` | ✅ **yes, both spellings** | integer handle indexes the slab |
| `p34` | `Rc`/refcount graph, attacker-chosen edges | ✅ **yes — LSan 432 B / 2160 B; Miri 6 / 30 `memory leaked`** | operands pack `(src, dst)` node indices |

⚠ **`harness/dloop.py:361`'s arity check is NOT the boundary, and the citation is
still accurate today** (verified: line 361 is
`if keep[-1] >= len(args):`, the `call_args` arity raise). It fires when a
`call_args` **declaration** keeps a position the written call does not have, and
the check immediately after it forbids dropping anything that is not a bare
identifier. It constrains **declarations**, not kernel arity. `p27`'s `spec.md`
cites it correctly and narrowly (*"the alternative — passing the slab as an
argument"*); the catalogue's compression is what over-reads it.

**So the boundary is not the signature and not the driver.** It is that every
handle the **file** supplies is an integer, which decides *how the bug is
reached*, not *whether it exists*:

- **reached by a plain walk** — `p27` (`tab[h]` retains the pointer), `p30`
  (the chain retains it). Both measured firing with no saved pointer anywhere.
- **reached only through a prior op** — `p29` (`FIND` then `USE`). Measured
  firing too, so this is a *longer* route and not a closed one.
- **not a pointer bug at all** — `p32`/`p33` slab, `p34` index arena: the
  integer handle indexes storage that is never deallocated.

---

## 3 — `p29`: the measurements, and why it re-opens on a reason nobody has stated

### 3a — the C rung has the bug, in the pinned shape

`.temp/t133/b_express/k29_bst.c` — `nins` / `nfind` (the textbook
pointer-returning lookup) / `nrem` with the in-order-successor splice.
`gcc -O1 -g -fsanitize=address`, `env -u LD_PRELOAD`, counted with
`grep -c AddressSanitizer` (never `head`):

```
k29_bst      uafleaf : rc=1 ASan=2 heap-use-after-free
k29_bst_hard uafleaf : rc=0 ASan=0            checksum 8684676083620
k29_bst      noreuse : rc=0 ASan=0            checksum 8684676079139   <- negative control
ASAN POSITIVE CONTROL : rc=1 ASan=2 heap-use-after-free
```

### 3b — ⚠⚠ THE FINDING NOBODY HAS: ONE SAFETY LINE, TWO BUG CLASSES, AND THE **INPUT** SELECTS

Same binary, same source line `acc = acc*31 + saved->val`, five inputs that
differ **only in which key is removed** from the fixed tree `10/5/20/15/25`
(`logs/b29-degree-sweep.log`):

```
victim  children  rc  ASan                 kind      buggy checksum   hardened checksum
    10         2   0     0                    -       8684676078980       8684676083620
     5         0   1     2  heap-use-after-free      (aborted)            8684676083620
    20         2   0     0                    -       8684676081220       8684676083620
    15         0   1     2  heap-use-after-free      (aborted)            8684676083620
    25         0   1     2  heap-use-after-free      (aborted)            8684676083620
```

**Mechanism**: the in-order-successor splice **does not free the victim** when it
has two children — it **overwrites the victim in place** and frees the
*successor*. So `saved` still points into a live allocation whose *occupant has
changed*: a **use-after-RECYCLE**, in bounds, ASan-silent, caught only by the
checksum. The leaf case frees the node `saved` names: a **use-after-FREE**.
**Two bug classes out of one line, selected by attacker data.**

⚠ Nearest shipped thing is `p09` (*"one character between a bug everything
catches and one nothing does"*) — but that is **two SOURCES**. This is **one
source and two INPUTS**, and I found no shipped pattern with that shape.

### 3c — limb 4 clause 3, measured: the safe rung is silently wrong exactly where C is loud

Three safe spellings were searched, because *"searching one side is not
searching"*:

| safe spelling | result |
|---|---|
| `Option<Box<Node>>` + saved `&Node` | **does not compile**, `2 error[E0502]` |
| index arena (`Vec<Node>` + free list), `#![forbid(unsafe_code)]` | compiles, runs |
| `Option<Rc<RefCell<Node>>>` + saved `Rc`, `#![forbid(unsafe_code)]` | compiles, runs |

```
victim deg |               C buggy          C hardened |     safe idx-arena           safe Rc
    10   2 |        8684676078980       8684676083620 |     8684676078980     8684676078980
     5   0 |        ABORTED(ASan)       8684676083620 |     8684676076740     8684676076740
    20   2 |        8684676081220       8684676083620 |     8684676081220     8684676081220
    15   0 |        ABORTED(ASan)       8684676083620 |     8684676078980     8684676078980
    25   0 |        ABORTED(ASan)       8684676083620 |     8684676081220     8684676081220
```

✅ **The two structurally different safe spellings agree on all five inputs**, so
this is a property of safe Rust and not of one representation. And:

- on the **two-child** inputs the safe rung is **bit-identical to buggy C** —
  no boundary anywhere, `TASK_094`'s probe 1 reproduced on `p29`'s own program;
- on the **leaf** inputs, where C **aborts under ASan**, the safe rung returns a
  **wrong answer and no diagnostic** — Miri clean, `UB=0 leaked=0`, positive
  control fires (`UB=3`).

> ⚠⚠ **`p29`'s one-sentence result: safe Rust does not remove this bug, it
> removes the DETECTOR.** That is not `p27`'s sentence (*"the free and the
> invalidation are one operation … and the bug is the third — the ASKING — going
> missing"*), and it is not `p04`'s (*"stays in bounds, invisible to a
> memory-safety proof"* — `p04`'s C rung has no detector to lose). **It is the
> `outcome 4` inversion `p34` claims and, per §5, does not have.**

### 3d — the borrowck limb, re-controlled, and it still does not carry anything

`.memory/01-ladder.md`'s method rule, obeyed rather than cited
(`logs/b29-borrowck.log`):

```
r29_saferef     2 error[E0502]  cannot borrow `root` as mutable ...   <- the BST
r29_ctl_nods2   1 error[E0502]  cannot borrow `s` as mutable ...      <- struct S { v: u32 }
r29_ctl_nods    1 error[E0506]                                        <- direct-field variant
```

**`TASK_095` E1 reproduces at `TASK_133`.** The `E0502` is generic borrowck.
⚠ **So limb 4 clause 1 (*"a rung that cannot EXPRESS the program"*) is TRUE of
`p29` and must NOT be the reason it ships** — it is true of every Rust program
that holds a reference across a mutation. `p29` re-opens on **clause 3 only**.

### 3e — the R5 artefact: re-extracted, re-verified, and given a mutant it had not seen

```
extracted from .tasks/TASK_095_REPORT.md : 232 lines
sha256 90a338c7567936464786e439a3f4e8e5da1ac3919e0853efaefcc31288811487   <- MATCHES
./verus_run.py .temp/t133/verus/v29_bst.rs --crate-type=lib
                                          -> 9 verified, 0 errors
TCB grep (assume|external_body|external|assume_specification|admit) -> 0
M1  splice the VICTIM's key, not the successor's   -> 8 verified, 1 errors  assertion failed
M5  two-child branch returns the LEFT subtree and  -> 8 verified, 1 errors  assertion failed
    DROPS the right one   (NEW at TASK_133)
```

✅ **The manager's most expensive unshipped asset is real and it is intact in the
report file.** M5 is a mutant `TASK_095` did not run and it fails too.

---

## 4 — `p32`/`p33`: ⚠⚠ THE MANAGER'S LEAST-CERTAIN CALL. The answer is neither option offered.

The manager asked: *"if the silence is a **temporal** silence and `p04`'s is a
**logical** one, they are not duplicates and I am wrong."*

**Measured answer: the silence is neither. It is a function of WHERE THE STORAGE
LIVES, and both choices are already shipped.** `.temp/t133/c_dup/k33_pool.c` is
**one source** built four ways (`-DSPELLING={SLAB,MALLOC} × -DHARDEN={0,1}`);
`r33_pool.rs` is **one safe source** with two arms, `#![forbid(unsafe_code)]`.

```
                          double-free input          use-after-recycle input
C  SLAB   harden=0    ASan 0   28173833944553      ASan 0            962056
C  SLAB   harden=1    ASan 0   28173841632553      ASan 0           1202306
C  MALLOC harden=0    ASan 2  "attempting double-free"   ASan 2 "heap-use-after-free"
C  MALLOC harden=1    ASan 0   28173841632553      ASan 0           1202306
Rust SAFE slab        ------   28173833944553      ------            962056   <- == C BUGGY
Rust SAFE boxed       ------   28173841632553      ------           1202306   <- == C HARDENED
miri, all four safe runs : UB=0                    positive control : UB=3
```

- **safe slab `==` buggy C, bit for bit, on both bug shapes.** No boundary
  anywhere — `TASK_094`'s probe 1, independently reproduced, and now with the
  *hardened* arm as the reference so the equality means something.
- **safe `Vec<Option<Box<u32>>>` `==` hardened C, bit for bit, with NO hardening
  line written.** The `Option` discriminant *is* the liveness test — `p27`'s
  shipped sentence, reproduced on `p32`/`p33`'s own program.
- **The two C spellings' hardened arms are the same checksum**, so SLAB and
  MALLOC are the same program modulo storage location.

> ⚠⚠ **`p32`/`p33` has exactly two spellings and they are `p04` and `p27`. There
> is no third.** That is a strictly stronger kill than *"it is `p04`'s class"*,
> and it does not depend on the word "duplicate", which `TASK_120` showed covers
> four different relations.

✅ **`p27`'s own hashed `why` predicted this before `p32`/`p33` was ever probed**,
and the manager did not cite it:

> *"if the slab were one allocation and 'close' were a freelist push, the stale
> read would be IN BOUNDS OF A LIVE ALLOCATION — Miri would not flag it,
> `PointsTo` would license it, and **the bug would be LOGICAL**"*

⚠ **One discrepancy worth landing:** that hashed sentence says the class is
**`p17`'s**; `.memory/01-ladder.md` and the catalogue say **`p04`'s**. Both are
"logical, memory-safe" rows so the verdict is unaffected, but two authoritative
texts name different precedents for the same class.

**Control for `p04`'s side of the comparison**, built from `p04`'s own shipped
sources against the real driver (`logs/c1-p04-detect.log`), ASan **and** UBSan:

```
p04_bug/hard × {small, adversarial-overwrite, adversarial-wrap,
                adversarial-count, large}  :  ASan=0 UBSan=0 on all ten runs
the bug is visible ONLY as a checksum divergence, on adversarial-overwrite:
        bug 12736506159104   hardened 61209146786944
```

So `p04`'s detector vector and the pool-slab's detector vector are **the same
vector**: nothing fires, the checksum decides.

---

## 5 — `p34`: ⚠⚠ BOTH THE MANAGER'S REASON AND THE ROW'S OWN HEADLINE ARE REFUTED BY ONE MEASUREMENT

The catalogue's reason: *"the safe rung leaks ONLY in the `Rc`-both-ways
spelling, and `Weak` is equally safe, equally idiomatic and measured
LEAK-FREE."* That was measured on a **doubly linked list**, where `prev` is
statically the back edge. **A shipped kernel takes a flat blob, so the EDGE SET
COMES OUT OF THE FILE** and no edge is statically the back edge.

`.temp/t133/c_dup/{k34_graph.c,r34_graph.rs}`, one op stream, five rungs, the
`__lsan_default_options() -> "use_stacks=0"` hook `TASK_100` found:

```
rung                                  checksum (mixed.bin)          leaks?
C   manual refcount   (ARM=RC)      6435204519055678286      YES  LSan 2160 B, 2 leak records
C   arena             (ARM=ARENA)   6435204519055678286      no
Rust safe  Rc                       6435204519055678286      YES  miri 30 x "memory leaked"
Rust safe  Weak                      749491243298922113      no   <- DIFFERENT PROGRAM
Rust safe  index arena              6435204519055678286      no
LSAN POSITIVE CONTROL : fires, 4096 B      MIRI LEAK POSITIVE CONTROL : fires, 1 line
```

Two independent conclusions, and they point opposite ways:

1. ⚠ **The manager's reason is FALSE in the shipped shape.** `Weak` is not a
   respelling of the same rung — a `Weak` edge can be gone, `upgrade()` needs an
   answer for that, and the answer **changes the published checksum**. Under
   `.memory/02-bench-rules.md`'s checksum contract the `Weak` arm is **not an
   admissible alternative rung at all**, so *"`Rc`-both-ways would have to be
   pinned as THE safe spelling"* is not the objection it looks like — the
   contract pins it for you.
2. ⚠⚠ **But the row dies harder anyway, because THE HEADLINE IS FALSE.** The
   correct C comparator for `Rc` is C's own reference counting, and **it leaks
   identically**. The correct Rust comparator for C's arena is the index arena,
   and **it is leak-free at the same checksum**. **Leaking is selected by the
   OWNERSHIP DISCIPLINE, not by the LANGUAGE. There is no inversion, so there is
   no `outcome 4` here.**

⚠ **`.memory/01-ladder.md`'s outcome 4 rests on the `Rc`-vs-`Weak` DLL pair.**
That pair is real, but the *generalisation* to *"the safe rung is WORSE than C"*
does not survive an attacker-shaped edge set, because the C side of that
comparison was never varied. **Recommend annotating outcome 4 as scoped to the
statically-asymmetric case rather than striking it** (rule 9: the conclusion and
the mechanism have different evidence).

The manager also asked whether this is `p17`/`p42`'s result in new vocabulary.
**It does not get that far.** `p42`'s result is about **R5's proof not covering
its own bug class**; `p34` has no rung-to-rung difference at all to publish.

---

## 6 — DELIVERABLE 3: THE RANKING, AND WHY THE LOSER LOSES

Two rows reached limb 4 on measurements: `p29` (clause 3) and `p32`/`p33`
(clause 3). **`p29` wins.**

| | `p29` | `p32`/`p33` |
|---|---|---|
| safe rung silently wrong | ✅ measured, two independent spellings agree | ✅ measured |
| does the safe rung differ from C anywhere? | ✅ **yes** — C aborts, Rust returns a wrong number (3 of 5 inputs) | ❌ **no** — slab arm is C bit-for-bit; boxed arm is hardened C bit-for-bit |
| is either spelling already a shipped row? | the R4/R5 side is `p27`'s machinery; **the R1↔R2 result is neither `p27`'s nor `p04`'s** | ⚠ **both spellings are, bit-identically** |
| new safety predicate? | ✅ *"is the node this pointer names still the node I found?"* — **C cannot write it** | ❌ `live[h]`, which is `p27`'s exactly |
| new detector behaviour? | ✅ **two detector vectors on one program, selected by input** | ❌ one vector, already published twice |
| R5 | ✅ **already built, `9/0`, TCB 0, re-verified today, survives 2 mutants** | not attempted |

⚠ **`p32`/`p33` loses because it has no degrees of freedom.** Its ladder is fully
determined by one representation choice and both answers are already on the
shelf. That is a cleaner statement than *"it is `p04`'s class"* and it should be
what goes in the cell.

---

## 7 — DELIVERABLE 4: THE FIRST DELIVERABLE FOR A RE-OPENED `p29`, NAMED

> ### ⚠⚠ **SETTLE THE DEGREE SPLIT FIRST — before any cell is built.**

**Because the R1/R1h convention every shipped pattern uses SILENTLY FAILS here,
and it fails in the flattering direction.** Measured
(`.temp/t133/b_express/k29_bst_null.c`, regenerated by `gen_nullsaved.py`;
`logs/b29-r1h.log`). R1h-candidate is R1 **plus one line** —
`if (t == g_saved) g_saved = NULL;` at each `free`, which is the canonical C fix:

```
victim deg |                   R1        R1h ONE-LINE     R1h re-derive-by-key | one-line fixes it?
    10   2 |        8684676078980       8684676078980            8684676083620 |    False
     5   0 |        ABORTED(ASan)       8684676083620            8684676083620 |    True
    20   2 |        8684676081220       8684676081220            8684676083620 |    False
    15   0 |        ABORTED(ASan)       8684676083620            8684676083620 |    True
    25   0 |        ABORTED(ASan)       8684676083620            8684676083620 |    True
```

⚠⚠ **The one-conjunct R1h fixes 3 of 5 inputs and on the other 2 produces the
BUGGY checksum bit-for-bit** — because on a two-child victim nothing was freed,
so the null-the-cache line never fires. A `p29` built on the usual
"R1h = R1 + one conjunct" convention would ship an R1h that **still has the bug**,
past a green gate, with the residue hidden in exactly the inputs where ASan is
silent. **That is `RECAP`'s "a headline can be wrong in the FLATTERING direction
and pass a green gate", available to be caught before a line is written.**

So the §0 question for `p29` is **not** *"is the bug real?"* (it is) but:

1. **Does the row publish ONE bug or TWO?** If two, the input set splits and so
   does the harm matrix, and `.memory/02-bench-rules.md`'s *"never compare COST
   on an input where the unhardened rung commits UB"* puts the UAF inputs and the
   recycle inputs in **different cost classes**.
2. **What is R1h?** Either (a) re-derive by key, which is not one conjunct and
   deletes the pattern's own subject, or (b) null-the-cache, which is one
   conjunct and **does not fix the recycle half**, or (c) `p27`'s liveness table,
   which *is* `p27`. **Pick before building; all three change what the row means.**
3. **Which safe spelling is R2, and is R3 allowed to be the other one?** Both
   measured spellings agree observably but are structurally unrelated
   (`Vec` + free list vs `Rc<RefCell>`), so `p27`'s per-language
   `required`/`forbidden` machinery is needed, not optional.

⚠ **And re-state the row's novelty as a QUESTION in the task file**, per the
standing rule: *"is `safe Rust removes the DETECTOR, not the bug` a result this
tree does not already have?"* — my §3c/§4/§5 say yes, and I would rather the
engineer re-run it than inherit it as fact.

---

## 8 — CLEAN NEGATIVES: named attacks that did NOT land. Do not re-run these.

1. **"The `E0502` might be BST-specific after all."** No. Reproduced at
   `TASK_133` on `struct S { v: u32 }` with no data structure. `TASK_095` E1
   stands.
2. **"`p29`'s safe rung might have an unsearched spelling that behaves like
   hardened C."** Searched three; two compile and **agree with each other on all
   five inputs**, and neither equals hardened C on any input.
3. **"`p30`'s `maxchain` measurement might not reproduce."** Not re-run — but
   the structural claim did: my chained table terminates on every input in
   `mixed.bin`, and the `UNLINK` arm is ASan-clean throughout. `p22`'s
   non-termination is structurally absent, as the cell says.
4. **"`p32`/`p33`'s safe slab might diverge from C somewhere."** It does not, on
   either bug shape, at the byte level.
5. **"Maybe LSan is simply blind to the C refcount graph on this box."**
   Positive control fires (4096 B); the `ARENA` arm of the *same binary family*
   reports 0 leaks; the `RC` arm reports 432 B / 2160 B. The detector is working.
6. **"`p42` already covers `p34`."** Does not arise — `p34` has no rung
   difference to cover.

---

## 9 — WHAT I DID NOT DO, AND WHAT I AM UNSURE OF

- **No cost axis was measured** for any of the five. Under the amended bar a
  non-cost result is shippable, so this did not decide anything — but it means
  **I cannot tell the manager what `p29` costs**, and `TASK_095`'s
  `+48.01 Ir`/key (the `remove`-inclusive pair) is the only figure that exists.
- **I did not re-run `p30`'s `maxchain=4096 of 4096`** flood, nor `p34`'s
  `2 allocs / 0 frees / 240 bytes` window. Both are already twice-measured.
- **I did not build a Verus rung for `p32`/`p33`/`p30`/`p34`.** For a refused row
  that is scope I declined; for `p29` the R5 already exists.
- **`p29`'s recycle half may still be a duplicate of `p04`/`p33` and I may be
  over-weighting the conjunction.** My case is that the *pair* — one line, two
  classes, input-selected, with safe Rust silent on the half C catches — is new;
  a reader who only counts bug classes will see `p27 ∪ p04` and be entitled to.
  **This is the call I am least sure of, and it is the one that decides whether
  the re-opening is worth ~3 tasks.**
- **My `census.py` pointer-hosting regex has one known false positive** (`p46`),
  disclosed in §1b. The two load-bearing hits (`p27`, `p42`) were read by hand.
- **`.temp/t133` binaries and `.bin` files are deleted**; `run.sh` rebuilds all
  of them and re-runs every number above.

---

## 10 — ⚠ A CONCURRENT BRANCH, NOTED FOR RECONCILIATION (I did not coordinate with it)

`RECAP.md`'s working tree gained finding **48** (`TASK_134`, engineer, **not yet
reviewed**) while I was running. I did not read it until my measurements were
finished, and I changed nothing in this report because of it. Two points the
manager needs when reconciling:

- ✅ **It corroborates my §3c and §4 from a different direction.** Its
  *"`pop` ends the element's lifetime, `push` recycles the slot, the read gets
  the new occupant … `forbid(unsafe_code)` … MIRI-CLEAN"* is my safe index arena
  and my `r33_pool` slab arm, on unrelated programs.
- ✅ **Its headline — *"the borrow checker is an ALIASING mechanism, not a
  temporal one"* — is CONSISTENT with my §3d and strengthens it.** It is the
  reason I refused to let `p29` re-open on limb 4 clause 1. ⚠ **If the manager
  lands finding 48, §3d stops being a caution and becomes a rule: no temporal
  row may cite a borrowck rejection as its mechanism.**
- ⚠ **I did NOT verify anything in finding 48**, and my `p29` re-opening does
  **not** depend on it either way.

---

## Memory updates owed (the manager applies, after this review)

1. `.memory/06-catalogue.md` `p29` cell — replace *"22 of 24 patterns take their
   payload from a file blob, so the shipped kernel cannot host a pointer"* with
   the corrected pair: **26/26 take payload from a file blob; 23/26 declare the
   canonical signature; a file cannot NAME a pointer but can name an operation
   that SAVES one; `p27` and `p42` host pointers inside the kernel.**
2. `.memory/06-catalogue.md` `p32`/`p33` — the reason becomes *"two spellings,
   both already shipped bit-identically (safe slab == buggy C; safe
   `Option<Box>` == hardened C)"*.
3. `.memory/06-catalogue.md` `p34` — the reason becomes *"no inversion: C's own
   refcount rung leaks identically, and `Weak` changes the checksum so it is not
   an alternative rung"*. Strike the `Weak`-is-equally-idiomatic reason.
4. `.memory/01-ladder.md` outcome 4 — **annotate as scoped** to the
   statically-asymmetric (DLL) case; do **not** strike (rule 9's refinement:
   the DLL measurement stands, the generalisation does not).
5. `.memory/01-ladder.md` `p32`/`p33` bullet — record that `p27`'s hashed `why`
   predicted the result, and that it names `p17` where the ladder names `p04`.
6. If `p29` is re-opened: its cell must **not** cite "outcome 5" (§0).

---

**PROTOCOL rule 2 running count: I was launched carrying 634.**
My branch delta is **+9**: §0 (the task file's "outcome 5" against `.memory/`'s
strike), §1a (the count is stale), §1a again (two counts merged into one), §1b
(the conclusion is refuted by two shipped kernels), §1c (the compression changed
what `p27`'s `why` says), §3b (one line, two input-selected bug classes — the
manager's `p29` pitch does not contain it), §4 (the least-certain call: neither
"temporal" nor "logical"), §5 (the `Weak` reason is false in the shipped shape),
§5 again (`p34`'s own headline is false — C leaks too). **634 + 9 = 643.**

⚠ **A concurrent branch also carries 634. Reconciliation is the manager's job,
not mine** (PROTOCOL rule 1, the `TASK_099`/`TASK_100` collision) — do **not**
add the two deltas as if they were one ledger.
