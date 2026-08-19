# p03 — bounded stack over an attacker-chosen opcode stream: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and both C rungs ignore it, so R1-vs-R1h is a
comparison with the calling convention, the argument count and the register
allocation all held fixed. The only difference between those two cells is one
`if`.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     nops      u32 LE    DECLARED operation count    ATTACKER DATA
byte 4..      operations, 5 bytes each:  op u8 (0 = PUSH, else POP)
                                         val u32 LE
data_start = 4 ;  avail = len - 4                 what ACTUALLY arrived
STACK_CAP  = 64                                   a compile-time constant
```

**The operation sequence is in the file.** That is the one sentence that
separates p03 from every pattern before it. p01, p02, p05, p16 and p17 fold, p07
searches, p11 scans — in all eight the *sequence of operations* is fixed by the
code and only the data varies. Here the file decides, per step, whether the
kernel pushes or pops, which is what a protocol state machine or a bytecode
interpreter actually looks like.

## Semantics

```
if len < 4:                                   return 0
nops from the header
if nops == 0:                                 return 0
if 5*nops > avail:                            return 0     # in u64/size_t

stack: [u64; STACK_CAP] ;  sp = 0 ;  acc = 0
for k in 0 .. nops:
    op  = buf[off + 4 + 5*k]
    val = load_u32(off + 5 + 5*k)
    if op == 0:
        # >>> THE PUSH GUARD. Present in EVERY rung. <<<
        if sp < STACK_CAP:
            stack[sp] = val ;  sp = sp + 1
    else:
        # >>> THE POP GUARD. R1 omits exactly this line and nothing else. <<<
        if sp > 0:
            sp = sp - 1
            acc = acc *64 31 +64 stack[sp]
return (acc *64 31 +64 sp) *64 31 +64 nops
```

`*64`/`+64` are wrapping, as in p01/p02/p16/p17/p05/p07/p11, so the kernel has
**no precondition on values** and every measured input is inside the verified
domain by construction. C's unsigned types wrap by definition (6.2.5p9) and the
Rust rungs write `wrapping_add`/`wrapping_mul`.

**The return is read left to right, i.e. as a Horner chain**:
`(acc*31 + sp)*31 + nops`, which is the grouping the Rust method-chain spelling
forces and the one every other pattern here uses. The C rungs write the
parentheses explicitly so that the two languages cannot differ by operator
precedence.

### The index goes negative, and `size_t` makes that `SIZE_MAX`

p16 walks one step past a *length* whose subtraction wrapped; p17 computes a
wrong-but-in-bounds *index* in signed arithmetic; p07 underflows an *inclusive
bound*; p11's loop does not stop. **Here `sp - 1` at `sp == 0` is `SIZE_MAX`**,
and `stack + SIZE_MAX` wraps to `stack - 1`: the read lands **8 bytes below the
array, inside the kernel's own stack frame**, not at a wild address. That is
arithmetic and it was checked on the disassembly before any rung was written
(NOTES.md 0). Three consequences the earlier patterns could not produce:

- **It does not fault.** A plain build reads a neighbouring stack slot and
  returns a wrong answer; ASan reports `stack-buffer-underflow` on both gcc and
  clang. NOTES.md 7 records where it *does* fault, which is a measured
  1 048 576 consecutive pops — exactly this box's 8 MiB `ulimit -s`.
- **One stray POP disables the stack for the rest of the call.** With
  `sp == SIZE_MAX` the push guard `sp < STACK_CAP` is false for ever after, so
  every later PUSH is dropped and every later POP walks one slot further down.
- **What it reads is ASLR-dependent, so R1's answer is not reproducible.**
  NOTES.md 7 measures it: three runs, three values, and `setarch
  --addr-no-randomize` makes it bit-stable. That is a pointer disclosure through
  a checksum, and it is a different harm from p17's cross-window read.

### The safety check is not on a slice

Every earlier pattern's checked rung is checked against a *slice length*. p03's
guards are `sp < STACK_CAP` — a comparison against a compile-time constant — and
`sp > 0` — an **emptiness** test with no length in it at all. Do not expect
another per-byte constant; the law is per *executed POP* and NOTES.md 4 states
it in that variable.

### Load-bearing, do not "improve"

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug.

- **The PUSH guard is in every rung and the POP guard is not.** Overflow is not
  the bug being modelled and letting R1 overflow too would confound them.
  `adversarial-overflow.bin` is the row on which all eight cells agree, and it
  is what makes "only one guard is the variable" a measurement.
- **`stack` is a fixed-size LOCAL array**, `[u64; STACK_CAP]` / `uint64_t
  stack[STACK_CAP]`. A `Vec` with `push`/`pop` moves the pattern to allocator
  behaviour, which is p02's axis and not this one, and it deletes the explicit
  `sp` that the result folds and the proof's invariant is about.
- **`sp` and `nops` are folded into the result**, so a rung that ends with a
  different stack depth, or runs a different number of operations, cannot
  produce the same checksum.
- **The per-operation dispatch is a real branch on the op byte**, spelled
  `if op == 0`. A rung that converted it into a branchless select would be
  measuring a different kernel — and it would delete the branch-predictability
  axis the sweep exists for. NOTES.md 1 checks on the disassembly that no
  compiler does it unasked; p07 measured LLVM's `X86CmovConverterPass` doing the
  *opposite*, so this is a thing to verify rather than assume.
- **The little-endian header and value decodes are written out** — `b0 + 256*b1
  + 65536*b2 + 16777216*b3` — in every rung, and `from_le_bytes` is `forbidden`.
  Two reasons, and the second decides it: it would delete the decode every rung
  shares, and it **cannot be an R4/R5 spelling at the pinned vstd**
  (`from_le_bytes`, `TryFromSliceError` and `from_raw_parts` are all `is not
  supported`, TASK_027_REVIEW), so a rung using it would compare a safe cell
  against an unsafe cell that cannot exist.
- **Masking the stack index is `forbidden`.** `stack[sp & (STACK_CAP - 1)]`
  deletes the surviving bounds check for `1.00000` of its `3.00000` Ir
  (NOTES.md 4d) and it is not the same program: it silently turns an
  out-of-range access into an in-range one, which is the opposite of what this
  pattern is about.
- **`MaybeUninit` is `forbidden`.** All four Rust rungs write
  `[0u64; STACK_CAP]` because safe Rust has no uninitialised array; C's is not
  initialised. That per-call constant is a *language* difference and NOTES.md 3c
  prices it separately. Letting the unsafe rung alone skip it would open a gap
  between R4 and R3 that is not a safety gap and that no safe rung could close.
- **The ACCESS spelling is deliberately NOT pinned**, and that is the point of
  the pattern. R2 and R3 index `stack[sp]`, R4 and R5 call `get_unchecked`;
  holding those fixed would hold fixed the one thing p03 exists to compare. What
  *is* pinned is that both guards are present and that the array is the same
  fixed-size local one in all six rungs.

### The declared count bounds the walk, and the stack depth does not

`nops` is attacker data, and unlike p11's `nstr` it **is** a loop bound — but
only after the length check `5*nops > avail`, which is in *every* rung including
R1. Two adversarial inputs separate the two quantities:

| input | what it attacks | R1 | every other rung |
|---|---|---|---|
| `adversarial-count` | the declared count, `5*4096 > 200` | returns 0 | returns 0 |
| `adversarial-overflow` | the push guard, 96 pushes into 64 slots | drops 32, pops 64 | identical |
| `adversarial-underflow` | **the pop guard**, POP as operation 0 | **reads `stack[-1]`** | no-op, correct |
| `adversarial-allpop` | the pop guard, 200 times | **walks 1600 B down the stack** | returns `nops` |

The first two are controls: they attack checks that R1 *has*, and every cell
agrees on them. The last two are the bug.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == stack_fold(buf, off, len)
```

`stack_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of the
kernel calls to prove that it does. `nops`, all 2^32 values of it, and every byte
of the window are *arguments* of the problem; the kernel is total in all of them.

**It is ONE clause, and both of p11's and p17's second ones are deliberately
absent.** p17 needed `buf_len <= 9223372036854775807` because it cast to `i64`;
p11 needed the same fact for its cursor step `p = q + 1` and bought it with a
program change. p03 needs neither, and the reason is arithmetic rather than
virtue: every index this kernel forms is `off + 4 + 5*k` with
`5*k < 5*nops <= len - 4`, so the largest address it computes is bounded by
`off + len`, which the structural `requires` already bounds by `buf@.len()`.
The length check every rung carries is what makes that total. **p03's hard
obligation is somewhere else entirely and it is `sp <= STACK_CAP`, maintained
across a branch the file chooses.** NOTES.md 5.

### What the `ensures` is, and what it is not — p03 is p16's case, not p17's

p16's `spec.md` says, correctly for p16, that a read-only kernel's `ensures`
cannot be its security property, because "no byte outside the window was read"
is not a property of the return value; the trusted accessors' discharged
`requires` are what carry the safety claim. **p03 is that case, with a
difference worth naming**: the address that goes out of range is **not in the
buffer at all**, it is on the stack, so the accessor whose precondition excludes
it is `stack_get_unchecked`'s `i < v@.len()` and not the slice one every earlier
pattern relies on.

**And there is a second thing the `ensures` deliberately does not say: that the
opcode stream is well bracketed.** `run` in `verus.rs` specifies what the
*program* does — take each guard or do not, exactly as the exec code does — so
`adversarial-underflow.bin` and `adversarial-allpop.bin` are inside the verified
domain and every checked rung agrees with `model.py` on both. Writing the
stronger postcondition would have forced a `requires` about the contents of a
file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it
would have deleted the rows that are the pattern.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p03's payload is p16's, p17's, p05's, p07's and
p11's:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — the functions p16 added to `common/`, reused verbatim,
with **nothing added to `common/` for p03**. All three are a bulk copy rather
than an element-by-element decode, which is what keeps every p03 row
Miri-checkable.

Nothing is a compile-time constant except `STACK_CAP`, which is the array's
size and is in every rung: `n_iters`, `stride`, `n_blob`, every `nops`, every op
byte and every value come from the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across, exactly as for p16, p17, p05, p07 and p11.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below. It is **p11's, unchanged**:
`stride_w >= 4` because p03's window header is the 4-byte `nops` field, and two
conjuncts rather than p17's three because p03's kernel needs no
`buf_len <= isize::MAX` fact (see "Contract").

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

The comparison is in `u64` *before* the `as usize` cast, so a truncating driver
cannot sneak a 2^40 stride past it. (Unchanged from p16, p17, p05, p07 and p11,
and still load-bearing.)

### Why this does not evaporate

Same mechanism as p01, p02, p16, p17, p05, p07 and p11: `k` is derived from
`acc`, and `acc` from the previous call's result, so call *i+1* cannot begin
until call *i* has returned. Nothing to CSE, nothing to hoist, no `black_box`
and no `asm volatile` — the same arithmetic in both languages, so neither gets a
stronger barrier than the other. `k = (acc * nwin) >> 64` is Lemire's map onto
`[0, nwin)`; see p01's `spec.md` for why it is a multiply-shift and not a
modulo.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically. p03 has a second, sharper reason than the
earlier patterns: **the address that goes out of range is on the stack**, so a
stray POP in a *middle* window is just as much a memory error as one in window 0
— but the value it reads, and therefore the checksum, depends on stack garbage.
With `nwin == 1`, `k` is always 0 and the gate records one behaviour per cell
rather than a mixture.

The related trap, from p17 and non-obvious: **window 0 must serve something**,
because a window returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is
then 0 for ever — the driver's Lemire index has an absorbing state at
`acc == 0`. Here a window can return 0 only by failing the length check, which
is exactly and only what `adversarial-count.bin` does, and that file has one
window so `k` is 0 regardless. `inputs/gen.py` records both constraints.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.aliases` cannot reconcile that
— both sides of an alias are a dotted identifier path, so an alias renames and
can do nothing else. `driver.call_args` declares which argument *positions* of a
named call are the canonical ones (`{"c": {"kernel": [0, 2, 3]}}`), and
`harness/dloop.py` refuses to drop anything that is not a single bare
identifier, so no prefetch, no side effect and no extra statement can hide in
the argument the diff stops looking at.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts,
because a declared number a reviewer cannot check from `spec.md` alone is
exactly what `.memory/02-bench-rules.md` forbids.

| pin | why |
|---|---|
| `verus.obligations` = 9 | **`STACK_CAP` 1 + `run` 1 + `kernel` 2 + `main` 5 = 9.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained, and the zero terms are checkable the same way: `u32_at`, `nops_at`, `zero_stack` and `stack_fold` are non-recursive spec fns and report **0**; the five `external_body` items report **0**; `run` is the one *recursive* spec fn and carries one termination query. **`STACK_CAP`'s 1 is a `const` inside `verus!`**, which `.memory/04-verus.md` records as its own query (measured on p08's `SCR`) — p03 is the second pattern to have one and the first since. `kernel`'s 2 is 1 body + 1 loop body, and that is p03's contrast with p11's 4 (three loops) and p05's 5 (two loops plus two `by (nonlinear_arith)` sub-proofs): **p03 has ONE loop and zero nonlinear arithmetic**, which is exactly why the surviving cost is interesting — the obligation is hard for LLVM and trivial for Z3. **`main`'s 5 does not decompose further from the command line and is quoted as measured**: the by-block rule of thumb would predict 6 and Verus reports 5, the identical off-by-one p05's, p17's, p07's and p11's `spec.md` record for the identical driver. `.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop rule gives **8** here and is therefore not the derivation. |
| `verus.twin_obligations` = 12 | the count in the **other** configuration, `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. **9 shipped + 3**, one per twin, and each is measured the same way: `--cfg slb_twin --verify-function slb_twin_<name> --verify-root` reports `1 verified` — one function, no loop body, no `by`-block. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. **p03 is the first pattern with more than one trusted `unsafe` item**, so it is the first whose twin count moves by more than 1. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item, because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`. `check.py` derives this from `verus.rs` rather than reading the flag. p03 has a second reason and it is the strongest in the project so far: **one of its trusted items WRITES**, so an incomplete `ensures` there could hide a store rather than a load. |
| `verus.unsafe_justifications` | one entry, `stack_set_unchecked`'s `x`. `.memory/04-verus.md` names the parameter-coverage rule's one documented false positive — *"a pure value parameter (`fn write(dst, i, v)` — `v` is written, never used as an address) genuinely needs no precondition"* — and records that **nothing in the tree exercises it**. p03 is the first pattern that does, because it is the first with a trusted item that stores a caller-supplied value. The gate `rep.block`s the justification and shouts it on every run. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == stack_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (stack_fold). p03 is p16's, p05's, p07's and p11's shape and NOT p17's: the harm is an ordinary out-of-range read, so a discharged accessor precondition is the security property and the `ensures` is what keeps the proof non-vacuous and pins WHICH values the answer is a function of. But note the difference from all four: **the address that goes out of range is NOT IN THE BUFFER**, it is 8 bytes below a 512-byte local array on the stack, so the precondition that excludes it is `stack_get_unchecked`'s `i < v@.len()` on a `[u64; 64]` and not the slice accessor every earlier pattern relies on. There is no 'inside the buffer but outside the window' band here for the ensures to be the only guard against. **What the `ensures` deliberately does NOT say is that the opcode stream is well bracketed** -- `run` specifies what the PROGRAM does, take each guard or do not, so adversarial-underflow.bin and adversarial-allpop.bin are INSIDE the verified domain and every checked rung agrees with model.py on both. A `requires` that the stream never pops an empty stack would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete the two rows that are the pattern.",
  "idiom": {
    "required": [
      {
        "c": "THE PUSH GUARD, present in every rung including R1: `if (sp < STACK_CAP) {` in both C rungs.",
        "rust": "THE PUSH GUARD, present in every rung: `if sp < STACK_CAP {` in all four Rust rungs."
      },
      {
        "c": "THE POP GUARD: `if (sp > 0) {` in c/kernel_hardened.c. c/kernel.c omits it and omits NOTHING ELSE, which IS the bug -- so the one scoped-absent pair this declaration reports is on that rung and is correct.",
        "rust": "THE POP GUARD: `if sp > 0 {` in all four Rust rungs."
      },
      {
        "c": "the stack is a fixed-size LOCAL array, not a heap allocation and not growable: `uint64_t stack[STACK_CAP];` in both C rungs.",
        "rust": "the stack is a fixed-size LOCAL array, never a growable one: `let mut stack: [u64; STACK_CAP] = [0; STACK_CAP];` in all four Rust rungs."
      },
      {
        "c": "the declared count is bounded by the window before the loop, in 64-bit arithmetic, in EVERY rung: `if (5 * (uint64_t)nops > (uint64_t)(len - 4))` in both C rungs.",
        "rust": "the declared count is bounded by the window before the loop, in 64-bit arithmetic, in EVERY rung: `if 5 * (nops as u64) > (len - 4) as u64 {` in all four Rust rungs."
      },
      {
        "c": "the per-operation dispatch is a REAL BRANCH on the attacker's op byte and not a branchless select: `if (op == 0) {` in both C rungs.",
        "rust": "the per-operation dispatch is a REAL BRANCH on the attacker's op byte and not a branchless select: `if op == 0 {` in all four Rust rungs."
      },
      "the stack pointer is decremented BEFORE the slot is read, so that every read is of the slot the pointer names and no rung indexes one below it: `sp = sp - 1;` in all six rungs.",
      "and incremented AFTER the slot is written: `sp = sp + 1;` in all six rungs.",
      "the little-endian u32 decodes are written out with + and * rather than | and <<, so they stay linear arithmetic: `+ 65536 *` in all six rungs.",
      "...and their top bytes: `+ 16777216 *` in all six rungs.",
      {
        "c": "the final stack depth and the declared count are both folded into the result, so a rung that ended at a different depth or ran a different number of operations cannot produce the same checksum: `(acc * 31 + (uint64_t)sp) * 31 + (uint64_t)nops` in both C rungs.",
        "rust": "the final stack depth and the declared count are both folded into the result, so a rung that ended at a different depth or ran a different number of operations cannot produce the same checksum: `.wrapping_add(sp as u64).wrapping_mul(31)` and `.wrapping_add(nops as u64)` in all four Rust rungs."
      }
    ],
    "forbidden": [
      "`from_le_bytes`",
      "`& (STACK_CAP - 1)`",
      "`MaybeUninit`",
      "`.push(`",
      "`.pop(`"
    ],
    "why": "each deletes something this pattern IS, and a rung that does it is a different benchmark whose numbers are not comparable (this file's second sentence). THE OPERATION SEQUENCE IS IN THE FILE, AND BOTH GUARDS ARE THE PROGRAM: `if sp < STACK_CAP` on the push and `if sp > 0` on the pop are not bounds checks a compiler inserted, they are the kernel's semantics, and exactly one of them -- the pop's -- is absent from `c/kernel.c` and present everywhere else. That single scoped-absent pair IS the bug, and it is the one this declaration exists to report. `adversarial-overflow.bin` and `adversarial-count.bin` are the controls that make it a measurement rather than a claim about the source: they attack the push guard and the length check, both of which R1 HAS, and all eight cells agree on both. THE PER-OPERATION DISPATCH IS A REAL BRANCH: `if op == 0` is pinned literally because a rung that lowered it to a branchless select would delete the branch-predictability axis `sweep-bpred`/`sweep-brand` exist for, and because p07 measured LLVM's X86CmovConverterPass doing the OPPOSITE transformation unasked, so this is a thing to check on the disassembly (NOTES.md 1) rather than to assume. THE STACK IS A FIXED-SIZE LOCAL ARRAY: `[u64; STACK_CAP]` / `uint64_t stack[STACK_CAP]`. A `Vec` with `.push(`/`.pop(` moves the pattern to allocator behaviour, which is p02's axis and not this one, and it deletes the explicit `sp` that the result folds and that the proof's invariant is about -- so both method names are `forbidden`. MASKING IS FORBIDDEN: `stack[sp & (STACK_CAP - 1)]` removes 1.00000 of the surviving check's 3.00000 Ir (NOTES.md 4d) and is not the same program, because it silently turns an out-of-range access into an in-range one, which is the opposite of what this pattern models. `MaybeUninit` is forbidden for a reason that runs the other way and is worth stating because it makes the Rust rungs DEARER: all four write `[0u64; STACK_CAP]` since safe Rust has no uninitialised array, and C's is not initialised, so that per-call memset is a LANGUAGE difference which NOTES.md 3c prices separately -- letting the unsafe rung alone skip it would open an R4-vs-R3 gap that is not a safety gap and that no safe rung could close. `from_le_bytes` deletes the written-out little-endian decode every rung shares AND is NOT AVAILABLE TO AN R4 AT ALL at the pinned vstd (`from_le_bytes` and the `try_into`/`TryFromSliceError` route to it are both `is not supported`, measured on p05 and p16 at TASK_027_REVIEW), so a rung using it would compare a safe cell against an unsafe cell that cannot exist -- the `identity`-pin trap this block's own `identity` key sets. WHAT IS DELIBERATELY *NOT* PINNED, and it is the point of the pattern: **the ACCESS spelling**. R2 and R3 index `stack[sp]`, R4 and R5 call `get_unchecked`, and holding those fixed would hold fixed the one thing p03 exists to compare. Nor is the opcode-stream cursor pinned: `w[4 + 5*k]` and `w[4..4 + 5*nops].chunks_exact(5)` are both in contract and NOTES.md 10a measures both, which is what makes the R3-side span a search rather than an assertion. WHEN THIS DECLARATION WAS WRITTEN, stated exactly because p11's could claim something stronger and p03's cannot: it was written AFTER the phase-0 probe of NOTES.md 0 and BEFORE any rung existed. What was known when it was written is the whole of NOTES.md 0 -- the underflow's address arithmetic, that STACK_CAP=64 keeps the array real, that a 5-byte op dominates the per-call constant, and probe figures for six candidate spellings including 3.00000 Ir per executed pop. What was NOT known is any figure in NOTES.md 3, 4, 10 or 11, because no rung, no input file and no `model.py` existed yet. TASK_036 required that probe before five rungs were built on the sizes, so this is a consequence of the task and not a choice; recording it is the only honest thing available, and `.memory/01-ladder.md`'s direction test is what a reviewer should apply to every entry above. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
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
      "verus.rs": 9
    },
    "twin_obligations": {
      "verus.rs": 12
    },
    "obligations_note": "9 = STACK_CAP 1 + run 1 + kernel 2 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. u32_at, nops_at, zero_stack and stack_fold are NON-RECURSIVE spec fns and carry 0; buf_get_unchecked, stack_get_unchecked, stack_set_unchecked, load_input and emit are external_body and carry 0; run is the one RECURSIVE spec fn and carries one termination query. STACK_CAP's 1 is a `const` inside verus!, which .memory/04-verus.md records as its own query (measured on p08's SCR); p03 is the second pattern to have one. kernel's 2 = body + ONE loop body, which is p03's contrast with p11's 4 (three loops) and p05's 5 (two loops plus two `by (nonlinear_arith)` sub-proofs): p03 has one loop and ZERO nonlinear arithmetic, which is exactly what makes the surviving 3.00000 Ir interesting -- the obligation is hard for LLVM and trivial for Z3. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per by-block would predict 6 and Verus reports 5, the identical off-by-one p05's, p17's, p07's and p11's spec.md record for the identical driver. .memory/04-verus.md's one-per-function-plus-one-per-loop rule of thumb gives 8 here and is therefore not the derivation.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 9 shipped + 3, one per twin, each measured the same way: `--cfg slb_twin --verify-function slb_twin_<name> --verify-root` reports `1 verified` -- one function, no loop body, no `by`-block. p03 is the FIRST pattern in this project with more than one trusted `unsafe` item, so it is the first whose twin count moves by more than 1, and pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body or an item that exists only under the cfg.",
    "unsafe_justifications": {
      "verus.rs": {
        "stack_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `u64` is a legal thing to store in a `u64` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [u64; 64]` reads `i < 64`. (A draft carried a second conjunct `old(v)@.len() == 64`; the gate refused it as a TAUTOLOGY -- vstd's `array_len_matches_n` discharges it from the parameter type alone -- and stage 5c-twin's PER-CONJUNCT deletion probe independently showed the twin never used it. NOTES.md 5b records both, because a tautological conjunct on a TRUSTED item is the shape .memory/04-verus.md warns about and neither Verus run moved: 9/0 and 12/0 with it and without it.) This is the one documented false positive of stage 5a's parameter-coverage rule (.memory/04-verus.md: *a pure value parameter -- `fn write(dst, i, v)`, `v` is written, never used as an address -- genuinely needs no precondition*), and .memory records that NOTHING IN THE TREE EXERCISES IT. p03 is the first pattern that does, because it is the first with a trusted item that stores a caller-supplied value. What still guards the store is the `ensures` `final(v)@ == old(v)@.update(i as int, x)`, which is a WHOLE-SEQUENCE equality: it says both that slot `i` became `x` and that nothing else moved, so an implementation that wrote a second slot would contradict it. NOTES.md 5b's SLB-TRUSTED-ARGUMENT (b) is the human reading of that."
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
        "zero_stack": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "stack_fold": {
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
        "stack_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_stack_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "stack_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_stack_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
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
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == stack_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 1189 on small and 4154 on large -- p16's, p05's and p11's denomination. Every byte of a well-formed p03 window is read exactly once: the 4 header bytes as a u32, then the op byte and the four value bytes of each operation. WHICH WAY THE ESTIMATE ERRS: STRICT on every input this pattern ships, and by ONE term rather than two -- a POP operation reads its op byte and does NOT read its four value bytes, because both LLVM and gcc sink that load into the push arm (checked on the disassembly, NOTES.md 0, before this file was written). So a window whose ops are all POPs visits `4 + nops` bytes where `stride` counts `4 + 5*nops`. The over-count is bounded by the pop density, 50% on small and 25% on large, so `stride` is at most 2x the byte-visit count and the derived floor is one the kernel must clear -- it can never let a collapsed kernel through, which is the only direction that matters. work_unit_bits is 8, one window byte, so the effective absolute bound under min_ir_per_work is 0.001953125 x 8 = 0.015625. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged, and the argument for it is the easiest of any pattern so far: p03's inner loop is a data-dependent two-way branch on an attacker byte followed by a serial dependence through `sp` and `acc`, so there is no vector form at any -march -- operation k+1 cannot be decoded into the right arm until operation k's effect on `sp` is known. The measured rate is 12.50 Ir per 5-byte operation on the unsafe rung, i.e. 2.50 Ir/byte, 10x the floor. The two probe inputs differ in work_per_call (1189 vs 4154) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the first kernel in this project whose CONTROL FLOW is attacker-chosen -- the file decides per step which of two updates `sp` gets, so the memory-safety obligation `sp <= STACK_CAP` is a loop invariant over a branch the input picks. The byte-identity result now also covers a kernel with THREE trusted accessors rather than one, one of which WRITES through an unchecked index into a fixed-size array, and a spec function that threads a whole `Seq<u64>` of machine state rather than a scalar accumulator. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p03 there is a second reason and it is the strongest in the project so far: **one of the three trusted items WRITES**, so an incomplete `ensures` on `stack_set_unchecked` could hide a store rather than a load, and a store past the array end would corrupt the frame rather than merely read it. A third: the unchecked index is `sp`, which is a function of the OP STREAM rather than of a header field, so an off-by-one in a guard would show up on some op sequences and not others rather than as a fixed shift the way p16's and p17's would. Cost: check.py rewrites n_iters to 4, so each row reads 4 x stride bytes -- 4756 on small and 16 616 on large, ~180x inside `.memory/02-bench-rules.md`'s measured 3.05 M budget. The only real cost is the 8.3 MB payload to_vec, and p07's 12 MB one passes.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |

There is no exit 7 here, for p16's, p17's, p05's, p07's and p11's reason: p03's
payload names no allocation size, so p02's `SLB_MAX_CAP` check would be dead
code.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header; a stride above `n_blob` leaves no whole
window, so `nwin` would be 0 and `k` would have nothing to index. Either way the
loop is skipped and the driver prints `0` after **zero** kernel calls. p03 ships
no input for it — p11's `adversarial-stride3.bin` covers the identical driver
and the identical guard, and duplicating it here would add a matrix row that
tests the driver rather than the kernel.

`adversarial-count.bin` is the kernel's own version of the same thing and it is
a **control**: `nops` is 4096 against a window that holds 40 operations, so
`5*nops = 20480 > avail = 200` and every rung — R1 included — returns 0 after
reading the header and nothing else. A checksum of 0 is a weak oracle, and this
row is here for the *behaviour* and *sanitiser* tables rather than for its
value: it is the input that would fire ASan in R1 if the missing check were the
length one, and it does not.

`adversarial-overflow.bin` is the other control. 96 pushes into a 64-slot array,
then exactly 64 pops: the push guard drops 32 values in **every** rung, and the
drain stops at `sp == 0` so R1's missing guard is never reached. All eight cells
print the same checksum. Between the two, the only guard left as a variable is
the pop's — which is what makes "R1 omits exactly one line" a measurement.

`adversarial-underflow.bin` and `adversarial-allpop.bin` are the bug, and they
are two different harms rather than two spellings of one. The first pops once at
`sp == 0`, which sets `sp = SIZE_MAX` and thereby **disables the stack for the
rest of the call** — every later PUSH fails `sp < STACK_CAP`. The second does it
200 times and walks one 8-byte slot further down the stack each time. Both read
inside the process's own stack; NOTES.md 7 records that R1's answer on them is
**not reproducible across runs** and becomes bit-stable under `setarch
--addr-no-randomize`, i.e. what the checksum discloses is derived from a stack
address.

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark. It is kept anyway so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition
— would be a precondition about the driver's own guard rather than about the
buffer. NOTES.md 9 records that it is dead and why it stays. The `nops == 0`
guard is *not* dead in the same way: it is reachable from the wire format, and
no shipped input takes it.
