# TASK_007 — p16, the TLV record walker: the first data-dependent loop bound

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.memory/01-ladder.md`,
`.memory/02-bench-rules.md`, `.memory/04-verus.md`, `.memory/05-layout.md`
("Adding a pattern — what the gate needs from you", **including the new "five
demands steps 1–5 predate"** — those are hard failures and clone-from-p02 does
not supply all of them), then `patterns/p02-buffer-copy/` in full — **p02 is the
template you clone**, not p01. p02 has the bug, the R1h cell, the `&mut`/`&[u8]`
handling and the adversarial protocol; p01 has none of them.

**Status: UNBLOCKED.** TASK_009 and TASK_010 landed and TASK_010_REVIEW cleared
them. That review also checked this spec against the hardened gate and answered
**PASS on all four** of the checks p16 would be the first to exercise — you do not
need to re-derive any of it:

| Check | Verdict for p16 |
|---|---|
| kernel called exactly once, inside the region | **PASS.** R1h reuses the same `c/main.c`, so it carries no region; `match`/nested-block/`#[cfg]` call sites all count as 1. |
| non-zero exclusive `Ir` + kernel's only caller | **PASS.** The stage reads only `collapse.probe_inputs[0]` and skips non-`isolated` modes, so adversarial inputs and `-O3` inlining never reach it. |
| verified twin, per-conjunct deletion | **PASS.** Your accessor is single-clause. The per-conjunct probe was verified by construction. |
| mandatory Miri, 180 s | **PASS**, subject to the blob-size rule below. |

Read `.tasks/TASK_010_REVIEW_REPORT.md` only if you hit one of these; it is 420
lines and you should not need it.

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
leaves the allocation deterministically.

**Keep the blob small there — a few KiB — and note that `n_iters` is not the
knob.** `check.py:3819` rewrites `n_iters` to 4 for every Miri run, discarding
whatever you declare, so this row's Miri cost is `4 × n_blob` folded bytes.
Measured throughput on this box is **~16 900 B/s**, so a blob above ~700 KiB
blocks the row and p16 is born `PASS-WITH-BLOCKED-ROWS`. The same bound applies
to `small` and `large` through their **stride**, not their blob size — which is
why p02's 8.38 MB `large.bin` finishes Miri in 1.5 s and p01's does not finish at
all. (p01 blocks for an unrelated reason worth knowing: `common/driver.rs`'s
`head_u64_body` decodes element-by-element under the interpreter. Your
`head1_u64_bytes` must be a bulk `to_vec()`, like `head2_u64_bytes`.)

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
7. **The three artefacts p02 did not have when it was built** — none are supplied
   by cloning p02, all three are hard failures, and an engineer should not meet
   them for the first time at hour three:
   - `#[cfg(slb_twin)] fn slb_twin_get_unchecked` beside the accessor, same
     signature and same contract character-for-character;
   - `verus.twin_obligations` in the `slb-contract` block, **with the arithmetic
     written out beside it** as p02 does ("9 shipped + 3: …"). Without that note
     it is a declared pin a reviewer cannot check from `spec.md` alone, which
     `.memory/02-bench-rules.md` forbids;
   - an `SLB-TRUSTED-ARGUMENT verus.rs get_unchecked` block in `NOTES.md` with
     the literal labels `(a)`, `(b)`, `(c)`, ≥200 chars. (b) — is the `ensures`
     complete with respect to every unchecked operation the body performs — is
     the one no oracle covers, so write it as if it were the deliverable.
8. **Say plainly in `NOTES.md` that the twin is idle on this pattern.** p16's
   accessor is the same single-clause `i < v@.len()` p01 and p02 ship, so a green
   5c-twin on p16 is **not** evidence that anything hard was checked — its value
   accrues from p17 on, where a multi-clause accessor can be missing a conjunct.
   Requirement 1 of "Harness adaptations" below still stands: show it *failing*
   on `i <= v@.len()` for this pattern's own accessor.

## If the proof stalls

**The budget is one engineer session for the R5 cell** (set by the manager at
TASK_008, pending a user override). If R5 is not converging by the end of it,
**stop and report where it stuck**, with the exact Verus error and the obligation
it could not discharge. `.memory/02-bench-rules.md` is explicit that a documented R5 failure
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

**If a prescription in this file is wrong, say so with the measurement.** Eight
agents have now contradicted my written instructions and all eight were right —
the last one overturned three premises in a single review, with measurements.
That is the most valuable thing an engineer on this project does.

## Part 0 — two gate fixes to land first (small, then leave the gate alone)

Both come from TASK_010_REVIEW and both pass the "could this happen by accident?"
test in `.memory/02-bench-rules.md`. Do these **first**, since you will be
running the gate all task; then do not touch `harness/` again except where p16
forces it.

1. **`check.py:3442-3474` asserts "the only caller" over an empty set.** If no
   callgrind symbol fullmatches the kernel name, `kids` is empty, so
   `callers_of_k` and `bad` are both empty, the cell is counted as **checked**,
   and the stage prints *"… has non-zero exclusive `Ir` and is the only caller of
   the `kernel` symbol"*. Reproduced by the reviewer in
   `.temp/review010/cgvac.py` by renaming the symbol to `kernel.constprop.0` —
   the shape of a gcc IPA clone — giving `failures=0 shouts=0` and an identical
   green line. That silences precisely the limb added to catch a live decoy, and
   it is the **fifth** instance of the rule TASK_010 itself promoted: *a
   count-bearing `rep.ok` must state its `n` and must never fire at `n == 0`*.
   Fix it, and re-run the reviewer's rig to show it now fails.
2. **Delete `MAX_TWIN_JUSTIFICATIONS` and its check** (`check.py:1131`,
   `:2830`). It was my round number. It is redundant — the separate "every twin
   justified away" rule already fails the case it was meant to catch, which the
   reviewer confirmed by re-running mirror `x3` — and it is the only knob in the
   twin regime that can hard-fail an honest pattern with **no route out**. The
   hatch stays, uncapped and shouted every run. Confirm `x3` still fails after
   the deletion; if it does not, keep the cap and tell me I was wrong to drop it.

Nothing else in `harness/` is in scope. If p16 needs a harness change beyond
`head1_u64_bytes`, report it rather than growing the gate — it is 4209 lines
against two patterns and that ratio is the reason this task exists.

## Harness adaptations

**Prerequisite: satisfied.** TASK_008, TASK_009 and TASK_010 have all landed and
been reviewed. The history below is kept because it explains *why* the accessor's
`requires` is the whole security argument for this pattern — not because anything
here is still blocking.

TASK_008 closed the fake-`verus!` ghost harbour and added `requires` mutation
testing. TASK_008_REVIEW then found that neither reaches the property p16 depends
on, and answered the "is the template ready for p16" question with **no**:

> p16's security argument is `get_unchecked`'s `requires i < v@.len()` and
> nothing else. Changing it to `i <= v@.len()` — the off-by-one OOB read p16
> exists to model — **passes the entire gate**, with stage 5a printing it
> approvingly. The tautology probe cannot see it (not a tautology); parameter
> coverage cannot see it (both parameters appear); deletion is not applied to
> trusted items and cannot be.

So the gate would certify a p16 whose trusted base axiomatises the exact bug
class p16 is about. **TASK_009's verified twin is the fix** — a mechanism that
judges the *strength* of a trusted precondition rather than its triviality. It
landed, was attacked at TASK_009_REVIEW and TASK_010_REVIEW, and survives.

Three further requirements the reviewer set for this pattern specifically:

1. **The accessor's `requires` must be checked, not declared.** Whatever
   mechanism TASK_009 lands, `NOTES.md` must show it failing on
   `i <= v@.len()` for *this* pattern's accessor, not only for p02's.
2. **Do not give p16 a generic or method-shaped trusted accessor.** The
   tautology probe hard-fails on generics, `self` receivers and lifetime
   parameters (TASK_009 Part C fixes it; until then a plain free function is the
   only shape that can be greened). A monomorphic `fn get_unchecked(v: &[u8], i:
   usize) -> u8` is what this pattern needs anyway.
3. **State the residual honestly in `NOTES.md`.** 5c-req's guarantee is
   "this precondition is not `true`", not "this precondition is strong enough".
   Say which of p16's trusted clauses are machine-judged and which rest on a
   human having read them.

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
