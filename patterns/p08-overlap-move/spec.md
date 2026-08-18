# p08 — overlapping move: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

p05's, deliberately. Four C arguments against three Rust ones, carrying exactly
the same information: `&[u8]` is a pointer and a length and C spells the pair
out. Both C cells take `buf_len` and ignore it, which keeps the calling
convention, the argument count and the register allocation fixed between R1 and
R1h so that the *only* difference between those two cells is one token.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..2    d       u16 LE    the SHIFT DISTANCE      ATTACKER DATA
byte 2..4    nrep_w  u16 LE    the LAYER COUNT         ATTACKER DATA
byte 4..     data    u8[]
data_start = 4 ;  avail = len - 4                      what ACTUALLY arrived
```

## Semantics

```
SCR = 4096                                  # capacity, a compile-time constant

if len < 4:                        return 0
d, nrep_w from the header
avail = len - 4
m     = min(avail, SCR)
nrep  = 1 + (nrep_w % 4)                    # 1..=4, a MASK, not a check

# The bounds guard. EVERY rung has this, R1 included.
if m < 2 || d == 0 || d + nrep > m:  return 0

scr[0..SCR] = 0                             # see "The scratch buffer"
scr[0..m]   = buf[off+4 .. off+4+m]

for r in 0 .. nrep:
    dr = d + r
    # >>> THE OPERATION. R1 spells this memcpy; every other rung memmove. <<<
    move_right(scr, dr, m)                  # scr[dr..m] <- scr[0..m-dr]

acc = 0
for j in 0 .. m: acc = acc *64 31 +64 scr[j]
return acc *64 31 +64 (m as u64)
```

`*64`/`+64` are wrapping, as in p01/p02/p16/p17/p05, so the kernel has **no
precondition on values** and every measured input is inside the verified domain
by construction. C's unsigned types wrap by definition (6.2.5p9) and the Rust
rungs write `wrapping_add`/`wrapping_mul`.

### This is not a bounds bug, and that is the whole point

**Every result this project has produced so far is about a bounds check.**
p01/p02/p16/p05 price one; p17 shows one cannot save you. p08 is the case where
Rust wins *structurally*, for a reason that is not a runtime check at all:

- the C program is undefined whenever `2*dr < m`, and `d` comes from the file;
- **safe Rust cannot express it.** `memcpy(scr + dr, scr, m - dr)` needs a
  `&[u8]` and a `&mut [u8]` into one buffer at the same time and the borrow
  checker rejects that *at compile time* (`E0502`), with no runtime cost to
  measure because there is no runtime check. The only safe spelling of an
  in-place shift is `copy_within`, which is `memmove` semantics, i.e. correct by
  construction;
- **unsafe Rust re-opens it**, exactly and only via `ptr::copy_nonoverlapping`,
  whose entire safety contract is the non-overlap;
- and at R5 a `requires` rules it out — except that `ptr::copy` *is* `memmove`,
  so there is no non-overlap precondition to state, and the C bug turns out to
  be **inexpressible in the specification logic too**: a `spec fn` is a function
  of the whole input sequence, so "read a byte you already overwrote" has no
  spelling in it.

So `nrep`, `d` and `m` are all attacker data, the bounds guard is identical in
all six rungs, and **R1 and R1h differ by exactly one token**: `memcpy` vs
`memmove`.

### Load-bearing, do not "improve"

**The authoritative copy of this list — and of "The scratch buffer" below — is
the `idiom` key in the `slb-contract` block**, which is hashed into
`contract_sha256`. What follows is the same statement in prose, with the
arguments; if the two ever disagree, the block wins and the prose is the bug.
Edit both or neither (TASK_016_REVIEW m2).

- **`dr = d + r`, not a fixed `d`.** With a fixed `d` and `d >= m/2` the rounds
  after the first are *no-ops* — the checksum would stop depending on `nrep`, a
  rung that skipped rounds 2..n would still pass, and LLVM would be free to
  eliminate them. Varying `dr` makes every round change the buffer. The
  realistic reading is nested framing headers of different lengths.
- **The guard is `d + nrep > m`, checked once**, so every `dr` is in range and
  no rung needs a per-round check. Do not push it into the loop.
- **Nothing is written into the space the move opens.** A real encoder writes
  the header bytes there; that is a second bounded loop and adds nothing to the
  aliasing axis. It is omitted deliberately, and this sentence is the record of
  the omission.
- **`nrep_w % 4`, not `nrep_w & 3`.** The same function on unsigned values and
  the same instruction (`and $0x3`) out of gcc, clang and rustc — but `%` is
  linear arithmetic and `&` drags in `by (bit_vector)`.
  `.memory/04-verus.md` blesses this trade explicitly for the `+`-vs-`|`
  little-endian decode: *choosing the spelling that is cheaper to prove is fine;
  choosing a weaker specification is not.* The specification is identical.
- **`m = min(avail, SCR)`.** `avail` comes from the file, and every shipped
  input has `avail < SCR`, so `m` is attacker data on every measured call and
  nothing is constant-folded. The clamp exists so the kernel is *total*: a
  window bigger than the scratch is not an error, it is a truncation.

### The scratch buffer

`scr` is a **fixed `SCR = 4096` byte array local to the kernel**, in all six
rungs (`uint8_t scr[4096]` / `[0u8; 4096]`). It is *not* a driver-owned `&mut`
argument, and that is a harness fact rather than a taste call: `driver.call_args`
refuses to drop anything that is not a single bare identifier, so C's `scr` and
Rust's `&mut scr` cannot be reconciled by the driver diff (`harness/dloop.py`),
and making them so would be a `harness/` change.

**It is zero-initialised in every rung, C included.** Safe Rust cannot construct
`[u8; 4096]` any other way; making C match keeps the memset a uniform per-call
constant that cancels in every rung-to-rung comparison. `NOTES.md` §2 reports
the memset's measured share of per-call `Ir`.

Consequence, stated plainly: **p08 has no cache axis in the scratch.** The
working set is 4 KiB in every cell of the matrix. `small` and `large` differ in
`m`, in `d`'s residue, and in *blob* size — the copy-in reads a pseudo-random
window out of the blob, so locality lives there and nowhere else.

### The perf inputs must NOT overlap, and this is the design

The move's source `[0, m-dr)` and destination `[dr, m)` overlap exactly when
`2*dr < m`. **On `small` and `large`, `d = ceil(m/2)` (bumped to the next
residue class where needed), so no round overlaps** — `memcpy` and `memmove`
agree, every rung produces the same checksum, and the perf rows compare like
with like. `adversarial-overlap` is where `d = 3`, the ranges overlap by more
than 4 KiB, and R1 executes the undefined behaviour.

This is not dodging the bug, it is the point: the overlap is
**attacker-controlled**, because `d` comes from the file.

It also protects the measurement. The driver's `k = (acc * nwin) >> 64` is
derived from the previous result, so **a rung whose checksum diverged would
visit different windows** and stop being comparable. Adversarial inputs are
exactly one window (`nwin == 1`, `k == 0` always), so divergence there is
harmless — the existing "exactly one window" rule doing a second job.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == shift_fold(buf, off, len)
```

`shift_fold` is the spec function; `model.py` is its independent Python twin.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included, and `harness/check.py` evaluates it at every one of
the kernel calls to prove that it does. `d` and `nrep_w`, all 2^32 pairs of
them, are *arguments* of the problem; the kernel is total in all of them.

### What the `ensures` is, and what it is not

p08 is neither p16's case nor p17's.

p16 and p05 are patterns where the harm is an out-of-bounds access, so the
trusted accessor's discharged `requires` is the security property and the
`ensures` only keeps the proof honest. p17 is the pattern where the harm was
memory-*safe* and only the functional `ensures` could exclude it.

**p08 is the case where the trusted `ensures` itself is the security
property**, and it is the first. `move_right`'s three conjuncts say what the
move did *and what it did not touch*; a one-conjunct version that said only "the
moved range is right" would verify, would pass every mechanical check the gate
has, and would be an axiom that `ptr::copy` may scribble anywhere outside
`[dr, m)`. The kernel-level `ensures` then pins the composition of the rounds,
which is what makes `nrep` meaningful. `NOTES.md` §4 has the argument per
conjunct and §6 the mutants that show each is load-bearing.

**Three conjuncts, not four**, and the fourth was tried and removed on a
measurement rather than on taste. A move contract usually carries
`final(v)@.len() == old(v)@.len()`; with it present gate step 5c reports
*"`move_right` ensures[0] is NOT load-bearing: deleting `final(v)@.len() ==
old(v)@.len()` still gives 11 verified, 0 errors"*. The only caller passes
`&mut scr` where `scr` is a `[u8; SCR]`, so Verus knows the length from the
array's type through the unsizing coercion whatever the contract says. A trusted
`ensures` nothing depends on is an unchecked claim about real Rust semantics
carried for free (`.memory/04-verus.md`), so it is gone. `NOTES.md` §4.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p08's payload is p16's, p17's and p05's:

```
word 0     u64  stride      # bytes per window; the kernel folds one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — the functions p16 added to `common/`, reused verbatim,
with **nothing added to `common/` for p08**. All three are a bulk copy rather
than an element-by-element decode, which is what keeps every p08 row
Miri-checkable.

Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob` and every `d`
and `nrep_w` come from the file. `SCR` is a *capacity*, like p02's destination
buffer, and the measured length `m = min(avail, SCR)` is file-derived on every
shipped input.

**There is no `cap` and nothing is allocated from an attacker-controlled size**
— the scratch is a fixed local array — so p02's `SLB_MAX_CAP` range check and
its exit 7 have no analogue here and are deliberately not copied across, exactly
as for p16, p17 and p05.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers, and **character-identical to p05's and p17's**.
`harness/check.py` normalises every copy — the C one included — and diffs it
against `driver.canonical` below.

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

`stride_w >= 4` because p08's window header is the 4-byte `d`/`nrep_w` pair.
`adversarial-stride3.bin` attacks it. The comparison is in `u64` *before* the
`as usize` cast, so a truncating driver cannot sneak a 2^40 stride past it.

### Why this does not evaporate

Same mechanism as p01, p02, p16, p17 and p05: `k` is derived from `acc`, and
`acc` from the previous call's result, so call *i+1* cannot begin until call *i*
has returned. Nothing to CSE, nothing to hoist, no `black_box` and no
`asm volatile` — the same arithmetic in both languages, so neither gets a
stronger barrier than the other. `k = (acc * nwin) >> 64` is Lemire's map onto
`[0, nwin)`.

### Why every adversarial input is exactly one window

`k` is pseudo-random over `[0, nwin)`, so with several windows a malformed one
would be hit only probabilistically. With `nwin == 1`, `k` is always 0 and `off`
is always 0, so `adversarial-overlap`'s undefined `memcpy` is executed
deterministically on every call.

The related trap, from p17 and non-obvious: **window 0 must serve something** on
any input where anything is meant to be visited, because a window returning 0
pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever — the driver's
Lemire index has an absorbing state at `acc == 0`. On `small` and `large` every
window holds a well-formed shift, so this is satisfied by construction.

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
when the tree stops matching it. What is worth saying here is the arithmetic
behind the two obligation counts, because a declared number a reviewer cannot
check from `spec.md` alone is exactly what `.memory/02-bench-rules.md` forbids.

| pin | why |
|---|---|
| `verus.obligations` = 11 | **`SCR` 1 + `shift_rounds` 1 + `fold_scr` 1 + `kernel` 3 + `main` 5 = 11.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, and so are the seven zero terms: `d_at`, `nrepw_at`, `init_scr`, `shift_round` and `shift_fold` are non-recursive spec fns and report **0**; `move_right`, `copy_in`, `load_input` and `emit` are `external_body` and report **0**; the two *recursive* spec fns carry one termination query each. `kernel`'s 3 is 1 body + 1 per loop body (two loops) and it has no `by`-block. **The `SCR` term is new to this project and is why `.memory/04-verus.md`'s rule of thumb misses here: a `const` item inside `verus!` is its own Verus query.** Measured two ways — `--verify-function SCR --verify-root` reports `1 verified`, and adding a second unrelated `const` to a mirror copy takes the file from 11 to 12. **`main`'s 5 is quoted AS MEASURED** and does not decompose from the command line: body + driver loop + one per `by`-block would predict 6 and Verus reports 5, exactly as on p05 and p17, whose drivers are character-identical to this one. |
| `verus.twin_obligations` = 15 | the count in the **other** configuration, `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. **11 shipped + 2 + 2**, and both 2s are measured the same way: `--cfg slb_twin --verify-function slb_twin_move_right --verify-root` reports `2 verified` and `slb_twin_copy_in` reports `2` — one function body plus one loop body each. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item, because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`. On p08 there is a second reason and it is the sharper one: **Miri's stacked/tree-borrows model is the only tool in this project's box that can see an *aliasing* violation**, and `controls/gen_controls.py` points it at one. `check.py` derives the flag from `verus.rs` rather than reading it. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": ["off + len <= buf_len"],
  "ensures": ["result == shift_fold(buf, off, len)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (shift_fold). p08 is NEITHER p16's shape NOR p17's: the harm is not an out-of-bounds access -- the guard `d + nrep > m` is present in EVERY rung, R1 included, and nothing leaves any allocation -- and it is not a memory-safe read of the wrong bytes either. It is UB with no spatial component: an overlapping memcpy, whose harm is silent corruption inside a buffer the program owns. The trusted item's THREE ensures conjuncts are the security property here, because they are what says the move did not touch the two regions outside [dr, m). See the prose above.",

  "idiom": {
    "required": [
      "R1 spells the move memcpy and R1h memmove -- that one token is the whole difference between them",
      "R2 shifts element-by-element in a backward loop, R3 uses copy_within, R4/R5 use core::ptr::copy; R2 and R3 differ in the body of move_right and in nothing else",
      "the bounds guard `m < 2 || d == 0 || d + nrep > m` is checked ONCE, outside the round loop, in every rung including R1",
      "dr = d + r, not a fixed d",
      "nrep = 1 + (nrep_w % 4), a mask and not a check, written `%` and not `&`",
      "scr is a fixed SCR = 4096 byte array LOCAL to the kernel in all six rungs, zero-initialised in all six, and m = min(avail, SCR)"
    ],
    "forbidden": [
      "a per-round bounds check -- do not push the guard into the loop",
      "`nrep_w & 3`",
      "a driver-owned &mut scratch argument",
      "writing anything into the space the move opens"
    ],
    "why": "p08's result is that one token (memcpy vs memmove) is the whole bug and that safe Rust cannot express it, so a rung that spells the move differently is not a rung of p08. A fixed d makes every round after the first a no-op, the checksum stops depending on nrep, and LLVM is free to delete the rounds. `&` is the same instruction as `%` on unsigned values but drags `by (bit_vector)` into R5 -- a cheaper proof of an identical specification, which `.memory/04-verus.md` blesses. The scratch must be kernel-local because `driver.call_args` refuses to drop anything that is not a single bare identifier, so C's `scr` and Rust's `&mut scr` cannot be reconciled by the driver diff; making them so would be a harness/ change, and the zero-init keeps the memset a uniform per-call constant that cancels in every rung-to-rung comparison. Writing header bytes into the opened space is a second bounded loop that adds nothing to the aliasing axis. RESTATED in this hashed block at TASK_016 from the prose sections 'Load-bearing, do not improve' and 'The scratch buffer' above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). Whoever edits one edits the other. TASK_016 did not measure a spelling spread for p08 and none is claimed here."
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
    "obligations": {"verus.rs": 11},
    "twin_obligations": {"verus.rs": 15},
    "obligations_note": "11 = SCR 1 + shift_rounds 1 + fold_scr 1 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. d_at, nrepw_at, init_scr, shift_round and shift_fold are non-recursive spec fns and carry 0; move_right, copy_in, load_input and emit are external_body and carry 0; shift_rounds and fold_scr are recursive and carry one termination query each; kernel's 3 = body + 2 loop bodies, no `by`-block. **The SCR term is new: a `const` item inside `verus!` is its own Verus query**, which `.memory/04-verus.md`'s rule of thumb does not mention because no earlier pattern declared one. Measured two ways: `--verify-function SCR --verify-root` reports `1 verified`, and adding a second unrelated const to a mirror copy of this file takes it from 11 to 12. main's 5 is quoted AS MEASURED and does not decompose from the command line: body + driver loop + one per `by`-block would predict 6 and Verus reports 5, the same off-by-one p05 and p17 report for a character-identical driver.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 11 shipped + 2 + 2. Both 2s are measured: `--cfg slb_twin --verify-function slb_twin_move_right --verify-root` reports `2 verified` and `--verify-function slb_twin_copy_in` reports `2 verified` -- one function body plus one loop body each, because unlike every earlier pattern's twin these are not one-liners. Pinned rather than merely required to rise: `tw > base` only says something extra compiled, and a twin that quietly lost its body, or an item that exists only under the cfg, moves this number and nothing else.",
    "items": {
      "verus.rs": {
        "d_at":        {"external": null, "requires": [], "ensures": []},
        "nrepw_at":    {"external": null, "requires": [], "ensures": []},
        "init_scr":    {"external": null, "requires": [], "ensures": []},
        "shift_round": {"external": null, "requires": [], "ensures": []},
        "shift_rounds":{"external": null, "requires": [], "ensures": []},
        "fold_scr":    {"external": null, "requires": [], "ensures": []},
        "shift_fold":  {"external": null, "requires": [], "ensures": []},
        "move_right":  {"external": "verifier::external_body",
                        "requires": ["0 < dr <= m", "m <= old(v)@.len()"],
                        "ensures": ["forall|j: int| dr <= j < m ==> final(v)@[j] == old(v)@[j - dr]",
                                    "forall|j: int| 0 <= j < dr ==> final(v)@[j] == old(v)@[j]",
                                    "forall|j: int| m <= j < old(v)@.len() ==> final(v)@[j] == old(v)@[j]"]},
        "slb_twin_move_right": {"external": null,
                        "requires": ["0 < dr <= m", "m <= old(v)@.len()"],
                        "ensures": ["forall|j: int| dr <= j < m ==> final(v)@[j] == old(v)@[j - dr]",
                                    "forall|j: int| 0 <= j < dr ==> final(v)@[j] == old(v)@[j]",
                                    "forall|j: int| m <= j < old(v)@.len() ==> final(v)@[j] == old(v)@[j]"]},
        "copy_in":     {"external": "verifier::external_body",
                        "requires": ["from + n <= src@.len()", "n <= old(dst)@.len()"],
                        "ensures": ["final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange( n as int, old(dst)@.len() as int, )"]},
        "slb_twin_copy_in": {"external": null,
                        "requires": ["from + n <= src@.len()", "n <= old(dst)@.len()"],
                        "ensures": ["final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange( n as int, old(dst)@.len() as int, )"]},
        "load_input":  {"external": "verifier::external_body",
                        "requires": [], "ensures": []},
        "emit":        {"external": "verifier::external_body",
                        "requires": [], "ensures": []},
        "kernel":      {"external": null,
                        "requires": ["off + len <= buf@.len()"],
                        "ensures": ["r == shift_fold(buf@, off as int, len as int)"]},
        "main":        {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                "c/main.c"],
    "aliases": {"c": {"n_body": "bytes.len()",
                      "bytes": "bytes.as_slice()",
                      "inp.n_iters": "n_iters"}},
    "call_args": {"c": {"kernel": [0, 2, 3]}},
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
    "probe_inputs": ["small.bin", "large.bin"],
    "probe_iters": [100, 200],
    "note": "work_per_call is the WINDOW in bytes -- the stride, 502 on small and 4093 on large -- and the two differ precisely so that check.py's d(Ir)/d(work) assertion has two probe shapes and can run at all. **The unit errs LOOSE here, which is p17's direction and NOT p16's or p05's, and by more than either.** The kernel touches its scratch four times over: 4096 bytes of memset, m of copy in, 4*(m-d)-6 of moves and m of fold = 6074 bytes on small against a window of 502 (12.1x) and 20444 against 4093 on large (5.0x). model.py's work_per_call docstring has the table. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged, and on p08 that argument is p16's and p17's rather than p05's: **the fold is a serial Horner chain**, acc = acc*31 + b, with a hard 3-cycle loop-carried dependence and no vector form -- measured at -O3 as a 4x-unrolled 23-instruction body over 4 bytes = 5.75 Ir/byte in every Rust rung (5.755 measured end to end, NOTES.md 3b), 23x the floor. The memmove calls themselves are BELOW the floor (glibc moves a byte in ~0.104 Ir), which is exactly why the floor is denominated in the window and not in bytes moved, and why NOTES.md quotes ns beside Ir for the move. Measured margins are in NOTES.md 9."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses the unsafe move at zero cost. What is new is what got proved -- this is the project's FIRST multi-clause trusted `ensures` (three region conjuncts partitioning the buffer; the length conjunct a move contract usually carries was tried and REMOVED because gate step 5c measured it not load-bearing -- NOTES.md 6a) and its first verified twin that is not a one-liner, and all of it erases. **The O0 row is pinned at `norel` and MEASURES `exact`, deliberately**: the gate accepts a stronger-than-pinned result and says so, and O0 identity between two crates whose names differ in length rests on call displacements, i.e. on link layout rather than on codegen -- `.memory/03-measurement.md`. Pinning the measured `exact` would turn a benign relink of `common/driver.rs` into a red gate reading as `the proof cost something`. NOTES.md 6 quotes the measured level. **safe_tuned vs unsafe is deliberately NOT pinned as an identity pair**: they are not identical, and NOTES.md 3 names the mechanism rather than asserting an equality that does not hold."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p08 there is a second, sharper reason: **this is the first pattern in the project whose UB is ALIASING rather than SPATIAL**, and Miri's borrow model is the only tool here that can see that class at all -- ASan's shadow memory cannot (it is an interceptor, not a shadow check, that catches the C rung) and valgrind memcheck cannot be run on this box at all (TASK_014 Part 0). controls/gen_controls.py points Miri at a `copy_nonoverlapping` mutant of R4 to find out whether it has teeth. Every input here is Miri-checkable: per call it is one 4 KiB memset, one m-byte copy, four moves and an m-byte fold -- ~82 KB at the 4 iterations check.py forces, against a budget of ~3 M.",
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

There is no exit 7 here, for p16's, p17's and p05's reason: p08's payload names
no allocation size — the scratch is a fixed local array — so p02's
`SLB_MAX_CAP` check would be dead code.

## Degenerate shapes

`stride_w >= 4 && stride_w <= n_blob` is the driver's whole input validation. A
stride below 4 cannot hold the header (`adversarial-stride3.bin`); a stride
above `n_blob` leaves no whole window. Either way the loop is skipped and the
driver prints `0` after **zero** kernel calls.

A window the kernel rejects is different and the difference is deliberate:
there the calls *do* happen and the **kernel** is what returns 0.
`adversarial-dzero` (`d == 0`) and `adversarial-dbig` (`d + nrep > m` by exactly
one) are those, and every rung including R1 returns 0 on both — they are
controls for `adversarial-overlap`, which passes the same guard and differs only
in that `d` is small enough for the ranges to overlap.

The kernel's `len < 4` guard is, given the driver's `stride_w >= 4`, unreachable
in this benchmark, and so is `m < 2` (with `d >= 1` and `nrep >= 1`, `m <= 1`
already fails `d + nrep > m`). Both are kept so the kernel is **total** and its
`requires` stays purely structural; the alternative — a `len >= 4` precondition
— would be a precondition about the driver's own guard rather than about the
buffer, which `.memory/02-bench-rules.md` warns against. `NOTES.md` §8 records
that they are dead and why they stay, along with the `avail >= SCR` branch that
no shipped input reaches.
