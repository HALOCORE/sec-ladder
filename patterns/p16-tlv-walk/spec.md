# p16 — TLV record walk: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Four C arguments against three Rust ones, and **the two sides carry exactly the
same information**: `&[u8]` is a pointer and a length, and C spells the pair
out. C is handed the blob length and R1 ignores it, so R1-vs-R1h is a comparison
with the calling convention, the argument count and the register allocation all
held fixed. The only difference between those two cells is one `if`.

(The arity mismatch is why `spec.md` carries a `driver.call_args` pin: no alias
can turn a four-argument call into a three-argument one. See "Driver loop".)

## Semantics

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
`nrec + 1` wraps too, which removes the only other overflow obligation; C's
`uint64_t` wraps by definition (6.2.5p9) and the Rust rungs write
`nrec.wrapping_add(1)`.

Five things are load-bearing. Do not "improve" any of them.

**The authoritative copy of this list is the `idiom` key in the `slb-contract`
block below**, which is hashed into `contract_sha256`. What follows is the same
statement in prose, with the arguments; if the two ever disagree, the block wins
and the prose is the bug. Edit both or neither (TASK_016_REVIEW m2).

- **Every comparison is subtraction-first** — `end - p >= 3`, and
  `vlen > end - (p + 3)`. **These are the tokens, not just the property.** A
  rung that establishes the same two facts some other way — `split_first_chunk`
  plus `split_at_checked` on a consumed slice, or `rem >= 3` / `vlen > rem - 3`
  on a running remainder — does **not** satisfy this and is a different
  benchmark; the block's `why` carries the argument and what the reading costs.
  That is the **named-spelling standard**, and it is a **policy adopted at
  TASK_018 for all six patterns, after the alternate spellings had been
  measured** — not a disambiguation of what this entry always meant. TASK_017
  applied it to p16 alone and refused it for p17 in the same commit
  (TASK_017_REVIEW B1); TASK_018 made it one rule and measured what it does
  *not* buy — respelling only what this declaration leaves free moves R3 by up
  to `4·nrec − 8` Ir/call and **R4 by `4·nrec`** (TASK_023), so `R3ship − R4ship`
  bounds only `inf(in-contract R3) − R4ship` and is **not** an upper bound on
  the in-contract safety tax: an admissible pair exceeds it by `5·nrec`
  (`NOTES.md` §10a). The additive spellings (`p + 3 <= end`,
  `p + 3 + vlen <= end`) can overflow `size_t` on an attacker-chosen `vlen` and
  wave the attack through. Neither subtraction can underflow *given the check*:
  `p <= end` and `p + 3 <= end` are loop invariants, and the second test is
  exactly what maintains the first. That is not a side note — it is why the two
  obligations in this kernel are not independent, and it is why deleting the
  check (R1) makes `end - p` underflow and the walk never stop at the buffer
  end. See `c/kernel.c`.

  p02 measured that subtraction-first costs rustc an idiom recognition, and its
  headline was retracted for attributing that to bounds checking. p16's fold is
  a serial `acc = acc*31 + b` chain with no bulk-memory idiom to lose, so the
  same escape route should not exist here — but "should not" is an argument.
  `NOTES.md` §3 is the measurement, and it changes one loop at a time.
- **R1 omits only the second check.** It keeps `end - p >= 3`; without that the
  walk reads a header off the end on *every* input, including the well-formed
  ones, and the pattern stops being about the length field. It drops
  `vlen > end - (p+3)`. That is the single edit between `c/kernel.c` and
  `c/kernel_hardened.c`.
- **The tag byte is folded, not ignored**, and it is folded *before* the fit
  test. An unread tag is deleted by LLVM and the walk stops looking like a TLV
  walk; folding it before the test is what makes a chain that stops early differ
  from a chain that was one record shorter.
- **`nrec` is folded into the result** so the record count is observable in the
  checksum. A walker that mis-parses the chain but folds the same bytes must not
  produce the same answer.
- **No tag dispatch, no skipped records.** A `if tag != 0 { skip }` branch is
  realistic and it is *deliberately excluded*: it adds an unpredictable
  data-dependent branch, which is a second new variable, and this box cannot
  measure branch misses (`.memory/00-environment.md`). One new thing at a time —
  the unpredictable-branch axis belongs to p19/p35.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == tlv_fold(buf, off, len)
```

`requires` is the whole of it: **the window is inside the blob.** That is
structural — it is about the shape of the buffer the driver built, not about its
contents — so it holds on every input this benchmark runs, `adversarial-*`
included, and `harness/check.py` evaluates it at every one of the kernel calls
to prove that it does. Every `vlen` a `u16` prefix can express is an *argument*
of the problem; the kernel is total in all 65 536 of them.

### The `ensures` is not the security property, and on this pattern nothing is

**This is the one real difference from p02 and it must not be glossed.** p02's
security property was statable as a postcondition, because p02 *writes*: an
equality on the whole destination sequence says "the record landed where it
should" and "not one byte outside it moved" at the same time. p16 writes
nothing. The harm it models is a **read**, and

> "no byte outside `buf[off .. off+len)` was read"

is **not a property of the return value** — a kernel could read out of bounds
and simply discard the byte. There is no `ensures` that says it.

So for a read-only kernel, R5's memory-safety claim rests **entirely on the
discharged `requires` of the trusted accessor**. Every `buf[i]` in verified exec
code carries the obligation `i < buf@.len()`; `get_unchecked`'s
`requires i < v@.len()` is what every call site must prove, and *that* — proved
at four call sites, for indices the attacker's own length fields chose — is the
security property of this pattern. The `ensures` above exists to make the proof
non-vacuous and to tie the value to `model.py`.

Two consequences, both recorded in `NOTES.md` §5:

1. the TCB story **is** the whole result here, so `harness/check.py`'s
   clause-deletion and verified-twin stages matter more on p16 than on any
   earlier pattern, and they matter on the accessor's `requires` specifically;
2. a green 5c-twin on p16 is **not** evidence that anything hard was checked —
   p16's accessor is the same single-clause `i < v@.len()` p01 and p02 ship, so
   there is no missing conjunct for the twin to find. `NOTES.md` §7 shows the
   twin *failing* on `i <= v@.len()` for this pattern's own accessor, which is
   the only form of evidence that stage can supply here.

### Termination, and what a proof catches that a test does not

The outer walk carries `decreases end - p`, and progress needs `3 + vlen >= 1`,
which is immediate — a record occupies at least its header, so the *header* is
what guarantees progress and the length field is not trusted for it.

A walker written `p += vlen` instead of `p += 3 + vlen` is a real and common
variant of this bug, and it does **not** terminate on `vlen == 0`. Verus rejects
it at the `decreases` clause with no test run and no input that triggers it;
`NOTES.md` §8 has the exact message. That variant is deliberately not built as a
rung — a sentence and the error is the whole point.

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p16's payload is:

```
word 0     u64  stride      # bytes per window; the kernel walks one window
byte 8..   u8[] blob        # the record chain; n_blob = payload_len - 8
```

decoded by `slb_head1_u64_bytes` / `driver::head1_u64_bytes` /
`slb.head1_u64_bytes` — one function per language, added to `common/` for this
pattern, never to the pattern itself (`.memory/05-layout.md`). All three are a
bulk copy rather than an element-by-element decode, which is what keeps every
p16 row Miri-checkable (`.memory/02-bench-rules.md`: `head_u64_body`'s
per-element loop is why p01's `large.bin` blocks).

A record is `tag:u8, vlen:u16le, value:u8[vlen]` and occupies `3 + vlen` bytes.
Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob`, every tag and
every length prefix come from the file.

**There is no `cap` and nothing is allocated from an attacker-controlled size**,
so p02's `SLB_MAX_CAP` range check and its exit 7 have no analogue here and are
deliberately not copied across. The only allocation the driver makes is the blob
itself, whose size is the file's size.

## Driver loop

Identical in all six rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` normalises every copy — the C one included — and
diffs it against `driver.canonical` below.

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
header, so `adversarial-stride2.bin` attacks this guard. When it fails the loop
is skipped entirely — rather than entered and broken out of, which would put a
branch in the measured loop — and the driver prints `0`. `n_iters == 0` is
handled by the `while` itself. The comparison is in `u64` *before* the
`as usize` cast, so a truncating driver cannot sneak a 2^40 stride past it.

### Why this does not evaporate

Same mechanism as p01 and p02: `k` is derived from `acc`, and `acc` from the
previous call's result, so call *i+1* cannot begin until call *i* has returned.
Nothing to CSE, nothing to hoist, no `black_box` and no `asm volatile` — the
same arithmetic in both languages, so neither gets a stronger barrier than the
other. `k = (acc * nwin) >> 64` is Lemire's map onto `[0, nwin)`; see p01's
`spec.md` for why it is a multiply-shift and not a modulo.

### Why the window, and not the chain

The driver walks a **fixed-size window** and the kernel walks the *records
inside it*. That is deliberate and it is the design decision that lets p16 exist
at all (TASK_006_REVIEW named the alternative as a hard stop): a TLV chain has
no natural stride, so a driver that walked the chain to pick a start offset
would put the walk's cost in the driver and swamp the marginal-`Ir` column. With
fixed windows the driver stays O(1) per call — one multiply, one shift, one
multiply — while the **kernel's** trip count stays data-dependent, which is the
entire point of the pattern.

It is also what makes `work_per_call` a single scalar. A parser that early-exits
has a *distribution* of work per call, and **`check_marginal_ir`** (`check.py:1976`) needs one number and
hard-fails on `work <= 0` at `:1987`; p02's min-over-records convention collapses
to 0 the moment a probe input contains one rejected record, which is exactly
what a TLV corpus contains. The window is fixed by the payload header, identical
on every call, and a strict over-estimate of the bytes actually folded — so the
derived floor errs strict. See `model.py`.

### Why the structural precondition holds

`k < nwin` because `(acc * nwin) >> 64 < nwin` for `nwin >= 1`, and
`k * stride + stride <= n_blob` because `k <= nwin - 1` and
`nwin * stride <= n_blob` (integer division rounds down). Both steps are
nonlinear, so R5 spells them out in ghost code.

### The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.aliases` cannot reconcile that
— both sides of an alias are a dotted identifier path, so an alias renames and
can do nothing else. `driver.call_args` declares which argument *positions* of a
named call are the canonical ones (`{"c": {"kernel": [0, 2, 3]}}`), and
`harness/dloop.py` refuses to drop anything that is not a single bare
identifier, so no prefetch, no side effect and no extra statement can hide in
the argument the diff stops looking at.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts,
because a declared number a reviewer cannot check from `spec.md` alone is
exactly what `.memory/02-bench-rules.md` forbids.

| pin | why |
|---|---|
| `verus.obligations` = 10 | **`fold_bytes` 1 + `tlv_walk` 1 + `kernel` 3 + `main` 5 = 10.** Every term is checkable with `./verus_run.py verus.rs --verify-function <name> --verify-root`, which is how they were obtained: the two *recursive* spec fns carry one termination query each, `vlen_at` and `tlv_fold` are non-recursive and carry **0**, the three `external_body` items carry **0**, `kernel` is 1 for the body + 1 per loop body (there are two loops), and `main` is 1 for the body + 1 for the driver loop + one per `by (nonlinear_arith)`/`by { .. }` sub-proof in its two ghost blocks. Note that `.memory/04-verus.md`'s rule of thumb — one query per function plus one per loop — under-counts by 3 here, because it predates a pattern with `by`-blocks in the driver; the rule is a skeleton checksum and it is the *measured* decomposition that a reviewer should re-run. |
| `verus.twin_obligations` = 11 | the count in the **other** configuration, `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. **10 shipped + 1**, and the 1 is measured the same way: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` — one function, no loop body, no `by`-block. Pinning the number rather than requiring `tw > base` is what catches a twin that quietly lost its body, or an item that exists only under the cfg. |
| `identity: unsafe ≡ verus, O3 exact` | Its obvious job is to certify that the proof is free. **Its other job is to bound the R4 class, and that was not written down until TASK_027 cost a headline.** The pin says R4 must have a byte-identical R5 that Verus verifies, so **an R4-side variant must be expressible in what vstd can verify or it is not a rung** — `read_unaligned` is not (one extra trusted item), and neither is any `chunks_exact` fold (`chunks_exact`, `ChunksExact`, `by_ref`, `TryFromSliceError`, `get_unchecked`: five). R3 is bounded by nothing of the kind. So the two classes are **incomparable, not nested**, `inf(R4) ≤ inf(R3)` "by construction" is false here, and a safe-side and an unsafe-side respelling are not the same category of edit. Audit an unsafe-side variant's TCB *before* differencing it. `NOTES.md` §10a.1, §10a.2. |
| `miri.required: true` | R4 and R5 *are* byte-identical at `-O3`. Since TASK_010 that no longer makes Miri optional: it is mandatory for any pattern with a trusted item, because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. `check.py` derives this from `verus.rs` rather than reading the flag. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": ["off + len <= buf_len"],
  "ensures": ["result == tlv_fold(buf, off, len)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (tlv_fold). NOTE WHAT THE ensures IS NOT: it is the value, not the security property. p16's kernel writes nothing, so 'no byte outside the window was read' cannot be a postcondition -- a kernel could read out of bounds and discard the byte. The memory-safety claim rests entirely on get_unchecked's discharged `requires i < v@.len()`. See the prose above.",

  "idiom": {
    "required": [
      "every comparison is subtraction-first AND IS SPELLED AS THESE TOKENS -- `end - p >= 3` and `vlen > end - (p + 3)` -- in every rung (R1: fourth entry below). This entry names TOKENS, not the weaker property 'contains no additive comparison'. That is the named-spelling standard, adopted as POLICY at TASK_018 for all six patterns AFTER the alternate spellings had been measured -- it is not a disambiguation of what this entry always meant. The argument, the history of the sentence, and what the standard demonstrably does NOT buy are in `why`",
      "the tag byte is folded, and folded BEFORE the fit test",
      "nrec is folded into the result",
      "R1 omits only the second check -- it keeps `end - p >= 3`"
    ],
    "forbidden": [
      "the additive spellings `p + 3 <= end` and `p + 3 + vlen <= end`",
      "tag dispatch or skipped records"
    ],
    "why": "the additive comparisons can overflow size_t on an attacker-chosen vlen and wave the attack through, which is the whole check p16 is about; an unread tag is deleted by LLVM and the walk stops looking like a TLV walk; a `if tag != 0 { skip }` branch adds an unpredictable data-dependent branch, which is a second new variable and belongs to p19/p35 (this box cannot measure branch misses). RESTATED in this hashed block at TASK_016 from the prose section 'Five things are load-bearing' above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither. WHAT THE STANDARD SAYS ABOUT p16: rows 3, 4 and 6 of NOTES.md 10 (`.temp/p05r3/v16/tuned_split.rs`, `tuned_splitat.rs`, `unsafe_consume.rs`) contain NEITHER named comparison and are OUT OF CONTRACT under it. WHAT THIS BLOCK USED TO SAY, AND WHEN AND WHY IT CHANGED -- restored here because TASK_017 deleted it and TASK_016_REVIEW's honesty verdict rested on it (TASK_017_REVIEW M1). Until 89f6598 (2026-08-17) this `why` said, in these words: `Note what is deliberately NOT restricted: the R2/R3/R4 spelling of THE WALK and of the value fold, beyond the comparisons above`, and `A consuming spelling (split_first_chunk::<3>() plus split_at) IS ADMISSIBLE under this declaration and measures 10*nrec + 9 CHEAPER than the shipped R3`. Both sentences were written at TASK_016 with the measurement already in hand, i.e. against the author's own interest. TASK_017 removed `the walk` from the first, dropped the second, and kept verbatim a third -- `the honest move is to declare the walk's spelling here BEFORE measuring` -- which under the new reading advises a future task to do, before measuring, what TASK_017 had just done after measuring. So: the consuming spelling WAS admissible when TASK_015 measured it at ad661ed, and stopped being admissible four tasks later at 89f6598. Nobody may read p16's `+27/+77` as a pre-registered matched pair; the walk's spelling was pinned AFTER the measurement, and this sentence is the record of that. THE FOUR GROUNDS TASK_017 GAVE, with what survived. (i) House convention (p05's `i*ncol + j written out in every rung`, p02's `spelled identically in every rung`, p17's `the one conjunctive if start < end && start >= 0`) -- TASK_017_REVIEW found the citation cuts the other way textually, every cited entry carrying an explicit strictness marker p16's did not have, which is exactly why this is now POLICY and not a reading. (ii) `p` and `end` ARE the traversal representation -- true, but the claim TASK_017 built on it, that pinning them `is what makes R3 - R4 a difference in safety rather than a difference in representation`, is REFUTED BY MEASUREMENT AT TASK_018 and is WITHDRAWN; see the in-contract spread below. (iii) The exclusion falls symmetrically -- true in EXISTENCE (the consuming R4 control goes out too) and misleading in EFFECT (TASK_017_REVIEW M4): the published pair is `7 + 5*nrec` / `7 + 7*nrec` (+27 small, +77 large) against the excluded matched consuming pair's `7` flat / `7 + nrec` (+7, +17), so the reading makes p16's published safety tax 3.9x (small) / 4.5x (large) LARGER, and removes 49 (small) / 109 (large) Ir/call of headroom from the SAFE side against 29 / 49 from the unsafe side. Quote the numbers, not the word. (iv) `inf(R4) <= inf(R3)` by construction (.memory/01-ladder.md finding 14) -- REFUTED AT TASK_025_REVIEW, and it never proved what it was cited for. See AN R4 MUST BE VERUS-EXPRESSIBLE below: this block's own `identity` pin makes the R4 class SMALLER than the R3 class, not larger, so the inclusion runs the opposite way. Ground (iv) is therefore withdrawn; the standard still applies to all six patterns, on grounds (i)-(iii) and on TASK_018's measurement, which is what actually selects it. THE IN-CONTRACT SPREAD, MEASURED AT TASK_018 -- this is what TASK_017 owed and did not do; the table is NOTES.md 10a. Three admissible respellings of the two things this block leaves free (the header read and the value fold), all keeping BOTH named comparisons literally, all identical to shipped R3 on 73/73 committed inputs: `r3_endslice` is `2*nrec - 2` Ir/call CHEAPER than shipped R3, `r3_window` is `4*nrec - 8` cheaper, `r3_hdrarray` is `nrec` DEARER. At `large` (nrec 10) that is a 42 Ir/call spread INSIDE the contract against a published `R3 - R4` of 77; at `small` (nrec 4), 12 against 27. `r3_endslice` keeps `p` absolute and `end = off + len`, so it satisfies even ground (ii)'s own gloss. CONSEQUENCE, plainly: `the shipped R3 is the cheapest admissible spelling` is not unestablished, it is FALSE. AND THE R4 SIDE HAS BEEN SEARCHED, AT TASK_023, AND WHAT IT FOUND IS A CONTROL AND NOT A RUNG: `R4ship - r4_hdr = 4*nrec` Ir/call -- the two length bytes read as one unaligned u16, the header read this block leaves free -- zero residual on 24 blobs, `nrec` 1 to 16 and both `vlen` residue classes. THE MEASUREMENT STANDS; THE INFERENCE FROM IT IS WITHDRAWN AT TASK_028. TASK_023 read it as `+27/+77 is NOT an upper bound on p16's in-contract safety tax either, because the admissible pair (r3_hdrarray, r4_hdr) EXCEEDS it by exactly 5*nrec, 47 against 27 at small and 127 against 77 at large`. `r4_hdr` IS NOT ADMISSIBLE -- see AN R4-SIDE VARIANT MUST BE EXPRESSIBLE below, which disqualified it for `read_unaligned` before TASK_023 quoted it -- so that pair is not a pair of rungs, and p16's R4 side has never moved by a single ADMISSIBLE instruction. The in-contract PAIR INTERVAL measured at TASK_023 -- `nrec + 13` ... `7 + 10*nrec` at `vlen = 0 mod 4` and `3*nrec + 13` ... `7 + 12*nrec` otherwise, width 111% / 109% of the published tax -- IS REFUTED: every number in it, and the SIGN of its bottom endpoint (TASK_023_REVIEW). It came from a TWO-LEVER search on a declaration whose last sentence also licenses UNROLLING by name, and the unroll lever is the only one of the three that acts PER BYTE. Measured over the same 24 blobs, adding only variants that same sentence licenses, the interval is -239 ... +236 (1759%) at small and -2449 ... +2244 (6095%) at large, and its bottom is NEGATIVE ON ALL 24 POINTS. AND THAT REPLACEMENT IS WITHDRAWN IN TURN AT TASK_028, NOT RE-POINTED: its R4 endpoints are `r4_hdr` and the unsafe-side `chunks_exact` folds, and NEITHER family is a rung, so p16 has no admissible R4 that moves and therefore NO PAIR INTERVAL AT ALL. What p16 publishes is the two quantities the shared paragraph above names -- the fixed-R4 bound and the R3-SIDE span -- and nothing that differences two searched sides. The comparison of that width against p05's 80% / 71% is WITHDRAWN outright rather than re-pointed: it put a 2-lever p16 search beside p05's 46-spelling one, which is the same 'one interval is not the other's peer' error, one level down, as the 'p05's declaration is the loosest of the set' claim it was written to replace. THE ONE-SIDED BOUND survives in FORM and not in VALUE: `R3ship - R4ship` still bounds `inf(in-contract R3) - R4ship` above with R4 held fixed by fiat, but the CHEAPEST FOUND in contract against the SHIPPED R4 is -199 (small, `chunks_exact(16)` or `(32)`) / -2545 (large, `chunks_exact(64)`), not `+19` / `+45` -- reached by shipped `safe_tuned.rs` with ONE substitution, ZERO `unsafe` tokens, both named comparisons literal under `check.spelling_matches`, and byte-identical stdout and exit status on 95/95 committed inputs. THE WORD IS `CHEAPEST FOUND` AND NEVER `MINIMUM`, and that is a measured rule rather than a caution: this figure has been published as a minimum four times and overturned by the next search every time (`+19/+45` TASK_023, `-199/-2365` TASK_024, `-127/-2545` TASK_025_REVIEW), which with p05's makes five. Nor is it one pair: `chunks_exact(64)` is 72 Ir/call DEARER than `chunks_exact(32)` at `small`, because a larger chunk width leaves a longer scalar `.remainder()` tail and small's vlen is 124, so NO SINGLE SPELLING IS CHEAPEST ON BOTH BLOBS and a cheapest-found figure must name its input as well as its spelling (TASK_027). THE PER-BYTE NULL is neither untouched nor sign-wrong; it is SPELLING-CONDITIONAL, and the conditional version is exactly true. `4*nrec` is genuinely per record (slope 0.0000 Ir/byte on a residue-matched `vlen` sweep), but the per-byte RATE is a property of the FOLD SPELLING: 5.7500 for the shipped rolled fold that LLVM unrolls 4x, 6.50000 for `chunks_exact(4)`, 6.62500 for `chunks_exact(8)`, 5.18750 for `chunks_exact(16)`, 5.09375 for `chunks_exact(32)`, 5.04688 for `chunks_exact(64)`. So `5 + 3/K` is a THREE-POINT FIT and the two small chunk sizes falsify it, both being DEARER than the shipped rung because `try_into::<[u8;K]>()` makes LLVM emit one word load plus byte extraction instead of K direct `movzbl`. THOSE SIX RATES ARE DISASSEMBLY QUANTITIES (chunk-body insns / K) AND NOT FIVE-DECIMAL MEASURED SLOPES, which is a distinction any table of p16 rates must make (TASK_025_REVIEW minor 6): a marginal is `(Ir @ 200 - Ir @ 100)/100`, so the driver's one `println` does not cancel and what survives is the digit-count difference between the two checksums at ~0.2263 Ir per call per digit, divided by only `nrec*K` folded bytes in a residue-matched pair. Measured over `inputs/gen.py`'s fourth band at every offset, `chunks_exact(64)` reads 5.04219..5.05156 against an exact 5.04688, `chunks_exact(32)` reads 5.08266..5.10313 against 5.09375, and THE SHIPPED FOLD'S OWN 5.7500 -- p16's published headline rate -- IS THE LEAST REPRODUCIBLE OF THE SET AT +-0.09 Ir/byte, because a pair matched at its own K = 4 is only 8 folded bytes apart. Read a rate off `controls/foldcmp.py`, never off a two-point marginal. What IS exact, at all six of those spellings, is that the SAFE and UNSAFE slopes are EQUAL -- difference 0.00000, and swept rather than sampled: over 130 consecutive value lengths the safe-minus-unsafe difference is a SINGLE INTEGER per call at every point (10 / 11 / 12 / 12 / 12 for K = 4 / 8 / 16 / 32 / 64, and 17 at `vlen == 0 mod 4` / 21 otherwise for the shipped fold), slope of the difference 0.0000000, max residual 0.00 -- because the reslice and the `get_unchecked` both sit OUTSIDE the fold loop and the chunk body is the same instruction sequence on both sides (identical MNEMONIC sequence at K = 4, 8, 16, 32 AND 64; 26 / 53 / 83 / 163 / 323 insns). The shipped pair is the one row where identity is multiset-only: 23 insns each side, same instructions, different schedule. `R3 rate == R4 rate` therefore stands AT MATCHED SPELLING, the difference between rungs is per RECORD at every spelling (`2 + 5*nrec` for the chunked folds, against the shipped pair's `7 + 5*nrec` / `7 + 7*nrec`, the residue dependence vanishing once the folds match), and the `-0.65625 Ir/byte` a K=32 safe rung shows against the K=4 shipped unsafe one is a CROSS-SPELLING figure and not a safety cost. THAT NUMBER WAS PUBLISHED AS `-0.5625` IN FOUR FILES AND IS ARITHMETIC (TASK_025_REVIEW major 2): 5.09375 - 5.75 = -0.65625, and -0.5625 is the K=16 figure left pointing at the K=32 rung when the sentence was re-aimed. AND THE `NOT A SAFE-BEATS-UNSAFE RESULT` CLAIM IS WITHDRAWN. TASK_024 wrote that the same fold on the UNSAFE side is cheaper still (`R4ship - u_c32 = +221 / +2417`, the unsafe rung winning by `2 + 5*nrec`) and read that as `inf(R4) <= inf(R3)` by construction, measured. IT HAS NO RUNG BEHIND IT: `u_c32` cannot be a p16 R4 at all -- see AN R4 MUST BE VERUS-EXPRESSIBLE below -- so the comparison was never between two rungs. What IS supported is the mechanism the other way round: the SAFE class reaches fold spellings the UNSAFE class cannot, because this block's `identity` pin chains R4 to what vstd can verify while R3 is chained to nothing. Whether `inf(admissible R4) > inf(admissible R3)` on p16 is OPEN -- a hand-unrolled 32x fold with explicit indices is Verus-expressible in principle, is licensed by this block's own `unrolling` clause and measures 5.18750, and nobody has built it. THE REPORTING RULE THIS ADOPTS, which is NOT a declaration edit and excludes NO spelling. TASK_024 adopted the weak form -- `a per-byte rate is quoted with its fold spelling named, and a DIFFERENCE of per-byte rates is quoted only between rungs that fold the same way` -- and that form was IN FORCE while this very block's headline broke it, because a named cross-spelling difference still reads as a per-byte tax. The rule is therefore: NEVER PUBLISH A BARE PER-BYTE RATE, OR A CROSS-SPELLING DIFFERENCE OF TWO RATES, AS THIS PATTERN'S NUMBER; PUBLISH ONLY MATCHED-SPELLING DIFFERENCES. In contract, one exact-string substitution apart, p16's rate ranges 5.04688 .. 6.62500 -- a 31% spread -- with a seventh spelling at 5.37500, so a bare rate is not a property of the kernel. THE FOLD SPELLING IS DELIBERATELY NOT PINNED, and the CONCLUSION stands while EVERY REASON TASK_024 GAVE FOR IT IS WITHDRAWN (TASK_025_REVIEW majors 4 and 5). The reason that survives is that pinning WOULD NOT HAVE WORKED: this block licenses MANUAL UNROLLING BY NAME, and a manual 32x unroll measures 5.18750, still below the shipped 5.75, so an exclusion aimed at `chunks_exact` does not restore `+19` -- it moves the cheapest admissible safe spelling from one licensed family to another. WITHDRAWN: (a) `the direction test forbids it`, which was the load-bearing sentence -- `.memory/01-ladder.md` states that test as a SUFFICIENT CONDITION FOR INNOCENCE and then cites as a PASSING example p16's own TASK_017 exclusion, which RAISED this pattern's published tax 4.5x, so the stated clause and its own cited precedent point in opposite directions and the rule decided nothing; it is now flagged as broken there with a repair marked PROVISIONAL and unattacked, and must not be cited here again until a reviewer has attacked it. (b) ``chunks_exact(4)` is DEARER than shipped, so the free parameter is not a dial that only ever flatters the safe rung` -- AN ARTEFACT OF `try_into`, refuted by the first control ever run for that mechanism: the same `chunks_exact(4)` fold with the `try_into` step removed measures 5.37500 (43 insns / 8 bytes) and is 1509 Ir/call CHEAPER than the shipped R4 at `large`. The argument rested on the one spelling that happened to go the other way. What survives untouched is the disassembly observation, which was never a reason to refuse a pin: the shipped rungs are ALREADY 4x-unrolled, by LLVM, from rolled source, so there is no unroll-free baseline for a chunked fold to be a different KERNEL from -- same serial Horner chain, same bytes, same order, same one `movzbl` per byte, differing only in how many loop-exit tests survive. AN R4-SIDE VARIANT MUST BE EXPRESSIBLE IN WHAT vstd CAN VERIFY AT THE PINNED VSTD, OR IT IS NOT A RUNG. `AT THE PINNED VSTD` is part of the claim and not a hedge, and TASK_028 added it because the `r4_hdr` instance three lines down has carried the qualification since it was written while this general sentence did not, which made it a hashed claim about a tool version with no version in it: Verus prints `you may be able to add a Verus specification to this function with assume_specification` on every rejection, so an upstream vstd that ships one makes the same spelling admissible at ZERO TCB, and a disqualification here is a statement about `0.2026.08.09.92f466f` and not about Rust. WHAT DISQUALIFIES AND WHAT DOES NOT -- read the ERROR TEXT, never the exit code: `is not supported` disqualifies, because that is what forces a NEW TRUSTED ITEM, while `postcondition not satisfied` disqualifies NOTHING, because it is a proof nobody has written yet. Measured on p05's exec code two ways (TASK_027_REVIEW): the transplant plus a minimal ghost tidy gives `11 verified, 1 errors` -- postcondition not satisfied -- and THE SAME EXEC CODE with one real lemma and one `proof` block gives `13 verified, 0 errors`, at zero TCB. So a variant refused on a postcondition is an unfinished proof and stays a candidate; a variant refused on `is not supported` cannot be a rung without enlarging the trusted base. This is a property of THIS CONTRACT and not of any one experiment, and it is a CONSEQUENCE of the `identity` pin below rather than a new restriction: `identity: unsafe == verus, O3 exact` has been in this block since the pattern shipped, and it says an R4 is not merely a program that MAY use `unsafe` -- it is a program that must have a byte-identical R5 twin that Verus verifies. So the R4 class is bounded by what vstd can express and the R3 class is not, the two classes are INCOMPARABLE rather than nested, and the safe-side and unsafe-side levers this block leaves free are NOT the same category of edit. Two measured instances. (1) `r4_hdr` -- the unaligned `u16` header read -- CANNOT BE A p16 RUNG: Verus at the pinned vstd cannot verify `read_unaligned` (`../LearnVeri/_VERUS_DOC_/vstd/raw_ptr.rs:128-131`: unsupported because `PointsTo` enforces both non-nullness and alignment), so shipping it would need a FOURTH TRUSTED ITEM carrying a security-relevant `ensures` over an unaligned two-byte load, in the pattern whose entire memory-safety claim is ONE trusted `requires` (TCB 6 lines across 3 items). It is a control and only a control, and that is a cost the interval's arithmetic does not show. (2) NEITHER CAN ANY `chunks_exact` FOLD ON THE UNSAFE SIDE: building the R5 twin the pin demands (verus.rs with its exec fold replaced by `u_c32`'s, verbatim) makes Verus reject `chunks_exact`, `ChunksExact`, `by_ref`, `TryFromSliceError` and `get_unchecked` as unsupported -- FIVE new trusted items, where `r4_hdr` was disqualified for needing one (TASK_025_REVIEW blocker 1, four Verus logs). The R3-side variants -- `r3_endslice`, `r3_window`, `r3_hdrarray` and the chunked folds -- are safe Rust and cost ZERO TCB, so 'the same category of edit on the safe side' is measurably NOT the same category: the safe-side levers are free and larger. AUDIT THE TCB OF AN UNSAFE-SIDE VARIANT BEFORE DIFFERENCING IT: TASK_023 audited the R3 side only and TASK_024's headline was built on six unsafe-side probes nobody had costed. `controls/gen_controls.py` says all of this at the file level and said the `r4_hdr` half from the start; this block did not, and now does. NOTES.md 10a.2 is the write-up and `controls/{gen_controls,foldcmp}.py` plus `inputs/gen.py`'s fourth band are its reproduction path. Still deliberately NOT restricted: the R2/R3/R4 spelling of the value fold and of the header read beyond the two comparisons, and unrolling."
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
    "obligations": {"verus.rs": 10},
    "twin_obligations": {"verus.rs": 11},
    "obligations_note": "10 = fold_bytes 1 + tlv_walk 1 + kernel 3 + main 5, each term measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`. vlen_at and tlv_fold are non-recursive spec fns and carry 0; get_unchecked, load_input and emit are external_body and carry 0; kernel is body + 2 loop bodies; main is body + driver loop + one per `by (nonlinear_arith)`/`by { .. }` sub-proof in its two ghost blocks. `.memory/04-verus.md`'s one-per-function-plus-one-per-loop rule of thumb gives 7 here and is therefore not the derivation -- it predates a pattern with `by`-blocks in the driver.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 10 shipped + 1, and the 1 is measured: `--cfg slb_twin --verify-function slb_twin_get_unchecked --verify-root` reports `1 verified` -- one function, no loop body, no `by`-block. Pinned for the same reason the shipped count is: `tv > base_v` only says something extra compiled, and a twin that quietly lost its body, or an item that exists only under the cfg, moves this number and nothing else.",
    "items": {
      "verus.rs": {
        "vlen_at":    {"external": null, "requires": [], "ensures": []},
        "fold_bytes": {"external": null, "requires": [], "ensures": []},
        "tlv_walk":   {"external": null, "requires": [], "ensures": []},
        "tlv_fold":   {"external": null, "requires": [], "ensures": []},
        "get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "slb_twin_get_unchecked": {"external": null,
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "load_input": {"external": "verifier::external_body",
                       "requires": [], "ensures": []},
        "emit":       {"external": "verifier::external_body",
                       "requires": [], "ensures": []},
        "kernel":     {"external": null,
                       "requires": ["off + len <= buf@.len()"],
                       "ensures": ["r == tlv_fold(buf@, off as int, len as int)"]},
        "main":       {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                "c/main.c"],
    "aliases": {"c": {"n_body": "bytes.len()",
                      "bytes": "bytes.as_slice()",
                      "inp.n_iters": "n_iters"}},
    "call_args": {"c": {"kernel": [0, 2, 3]}},
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 3 && stride_w <= n_blob",
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
    "probe_inputs": ["small.bin", "large.bin"],
    "probe_iters": [100, 200],
    "note": "work_per_call is the WINDOW in bytes -- the stride, 508 on small and 4090 on large -- and the two differ precisely so that check.py's d(Ir)/d(work) assertion has two probe shapes and can run at all. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged. That is legitimate here where it was not for p02: p02's kernel is dominated by a bulk copy and glibc memcpy moves a byte in 0.104 Ir, so 0.25 forbade the fastest correct implementation. p16's inner loop is a serial `acc = acc*31 + byte` Horner chain -- each byte's result feeds the next multiply -- so there is no bulk-memory instruction and no vector form that could undercut the default. Measured margins are in NOTES.md 4."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost, on a kernel whose trip count is attacker data and whose loop invariant is a recursive spec function (10 obligations, an invariant_except_break/ensures pair for the early exit, two nonlinear steps in the driver). At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3. Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag -- because R4 inherits R5's proof and R5's proof is only as good as its trusted `ensures`, which need not be complete with respect to the operations the trusted body performs. On p16 that argument is at its strongest: the pattern's entire memory-safety claim is a trusted `requires`, there is no security `ensures` to back it up, and Miri on R4 is one of only two mechanical backstops (the other being stage 3c identity, which catches R5-only drift). Every input here is Miri-checkable: the cost is 4 iterations x the STRIDE, and the largest stride is 4090 bytes against a budget of ~3 M folded bytes.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed -- but note that p16 is the pattern where that hurts most, for the reason in `reason` above."
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

There is no exit 7 here. p02 has one because its payload names its own
destination-buffer capacity, so the driver allocates from an attacker-controlled
size and both languages must reject the same range identically before
allocating. p16's payload names no allocation size at all, so the check would be
dead code and copying it across would be worse than not having it.

## Degenerate shapes

The guard `stride_w >= 3 && stride_w <= n_blob` is the driver's whole input
validation. A stride below 3 cannot hold a header (`adversarial-stride2.bin`);
a stride above `n_blob` leaves no whole window, so `nwin` would be 0 and `k`
would have nothing to index. Either way the loop is skipped and the driver
prints `0` after zero kernel calls.

A window whose *tail* is 1 or 2 bytes (`adversarial-trunc.bin`) is not
degenerate — it is the ordinary end of a chain, handled by `end - p >= 3`, which
**every** rung including R1 keeps. All six rungs must agree on it.
