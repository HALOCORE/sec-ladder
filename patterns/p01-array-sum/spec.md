# p01 — array sum over a window: the kernel contract

Every rung implements exactly this. If a rung deviates, it is a different
benchmark and its numbers are not comparable.

## Kernel signature

| Rung | Signature |
|---|---|
| R1 C | `uint64_t kernel(const uint64_t *v, size_t off, size_t len)` |
| R2/R3/R4/R5 Rust | `fn kernel(v: &[u64], off: usize, len: usize) -> u64` |

The C kernel takes three arguments; the Rust kernels take four registers, because
`&[u64]` is a pointer *and* a length. That asymmetry is deliberate and is the
finding, not a rigging: the length is the thing C does not have and therefore
cannot check. R2 and R3 consume it (bounds check / slice construction); R4 and R5
receive it and never read it, so LLVM should drop it — whether it does is one of
the things the assembly comparison answers. Do not "fix" this by giving C a dead
`v_len` parameter; that would be Rust-in-C-syntax.

## Semantics

```
kernel(v, off, len) = fold over i in [off, off+len) of  acc := acc +64 v[i]
                      starting from acc = 0
```

where `+64` is wrapping addition modulo 2^64. `len == 0` yields `0`.

Wrapping, not checked, addition is deliberate. It makes the kernel *total* on
values: there is no precondition on the contents of `v`, only on the shape of the
window. Rung 5's proof obligation is therefore exactly the memory-safety
property — `off + len <= v.len()` — and nothing is smuggled in via an artificial
value bound that the input generator would then have to be trusted to respect.
(The pilot did the opposite: `requires v[i] < 1000` and `n < 1000`, which its own
measured inputs violated. See `.memory/02-bench-rules.md`.)

C's `uint64_t` addition already wraps by definition, so R1 needs no special
spelling; the Rust rungs use `u64::wrapping_add`.

**The authoritative statement of p01's idiom** — this section's wrapping-addition
rule and the "Kernel signature" section's C/Rust arity asymmetry — **is the
`idiom` key in the `slb-contract` block below**, which is hashed into
`contract_sha256`. The prose here is the same statement with the arguments; if
the two ever disagree, the block wins and the prose is the bug. Edit both or
neither (TASK_016_REVIEW m2).

## Contract

```
requires:  off + len <= v_len
ensures:   result == wrapping_sum(v, off, len)
```

`harness/check.py` parses the block below, drives `model.py` against **every**
input file — `adversarial` included — and evaluates `requires` at every call the
benchmark actually makes and `ensures` against every value it actually returns.
That is the mechanical enforcement of `.memory/02-bench-rules.md` "Proof domain
must cover the measured domain" rules 1 and 3.

`off + len` cannot itself overflow `usize` in the measured domain because the
driver derives `off` from `(acc * nwin) >> 64` in 128-bit arithmetic with
`nwin = v_len - len + 1`, so `off < nwin` and `off + len <= v_len`. R5 proves
this at the call site — see "the barrier" below for why the bound needs three
lines of nonlinear arithmetic where `acc % nwin` needed none.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. The pins exist because a green verification and
a green gate are, separately, evidence of very little:

| pin | the bypass it closes |
|---|---|
| `verus.obligations` | `#[verifier::external_body] fn main` — no call site verifies, so no precondition is discharged, and the obligation count drops 5 → 3. This is the pilot's fatal defect (`.memory/02-bench-rules.md` rule 2). |
| `verus.items[*].requires` / `.ensures` | replacing the kernel's postcondition with `ensures r == r` still gives *5 verified, 0 errors*. So does **deleting a `requires` from an `external_body` wrapper**, which silently deletes every caller's obligation and moves no count at all — the project's most dangerous known vacuity mode (`.memory/04-verus.md`). Only a textual diff against a pin catches it. |
| the item set itself | a *new* `external_body` item can otherwise be added without the TCB tally noticing. |
| `driver.canonical` | the driver loop was previously diffed rung-against-rung, so a mutation applied to *every* rung — deleting the anti-collapse barrier — passed; and the C copy was checked by required substrings, so adding a prefetch and a memory barrier passed (`.memory/02-bench-rules.md` forbids exactly that asymmetry). |
| `collapse.probe_inputs` | a kernel that got constant-folded away still has a backward branch somewhere in the symbol. **The floor itself is no longer pinned here**: `check.py` derives it as `ALPHA_IR_PER_WORK * model.work_per_call` and, across the two probe shapes, asserts `d(Ir)/d(work) >= ALPHA`. ALPHA is a harness constant. The old declared floor of 400 was 0.80 Ir/element against 1.83 achieved, and whoever broke the loop could have lowered it in the same commit (TASK_003_REVIEW). |
| `verus.translate` | `contract.requires` (Python) and `verus.items[*].requires` (Verus) used to be two independent transcriptions of one predicate with nothing checking they corresponded, so the proof's precondition could be weakened while the gate went on evaluating the strong one over every input. The Python side is now *generated* from the Verus clause text through this table. |
| `driver.regions` | deleting the two `SLB-DRIVER` marker comments used to make a rung vanish from the driver diff silently — the gate only required that ≥2 regions were found anywhere. |
| `identity` | recorded as a **result**, not a gate condition. A pattern whose proof legitimately costs an instruction is a finding; only a *drop below the pinned level* is a failure. |

```slb-contract
{
  "kernel": "kernel(v: &[u64], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": ["off + len <= v_len"],
  "ensures": ["result == wrapping_sum(v, off, len)"],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (off/len/v_len/v/result) plus the helpers it supplies (wrapping_sum).",

  "idiom": {
    "required": [
      "wrapping, not checked, addition in every rung -- the kernel is total on VALUES and R5's only obligation is off + len <= v.len()",
      "the C kernel takes (v, off, len) and has no length to check; the Rust kernels take &[u64], i.e. a pointer AND a length",
      "R2 indexes v[i] element by element; R3 reslices the window once and folds it with an iterator"
    ],
    "forbidden": ["a dead v_len parameter on the C kernel"],
    "why": "wrapping addition is what keeps the proof obligation exactly the memory-safety property, with no value bound smuggled in that the input generator would then have to be trusted to respect -- the pilot did the opposite and its own measured inputs violated it. The C/Rust arity asymmetry is the finding and not a rigging: the length is the thing C does not have and therefore cannot check, so handing C a dead v_len to make the signatures match would be Rust-in-C-syntax and would delete the comparison. Both are also written out in the prose above ('Kernel signature' and 'Semantics'); TASK_016 RESTATED them here rather than moving them, so p01 states its idiom twice and THIS block is the authoritative copy (TASK_016_REVIEW m2). Whoever edits one edits the other. Note how weak this declaration deliberately is: p01 is the CALIBRATION pattern, it models no bug, and its inner fold is an associative sum with no bulk-memory idiom to lose, so beyond the three required entries no spelling of the fold is excluded and p01's numbers are a spelling's numbers. TASK_016 did not measure a spelling spread for p01; one is owed before any p01 number is quoted as what safe Rust costs. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 Ir/call flat and p02's by 3 to 4, so `R3ship - R4ship` is an UPPER BOUND on the in-contract safety tax and never the tax itself. Every pattern owes an in-contract spelling spread beside its headline; p16 and p17 have one from TASK_018 and p02 from TASK_019 (their NOTES.md 10a) and p05 from TASK_021 (its NOTES.md 14, which also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep); p01 and p08 do not."
  },

  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "v@.len()": "v_len",
      "sum_wrap": "wrapping_sum",
      " as int": "",
      "v@": "v",
      "r": "result"
    },
    "obligations": {"verus.rs": 7, "safe_naive_verus.rs": 7},
    "twin_obligations": {"verus.rs": 8},
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twin. 7 shipped + 1 for slb_twin_get_unchecked. `safe_naive_verus.rs` has no trusted item with an `ensures` and no `unsafe`, so it needs no twin and gets no twin run.",
    "items": {
      "verus.rs": {
        "sum_wrap":      {"external": null, "requires": [], "ensures": []},
        "get_unchecked": {"external": "verifier::external_body",
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "slb_twin_get_unchecked": {"external": null,
                          "requires": ["i < v@.len()"],
                          "ensures": ["r == v@[i as int]"]},
        "load_input":    {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "emit":          {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "kernel":        {"external": null,
                          "requires": ["off + len <= v@.len()"],
                          "ensures": ["r == sum_wrap(v@, off as int, len as int)"]},
        "main":          {"external": null, "requires": [], "ensures": []}
      },
      "safe_naive_verus.rs": {
        "sum_wrap":      {"external": null, "requires": [], "ensures": []},
        "load_input":    {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "emit":          {"external": "verifier::external_body",
                          "requires": [], "ensures": []},
        "kernel":        {"external": null,
                          "requires": ["off + len <= v@.len()"],
                          "ensures": ["r == sum_wrap(v@, off as int, len as int)"]},
        "main":          {"external": null, "requires": [], "ensures": []}
      }
    }
  },

  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": ["safe_naive.rs", "safe_naive_verus.rs", "safe_tuned.rs",
                "unsafe.rs", "verus.rs", "c/main.c"],
    "aliases": {"c": {"n_body": "vals.len()",
                      "inp.n_iters": "n_iters",
                      "vals": "vals.as_slice()"}},
    "canonical": [
      "n_vals = vals . len ( ) ;",
      "vs = vals . as_slice ( ) ;",
      "acc = 0 ;",
      "if win_len_w > 0 && win_len_w <= n_vals",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100. A difference of two runs of the same binary, so the one-shot loader terms that make whole-program Ir unquotable cancel. They do NOT cancel EXACTLY, and this note said they did until TASK_019: two terms survive the difference and both are measured. (1) The environment block, WITHIN ONE BUILD. The same p08 binary on the same input, with only the length of the environment varying, gives a spread of about 0.1, and three probes agree: 21 pad lengths 0..900 at TASK_020 and six at TASK_019 both give 7292.12 .. 7292.22 on p08's `small` (TASK_019 also 29037.52 .. 29037.62 on its `large`), and TASK_018_REVIEW's five points give 7292.10 .. 7292.22. It is SCATTER, not a trend -- the marginal is not monotone in the environment length. (2) THE BUILD ITSELF, which is the larger half and is not the environment at all. TASK_019 said here that `harness/check.py` step 3b's `7292.14 .. 7292.30` had neither endpoint reproduced; that is WRONG and TASK_020 retracts it -- both endpoints are TASK_017_REVIEW's five measured points, recorded at `patterns/p08-overlap-move/NOTES.md` 2b, on a DIFFERENT build of the same source, and TASK_018_REVIEW m3 flagged only the lower one while explicitly endorsing the 0.2 headline. So the union over all five probes is 7292.10 .. 7292.30, spread 0.20: ~0.1 of it is the environment and the rest is the build-to-build level shift. The mechanism of that shift is the same one measured on p02: p02's shipped R3 source built at two different paths gives 10210.82 and 10210.84 on `large` with a byte-identical kernel (`md5_fn e207ec6c8697...`, n_fn 95); per-function callgrind puts the whole 0.02 inside glibc's AVX memmove and the kernel's own self-cost at 9783.00 in BOTH, because the two binaries differ in size and the destination buffer therefore lands at a different alignment (TASK_019). So a marginal is exact WITHIN one build and one session and is quotable to the instruction only as a difference taken there; across sessions or builds, expect the last digit or two to move, and do not hunt a code change for it. Symbol-independent, so it works in `whole` mode and at O0 where the work lives in core::iter symbols. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call, and the two probe inputs have different work per call (501 vs 4096 elements) so it can also assert d(Ir)/d(work) >= alpha. The old declared floor of 400 was 0.80 Ir/element against 1.83 achieved, and an author who broke the loop could lower it in the same commit."
  },

  "identity": [
    {"a": "unsafe", "b": "verus", "O0": "norel", "O3": "exact",
     "why": "R4 == R5: the proof licenses unsafe code at zero cost. At O0 the Rust kernel still calls Iterator::next and the crate names differ in length, so the call displacements differ -- link layout, not codegen."},
    {"a": "safe_naive", "b": "safe_naive_verus", "O0": "exact", "O3": "exact",
     "why": "R2 == R2v: proving safe code buys nothing."}
  ],

  "miri": {
    "pair": ["unsafe", "verus"],
    "sources": ["unsafe.rs"],
    "required": true,
    "reason": "R4 and R5 ARE byte-identical at O3 (`identity` above pins `exact`), and that used to make Miri optional here. It no longer does: `.memory/02-bench-rules.md`, revised at TASK_010, makes Miri mandatory for any pattern with a trusted `unsafe` item, and `check.py` derives that from `verus.rs` rather than from this flag. The reason byte-identity is not an excuse: R4 inherits R5's proof, and R5's proof is only as good as its trusted `ensures`, which need not be COMPLETE with respect to the operations the trusted body performs -- a `get_unchecked` wrapper that also reads `i + 1` passes every Verus stage with its contract, twin and pins unchanged (TASK_009_REVIEW x4). Miri is the only backstop for that class when R4 carries the same read, and byte-identity propagates it rather than excusing it.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). p01's `large.bin` is 1.5 M u64s that the driver decodes one at a time, so that row may exceed check.py's MIRI_TIMEOUT under interpretation; a timeout is recorded as a BLOCKED row for that input, never as a pattern failure, and the verdict then reads PASS-WITH-BLOCKED-ROWS. The size of an input file must not decide whether the gate is green."
  }
}
```

## Payload layout

The generic file format (`.memory/02-bench-rules.md`) is `u64 n_iters`,
`u64 payload_len`, payload. p01's payload is:

```
word 0     u64  win_len    # the window length passed to the kernel as `len`
word 1..   u64  values     # the array `v`; v_len = (payload_len/8) - 1
```

Nothing is a compile-time constant: `n_iters`, `win_len` and `v_len` all come
from the file.

## Driver loop

Identical in all five rungs, between the `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END`
markers. `harness/check.py` diffs the copies.

```
n_vals  := vals.len()
acc     := 0
if win_len_w > 0 and win_len_w <= n_vals:
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

`off` is derived from `acc`, and `acc` is derived from the previous call's
result. Call *i+1* therefore cannot begin until call *i* has returned, so LLVM
can neither CSE the calls nor hoist them out of the loop, and no `black_box` or
`asm volatile` is needed — which matters, because those two are not equally
strong barriers and using them would put a C-vs-Rust asymmetry in the driver
(`.tasks/TASK_002.md`). The mechanism is the same arithmetic in both languages.

### The barrier is a multiply-shift, not a modulo

`off = (acc * nwin) >> 64` in 128-bit arithmetic — Lemire's map from a uniform
`u64` onto `[0, nwin)`. It was `acc % nwin` until TASK_005.

The swap is not a micro-optimisation, it is a measurement-validity fix. A 64-bit
`div` is ~0.1 % of `Ir`, so the *primary* metric never noticed it — but it is
20–40 cycles of latency sitting on the serial dependency chain that makes the
loop a loop, and that is a **rung-independent additive constant**. An additive
constant compresses every cross-rung wall-clock *ratio* toward 1, which is the
direction that flatters this project's own headline. `mul` is 3 cycles and
keeps the cache randomisation exactly (`off` is still uniform over `[0, nwin)`),
so the ratios get more honest and nothing else changes. Both languages compile
it to a single `mul` and a `mov` (gcc `-O3`: `mov %rdi,%rax; mul %rsi;
mov %rdx,%rax`).

It costs three lines of ghost proof in R5, where `%` cost none: `(acc * nwin)
>> 64 < nwin` is nonlinear in both steps, so Z3 needs `acc * nwin` bounded
explicitly and `vstd::bits::lemma_u128_shr_is_div` to turn the shift into the
division the argument is about. That is why the obligation count moved 5 → 7.

`harness/check.py` proves this held, per cell, by disassembling and requiring a
backward branch and a plausible body size.

### Degenerate shapes

The guard `win_len_w > 0 && win_len_w <= n_vals` is the whole of the driver's
input validation, and it is what the `adversarial-*` inputs attack. When it
fails the loop is skipped entirely (rather than being entered and broken out of,
which would put a branch in the measured loop) and the driver prints `0`.
`n_iters == 0` is handled by the `while` itself.

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
