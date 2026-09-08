# ph03-uudecode-bound — the kernel contract

**`php_uudecode`, PHP 5.0.0, `ext/standard/uuencode.c:126-171`. Corpus row
CRASH-115 (merged with V5C-116). Tier `verbatim`.**

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## What the row is about

`:131` sizes the output from the *whole* input:

```c
p = *dest = emalloc(ceil(src_len * 0.75) + 1);
```

`:133` computes the true end of the input:

```c
e = src + src_len;
```

and **the only thing that ever reads `e` is the outer loop at `:135`.** The
inner loop's bound is a different quantity, computed at `:141` from a byte
inside the data:

```c
ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));
```

`len` came from `PHP_UU_DEC(*s++)` one line earlier. A line whose length byte
claims 45 with fewer than 60 characters behind it makes `ee > e`, and `:143-148`
then reads `*s .. *(s+3)` past the source **and** writes `*p++` past the
allocation, three bytes per iteration.

⚠⚠ **Both limbs are real, and which one a detector reports is decided by the
source buffer rather than by the defect.** `inputs/adversarial-read.bin` and
`inputs/adversarial-write.bin` differ by 60 bytes of slack after the window and
in nothing else:

| input | slack after the window | ASan reports |
|---|--:|---|
| `adversarial-read.bin` | 0 | `heap-buffer-overflow READ of size 1` at `uuencode.c:144` |
| `adversarial-write.bin` | 60 | `heap-buffer-overflow WRITE of size 1` at `uuencode.c:146` |

That is why `index.csv` can carry `cwe = CWE-125` (read) while its own
`root_cause_id` says *"writes past emalloc"* and both be right. PHP always has
slack — a zval string is NUL-terminated and `emalloc` rounds to 8 — which is why
the corpus recorded the write. **The row records both; it does not pick one.**

## Kernel signature

| Rung | Signature |
|---|---|
| R1 / R1h C | `uint64_t kernel(const uint8_t *buf, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

⚠ **The C kernel is NOT given `buf_len`, and that is not an omission.** PHP's own
`php_uudecode(char *src, int src_len, char **dest)` does not take one either.
The bound this row is about is *inside* the function — `e`, a local — so handing
the kernel an extra length would be modelling p16's defect (*the size was in the
signature and the code did not look*) instead of this one (*the size was in a
local and the inner loop used a different one*).

## Semantics

```
kernel(buf, off, len):
    src = buf[off .. off+len);   src_len = len
    (dest, total_len, ok) = php_uudecode(src, src_len)
    acc = 0
    if not ok:  acc = 0xFFFFFFFF                       # (u64)(unsigned int)(-1)
    else:       acc = fold31(dest[0 .. total_len)) * 31 + total_len
    return acc XOR php_shim_tally()
```

`fold31` is Horner with a multiplier of 31 over `u64` wrapping arithmetic.
Folding `total_len` bytes rather than the bytes actually emitted is what PHP
does: `:202 RETURN_STRINGL(dst, dst_len, 0)` makes a zval string of exactly
`dst_len` bytes over that buffer.

⚠⚠ **The five rungs do not implement the same fix, and that is the row's
headline.**

| rung | checks it carries |
|---|---|
| **R1** `c/kernel.c` | none — PHP 5.0.0 verbatim |
| **R1h** `c/kernel_hardened.c` | `f95c1df58349` (2004): `len > src_len`, `ee > e`, `err:` |
| **R2–R5** | the above **plus** `1e2818b14376` (2014): `s + 4 > e` inside the loop |

The 2004 fix is *incomplete*: `ee > e` bounds where the inner loop **tests**
while the body reads `*(s+3)`, so it still overshoots by up to three bytes.
Measured over 12 600 single-line documents (`.temp/php13/02-reach.log` Q3):
with the 2004 fix applied, **0 write past `emalloc` and 144 still read past the
source**. A safe-Rust rung with only the 2004 pair would *panic* on those, and a
rung that panics is not a translation of the C. So R2–R5 carry the 2014 check as
well, `verus.rs` cannot verify without it (`controls/negatives.py --emit
no2014`), and `NOTES.md` §5 has both runs.

On every one of the seven inputs this row ships a 2004 check fires first — so
R1h and R2–R5 agree everywhere and only R1 diverges. `model.py::selfcheck`
asserts that per input rather than leaving it to the corpus, because an
input in the 2014-only class would make `harness/check.py` stage `7h` hard-fail
on the hardened arm.

## The floating point is part of the mechanism

`(int) floor(len * 1.33)` stays floating point in **R1 and R1h**. `1.33` is not
representable in binary64, and an extraction that "tidies" it to integer
arithmetic changes which `len` values trigger.

Two things had to be measured rather than asserted:

1. **It is reproducible across all eight C build cells.** gcc and clang, `-O0`
   and `-O3`, isolated and whole: byte-identical checksums on `small` and
   `large` (`.temp/php13/05-crun.log`), and the `floor` table itself hashes the
   same everywhere (`.temp/php13/01b-floor-runtime.log`).
2. ⚠ **`harness/build.py` links no `-lm`, and it is frozen.** A verbatim
   `floor`/`ceil` call **fails to link in 6 of the 8 C cells** — `gcc -O0` ×2,
   `clang -O0` ×2 (undefined `floor`) and `clang -O3` ×2 (undefined `ceil`).
   Only `gcc -O3` folds both. The C rungs therefore define `php_uu_floor` /
   `php_uu_ceil` and substitute them by macro; they take and return `double`, so
   the binary64 arithmetic is untouched. Differential against libm with a
   must-fire control: **0 disagreements** over `len` 0..63 and `n` 0..10⁶,
   control **38** (`.temp/php13/02-reach.log` Q1).

The Rust rungs use `(ln * 133) / 100`. **Verus has no `f64` arithmetic at all**,
so the float cannot cross to R5; the substitution is licensed by the same
exhaustive equivalence, and `model.py::selfcheck` re-derives it *from the float*
on every gate run.

## `uuencode.c:158` is dead, and is lifted anyway

```c
if ((len = total_len > (p - *dest))) {
```

`>` binds tighter than `=`, so `len` receives 0 or 1 and `:160`/`:162` can never
run. **Measured: the whole block is dead** — over 12 600 `(src_len, len)`
single-line documents the condition was true **zero** times
(`.temp/php13/02-reach.log` Q2), and `model.py::selfcheck` re-derives it per
window. It is lifted as written; "fixing" it to
`len = total_len - (p - *dest)` would build a different program, and the
`forbidden` list says so.

## The allocator

`emalloc(ceil(src_len * 0.75) + 1)` at `:131` is a real allocation and this row
makes one per kernel call, through `common-php/emalloc_shim.h`:
`php_shim_reset()` at the top (`PROTOCOL_PHP.md` §B1.3), `php_shim_emalloc`,
`php_shim_efree`, and `php_shim_tally()` xored into the returned `u64` (§B1.2).

✅ **`emalloc_dependent: false` is CONFIRMED, not assumed.** `cap` is at most
3069 bytes for the largest window this row ships, so truncation T1 (32-bit
`real_size`), T2 (31-bit recorded size) and T3 (`_ecalloc`, never called) all sit
many orders of magnitude below their moduli and none of them fires. What the
shim contributes here is faithful *sizing* and the size-class cache's per-call
state — not a truncation.

⚠ **The Rust rungs do not link the shim.** They reproduce `php_shim_tally()`
arithmetically from the same `cap`. That makes the *allocation size* a pinned,
cross-rung quantity in the checksum — a rung that sized its destination
differently could not agree by accident — and it is **not** evidence that any
Rust rung ran PHP's allocator. `NOTES.md` §7.

## Contract

```
requires:  off + len <= buf_len
ensures:   result == uu_fold(buf, off, len)
```

`harness/check.py` parses the block below, drives `model.py` against **every**
input file — `adversarial` included — and evaluates `requires` at every call the
benchmark actually makes and `ensures` against every value it actually returns.

The `requires` is structural: it is about the shape of the buffer the driver
built, not about its contents, so it holds on every input including the
adversarial ones. **Every value the length byte can take is an argument of the
problem, not an assumption.**

⚠ **The `ensures` is the VALUE, not the safety property.** This kernel writes,
but into a buffer it allocates and frees itself, so "nothing outside the
destination moved" is no more observable in the return value than p16's "no byte
outside the window was read" was. The memory-safety claim rests entirely on the
discharged `requires` of the three trusted accessors in `verus.rs` —
`get_unchecked`, `vget_unchecked`, `vset_unchecked`, each `i < v@.len()` — proved
at every call site for indices the attacker's own length bytes chose. The
`ensures` exists to make the proof non-vacuous, to tie the value to `model.py`,
and to force the invariants to describe the walk rather than merely bound the
indices.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. The pins exist because a green verification and
a green gate are, separately, evidence of very little; `patterns/p01-array-sum/spec.md`
has the table of which bypass each pin closes, and it applies here unchanged.

⚠⚠ **Three of that table's pins mean something DIFFERENT for an extracted
kernel, and `TASK_PHP_013` §7 asked which. The answer is in `NOTES.md` §11**:
`idiom.required` is doing double duty here as *"this is what the tarball said"*
rather than only *"this is the spelling we chose"*, and a `forbidden` entry can
name a tidy-up that would be an improvement in any other row.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == uu_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (uu_fold). `uu_fold` is model.py's SECOND, independent implementation -- a recursive walk over the line chain mirroring verus.rs's `uu_walk`/`fold_line`, which accumulates the emitted bytes and folds THE FIRST total_len OF THEM exactly as verus.rs's `fold_bytes(w.0, w.1, 0)` does -- and not the simulation that produced `result`; `selfcheck()` runs the two against each other, on the calls each input makes AND on synthetic windows model.py builds itself over the whole ln = 0..63 domain. THE SECOND HALF IS NOT OPTIONAL AND THIS SENTENCE WAS FALSE WITHOUT IT (TASK_PHP_014 M1): until TASK_PHP_015 `uu_fold` folded EVERY emitted byte, which is a different function from verus.rs's whenever a line declares an ln that is not a multiple of 3 -- 42 of the 63 length bytes -- and it agreed on the whole shipped corpus because inputs/gen.py emitted length 45 exclusively and 45 % 3 == 0. A second implementation is only as strong as the domain it is exercised over, and six .bin files are not a domain.",
  "idiom": {
    "required": [
      {
        "c": "the inner loop's bound comes from the DATA and the true end does not: `ee = s + (len == 45 ? 60 : (int) floor(len * 1.33))` at uuencode.c:141, with `e = src + src_len` computed at :133 and read only by the outer loop at :135"
      },
      {
        "c": "`(int) floor(len * 1.33)`",
        "rust": "`(ln * 133) / 100`"
      },
      {
        "c": "uuencode.c:158's tail block is lifted WITH its precedence bug -- `if ((len = total_len > (p - *dest)))`, so the assignment receives 0 or 1 and :160/:162 are dead -- in both C rungs"
      },
      "R1h is the real upstream fix f95c1df58349 and NOTHING ELSE; R2-R5 carry 1e2818b14376 as well, because the 2004 fix alone does not make a rung memory-safe. NO BACKTICKED SPELLING, deliberately: this is a statement about WHICH ALGORITHM each rung implements, and no single token decides it. The mechanical check is controls/negatives.py --emit no2014, which must NOT verify.",
      "every rung allocates its destination once per call, at the size uuencode.c:131 asks for, and folds the first total_len bytes of it -- so the allocation size is pinned across every rung by the checksum, and sizing is half of this defect. NO BACKTICKED SPELLING: C writes the emalloc call and an int-indexed loop while the Rust rungs write an index loop, a slice iterator and an unchecked loop -- three legitimate spellings of one operation, which is what R2 / R3 / R4 ARE."
    ],
    "forbidden": [
      "`len = total_len - (p - *dest)` -- the repair of uuencode.c:158's precedence bug. It would be an improvement in any other row; here it builds a different program, and the block is DEAD anyway (0 of 12 600 documents enter it).",
      "`s + 4 > e` -- the additive spelling of the 2014 check 1e2818b14376. Every rung writes the subtraction-first form instead, because the additive one can overflow the index type on a window near the address-space limit and R5 cannot discharge it.",
      "`(3 * src_len + 3) / 4` -- the obvious spelling of ceil(3n/4) at uuencode.c:131. The subtractive form is the same value on every integer and cannot overflow; safe_naive.rs's capacity() carries the argument."
    ],
    "why": "ph03 is `php_uudecode` out of PHP 5.0.0, `ext/standard/uuencode.c:126-171`, corpus row CRASH-115, tier `verbatim`. The idiom is a LOOP BOUND COMPUTED FROM THE DATA: `:133` computes the true end `e = src + src_len` and only the OUTER loop ever reads it, while the INNER loop's bound is `ee = s + (len == 45 ? 60 : (int) floor(len * 1.33))` at `:141`, derived from a length byte the attacker wrote one line earlier. Both an over-read and an over-write follow from the one wrong bound, and WHICH ONE A DETECTOR SEES IS DECIDED BY THE SOURCE BUFFER RATHER THAN BY THE DEFECT: `adversarial-read.bin` and `adversarial-write.bin` differ in 60 bytes of slack after the window and nothing else, and ASan reports a READ at uuencode.c:144 on the first and a WRITE at :146 on the second. That is why the corpus can carry `cwe = CWE-125` and a `root_cause_id` saying `writes past emalloc` and be right twice. THE FLOATING POINT IS PART OF THE MECHANISM AND STAYS IN R1/R1h: an extraction that tidies `(int) floor(len * 1.33)` to integer arithmetic changes which `len` values trigger. The Rust rungs use `(ln * 133) / 100` because Verus has no f64 at all; the two agree on the whole reachable domain (`dec` masks with `077`, so `ln` is 0..63) and `model.py::selfcheck` re-derives that from the float on every gate run. `uuencode.c:158`'s `if ((len = total_len > (p - *dest)))` keeps its precedence bug and is DEAD -- measured over 12 600 documents, not argued -- and is pinned dead. R1h IS THE REAL UPSTREAM FIX, f95c1df58349 (2004), all three hunks, and IT IS INCOMPLETE: `ee > e` bounds where the inner loop tests while the body reads `*(s+3)`, so 144 of those 12 600 documents still read past the source. R2-R5 therefore carry PHP's own 2014 fix 1e2818b14376 as well, and deleting those four lines from verus.rs makes `get_unchecked(buf, s + 1)`'s `i < v@.len()` fail -- the proof refuses the shipped fix for the reason the second commit exists. AND THE OTHER HALF OF THAT FIX IS DEAD: of hunk 1's 1953 firings over the same 12600 documents, hunk 2 would have refused all 1953, and deleting hunk 1 from verus.rs still gives 25 verified / 0 errors (controls/negatives.py --emit no2004a, a control whose declared expectation is that it STILL VERIFIES). So of a two-hunk fix one hunk is dead and the other is incomplete. ⚠ READ THE `sanitizer_hardened` BLOCK OF THIS RECORD WITH THAT IN MIND: it reads `expect: clean, fired: false` on every adversarial input, and that is NOT evidence the fix is complete -- check.py stage 7h HARD-FAILS on any R1h diagnostic, so an input demonstrating the residual is structurally unshippable under inputs/ and lives in controls/fix_incomplete.c instead (NOTES.md 5d). A machine consumer reading those four clean rows alone would draw the wrong conclusion; this sentence is in the hashed block because the gate record does not echo `provenance` at all. ⚠⚠ AND THE BENIGN CORPUS TAKES BOTH ARMS OF `:141` SINCE TASK_PHP_015: it used to declare 45 on every line, so it never once reached the floor() arm this row is named for, and `45 % 3 == 0` hid a real defect in model.py's second implementation for a whole task (TASK_PHP_014 M1). inputs/gen.py::_check_span now REFUSES to write a corpus that misses the floor() arm, the strict case declared < emitted, or the equality case declared == emitted. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither."
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "uu_fold": "uu_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 25
    },
    "twin_obligations": {
      "verus.rs": 28
    },
    "obligations_note": "25 verified / 0 errors, and 28 under `--cfg slb_twin` -- three trusted accessors, therefore three twins. The count is high for this project because the spec is a pair of mutually recursive walks plus five lemmas: `lemma_cap_bound` (cap_of cannot overflow a usize at either word width), `lemma_store_in_bounds` (the three destination stores), `lemma_nsteps_exact` (the inner loop lands on s0 + 4*nsteps(fl), which is PAST `ee` whenever fl % 4 != 0 -- the overshoot the 2004 fix does not bound), `lemma_emit_covers_declared` (the bounded 1..=63 fact that `total_len <= p`), and `lemma_fold_prefix`.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 25 shipped + 3 for slb_twin_get_unchecked, slb_twin_vget_unchecked and slb_twin_vset_unchecked.",
    "items": {
      "verus.rs": {
        "dec_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "line_len_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "cap_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "tally_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "grp": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nsteps": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_line": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "uu_walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_bytes": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "uu_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_fold_prefix": {
          "external": null,
          "requires": [
            "0 <= n <= a.len()",
            "n <= b.len()",
            "forall|i: int| 0 <= i < n ==> a[i] == b[i]"
          ],
          "ensures": [
            "fold_bytes(a, n, acc) == fold_bytes(b, n, acc)"
          ]
        },
        "lemma_cap_bound": {
          "external": null,
          "requires": [
            "0 <= n <= usize::MAX"
          ],
          "ensures": [
            "1 <= cap_of(n) <= usize::MAX - 7",
            "4 * cap_of(n) >= 3 * n + 4"
          ]
        },
        "lemma_nsteps_exact": {
          "external": null,
          "requires": [
            "0 <= fl",
            "0 <= d",
            "d % 4 == 0",
            "d >= fl",
            "d <= 4 * nsteps(fl)"
          ],
          "ensures": [
            "d == 4 * nsteps(fl)"
          ]
        },
        "lemma_store_in_bounds": {
          "external": null,
          "requires": [
            "len >= 0",
            "p >= 0",
            "s >= off",
            "4 * p <= 3 * (s - off)",
            "s + 4 <= off + len"
          ],
          "ensures": [
            "p + 2 < cap_of(len)"
          ]
        },
        "lemma_dec_range": {
          "external": null,
          "requires": [],
          "ensures": [
            "dec_of(b) <= 63"
          ]
        },
        "emit_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "emit_ok_upto": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_emit_upto_elim": {
          "external": null,
          "requires": [
            "emit_ok_upto(n)",
            "1 <= k <= n"
          ],
          "ensures": [
            "emit_ok(k)"
          ]
        },
        "lemma_emit_covers_declared": {
          "external": null,
          "requires": [
            "1 <= ln <= 63"
          ],
          "ensures": [
            "emit_ok(ln)"
          ]
        },
        "get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "vget_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_vget_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "vset_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_vset_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
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
        "dec": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == dec_of(b)"
          ]
        },
        "line_len": {
          "external": null,
          "requires": [
            "ln <= 63"
          ],
          "ensures": [
            "r == line_len_of(ln as int)"
          ]
        },
        "capacity": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == cap_of(src_len as int)",
            "1 <= r <= usize::MAX - 7"
          ]
        },
        "tally": {
          "external": null,
          "requires": [
            "cap <= usize::MAX - 7"
          ],
          "ensures": [
            "r == tally_of(cap as int)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == uu_fold(buf@, off as int, len as int)"
          ]
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    },
    "unsafe_justifications": {
      "verus.rs": {
        "vset_unchecked": "`x: u8` is a PURE VALUE and needs no precondition. The unchecked operation is `*v.get_unchecked_mut(i) = x`: its definedness depends on `i` being in bounds and on `v` being a live `Vec<u8>`, and on NOTHING about the byte being written -- every one of the 256 values of `x` is a legal `u8` store into a byte that is already initialised (`vec![0u8; cap]` initialised the whole buffer before the first call site is reached). Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. Here the indexing parameter `i` IS constrained, by `i < old(v)@.len()`, and the `ensures` names `x` in the post-state -- `final(v)@ == old(v)@.update(i as int, x)` -- so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition. That postcondition is what makes the value parameter safe to leave free, and it is why the `ensures` is the WHOLE post-state rather than `v@[i] == x`."
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
      "if stride_w >= 1 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph03's two probe shapes have different work per call (556 and 4090 window bytes) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. Note that ph03's kernel does one `emalloc` + one `efree` + one `php_shim_reset` per call on the C side and one Vec allocation per call on the Rust side, so a fixed per-call term is present in every rung and the marginal is NOT a pure decode rate; NOTES.md 8 decomposes it."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "exact",
      "why": "R4 == R5 at O3: the proof licenses the unchecked reads AND the unchecked writes at zero cost. Measured, `results-php/ph03-uudecode-bound.json`: `md5_fn 338505795ee18db952aafcdaec522df4`, 708 bytes, 200 instructions, identical for both cells. \u26a0 AT O0 THE TWO GENUINELY DIFFER AND THE LEVEL IS `differ`, NOT `norel` -- 335 vs 352 instructions, 1906 vs 2042 bytes. That is not link layout: at O0 nothing is inlined, so R5's five trusted wrappers survive as real calls where R4's `get_unchecked` sites are open-coded, and the Verus crate keeps a larger frame. p01 and p16 pin `norel` here because their O0 difference IS only relocations; ph03's is not, and the pin says so rather than being copied. \u26a0 THIS PIN WAS FIRST WRITTEN `norel` FROM A HAND BUILD AND THE GATE REFUTED IT; see NOTES.md 0."
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
    "reason": "R4 and R5 ARE byte-identical at O3, and that is not an excuse: `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph03 has THREE such items and one of them WRITES (`vset_unchecked`), which is the case p16 did not have: a trusted `ensures` need not be COMPLETE with respect to what the body does, and a write wrapper whose `ensures` named only `v@[i] == x` would let a body that also clobbered `v[i+1]` through every Verus stage. The shipped `ensures` is the whole post-state, `old(v)@.update(i, x)`, and Miri is the backstop for the class regardless.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph03's cost is 4 x (one window decoded), i.e. 4 x 4090 bytes at worst -- three orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "ext/standard/uuencode.c",
    "c_lines": [
      126,
      171
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/uuencode.c | sed -n '126,171p'",
    "extract_sha256": "9f68d3cfb639cb62a3ec7b685da1a8e4cec828085791e200c23ffa8eb12778fe",
    "tier": "verbatim",
    "divergences": [
      {
        "what": "emalloc -> php_shim_emalloc, efree -> php_shim_efree",
        "kind": "substitution",
        "where": "uuencode.c:131 (emalloc); the efree is added by fix_commit at :181",
        "why": "the allocator is SUBSTITUTED, not deleted: common-php/emalloc_shim.h is PHP 5.0.0's own _emalloc/_efree line-cited to the same tarball (PLAN_PHP.md 4.3). No semantics change; a plain malloc WOULD be a change and is what PROTOCOL_PHP.md B forbids."
      },
      {
        "what": "floor -> php_uu_floor, ceil -> php_uu_ceil (macro substitution, both C rungs)",
        "kind": "substitution",
        "where": "uuencode.c:131 (ceil), :141 (floor); the include is at :57, outside the extracted span",
        "why": "harness/build.py links no -lm and is FROZEN, so a verbatim libm call FAILS TO LINK in 6 of the 8 C cells (measured, .temp/php13/01b-floor-runtime.log). The substitutes take and return double and are called on the same double expressions, so the binary64 arithmetic is unchanged; 0 disagreements against libm over len 0..63 and n 0..10^6 with a must-fire control at 38 (.temp/php13/02-reach.log Q1). No semantics."
      },
      {
        "what": "PHPAPI",
        "kind": "deletion",
        "where": "uuencode.c:126",
        "why": "an empty macro on every non-Windows build; the function is declared `static` here because the kernel TU has no header to export it through. No semantics."
      },
      {
        "what": "the emalloc NULL arm",
        "kind": "projection",
        "where": "common-php/emalloc_shim.h, _emalloc's :189-198 projection",
        "why": "PHP prints to stderr and exit(1)s; the shim returns NULL and the caller decides, because a kernel that exits turns a measurement into a build failure. DECLARED per emalloc_shim.h's own instruction. ph03 cannot reach it: cap is at most (window + 1) bytes and the largest window this row ships is 4090."
      }
    ],
    "divergences_note": "THE KEY WAS `deletions` UNTIL TASK_PHP_015 AND THREE OF THESE FOUR ENTRIES ARE NOT DELETIONS (TASK_PHP_014, tier clause): two are substitutions and one is a projection of the shim's NULL arm. Renamed rather than explained away, because a ledger whose name describes a quarter of its contents is a ledger a builder fills in wrongly. `kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it.",
    "root_cause_ids": [
      "uudecode-decode-loop-writes-past-emalloc-on-short-line"
    ],
    "cwe": "CWE-787",
    "cwe_note": "index.csv records CWE-125 / out-of-bounds-read for CRASH-115 while its own root_cause_id says `writes past emalloc`. BOTH ARE RIGHT and the row ships both: adversarial-read.bin (no slack after the window) gives ASan a READ at uuencode.c:144, adversarial-write.bin (60 bytes of slack, otherwise byte-identical) gives a WRITE at :146. CWE-787 is recorded here because the write is the limb PHP itself sees -- a zval string is NUL-terminated and emalloc rounds to 8, so the source always has slack -- and because the write is what f95c1df58349 closes. TASK_PHP_012 m8 proposed exactly this and it is adopted with the read recorded beside it, not dropped.",
    "fix_commit": "f95c1df583490814b0501c56f59671193a57507b",
    "fix_commit_note": "Ilia Alshanetsky, 2004-08-24, `Fixed bug #29821 (Fixed possible crashes in convert_uudecode() on invalid data)`, ext/standard/uuencode.c, +17 lines, three hunks. Patch bytes kept at controls/f95c1df58349.patch, 1433 bytes, sha256 fc3ef3c50488d0047b04629fabecb2d89aaa95d5b6f9b0085e6b61703ac31a7f. AND IT IS INCOMPLETE: PHP needed 1e2818b143760a79a0887861bd6221b158355073 (Stanislav Malyshev, 2014-05-11, bug #67252) to close the remaining over-read. That patch is at controls/1e2818b14376.patch, 2063 bytes, sha256 97975e658d67aaade1c24f6f4fb6cfc567abc2516f166cd3126f920e2dab5fff, and is NOT in kernel_hardened.c -- PROTOCOL_PHP.md C: report it, do not repair it.",
    "invariant": "I1",
    "obligation": "O2",
    "echoes": [
      "p16"
    ],
    "echoes_note": "p16-tlv-walk is the closest PAT analogue -- a length-driven walk whose bound is attacker data. It is a CROSS-REFERENCE, never a filter (PLAN_PHP.md 3.1). Two differences worth carrying: p16's kernel is given `buf_len` and does not look, while php_uudecode's true end is a LOCAL it computes and then does not consult; and p16 only reads, while this row writes into an allocation whose size is derived from the same length the loop mis-bounds.",
    "uses_allocator": true,
    "uses_allocator_why": "c/kernel.c and c/kernel_hardened.c call php_shim_emalloc once and php_shim_efree once per kernel call, and php_shim_reset() at the top of every call (PROTOCOL_PHP.md B1.3). php_shim_tally() is folded into the returned u64 (B1.2). BUT THE TRUNCATIONS ARE NOT THE DEFECT: cap = ceil(src_len*0.75)+1 is at most 3069 for the largest window this row ships, so T1 (32-bit real_size), T2 (31-bit recorded size) and T3 (_ecalloc, not called) all sit far below their moduli and none fires. The catalogue's `emalloc_dependent: false` is CONFIRMED. What the shim contributes here is faithful SIZING and the size-class cache's per-call state, not a truncation. DECLARED, NEVER DETECTED (TASK_PHP_008 0.4) -- nothing reads this field.",
    "task": "TASK_PHP_013"
  }
}
```

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. ph03's payload is:

```
word 0     u64  stride     bytes per window; the kernel uudecodes one window
byte 8..   u8[] blob       uuencoded text; n_blob = payload_len - 8
```

A *window* is a complete uuencoded document, exactly as `php_uuencode`
(`uuencode.c:68-124`) emits one: `K` full lines of
`PHP_UU_ENC(45) + 60 characters + '\n'` (62 bytes each), then a **short final
line** of `PHP_UU_ENC(T) + 4·ceil(T/3) characters + '\n'`, then
`PHP_UU_ENC(0) + '\n'`. With `T ∈ {40, 41, 42}` — all three encode to 14 groups
— the short line is 58 bytes, so `stride = 62K + 60` and the window declares
`45K + T` bytes. `small` is K = 8 (stride 556), `large` is K = 65 (stride 4090);
the two differ mod 4, 8 and 16, which `inputs/gen.py::_check_residues` asserts.

⚠⚠ **The short final line is what makes `:141`'s `floor()` arm reachable from
the benign corpus at all**, and its absence is `TASK_PHP_014` M1's root cause:
every length byte used to be 45, `45 ≡ 0 (mod 3)` is exactly the case in which a
line emits as many bytes as it declares, and `model.py`'s second implementation
was therefore never exercised off that diagonal. `inputs/gen.py::_check_span`
now refuses to write a corpus that misses the `floor()` arm, the strict case
`declared < emitted` or the equality case `declared == emitted`.
⚠ The decoder never reaches the terminator on such a document — `uuencode.c:156`
breaks at the first `len < 45` — which is real `php_uudecode` behaviour, not an
artefact of the fixture.

Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob` and **every
length byte** come from the file, and the length byte is the datum the whole row
is about.

## Driver loop

Identical in all five rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` diffs the copies.

```
n_blob := bytes.len()
acc    := 0
if stride_w >= 1 and stride_w <= n_blob:
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

`stride_w >= 1` rather than p16's `>= 3`: `php_uudecode` is total on a one-byte
source, so there is no window size below which the kernel has nothing to do. The
guard exists to keep `n_blob / stride` from dividing by zero and to make
`adversarial-nowin.bin` skip the loop entirely rather than enter it and break
out, which would put a branch inside the measured loop.

### Why this does not evaporate

`k` is derived from `acc`, and `acc` from the previous call's result, so call
*i+1* cannot begin until call *i* has returned. LLVM can neither CSE the calls
nor hoist them, and no `black_box` or `asm volatile` is needed — which matters,
because those two are not equally strong barriers and using them would put a
C-vs-Rust asymmetry in the driver. The multiply-shift is Lemire's map onto
`[0, nwin)`; `.memory/03-measurement.md` records why it is not a modulo.

### Degenerate shapes

The guard is the whole of the driver's input validation, and
`adversarial-nowin.bin` is what attacks it: `stride = n_blob + 1`, so the loop
is skipped, zero kernel calls are made and every rung prints `0`.
`payload_len` declaring more bytes than the file carries is caught earlier, in
`slb_load` / `driver::load`, which exits `5`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success; checksum on stdout |
| 2 | wrong argument count |
| 3 | cannot open input file |
| 4 | file shorter than the 16-byte header |
| 5 | `payload_len` exceeds the bytes present |
| 6 | allocation failure (C only) |
