# p42 — `goto cleanup` error handling: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## ⚠ WHAT THIS PATTERN PRICES, DECLARED BEFORE IT WAS MEASURED

**p42's subject is a BEHAVIOUR MATRIX, not a cost.** A `free` that is never
executed has no per-element price and this pattern does not manufacture one.
What it prices is the *scratch*: what each rung pays to acquire, initialise and
release a heap buffer it holds for the length of one call, on the path where
nothing goes wrong. The leak itself is priced at exactly what it costs, which is
**`0.00` on the success path** — R1 and R1h differ by one branch target and by
nothing else.

So the row has three results and they are different kinds of thing:

| result | kind | where |
|---|---|---|
| R1 leaks on the error path; R1h, R2, R3, R4, R5 do not | behaviour matrix, detector-backed | `model.py::sanitizer_expect`, gate stage 7 |
| R1 − R1h on the success path | a cost, and it is `0.00` | NOTES.md 8 |
| what a scratch buffer costs per element, per rung | a cost, and it is not zero | NOTES.md 9 |

⚠ **The zero in the middle row is a RESULT, and its axis is named here in
advance** — `.memory/06-catalogue.md`'s probe 3. It is not "safety is free".

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C | `uint64_t kernel(const uint64_t *v, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(v: &[u64], off: usize, len: usize) -> u64` |

The C kernel takes three arguments; the Rust kernels take four registers,
because `&[u64]` is a pointer *and* a length. That asymmetry is p01's and is
deliberate: the length is the thing C does not have and therefore cannot check.

`len` is **both** the window length in `u64` elements **and** the digest length
in bytes. That is not a coincidence to be tidied away: it is what makes the
allocation size input-derived, which is what makes it a heap allocation rather
than a stack array (see `forbidden` below).

## Semantics

```
kernel(v, off, len):
    dig := a heap buffer of `len` BYTES          # allocated FIRST
    if (v[off] & 0xff) != TAG:                   # the record tag is wrong
        ERROR PATH -> release dig; return 0      # R1 does NOT release it
    run := 0
    for i in 0 .. len:
        run    := run +64 (v[off+i] ^ MIX)
        dig[i] := (uint8_t)(run >> 24)
    acc := 0
    for i in 0 .. len:
        acc := acc *64 31 +64 dig[len-1-i]       # the digest, BACKWARDS
    release dig
    return acc
```

`TAG = 0xA7`, `MIX = 0x9E3779B97F4A7C15`. `+64` and `*64` are wrapping.

**Three things in that are load-bearing and are pinned in the block below.**

1. **The allocation precedes the tag test.** Take the working storage, then
   parse. This is the ordinary order and it is what makes an error path capable
   of leaking at all; hoisting the test above the allocation is not a tuning, it
   is the fix for the bug the pattern models.
2. **The digest byte is `run >> 24`, not `run`.** `run` is a wrapping sum, so
   its bits 0..7 depend only on bits 0..7 of the inputs — and those carry the
   record tag, which is `TAG` on every well-formed window. A digest taken from
   the low byte would be a function of `len` alone and the kernel would not read
   its input at all. The first draft of `c/kernel.c` had exactly that and the
   generator's data-dependence control is what caught it (NOTES.md 4).
3. **The fold runs backwards.** The last digest byte is needed first and it is a
   function of every element before it, so the digest has to be *materialised*.
   A forward fold could be fused with the scan and the allocation would become
   dead — which clang does eliminate: a heap block whose stores it can forward
   is deleted at `-O1` and above, measured, with a control (NOTES.md 4).

## The bug, and the real code it is modelled on

R1 is single-exit C with a `goto cleanup` chain, the shape SEI CERT **MEM12-C**
recommends ("Consider using a goto chain when leaving a function on error when
using and releasing resources"). Its bug is the failure mode that rule warns
about: **one error branch leaves without joining the chain.**

Precedent, fetched and quoted rather than remembered — Linux commit
`505d9dcb0f7ddf9d075e729523a33d38642ae680`, *"crypto: ccp - fix resource leaks in
`ccp_run_aes_gcm_cmd()`"*, `drivers/crypto/ccp/ccp-ops.c`:

```
 		if (ret)
-			goto e_ctx;
+			goto e_aad;
```

`e_ctx` sits *below* `e_aad` in the cleanup chain, so the wrong label skipped the
AAD work area's release. That is **CVE-2021-3764**, whose description reads *"A
memory leak flaw was found in the Linux kernel's `ccp_run_aes_gcm_cmd()` function
that allows an attacker to cause a denial of service"* (CVSS 3.1 base 5.5,
`AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`). p42's C rung does the simpler half of the
same mistake — a bare `return` where a `goto cleanup` belonged — because one
label is easier to read in 25 lines than a five-link chain.

`c/kernel_hardened.c` (R1h) differs from `c/kernel.c` in **one statement** and
returns the same value on that path, so R1-vs-R1h prices the leak inside one
language rather than across two.

## Contract

```
requires:  off + len <= v_len  and  1 <= len <= isize::MAX
ensures:   result == digest_fold(v, off, len)
```

`harness/check.py` parses the block below, drives `model.py` against **every**
input file — `adversarial` included — and evaluates `requires` at every call the
benchmark actually makes and `ensures` against every value it actually returns.

⚠ **`1 <= len <= isize::MAX` is R5's doing and is disclosed rather than buried.**
`vstd::layout::valid_layout(size, 1)` is `size <= isize::MAX`, and the pinned
vstd axiomatises **no** bound on a slice's length below `usize::MAX` — `grep -rn
'isize::MAX' ~/tools/verus/vstd/` finds it only inside `layout.rs` itself. The
ceiling therefore has to come from the driver, and it does: `win_len_w <=
MAXWIN` with `MAXWIN = 65536`, one conjunct in the guard that already exists,
outside the measured loop, carried by all six rungs and costing nothing per
call. It is p17's route, and it is also the ceiling a C program that allocates
from an untrusted header owes anyway. `inputs/adversarial-wincap.bin` reaches it
and nothing else — a window larger than the cap but smaller than the array.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. The pin table is p01's; what is specific to p42
is which conditions the `forbidden` list has to carry.

| pin | the bypass it closes |
|---|---|
| `verus.obligations` | `#[verifier::external_body] fn main` — no call site verifies, so no precondition is discharged. The pilot's fatal defect. |
| `verus.items[*].requires` / `.ensures` | deleting a `requires` from an `external_body` wrapper silently deletes every caller's obligation and moves no count. Only a textual diff against a pin catches it. |
| the item set itself | a *new* `external_body` item can otherwise be added without the TCB tally noticing. |
| `driver.canonical` | the driver loop is diffed against a pinned token sequence rather than rung-against-rung, so a mutation applied to *every* rung is still caught. |
| `collapse.probe_inputs` | a kernel that got constant-folded away still has a backward branch somewhere. The floor is derived from `model.work_per_call`. |
| `verus.translate` | `contract.requires` (Python) and `verus.items[*].requires` (Verus) used to be two independent transcriptions of one predicate. The Python side is now *generated* from the Verus clause text. |
| `driver.regions` | deleting the two `SLB-DRIVER` marker comments used to make a rung vanish from the driver diff silently. |
| `identity` | recorded as a **result** *and* enforced. A drop below the pinned level calls `rep.fail` (`check.py`'s `check_identity`). |
| `idiom.forbidden` | ⚠ **p42's are not stylistic.** They are the CONDITIONS under which the row's claim is true: heap not stack, a real `free` not a freelist push, an error path a committed input reaches, and no Rust rung permitted to leak deliberately. Delete any one and the pattern is measuring something else. |

```slb-contract
{
  "kernel": "kernel(v: &[u64], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": ["off + len <= v_len", "1 <= len <= 9223372036854775807"],
  "ensures": ["result == digest_fold(v, off, len)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (off/len/v_len/v/result) plus the helper it supplies (digest_fold, which is model.py's SECOND implementation -- the literal accumulate-truncate-fold-backwards one, not the prefix-table simulation the checksum comes from).",

  "idiom": {
    "required": [
      "the digest buffer is acquired BEFORE the tag test and released after it, in every rung. Take the working storage, then parse. This is the order that makes an error path capable of leaking; a rung that tests first is not a port of the C rung, it is the fix.",
      {"c": "goto cleanup"},
      {"c": "(uint8_t)(run >> 24)", "rust": "(run >> 24) as u8"},
      "the digest is folded BACKWARDS -- `dig[len-1]` first -- so that it must be materialised. Scoped to all six rungs; a forward fold is fusible with the scan and clang deletes the allocation.",
      "R2 acquires with `vec![0u8; len]` and indexes; R3 acquires with `Vec::with_capacity` and fills with `extend`; R4 and R5 acquire and release by hand through `std::alloc::alloc` / `std::alloc::dealloc`. Scoped one entry per rung, by name, and stated here rather than backticked because no single spelling covers all four."
    ],
    "forbidden": [
      "a STACK buffer for the digest. The allocation size is the window length, which comes from the file, so a stack array would have to be fixed-size and over-large -- and a stack array cannot leak, which deletes the pattern. This is a CONDITION of p42's claim, not a style rule. NOTE: this entry deliberately quotes NO spelling, because a backticked span in a forbidden entry is a forbidden SPELLING and every rung legitimately writes the words this condition is about.",
      "a freelist, arena or slab in place of the allocator. The release must be a REAL allocator release: pushing the block onto a pattern-local freelist leaves the leaked block inside a live allocation, LeakSanitizer sees nothing, and the row measures bookkeeping instead of memory. p33's refusal is the precedent -- asking whether a rung released its heap blocks is vacuous for an allocator. Quotes no spelling, for the reason the entry above gives.",
      "an error path that no committed input reaches. The generator asserts the reachability by simulation and the model's selfcheck re-asserts it; p31 died on exactly the shape where the interesting path is unreachable. Quotes no spelling.",
      "a measured input -- the two the collapse probe names -- that reaches the error path. Those cells would then be timing a leaking program and the leak would grow with the iteration count. The model's selfcheck fails on it. Quotes no spelling.",
      {"rust": "`ManuallyDrop`"},
      {"rust": "`mem::forget`"},
      {"rust": "`Box::leak`"},
      {"rust": "`Box::into_raw`"}
    ],
    "why": "p42 models a LEAK, and a leak is a property of a program's whole execution rather than of any one instruction, so the declaration has to pin the CONDITIONS under which the measurement means what it says -- which is why four of the forbidden entries are prose about shape rather than backticked tokens. HEAP, not stack: `len` is the window length and also the digest length in bytes, so the allocation size comes from the file; a stack array would have to be a fixed over-allocation and a stack array cannot leak at all, so the row would have no subject. A REAL free, not a freelist: p33's refusal measured that `did the rung release its heap blocks?` reads zero on BOTH sides for an allocator, because a C free-list allocator also calls `free()` once at teardown, and the same collapse would happen here if the digest went back to a pool. REACHABLE: `p31` was refused because its interesting path did not exist in any committed input, and p42 avoids that mechanically rather than by inspection -- `inputs/gen.py` replays the driver loop through `model.py` before writing each file and asserts the (ok, err) call counts the case declares, `adversarial-mixed.bin` is asserted to reach BOTH paths, and `model.py::selfcheck` re-asserts both properties at gate time. NOT ON A MEASURED INPUT: the converse condition, and it is the one that would corrupt the numbers rather than the story. ⚠ THE FIRST FOUR `forbidden` ENTRIES BACKTICK NO SPELLING, DELIBERATELY, AND THE GATE'S SHOUT ABOUT THEM IS PERMANENT AND CORRECT: each forbids a STRUCTURE rather than a token -- a storage class, an allocator discipline, a reachability property of the committed inputs -- and `check.py::spelling_matches` decides tokens, not structures. p05's `a running row pointer` is the precedent the gate itself names. What enforces them instead is stated per entry: `inputs/gen.py` asserts reachability by simulation before writing each file and `model.py::selfcheck` re-asserts both reachability properties at gate time, so entries 2 and 3 are MECHANICAL even though the idiom audit cannot see them; entries 0 and 1 are enforced by review of `c/kernel.c` and the four Rust rungs, and by the fact that a stack buffer or a freelist would make `controls/leak.sh` report nothing at all. The last four `forbidden` entries DO backtick a spelling and the audit does range over them: they are p27's list and they close the other direction: a Rust rung is not allowed to leak DELIBERATELY, because the finding is that safe Rust's `Drop` glue makes the C bug unwriteable, not that safe Rust cannot leak if you ask it to. WHAT THIS DECLARATION DOES NOT CLAIM, said here because the R5 rung's own comment says it and a reader of the contract should not have to find it there: Verus at the pinned version CANNOT state `this allocation is released on every path`. `Tracked<Dealloc>` is AFFINE, not linear -- a proof may drop it -- so an R5 that forgot the error path's `dig_free` verifies with `0 errors`. Measured with a control that fires; NOTES.md 6. The `identity` pin therefore certifies that R4 and R5 are the same machine code, and NOT that either is leak-free; what stands behind leak-freedom on those two rungs is Miri and the reader. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },

  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "v@.len()": "v_len",
      "isize::MAX": "9223372036854775807",
      "kspec": "digest_fold",
      " as int": "",
      "v@": "v",
      "r": "result"
    },
    "obligations": {"verus.rs": 15},
    "twin_obligations": {"verus.rs": 18},
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`. 15 shipped + 3 twins (`slb_twin_v_get_unchecked`, `slb_twin_dig_alloc`, `slb_twin_dig_free`), one per item `check.py::_is_trusted` calls trusted.",
    "axioms": {"verus.rs": 0},
    "items": {
      "verus.rs": {
        "scan":        {"external": null, "requires": [], "ensures": []},
        "digb":        {"external": null, "requires": [], "ensures": []},
        "rfold":       {"external": null, "requires": [], "ensures": []},
        "kspec":       {"external": null, "requires": [], "ensures": []},
        "slot_ok":     {"external": null, "requires": [], "ensures": []},
        "v_get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "slb_twin_v_get_unchecked": {"external": null,
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "dig_alloc":   {"external": "verifier::external_body",
                          "requires": ["valid_layout(size, align)", "size != 0"],
                          "ensures": ["pt.1@.is_range(pt.0.addr() as int, size as int)",
                                      "pt.0.addr() + size <= usize::MAX + 1",
                                      "pt.2@@ == (vstd::raw_ptr::DeallocData { addr: pt.0.addr(), size: size as nat, align: align as nat, provenance: pt.1@.provenance(), })",
                                      "pt.0@.provenance == pt.1@.provenance()"]},
        "slb_twin_dig_alloc": {"external": null,
                          "requires": ["valid_layout(size, align)", "size != 0"],
                          "ensures": ["pt.1@.is_range(pt.0.addr() as int, size as int)",
                                      "pt.0.addr() + size <= usize::MAX + 1",
                                      "pt.2@@ == (vstd::raw_ptr::DeallocData { addr: pt.0.addr(), size: size as nat, align: align as nat, provenance: pt.1@.provenance(), })",
                                      "pt.0@.provenance == pt.1@.provenance()"]},
        "dig_free":    {"external": "verifier::external_body",
                          "requires": ["dealloc@.addr() == p.addr()",
                                       "dealloc@.size() == size",
                                       "dealloc@.align() == align",
                                       "dealloc@.provenance() == pt@.provenance()",
                                       "pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int)",
                                       "p@.provenance == dealloc@.provenance()"],
                          "ensures": []},
        "slb_twin_dig_free": {"external": null,
                          "requires": ["dealloc@.addr() == p.addr()",
                                       "dealloc@.size() == size",
                                       "dealloc@.align() == align",
                                       "dealloc@.provenance() == pt@.provenance()",
                                       "pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int)",
                                       "p@.provenance == dealloc@.provenance()"],
                          "ensures": []},
        "load_input":  {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "emit":        {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "dig_at":      {"external": null,
                          "requires": ["p.addr() == base", "base + i <= usize::MAX"],
                          "ensures": ["q == ptr_mut_from_data::<u8>( PtrData { addr: (base + i) as usize, provenance: p@.provenance, metadata: () }, )"]},
        "dig_write":   {"external": null,
                          "requires": ["old(pt).ptr() == q"],
                          "ensures": ["final(pt).ptr() == q", "final(pt).is_init()",
                                      "final(pt).value() == b"]},
        "dig_read":    {"external": null,
                          "requires": ["pt.ptr() == q", "pt.is_init()"],
                          "ensures": ["b == pt.value()"]},
        "kernel":      {"external": null,
                          "requires": ["off + len <= v@.len()", "1 <= len <= isize::MAX"],
                          "ensures": ["r == kspec(v@, off as int, len as int)"]},
        "main":        {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
                "c/main.c"],
    "aliases": {"c": {"n_body": "vals.len()",
                      "inp.n_iters": "n_iters",
                      "vals": "vals.as_slice()",
                      "P42_MAXWIN": "MAXWIN"}},
    "canonical": [
      "n_vals = vals . len ( ) ;",
      "vs = vals . as_slice ( ) ;",
      "acc = 0 ;",
      "if win_len_w > 0 && win_len_w <= MAXWIN && win_len_w <= n_vals",
      "{",
      "win_len = win_len_w ;",
      "nwin = n_vals - win_len + 1 ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "off = acc * nwin >> 64 ;",
      "r = kernel ( vs , off , win_len ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },

  "collapse": {
    "probe_inputs": ["small.bin", "large.bin"],
    "probe_iters": [100, 200],
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100. A difference of two runs of the same binary, so the one-shot loader terms that make whole-program Ir unquotable cancel. They do NOT cancel EXACTLY -- patterns/p01-array-sum/spec.md's copy of this note has the two surviving terms and their measured sizes, and nothing about p42 changes them. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call, and the two probe inputs have different work per call (97 vs 4096 window elements) so it can also assert d(Ir)/d(work) >= alpha. p42's work_per_call is the window elements the kernel actually SCANS, averaged over the calls the input makes -- the error path allocates and returns without scanning, so an all-error input reports zero rather than being given a floor it cannot meet. On both probe inputs every call succeeds, so the floor there is the ordinary one."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost, on the second kernel in this project that ALLOCATES AND FREES (p27 is the first) and the first that keeps a permission MAP over an input-sized block, split one byte at a time out of a `PointsToRaw` and rejoined one byte at a time on the way back. The pin has a measured price here and it is TWO EDITS, both in unsafe.rs, both found by the pin dropping. (1) `dig_write` writes `*q = b` and NOT `core::ptr::write(q, b)`: the two are the same operation for a `u8`, but `core::ptr::write` is `#[inline]` and at -O0 survives as a CALL -- `lea RIP,%rdx; movzbl %al,%esi; call core::ptr::write` -- while vstd's `ptr_mut_write`, which R5 uses and which is `#[inline(always)]` over a precompiled already-optimised vstd, becomes a bare `mov %cl,(%rax)`. Two instructions, and O0 identity reads `differ`. This is p27's finding (p27/spec.md's identity why, clause 2) and TASK_104 reproduced it by writing it BACKWARDS first. (2) `q` is bound BEFORE `run` is updated and `b` before the store, because verus.rs must bind them in that order -- the permission split that licenses the store happens between them. Folding `dig_at` into the `dig_write` argument list is the same program and NOT the same object code: LLVM strength-reduces the write loop differently, R5 keeping a byte cursor in `%r8` where R4 kept an index, and O3 identity reads `differ` on two instructions. NOTES.md 8 has both disassembly diffs. At O0 the crate names differ in length so the call displacements differ, which is link layout and not codegen, hence `norel` there and `exact` at O3. ⚠ WHAT THIS PIN DOES NOT CERTIFY, and it matters more here than on any earlier row: it says R4 and R5 are the same machine code, NOT that either is leak-free. Verus cannot state leak-freedom at the pinned version (idiom.why, and verus.rs's module comment)."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3, and since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item regardless -- check.py DERIVES that from verus.rs rather than reading this flag. On p42 there are two sharper reasons. First, `dig_alloc`'s and `dig_free`'s trusted contracts are about an ALLOCATION, and a trusted `ensures` need not be complete with respect to what the body does; Miri is what checks that the block R4 writes into is the block it allocated and the block it frees. Second, and specific to this row: Verus does NOT prove that `dig_free` is reached on every path, so the only mechanical check that R4 does not leak is Miri's own leak report at process exit. That makes Miri load-bearing for the pattern's own subject on the Rust side, not merely a backstop.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). p42's `large.bin` is 1 000 000 u64s and 1 500 calls of 4 096 elements each, so that row may exceed check.py's MIRI_TIMEOUT under interpretation; a timeout is recorded as a BLOCKED row for that input, never as a pattern failure, and the verdict then reads PASS-WITH-BLOCKED-ROWS. ⚠ AND READ THE MIRI ROW NARROWLY: `harness/check.py` passes no `MIRIFLAGS` and no `-Zmiri-seed`, and `.memory/00-environment.md` records that Miri's alignment check is SEED-DEPENDENT, so a green row is `no UB at whatever seed ran`. NOTES.md 10 records the seeds TASK_104 swept by hand."
  }
}
```

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p42's payload is:

```
word 0     u64  win_len    # the window length passed to the kernel as `len`
word 1..   u64  values     # the array `v`; v_len = (payload_len/8) - 1
```

Each value is a **record header word**. Its low byte is the record TAG and must
be `0xA7` for the window to be well formed; the other 56 bits are payload and
are what the digest reads. Nothing is a compile-time constant: `n_iters`,
`win_len` and `v_len` all come from the file.

⚠ **Every word of a measured input must carry the tag, not just word 0.** `off`
is data-derived and ranges over the whole array, so a single malformed word
anywhere would make `small.bin` leak. `inputs/gen.py::_check_all_tagged`
asserts it.

## Driver loop

Identical in all five region-carrying rungs, between the `SLB-DRIVER-BEGIN` /
`SLB-DRIVER-END` markers. `harness/check.py` diffs the copies against the
`canonical` token sequence above.

```
n_vals  := vals.len()
acc     := 0
if win_len_w > 0 and win_len_w <= MAXWIN and win_len_w <= n_vals:
    win_len := win_len_w as usize
    nwin    := (n_vals - win_len + 1) as u64
    it      := 0
    while it < n_iters:
        off := ((acc as u128 * nwin as u128) >> 64) as usize
        r   := kernel(vals, off, win_len)
        acc := acc *64 31 +64 r
        it  := it + 1
emit(acc)
```

### Why this does not evaporate

`off` is derived from `acc`, and `acc` from the previous call's result, so call
*i+1* cannot begin until call *i* has returned. p01's argument, unchanged, and
the same multiply-shift barrier for the same measurement-validity reason.

### The three-conjunct guard

`win_len_w > 0` is what gives the kernel `1 <= len`, without which the
allocation size could be zero and `std::alloc::alloc` would be undefined.
`win_len_w <= MAXWIN` is the ceiling described under "Contract" above.
`win_len_w <= n_vals` is p01's window bound. All three are outside the measured
loop; the loop itself is unchanged from p01's.

### Degenerate shapes

When the guard fails the loop is skipped entirely (rather than being entered and
broken out of, which would put a branch in the measured loop) and the driver
prints `0`. `n_iters == 0` is handled by the `while` itself. `payload_len`
declaring more bytes than the file carries is caught earlier, in `slb_load` /
`driver::load`, which exits `5`.

`inputs/` carries one adversarial input per way of failing the guard —
`-win0`, `-winbig`, `-wincap`, `-headonly`, `-empty`, `-shortlen` — plus the
three that reach the kernel's own error path: `-notag`, `-mixed`, `-win1`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |

⚠ The C kernel does **not** exit 6 on a failed digest `malloc`: it jumps into
the cleanup chain and returns 0 for that call, because a kernel that aborts
would make the allocation-failure path untestable and because `free(NULL)` is
defined. The Rust rungs abort (`Vec`'s allocation error hook; `dig_alloc`'s
explicit `std::process::abort()`), which is the same divergence every pattern
has between C's `malloc` and Rust's allocator and is not exercised by any
committed input.
