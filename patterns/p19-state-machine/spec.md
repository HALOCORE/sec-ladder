# p19 — protocol state machine over a loaded transition table: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

⚠ **This file is NOT generated.** `.memory/05-layout.md` records three tasks in
a row that shipped a `spec.md` edit a generator silently reverted; p19 has no
`controls/mkcontract.py` and nothing will revert an edit here. The shared
named-spelling paragraph inside `idiom.why` was spliced in once from a donor
`spec.md` and its `sha256` is checked by `harness/check.py::named_spelling_problem`
on every run.

## What p19 is, and what it is NOT

p19 is a byte-at-a-time protocol decoder whose transition table **arrives in the
input**. Each window is `[2048-byte table][message]`; the decoder validates the
table once, then folds the message through it:

```c
for (p = 0; p < TBL; p++) if (w[p] >= NST) return REJ;   /* c/kernel.c omits this */
for (p = TBL; p < len; p++) { st = w[st * 256 + w[p]]; acc = acc * 31 + st; }
```

⚠ **THE UNFLATTERING SENTENCE COMES FIRST. p19's BUG CLASS IS THIS TREE'S
THIRTEENTH `index >= len`.** p01, p02, p03, p05, p07, p11, p12, p13, p14, p16,
p17 and p36 are all *"an index or a length is not checked against a buffer"*,
and so is this. p36 shipped the twelfth and said so; this is the thirteenth and
says so. Its nearest sibling is **p36** — an index out of a dispatch table.

⚠⚠ **AND THE MEMORY-UNSAFE FRAMING IS CONDITIONAL. THE CONDITION IS NAMED, IT
IS PINNED IN THE HASHED BLOCK BELOW, AND IT WAS SETTLED BY RUNS BEFORE ANY CELL
WAS BUILT** (`NOTES.md` 0a). A textbook "state confusion" bug is a **logic** bug
with no out-of-bounds access at all, and this row would have had to be refused
the way `p31` was. It is not, because **both** of the following hold and both
are `forbidden` entries in the contract:

| | measured in |
|---|---|
| **the table is LOADED DATA, not a program constant.** With a tool-generated table (flex / ragel / re2c) every entry is in range by construction: 0 out-of-range successors over all 2048 (state, byte) pairs, and 1e6 adversarial bytes never leave state 7. The OOB is **unreachable** | `NOTES.md` 0a run A |
| **the decoder dispatches by INDEXING, not by `switch`.** The identical bad entry written as `switch (st) { … default: }` is a wrong answer with **no memory event at all** — ASan and UBSan both silent. That is p31's shape, demonstrated rather than argued | `NOTES.md` 0a run C |

**Both hold of real DFA decoders**, and the precedent is not hypothetical. The
Linux kernel's AppArmor policy engine (`security/apparmor/match.c`) folds with

```c
pos = base_idx(base[state]) + (u8) *str++;
if (check[pos] == state) state = next[pos]; else state = def[state];
```

— four unchecked loads — licensed by `verify_dfa()` having walked the whole
unpacked table **once** at policy load:

```c
for (i = 0; i < state_count; i++)
    if (DEFAULT_TABLE(dfa)[i] >= state_count) { pr_err("AppArmor DFA default state out of bounds"); goto out; }
for (i = 0; i < trans_count; i++) {
    if (NEXT_TABLE(dfa)[i]  >= state_count) goto out;
    if (CHECK_TABLE(dfa)[i] >= state_count) goto out;
}
```

The tables are unpacked from a userspace-supplied binary policy blob, and
getting that validator wrong is a live CVE class. **The one this pattern models
is `CVE-2026-23407`** *"apparmor: fix missing bounds check on DEFAULT table in
`verify_dfa()`"*, whose description is p19's bug in the CVE's own words: *"it
reads `k = DEFAULT_TABLE[j]` and uses `k` as an array index without validation.
A malformed DFA with `DEFAULT_TABLE[j] >= state_count`, therefore, causes both
out-of-bounds reads and writes."* ⚠ **`CVE-2026-23269` is cited here for the
class and NOT for the shape**: its real title is *"apparmor: validate DFA start
states are in bounds in `unpack_pdb`"* and its bug is an untrusted *start
state*, which p19 does not model — the walk starts at `st = 0` by construction.
An earlier version of this paragraph gave it a paraphrased title in quotation
marks and attributed p19's shape to it (TASK_087_REVIEW major 3).
**So "validate the whole table once, then index it unchecked" is not a benchmark
contrivance; it is the shipped kernel idiom, and it is exactly this pattern's
R4/R5 rung.**

Three things are new here and none of them is the bug class:

| | measured in |
|---|---|
| **the obligation is a LOOP-CARRIED DATA INVARIANT.** `st < NST` holds because 2048 bytes read out of the input at run time were checked once before the loop — not because of arithmetic on a loop counter. Nothing else in this tree has that shape | `NOTES.md` 6 |
| **a rung boundary INSIDE the safe class, worth exactly one instruction per byte.** Safe Rust can reach within `1.00000 Ir/byte` of unsafe Rust by masking, and not to it; the one instruction is `and $0x7`, and adding the same mask to the *unsafe* rung costs the identical +1.00, which is how it is attributed to the mask rather than to the check. **This is p47's shape.** ⚠ *"p47 is the only other pattern with one"* is `.memory/06-catalogue.md`'s reading of its own three probes, quoted and NOT re-measured here | `NOTES.md` 8 |
| **the two hardening strategies have different ASYMPTOTICS.** C's validation pass is `O(table)` once per call; safe Rust's per-access check is `O(message)` per byte. They are not interchangeable and the pattern prices both | `NOTES.md` 9 |

✅ **What is NOT p09's**: the mask is p09's `q & 31` used as the **fix** rather
than as the bug, and the behaviour matrix — reject / silent state confusion /
named overflow / unnameable overflow — is not p09's. **One byte of one table
entry decides which of the last three happens**, and all three are shipped as
inputs.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C, R1h C-hardened | `uint64_t kernel(const uint8_t *buf, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

Three C arguments against three Rust ones, but the Rust kernel takes four
registers because `&[u8]` is a pointer *and* a length. That is p01's asymmetry
and it is the finding, not a rigging: the length is the thing C does not have
and therefore cannot check. Do not "fix" it by giving C a dead `buf_len`; the
contract forbids that by name.

## Window layout

The window is `buf[off .. off+len)` and everything is window-relative:

```
byte 0    .. 2048   the transition table, NST rows of 256   ATTACKER DATA
byte 2048 .. len    the message                             ATTACKER DATA

NST = 8      the decoder's FIXED table capacity, a compile-time constant in
             every rung -- the array the loaded table has to fit into, exactly
             as AppArmor's `state_count` bounds its unpacked tables
TBL = NST * 256 = 2048
REJ = 0xD1B54A32D192ED03     what an invalid table folds to
```

`NST`, `TBL` and `REJ` are compile-time constants in every rung. They are
properties of the *program*; `n_iters`, `stride`, `n_blob`, every table entry
and every message byte come from the file.

**One out-of-range entry anywhere in 2048 is enough**, so the bug is one byte
away from every conforming input.

## Semantics

```
if len <= TBL:                             return 0

# >>> THE SAFETY LINE. c/kernel.c omits exactly this loop. <<<
for i in 0 .. TBL:
    if w[i] >= NST:                        return REJ

st = 0 ; acc = 0
for p in TBL .. len:
    st  = w[st * 256 + w[p]]                       # THE TRANSITION
    acc = acc *64 31 +64 st
return acc *64 31 +64 st
```

`*64` and `+64` are wrapping `u64` operations. Wrapping, not checked, is
deliberate: it makes the kernel *total on values*, so R5's only obligation is
the memory-safety one and no value bound is smuggled in that the input generator
would then have to be trusted to respect.

**The fold is one indexed load, one multiply and one add per message byte, on
purpose.** The finding is the table lookup and the invariant that licenses it; a
heavier fold would drown the single instruction that separates safe-tuned from
unsafe.

⚠ **Every rung validates**, so all six compute the same function on every input
including the adversarial ones, and R2-vs-R3 is a comparison of two spellings
rather than of two programs. `c/kernel.c` is the one cell that does not, and
that omission is the bug.

## The rungs, in one table

| rung | the row expression | how it knows `st < NST` | Ir per message byte |
|---|---|---|---|
| R1 `c/kernel.c` | `w[st * 256 + w[p]]` | **it does not** | — |
| R1h `c/kernel_hardened.c` | `w[st * 256 + w[p]]` | the validation pass | — |
| R2 `safe_naive.rs` | `tbl[st * 256 + b as usize]` | the language checks it per access | **15.00000** |
| R3 `safe_tuned.rs` | `tbl[(st & (NST - 1)) * 256 + b as usize]` | it forces it, per access, with a mask | **9.75000** |
| R4 `unsafe.rs` | `*tbl.get_unchecked(st * 256 + b)` | the author asserts it | **8.75000** |
| R5 `verus.rs` | the same, verbatim | **Verus proves it** | **8.75000** |

The rates are `body_len / K` read off the disassembly, not marginals
(`.tasks/TASK_026.md` §0 item 2). `NOTES.md` 8 carries the whole derivation, the
rolled-vs-rolled control that splits R2's 6.25 into 3.00 check + 3.25 foreclosed
unroll, and the instruction-by-instruction diff that names the third one.

## The adversarial rows

⚠ **THREE ROWS THAT DIFFER IN ONE BYTE OF ONE TABLE ENTRY, AND THEY BEHAVE
THREE DIFFERENT WAYS.** `inputs/gen.py` asserts the one-byte distance and
prints it every run. All three are **silent at plain `-O2`, exit 0, with a wrong
checksum**; what changes is how far past the object the index lands, and
therefore what a sanitizer can say about it.

| input | table entry | where row `entry` starts | ASan + UBSan on R1 |
|---|---|---|---|
| `adversarial-confuse` | **8** — the nearest out-of-table state | window byte 2048: **inside the window's own message** | **clean.** Defined behaviour; the message is read as if it were a transition row. Pure state confusion, and the reason p19's memory-safety claim is bounded rather than blanket |
| `adversarial-oobnear` | **10** | window byte 2560: **0…255 bytes past a 2 560-byte blob** | **`heap-buffer-overflow`**, `READ of size 1`, *"5 bytes after 2560-byte region"*, and it names the allocation site `slb_head1_u64_bytes common/driver.c:157` |
| `adversarial-oob` | **255** | window byte 65 280 | **`SEGV on unknown address`**, *"The signal is caused by a READ memory access"*, and *"AddressSanitizer can not provide additional info"* — too far out for the shadow map, so the object is not named |
| `adversarial-tiny` | — | stride 64, below the table size | every rung returns 0; the kernel's degenerate branch is reachable from the measured domain instead of being dead code the proof still carries |
| `adversarial-shortlen` | — | `payload_len` declares 64 bytes more than the file carries | `slb_load` / `driver::load` exits 5 |

**So "the sanitizer catches it" is bounded too**: one attacker byte decides
between no diagnostic, a diagnostic that names the object, and a diagnostic that
cannot.

⚠ **`sanitizer_expect` is COMPUTED, not declared by name.** `model.py`
simulates `c/kernel.c` and reports whether the walk leaves `[0, n_blob)`, and
`inputs/gen.py` re-implements the same detector independently and refuses to
write a blob whose declaration disagrees with it. So the "fires" on one row and
the "clean" on the other are both measurements, and neither can be mislabelled
by editing prose.

⚠ **The plain-build harm is SILENT, and the `exit 139 SIGSEGV` that
`TASK_086`'s probe reported for this row is a STORAGE-CLASS artefact.** That
probe put the table in `static uint8_t TBL[8][256]`, i.e. `.bss`, where row 200
is 51 200 bytes past a 2 048-byte object and leaves the segment. p19's table
must be loaded data — with a constant table the bug is unreachable at all — and
loaded data lives in the driver's heap payload buffer. Both were run:
`NOTES.md` 0b.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. The pins exist because a green verification and
a green gate are, separately, evidence of very little; `patterns/p01-array-sum/spec.md`
carries the table of which bypass each pin closes and it is not repeated here.

Two pins are specific to p19 and worth reading before the block:

| pin | what it is doing here |
|---|---|
| `idiom.forbidden[0]` and `[1]` | **the bug class's own preconditions, written as spellings.** `switch (st)` and a `static` table are each excluded because a rung that took either would still compute p19's function and would no longer model p19's bug. They forbid a spelling for being *safe* rather than for being *fast* — ⚠ **p19 is the third pattern to do that and not the first**, after p36's `op & 7` / `op % 8` (masking makes every byte a legal opcode, so the adversarial input stops being adversarial) and p03's `& (STACK_CAP - 1)` (masking turns an out-of-range access into an in-range one). `NOTES.md` §0a carries both quotations. |
| `identity` | pinned `exact` at O3, and established **before either rung was written**: an R4 written with `&w[0..TBL]` and the R5 written with `vstd::slice::slice_subrange` compile to the same 235 bytes, `md5 ac3fb207cd05963419d722adcd8b9da2`, extracted from the **linked** binaries because a relocated field is zero in an object file (`TASK_086` #238). |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == st_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (st_fold). `requires` is about the WINDOW's placement in the blob and nothing else: the kernel is TOTAL on the contents of the window, which is what lets every adversarial input -- an invalid table included -- sit inside the proof domain rather than outside it.",
  "idiom": {
    "required": [
      {
        "c": "every rung validates the WHOLE transition table before the fold, and `>= SLB_P19_NST` is that test. `c/kernel_hardened.c` spells it; `c/kernel.c` DOES NOT, and that omission is the bug this pattern models. The idiom audit prints the absence, and the absence is the vulnerability.",
        "rust": "every Rust rung validates the WHOLE transition table before the fold, spelled `>= NST`. It is what makes `st < NST` true at the top of the fold in all four."
      },
      {
        "c": "the fold is one indexed load, one multiply and one add per message byte, spelled `acc * 31 + st`; C's unsigned arithmetic wraps by definition (6.2.5p9) so it needs no special spelling.",
        "rust": "the fold is one indexed load, one multiply and one add per message byte, spelled `acc.wrapping_mul(31).wrapping_add(` -- wrapping, not checked, so the kernel is total on VALUES and the only obligation is the index."
      },
      {
        "rust": "THE RUNG BOUNDARY INSIDE THE SAFE CLASS, and it is one token. R2 spells the row `st * 256 + b as usize`; R3 spells it `(st & (NST - 1)) * 256 + b as usize`. Each is present in exactly one rung by construction, so the audit reports the other three as absent for both -- that is the declaration working, not failing."
      },
      "the transition table is ATTACKER DATA read out of the window and is never a compile-time constant, and the decoder dispatches by INDEXING it rather than by switching on the state. Both halves are conditions on the BUG CLASS rather than on the cost, both are forbidden below by name, and both were settled by a run before any cell was written (NOTES.md 0a).",
      "the Rust rungs take the window as a sub-slice of `buf` and index that, so the table's length is a compile-time constant to LLVM and the masked index is provably in range. Absolute indexing is forbidden below and it is forbidden for a measured reason, not an aesthetic one."
    ],
    "forbidden": [
      {
        "c": "`switch (st)` -- the hand-rolled dispatch. It is not slower and it is not wrong; it DELETES THE PATTERN, because an out-of-range state then falls to `default` and there is no memory-safety event at all. Measured, not argued: NOTES.md 0a run C, ASan and UBSan both silent. This entry is the bug class's own precondition written as a spelling.",
        "rust": "`match st {` -- the same exclusion on the Rust side."
      },
      {
        "c": "`static uint8_t` -- a compile-time transition table. With one, every entry is in range by construction and the bug is UNREACHABLE: NOTES.md 0a run A checks all 2048 state-byte successors exhaustively and drives 1e6 adversarial bytes without leaving state 7.",
        "rust": "`const TABLE` -- the same exclusion."
      },
      {
        "rust": "`buf[off +` -- absolute indexing instead of a sub-slice. Measured (NOTES.md 10): +2.25 Ir/byte on the UNSAFE rung, because the window offset cannot be folded into the base pointer and the fold unrolls 2x instead of 4x; and +10.87 Ir/byte on the MASKED safe rung, because the blob length is a runtime value so the bounds check stops being elidable. It would turn the safe-vs-unsafe comparison into a comparison of base-pointer arithmetic. NOTE the backticked span is the WHOLE of what this entry pins: no other word here is in backticks, because a stray pair around a common identifier is audited as a forbidden spelling in its own right and hit all four Rust rungs on this pattern's first gate run."
      },
      {
        "rust": "`st % NST` -- the modulo clamp. Semantically identical to the mask under this contract, and a different instruction at a different price; naming it keeps R3's number attached to R3's spelling."
      },
      "a dead `buf_len` parameter on the C kernel. The length is the thing C does not have and therefore cannot check; handing C one to make the signatures match would be Rust-in-C-syntax and would delete half the comparison."
    ],
    "why": "p19's whole question is where the fact `st < NST` comes from, and every entry above is about that. The kernel folds a message through a transition table that arrives IN THE INPUT, one indexed load per byte, and `st` is loop-carried and data-dependent -- so no bounds check on `tbl[st * 256 + b]` can be hoisted, and the check's exit edge forecloses the 4x unroll the unchecked spelling gets. Three rungs establish the same fact three ways and the pattern prices all three: R5 proves it statically (0 instructions), R3 re-establishes it dynamically with a mask (1 instruction per message byte), R2 tests it per access (measured 6.25 per message byte against R4, of which 3.00 is the check and 3.25 is the unroll it forbids). THE MASK IS A RESPELLING AND NOT A DIFFERENT PROGRAM, AND THE REASON IS THE VALIDATION PASS: after it, `st < NST` holds on every path that reaches the fold, so `st & (NST - 1) == st` identically on every input this benchmark can present, adversarial ones included -- and that equality IS the loop invariant verus.rs discharges. Delete the validation pass and the claim fails: the mask would silently remap an out-of-range state where the checked spelling panics, and R2 and R3 would be two different benchmarks rather than two spellings of one. That is why `required[0]` pins the validation pass in every rung and why the C rung that omits it is the BUG rather than a cheaper rung. THE TWO `forbidden` ENTRIES ABOUT THE BUG CLASS ARE CONDITIONS, NOT TASTE. A textbook \"state confusion\" bug is a LOGIC bug with no out-of-bounds access, and p19 escapes that only because the table is loaded data and the dispatch is an index. Both were settled by runs before any cell was written (NOTES.md 0a): with a tool-generated table, all 2048 state-byte successors are in range by construction and 1e6 adversarial bytes never leave state 7; with a `switch`, the same bad entry falls to `default` and ASan and UBSan are both silent. A rung that took either route would still compute the pattern's function and would no longer model the pattern's bug, which is exactly what a `forbidden` entry is for. WHAT THE BACKTICKED PINS COST IN AUDIT NOISE, SAID HERE RATHER THAN DISCOVERED: `required[2]` backticks two spellings that are present in exactly one rung each, by construction -- they are the R2/R3 boundary -- so the idiom audit reports each as absent from the other three Rust rungs. That is the declaration working. `required[0]`'s C spelling is absent from `c/kernel.c` for the same kind of reason and it is the sharpest line the audit prints about this pattern: the missing spelling is the vulnerability. p19's numbers are still a spelling's numbers, and the in-contract spread is measured on BOTH sides rather than one (NOTES.md 10): three R2 spellings span 12 Ir/call, three R3 spellings span 11, and three R4 spellings span 11, at m = 4096 -- comparable lever counts, all three degenerate. A fourth R3 spelling, the branch clamp `if st < NST { st } else { 0 }`, is 8.25 Ir/byte dearer than R4, i.e. dearer than the bounds check it replaces; it is in contract and it is not shipped, and saying so is the point of the spread. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      " as int": "",
      "buf@": "buf",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 12
    },
    "twin_obligations": {
      "verus.rs": 13
    },
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 12 shipped + 1 for slb_twin_buf_get_unchecked.",
    "items": {
      "verus.rs": {
        "tbl_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "window_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "st_fold": {
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
            "r == st_fold(buf@, off as int, len as int)"
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
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w > 0 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100. A difference of two runs of the same binary, so the one-shot loader terms that make whole-program Ir unquotable cancel -- not EXACTLY, see p01's copy of this note for the two surviving terms and their measured size. The two probe inputs have different work per call (2304 vs 6144 bytes), so check.py can also assert d(Ir)/d(work) >= ALPHA. The floor is NOT declared here: check.py derives it from model.py's work_per_call."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5: the proof licenses unsafe code at zero cost. Established BEFORE either rung was written and not after: a plain-rustc kernel written with `&buf[off..off + len]` and `&w[0..TBL]` and the Verus kernel written with `vstd::slice::slice_subrange` are byte-identical -- 235 B, md5 ac3fb207cd05963419d722adcd8b9da2, extracted from the LINKED binaries because a relocated field is zero in an object file (TASK_086 #238). At O0 the crate names differ in length so call displacements differ -- link layout, not codegen."
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
    "reason": "R4 and R5 ARE byte-identical at O3 (`identity` above pins `exact`), and that does not make Miri optional: `.memory/02-bench-rules.md` makes it mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. The reason byte-identity is not an excuse: R4 inherits R5's proof, and R5's proof is only as good as its trusted `ensures`, which need not be COMPLETE with respect to the operations the trusted body performs. Miri is the only backstop for that class, and here it has a specific job: p19's unchecked read is indexed by a value that came out of the buffer being read, so a wrong invariant produces a read that is in bounds of the allocation on most inputs and out of it on one.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). p19's inputs are sized for it -- the largest blob is 98 304 bytes and a call touches at most 6 144 -- so no row is expected to block. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  }
}
```

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p19's payload is p36's, p22's, p38's, p47's and
eleven others':

```
word 0     u64  stride     # bytes per window
byte 8..   u8[] blob       # the windows
```

Nothing is a compile-time constant: `n_iters`, `stride` and `n_blob` all come
from the file, and so does every byte of every table and every message.

## Driver loop

Identical in all five rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` step 6 normalises every copy — the C one included —
with `harness/dloop.py` and diffs each against the canonical token sequence
pinned above.

```
n_blob := bytes.len()
buf    := bytes.as_slice()
acc    := 0
if stride_w > 0 and stride_w <= n_blob:
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

### Why this does not evaporate

`k` is derived from `acc`, and `acc` is derived from the previous call's result.
Call *i+1* therefore cannot begin until call *i* has returned, so LLVM can
neither CSE the calls nor hoist them out of the loop, and no `black_box` or
`asm volatile` is needed — which matters, because those two are not equally
strong barriers and using them would put a C-vs-Rust asymmetry in the driver.
The mechanism is the same arithmetic in both languages.

### The barrier is a multiply-shift, not a modulo

`k = (acc * nwin) >> 64` in 128-bit arithmetic — Lemire's map from a uniform
`u64` onto `[0, nwin)`. p01's `spec.md` carries the measurement that motivated
the swap: a 64-bit `div` is ~0.1 % of `Ir` but 20–40 cycles of latency on the
serial dependency chain, i.e. a rung-independent additive constant that
compresses every cross-rung wall-clock ratio toward 1 — the direction that
flatters this project's own headline.

It costs three ghost `proof` blocks in R5, all of them nonlinear; they erase, so
R5's driver loop is byte-identical to R4's.

### The one guard, and why it is weak on purpose

`stride_w > 0` is there for the division alone. A stride at or below the table
size is **not** rejected here: it reaches the kernel, whose own `len <= TBL`
test returns 0. That makes the kernel's degenerate branch reachable from the
measured domain instead of being dead code the proof still has to discharge, and
`adversarial-tiny.bin` is the input that exercises it. `n_iters == 0` is handled
by the `while` itself.

`payload_len` declaring more bytes than the file carries is caught earlier, in
`slb_load` / `driver::load`, which exits `5`; `adversarial-shortlen.bin` is that
input.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |
