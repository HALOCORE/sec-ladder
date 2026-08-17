# TASK_007 — p16, the TLV record walker: the first data-dependent loop bound

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.memory/01-ladder.md`,
`.memory/02-bench-rules.md`, `.memory/04-verus.md`, `.memory/05-layout.md`
("Adding a pattern — what the gate needs from you"), then
`patterns/p02-buffer-copy/` in full — **p02 is the template you clone**, not p01.
p02 has the bug, the R1h cell, the `&mut`/`&[u8]` handling and the adversarial
protocol; p01 has none of them.

## Why this pattern, and what it is for

Every perf result so far says the same thing: **safety is cheap when the
optimiser can see the loop.** Three patterns running, R3 within ~+10 Ir/call of
unsafe, flat. p02 looked like the exception and was not — its delta was a lost
`memcpy` idiom, not a bounds-check tax, and `.memory/01-ladder.md` carries the
retraction.

`.memory/01-ladder.md` also says, explicitly: *"Do not generalise any of this to
patterns with data-dependent indices — the interesting patterns are precisely
the ones where LLVM cannot hoist, and that is where the ladder earns its keep."*

**p16 is the first honest test of that sentence.** Its kernel walks a chain of
length-prefixed records: the trip count comes from the data, each record's
position depends on every previous record's length field, and the fold index is
loop-carried through a value the attacker wrote. There is no loop-invariant
bound for LLVM to hoist, and the walk cannot be turned into a `memcpy`.

If the safe rungs still land at +10 flat, that is a *stronger* result than
anything p01/p02 produced, because the obvious escape route is gone. If they do
not, this is the pattern where the ladder finally shows a real cost — and then
the decomposition below is what turns a number into a mechanism.

**Either outcome is publishable. Do not aim for one.**

## The bug class

CWE-125, out-of-bounds **read**. p02 was an out-of-bounds write; this is the
read, which is the one that leaks rather than corrupts (Heartbleed's class) and
which no allocator rounding absorbs. A length field says the value is longer
than the bytes that remain, and a walker that trusts it folds its way off the
end of the buffer.

## Kernel contract

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

As in p02, C is handed the buffer length and R1 ignores it — so R1-vs-R1h holds
the calling convention, the argument count and the register allocation fixed and
differs only in the check.

### Semantics

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

Five things are load-bearing. Do not "improve" any of them:

- **Every comparison is subtraction-first** — `end - p >= 3`, and
  `vlen > end - (p + 3)`. Neither can underflow: `p <= end` and `p + 3 <= end`
  are loop invariants. The additive spellings (`p + 3 <= end`,
  `p + 3 + vlen <= end`) can overflow `size_t` and wave the attack through.
  This is p02's rule, and p02 measured that it costs rustc an idiom
  recognition — **expect it to cost something here too, and decompose before
  attributing it to bounds checking.** That mistake has been made once already.
- **R1 omits only the second check.** It keeps `end - p >= 3` (without it the
  walk reads a header off the end on *every* input, including the well-formed
  ones, and the pattern stops being about the length field). It drops
  `vlen > end - (p+3)`. That is the single edit between R1 and R1h.
- **The tag byte is folded, not ignored.** An unread tag is deleted by LLVM and
  the walk stops looking like a TLV walk.
- **`nrec` is folded into the result** so the record count is observable in the
  checksum. A walker that mis-parses the chain but folds the same bytes must not
  produce the same answer.
- **No tag dispatch, no skipped records.** A `if tag != 0` branch is realistic
  and it is *deliberately excluded*: it adds an unpredictable data-dependent
  branch, which is a second new variable, and this box cannot measure branch
  misses (`.memory/00-environment.md`). One new thing at a time — the
  unpredictable-branch axis belongs to p19/p35.

### Contract

```
requires:  off + len <= buf_len            # structural
ensures:   result == tlv_fold(buf, off, len)
```

`tlv_fold` is a recursive spec function over the walk, mirrored in `model.py` as
an independent Python implementation (p02's `copy_dst`/`copy_sum` are the shape).

**Read this next paragraph before writing the proof — it is the one real
difference from p02.** p02's security property was statable as an `ensures`
(an equality on the whole destination buffer, which said "nothing outside the
copied prefix moved"). **p16's is not.** This kernel writes nothing; the harm is
a read, and "no byte outside the window was read" is not a property of the
return value — a kernel could read out of bounds and discard the byte.

For a read-only kernel, **R5's memory-safety claim rests entirely on the
discharged `requires` of the trusted accessor**, not on any `ensures`. Every
`buf[i]` in verified exec code carries the obligation `i < buf.len()`; the
`get_unchecked` wrapper's `requires i < v@.len()` is what every call site must
prove, and *that* is the security property. The `ensures` above exists to make
the proof non-vacuous and to tie the value to `model.py`.

Consequence, and put it in `NOTES.md`: for this pattern the TCB story **is** the
whole result, and `harness/check.py`'s clause-deletion stage matters most on the
accessor's `requires`. Say so explicitly rather than presenting a functional
`ensures` as if it were the safety argument.

### Termination

The outer walk needs `decreases end - p`, and progress needs `3 + vlen >= 1`,
which is immediate. Note in `NOTES.md` that a walker written `p += vlen` — a
real and common variant of this bug — does **not** terminate on `vlen == 0`, and
that Verus rejects it at the `decreases` clause with no test run. That is a
cheap, honest point about what a proof catches that a test suite does not.
Do not build that variant as a rung; a sentence and the error message is enough.

## Payload layout

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the record chain; n_blob = payload_len - 8
```

One `u64` head, not p02's two, so **`common/` needs a `head1_u64_bytes` in all
three languages** (`slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes`). Add it to `common/`, never to the pattern
(`.memory/05-layout.md`). There is no `cap` and nothing is allocated from an
attacker-controlled size, so p02's exit-7 range check does not apply here — say
so in `spec.md` rather than copying a dead check across.

## Driver loop

Same skeleton as p02, one argument narrower:

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
header. Generate the canonical token sequence with
`python3 harness/dloop.py <rung>.rs` and paste it into `driver.canonical` —
**do not hand-write it**, and do not copy p02's.

## Inputs

Five, all from `inputs/gen.py`, deterministic from a fixed seed:

| stem | shape | purpose |
|---|---|---|
| `small` | windows tiling L1 (~16 KiB blob), records exactly tiling each window | the L1-resident perf row |
| `large` | blob well past L2 (8 MiB), same structure | the memory-bound perf row |
| `adversarial-overrun` | **`n_blob == stride`, i.e. exactly one window**, whose last record declares a `vlen` running past the end of the blob | R1 reads off the end of the *allocation* → ASan fires |
| `adversarial-trunc` | a window whose tail is 1 or 2 bytes — a header that does not fit | exercises `end - p >= 3`; every rung must stop cleanly |
| `adversarial-stride2` | `stride_w == 2` | the driver guard; loop never entered, prints 0 |

**`adversarial-overrun` must be exactly one window.** `k` is pseudo-random over
`[0, nwin)`, so with several windows the malformed one is hit only
probabilistically and an overrun from a middle window stays inside the
allocation — silent wrong answer, no ASan, and a gate that passes by luck. With
`nwin == 1`, `k` is always 0, the window is also the last, and the overshoot
leaves the allocation deterministically. Keep `n_iters` small there.

Give `small` and `large` **different window sizes mod 16 and mod 4**
(`.memory/01-ladder.md`: residues have bitten three times, and p02's real
modulus was 16). Extend `gen.py --sweep` from p02's.

## The decomposition is mandatory, and it comes before the claim

p02's headline was published and then retracted because a whole-kernel delta was
attributed to bounds checking without changing one loop at a time. **Do not
report a single R2-vs-R4 number for p16.** Build and measure these variants
(under `.temp/`, not as rungs) *before* writing anything into `NOTES.md`:

1. R2 as shipped (indexed walk, indexed fold).
2. R2 with the **fold** replaced by an iterator/`chunks_exact` fold, walk indexed.
3. R2 with the **walk** rewritten to reslice (`let rest = &buf[p..end];`), fold
   indexed.
4. Both.
5. The check written **additively** (unsound — a measurement only, never shipped).

Then state which loop the delta lives in. If the answer is "the fold, and it
scales with bytes", that is the first genuine O(n) safety cost in this project
and it needs the `bulk_calls` / disassembly evidence beside it. If the answer is
"the walk", say what LLVM lost.

Also check, on the disassembly rather than by assertion: does the inner fold
vectorise in any rung? A per-record fold whose length is data-dependent usually
does not, and if R4 does not vectorise either then the safe-vs-unsafe gap is
being measured on a scalar loop in both — worth knowing before interpreting it.

## Expected sticking points

- **Nonlinear arithmetic in the driver**, as in p02: `k < nwin` and
  `k * stride + stride <= n_blob`. p02 spells these out in ghost code; lift its
  three lines (`lemma_div_non_zero`, `lemma_fundamental_div_mod`,
  `lemma_mul_inequality` + one `by (nonlinear_arith)` — `.memory/04-verus.md`).
- **`v@.len() <= usize::MAX` is not free** — `assert(buf@.len() ==
  vstd::slice::spec_slice_len(buf));` once before the loop
  (`.memory/04-verus.md`).
- **A recursive spec function over the walk needs a `decreases`** too, and the
  loop invariant has to relate `acc` at each step to `tlv_fold` over the prefix
  already walked. That is the real proof work here and it is the reason p16 is
  rated easy–*moderate* rather than easy. Budget for it; if it stalls, see
  "If the proof stalls" below.

## Done when

1. All six cells build at both opt levels and both inline modes; `check.py p16`
   is green on a **complete** run (`complete_run: true`), or every non-green row
   is a documented failure with the reason.
2. Checksums agree across all rungs on `small` and `large`, and against
   `model.py`.
3. The adversarial table records per-rung behaviour: exit code, stdout, stderr,
   ASan/UBSan, panic, silent-wrong-answer. **`adversarial-overrun` must actually
   fire ASan on R1** — if it does not, the security half is unsupported and that
   is a finding to report, not to paper over (`.memory/02-bench-rules.md`).
4. The decomposition table above exists and the perf claim names a loop.
5. You mutated your own proof and the gate failed: at least one mutant that
   weakens the accessor's `requires`, and one that makes the kernel's `ensures`
   trivial. Paste both results.
6. `NOTES.md` carries the TCB tally, counted per `.memory/04-verus.md` (**every**
   `external_body` item, individually).

## If the proof stalls

There is no proof-effort budget set yet — the user owes that decision. Until
then: if R5 is not converging after a serious attempt, **stop and report where
it stuck**, with the exact Verus error and the obligation it could not
discharge. `.memory/02-bench-rules.md` is explicit that a documented R5 failure
is a finding, not a gap, and p16 is supposed to be one of the *easy* ones — a
stall here is important information about the harder families and I want it
early rather than late.

## Constraints

No root; no `/tmp` (scratch in `.temp/p16/`); **no `git add`/`git commit`**; do
not edit `pilot/`, and do not edit `patterns/p01-array-sum/` or
`patterns/p02-buffer-copy/` except where this task says to. Verus only via
`./verus_run.py`. clang is `~/tools/llvm/bin/clang`, valgrind is
`~/tools/valgrind/bin/valgrind`, rustc is `~/.cargo/bin/rustc` — none are on
PATH. Long builds get `timeout <N>`.

**If a prescription in this file is wrong, say so with the measurement.** Five
engineers have now contradicted my instructions and all five were right. That is
the most valuable thing an engineer on this project does.

## Harness adaptations

**Prerequisite: TASK_008 must land first.** It closes two gate bypasses
(a rung can fake a `verus!` block and enter the ghost-strip path; stage 5c never
tests `requires`, so a trusted `unsafe` wrapper can demand `n >= 0` and pass the
whole gate). Cloning the template before those are fixed clones both holes into
p16 — and p16's *entire* security argument is the accessor's `requires`, so
blocker 2 lands on it harder than it lands on p02.

TASK_006_REVIEW was asked what in the template will not survive a parser kernel
and named four hard stops, with file:line. **The design above was chosen to
clear all four** — that is why it looks conservative. Do not "simplify" it into
one of them:

1. **`work_per_call` must be one scalar per input** (`check.py:625`, hard-fails
   on `work <= 0` at `:632`). A parser that early-exits has a *distribution* of
   work per call, and p02's `min`-over-records convention collapses to 0 the
   moment a probe input contains one rejected record — which is exactly what a
   TLV corpus contains. p16 sidesteps this by making the **window** the unit:
   `work_per_call = stride`, constant across calls, and an over-estimate of the
   bytes actually folded (headers are skipped), so the floor errs strict.
   **Do not denominate p16's work in records or in bytes-folded.**
2. **The `d(Ir)/d(work)` assertion needs two probe shapes with *different*
   `work_per_call`** (`check.py:682-688`). `small` and `large` must therefore
   have **different strides**, not merely different blob sizes. Check this
   explicitly; it is easy to generate two inputs that differ only in blob size.
3. **The driver barrier assumes fixed-stride records.** A TLV walker has no
   natural stride, so a driver that walked the chain to pick a start offset
   would put the walk's cost in the driver and swamp the marginal-`Ir` column.
   Fixed-size *windows* with a Lemire index keep the driver O(1) per call while
   the **kernel's** trip count stays data-dependent — which is the whole point
   of the pattern. This is why the design walks a window rather than the blob.
4. **A struct result cannot be passed out through a C out-parameter**
   (`dloop._apply_call_args:337-342` refuses to drop a non-identifier argument;
   `build.py:161-163` hard-codes exactly three C TUs). p16 returns `u64`. This
   stop is why p17's `Range` parser is sequenced after p16 and will need harness
   work of its own — do not try to solve it here.

Everything else was checked and survives: `_probe_input` (`check.py:534`)
rewrites `n_iters` at offset 0 for any payload shape, and `dloop._NOT_CALLS`
already knows `match`/`switch`.

The one genuinely new harness item p16 needs is `head1_u64_bytes` in all three
languages, per "Payload layout" above.
