# p01 — array sum over a window: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C | `uint64_t kernel(const uint64_t *v, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(v: &[u64], off: usize, len: usize) -> u64` |

The C kernel takes three arguments; the Rust kernels take four registers, because
`&[u64]` is a pointer *and* a length. That asymmetry is deliberate and is the
finding, not a rigging: the length is the thing C does not have and therefore
cannot check. R2 and R3 consume it (bounds check / slice construction); R4 and R5
receive it and never read it, so LLVM should drop it — whether it does is one of
the things the assembly comparison answers. Do not "fix" this by giving C a dead
`v_len` parameter; that would be Rust-in-C-syntax.

## Semantics

```
kernel(v, off, len) = fold over i in [off, off+len) of  acc := acc +64 v[i]
                      starting from acc = 0
```

where `+64` is wrapping addition modulo 2^64. `len == 0` yields `0`.

Wrapping, not checked, addition is deliberate. It makes the kernel *total* on
values: there is no precondition on the contents of `v`, only on the shape of the
window. Rung 5's proof obligation is therefore exactly the memory-safety
property — `off + len <= v.len()` — and nothing is smuggled in via an artificial
value bound that the input generator would then have to be trusted to respect.
(The pilot did the opposite: `requires v[i] < 1000` and `n < 1000`, which its own
measured inputs violated. See `.memory/02-bench-rules.md`.)

C's `uint64_t` addition already wraps by definition, so R1 needs no special
spelling; the Rust rungs use `u64::wrapping_add`.

## Contract

```
requires:  off + len <= v_len
ensures:   result == wrapping_sum(v, off, len)
```

`harness/check.py` parses the block below, drives `model.py` against **every**
input file — `adversarial` included — and evaluates `requires` at every call the
benchmark actually makes and `ensures` against every value it actually returns.
That is the mechanical enforcement of `.memory/02-bench-rules.md` "Proof domain
must cover the measured domain" rules 1 and 3.

`off + len` cannot itself overflow `usize` in the measured domain because the
driver derives `off` from `acc % nwin` with `nwin = v_len - len + 1`, so
`off < nwin` and `off + len <= v_len`. R5 proves this at the call site.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. The pins exist because a green verification and
a green gate are, separately, evidence of very little:

| pin | the bypass it closes |
|---|---|
| `verus.obligations` | `#[verifier::external_body] fn main` — no call site verifies, so no precondition is discharged, and the obligation count drops 5 → 3. This is the pilot's fatal defect (`.memory/02-bench-rules.md` rule 2). |
| `verus.items[*].requires` / `.ensures` | replacing the kernel's postcondition with `ensures r == r` still gives *5 verified, 0 errors*. So does **deleting a `requires` from an `external_body` wrapper**, which silently deletes every caller's obligation and moves no count at all — the project's most dangerous known vacuity mode (`.memory/04-verus.md`). Only a textual diff against a pin catches it. |
| the item set itself | a *new* `external_body` item can otherwise be added without the TCB tally noticing. |
| `driver.canonical` | the driver loop was previously diffed rung-against-rung, so a mutation applied to *every* rung — deleting the anti-collapse barrier — passed; and the C copy was checked by required substrings, so adding a prefetch and a memory barrier passed (`.memory/02-bench-rules.md` forbids exactly that asymmetry). |
| `collapse.min_marginal_ir_per_call` | a kernel that got constant-folded away still has a backward branch somewhere in the symbol. |
| `identity` | recorded as a **result**, not a gate condition. A pattern whose proof legitimately costs an instruction is a finding; only a *drop below the pinned level* is a failure. |

```slb-contract
{
  "kernel": "kernel(v: &[u64], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": ["off + len <= v_len"],
  "ensures": ["result == wrapping_sum(v, off, len)"],
  "note": "expressions are evaluated in Python against the bindings model.py yields per call (off/len/v_len/v/result) plus the helpers it supplies (wrapping_sum)",

  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "obligations": {"verus.rs": 5, "safe_naive_verus.rs": 5},
    "items": {
      "verus.rs": {
        "sum_wrap":      {"external": null, "requires": [], "ensures": []},
        "get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "load_input":    {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "emit":          {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "kernel":        {"external": null,
                          "requires": ["off + len <= v@.len()"],
                          "ensures": ["r == sum_wrap(v@, off as int, len as int)"]},
        "main":          {"external": null, "requires": [], "ensures": []}
      },
      "safe_naive_verus.rs": {
        "sum_wrap":      {"external": null, "requires": [], "ensures": []},
        "load_input":    {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "emit":          {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "kernel":        {"external": null,
                          "requires": ["off + len <= v@.len()"],
                          "ensures": ["r == sum_wrap(v@, off as int, len as int)"]},
        "main":          {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "aliases": {"c": {"n_body": "vals.len()",
                      "inp.n_iters": "n_iters",
                      "vals": "vals.as_slice()"}},
    "canonical": [
      "n_vals = vals . len ( ) ;",
      "vs = vals . as_slice ( ) ;",
      "acc = 0 ;",
      "if win_len_w > 0 && win_len_w <= n_vals",
      "{",
      "win_len = win_len_w ;",
      "nwin = n_vals - win_len + 1 ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "off = acc % nwin ;",
      "r = kernel ( vs , off , win_len ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },

  "collapse": {
    "probe_input": "small.bin",
    "probe_iters": [100, 200],
    "min_marginal_ir_per_call": 400,
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100. A difference of two runs of the same binary in the same environment, so the loader/env terms that make whole-program Ir unquotable cancel exactly. Symbol-independent, so it works in `whole` mode and at O0 where the work lives in core::iter symbols. Measured floor across all 28 cells is 915 (c-clang O3 whole); 400 leaves >2x margin and is >100x above a collapsed loop."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost. At O0 the Rust kernel still calls Iterator::next and the crate names differ in length, so the call displacements differ -- link layout, not codegen."},
    {"a": "safe_naive", "b": "safe_naive_verus", "O0": "exact", "O3": "exact",
     "why": "R2 == R2v: proving safe code buys nothing."}
  ],

  "miri": {
    "required": false,
    "reason": "R4 and R5 are byte-identical at O3 (`identity` above pins `exact`), so R4 inherits R5's discharged obligations exactly. `.memory/02-bench-rules.md` makes Miri mandatory only when they are not."
  }
}
```

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p01's payload is:

```
word 0     u64  win_len    # the window length passed to the kernel as `len`
word 1..   u64  values     # the array `v`; v_len = (payload_len/8) - 1
```

Nothing is a compile-time constant: `n_iters`, `win_len` and `v_len` all come
from the file.

## Driver loop

Identical in all five rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` diffs the copies.

```
n_vals  := vals.len()
acc     := 0
if win_len_w > 0 and win_len_w <= n_vals:
    win_len := win_len_w as usize
    nwin    := (n_vals - win_len + 1) as u64
    it      := 0
    while it < n_iters:
        off := (acc % nwin) as usize
        r   := kernel(vals, off, win_len)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

### Why this does not evaporate

`off` is derived from `acc`, and `acc` is derived from the previous call's
result. Call *i+1* therefore cannot begin until call *i* has returned, so LLVM
can neither CSE the calls nor hoist them out of the loop, and no `black_box` or
`asm volatile` is needed — which matters, because those two are not equally
strong barriers and using them would put a C-vs-Rust asymmetry in the driver
(`.tasks/TASK_002.md`). The mechanism is the same arithmetic in both languages.

`harness/check.py` proves this held, per cell, by disassembling and requiring a
backward branch and a plausible body size.

### Degenerate shapes

The guard `win_len_w > 0 && win_len_w <= n_vals` is the whole of the driver's
input validation, and it is what the `adversarial-*` inputs attack. When it
fails the loop is skipped entirely (rather than being entered and broken out of,
which would put a branch in the measured loop) and the driver prints `0`.
`n_iters == 0` is handled by the `while` itself.

`payload_len` declaring more bytes than the file carries is caught earlier, in
`slb_load` / `driver::load`, which exits `5`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |
