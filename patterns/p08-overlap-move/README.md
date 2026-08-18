# p08 — overlapping move: the bug safe Rust cannot express

**The C bug.** A fixed read buffer is shifted right to make room at the front,
once per framing layer — the nested-encapsulation idiom.
`memmove(scr + d, scr, m - d)` is correct; **`memcpy` is undefined behaviour**
whenever the source and destination ranges overlap, and `d` comes from the file.
CWE-1341-adjacent, and in practice the plain one: *`memcpy` where `memmove` is
required*.

```c
for (r = 0; r < nrep; r++) {
    size_t dr = d + r;
    memcpy(scr + dr, scr, m - dr);      /* R1.  R1h says memmove. */
}
```

## Why this pattern exists

Every other result in this project is about a **bounds check**. p01, p02, p16
and p05 price one; p17 shows one cannot save you. So the programme says "Rust
costs a check" and "Rust does not help here" and has nothing that says *"Rust
wins structurally, for a reason that is not a runtime check at all."*

p08 is that case, and it has the full arc:

| | can it express the bug? | cost |
|---|---|---|
| C | yes — `memcpy` | — |
| **safe Rust** | **no.** `&[u8]` and `&mut [u8]` into one buffer at once is `E0502` | **zero: the program does not compile** |
| unsafe Rust | yes again — `ptr::copy_nonoverlapping` | its whole contract is the non-overlap |
| Verus | **yes — and the verifier does not see it.** The *caller's* obligation is discharged; the trusted body is trusted | the proof moves the bug into the TCB, it does not remove it |

**That last row was wrong until TASK_014_REVIEW measured it**, and the correction
matters more than the row: it used to read *"the bug is not even expressible in
the spec logic"*. Substitute `core::ptr::copy` → `core::ptr::copy_nonoverlapping`
in `verus.rs`'s trusted body and nothing else, and Verus reports
**`11 verified, 0 errors`** shipped and **`15 verified, 0 errors`** under
`--cfg slb_twin`. The mutant is invisible to the verifier, to the verified twin,
to `spec.md`'s contract pin (the contract text does not change) and to gate
stages 5c/5c-req. What catches it is the `O3` identity pin against R4 — the call
target differs — and Miri, which reports *"`copy_nonoverlapping` called on
overlapping ranges"*. `NOTES.md` §8 (SLB-TRUSTED-ARGUMENT (b)) has always said
this; the table contradicted it. **A proof of a `requires` is not a proof that
the trusted body honours it**, and there is no non-overlap `requires` to state
because `ptr::copy` legitimately permits overlap.

Three further things make it worth doing, and they are all measurements rather
than arguments:

1. **It is UB with no out-of-bounds access.** The bounds guard
   `d + nrep > m -> reject` is in *every* rung, R1 included; nothing leaves any
   allocation. Every harm this project has measured before is spatial. This one
   is silent corruption inside a buffer the program owns, which tests the
   tooling as much as the ladder.
2. **It produced the project's first multi-clause trusted item and its first
   non-trivial verified twin.** Five patterns in, every trusted item had been a
   single-clause `get_unchecked`, so the twin mechanism had never been exercised
   on the case it was built for.
3. **`R2` and `R3` differ in one function body, and so do `R3` and `R4`.** The
   decomposition every earlier pattern had to establish afterwards is here by
   construction.

## The headline, before you read anything else

**The overlapping `memcpy` does not corrupt on this box, ever.** On glibc 2.39 /
x86-64, `dlsym("memcpy")` and `dlsym("memmove")` return **the same address**, and
that function carries a live `dst - src < n -> copy backwards` branch. Swept
across every glibc size regime, both compilers, both optimisation levels: zero
differing bytes.

So p08's security axis is not "C computes the wrong answer". It is **"UB that is
invisible without a sanitiser"** — and even the sanitiser is conditional: this
box's gcc default-enables `_FORTIFY_SOURCE=3`, which rewrites the call to
`__memcpy_chk`, which ASan does not intercept. `NOTES.md` §1 and §5 have the
measurements; `NOTES.md` §5's detection table is the security result.

## Layout

| file | what |
|---|---|
| `spec.md` | the contract every rung implements, plus the machine-readable pins |
| `model.py` | the independent Python reference the gate drives |
| `inputs/gen.py` | deterministic input generation |
| `c/kernel.c` | R1 — `memcpy`. THE BUG |
| `c/kernel_hardened.c` | R1h — `memmove`. One token apart |
| `safe_naive.rs` | R2 — a reverse indexed byte loop |
| `safe_tuned.rs` | R3 — `copy_within` |
| `unsafe.rs` | R4 — `ptr::copy` |
| `verus.rs` | R5 — R4 with the move behind a trusted, three-clause `ensures` |
| `controls/gen_controls.py` | the three controls + the detection table |
| `NOTES.md` | findings, adversarial behaviour, TCB tally, sticking points |
