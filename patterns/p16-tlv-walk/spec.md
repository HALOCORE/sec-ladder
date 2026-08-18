# p16 — TLV record walk: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and R1 ignores it, so R1-vs-R1h is a comparison
with the calling convention, the argument count and the register allocation all
held fixed. The only difference between those two cells is one `if`.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Semantics

```
p    = off
end  = off + len
acc  = 0
nrec = 0

while end - p >= 3:                        # a header fits (subtraction-first)
    acc  = acc *64 31 +64 buf[p]           # the tag byte, folded so it is live
    vlen = buf[p+1] + 256 * buf[p+2]       # little-endian u16
    if vlen > end - (p + 3):               # <<< THE CHECK: the value does not fit
        break                              #     malformed -> stop walking
    j = 0
    while j < vlen:
        acc = acc *64 31 +64 buf[p+3+j]
        j  += 1
    p    = p + 3 + vlen
    nrec = nrec + 1

return acc *64 31 +64 nrec
```

`*64`/`+64` are wrapping, as in p01/p02, so the kernel has **no precondition on
values** and every measured input is inside the verified domain by construction.
`nrec + 1` wraps too, which removes the only other overflow obligation; C's
`uint64_t` wraps by definition (6.2.5p9) and the Rust rungs write
`nrec.wrapping_add(1)`.

Five things are load-bearing. Do not "improve" any of them.

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither (TASK_016_REVIEW m2).

- **Every comparison is subtraction-first** — `end - p >= 3`, and
  `vlen > end - (p + 3)`. **These are the tokens, not just the property.** A
  rung that establishes the same two facts some other way — `split_first_chunk`
  plus `split_at_checked` on a consumed slice, or `rem >= 3` / `vlen > rem - 3`
  on a running remainder — does **not** satisfy this and is a different
  benchmark; the block's `why` carries the argument and what the reading costs
  (TASK_017, from TASK_016_REVIEW M2). The additive spellings (`p + 3 <= end`,
  `p + 3 + vlen <= end`) can overflow `size_t` on an attacker-chosen `vlen` and
  wave the attack through. Neither subtraction can underflow *given the check*:
  `p <= end` and `p + 3 <= end` are loop invariants, and the second test is
  exactly what maintains the first. That is not a side note — it is why the two
  obligations in this kernel are not independent, and it is why deleting the
  check (R1) makes `end - p` underflow and the walk never stop at the buffer
  end. See `c/kernel.c`.

  p02 measured that subtraction-first costs rustc an idiom recognition, and its
  headline was retracted for attributing that to bounds checking. p16's fold is
  a serial `acc = acc*31 + b` chain with no bulk-memory idiom to lose, so the
  same escape route should not exist here — but "should not" is an argument.
  `NOTES.md` §3 is the measurement, and it changes one loop at a time.
- **R1 omits only the second check.** It keeps `end - p >= 3`; without that the
  walk reads a header off the end on *every* input, including the well-formed
  ones, and the pattern stops being about the length field. It drops
  `vlen > end - (p+3)`. That is the single edit between `c/kernel.c` and
  `c/kernel_hardened.c`.
- **The tag byte is folded, not ignored**, and it is folded *before* the fit
  test. An unread tag is deleted by LLVM and the walk stops looking like a TLV
  walk; folding it before the test is what makes a chain that stops early differ
  from a chain that was one record shorter.
- **`nrec` is folded into the result** so the record count is observable in the
  checksum. A walker that mis-parses the chain but folds the same bytes must not
  produce the same answer.
- **No tag dispatch, no skipped records.** A `if tag != 0 { skip }` branch is
  realistic and it is *deliberately excluded*: it adds an unpredictable
  data-dependent branch, which is a second new variable, and this box cannot
  measure branch misses (`.memory/00-environment.md`). One new thing at a time —
  the unpredictable-branch axis belongs to p19/p35.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == tlv_fold(buf, off, len)
```

`requires` is the whole of it: **the window is inside the blob.** That is
structural — it is about the shape of the buffer the driver built, not about its
contents — so it holds on every input this benchmark runs, `adversarial-*`
included, and `harness/check.py` evaluates it at every one of the kernel calls
to prove that it does. Every `vlen` a `u16` prefix can express is an *argument*
of the problem; the kernel is total in all 65 536 of them.

### The `ensures` is not the security property, and on this pattern nothing is

**This is the one real difference from p02 and it must not be glossed.** p02's
security property was statable as a postcondition, because p02 *writes*: an
equality on the whole destination sequence says "the record landed where it
should" and "not one byte outside it moved" at the same time. p16 writes
nothing. The harm it models is a **read**, and

> "no byte outside `buf[off .. off+len)` was read"

is **not a property of the return value** — a kernel could read out of bounds
and simply discard the byte. There is no `ensures` that says it.

So for a read-only kernel, R5's memory-safety claim rests **entirely on the
discharged `requires` of the trusted accessor**. Every `buf[i]` in verified exec
code carries the obligation `i < buf@.len()`; `get_unchecked`'s
`requires i < v@.len()` is what every call site must prove, and *that* — proved
at four call sites, for indices the attacker's own length fields chose — is the
security property of this pattern. The `ensures` above exists to make the proof
non-vacuous and to tie the value to `model.py`.

Two consequences, both recorded in `NOTES.md` §5:

1. the TCB story **is** the whole result here, so `harness/check.py`'s
   clause-deletion and verified-twin stages matter more on p16 than on any
   earlier pattern, and they matter on the accessor's `requires` specifically;
2. a green 5c-twin on p16 is **not** evidence that anything hard was checked —
   p16's accessor is the same single-clause `i < v@.len()` p01 and p02 ship, so
   there is no missing conjunct for the twin to find. `NOTES.md` §7 shows the
   twin *failing* on `i <= v@.len()` for this pattern's own accessor, which is
   the only form of evidence that stage can supply here.

### Termination, and what a proof catches that a test does not

The outer walk carries `decreases end - p`, and progress needs `3 + vlen >= 1`,
which is immediate — a record occupies at least its header, so the *header* is
what guarantees progress and the length field is not trusted for it.

A walker written `p += vlen` instead of `p += 3 + vlen` is a real and common
variant of this bug, and it does **not** terminate on `vlen == 0`. Verus rejects
it at the `decreases` clause with no test run and no input that triggers it;
`NOTES.md` §8 has the exact message. That variant is deliberately not built as a
rung — a sentence and the error is the whole point.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p16's payload is:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the record chain; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — one function per language, added to `common/` for this
pattern, never to the pattern itself (`.memory/05-layout.md`). All three are a
bulk copy rather than an element-by-element decode, which is what keeps every
p16 row Miri-checkable (`.memory/02-bench-rules.md`: `head_u64_body`'s
per-element loop is why p01's `large.bin` blocks).

A record is `tag:u8, vlen:u16le, value:u8[vlen]` and occupies `3 + vlen` bytes.
Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob`, every tag and
every length prefix come from the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across. The only allocation the driver makes is the blob
itself, whose size is the file's size.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below.

```
n_blob := bytes.len()
buf    := bytes
acc    := 0
if stride_w >= 3 and stride_w <= n_blob:
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

`stride_w >= 3` rather than p02's `>= 2`: a window below 3 bytes cannot hold a
header, so `adversarial-stride2.bin` attacks this guard. When it fails the loop
is skipped entirely — rather than entered and broken out of, which would put a
branch in the measured loop — and the driver prints `0`. `n_iters == 0` is
handled by the `while` itself. The comparison is in `u64` *before* the
`as usize` cast, so a truncating driver cannot sneak a 2^40 stride past it.

### Why this does not evaporate

Same mechanism as p01 and p02: `k` is derived from `acc`, and `acc` from the
previous call's result, so call *i+1* cannot begin until call *i* has returned.
Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile` — the
same arithmetic in both languages, so neither gets a stronger barrier than the
other. `k = (acc * nwin) >> 64` is Lemire's map onto `[0, nwin)`; see p01's
`spec.md` for why it is a multiply-shift and not a modulo.

### Why the window, and not the chain

The driver walks a **fixed-size window** and the kernel walks the *records
inside it*. That is deliberate and it is the design decision that lets p16 exist
at all (TASK_006_REVIEW named the alternative as a hard stop): a TLV chain has
no natural stride, so a driver that walked the chain to pick a start offset
would put the walk's cost in the driver and swamp the marginal-`Ir` column. With
fixed windows the driver stays O(1) per call — one multiply, one shift, one
multiply — while the **kernel's** trip count stays data-dependent, which is the
entire point of the pattern.

It is also what makes `work_per_call` a single scalar. A parser that early-exits
has a *distribution* of work per call, and `check.py:625` needs one number and
hard-fails on `work <= 0` at `:632`; p02's min-over-records convention collapses
to 0 the moment a probe input contains one rejected record, which is exactly
what a TLV corpus contains. The window is fixed by the payload header, identical
on every call, and a strict over-estimate of the bytes actually folded — so the
derived floor errs strict. See `model.py`.

### Why the structural precondition holds

`k < nwin` because `(acc * nwin) >> 64 < nwin` for `nwin >= 1`, and
`k * stride + stride <= n_blob` because `k <= nwin - 1` and
`nwin * stride <= n_blob` (integer division rounds down). Both steps are
nonlinear, so R5 spells them out in ghost code.

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
| `verus.obligations` = 10 | **`fold_bytes` 1 + `tlv_walk` 1 + `kernel` 3 + `main` 5 = 10.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained: the two *recursive* spec fns carry one termination query each, `vlen_at` and `tlv_fold` are non-recursive and carry **0**, the three `external_body` items carry **0**, `kernel` is 1 for the body + 1 per loop body (there are two loops), and `main` is 1 for the body + 1 for the driver loop + one per `by (nonlinear_arith)`/`by { .. }` sub-proof in its two ghost blocks. Note that `.memory/04-verus.md`'s rule of thumb — one query per function plus one per loop — under-counts by 3 here, because it predates a pattern with `by`-blocks in the driver; the rule is a skeleton checksum and it is the *measured* decomposition that a reviewer should re-run. |
| `verus.twin_obligations` = 11 | the count in the **other** configuration, `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. **10 shipped + 1**, and the 1 is measured the same way: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` — one function, no loop body, no `by`-block. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item, because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. `check.py` derives this from `verus.rs` rather than reading the flag. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": ["off + len <= buf_len"],
  "ensures": ["result == tlv_fold(buf, off, len)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (tlv_fold). NOTE WHAT THE ensures IS NOT: it is the value, not the security property. p16's kernel writes nothing, so 'no byte outside the window was read' cannot be a postcondition -- a kernel could read out of bounds and discard the byte. The memory-safety claim rests entirely on get_unchecked's discharged `requires i < v@.len()`. See the prose above.",

  "idiom": {
    "required": [
      "every comparison is subtraction-first AND IS SPELLED AS THESE TOKENS -- `end - p >= 3` and `vlen > end - (p + 3)` -- in every rung (R1: fourth entry below). This entry names TOKENS, not the weaker property 'contains no additive comparison'; TASK_017 disambiguated it and the argument is in `why`",
      "the tag byte is folded, and folded BEFORE the fit test",
      "nrec is folded into the result",
      "R1 omits only the second check -- it keeps `end - p >= 3`"
    ],
    "forbidden": [
      "the additive spellings `p + 3 <= end` and `p + 3 + vlen <= end`",
      "tag dispatch or skipped records"
    ],
    "why": "the additive comparisons can overflow size_t on an attacker-chosen vlen and wave the attack through, which is the whole check p16 is about; an unread tag is deleted by LLVM and the walk stops looking like a TLV walk; a `if tag != 0 { skip }` branch adds an unpredictable data-dependent branch, which is a second new variable and belongs to p19/p35 (this box cannot measure branch misses). RESTATED in this hashed block at TASK_016 from the prose section 'Five things are load-bearing' above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). DISAMBIGUATION (TASK_017, from TASK_016_REVIEW M2). This block used to contradict itself: the first entry read as naming tokens while this text asserted that a consuming spelling containing NEITHER named comparison (`split_first_chunk::<3>()` plus `split_at_checked`, `.temp/p05r3/v16/tuned_split.rs`) was admissible under it. The first entry names TOKENS. Four reasons, none of them 'which spelling turned out cheaper' -- that reason is refused explicitly, because a restriction selected by a measurement is self-certification (.memory/02-bench-rules.md), and the counterfactual holds: the same four reasons pick the same reading if the consuming spelling had measured DEARER. (i) House convention. p05's 'i*ncol + j written out in every rung, not strength-reduced', p02's 'spelled identically in every rung' and p17's 'the one conjunctive if start < end && start >= 0, not two continues' are all token pins, and p17's rejects a spelling that is SEMANTICALLY IDENTICAL to the one it names -- so a `required` entry in this project constrains shape, not only meaning, and reading p16's as the outlier needs a reason nobody has given. (ii) These two tokens ARE the traversal representation. `p` indexing the whole blob with `end` re-derived per record is what they say; requiring them holds the representation fixed across all six rungs, which is what makes R3 - R4 a difference in safety rather than a difference in representation. That is the unmatched-pair defect TASK_014/TASK_015 shipped twice. (iii) The exclusion falls SYMMETRICALLY. The consuming R4 control (`.temp/p05r3/v16/unsafe_consume.rs`, `rem >= 3` and `vlen > rem - 3` on a running remainder) is out of contract for exactly the same reason, so this reading does not protect the shipped safe rung by excluding only its competitor -- it excludes a representation, on both sides of the pair. (iv) Under the semantic reading both R3 and R4 become cells defined by PERMISSION, and .memory/01-ladder.md finding 14 (inf(R4) <= inf(R3) by construction) says the published pair then has no fixed point -- the measured R4' is already 29 Ir/call cheaper than the shipped R4, so the chase does not terminate on the unsafe side either. WHAT THIS READING COSTS, said plainly, because it is not free: rows 3, 4 and 6 of NOTES.md 10 are OUT OF CONTRACT, so p16 now has ZERO measured admissible alternate spellings, and 'the shipped R3 is the cheapest admissible spelling' is UNESTABLISHED rather than established -- nobody has searched the in-contract space, and .memory/05-layout.md finding 13 wants at least two admissible alternates per rung. p16's published R3 number therefore remains a spelling's number in everything this block does not pin: the value fold, how the three header bytes are read, unrolling. Note what is deliberately NOT restricted: the R2/R3/R4 spelling of the value fold and of the header read, beyond the two comparisons. If a later task wants p16's R3 to be more than a spelling's number, the honest move is p05's at TASK_013 -- declare the walk's spelling here BEFORE measuring."
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
    "obligations": {"verus.rs": 10},
    "twin_obligations": {"verus.rs": 11},
    "obligations_note": "10 = fold_bytes 1 + tlv_walk 1 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. vlen_at and tlv_fold are non-recursive spec fns and carry 0; get_unchecked, load_input and emit are external_body and carry 0; kernel is body + 2 loop bodies; main is body + driver loop + one per `by (nonlinear_arith)`/`by { .. }` sub-proof in its two ghost blocks. `.memory/04-verus.md`'s one-per-function-plus-one-per-loop rule of thumb gives 7 here and is therefore not the derivation -- it predates a pattern with `by`-blocks in the driver.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 10 shipped + 1, and the 1 is measured: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` -- one function, no loop body, no `by`-block. Pinned for the same reason the shipped count is: `tv > base_v` only says something extra compiled, and a twin that quietly lost its body, or an item that exists only under the cfg, moves this number and nothing else.",
    "items": {
      "verus.rs": {
        "vlen_at":    {"external": null, "requires": [], "ensures": []},
        "fold_bytes": {"external": null, "requires": [], "ensures": []},
        "tlv_walk":   {"external": null, "requires": [], "ensures": []},
        "tlv_fold":   {"external": null, "requires": [], "ensures": []},
        "get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "slb_twin_get_unchecked": {"external": null,
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "load_input": {"external": "verifier::external_body",
                       "requires": [], "ensures": []},
        "emit":       {"external": "verifier::external_body",
                       "requires": [], "ensures": []},
        "kernel":     {"external": null,
                       "requires": ["off + len <= buf@.len()"],
                       "ensures": ["r == tlv_fold(buf@, off as int, len as int)"]},
        "main":       {"external": null, "requires": [], "ensures": []}
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
      "if stride_w >= 3 && stride_w <= n_blob",
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
    "note": "work_per_call is the WINDOW in bytes -- the stride, 508 on small and 4090 on large -- and the two differ precisely so that check.py's d(Ir)/d(work) assertion has two probe shapes and can run at all. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged. That is legitimate here where it was not for p02: p02's kernel is dominated by a bulk copy and glibc memcpy moves a byte in 0.104 Ir, so 0.25 forbade the fastest correct implementation. p16's inner loop is a serial `acc = acc*31 + byte` Horner chain -- each byte's result feeds the next multiply -- so there is no bulk-memory instruction and no vector form that could undercut the default. Measured margins are in NOTES.md 4."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost, on a kernel whose trip count is attacker data and whose loop invariant is a recursive spec function (10 obligations, an invariant_except_break/ensures pair for the early exit, two nonlinear steps in the driver). At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p16 that argument is at its strongest: the pattern's entire memory-safety claim is a trusted `requires`, there is no security `ensures` to back it up, and Miri on R4 is one of only two mechanical backstops (the other being stage 3c identity, which catches R5-only drift). Every input here is Miri-checkable: the cost is 4 iterations x the STRIDE, and the largest stride is 4090 bytes against a budget of ~3 M folded bytes.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed -- but note that p16 is the pattern where that hurts most, for the reason in `reason` above."
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

There is no exit 7 here. p02 has one because its payload names its own
destination-buffer capacity, so the driver allocates from an attacker-controlled
size and both languages must reject the same range identically before
allocating. p16's payload names no allocation size at all, so the check would be
dead code and copying it across would be worse than not having it.

## Degenerate shapes

The guard `stride_w >= 3 && stride_w <= n_blob` is the driver's whole input
validation. A stride below 3 cannot hold a header (`adversarial-stride2.bin`);
a stride above `n_blob` leaves no whole window, so `nwin` would be 0 and `k`
would have nothing to index. Either way the loop is skipped and the driver
prints `0` after zero kernel calls.

A window whose *tail* is 1 or 2 bytes (`adversarial-trunc.bin`) is not
degenerate — it is the ordinary end of a chain, handled by `end - p >= 3`, which
**every** rung including R1 keeps. All six rungs must agree on it.
