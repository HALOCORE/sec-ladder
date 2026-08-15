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

`harness/check.py` parses the block below, simulates the driver against every
input file, and evaluates `requires` at every call the benchmark actually makes
and `ensures` against every value it actually returns. That is the mechanical
enforcement of `.memory/02-bench-rules.md` "Proof domain must cover the measured
domain" rules 1 and 3.

```slb-contract
{
  "kernel": "kernel(v: &[u64], off: usize, len: usize) -> u64",
  "requires": ["off + len <= v_len"],
  "ensures": ["result == wrapping_sum(v, off, len)"],
  "note": "expressions are evaluated in Python with v_len/off/len/result bound per call and wrapping_sum supplied by harness/check.py"
}
```

`off + len` cannot itself overflow `usize` in the measured domain because the
driver derives `off` from `acc % nwin` with `nwin = v_len - len + 1`, so
`off < nwin` and `off + len <= v_len`. R5 proves this at the call site.

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
