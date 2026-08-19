# p07 — binary search

`nq` lookups into one window's sorted `u32` array, per kernel call. Family A,
the seventh pattern built.

**Two things make p07 different from every pattern before it, and they are the
reason it exists rather than the pattern count.**

1. **It is the first kernel here that is not a linear fold.** p01, p02, p05,
   p08, p16 and p17 all do `for each byte: acc = f(acc, b)`, so a per-call
   safety constant divided by `n` bytes goes to zero — which is *why* "safety is
   cheap" keeps coming out. Binary search does `ceil(log2(n+1))` probes over a
   `4n`-byte array: on `large.bin`, 6624 bytes read out of a 1 048 916-byte
   window (0.63%). **R3's per-probe bounds check is a fixed fraction of the
   kernel and cannot be amortised by making the input bigger.** Measured:
   `NOTES.md` §3c.
2. **It is the canonical unpredictable-branch kernel**, so it tests
   `.memory/01-ladder.md`'s "static instruction counts are not a cost model" and
   "`Ir` and wall clock can disagree in direction" on a kernel *designed* to
   make them disagree. This box has `perf_event_paranoid = 3` and no branch-miss
   counter, which makes a branchless control **mandatory rather than optional**:
   `NOTES.md` §11.

It is also the first pattern **built to the named-spelling standard natively**
rather than retrofitted with it. Its `idiom` declaration pins 34 backticked
spellings over 102 (spelling, rung) pairs with zero `pins_nothing` entries;
p01's and p05's pin nothing at all (`NOTES.md` §10c).

## The kernel

```
window = buf[off .. off+len)
n           u32 LE at window byte 0        DECLARED. ATTACKER DATA.
nq          u32 LE at window byte 4        DECLARED. ATTACKER DATA.
elements    u32 LE x n   at window byte 8       -- SORTED ASCENDING
queries     u32 LE x nq  at window byte 8 + 4*n
avail       = len - 8                      what actually ARRIVED

if len < 8:                    return 0
if n == 0 || nq == 0:          return 0
if 4*n + 4*nq > avail:         return 0     <<< THE CHECK. R1 omits this line.

for q in 0 .. nq:
    key = queries[q]
    lo = 0 ; hi = n                         <<< HALF-OPEN, see below
    found = u64::MAX
    while lo < hi:
        mid = lo + (hi - lo) / 2            <<< the overflow-safe midpoint
        v   = elements[mid]
        if v == key: found = mid ; break
        if v <  key: lo = mid + 1
        else:        hi = mid
    acc = acc*31 + (found + 1)
return acc*31 + n*nq
```

Full contract, pins and rationale: `spec.md`.

## The C bug, and the two the catalogue did not name

**R1 omits exactly one line: `4*n + 4*nq > avail`.** CWE-129 turning into
CWE-125, with CWE-190 one width down — the same family as p05's, and a
**different shape**. p16's and p05's overruns walk *forward, one byte at a time,
starting one past the end*; p17's runs *backward but in bounds*. Binary search's
first probe is at element `n/2`, so R1's first out-of-bounds access is `2*n`
bytes past the window with **nothing touched in between** — a single wild jump.
Both regimes ship:

| input | what R1 does | plain build | ASan |
|---|---|---|---|
| `adversarial-count` (n = 4096 declared, 16 present) | reads ~16 KiB past an 88-byte window — still inside the heap | **exit 0, plausible wrong number** | `heap-buffer-overflow` |
| `adversarial-width` (n = 2^30) | reads 4 GiB past | **SIGSEGV** | `SEGV on unknown address` |

**`.memory/06-catalogue.md` lists p07's bug as midpoint overflow `(lo+hi)/2`.
That row is wrong, and `NOTES.md` §0 has the arithmetic.** `n` is a u32 header
field, so `lo + hi <= 2*(2^32 - 2) = 8 589 934 588` — 2.1e9 times short of
`2^64`. The midpoint sum cannot wrap for any input this wire format can express;
RAM is not the binding constraint, the field width is. The cheapest index type
that *could* wrap is `int`, and it needs 4 GiB of u32 elements. The overflow
that **is** reachable is in the other multiplication: `4*n + 4*nq` needs 35 bits
and a 32-bit check waves `adversarial-width` straight through
(`NOTES.md` §6, and note that unlike p05 the *unsigned* 32-bit spelling breaks
too).

**And there is a third bug, one spelling away from the shipped kernel.** The
textbook inclusive form — `hi = n - 1`, `while lo <= hi`, `hi = mid - 1` —
underflows `size_t` at `mid == 0`, which any key below `elements[0]` reaches.
Built from `c/kernel_hardened.c` by exact-string substitution
(`controls/gen_controls.py`) it **SIGSEGVs on p07's own `small.bin`**:
well-formed input, length check present, no attacker. That is why the half-open
bounds are `idiom.required` and not merely conventional, and it is why
`adversarial-zero.bin` exists — the `n == 0` guard is load-bearing memory safety
in the inclusive spelling and completely dead in the shipped one.

## What was measured

`-O3 isolated`, kernel-exclusive `Ir`, wall clock pinned and interleaved:

| | `Ir` vs R4, small | ns vs R4, small | `Ir` vs R4, large | ns vs R4, large |
|---|---:|---:|---:|---:|
| R2 safe-naive | +87.8% | *withdrawn* | +87.7% | *withdrawn* |
| R3 safe-tuned | +45.9% | +13.0% | +47.0% | +1.6% |
| R5 verus | 0.0% | −0.0% | 0.0% | +0.3% |

**The `Ir` columns are the result, and the swept laws behind them are exact
integers with zero residual over 113 sweep blobs**:

```
R2 - R4 = 36 + 11.0000*nq + 11.0000*probes     (the four per-byte index checks)
R3 - R4 =  9 +  4.0000*nq +  6.0000*probes     (one two-sided slice range check)
```

both derived from the disassembly with the per-probe coefficients counted rather
than fitted (`NOTES.md` §3a), and re-verified out of sample on 30 fresh blobs
under six query distributions.

**R2's two `ns` cells are withdrawn** (`NOTES.md` §3, §11e). They were published
as "+28.0% on `small`, +3.5% on `large` — an 8x difference in the conversion
factor". Built at 30 code layouts, `safe_naive`'s wall clock is **bimodal**:
17.708 ms or 13.931 ms on `small`, selected by whether its **73-byte inner loop
occupies 3 or 4 32-byte instruction-fetch windows**, so R2-vs-R4 is **+26.42% in
one mode and −0.93% in the other** — on machine code identical but for call
displacements (`md5_fn_norel` equal) at an identical executed instruction count
(12346.57 Ir/call at every layout). Every counter this box can produce — `Ir`,
`Dr`, `D1mr`, `DLmr`, simulated `Bcm` — is equal across that boundary to **≤6
events in 10⁸**, because callgrind models no part of the front end. The
partition was confirmed **out of sample on 20 fresh layouts with the predictions
hashed before timing**. ("Bit 4 of the kernel's entry address" is a *proxy* for
the window count and only works because every kernel here is 16-byte aligned;
`NOTES.md` §11e.) **R3's `ns` cells survive** mode-matching: +11.12% / +17.37%
on `small`, +0.85% / +2.52% on `large`. ⚠ And R4 itself has an **8% layout band
with no mode and no explanation** (§11f), which is larger than several gaps in
the table above.

**R3's tax is 46.6% of the kernel at n = 16 385 and still rising**, toward an
asymptote of `6 / (12 + f_lo)` ∈ **[46.15%, 50.00%]** — 47.99% on the shipped
50/50-hit workload, and workload-dependent because `f_lo`, the fraction of probes
taking the `lo = mid + 1` arm, is data. **p07 is the first pattern where R3's tax
has no axis along which it amortises**: p16's and p17's is a per-*call* constant
(0.00000 Ir/byte swept — the reslice sits outside the fold loop) and p05's is
`O(nrow)`, which vanishes along `ncol`; p07's vanishes along nothing, because
there is no inner loop to hoist it out of. It is **not** "the first
counterexample to safety is cheap" — `.memory/01-ladder.md` finding 4 already
carries p16's swept **R2** tax of 4.25 Ir per folded byte, whose fraction also
rises.

**The branch result** (`NOTES.md` §11): every source-level branchless spelling
is converted back to a branch by LLVM's `X86CmovConverterPass` and measures
*exactly* the shipped rung. The control that works is the pass itself —
`-C llvm-args=-x86-cmov-converter=false` on the unchanged source — which emits
2 `cmov`, executes **+10% instructions** and runs **9–18% faster**, with the
bands separated from a seven-alignment layout control. `callgrind --branch-sim`
then measures what the control was built to infer: **0.586 simulated mispredicts
per probe branchy against 0.129 branchless**, with `D1mr` identical, and a
symbol-by-symbol diff showing 559 symbols of which exactly one differs.

**R5 is free and verified first try**: `10 verified, 0 errors`, R4 ≡ R5
byte-identical at `-O3` (`md5_fn 4f8c443684e1`), and p07's kernel needs **zero**
nonlinear arithmetic where p05's needs two `by (nonlinear_arith)` blocks —
because every multiplication here is by the literal 4. What it pays instead is a
loop with a `break`, and the invariant *"the search from here is the whole
search"*.

## Files

```
spec.md                the contract + the hashed slb-contract pins
model.py               the independent Python reference (two implementations)
inputs/gen.py          deterministic inputs; --sweep adds 113 blobs over log2 n
c/kernel.c             R1  -- no length check. THE BUG.
c/kernel_hardened.c    R1h -- the same, plus that one line
c/main.c               the C driver loop
safe_naive.rs          R2  -- four bounds checks per probe
safe_tuned.rs          R3  -- one, via a 4-byte reslice
unsafe.rs              R4  -- none
verus.rs               R5  -- R4's exec code + 10 discharged obligations
controls/gen_controls.py   the 15 derived controls (branchless, R3/R4
                           respellings, both R4 candidates' Verus twins, and
                           the three C bug variants)
NOTES.md               everything that was measured
```
