# p47 — constant-time tag comparison: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

⚠ **The fenced `slb-contract` block at the bottom is written by
`controls/mkcontract.py`, which reads the shared named-spelling paragraph out
of a DONOR pattern's `spec.md` and refuses to write anything if the result does
not satisfy `harness/check.py::named_spelling_problem`.** It does not carry its
own copy of that paragraph, which is the defect
`patterns/p27-handle-table/controls/mkspec.py` shipped (`.memory/05-layout.md`).

## What makes p47 different from the other eighteen

**Every other pattern in this tree asks what safety costs. p47 asks a question
the ladder is structurally unable to answer, and that is the result.**

| | every other pattern | p47 |
|---|---|---|
| what `c/kernel.c` does wrong | reads outside an allocation, or returns a wrong answer | **nothing, in the value domain** |
| stage 2 (checksums) sees it | on some input | **never** |
| stage 7 (ASan+UBSan) sees it | usually | **never** — every input is `clean` |
| Miri sees it | sometimes | **never** |
| R5's `ensures` excludes it | yes | **no — and it cannot be strengthened to** |
| what does see it | several things | **`Ir` under callgrind, and the disassembly** |

R1 leaks the first-mismatch position of a secret through its instruction count.
R1h does not. **Both return the same value on every input this benchmark will
ever run**, and `harness/check.py` requires exactly that, so the bug can only
be recorded by the two instruments the pattern was designed around: a
deterministic instruction count that is a function of the input, and a static
read of the shipped machine code.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and the two sides carry exactly the
same information: `&[u8]` is a pointer and a length, and C spells the pair out.
C is handed the blob length and *both* C rungs ignore it — p06's, p10's, p12's,
p14's and p27's shape. (The arity mismatch is why `spec.md` carries a
`driver.call_args` pin.)

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0..4     ntag   u32 LE    DECLARED comparison count       ATTACKER DATA
byte 4..8     tlen   u32 LE    DECLARED tag length             ATTACKER DATA
byte 8..      ntag records of 2*tlen bytes each:
                u8[tlen]  secret       the value being protected
                u8[tlen]  candidate    what the attacker supplied
data_start = 8
MATCH = 7                     what an equal comparison folds
MISS  = 251                   what an unequal comparison folds
```

`MATCH` and `MISS` are compile-time constants in every rung. `ntag`, `tlen` and
every tag byte come from the file.

**`k` — the first-mismatch position — is a property of the FILE and no rung
computes it.** `inputs/gen.py` places it and prints it; `model.py` recovers it
and reports it in `describe()`. It is the independent variable of every law
this pattern publishes, and nothing in the kernel is told what it is.

## Semantics

```
if len < 8:                                   return 0
ntag, tlen from the header
if ntag == 0 || tlen == 0:                    return 0

acc = 0 ; p = 8 ; o = 0
while o < ntag and len - p >= 2*tlen:         # THE WINDOW GUARD, every rung
    eq = COMPARE(buf[off+p       .. off+p+tlen],
                 buf[off+p+tlen  .. off+p+2*tlen])      # <<< THE TIMING LINE
    acc = acc *64 31 +64 (MATCH if eq else MISS)
    p += 2*tlen
    o += 1
return acc *64 31 +64 o
```

`*64` and `+64` are wrapping `u64` operations.

Load-bearing, do not "improve":

- **The fold folds the VERDICT and never a tag byte.** Two windows with the
  same verdict sequence and different `k` therefore produce the *same checksum
  in every rung*. That is what makes `adversarial-k000.bin` and
  `adversarial-klast.bin` a timing row rather than a correctness row, and a
  fold that could see a tag byte would turn p47 into a different pattern.
- **`o` is folded last**, so a rung that performed a different number of
  comparisons cannot produce the same checksum.
- **The window guard is in every rung, R1 included, and is subtraction-first.**
  `p <= len` is maintained by the guard itself so the subtraction cannot wrap;
  the additive `p + 2*tlen <= len` can overflow and Verus rejects it.
- **p47 models no spatial bug.** Ten of the eighteen patterns already do
  (`.memory/06-catalogue.md`), and an eleventh here would confound the axis
  this pattern exists for.

## The bug

`c/kernel.c` writes

```c
if (memcmp(buf + off + p, buf + off + p + tlen, tlen) == 0)
```

and `c/kernel_hardened.c` writes

```c
d = 0;
for (i = 0; i < tlen; i++)
    d |= (uint8_t)(buf[off + p + i] ^ buf[off + p + tlen + i]);
if (d == 0)
```

CWE-208, observable timing discrepancy. `memcmp` stops at the first differing
byte, so how long the call takes — and, on this project's primary metric, how
many instructions it executes — is a function of how many leading bytes of the
secret the attacker guessed right. The attack is the standard one: hold `tlen`
and everything else fixed, vary the candidate, and read `k` off the clock, one
block at a time, in `O(256 · tlen)` queries instead of `O(256^tlen)`.

### ⚠ The catalogue's stated bug class is OVERTURNED, with the measurement

`.memory/06-catalogue.md` says *"timing side channel — **compiler may
reintroduce a branch**"*. The second half is **false on this toolchain** and
p47 is not built on it. Measured before any cell was written (`NOTES.md` 0):
five accumulate spellings (or-accumulate, boolean flag, and-accumulate, match
count, wide-word or) × {gcc 13.3.0, clang 22.1.6} × {`-O1 -O2 -O3 -Os -Oz`},
plus rustc 1.97.1 at `-C opt-level={1,2,3,s,z}`, in a free function and
`#[inline(always)]`-inlined into a caller that **branches on the result**, and
for fixed-size `[u8;16]`/`[u8;32]` as well. **Not one of them grew a
data-dependent exit.** gcc's boolean-flag variant becomes `cmovne`; clang's
vectorises; the fixed-size Rust folds become `pcmpeqb ; pmovmskb ; xor ;
cmove`.

So the adversary here is **not** the optimiser. It is the *idiom*: `memcmp` and
`==` leak by definition and need no compiler help to do it. That is the fourth
catalogue row this project has overturned and the third it has kept.

### ⚠ And R1-clang and R2 call the same libc routine

clang `-O3` rewrites `memcmp(a, b, n) == 0` into a call to **`bcmp`**
(`R_X86_64_JUMP_SLOT bcmp` on the shipped `c-clang` binary), which is the
identical symbol rustc emits for `a == b` on two slices
(`R_X86_64_GLOB_DAT bcmp`, reached from the `kernel` symbol on the shipped
`safe_naive` binary). gcc emits `memcmp`. **A `c-clang` vs `safe_naive`
difference is therefore a difference in what the caller does around one shared
glibc routine, not a language difference** (`.memory/03-measurement.md`, "name
the routine"; p11 and p13 are the two patterns that learned this the hard way).
`NOTES.md` 4 separates them.

**No p47 cell contains a `rep`-string instruction** — checked on all eight
shipped kernels — so `.memory/03-measurement.md`'s `rep`-string counting hazard
is empty here, and glibc's `bcmp` on this box exits at **32-byte** granularity,
which is what makes `Ir(k)` a staircase rather than a line.

## The adversarial rows, and what one even means here

**A timing pattern has no crash and no wrong answer, so an adversarial row
cannot be either.** What p47 ships instead is a *pair*:

| input | shape | what it shows |
|---|---|---|
| `adversarial-k000` | 8 comparisons, `tlen` 128, every one mismatching at byte **0** | the attacker's guess is wrong immediately |
| `adversarial-klast` | the same seed, the same shape, every one mismatching at byte **127** | the attacker has guessed 127 of 128 bytes |
| `adversarial-equal` | the same shape, every comparison **equal** | the attacker has guessed the whole secret |
| `adversarial-stride7` | a 7-byte window | the driver's `stride_w >= 8` guard skips the loop; every rung prints 0 |

`adversarial-k000` and `adversarial-klast` are **byte-different files that
print an identical checksum on all eight cells** (`15618968502624590848`), on
every optimisation level and both inline modes. Their difference is recorded in
`Ir` and nowhere else, per rung, in `NOTES.md` 5. That is p17's shape one level
up: memory-safe, functionally correct, provably correct, and leaking.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == tag_fold(buf, off, len)
```

`tag_fold` is the spec function; `model.py` is its independent Python twin —
and independent in the way that matters here: **`model.py`'s simulation decides
each comparison with Python's own early-exiting `bytes.__eq__` and its helper
`tag_fold` decides it with the constant-time or-accumulate, byte by byte.** The
two implementations disagree about how long they take and agree about what they
return, on every call of every input. That is the pattern's subject, and the
gate checks the two decision procedures against each other every time it runs.

The `requires` is **structural** — about the shape of the buffer the driver
built, not about its contents — so it holds on every input this benchmark runs,
`adversarial-*` included. It is **ONE clause**, as on p03, p06, p10, p11, p12,
p14 and p27 and unlike p17.

### ⚠ What the `ensures` cannot say, and why that is the deliverable

The `ensures` is the **functional** postcondition, and **the leaking rung
satisfies it too.** This is not a weakness in the specification and it cannot
be repaired by strengthening it:

- `tag_fold` denotes the **value** the kernel returns. p47's defect does not
  change the value.
- A timing property is a statement about the **trace**, and Verus's assertion
  language has no term denoting a trace, no cost model, and no way to quantify
  over the *two* executions a non-interference property compares.
- The property is not even a property of this program. It is a property of the
  machine code, which LLVM chooses after Verus has finished — the same hazard
  as `.memory/06-catalogue.md`'s *"a text pin binds the source, not the
  object"*, with the prover in place of the pin.

`controls/proof_mutants.py`'s `m_leak` substitutes an early-exiting comparison
into `verus.rs` and it **verifies**, at the same obligation count, with this
same `ensures`. See `NOTES.md` 9 for what *can* be proved.

## The trusted base

**Three** `external_body` items, **one** of them with a `requires`:
`buf_get_unchecked` (the spatial accessor every unsafe rung in this project
ships), `load_input` and `emit` (infra, in every pattern here). The
classification is **1 U-license + 2 infra + 0 V-gap**. p47's kernel performs
exactly one kind of memory access — a byte read of the input window — with no
scratch, no output buffer, no allocation and no write of any kind.

⚠ **On p47 the trusted item's `requires` has nothing to do with the pattern's
bug.** `c/kernel.c` violates no bound, so `i < v@.len()` — and every other
obligation in `verus.rs` — is silent about it. `NOTES.md` 6 and 9.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p47's payload is p10's, p27's and eight others':

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the windows; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes`, reused verbatim,
with **nothing added to `common/` for p47**.

## Driver loop

Identical in all eight rungs, between the `SLB-DRIVER-BEGIN` /
`SLB-DRIVER-END` markers, and byte-for-byte p10's. `harness/check.py`
normalises every copy — the C one included — and diffs it against
`driver.canonical` in the block below.

```
n_blob := bytes.len()
buf    := bytes
acc    := 0
if stride_w >= 8 and stride_w <= n_blob:
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

`stride_w >= 8` because p47's window header is the two u32 fields.
`adversarial-stride7.bin` attacks it.

`k` is derived from `acc`, and `acc` from the previous call's result, so call
*i+1* cannot begin until call *i* has returned. Nothing to CSE, nothing to
hoist, no `black_box` and no `asm volatile` — and `black_box` is `forbidden` in
the block below precisely so that a constant-time rung cannot be rescued by one.

**Every sweep blob is window-homogeneous**: every window in it has the same
`(ntag, tlen, k, nmatch)`, so whichever window the Lemire index picks the
kernel does the same work, and a swept `Ir` law is exact rather than an average
over a window mix. `inputs/gen.py` checks that window 0 returns non-zero, for
`.memory/01-ladder.md`'s absorbing-state reason.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the
pattern when the tree stops matching it. p01's `spec.md` explains what each pin
closes; what is worth saying here is the arithmetic behind the two obligation
counts.

| pin | why |
|---|---|
| `verus.obligations` = 12 | **`MATCH` 1 + `MISS` 1 + `xacc` 1 + `twalk` 1 + `kernel` 3 + `main` 5 = 12**, every term measured with `--verify-function <name> --verify-root`. `main` is **5**, which is what all seventeen other patterns that record the term record for the identical driver; ⚠ an earlier draft of this row said 5 was the exception and 4 the rule, and that was backwards (TASK_064_REVIEW major 2 — the one pattern recording 4 was p27, whose own decomposition then summed to 14 against a pinned 15). `u32_at` and `tag_fold` are non-recursive spec fns and report 0; `xacc` and `twalk` are recursive and carry one termination query each; the three `external_body` items report 0. `kernel`'s 3 is 1 body + 1 per loop body (**two** loops: the comparison walk and the tag loop). |
| `verus.twin_obligations` = 13 | the count under `--cfg slb_twin`. **12 shipped + 1**, the single trusted item inside the twin regime. |
| `identity` `O3: exact`, `O0: norel` | and on p47 it carries a second job: it is what makes *"the proved rung leaks"* a statement about a **binary**. R5's object is R4's object byte for byte, and R4's object is disassembled in `NOTES.md` 1. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. **Miri is expected to be, and is, entirely silent about p47's bug** — it checks the unchecked reads, which are the thing `c/kernel.c` gets right. |
| `forbidden: volatile` | the received hardening idiom, measured **6.35× dearer** and unnecessary here; shipped as the control `h_vol` so the figure is checkable rather than asserted. |
| `forbidden: black_box` | a constant-time rung rescued by an optimisation barrier would be measuring the barrier. |
| `forbidden: fold(0u64` | the same algorithm with a `u64` accumulator moves 4 bytes per iteration instead of 32 — a codegen accident that would land in the safety column. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == tag_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (tag_fold). p47's bindings are the READ-ONLY set p03, p06, p10, p11, p12, p14, p16, p17, p05, p07 and p27 use: the kernel writes nothing and allocates nothing. **THE `ensures` IS THE FUNCTIONAL ONE AND IT IS SATISFIED BY THE LEAKING RUNG TOO.** That is not an oversight and it cannot be repaired by strengthening it: `tag_fold` is a statement about the VALUE the kernel returns, p47's defect does not change the value, and a timing property is a statement about the TRACE -- which instructions ran, and how many -- for which Verus's assertion language has no term at all. It also is not a property of this program: it is a property of the machine code LLVM chooses after Verus has finished. controls/proof_mutants.py's `m_leak` substitutes an early-exiting comparison into verus.rs and it VERIFIES, at the same obligation count, with this same `ensures`. **So the top rung of this ladder certifies a leaking kernel, and that is p47's deliverable rather than its gap** -- p17 (provably memory-safe and still leaking) one level up. What the `ensures` deliberately does NOT say is that `ntag` or `tlen` is honest: a precondition about the contents of a file is one no honest loader can discharge (`.memory/02-bench-rules.md`), and `twalk`'s own window guard is what stops the walk instead, so degenerate.bin and every adversarial row are INSIDE the verified domain and every rung agrees with model.py on all of them.",
  "idiom": {
    "required": [
      {
        "c": "THE TIMING LINE, and the whole of what c/kernel.c does differently: `memcmp(buf + off + p, buf + off + p + tlen, tlen) == 0`. c/kernel_hardened.c writes the or-accumulate instead and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.",
        "rust": "THE TIMING LINE at R2, the idiomatic safe-Rust comparison and the LEAKING one: `if a == b {` in safe_naive.rs. It lowers to a `bcmp` call -- one R_X86_64_GLOB_DAT bcmp relocation reached from the kernel symbol on the shipped binary -- which is the same glibc routine c-clang enters. safe_tuned.rs, unsafe.rs and verus.rs write the or-accumulate instead."
      },
      {
        "c": "THE CONSTANT-TIME LINE, present in c/kernel_hardened.c and ABSENT from c/kernel.c: `d |= (uint8_t)(buf[off + p + i] ^ buf[off + p + tlen + i]);`. Every byte of the tag is read on every call whatever the data says.",
        "rust": "THE CONSTANT-TIME LINE. In safe_tuned.rs it is the fold, spelled with the `u8` accumulator the why key argues for: `fold(0u8, |acc, (x, y)| acc | (x ^ y))`. In unsafe.rs and verus.rs the language forces the other spelling -- there is no iterator over `get_unchecked` -- so those two write the same accumulation as an indexed loop and the entry scopes to R3. safe_naive.rs does NOT have it, and that is the pattern."
      },
      {
        "c": "the WINDOW GUARD, present in BOTH C rungs including the buggy one, so p47 models no spatial bug: `while (o < ntag && len - p >= 2 * tlen) {`. Subtraction-first, because p <= len is maintained by the guard itself so the subtraction cannot wrap, while the additive form can overflow and Verus rejects it.",
        "rust": "the window guard, subtraction-first, in all four Rust rungs: `while o < ntag && len - p >= 2 * tlen {`."
      },
      {
        "c": "the VERDICT FOLD, and it may not see a tag byte -- see the why key: `acc = acc * 31 + MATCH;` and `acc = acc * 31 + MISS;` in both C rungs.",
        "rust": "the verdict fold in all four Rust rungs, spelled with the literal multiplier: `.wrapping_mul(31).wrapping_add(MATCH)` and `.wrapping_mul(31).wrapping_add(MISS)`."
      },
      {
        "c": "the CURSOR ADVANCE is by a whole record, so a rung that compared overlapping or misaligned tags cannot produce the same verdicts: `p += 2 * tlen;` in both C rungs.",
        "rust": "the cursor advance in all four Rust rungs: `p = p + 2 * tlen;`."
      },
      {
        "c": "the header is decoded with + and * and never with | and <<, so the whole specification stays inside linear arithmetic (.memory/04-verus.md): `256 * (size_t)buf[off + 1]` in both C rungs.",
        "rust": "the header decode, in all four Rust rungs: `256 *`."
      },
      "the number of comparisons actually performed is folded LAST, so a rung that stopped at a different point cannot produce the same checksum: `o` appears in the return expression of all eight rungs.",
      "the two header fields are rejected together and before any read of a tag, so no rung can divide by or index with zero: `ntag == 0` appears in all eight rungs."
    ],
    "forbidden": [
      "`volatile`",
      "`black_box`",
      "`fold(0u64`",
      {
        "rust": "`memcmp`"
      },
      {
        "rust": "`bcmp`"
      },
      {
        "rust": "`libc`"
      },
      "`starts_with`",
      "`iter().eq(`",
      "`subtle`",
      "`chunks_exact`",
      "`from_le_bytes`",
      "`copy_from_slice`",
      "`position(`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all eight rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ON p47 THE PINNED SPELLING IS THE SECURITY PROPERTY ITSELF, WHICH IS NEW. Every other pattern here pins spellings so that a COST comparison is between comparable programs; p47 pins them because the difference between `memcmp(a, b, tlen) == 0` and an or-accumulate over every byte IS the pattern, and it is invisible to every other check in the gate -- both expressions compute the same predicate, return the same value on every input, are memory-safe, are ASan/UBSan/Miri clean, and satisfy the same `ensures`. THE PIN IS THEREFORE THE ONLY THING IN THIS TREE THAT RECORDS WHICH RUNGS LEAK. WHY THE ACCUMULATOR IS NOT `volatile`, AND WHY `volatile` IS FORBIDDEN RATHER THAN MERELY UNUSED: the received advice for this idiom is to force the accumulator into memory. Measured on this toolchain it is unnecessary -- the plain accumulate is already constant in the first-mismatch position, to the instruction, at every optimisation level tested -- and it costs 6.35x, because it defeats vectorisation entirely in both gcc and clang. A cell that reached for it would be 6.35x dearer for no security gain and would make the R1-vs-R1h column mean something else; controls/gen_controls.py ships it as `h_vol` so the figure is checkable. WHY `fold(0u8` IS PINNED AND NOT MERELY `fold`: the identical algorithm with a `u64` accumulator lowers to a `movzwl/punpcklbw/punpcklwd/punpckldq` widening loop moving 4 bytes per iteration instead of 32, because LLVM vectorises the zero-extension rather than the xor. It is still constant-time; it is five times the work, and a rung that reached for it would put a codegen accident into the safety column. WHAT IS DELIBERATELY NOT PINNED is how the two tags are ADDRESSED -- R2 and R3 reslice with `&buf[a..b]` and R4/R5 index `buf` directly with `get_unchecked` -- because that is the SAFETY axis and it is the axis the R3-side span is measured along (../NOTES.md 8). R2 and R3 are pinned to the SAME addressing on purpose: they carry the identical panic-path structure on the shipped binaries (two `slice_index_fail` and eight `panic_bounds_check` call sites each), so `R2 - R3` differences the comparison idiom with the safety term cancelled exactly, and it is the only pair in this pattern that isolates the leak from everything else. WHY THE FOLD MAY NOT MIX IN A TAG BYTE: `acc = acc*31 + (MATCH|MISS)` folds the VERDICT and the number of comparisons performed and nothing else, so two windows with the same verdict sequence and different first-mismatch positions produce the SAME CHECKSUM in every rung. That is what makes `adversarial-k000.bin` and `adversarial-klast.bin` a timing row rather than a correctness row; a fold that could see a tag byte would turn p47 into a different pattern. WHY `memcmp` IS REQUIRED IN c/kernel.c AND FORBIDDEN EVERYWHERE ELSE: it is the bug. clang -O3 rewrites `memcmp(a,b,n) == 0` into a call to `bcmp`, which is the identical symbol rustc emits for `a == b` on slices, so the c-clang cell and the safe_naive cell enter one glibc routine and any difference between them is a LIBRARY difference (`.memory/03-measurement.md`, name the routine). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
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
      "verus.rs": 12
    },
    "twin_obligations": {
      "verus.rs": 13
    },
    "obligations_note": "12 = MATCH 1 + MISS 1 + xacc 1 + twalk 1 + kernel 3 + main 5, each term MEASURED with `./verus_run.py verus.rs --verify-function <name> --verify-root` and not predicted. The zero terms are checkable the same way: u32_at and tag_fold are NON-RECURSIVE spec fns and report 0, while xacc and twalk are RECURSIVE and carry one termination query each; buf_get_unchecked, load_input and emit are external_body and report 0. TWO `const`s carry one query each (`.memory/04-verus.md`: a `const` inside verus! is its own obligation). kernel's 3 = body + TWO loop bodies (the comparison walk and the tag loop). main's term is 5, which is what **every other pattern in this tree that records the term also records** -- seventeen of them, p03 p04 p05 p06 p07 p08 p09 p10 p11 p12 p13 p14 p16 p17 p18 p27 -- for the byte-identical driver loop; p01 and p02 record no term. ⚠ **AN EARLIER DRAFT OF THIS NOTE SAID 5 WAS THE EXCEPTION AND 4 THE RULE, AND THAT WAS BACKWARDS** (TASK_064_REVIEW major 2). The one pattern that recorded 4 was p27, whose own decomposition then summed to 14 against a pinned and measured total of 15; `./verus_run.py patterns/p27-handle-table/verus.rs --verify-function main --verify-root` reports 5, TASK_065 corrected p27's note, and no pattern here records 4. ⚠ The \"shared off-by-one note\" other patterns carry is also not about the value 4: it is a PREDICTION-MINUS-ONE claim about `.memory/04-verus.md`'s rule of thumb (p10: \"would predict 6 and Verus reports 5\"), so \"it does not transfer\" was denying something no pattern claims.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 12 shipped + 1, the single trusted item inside the twin regime being slb_twin_buf_get_unchecked. `load_input` and `emit` are outside the regime (external_body with no `ensures` and no `unsafe` body) and have no twins.",
    "unsafe_justifications": {},
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "xacc": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "twalk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "tag_fold": {
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
            "r == tag_fold(buf@, off as int, len as int)"
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
      "if stride_w >= 8 && stride_w <= n_blob",
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
    "note": "work_per_call is **BYTE COMPARISONS** -- `min over windows of (ncmp * tlen)`, **96 on small.bin and 512 on large.bin** -- and NOT `stride`, the window-byte denomination p16, p05, p11, p12, p06, p14 and p27 use. ⚠ **THIS NOTE SAID `stride`, 200 and 1032, UNTIL TASK_065, WHICH IS THE PRE-REPAIR TEXT AND WAS STALE** (TASK_064_REVIEW major 3): a reader who trusted it recomputed 172/832 = 0.207 < 0.25 and concluded the gate was passing a floor the kernel fails. WHY THE UNIT MOVED, and it is a fact about the algorithm rather than a preference: **each unit of p47's work consumes TWO window bytes** -- a secret byte and a candidate byte -- and produces one xor, so a window byte is half a unit by construction. Denominated in window bytes the vectorised rungs land at 0.189..0.245 Ir per byte, under the harness default of 0.25, on kernels demonstrably doing the whole job: the tag loops are 11 instructions per 64 window bytes (R3) and 12 per 64 (R4) read straight off the disassembly, i.e. 0.172 and 0.188 asymptotically, so a 0.25-per-window-byte floor does not embarrass this kernel, it FORBIDS it -- which is the case `.memory/02-bench-rules.md` names and `harness/check.py`'s own collapse-ir message prescribes re-denomination for. p07 (4 bytes per `probe`), p10 (2 bytes per `tap`) and p13 made the same move; p10's made the check STRICTER. WHICH WAY THE ESTIMATE ERRS, and p47 is the first pattern here where THE DIRECTION DEPENDS ON THE RUNG: for the constant-time rungs `ncmp * tlen` is exact and the header, the guard arithmetic, the verdict fold, the Horner chain and window padding are all counted as ZERO, so it is strict; the LEAKING rungs read FEWER bytes than that -- that is the bug -- so on a blob whose comparisons all mismatch early they touch 32 bytes per `2*tlen` and the per-unit rate falls with `tlen`. Both probe inputs are chosen so that cannot fire and every rung clears 0.25 with room (../NOTES.md 3): `small` mismatches at k = 5 with tlen 24, so even `bcmp` reads a whole 32-byte block per comparison, and `large` has two of its eight comparisons EQUAL, which forces a full scan of those two in every rung. model.py declares no min_ir_per_work, so the harness default applies unchanged. What the floor still catches is the failure it exists to catch -- a kernel the optimiser collapsed to nothing -- and p47 keeps the TIGHTEST anti-collapse margin in the tree at 2.93x (next 7.02x; p27 134.45x), so the re-denomination did not neuter the check. The two probe inputs differ in work_per_call (96 vs 512) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost. On p47 the pin carries a second job no other pattern's does -- it is what makes the sentence *the proved rung leaks* a statement about a BINARY rather than about a source file. `.memory/06-catalogue.md` hazard 2 is that a text pin binds the source and not the object; here R5's object is R4's object byte for byte, R4's object is disassembled in ../NOTES.md 1 and contains a vectorised `pxor/por` loop with no data-dependent branch, and the leak that R5 fails to exclude is therefore demonstrated on the shipped machine code rather than argued from the text. At O0 the crate names differ in length so call displacements differ, which is link layout and not codegen, hence `norel` there and `exact` at O3."
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
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag. **On p47 Miri is expected to be, and is, entirely silent about the pattern's bug** -- it checks the unchecked reads, which are the thing p47's C rung gets RIGHT. It is listed here because the trusted item is real and a wrong `buf_get_unchecked` would still be invisible to Verus; it is not evidence about the timing property and ../NOTES.md 7 says so.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```
