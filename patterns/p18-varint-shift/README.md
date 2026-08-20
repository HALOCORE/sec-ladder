# p18 — LEB128 varint decoder

**The bug is undefined behaviour that touches no memory, and it is the first one
in this project that is.** Every earlier pattern's defect is spatial — an
out-of-bounds read or write — or logical-but-in-bounds. p18's is an
**out-of-range shift count**, which addresses nothing, allocates nothing and
stores nothing, and which returns a silently wrong integer.

```
byte 0..4   nv   u32 LE   DECLARED varint count     ATTACKER DATA
byte 4..    the varint bytes                        ATTACKER DATA
VBITS = 64                the accumulator's width

for each of nv varints:
    val = 0 ; shift = 0 ; nb = 0
    while p < len:                      # BOUNDED, in every rung
        c = buf[off + p] ; p += 1 ; nb += 1
        if shift < VBITS:               # <<< THE SAFETY LINE. R1 omits THIS.
            val |= (c & 0x7f) << shift
        shift +=32 7                    # wrapping, in every rung
        if c & 0x80 == 0: break
    acc = acc*31 + val ; acc = acc*31 + nb
return acc*31 + nv
```

`shift` is `7 * nb`, and `nb` is set by the attacker's *continue bits*, not by
any declared length. A canonical `uint64_t` encoding is at most **ten** bytes
and its last shift is exactly **63** — in range. The **eleventh** byte is the
first one that is not, and nothing in the wire format forbids one.

## What is new here

**1. The bound is a SHIFT COUNT.** Every earlier bound in this project decides
whether an *address* is inside an *allocation* — p02's, p16's and p17's compare
a declared length to a buffer extent, p11's and p13's are about a terminator,
p14's is a count of a byte value against a table's extent, p09's is a bit index
against a word count. p18's decides whether an **arithmetic operation is defined
at all.** No rung of p18 ever reads or writes out of bounds, on any input.

**2. The safety line runs ONCE PER INPUT BYTE, so its cost does not amortise.**
`c-gcc-h − c-gcc = 2.00 · varint bytes`, exactly, with a zero intercept and a
zero per-varint term — 11.89% of the kernel's instructions on `small` **and
11.11% on `large`**, because both the numerator and the denominator are per-byte
terms. That is the first honest counterexample in this project to *"the safety
check amortises away"* on the C side. In wall clock, defended by a 30-layout
population per cell: **+7.14% on gcc (`P = 0.976`), +12.04% on clang
(`P = 0.998`)**, mode-matched, sign stable.

**3. Safe Rust with the guard deleted is BIT-IDENTICAL to C, at both opt levels
this benchmark measures.** Not "similar" — the same 64-bit integer, on four
adversarial blobs, from a rung with **zero `unsafe`** in it. The type system
does not see this bug and neither do the bounds checks.

**4. What does see it is four things, and all four are outside the 24-cell
matrix:** **UBSan** on the C side, **`-C debug-assertions=on`** and **Miri** on
the Rust side, and **Verus** — which raises `possible bit shift
underflow/overflow` on the operator itself, with no accessor and no
postcondition involved. p18 is p09's mirror: p09's bug was invisible to a
memory-safety proof and to everything else; p18's is invisible to the
*postcondition* and caught by an obligation that is not part of the
specification.

**5. `O0d` — `-C debug-assertions=on` — has existed since p01 and had never been
measured on any pattern.** p18 measures it, and the result is not the one the
axis's name suggests: **at `-O3` the flag costs the shipped tuned safe rung 3.00
instructions per kernel call and NOTHING per byte**, because on a program that
*has* the guard the inserted assertion is provably dead. On the program that
does not have it, it cannot be folded away and it panics.

**6. A second bug that nothing catches at all.** A **ten**-byte varint ending at
shift 63 with payload `0x7f` loses six bits to the shift itself — in range, no
undefined behaviour, guard never fires. `truncating.bin` is that input: every
rung agrees, ASan/UBSan clean, `debug-assertions` clean, Miri clean, the proof
discharges, and the decoded number is not the number that was written. p17's
limit arriving on arithmetic instead of on a range, and the catalogue row's
*"truncation"* half.

**7. And the checksum cannot see bug 1 on every input.** `|=` is idempotent, so
a payload wrapped round into a bit that is already set changes nothing.
`adversarial-sat.bin` is a twenty-byte varint of `0x7f` payloads: ten undefined
shifts execute, UBSan fires, and **all eight cells print the same number.** That
is a property of the *bug*, not of the fold, and no choice of fold could repair
it.

## The rungs

| rung | file | what it is |
|---|---|---|
| R1 | `c/kernel.c` | idiomatic C99, **no shift bound** — the bug |
| R1h | `c/kernel_hardened.c` | the same C plus `if (shift < VBITS)`, one line |
| R2 | `safe_naive.rs` | the mechanical safe port, indexed |
| R3 | `safe_tuned.rs` | safe, window reslid once, explicit cursor |
| R4 | `unsafe.rs` | R2 with the bounds checks removed |
| R5 | `verus.rs` | R4's exec code, plus the proof |

R4 and R5 are **byte-identical at `-O3`** (`identity: exact`) and `norel` at
`-O0`, and the pin has **no measured price on p18** — unlike p06's and p14's,
which each had to bind a value to a local because R5's store is a call. p18 has
no store at all.

**TCB: 3 items, 1 with a `requires`** — 1 U-license + 2 infra, 0 V-gap. The
smallest trusted base of any pattern here, for a structural reason: the kernel
performs exactly one kind of memory access, a byte read of the input window.
And that item **has nothing to do with the pattern's bug** — weakening its
`requires` neither admits nor excludes R1's defect (`NOTES.md` 6a, 10a).

## Files

```
spec.md      the contract every rung implements + the machine-readable pins
model.py     the independent Python reference (unbounded ints + a final mask,
             against the helper's explicit per-byte width test)
inputs/gen.py   deterministic generator: 8 matrix blobs + 4 sweep bands
controls/    mkcontract.py  splices the slb-contract block, --check verifies it
             gen_controls.py  every control, by exact-string substitution
             build_controls.sh / verify_controls.sh
             sweep_ir.py / fit.py     the swept laws, rank and hold-out analysis
             predict.py               pre-registered extrapolation, hashed
             clayout.py               layout populations, C and Rust
NOTES.md     the evidence, section by section
```

Run `harness/check.py p18` before believing any of it.
