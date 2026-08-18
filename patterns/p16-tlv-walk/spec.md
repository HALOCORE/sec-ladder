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
  to `4·nrec − 8` Ir/call, so `R3 − R4` is an upper bound on the in-contract
  safety tax, not the tax (`NOTES.md` §10a). The additive spellings (`p + 3 <= end`,
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
has a *distribution* of work per call, and `check.py:625` needs one number and
hard-fails on `work <= 0` at `:632`; p02's min-over-records convention collapses
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
    "why": "the additive comparisons can overflow size_t on an attacker-chosen vlen and wave the attack through, which is the whole check p16 is about; an unread tag is deleted by LLVM and the walk stops looking like a TLV walk; a `if tag != 0 { skip }` branch adds an unpredictable data-dependent branch, which is a second new variable and belongs to p19/p35 (this box cannot measure branch misses). RESTATED in this hashed block at TASK_016 from the prose section 'Five things are load-bearing' above -- restated, not moved: the prose is still there, says the same thing, and THIS block is the authoritative copy of it (TASK_016_REVIEW m2). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 Ir/call flat and p02's by 3 to 4, so `R3ship - R4ship` is an UPPER BOUND on the in-contract safety tax and never the tax itself. Every pattern owes an in-contract spelling spread beside its headline; p16 and p17 have one from TASK_018 and p02 from TASK_019 (their NOTES.md 10a); p01, p05 and p08 do not. WHAT THE STANDARD SAYS ABOUT p16: rows 3, 4 and 6 of NOTES.md 10 (`.temp/p05r3/v16/tuned_split.rs`, `tuned_splitat.rs`, `unsafe_consume.rs`) contain NEITHER named comparison and are OUT OF CONTRACT under it. WHAT THIS BLOCK USED TO SAY, AND WHEN AND WHY IT CHANGED -- restored here because TASK_017 deleted it and TASK_016_REVIEW's honesty verdict rested on it (TASK_017_REVIEW M1). Until 89f6598 (2026-08-17) this `why` said, in these words: `Note what is deliberately NOT restricted: the R2/R3/R4 spelling of THE WALK and of the value fold, beyond the comparisons above`, and `A consuming spelling (split_first_chunk::<3>() plus split_at) IS ADMISSIBLE under this declaration and measures 10*nrec + 9 CHEAPER than the shipped R3`. Both sentences were written at TASK_016 with the measurement already in hand, i.e. against the author's own interest. TASK_017 removed `the walk` from the first, dropped the second, and kept verbatim a third -- `the honest move is to declare the walk's spelling here BEFORE measuring` -- which under the new reading advises a future task to do, before measuring, what TASK_017 had just done after measuring. So: the consuming spelling WAS admissible when TASK_015 measured it at ad661ed, and stopped being admissible four tasks later at 89f6598. Nobody may read p16's `+27/+77` as a pre-registered matched pair; the walk's spelling was pinned AFTER the measurement, and this sentence is the record of that. THE FOUR GROUNDS TASK_017 GAVE, with what survived. (i) House convention (p05's `i*ncol + j written out in every rung`, p02's `spelled identically in every rung`, p17's `the one conjunctive if start < end && start >= 0`) -- TASK_017_REVIEW found the citation cuts the other way textually, every cited entry carrying an explicit strictness marker p16's did not have, which is exactly why this is now POLICY and not a reading. (ii) `p` and `end` ARE the traversal representation -- true, but the claim TASK_017 built on it, that pinning them `is what makes R3 - R4 a difference in safety rather than a difference in representation`, is REFUTED BY MEASUREMENT AT TASK_018 and is WITHDRAWN; see the in-contract spread below. (iii) The exclusion falls symmetrically -- true in EXISTENCE (the consuming R4 control goes out too) and misleading in EFFECT (TASK_017_REVIEW M4): the published pair is `7 + 5*nrec` / `7 + 7*nrec` (+27 small, +77 large) against the excluded matched consuming pair's `7` flat / `7 + nrec` (+7, +17), so the reading makes p16's published safety tax 3.9x (small) / 4.5x (large) LARGER, and removes 49 (small) / 109 (large) Ir/call of headroom from the SAFE side against 29 / 49 from the unsafe side. Quote the numbers, not the word. (iv) `inf(R4) <= inf(R3)` by construction (.memory/01-ladder.md finding 14) -- correct, and it proves too much: it selects the pin for every pattern equally, which is why TASK_018 applies the standard to all six rather than to p16 alone. THE IN-CONTRACT SPREAD, MEASURED AT TASK_018 -- this is what TASK_017 owed and did not do; the table is NOTES.md 10a. Three admissible respellings of the two things this block leaves free (the header read and the value fold), all keeping BOTH named comparisons literally, all identical to shipped R3 on 73/73 committed inputs: `r3_endslice` is `2*nrec - 2` Ir/call CHEAPER than shipped R3, `r3_window` is `4*nrec - 8` cheaper, `r3_hdrarray` is `nrec` DEARER. At `large` (nrec 10) that is a 42 Ir/call spread INSIDE the contract against a published `R3 - R4` of 77; at `small` (nrec 4), 12 against 27. `r3_endslice` keeps `p` absolute and `end = off + len`, so it satisfies even ground (ii)'s own gloss. CONSEQUENCE, plainly: `the shipped R3 is the cheapest admissible spelling` is not unestablished, it is FALSE. p16's published `+27/+77` is an UPPER BOUND on the in-contract safety tax, whose measured in-contract minimum is `+19` (small) / `+45` (large) against the shipped R4 -- and since the R4 side has not been searched in contract, that is a bound too, not a safety number. Still deliberately NOT restricted: the R2/R3/R4 spelling of the value fold and of the header read beyond the two comparisons, and unrolling."
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
