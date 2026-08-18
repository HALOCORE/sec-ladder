# TASK_018_REVIEW_REPORT — the cross-language clause does not re-admit p17, and does not admit the four cells it was written for; the pin is not decidable on the one pattern the mechanism was built for

**(a) Does the cross-language clause hold?** It holds in the direction it was
attacked — `tuned_suffix.rs` stays out, verified: four shipped p17 rungs bind
`let end: i64 = content_len;`, so the clause's antecedent is false for it — but
it **fails in the other direction**: it does not admit p02's four Rust rungs
either, because Rust can spell `len > src_len - (src_off + 2)` too, and I built
the proof (**byte-identical**, `md5_fn e207ec6c8697d2449b1761eeb58abff1`). The
"EIGHT SHIPPED CELLS" that justify the clause are miscounted: literally it is
**10 or 4, never 8**.

**(b) Keep the idiom key or delete it?** **Keep it** — but on the ground
`harness/check.py:579-592` already gives (required · visible · hashed), not on
decidability. Decidability is demonstrated only for p16's two variants and is
**refuted on p02**: the token pin cannot separate p02's shipped R3 from p02's
own `forbidden` additive spelling, which builds and measures **3.00 Ir/call
cheaper** (30% of p02's published +10). Nobody has ever run the grep the
standard says settles it; I ran it and it fails on shipped cells.

---

## Blocker

### B1 — the cross-language clause does not do the job it was added for, and the measurement that justifies it is miscounted. Six hashed blocks and `.memory/01-ladder.md` state it as measured fact

The clause, byte-identical in all six `why` strings (`patterns/p01-array-sum/spec.md:99`,
`p02:225`, `p05:333`, `p08:322`, `p16:295`, `p17:409`; sha256 of the paragraph
`2bdbe660ccac`, 2790 chars, verified identical 6/6), and restated at
`.memory/01-ladder.md:30-38`:

> Where a rung's **LANGUAGE cannot express** the quoted spelling, that rung
> spells the same operands the way its language forces and nothing else varies.
> That clause was MEASURED, not granted: without it a literal reading puts
> **EIGHT SHIPPED CELLS** out of their own contract — p02's four Rust rungs …
> and p08's four Rust rungs …

Three things are wrong with it, and the third is the blocker.

**(i) p08's four rungs were never pinned.** The standard's own trigger is
backticks — "where a `required` entry quotes an expression **in backticks** it
pins THAT SPELLING". `patterns/p08-overlap-move/spec.md` `required[3]` is
`dr = d + r, not a fixed d` with **no backticks anywhere**. p08's one backticked
entry, `required[2]`'s `m < 2 || d == 0 || d + nrep > m`, is spelled **literally
by all six rungs** (measured, comments stripped). So the half of the "eight" the
clause legitimately rescues was not at risk. (And if the trigger is widened to
un-backticked expressions, p08's *C* rungs fail too — `size_t dr = d + r;` — so
the number would be 6, not 4.)

**(ii) six cells nobody counted.** `patterns/p17-http-range/spec.md:401`
`required[2]` backticks `2 + 2*nsuf > len`. **All six p17 rungs** write
`2 + 2 * nsuf > len` (`safe_tuned.rs:34`, `safe_naive.rs`, `unsafe.rs:44`,
`verus.rs`, `c/kernel.c:66`, `c/kernel_hardened.c`). Under a standard that puts
a rung out "even when it is semantically identical and even when it compiles to
the same bytes", six shipped cells are out of contract **on two space
characters**, and no cross-language clause reaches them (C spells it the same
way Rust does). The standard supplies no token-normalisation rule, so "literal"
is undefined at exactly the granularity that decides this.

Counting the backticked expressions against the shipped rungs, the literal
misses are **10** (p02 ×4 + p17 ×6) under character-literal matching, or **4**
(p02 ×4) under any whitespace-normalising reading. Never 8.

**(iii) the clause does not rescue p02's four — by the engineer's own test.**
The engineer's discriminator is *demonstrated capability*: "It does not re-admit
p17's variant, because Rust **can** write `let end: i64 = content_len` and four
shipped p17 rungs do." Applied to p02 it cuts the other way. I built
`.temp/review018/src/r3_srclen.rs` = shipped `safe_tuned.rs` plus two lines:

```rust
let src_len: usize = src.len();
let dst_cap: usize = dst.len();
if len > dst_cap || len > src_len - (src_off + 2) {
```

which is `required[0]`'s R1h token string **verbatim**. Built with `build.py`'s
exact `-O3 isolated` flags:

| | `n_fn` | `fn_bytes` | `md5_fn` |
|---|---:|---:|---|
| `patterns/p02-buffer-copy/safe_tuned.rs` (shipped) | 95 | 333 | `e207ec6c8697d2449b1761eeb58abff1` |
| `r3_srclen.rs` (literal tokens) | 95 | 333 | `e207ec6c8697d2449b1761eeb58abff1` |

Marginal `Ir`/call identical to the hundredth on both bands (239.00 / 10210.84).
So Rust **can** express the quoted spelling, at zero cost, and the antecedent
"the rung's LANGUAGE cannot express" is **false for p02**. The clause therefore
leaves p02's four Rust rungs out of contract — the four cells it exists to keep
in — while the block asserts the opposite as a measurement, in six hashed
contract blocks, in `results/tables/*.md` (which print the whole `why`), and in
`.memory/01-ladder.md:30-38`.

The distinction that *would* work is not the one written: `src_len` is a
**parameter of the C signature that the Rust signature does not carry**, whereas
`end` is a local the author chose. "The way its language forces" does not
capture that, because Rust forces neither.

**Failure scenario.** The next agent to touch p02 applies the standard as
written — it is now house convention in all six blocks and printed above every
table — finds `required[0]`'s token absent from all four Rust rungs, and either
(a) declares p02's `+10` out of contract and retracts the third of the project's
five "R3 is free" pattern-results, or (b) edits `required[0]` to say `src.len()`,
which moves `contract_sha256` and silently narrows the entry so that the C rungs
are the ones out. Either way the repair for TASK_017_REVIEW B1 — *one standard,
applied to all six* — is not what shipped: it is one standard that four shipped
cells fail and six more fail on whitespace.

---

## Major

### M1 — on p02 the token pin cannot distinguish the shipped R3 from the spelling p02's own `forbidden` list rejects; the difference is 3.00 Ir/call

`patterns/p02-buffer-copy/spec.md` `forbidden[0]` is the additive check
`src_off + 2 + len > src_len`. No Rust rung can spell `src_len` either, so under
the token reading the forbidden string matches **nothing in Rust** — while the
required string also matches nothing in Rust. The pin is blind to the one
distinction p02 exists to make, and the block's paragraph scopes the clause to
`required` entries only, so `forbidden` gets no cross-language treatment at all.

Measured, `.temp/review018/src/r3_additive.rs` (shipped R3 with only the guard
made additive), `-O3 isolated`, marginal `Ir`/call, my own probe:

| cell | small | large | − R4 ship |
|---|---:|---:|---:|
| R4 `unsafe.rs` | 229.00 | 10200.84 | 0 |
| **R3 shipped** | **239.00** | **10210.84** | **+10.00** |
| R3, literal `src_len` tokens | 239.00 | 10210.84 | +10.00 |
| R3, **forbidden** additive guard | 236.00 | 10207.84 | **+7.00** |

`n_fn` 95 → 87, `md5_fn f8288927…`. So the forbidden spelling is **3.00
Ir/call cheaper, 30% of p02's published safety tax**, and the only thing that
excludes it is the prose adjective "subtraction-first" — i.e. the *semantic*
reading the standard replaced because "a contract a grep can settle beats a
contract only an argument can settle". On the pattern whose retraction created
this whole mechanism, the grep settles nothing and the argument is doing all the
work.

**Failure scenario.** An agent asked (correctly, per finding 3's corollary) to
write a second in-contract R3 for p02 writes the additive guard, greps
`forbidden` for its literal text, finds no match in any Rust rung including the
shipped one, publishes `+7` as p02's in-contract floor — and p02's finding, that
the additive form is the overflow the pattern exists to reject, is the casualty.

### M2 — p16's §2, the section a reader of the performance result reads, still states the claim §10a of the same file calls FALSE

`patterns/p16-tlv-walk/NOTES.md:188-189`:

> **The shipped R3 is not known to be the cheapest admissible spelling — and
> after TASK_017 it is the only admissible spelling anybody has measured.**

and `:206-208`:

> nobody has searched p16's in-contract spelling space. "The shipped R3 is the
> cheapest admissible spelling" is **unestablished**, not established

`:1129-1130` of the same file: *"is **FALSE**, not unestablished"*, with three
measured alternates. Lines 175-216 contain **no** `TASK_018` reference; the six
hits in the file are at 32, 984, 1009, 1054, 1058, 1065. §0's ⚠ (line 31) is
correct and 155 lines away in a different section; §10 (row-3 table) got a
`> Read §10a with this section` pointer in p17 (`p17…/NOTES.md:1273-1275`) and
p16's §2 got nothing.

This is the file's own named defect — `NOTES.md:22`, *"when a headline and a
decomposition disagree, the decomposition is the one that was measured"* — and
the fourth consecutive review to find it. **Failure scenario:** the next agent
greps p16 for "cheapest admissible", finds §2's sentence 900 lines above §10a,
and re-publishes "zero measured admissible alternates" — which is precisely the
sentence TASK_018's own commit message says it refuted.

### M3 — the sentence TASK_018 corrected in `check.py` survives verbatim in a **hashed contract block**

`patterns/p01-array-sum/spec.md:178`, inside `collapse.note`, i.e. inside
`contract_sha256`:

> A difference of two runs of the same binary in the same environment, so the
> loader/env terms that make whole-program `Ir` unquotable **cancel exactly**.

Same claim at `patterns/p01-array-sum/NOTES.md:110-111` and
`patterns/p05-index-flatten/NOTES.md:237-238`. `harness/check.py:869-873` now
says the opposite, from p08's measurement, and TASK_018 rehashed all six
contract blocks anyway, so fixing it cost nothing extra. The `spec.md` copy is
the authoritative one and it is the one that is wrong.

I reproduced the effect independently rather than inheriting it: same binary
(`.temp/build/p08/unsafe-O3-whole`), same input, only the environment block's
length varied —

```
PAD=   0 marginal=7292.22      PAD= 400 marginal=7292.22
PAD=  64 marginal=7292.12      PAD= 600 marginal=7292.10
PAD= 200 marginal=7292.16
```

**Failure scenario.** The next agent reads p01's hashed note — the copy the
project calls authoritative — concludes the marginal is exact, and quotes a
cross-session marginal to the hundredth, or hunts a phantom code change when
p08's cells move. That is exactly the session TASK_017 lost.

---

## Minor

- **m1 — `.memory/01-ladder.md:42-43`** says *"42 of 77 `Ir`/call at `large` sit
  inside the unpinned part of the spelling"*. 42 is the **two-sided spread**
  (`r3_window` −32 … `r3_hdrarray` +10); the part actually removable in contract
  is **32 of 77**. `patterns/p16-tlv-walk/NOTES.md:1135-1141` states the
  decomposition correctly and `spec.md`'s `why` quotes the right figure
  (`4*nrec - 8`); the `.memory` sentence is the one that reads as an
  attribution. Both figures reproduce (below).
- **m2 — `harness/report.py:115-118`'s replacement mechanism is stronger than
  its evidence, in the docstring that exists to stop that.** It says the two
  tasks *"both quoted `.memory/01-ladder.md`'s own permissive R3 rung list … as
  licence"*. Measured: `.temp/review014/NOTES.md` has 1 hit for `01-ladder` and
  its report cites it explicitly (`TASK_014_REVIEW_REPORT.md:36`, *"a spelling
  `.memory/01-ladder.md:11` names in the R3"*) — true. `.temp/p05r3/NOTES.md`
  (TASK_015) has **0** hits for `01-ladder` and 2 for `spec.md`; its licence was
  `.tasks/TASK_015.md:58`, *"## Part 2 — land `chunks_exact` as p05's R3"*, a
  manager-written task file. The corrected sentence is far closer to true than
  the one it replaced (the `results/tables` count of 0/0 verifies exactly), but
  the second occurrence came through a **fourth** surface — the task spec — that
  a declaration on the ladder table would not have covered either.
- **m3 — `harness/check.py:873-874` under-quotes its own interval.** It gives
  the p08 spread as `7292.14 … 7292.30`; I measured **7292.10** at PAD 600, so
  the observed range is 7292.10 … 7292.30 = **0.20**. The headline ("about 0.2,
  not exactly") is right; the quoted endpoints are not, which is the same defect
  TASK_017_REVIEW m3 raised against the previous bound.
- **m4 — `source_sha256` does not cover the input generators.** 138/138 verify
  (below), but the glob (`harness/check.py:4207-4212`) omits
  `patterns/*/inputs/gen.py` and `common/slb.py`, so a change to fixture
  generation moves no hash in any gate artefact. Adjacent to this task, not
  caused by it.

---

## What reproduces — every headline claim of the delivery, verified independently

**p17's identity, rebuilt from source by me** (`.temp/review018/bin/`,
`build.py`'s exact `-O3 isolated` flags):

```
r3_incontract.rs   n_fn=135  fn_bytes=478  md5_fn=532201c70eeb5fea622c8199d94edd99  md5_raw=12fd8faca909d0e087c517a0f1142d25
tuned_suffix.rs    n_fn=135  fn_bytes=478  md5_fn=532201c70eeb5fea622c8199d94edd99  md5_raw=12fd8faca909d0e087c517a0f1142d25
```

Identical stdout and exit status on **8/8** committed p17 inputs, against shipped
R3 and R4 as well. Marginal `Ir`/call, both bands, exact:
`R3ship − r3_incontract = 51.00`, `r3_incontract − R4ship = −19.00`,
`r3_tabonly − R3ship = −6.00`. And the `17·nsuf` law is now measured **on the
in-contract variant directly**, not transferred: 17 / 51 / 85 / 136 at
`nsuf` 1 / 3 / 5 / 8, with `inc − R4` = +1 / −21 / −41 / −73.

**p16's three respellings and the `nrec` coefficient the engineer flagged as a
3-point fit.** The 68 committed sweep blobs cannot test it — both bands are
`nrec` 2 and 4 (`inputs/gen.py:SWEEP_BANDS`), so they sweep the residue and not
`nrec`. I generated 22 fresh inputs (`nrec` 1,2,3,4,5,6,7,8,9,12,16 × `vlen`
124 (`≡0 mod 4`) and 126 (`≡2`), `.temp/review018/in16/`) and measured all five
binaries on each — 110 marginals, all six rungs printing identical checksums on
every input:

| difference | law | residual over 22 points |
|---|---|---|
| `R3ship − r3_endslice` | `2·nrec − 2` | **0** |
| `R3ship − r3_window` | `4·nrec − 8` | **0** |
| `r3_hdrarray − R3ship` | `nrec` | **0** |
| `R3ship − R4ship` | `7 + 5·nrec` (`vlen≡0 mod 4`) / `7 + 7·nrec` | **0** |

So the 3-point fits **survive an 11-point sweep at two residues** — this is not
a repeat of `nrec + 3`, and the `nrec` forms may now be quoted. The consequences
follow with them: at `nrec` 10 the in-contract span is `10 − (−32)` = **42**
against `R3−R4 = 77`, cheapest admissible `+45`; at `nrec` 4, 12 against 27,
cheapest `+19`. `md5_fn` 5/5 as recorded (`07b07f1a` 117 / `34a618f8` 117 /
`c7f697a8` 119 / `999fb677` 118 / `852405e0` 92).

**"Cheapest admissible is FALSE, not unestablished" — the engineer's refusal of
the manager's mandated sentence was right, on both patterns.** p16: two
admissible respellings are cheaper on **all 22** of my inputs as well as the
committed ones. p17: one is 51.00 cheaper on both bands. The mandated sentence
("zero measured admissible alternate spellings … unestablished for both") would
have been false in the tree that shipped.

**The invariant, from git objects rather than from the report**
(`991b1e4 → 432a7c6`): `md5_fn` **28/28** unchanged (14 identity pairs × `_a`/`_b`);
`marginal_ir_per_call` **564/564** unchanged, bit-exact, no key added or removed
(376 measured cells + 188 derived `d_ir_d_work` slopes — the word "cells" covers
both); `contract_sha256` **6/6** moved; `source_sha256` **138/138** entries match
both the blobs at `432a7c6` and the working tree at `HEAD`.

**Two gates re-run in a different session** (`.temp/review018/gate-p16.log`,
`gate-p02.log`; the produced JSONs are in `.temp/review018/gate-*-rerun.json`
and `results/gate/` was restored):

```
p16-tlv-walk    check.py: PASS   487 JSON leaves, 1 differs (an ASan diagnostic string)
p02-buffer-copy check.py: PASS   794 JSON leaves, 3 differ (ASan diagnostic strings)
contract_sha256 identical in both; complete_run true; failures []
```

Every `marginal_ir_per_call` and every `md5_fn` reproduced **exactly**, which is
a stronger reproduction than TASK_018 claimed for itself.

**The standard is genuinely one standard.** The 2790-character paragraph is
byte-identical in all six `why` strings (sha256 `2bdbe660ccac…`), and
`results/tables/*.md` carry the current text.

**Both corrected mechanism sentences are true as far as they go.**
`.temp/review014/NOTES.md` and `.temp/p05r3/NOTES.md` have **0** occurrences of
`results/tables` (report.py's correction), and the p08 environment term is real
and ~0.2 (check.py's correction, reproduced above). See m2/m3 for the residue.

---

## Clean negatives — named so nobody re-runs them

1. **"The cross-language clause re-admits `tuned_suffix.rs`."** It does not.
   `let end: i64 = content_len;` + `if start < end && start >= 0 {` appear in
   `safe_naive.rs:50-51`, `safe_tuned.rs:46-47`, `unsafe.rs:56-57`,
   `verus.rs:331-332`; the antecedent "the language cannot express" is false, so
   the clause never fires. The engineer's defence is exactly right, and it is
   what makes B1 unavoidable — the same test applied to p02 breaks the clause.
2. **"The p16 respellings are not semantically equivalent."** All five binaries
   print identical checksums on all 22 generated inputs (nrec 1–16, two
   residues) on top of the committed 73/73. `r3_endslice`'s earlier `&buf[..end]`
   bound check is licensed by the R3 rung definition and is unobservable under
   the kernel's `requires`.
3. **"The `nrec` coefficient is another `nrec + 3`."** Refuted — 11 `nrec`
   values × 2 residues, zero residual (above).
4. **"p16's `42 of 77` is inflated."** The number reproduces; only the sentence
   in `.memory` reads as an attribution (m1).
5. **"The p08 environment drift contaminates p16's marginals."** It does not: I
   re-measured shipped `small`/`large` in a fresh session and got 3051.30 /
   3024.30 / 23889.30 / 23812.30 — the committed figures to the hundredth. The
   fractional part of a p16 marginal is an input-dependent `println!` digit-count
   term that cancels in every difference; every difference I measured is an exact
   integer.
6. **"TASK_018 moved a measured column."** It did not — 28/28, 564/564 bit-exact
   from git, and two gates re-run agree cell-for-cell.
7. **"The `why` paragraph drifted between patterns."** It did not: identical
   sha256 in 6/6.
8. **"`report.py` prints stale idiom text."** It does not; the six tables carry
   the current `why` byte-for-byte.
9. **"p16's `required[1]`/`[2]`/`[3]` or p17's `required[0]`/`[1]` are false of a
   shipped rung."** Checked by grep against the sources: they hold. The only
   literal misses anywhere are p02's four and p17's `2 + 2*nsuf > len` (B1).

---

## Answering the question the task actually turned on

The pin buys **decidability only where the tokens exist in every rung**. That is
p16 (all six rungs carry `end - p >= 3`) and p17's `required[1]` (all four Rust
rungs carry the conjunctive guard). It buys nothing on p02, where no Rust rung
can carry the token and the two spellings that matter — the shipped one and the
forbidden one — are equally unmatched. So the honest form of the TASK_018
synthesis is narrower than the one that landed:

> A token pin is decidable **for the rungs whose language can spell the token**.
> Where the entry names an operand the rung's signature does not carry, the
> entry decides nothing and the pattern is back on its prose.

Deleting the key is still the wrong move: `required` is what makes `R3 − R4` a
matched pair at all, `forbidden` is the only thing that stopped p05's retraction
recurring, and finding 14 makes the unpinned spread unbounded below on both
sides. Keeping it costs one green stage that already describes itself correctly
(`harness/check.py:552-600`, "Presence only — no stage here checks that a rung
honours it"). What should go is the sentence that a grep settles it, or — the
cheaper repair — the clause should be restated in **signature** terms ("where a
`required` entry names a parameter of the C signature that the Rust signature
does not carry, the Rust rung denotes the same value by the expression its
signature gives") and compared **after tokenisation**, at which point the grep
really would settle it, would pass on the shipped tree, and would have caught
TASK_017's p17 sentence on the day it was written.

---

## Not done

- I did not re-run p01, p05, p08 or p17's gates (p16 and p02 only). The committed
  records self-certify via `source_sha256` 138/138 against this tree, and p08's
  marginals would not have reproduced by construction (M3).
- I did not sweep p17's `nsuf` on shipped inputs — p17 still ships no sweep, and
  that debt is unchanged by TASK_018.
- I landed no cell swap and edited nothing under `patterns/`, `harness/`,
  `.memory/` or `pilot/`. All probes are under `.temp/review018/`;
  `results/gate/` was restored from backup and `git status` is clean.
- I did not attempt to decide whether p02's four Rust rungs should be brought in
  by rewording `required[0]` or by rewording the clause. B1 says the tree cannot
  hold both sentences; choosing is a design act and belongs to a task.
