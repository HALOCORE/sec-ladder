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
        shift += 7                      # wrapping (u32), in every rung
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
zero per-varint term. On band `b` — `nv` held at 8, varint bytes swept 8 → 80 —
the *fraction* `(R1h − R1)/R1` rises monotonically **5.08% → 13.57%** across all
ten rows, toward the `2/12 = 16.67%` the laws give as `bytes → ∞`. That is the
first honest counterexample in this project to *"the safety check amortises
away"* on the C side: it does not shrink with the input, it **grows**. (The two
matrix inputs read 11.89% on `small` and 11.11% on `large`; they are two
*shapes* — 112 varint bytes against 41 — and are quoted as levels, not as the
trend. `NOTES.md` 4b.) In wall clock **on `small`**, defended by a 30-layout
population per cell: **+7.14% on gcc (`P = 0.976`), +12.04% on clang
(`P = 0.998`)**, mode-matched, sign stable. `large`'s wall-clock row is weak
(`P = 0.676 / 0.829`) and is reported in `NOTES.md` 4c with its `P` and nowhere
else. ⚠ **Every other per-call `Ir` law here has a DOMAIN** — see the section
below the numbered list, and `NOTES.md` 4a0, before quoting one. This particular
difference is the exception and the section says why.

**3. Safe Rust with the guard deleted is BIT-IDENTICAL to C, at both opt levels
this benchmark measures.** Not "similar" — the same 64-bit integer, on four
adversarial blobs, from a rung with **zero `unsafe`** in it. The type system
does not see this bug and neither do the bounds checks.

**4. What does see it is four things, and all four are outside the 24-cell
matrix:** **UBSan** on the C side, **`-C debug-assertions=on`** and **Miri** on
the Rust side, and **Verus** — which raises `possible bit shift
underflow/overflow` on the operator itself, with no accessor and no
postcondition involved. ⚠ **Verus's obligation attaches to the operator
SPELLING**: `x.wrapping_shl(s)`, which computes exactly the masked shift the
buggy rung realises, **verifies with no obligation at all**, so "Verus catches
this" holds for a rung that writes `<<` and not for one that writes
`wrapping_shl`. That exclusion is a declared, priced, whole-pattern fiat
(`NOTES.md` 9). p18 is p09's mirror: p09's bug was invisible to a
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

## ⚠ Read this before any per-call `Ir` law in `NOTES.md`

**Every level law p18 publishes has a stated domain, and one of the pattern's own
committed inputs is outside it.** The kernel's cost depends on two control-flow
parameters as well as on bytes and varints:

| | what it means |
|---|---|
| **`cut`** | the last varint ran off the end of the window instead of ending on a terminator |
| **`brk`** | the window declared more varints than it holds, so the outer loop exits on `p == len` |

`small`, `large`, `truncating.bin`, every `adversarial-*` blob and all 34 blobs
of sweep bands b/v/x/y have **`cut = brk = 0`**. **`degenerate.bin` has both**,
and against the two-column law it misses by up to **+8.00 Ir/call** — which was
enough to reverse the *sign* of `R3 − R4` there. Sweep band **`t`** (8 blobs,
added at TASK_052 after TASK_051_REVIEW's blocker) varies the two independently;
the four-column law is exact over all 42 sweep blobs and predicts
`degenerate.bin`, which is in no band, on all eight cells. `NOTES.md` 4a0–4a3.

The per-byte hardening figure quoted in **2** above is the one law with no
domain to state: `cut` and `brk` cancel exactly between `c-gcc-h` and `c-gcc`
(and between the two clang cells), and `degenerate.bin` confirms it out of
domain — `410.018 − 374.018 = 36.000 = 2 × 18`.

Same *class* of defect as p14's (a law fitted inside one regime of a parameter
the design never varied — `.memory/01-ladder.md` finding 16), on a different
axis. It is not a new kind of mistake.

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
inputs/gen.py   deterministic generator: 8 matrix blobs + 5 sweep bands
controls/    mkcontract.py  splices the slb-contract block, --check verifies it
             gen_controls.py  every control, by exact-string substitution
             build_controls.sh / verify_controls.sh
             sweep_ir.py / fit.py     the swept laws, their DOMAIN, rank and
                                      hold-out analysis
             predict.py               the zero-free-parameter extrapolation
                                      (band y), hashed -- tamper-evidence, NOT
                                      an ordering proof; NOTES.md 8b1
             clayout.py               layout populations, C and Rust
             miri_exit_hole.py        regression check for harness/check.py's
                                      Miri exit-code comparison (TASK_052)
NOTES.md     the evidence, section by section
```

Run `harness/check.py p18` before believing any of it.
