# p02 — length-prefixed record copy: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *src, size_t src_len, size_t src_off, uint8_t *dst, size_t dst_cap)` |
| R2/R3/R4/R5 Rust | `fn kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> u64` |

Five C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, `&mut [u8]` is a pointer
and a length, and C spells each pair out. This is the opposite of p01, where the
C kernel genuinely could not know the array's length and that asymmetry was the
finding. Here C is handed both sizes and R1 ignores them — which is the more
common and more damning shape of CWE-787, and it makes R1-vs-R1h a comparison
with the calling convention, the argument count and the register allocation all
held fixed. The only difference between those two cells is three lines of check.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a five-argument call into a three-argument one. See "Driver loop".)

## Semantics

```
len = src[src_off] + 256 * src[src_off + 1]              # little-endian u16

if len <= dst_cap and len <= src_len - (src_off + 2):     # the record fits
    dst[0 .. len)  := src[src_off+2 .. src_off+2+len)
    return  the wrapping sum of the bytes now in dst[0 .. len)
else:                                                     # reject, untouched
    return 0
```

Four things about that are load-bearing:

- **The kernel is total in `len`.** Every one of the 65 536 values a `u16`
  prefix can express is handled. `.memory/02-bench-rules.md`: the attacker
  quantity is an *argument*, not an assumption. A contract that assumed
  `len <= dst_cap` would verify, would pass the gate, and would have assumed the
  vulnerability away.
- **The check is written subtraction-first.** `len > src_len - (src_off + 2)`,
  not `src_off + 2 + len > src_len`: the additive form can overflow `size_t`
  and wave the attack through. The subtraction cannot underflow, because
  `src_off + 2 <= src_len` is the structural precondition (below). Every rung
  spells the test identically.

  **This spelling has a measured codegen cost in R2, and it is a finding rather
  than a reason to change it** (`NOTES.md` §3a). Subtraction-first leaves LLVM
  unable to prove the copy loop's index in bounds, so rustc never rewrites
  R2's byte loop into a `memcpy`: one operator flips `bulk_calls []` →
  `['memcpy@GLIBC_2.14']` and 118 kernel instructions → 87, and that difference
  is 100% of R2's published delta. The additive form is the one `spec.md`
  forbids, so the honest reading is *the sound spelling of an overflow check
  costs rustc an idiom recognition*, not *bounds checks are expensive*. R3, R4
  and R5 write the same subtraction-first check and pay nothing, because their
  copies are not index-by-index.
- **The prefix is decoded with `+`, not `|`.** `b0 + 256*b1` and
  `b0 | (b1 << 8)` are the same function on bytes and LLVM emits the same
  instruction for both, but the additive form needs no bit-vector reasoning in
  R5. Choosing the spelling that is cheaper to prove is legitimate; choosing a
  weaker *specification* would not be.
- **The result is folded over `dst`, after the copy, not over `src`.** So the
  copy cannot be dead-coded: the return value depends on the bytes having
  actually arrived. `ensures` states the sum over `src`, which is what makes the
  postcondition also assert that the copy was correct.

Wrapping addition, as in p01, so the kernel has no precondition on *values* and
every measured input is inside the verified domain by construction.

## Contract

```
requires:  src_off + 2 <= src_len
ensures:   result == copy_sum(src, src_off, dst_after_len)
           dst_after == copy_dst(dst_before, src, src_off)
```

**Two clauses, not three.** There was a third, `dst_after_len == dst_len`, and
`harness/check.py` step 5c deleted it and found the file still verified with 0
errors: `copy_dst` returns a sequence of `dst_before`'s length on both branches,
so the security clause already entails it. `copy_bytes`'s trusted contract lost
its own copy of the same statement for the same reason. Saying an entailed fact
a second time does not strengthen a contract; it inflates the TCB tally, gives a
reviewer two claims to judge where there is one, and lets a later weakening of
the strong clause hide behind the weak one.

`requires` is the whole of it: **the two prefix bytes are inside the source
buffer.** That is structural — it is about the shape of the buffers the driver
built, not about their contents — so it holds on every input this benchmark
runs, `adversarial-*` included, and `harness/check.py` evaluates it at every one
of the 220 032 kernel calls to prove that it does.

The security property is in the `ensures`, and specifically in the second
clause, which pins the **entire** destination sequence rather than the copied
prefix:

> `dst_after == copy_dst(dst_before, src, src_off)`, where `copy_dst` is the
> record followed by *the bytes that were already there*.

So it says both "the record landed where it should" and "not one byte outside
`dst[0..len)` moved" — and on a record that does not fit, `copy_dst` is the
identity, i.e. *nothing at all was written*. That is the clause R1 violates.

`harness/check.py` derives these three Python expressions from `verus.rs`'s own
clause text through the `verus.translate` table below, drives `model.py` over
**every** input file, and evaluates them at every call. `dst_before`/`dst_after`
are the whole buffer, before and after, as `bytes`.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p02's payload is:

```
word 0     u64  cap        # destination buffer capacity, in bytes
word 1     u64  stride     # bytes per record
byte 16..  u8[] src        # the record blob; n_src = payload_len - 16
```

decoded by `slb_head2_u64_bytes` / `driver::head2_u64_bytes` /
`slb.head2_u64_bytes` — one function per language, added to `common/` for this
pattern. Every record is `stride` bytes: a little-endian `u16` length prefix and
then that many data bytes. Nothing is a compile-time constant: `n_iters`, `cap`,
`stride`, `n_src` and every length prefix come from the file.

`cap` is an attacker-controlled allocation size, so both drivers reject it
outside `1 ..= SLB_MAX_CAP` (64 MiB) **before allocating**, with the same exit
code. Otherwise C's `calloc` returns `NULL` where Rust's allocator aborts, and a
driver difference reads as a rung difference.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below.

```
n_src := bytes.len()
src   := bytes
dst   := dbuf                        # cap zeroed bytes, allocated before the region
acc   := 0
if stride_w >= 2 and stride_w <= n_src:
    stride := stride_w as usize
    nrec   := (n_src / stride) as u64
    it     := 0
    while it < n_iters:
        k   := ((acc as u128 * nrec as u128) >> 64) as usize
        r   := kernel(src, k * stride, dst)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

### Why this does not evaporate

Same mechanism as p01: `k` is derived from `acc`, and `acc` from the previous
call's result, so call *i+1* cannot begin until call *i* has returned. Nothing
to CSE, nothing to hoist, no `black_box` and no `asm volatile` — the same
arithmetic in both languages, so neither gets a stronger barrier than the other.
`off = (acc * nrec) >> 64` is Lemire's map onto `[0, nrec)`; see p01's `spec.md`
for why it is a multiply-shift and not a modulo.

The record index also means every call reads a *different* 4 KiB of an 8 MiB
blob on `large`, which is what makes that input memory-bound.

### Why the structural precondition holds

`k < nrec` because `(acc * nrec) >> 64 < nrec` for `nrec >= 1`, and
`k * stride + 2 <= n_src` because `k <= nrec - 1` and `nrec * stride <= n_src`
(integer division rounds down). Both steps are nonlinear, so R5 spells them out
in ghost code; that is where three of this pattern's nine obligations live.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(src, n_src, k * stride, dst, dst_cap)` and the Rust
loop calls `kernel(src, k * stride, dst)`. `driver.aliases` cannot reconcile
that — both sides of an alias are a dotted identifier path, so an alias renames
and can do nothing else. `driver.call_args` declares which argument *positions*
of a named call are the canonical ones (`{"c": {"kernel": [0, 2, 3]}}`), and
`harness/dloop.py` refuses to drop anything that is not a single bare
identifier, so no prefetch, no side effect and no extra statement can hide in
the arguments the diff stops looking at. Keeping the wrong positions raises
rather than quietly matching.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
the two entries that are new here:

| pin | why |
|---|---|
| `driver.call_args` | the C kernel takes the two slice lengths Rust carries inside `&[u8]`, so the C call has five arguments and the Rust call has three. Declared positionally and checked structurally (above). |
| `miri.required: true` | R4 and R5 are byte-identical at `-O3`, so `.memory/02-bench-rules.md` does **not** require Miri here. It is switched on anyway: this is the project's first rung-4 with raw pointer arithmetic (`copy_nonoverlapping`, `as_ptr().add()`), and a UB test over all nine inputs costs a minute. Turning it off would be a weakening. |

```slb-contract
{
  "kernel": "kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> u64",
  "model": "model.py",
  "requires": ["src_off + 2 <= src_len"],
  "ensures": ["result == copy_sum(src, src_off, dst_after_len)",
              "dst_after == copy_dst(dst_before, src, src_off)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (src/src_off/src_len/dst_len/dst_after_len/dst_before/dst_after/result) plus the helpers it supplies (copy_dst, copy_sum). dst_before and dst_after are the WHOLE destination buffer as bytes: the security property is an equality on all of it, not on the copied prefix.",

  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "final(dst)@.len()": "dst_after_len",
      "old(dst)@.len()": "dst_len",
      "final(dst)@": "dst_after",
      "src@.len()": "src_len",
      "old(dst)@": "dst_before",
      " as int": "",
      "src@": "src",
      "=~=": "==",
      "r": "result"
    },
    "obligations": {"verus.rs": 9},
    "items": {
      "verus.rs": {
        "rec_len":      {"external": null, "requires": [], "ensures": []},
        "fits":         {"external": null, "requires": [], "ensures": []},
        "copy_dst":     {"external": null, "requires": [], "ensures": []},
        "sum_bytes":    {"external": null, "requires": [], "ensures": []},
        "copy_sum":     {"external": null, "requires": [], "ensures": []},
        "lemma_sum_congruent": {
            "external": null,
            "requires": ["0 <= n",
                         "forall|j: int| 0 <= j < n ==> #[trigger] a[fa + j] == b[fb + j]"],
            "ensures": ["sum_bytes(a, fa, n) == sum_bytes(b, fb, n)"]},
        "get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "slb_twin_get_unchecked": {"external": null,
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "copy_bytes":   {"external": "verifier::external_body",
                         "requires": ["from + n <= src@.len()",
                                      "n <= old(dst)@.len()"],
                         "ensures": ["final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange( n as int, old(dst)@.len() as int, )"]},
        "slb_twin_copy_bytes": {"external": null,
                         "requires": ["from + n <= src@.len()",
                                      "n <= old(dst)@.len()"],
                         "ensures": ["final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange( n as int, old(dst)@.len() as int, )"]},
        "load_input":   {"external": "verifier::external_body",
                         "requires": [], "ensures": []},
        "emit":         {"external": "verifier::external_body",
                         "requires": [], "ensures": []},
        "kernel":       {"external": null,
                         "requires": ["src_off + 2 <= src@.len()"],
                         "ensures": ["r == copy_sum(src@, src_off as int, final(dst)@.len() as int)",
                                     "final(dst)@ =~= copy_dst(old(dst)@, src@, src_off as int)"]},
        "main":         {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 13,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                "c/main.c"],
    "aliases": {"c": {"n_body": "bytes.len()",
                      "bytes": "bytes.as_slice()",
                      "dbuf": "dbuf.as_mut_slice()",
                      "inp.n_iters": "n_iters"}},
    "call_args": {"c": {"kernel": [0, 2, 3]}},
    "canonical": [
      "n_src = bytes . len ( ) ;",
      "src = bytes . as_slice ( ) ;",
      "dst = dbuf . as_mut_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 2 && stride_w <= n_src",
      "{",
      "stride = stride_w ;",
      "nrec = n_src / stride ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "k = acc * nrec >> 64 ;",
      "r = kernel ( src , k * stride , dst ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },

  "collapse": {
    "probe_inputs": ["small.bin", "large.bin"],
    "probe_iters": [100, 200],
    "note": "work_per_call is BYTES COPIED (61 on small, 4092 on large) and model.py declares min_ir_per_work = 0.0625 Ir per byte beside it, replacing the harness default of 0.25. The default is derived in 64-bit-lane terms and is unsound for a byte: glibc memcpy moves a byte in 0.104 instructions on this box (re-measured at TASK_006), so a bulk-copy kernel scores 0.118 and 0.25 would fail it at 0.47x while it is the fastest correct implementation there is. 0.0625 is the fused AVX-512 lower bound -- load, store, vpsadbw, vpaddq per 64-byte lane. The shipped rungs measure 2.25 to 6.67 Ir/byte, 36x to 107x clear, because the byte fold does not vectorise in rustc. Neither the rate nor the unit is settable from this file: both live in model.py, which the gate drives in a sandbox, and the gate prints the rate and its justification in every verdict."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost, on a kernel with a raw copy_nonoverlapping and a real proof (9 obligations, an induction lemma, two nonlinear steps in the driver) rather than p01's single get_unchecked. At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3, so `.memory/02-bench-rules.md` does not make Miri mandatory. It is required here anyway: R4 is the project's first rung-4 carrying raw pointer arithmetic (`src.as_ptr().add(src_off + 2)`, `dst.as_mut_ptr()`, `copy_nonoverlapping`), where p01's was a single `get_unchecked`, and the adversarial inputs drive it down the rejection path that the proof is about. A UB test over all nine inputs costs about a minute.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed -- but note the pattern is NOT exempt from the policy on identity grounds alone in spirit: R4 here is materially more unsafe than p01's."
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
| 7 | declared `cap` is 0 or above `SLB_MAX_CAP` |

## Degenerate shapes

The guard `stride_w >= 2 && stride_w <= n_src` is the driver's whole input
validation and it is what `adversarial-stride1` attacks: a stride below 2 cannot
hold a length prefix, and a stride above `n_src` leaves no whole record, so
`nrec` would be 0 and `k` would have nothing to index. When it fails the loop is
skipped entirely — rather than entered and broken out of, which would put a
branch in the measured loop — and the driver prints `0`. `n_iters == 0` is
handled by the `while` itself. Comparison is in `u64` *before* the `as usize`
cast, so a truncating driver cannot sneak a 2^40 stride past it.

`cap` outside `1 ..= SLB_MAX_CAP` exits 7 before anything is allocated;
`payload_len` declaring more bytes than the file carries is caught earlier still,
in `slb_load` / `driver::load`, which exits 5.
