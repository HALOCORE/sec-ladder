# p27 — handle table over per-record allocations: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and *both* C rungs ignore it — p06's, p12's and
p14's shape.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

⚠ **What p27 does NOT need, and the measurement that says so.** TASK_055 §2.8
proposed a formulation in which the slab and the handle table are *arguments*,
with different signatures per rung — and TASK_055_REVIEW M1 found that
`harness/dloop.py:361` raises on the resulting arity mismatch, leaving a **dead
`slab` argument at R4/R5** as the only escape. **p27 needs neither.** The driver
loop is pinned identical across all seven rungs, so there is nowhere rung-specific
to build a slab; the slab therefore lives *inside* the kernel, exactly as p14's
scratch and field table do, and every rung's signature is the one above.

The dead-argument escape was measured anyway, because the task asked
(`NOTES.md` 1): at `-O3` it is **free and byte-identical** (LLVM's
dead-argument elimination removes it entirely; `kernel` and `main` both
`md5_raw`-identical, `385.0000` Ir/call either way), and at `-O0` it costs
**+3.0000 Ir/call**, all of it at the call site. So the escape survives `-O3`
exactly — and p27 does not use it.

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nops   u32 LE    DECLARED operation count       ATTACKER DATA
byte 4..      ops, each 2 bytes:
                u8  c         opcode byte                     ATTACKER DATA
                u8  a         operand byte                    ATTACKER DATA
data_start = 4
TABCAP = 32                   the handle table's extent
RECSZ  = 1                    one record, one allocation
SENT   = 251                  what a rejected operation folds
```

`TABCAP`, `RECSZ` and `SENT` are compile-time constants in every rung. They are
properties of the *program* — a handle table has a fixed number of slots and a
record has a fixed size — and not of the input: `n_iters`, `stride`, `n_blob`,
`nops`, every opcode byte and every operand byte come from the file.

**Every byte value is a legal opcode.** The opcode is `c % 4`, so no input is
malformed and no rung rejects anything for shape. `a` is the record's *value* on
an OPEN and the *slot number* on a CLOSE or a READ.

**Honesty is a property of the file, not of the kernel.** No rung checks that
`nops` is truthful, no rung checks that a handle names a live slot before
testing it, and — the part that matters — *the specification does not assume the
op stream is well formed*. See "What the `ensures` is, and what it is not".

## Semantics

```
if len < 4:                                   return 0
nops from the header
if nops == 0:                                 return 0

tab[TABCAP] = {NULL} ; live[TABCAP] = {0} ; ntab = 0 ; acc = 0 ; p = 4
for o in 0 .. nops:
    if len - p < 2:   break                                # subtraction-first
    c = buf[off+p] ; a = buf[off+p+1] ; p += 2 ; h = a
    switch c % 4:
      0 OPEN :  if ntab < TABCAP:                          # in EVERY rung
                    q = malloc(RECSZ) ; *q = a
                    tab[ntab] = q ; live[ntab] = 1 ; ntab += 1
                    acc = acc *64 31 +64 a
                else:
                    acc = acc *64 31 +64 SENT
      1 CLOSE:  if h < ntab and live[h] == 1:              # in EVERY rung
                    free(tab[h]) ; live[h] = 0
                    acc = acc *64 31 +64 1
                else:
                    acc = acc *64 31 +64 SENT
      2,3 READ:
                # >>> THE SAFETY LINE. R1 omits exactly `live[h] == 1`. <<<
                if h < ntab and live[h] == 1:
                    acc = acc *64 31 +64 *tab[h]
                else:
                    acc = acc *64 31 +64 SENT

for j in 0 .. ntab:                                        # THE EPILOGUE
    if live[j] == 1: free(tab[j]) ; live[j] = 0

return acc *64 31 +64 ntab
```

`*64` and `+64` are wrapping `u64` operations.

**Slots are never reused.** `ntab` only grows, so a closed slot stays closed for
the rest of the call and a liveness *bit* is enough — a generation counter with
the reuse removed. This is why no rung carries a generation and why the ABA
problem does not arise.

## The bug, and why it is the one this project has never had

R1 writes `if (h < ntab)` where R1h writes `if (h < ntab && live[h] == 1)`. On a
READ naming a slot that has been closed, R1 loads through a pointer whose record
has been `free`d.

**Every other bug in this tree is spatial or logical.** p02, p05, p12, p13 and
p14 index outside an allocation; p17 and p09 read the wrong thing inside a live
one. p27's address is inside **no live allocation at all**. That is a different
class, it is the class safe Rust rejects at *compile* time, and it is the reason
this pattern exists.

**Three things make it that class rather than a lookalike:**

1. **`free` is a real `free`.** Each record is its own `malloc(RECSZ)` and its
   own `free`. If the table were one slab and "close" were a freelist push, the
   stale read would be *in bounds of a live allocation*: Miri would not flag it,
   `PointsTo` would license it, and the bug would be **logical** — which is
   p17's class and the tree already has one (TASK_055 §2.8 caveat 1).
2. **R1 keeps the slot bound.** `h < ntab` is in every rung, so `tab[h]` is
   always a table entry that was written by some OPEN. The bug is not "index out
   of range"; it is "the record behind this index is gone".
3. **The liveness bit cannot be the pointer.** The handle is an *integer* — the
   op stream comes out of a file and a file cannot name a pointer — so the READ
   must consult something. Nulling `tab[h]` on close would turn the stale read
   into a NULL dereference, which is a crash and a different bug class, and it
   would leave the epilogue unable to tell a closed slot from a live one.

## Why the use-after-free lives on ADVERSARIAL inputs only

Two independent reasons, and either alone would be enough.

1. `harness/check.py` stage 2 requires every non-adversarial cell to agree with
   `model.py` **and with every other cell**. R1 reading a freed record disagrees
   with all of them.
2. **What a stale read returns is a function of the optimisation level**, and
   `harness/build.py` puts both levels in one agreement set. TASK_055_REVIEW
   blocker B1 measured it on the probe: `gcc -O0..-O2` print
   `2582767925679282152` and `gcc -O3` prints `6789584477807083544`, because at
   `-O3` the stores into the recycled record are dead-store-eliminated — the
   recycled record does not exist in the `-O3` binary at all. **A pattern that
   put the UAF on a perf row would be publishing a number from the one build
   where the bug does not execute.**

⚠ The offset-16 rule recorded in `.memory/03-measurement.md` is a **true but
insufficient** sub-fact. `spec.md` therefore declares **no fiat** about it:
TASK_055_REVIEW m5 is right that neither §2.7 fiat is checkable by reading
`spec.md` alone, and with the UAF on adversarial rows the question does not
arise.

## The adversarial rows

A use-after-free has no magnitude axis. What it has is a **recycling** axis, and
that is what decides whether the harm is disclosure or noise:

| input | shape | R1's harm |
|---|---|---|
| `adversarial-uaf` | OPEN, CLOSE, OPEN (tcache LIFO returns the same chunk), READ the closed handle | **discloses the newer record's byte under the older record's handle** — deterministic, and *identical on gcc and clang* |
| `adversarial-noreuse` | OPEN, CLOSE, READ, with no OPEN between | reads glibc's own safe-linked tcache `next` word — **a different number on every run** |
| `adversarial-many` | 24 stale reads in one window, both shapes | the same, 24 times |
| `adversarial-stride3` | a 3-byte window | none: the driver guard `stride_w >= 4` skips the loop and every rung prints 0 |

⚠ **`adversarial-noreuse`'s R1 cells are deliberately not reproducible**, and
that is the row's whole point: it is the measurement behind
`.memory/03-measurement.md`'s constraint. Its recorded stdout in
`results/gate/p27-handle-table.json` therefore changes on every gate run for the
`c-gcc` and `c-clang` cells and for those cells only. Stage 4 *records*
behaviour rather than requiring it, so this is a note and not a failure.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == op_fold(buf, off, len)
```

`op_fold` is the spec function; `model.py` is its independent Python twin — and
independent in a way that matters here: `model.py`'s *simulation* keeps the
table as a list of `Optional[int]`, which is the safe rungs' `Option<Box<u8>>`
and carries no separate liveness array at all, while the helper `op_fold`
mirrors `verus.rs`'s `run` and carries the two parallel sequences `vals` and
`lv`. **The two implementations disagree about where liveness is stored and
agree about the answer** — which is precisely the difference R1's bug lives in.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. It is **ONE clause**, as on p03, p06, p11,
p12 and p14 and unlike p17.

### What the `ensures` is, and what it is not

**It is the FUNCTIONAL postcondition.** `run` is an abstract machine carrying a
value sequence `vals` and a liveness sequence `lv`; the `ensures` says the
accumulator is what that machine computes. A memory-safety-only spec would
accept a kernel that folded a closed record's value, or a different record's, or
that truncated at a different `TABCAP`; this one rejects all three. `NOTES.md`
10 is where the mutants are.

**And there is a second thing the `ensures` deliberately does not say: that
`nops` is honest, that the op stream is well formed, or that a handle names a
live slot.** `run` specifies what the *program* does — stop when the window runs
out, reject an OPEN past `TABCAP`, reject a CLOSE or a READ of a slot that is out
of range or already closed — so `degenerate`, `adversarial-uaf`,
`adversarial-noreuse` and `adversarial-many` are all inside the verified domain
and every checked rung agrees with `model.py` on all four. Writing the stronger
precondition would have been an assumption about the contents of a file that no
honest loader can discharge (`.memory/02-bench-rules.md`), and it would have
deleted every row the pattern exists for.

## The trusted base, and what its number does not mean

⚠ **Read `NOTES.md` 6 before quoting `tcb_items`.** p27 publishes **seven**
project-local trusted items, and **not one of them is the temporal property**:

- `buf_get_unchecked`, `arr_get_unchecked`, `arr_set_unchecked` — the *spatial*
  accessors, the same axiom every unsafe rung in this project ships;
- `load_input`, `emit` — infra, in every pattern here;
- `rec_alloc`, `rec_free` — `vstd::raw_ptr::allocate` and `deallocate` copied
  into the crate **for a codegen reason**, whose *verified twins are vstd's own
  `allocate` and `deallocate`*, so the gate itself proves the copies are no
  stronger than the originals. ⚠ Not *character for character*: `rec_alloc`
  ships **three** of vstd's five `ensures` (two were dropped as not
  load-bearing), `rec_free` spells vstd's six `requires` through `dealloc@.`
  rather than a destructured `dealloc.`, and both bodies write `std::alloc::`
  where vstd writes `alloc::alloc::`. Every difference is a weakening or a
  respelling; the twins are what make that checkable rather than asserted.

The whole lifetime argument — `PointsTo` consumed by a deallocation, a
permission map maintained across `open`/`close`, and a stale read that has no
permission to present — costs **zero** project-local axioms: `ptr_ref` and
`ptr_mut_write` are `external_body` *inside vstd*, and `into_typed`, `into_raw`,
`leak_contents` and the `Map` operations are vstd `axiom fn`s. TASK_055 §2.5's
alarm is therefore **confirmed in substance and wrong in its number**: a
raw-pointer rung does not publish `tcb_items = 2`, because a real pattern also
indexes a table and reads a window — but the part of it that does manual
allocation genuinely adds nothing to the column.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p27's payload is p06's, p11's, p03's, p12's, p16's,
p17's, p05's, p07's and p14's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes`, reused verbatim,
with **nothing added to `common/` for p27**.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here. The
allocations p27 is about are the *records*: their size is the compile-time
constant `RECSZ`, at most `TABCAP` are alive at once, and every one of them is
freed before the kernel returns.

## Driver loop

Identical in all seven rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers, and byte-for-byte p06's, p12's and p14's. `harness/check.py` normalises
every copy — the C one included — and diffs it against `driver.canonical` below.

```
n_blob := bytes.len()
buf    := bytes
acc    := 0
if stride_w >= 4 and stride_w <= n_blob:
    stride := stride_w as usize
    nwin   := (n_blob / stride) as u64
    it     := 0
    while it < n_iters:
        k   := ((acc as u128 * nwin as u128) >> 64) as usize
        r   := kernel(buf, k * stride, stride)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

`stride_w >= 4` because p27's window header is the 4-byte `nops` field.
`adversarial-stride3.bin` attacks it.

### Why this does not evaporate

Same mechanism as every earlier pattern: `k` is derived from `acc`, and `acc`
from the previous call's result, so call *i+1* cannot begin until call *i* has
returned. Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile`.

**And there is a second reason here that no earlier pattern has**: the kernel
calls `malloc` and `free`, which are opaque cross-TU calls in every rung, so
even a compiler that could see through the fold cannot remove them.

### Why every window must return non-zero, and why every benign window must read only live slots

`inputs/gen.py` checks both, by running a copy of the checked kernel over every
window of every blob it emits. The first is `.memory/01-ladder.md`'s absorbing
state (`acc == 0` pins `k = (acc*nwin) >> 64` at 0 for ever). The second is the
adversarial-only rule above — and the check earned its keep on the first draft
of `degenerate.bin`, which contained a `READ 0` after a `CLOSE 0` and was
refused.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.call_args` declares which
argument *positions* of a named call are the canonical ones
(`{"c": {"kernel": [0, 2, 3]}}`), and `harness/dloop.py` refuses to drop anything
that is not a single bare identifier. **This is p14's pin unchanged**; p27 adds
no new declaration surface.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts and
the price of the identity pin.

| pin | why |
|---|---|
| `verus.obligations` = 15 | **`TABCAP` 1 + `RECSZ` 1 + `SENT` 1 + `run` 1 + `rec_open` 1 + `rec_close` 1 + `rec_read` 1 + `kernel` 3 + `main` 4 = 15.** Every term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, and so were the zero terms. `kernel`'s 3 is 1 body + 1 per loop body (**two** loops: the op walk and the epilogue). |
| `verus.twin_obligations` = 20 | the count under `--cfg slb_twin`. **15 shipped + 5**, one per trusted item inside the twin regime. Two of the five twins are `vstd::raw_ptr::allocate` and `deallocate` themselves — see the TCB section above. |
| `identity` `O3: exact`, `O0: norel` | and **it cost two lines to get**, both recorded in the pin's `why`: local `#[inline(always)]` copies of vstd's allocation API instead of calls to it, and `*base = v` instead of `core::ptr::write(base, v)`. With vstd's own `allocate` the pair is `differ` at both levels. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`, and since TASK_010 that does not make Miri optional. On p27 Miri is the **only** tool in the matrix that checks the *temporal* property on the unsafe rung. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == op_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (op_fold). p27's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05 and p07 use and NOT p02's before/after set: p27's records are allocated AND FREED inside the kernel, so no buffer crosses the signature and there is nothing for an `after` binding to name. **The security property is carried by the LIVENESS conjunct on the READ path** -- `live[h] == 1` in C and in the unsafe rungs, `Some(..)` in the safe rungs -- and at R5 it is what the permission map converts into `perms.dom().contains(h)`, which is the precondition `rec_read` cannot be called without. **The `ensures` is the FUNCTIONAL one**: `run` is an abstract machine carrying a value sequence `vals` and a liveness sequence `lv`, and it says the accumulator is what that machine computes -- so a kernel that folded a closed record's value, or the wrong record's, or that truncated at a different TABCAP, is rejected. **What the `ensures` deliberately does NOT say is that `nops` is honest, that the op stream is well formed, or that a handle names a live slot.** `run` specifies what the PROGRAM does -- stop when the window runs out, reject an OPEN past TABCAP, reject a CLOSE or a READ of a slot that is out of range or already closed -- so degenerate.bin, adversarial-uaf.bin, adversarial-noreuse.bin and adversarial-many.bin are ALL INSIDE the verified domain and every checked rung agrees with model.py on all four. A `requires` that a handle named a live slot would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete every row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: the liveness conjunct on the READ path, `if (h < ntab && live[h] == 1) {` in c/kernel_hardened.c. c/kernel.c writes `if (h < ntab) {` there and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.",
        "rust": "THE SAFETY LINE: the liveness test on the READ path, `if h < ntab && arr_get_unchecked(&live, h) == 1u8 {` in unsafe.rs and verus.rs. In the safe rungs it is the `Option` discriminant instead -- `tab[h].is_some()` in safe_naive.rs and the `Some(rec)` arm in safe_tuned.rs -- because safe Rust has no separate liveness array to test: `Option<Box<u8>>` is niche-optimised to one pointer word and IS the hardened-C representation. That is the pattern's whole subject; see the why key."
      },
      {
        "c": "THE LINE THE C RUNG MUST NOT FORGET, present in BOTH C rungs: `live[h] = 0;` immediately after the `free`. R1's bug is NOT that it skips this -- it does not -- it is that its READ path never asks. Splitting the free from the invalidation is what makes forgetting possible at all.",
        "rust": "the same line in the unsafe rungs, `arr_set_unchecked(&mut live, h, 0u8);` in unsafe.rs and verus.rs -- and at R5 the proof FORCES it: without it the loop invariant cannot be re-established, because `rec_free` has consumed slot h's permission while the liveness array would still claim it exists. In the safe rungs there is no such line, because `tab[h] = None` and `tab[h].take()` free the record and invalidate the handle in ONE operation."
      },
      {
        "c": "THE REAL `free`, in both C rungs: `free(tab[h]);`. Not a freelist push into a slab -- see the why key.",
        "rust": "THE REAL free, in all four Rust rungs: `std::alloc::dealloc(p, layout);` inside rec_free in unsafe.rs and verus.rs (`vstd::raw_ptr::deallocate`'s six preconditions and its body, respelled but not weakened -- see the TCB section -- whose verified twin in verus.rs is vstd's own `deallocate`), and the drop of `Option<Box<u8>>` in safe_naive.rs and safe_tuned.rs."
      },
      {
        "c": "ONE ALLOCATION PER RECORD, in both C rungs: `malloc(RECSZ)`.",
        "rust": "ONE ALLOCATION PER RECORD, in all four Rust rungs: `std::alloc::alloc(layout)` inside rec_alloc in unsafe.rs and verus.rs, and `Box::new(a)` in safe_naive.rs and safe_tuned.rs. Rust's default global allocator calls `malloc` for `align <= 8`, so all seven rungs hit the same glibc, in the same size class, once per record."
      },
      {
        "c": "the handle table's extent is a COMPILE-TIME CONSTANT and the capacity guard is in every rung including R1: `if (ntab < TABCAP) {` in both C rungs.",
        "rust": "the capacity guard, in all four Rust rungs: `if ntab < TABCAP {`."
      },
      {
        "c": "the SLOT BOUND is in every rung including R1, so the bug is TEMPORAL and not spatial: `h < ntab` in both C rungs.",
        "rust": "the slot bound, in all four Rust rungs: `h < ntab`."
      },
      {
        "c": "the EPILOGUE frees every record still alive, so neither C rung leaks and the allocator state at the end of a call is the state at its start: `for (j = 0; j < ntab; j++) {` in both C rungs.",
        "rust": "the epilogue, in unsafe.rs and verus.rs: `while j < ntab {`. **safe_naive.rs and safe_tuned.rs deliberately do NOT have one** -- dropping the table is the epilogue, written by the language -- and that asymmetry is a measured result rather than an oversight (../NOTES.md 3)."
      },
      {
        "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.",
        "rust": "the cursor guard, subtraction-first, in all four Rust rungs: `if len - p < 2 {`."
      },
      {
        "c": "the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.",
        "rust": "the opcode, in all four Rust rungs: `c % 4 == 0`."
      },
      {
        "c": "a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `acc = acc * 31 + SENT;` in both C rungs.",
        "rust": "the sentinel fold, in all four Rust rungs: `.wrapping_add(SENT)`."
      },
      {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the literal multiplier: `acc = acc * 31 +` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal multiplier: `.wrapping_mul(31)`."
      },
      "the slot count is folded last so that a rung which opened a different number of records cannot produce the same checksum: `ntab` appears in the return expression of all seven rungs."
    ],
    "forbidden": [
      "`realloc(`",
      "`calloc(`",
      "`Vec::with_capacity`",
      "`Rc<`",
      "`RefCell`",
      "`ManuallyDrop`",
      "`mem::forget`",
      "`Box::leak`",
      "`Box::into_raw`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. Here that clause is load-bearing and it IS the pattern. THE FREE AND THE INVALIDATION ARE ONE OPERATION IN SAFE RUST AND TWO IN C: `tab[h] = None` frees the record and invalidates the handle together, and `free(tab[h]); live[h] = 0;` is the same thing written twice, which is what makes forgetting the second half possible. So the safe rungs have no `live[]` array and cannot be asked to spell one, and the unsafe rungs have no `Option` and cannot be asked to spell that. THE HANDLE IS AN INTEGER AND THAT IS WHY NULLING IS NOT A DEFENCE: the op stream comes out of a file and a file cannot name a pointer, so the READ has an index and must consult something to learn whether the record is there. Nulling `tab[h]` on close would make a stale read a NULL DEREFERENCE -- a crash, a different bug class -- rather than a use-after-free, and it would leave the epilogue unable to tell a closed slot from a live one without the very bit it is trying to avoid carrying. `live[]` is a generation counter with slot reuse removed, and every real handle table carries one. THE FREE MUST BE A REAL `free`: if the slab were one allocation and 'close' were a freelist push, the stale read would be IN BOUNDS OF A LIVE ALLOCATION -- Miri would not flag it, `PointsTo` would license it, and the bug would be LOGICAL, which is p17's class and the tree already has one (TASK_055 \u00a72.8 caveat 1). That is what `Box::into_raw`, `ManuallyDrop`, `mem::forget` and `Box::leak` are forbidden for: each is a route to holding a record past its free without the allocator knowing, i.e. to turning the temporal bug back into a logical one. `realloc`/`calloc`/`Vec::with_capacity` are forbidden because they change the allocator traffic and the pattern's fairness argument is that every rung makes exactly one allocation and one free per record; `Rc`/`RefCell` because they would move the liveness decision to run time inside the library and delete the comparison. WHAT IS DELIBERATELY NOT PINNED is how the liveness test is SPELLED -- `is_some()` in R2, a `match` arm in R3, `take().is_some()` in R3's CLOSE -- exactly as p14 leaves its fold loop unpinned: those are the R3-side levers, they cost zero TCB, and the pattern reports the cheapest one FOUND on a named input rather than a minimum (../NOTES.md 8). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 15
    },
    "twin_obligations": {
      "verus.rs": 20
    },
    "obligations_note": "15 = TABCAP 1 + RECSZ 1 + SENT 1 + run 1 + rec_open 1 + rec_close 1 + rec_read 1 + kernel 3 + main 4, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. The zero terms are checkable the same way: u32_at, nops_at, op_fold, slot_ok and wf are NON-RECURSIVE spec fns and report 0, while `run` is RECURSIVE and carries one termination query; buf_get_unchecked, arr_get_unchecked, arr_set_unchecked, rec_alloc, rec_free, load_input and emit are external_body and report 0. THREE `const`s carry one query each (`.memory/04-verus.md`: a `const` inside verus! is its own obligation). kernel's 3 = body + TWO loop bodies (the op walk and the epilogue). main's 4 is quoted AS MEASURED: body + driver loop + one per by-block would predict 5 and Verus reports 4, the same off-by-one p03, p05, p06, p07, p11, p12, p14 and p17 record for the identical driver.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 15 shipped + 5, one per trusted item that is inside the twin regime: slb_twin_buf_get_unchecked, slb_twin_arr_get_unchecked, slb_twin_arr_set_unchecked, slb_twin_rec_alloc and slb_twin_rec_free. **The last two are unusual and are the point of the pattern's TCB section: their checked implementations are `vstd::raw_ptr::allocate` and `vstd::raw_ptr::deallocate` themselves**, so what the twin stage proves is that this crate's copies are no stronger than vstd's originals -- a relocation of trust for a codegen reason, not new trust. `load_input` and `emit` are outside the regime (external_body with no `ensures` and no `unsafe` body) and have no twins.",
    "unsafe_justifications": {
      "verus.rs": {
        "arr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth and p27 the fifth.",
        "rec_alloc": "`size` and `align` are constrained by `valid_layout(size, align)` and `size != 0`, which is vstd's own precondition for the identical body, and the returned pointer is constrained by THREE `ensures` clauses copied from vstd verbatim -- vstd states five, and the other two (`pt.0.addr() + size <= usize::MAX + 1` and `pt.0.addr() as int % align as int == 0`) were dropped when the gate's clause-mutation stage found them not load-bearing at `align == 1`; the `verus.items` dump below is the authority and lists three. Dropping them makes the item strictly WEAKER, and the twin -- vstd's own `allocate` -- still verifies, which is what a weakening has to do. There is no unconstrained parameter. The reason this item exists at all is CODEGEN and not trust: vstd carries no `#[inline]` on `allocate`, so an R5 that called it directly emits a GOT-indirect cross-crate `call` that unsafe.rs cannot produce, and the `identity` pin drops from `exact` to `differ` (measured, ../NOTES.md 5). Its verified twin is vstd's `allocate`.",
        "rec_free": "Every parameter is constrained: `p`, `size` and `align` by the four `dealloc.*` equalities, and the two tracked permissions by `pt.is_range(..)` and the provenance equalities -- vstd's own six preconditions for the identical body, all six shipped, RESPELLED through `dealloc@.` / `pt@.` because vstd destructures its tracked parameters (`Tracked(pt): Tracked<PointsToRaw>`) and this item takes plain ones; the destructured form made the gate's tautology probe unsynthesisable and left all six conjuncts unjudged. Its verified twin is vstd's `deallocate`. Same codegen reason as `rec_alloc`."
      }
    },
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nops_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "op_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "slot_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "buf_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_buf_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "load_input": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "emit": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "arr_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_arr_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "arr_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_arr_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "rec_alloc": {
          "external": "verifier::external_body",
          "requires": [
            "valid_layout(size, align)",
            "size != 0"
          ],
          "ensures": [
            "pt.1@.is_range(pt.0.addr() as int, size as int)",
            "pt.2@@ == (DeallocData { addr: pt.0.addr(), size: size as nat, align: align as nat, provenance: pt.1@.provenance(), })",
            "pt.0@.provenance == pt.1@.provenance()"
          ]
        },
        "slb_twin_rec_alloc": {
          "external": null,
          "requires": [
            "valid_layout(size, align)",
            "size != 0"
          ],
          "ensures": [
            "pt.1@.is_range(pt.0.addr() as int, size as int)",
            "pt.2@@ == (DeallocData { addr: pt.0.addr(), size: size as nat, align: align as nat, provenance: pt.1@.provenance(), })",
            "pt.0@.provenance == pt.1@.provenance()"
          ]
        },
        "rec_free": {
          "external": "verifier::external_body",
          "requires": [
            "dealloc@.addr() == p.addr()",
            "dealloc@.size() == size",
            "dealloc@.align() == align",
            "dealloc@.provenance() == pt@.provenance()",
            "pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int)",
            "p@.provenance == dealloc@.provenance()"
          ],
          "ensures": []
        },
        "slb_twin_rec_free": {
          "external": null,
          "requires": [
            "dealloc@.addr() == p.addr()",
            "dealloc@.size() == size",
            "dealloc@.align() == align",
            "dealloc@.provenance() == pt@.provenance()",
            "pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int)",
            "p@.provenance == dealloc@.provenance()"
          ],
          "ensures": []
        },
        "rec_open": {
          "external": null,
          "requires": [],
          "ensures": [
            "r.1@.ptr() == r.0",
            "r.1@.is_init()",
            "r.1@.value() == v",
            "r.2@.addr() == r.0.addr()",
            "r.2@.size() == RECSZ",
            "r.2@.align() == 1",
            "r.2@.provenance() == r.0@.provenance"
          ]
        },
        "rec_close": {
          "external": null,
          "requires": [
            "pt.ptr() == p",
            "dl.addr() == p.addr()",
            "dl.size() == RECSZ",
            "dl.align() == 1",
            "dl.provenance() == p@.provenance"
          ],
          "ensures": []
        },
        "rec_read": {
          "external": null,
          "requires": [
            "pt.ptr() == p",
            "pt.is_init()"
          ],
          "ensures": [
            "r == pt.value()"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == op_fold(buf@, off as int, len as int)"
          ]
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    }
  },
  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": [
      "safe_naive.rs",
      "safe_tuned.rs",
      "unsafe.rs",
      "verus.rs",
      "c/main.c"
    ],
    "aliases": {
      "c": {
        "n_body": "bytes.len()",
        "bytes": "bytes.as_slice()",
        "inp.n_iters": "n_iters"
      }
    },
    "call_args": {
      "c": {
        "kernel": [
          0,
          2,
          3
        ]
      }
    },
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 4 && stride_w <= n_blob",
      "{",
      "stride = stride_w ;",
      "nwin = n_blob / stride ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "k = acc * nwin >> 64 ;",
      "r = kernel ( buf , k * stride , stride ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },
  "collapse": {
    "probe_inputs": [
      "small.bin",
      "large.bin"
    ],
    "probe_iters": [
      100,
      200
    ],
    "note": "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 on large -- which is p16's, p05's, p11's, p12's, p06's and p14's denomination. WHICH WAY THE ESTIMATE ERRS: STRICT, and by two orders of magnitude. It OVER-counts by the 4 window-header bytes, which are decoded as a u32 and are not operations. It UNDER-counts by everything else: each 2 window bytes is one OPERATION, and an operation is a table index, a liveness test and -- for two of the four opcodes -- a `malloc` or a `free`, which are tens of instructions each in glibc. Measured, the shipped rungs run 840-1040 Ir per call against a declared 52 bytes on small, i.e. ~16-20 Ir per declared byte against a 0.25 floor. model.py declares NO min_ir_per_work, so the harness default applies unchanged; it is not a tight floor here and is not meant to be, because a kernel that calls the allocator cannot be denominated like a fold. What it still catches is the failure it exists to catch -- a kernel the optimiser collapsed to nothing. The two probe inputs differ in work_per_call (52 vs 244) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project that ALLOCATES AND FREES. **The pin has a measured price here and it is two lines.** (1) `rec_alloc` and `rec_free` are local `#[inline(always)]` copies of `vstd::raw_ptr::allocate` and `deallocate` rather than calls to vstd's own: vstd carries no `#[inline]` on either, so calling them emits a GOT-indirect cross-crate `call` that unsafe.rs cannot produce, and the pair measures `differ` at BOTH opt levels. controls/ ships that rung so the claim is checkable, and NOTES.md 5 has the disassembly. (2) unsafe.rs writes the record with `*base = v` rather than `core::ptr::write(base, v)`: the two are the same operation for a `u8`, but `core::ptr::write` is `#[inline]` and survives as a CALL at `-O0`, while vstd's `ptr_mut_write` is `#[inline(always)]` over a precompiled vstd and inlines to a bare store -- one instruction of difference and `-O0` identity drops to `differ`. At O0 the crate names differ in length so call displacements differ, which is link layout and not codegen, hence `norel` there and `exact` at O3."
    }
  ],
  "miri": {
    "pair": [
      "unsafe",
      "verus"
    ],
    "sources": [
      "unsafe.rs"
    ],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag. **On p27 Miri is doing something no other pattern asks of it: it is the only tool in the matrix that checks the TEMPORAL property on the unsafe rung.** ASan checks it on the C rungs; the O3 identity pin and the proof cover R5; but a trusted body that read one byte past a record, or read a record it had freed, would satisfy every `ensures` here and be invisible to Verus, to the twins, to the contract pin and to stages 5c/5c-req -- p08's `copy_nonoverlapping` substitution passed all of those and was caught by the O3 identity pin and Miri alone. Cost: check.py rewrites n_iters to 4, so each row performs at most 4 x nops allocator operations -- about 100 on small and 500 on large, four orders of magnitude inside `.memory`'s measured budget.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```
