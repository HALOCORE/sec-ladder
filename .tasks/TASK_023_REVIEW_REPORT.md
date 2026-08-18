# TASK_023_REVIEW — `r4_hdr` is in contract, and it is nowhere near the cheapest

**Is `r4_hdr` in contract? YES.** Mechanically, by the gate's own matcher, under a
licence sentence that pre-dates the measurement by two tasks, sound under Miri,
and equivalent on 95/95 committed inputs. The engineer nominated the right thing
to attack and the attack fails. What does *not* survive is everything §10a.1
built on top of it: `r4_hdr` is the **first** lever, not a cheap one, and the
interval it defines is wrong by one to two orders of magnitude and wrong in
**sign** at the bottom.

Everything below was measured in one build session on this box (2026-08-18),
`-O3 isolated` with `harness/build.py`'s exact rustc flags, marginal `Ir`/call by
`n_iters` 100→200 whole-program callgrind difference — `harness/check.py` step
3b's own probe, re-implemented independently. Raw data
`.temp/review023/marginal_all.json`, `.temp/review023/vlensweep.json`,
`.temp/review023/r3unroll.json`; scripts `.temp/review023/{gen_r4_attack,measure,leafdiff}.py`.

---

## Priority 1 — is `r4_hdr` genuinely in contract?

**Yes**, on four independent checks, none of which the engineer's write-up had run:

1. **The gate's own matcher.** `check.spelling_matches` (the function that decides
   admission and is selftested at gate stage 0, hence inside `source_sha256`),
   applied to `.temp/p16/controls/r4_hdr.rs`:

   | rung | `end - p >= 3` | `vlen > end - (p + 3)` | `p + 3 <= end` | `p + 3 + vlen <= end` |
   |---|---|---|---|---|
   | `unsafe.rs` (shipped) | True | True | False | False |
   | `r4_hdr` | **True** | **True** | False | False |

2. **Not self-certification.** p16's `spec.md` `idiom.why` has ended with
   *"Still deliberately NOT restricted: the R2/R3/R4 spelling of the value fold
   and of the header read beyond the two comparisons, and unrolling."*
   **byte-identically since `432a7c6` (TASK_018)** — two tasks before TASK_023
   measured anything. `git show 432a7c6:patterns/p16-tlv-walk/spec.md` and
   `git show HEAD:...` return the same string. The `direction test`
   (`.memory/01-ladder.md:134-139`) is not even engaged: the licence was not edited.

3. **Sound.** `end - p >= 3` plus `end <= buf.len()` gives `p + 2 < buf.len()`,
   which is exactly the obligation the two `get_unchecked` byte loads already
   carried. Miri, nightly `2026-08-14`, `n_iters` 4, run by me:

   ```
   small.bin                unsafe/r4_hdr/rv_u16/rv_u32_hdr   exit=0 UB=False  14520258090713499404
   adversarial-trunc.bin    all four                          exit=0 UB=False   5018301368121126796
   adversarial-overrun.bin  all four                          exit=0 UB=False  11362453224674129216
   adversarial-stride2.bin  all four                          exit=0 UB=False                     0
   ```

4. **Equivalent.** 95 committed inputs × 9 of my variants = 855 comparisons on
   stdout **and** exit status against the shipped R4 binary, **0 mismatches**.

**But there is one cost §10a.1 does not disclose — see `major 4`.** `r4_hdr`
cannot be a p16 *rung*, only a control, because Verus cannot verify
`read_unaligned`. `controls/gen_controls.py:69-71` says so; `NOTES.md` §10a.1 and
`spec.md`'s `why` — the copy rendered into all six published tables — do not.

---

## Priority 2 — reproduce `R4ship − r4_hdr = 4·nrec`, then break it

### The engineer's laws all reproduce, exactly

Every digest in §10a.1's and §10a's tables reproduces byte for byte in my own
session, including the control I built purely as a cross-build check (`rv_ship`
= `unsafe.rs` with only the `#[path]` rewrite):

```
unsafe(ship)   md5_fn 852405e0fa43  n_fn  92     rv_ship  852405e0fa43  92   <- path fix is codegen-neutral
safe_tuned     md5_fn 07b07f1a8055  n_fn 117
r4_hdr         md5_fn 4b800e6d0d47  n_fn  88     rv_hdr (my own derivation) 4b800e6d0d47  88
r4_window      md5_fn f99559928bb6  n_fn  94     r4_window_hdr  cd404bbbfec3  90
r3_endslice    md5_fn 34a618f837f2  n_fn 117     r3_window c7f697a8d9ec 119   r3_hdrarray 999fb67758ff 118
```

| law | residual over my 24 blobs |
|---|---|
| `R4ship − r4_hdr = 4·nrec` | **0** |
| `R4ship − r4_window = −2` (flat) | **0** |
| `R4ship − r4_window_hdr = 4·nrec − 2` | **0** |
| `R3ship − R4ship = 7 + 5·nrec` / `7 + 7·nrec` | **0** |
| `r3_hdrarray − R3ship = nrec` | **0** |

**And the coefficient claim is right for a stronger reason than stated.** On a
`vlen` sweep at fixed `nrec` (56→88, both `≡ 0 mod 4`, both leaving an 8-byte
remainder, so residue-matched), the *binary-differenced* `R4ship − r4_hdr` is
**16.00 → 16.00, slope exactly +0.0000 Ir/byte**. It is genuinely per-record. The
`4·nrec` is confirmed.

### The break: a cheaper in-contract R4, then a cheaper in-contract **R3**

The same licence sentence names **unrolling**. The shipped inner fold is already
unrolled 4× *by LLVM*: `mov / shl / sub` (the `×31`), `movzbl`, `add` = **5
instructions per byte**, plus `add / cmp / jne` = **3 per block**. So the
per-byte rate is

> **`5 + 3/K`, where `K` is the unroll factor — and `K` is a spelling the
> declaration explicitly leaves free.**

That is a zero-parameter derivation, and it lands on every measured value:

| variant | `K` | predicted | measured (incl. the +0.0047 `println` digit term) |
|---|---:|---:|---:|
| shipped R3, shipped R4, `r4_hdr` | 4 | 5.7500 | **5.7547** |
| `rv_u16` (unsafe, 16× manual, 2 induction vars → 6 control) | 16 | 5.3750 | **5.3797** |
| `sv_c16` (**safe**, `chunks_exact(16)` + `try_into::<[u8;16]>()`), `rv_u32_hdr` | 16 | 5.1875 | **5.1922** |
| `sv_c32` (**safe**, `chunks_exact(32)`) | 32 | 5.09375 | **5.0984** |

Disassembly confirms it: `sv_c16`'s hot loop is a straight-line 16-byte body,
`mov/shl/sub/movzbl/add` × 16 with **no bounds check inside it**, then one
`add/cmp/jne`.

`sv_c16` / `sv_c32` are the sharp result. They are **safe Rust — zero `unsafe`
tokens in the kernel** — differ from shipped `safe_tuned.rs` by exactly one
substitution (the value fold), keep both named comparisons literally
(`spelling_matches` req1=req2=True, forb1=forb2=False), keep `p`/`end`,
`p = p + 3 + vlen`, the tag fold before the fit test and the `nrec` fold, and are
byte-identical in stdout and exit status to shipped R3 on **95/95** committed
inputs.

> **`R4ship − sv_c32 = 51·nrec − 5` (`vlen ≡ 0 mod 4`) / `48·nrec − 5` (else),
> ZERO residual on all 22 committed `sweep-n*` blobs; 199 at `small`, 2365 at
> `large`. Positive means the SAFE rung is cheaper than the shipped UNSAFE one.**
>
> Equivalently `R3ship − sv_c32 = 56·nrec + 2` / `55·nrec + 2`, against a
> published safety tax of `5·nrec + 7` / `7·nrec + 7`.

`sv_c32` is cheaper than shipped R4 on **all 24 blobs**, at every `nrec` from 1 to
16 and in both residue classes.

---

## Findings

### `blocker 1` — p16's published in-contract pair interval is wrong by 1–2 orders of magnitude and wrong in sign

`patterns/p16-tlv-walk/NOTES.md:1312-1332` (the "What it refutes" table), and the
same numbers in `patterns/p16-tlv-walk/spec.md:297` (`idiom.why`, **hashed**, and
therefore rendered into `results/tables/p16-tlv-walk.md:37`),
`.memory/01-ladder.md:419-421`, `RECAP.md:459-462`,
`patterns/p05-index-flatten/NOTES.md:1748-1755`,
`patterns/p05-index-flatten/README.md:174-177`.

Published: bottom `nrec + 13` / `3·nrec + 13` (**17 / 43**), top `7 + 10·nrec` /
`7 + 12·nrec` (**47 / 127**), width **111% / 109%** of the shipped pair.

Measured over the same 24 blobs, adding only variants licensed by the same
sentence:

| blob | `nrec` | published `R3−R4` | §10a.1 bottom … top | **measured bottom … top** | width |
|---|---:|---:|---|---|---:|
| `sweep-n1v124` | 1 | 12 | 14 … 17 | **−59 … +65** | 1033% |
| `sweep-n4v124` / `small` | 4 | 27 | 17 … 47 | **−239 … +236** | 1759% |
| `sweep-n9v124` | 9 | 52 | 22 … 97 | **−539 … +526** | 2048% |
| `large` | 10 | 77 | 43 … 127 | **−2449 … +2244** | **6095%** |
| `sweep-n16v124` | 16 | 87 | 29 … 167 | **−959 … +932** | 2174% |

Bottom is **negative on all 24 points**. §10a.1 reports it as strictly positive.

*Failure scenario.* A reader takes "the interval is 111% / 109% wide and the
published pair sits inside it" as p16's honest uncertainty band and quotes
"p16's in-contract safety tax is somewhere in 17…47 Ir/call at `small`". The
true in-contract class on the same blobs contains a **zero-`unsafe` rung that is
199 Ir/call cheaper than the shipped unsafe one**. Every downstream sentence
built on that interval goes with it — including the comparative claim TASK_023
substituted for the one it withdrew (see `major 5`).

### `blocker 2` — "the one-sided bound survives, and it is the only thing that does" — the number attached to it does not

`patterns/p16-tlv-walk/NOTES.md:1338-1341`; the `+19 / +45` figure it defends is
repeated at `NOTES.md:194-204`, `NOTES.md:1250-1257`,
`.memory/01-ladder.md:422-423`, and inside the hashed `why` at
`patterns/p16-tlv-walk/spec.md:297` ("*against the SHIPPED R4 the measured
in-contract minimum is `+19` (small) / `+45` (large)*").

The *bound* statement is still true (trivially). The **measured in-contract
minimum against the shipped R4 is not `+19 / +45`** — it is
**`−199` (`small`) / `−2365` (`large`)**, i.e. negative on all 24 blobs, via
`sv_c32`, which is safe, in contract by the gate's own matcher, and 95/95
equivalent.

*Failure scenario.* p16 remains the project's canonical "idiomatic safe Rust
costs `+27 / +77` here, `+19 / +45` at best" pattern
(`.memory/01-ladder.md` finding 4 is written around it). The correct in-contract
statement is that safe Rust is **cheaper than the shipped unsafe rung on every
blob measured**. p17 already has that result (`−19.00`) and the project treats it
as significant enough to refuse a cell swap over. **p16 is now the second such
pattern and nothing in the tree says so.**

### `major 3` — "The per-byte null survives … stated so nobody re-runs them" is the bullet that hides the result

`patterns/p16-tlv-walk/NOTES.md:1334-1337`, under the heading *"Three things this
does **not** touch, stated so nobody re-runs them."*

The bullet is literally true of `r4_hdr` (slope exactly 0.0000 Ir/byte, I
confirmed it) and false as the class statement it is written as. The per-byte
rate is `5 + 3/K` with `K` unpinned by the same sentence that licensed `r4_hdr`;
in contract the safe rung reaches **5.1875** against the shipped unsafe rung's
**5.7500**, so safe Rust is **0.5625 Ir/byte cheaper** — the opposite sign from
`.memory/01-ladder.md:367-371`'s *"R3's marginal rate is 5.7500 Ir per folded
byte, which is R4's exactly. Idiomatic safe Rust costs **zero per byte** here."*

*Failure scenario.* The sentence is an explicit instruction not to re-run the
experiment. The next agent obeys it and finding 4's headline stands
indefinitely. This is the same defect class as the sentence TASK_023 was written
to remove, one level up: a one-lever result generalised into a null.

Finding 4's claim remains true **of the shipped pair**. What must go is §10a.1's
inference that the search left it untouched.

### `major 4` — the interval's top endpoint cannot be a p16 rung, and only a generator docstring says so

`patterns/p16-tlv-walk/NOTES.md:1298-1300` (the `r4_hdr` table row) and
`spec.md:297` present `(r3_hdrarray, r4_hdr)` as an *"admissible pair"*.

Verus, at the pinned vstd, **cannot verify `read_unaligned`** — its own source
says so: `../LearnVeri/_VERUS_DOC_/vstd/raw_ptr.rs:128-131`, *"`std::ptr::read_unaligned`
… aren't supported because `PointsTo` enforces both non-nullness and
alignment."* p16's `identity` pin (`spec.md:372-375`) requires `unsafe` ≡
`verus` **exact** at `-O3`, and `.memory/01-ladder.md:13` defines R5 as "R4's
exec code, plus Verus specs". So shipping `r4_hdr` needs a **fourth trusted
item**, carrying a security-relevant `ensures` over an unaligned 2-byte load, in
the pattern whose *entire* memory-safety claim is one trusted `requires`
(`spec.md:132`, `NOTES.md:553-556` — "**TCB: 6 lines across 3 items**", "p16 has
*nothing* behind its one trusted `requires`").

`controls/gen_controls.py:69-71` states this. `NOTES.md` §10a.1 does not, and
neither does the hashed `why` that `report.py` renders into all six published
tables.

This is also the precise answer to the prompt's "same category of edit on the
safe side": it is **not** the same category. `r3_hdrarray`, `r3_window`,
`sv_c16` and `sv_c32` are safe Rust and cost zero TCB. The R4-side endpoint costs
a trusted axiom; the R3-side ones — which are the larger effect anyway — cost
nothing.

### `major 5` — the withdrawal is right; its replacement inherits the defect

The withdrawal of *"p05's declaration is the loosest of the set"* is **correct
and complete**. All three sites now carry it as withdrawn with the reason and
none asserts it: `patterns/p05-index-flatten/NOTES.md:1747-1755`,
`patterns/p05-index-flatten/README.md:174-177`, `RECAP.md:259-262`. Independent
grep for `loosest` across the tree returns exactly those three, all in
retraction form. **Confirmed.**

But the **replacement** comparison — *"p16's pair interval is 111% / 109%,
**wider** than p05's 80% / 71%"* — is now asserted in four files
(`p16/NOTES.md:1332`, `p05/NOTES.md:1752`, `p05/README.md:176`,
`.memory/01-ladder.md:419-421`, `RECAP.md:460-462`), and:

- p16's half of it is refuted above (≥1759% / 6095%);
- it compares a **2-lever** p16 search against p05's **46-spelling** search,
  which is the same "one interval is not the other's peer" error one level down
  from the pair-vs-R3-only one it replaced.

The right move is to withdraw the comparison entirely, not to re-point it.

### `minor 6` — `.memory/01-ladder.md:86-89` still says the edit is owed

> *"It is currently written unqualified in all six patterns' `idiom.why`, hashed
> into `contract_sha256` (TASK_022 flagged it and correctly did not touch it; it
> is a cross-pattern decision)."*

False since `1c24c6c`. The manager's follow-up `7c9b11c` fixed `01-ladder:412`,
`01-ladder:620` and `06-catalogue:136` and describes itself as *"Three places in
`.memory/`"*; this is a fourth, **eleven lines above** one it did fix. A future
agent reads it as an open cross-pattern edit and re-does it.

### `minor 7` — `.memory/02-bench-rules.md:38-44` still lists p08's generator as unfixed

> *"p16's new generator rewrites the path to the real, hashed file; **p08's is
> not fixed**."*

It was fixed at `1fec803` (TASK_022): `patterns/p08-overlap-move/controls/gen_controls.py:67`
now carries `PATH_FIX`. This is the *same* stale claim TASK_023 corrected as a
ride-along in `p16/controls/gen_controls.py:51-58` and `p16/NOTES.md:1232-1237` —
the authoritative copy was the one nobody grepped. It sits in the "known
residuals we are deliberately **not** closing" list, so it actively misdirects.

### `minor 8` — the gate-noise inventory understates itself by 2.7×

`.memory/03-measurement.md:483-495` records, for two consecutive runs on an
unchanged tree: *"p05: 4 leaves … p08: **8 leaves**. `marginal_ir_per_call` on
the `O0`/`whole` rows, all ±0.02."*

I re-ran all six gates on the **unchanged committed tree** and leaf-diffed
against the committed records:

| pattern | leaves moved | what |
|---|---:|---|
| p01 | 0 | — |
| p02 | **3** | ASan diagnostic strings — **not recorded** |
| p05 | 4 | 2 heap-OOB stdouts + 2 ASan diagnostics ✔ matches |
| p08 | **23** | `marginal_ir_per_call`, and **not only `O0`/`whole`**: `O0/isolated`, `O0/whole`, `O3/isolated`, `O3/whole` |
| p16 | **1** | ASan diagnostic — **not recorded** |
| p17 | **1** | ASan diagnostic — **not recorded** |
| total | **32** | |

The delivery's own churn is the **same 23 p08 keys**, so it is noise and not an
effect — the engineer was right to leave it. Magnitudes run to **±0.08**
(`unsafe/O0/whole/large.bin`, 206209.62 → 206209.54), not ±0.02. So: **p08's
churn is 23 leaves this run, not ~8** — the task file's expectation was wrong,
and `.memory/03-measurement.md` understates the count, the row span and the
magnitude, and omits p02/p16/p17 entirely.

### `minor 9` — 26 citations of a finding that does not exist

`grep -rn "finding 14" --include=*.md` returns **26** hits outside `.temp/`, all
pointing at `.memory/01-ladder.md`, whose numbered structural findings run
**1–7**. Pre-existing, but TASK_023 propagated two more
(`patterns/p16-tlv-walk/NOTES.md:1257`, `patterns/p02-buffer-copy/NOTES.md:48`).
The intended referent is presumably the R4-by-permission paragraph at
`.memory/01-ladder.md:24-28`.

### `minor 10` — p02's hashed `why` still says "is an UPPER BOUND" bare

`patterns/p02-buffer-copy/spec.md:227`, pattern-specific tail:
*"So p02's published `R3ship - R4ship = +10` … **is an UPPER BOUND** whose
measured in-contract minimum is `+6` / `+5`."* — two sentences before the shared
paragraph that now says `R3ship - R4ship` is **not** an upper bound on the safety
tax. A closing sentence does qualify it (*"`+6` is an R3-side bound and not p02's
safety number"*), so this is an internal inconsistency inside one hashed block
rather than a false claim. `patterns/p02-buffer-copy/NOTES.md:1364` states it
correctly.

---

## Priority 4 — the eleven out-of-block occurrences, re-grepped independently

At `b0533f7` (the tree TASK_023 started from), `git grep` for the refuted forms
outside the six hashed `why` blocks and their six rendered table copies, and
outside `.tasks/` (historical specs, correctly left alone), gives **12** sites:
`.memory/01-ladder.md` ×2, `RECAP.md` ×2, `p02/NOTES.md` ×2, `p05/NOTES.md` ×1,
`p16/NOTES.md` ×3, `p16/spec.md` prose ×1, `p17/NOTES.md` ×1. Ten of those were
in files the engineer was allowed to touch — consistent with the reported eleven
(the engineer's count includes looser RECAP phrasings my pattern misses).

**At HEAD, no file in `patterns/`, `RECAP.md` or `results/tables/` still asserts
it.** Every surviving "upper bound" in those trees is the correctly qualified
`inf(in-contract R3) − R4ship` form. The only survivors are the two `.memory/`
items above (`minor 6`, `minor 7`) — the authoritative layer, again.

The six tables are in sync with their `spec.md`: for all six, the full `why`
string and the new sentence are present verbatim in `results/tables/*.md`.

## Priority 5 — nothing checks the six `why` copies are byte-identical

**Confirmed, structurally.** `check.read_contract` (`harness/check.py:467-478`)
opens `os.path.join(pdir, "spec.md")` and nothing else; `check.py` takes one
pattern per invocation and never reads another pattern's `spec.md`. So the
paragraph's own instruction — *"this paragraph is byte-identical in all six
patterns' `why` -- diff them"* — is enforced by nobody.

I diffed them: the shared block is **8526 characters, byte-identical in all
six**, the replacement sentence occurs **exactly once** in each, and the block is
**87.9 / 77.5 / 87.9 / 86.6 / 60.7 / 73.8 %** of each `why` — which independently
confirms the commit message's "61-88%".

**Is it worth a harness change? No.** Per `.memory/02-bench-rules.md:25` the test
is "could this defect happen by accident?" — yes, it plainly could, TASK_023 is
exactly that edit. But the cheap detector already exists and was already used:
**"`contract_sha256` moved on all six" catches a missed file**, and that check
costs nothing because the records are committed. A cross-pattern gate stage would
also have to decide *where the shared block ends*, which is a reading and not a
grep — the same undecidability `.memory/01-ladder.md:119-128` already found for
`required`. Recommendation: put the 15-line differ under `.temp/` provenance in
the paragraph itself, or have `report.py` (which already walks all six for the
index) note divergence in the **reporting-only** style of stage `0b`. Do not add a
failing gate stage.

## Priority 6 — standard validity

- **All six gates re-run by me on the committed tree, fresh builds, full runs:**
  p01 `PASS-WITH-BLOCKED-ROWS` (the pre-existing `miri … large.bin` 180 s block,
  documented in its own record), p02 / p05 / p08 / p16 / p17 **`PASS`**.
  Logs `.temp/review023/gate_p*.log`; fresh records `.temp/review023/gate_fresh/`;
  the committed records were restored byte-for-byte afterwards (`git status`
  clean).
- **42 md5 leaves unchanged: verified.** Flattening all six records gives exactly
  42 `md5*` leaves (`identity[i].md5_fn_a`, `md5_fn_b`, `md5_raw_equal`; p01 has
  two identity pairs, the rest one), **0 moved** across `b0533f7 → 1c24c6c`, and
  0 moved across `HEAD → my re-run`.
- **Six `contract_sha256` moved: verified.**

  | pattern | before | after |
  |---|---|---|
  | p01 | `bc27937575846299` | `3fcbdf0e9cfe8ad1` |
  | p02 | `ada09f7bd62411bf` | `42370b066e8cff1d` |
  | p05 | `08d96ff2cb25d336` | `9f1f7ba19d1f8943` |
  | p08 | `0bc0c03f1265a866` | `cd81ea6118e1ca35` |
  | p16 | `d661369f1c3777fd` | `ca4e867d450bf1cd` |
  | p17 | `e24976ac41cfdedf` | `7b6d6cd6182b5933` |

  `source_sha256` moved on all six too, correctly (the `spec.md` leaf in each,
  plus the `NOTES.md`/`README.md`/`gen_controls.py` leaves that were edited).
- **p08 churn: 23 leaves this run, not ~8.** See `minor 8`.
- The ride-along is done: `controls/gen_controls.py:51-58` now credits TASK_022
  with the p08 `#[path]` fix, and p08's generator does carry `PATH_FIX` at line 67.

## Priority 7 — clean negatives (named so nobody re-runs them)

1. **`r4_hdr` is unsound / Miri-dirty** — no. Clean on `small` plus all three
   adversarial inputs; the obligation is the one the two byte loads already had.
2. **`r4_hdr` is self-certified** — no. The licence sentence is byte-identical in
   `spec.md` since `432a7c6`, two tasks before the measurement.
3. **`r4_hdr` fails the gate's own token matcher** — no. req1=req2=True,
   forb1=forb2=False, same as the shipped rung.
4. **`4·nrec` is a fit, or a per-byte effect in disguise** — no. Zero residual on
   24 blobs in my own build, both residue classes, and the binary-differenced
   `vlen` sweep gives slope **exactly 0.0000 Ir/byte**.
5. **The controls drifted from the rungs, or the digests are cross-build** — no.
   `rv_ship` (shipped `unsafe.rs`, only the `#[path]` rewritten) reproduces
   `md5_fn 852405e0fa43 / n_fn 92`; my independent derivation of the header edit
   reproduces `4b800e6d0d47 / 88`; all eight §10a/§10a.1 digests reproduce.
6. **`rv_slice` — the value fold as `get_unchecked(p+3..p+3+vlen).iter().fold()`**
   — **dearer**, 5…37 Ir/call, on all 24 blobs. The R3-style fold does not help R4.
7. **`rv_u8` — 8× manual unroll** — **dearer**, 12…148 Ir/call. 8 is below the
   quality of LLVM's own 4× unroll once the manual guard adds an induction
   variable; **16 is the first factor that wins**. (It is nonetheless a legitimate
   in-contract spelling and is what makes the interval's bottom negative.)
8. **Forcing `imul $31` instead of `mov/shl/sub`** — not reachable from Rust
   source; LLVM's strength reduction is a latency choice and only inline asm
   would override it, which the pattern's no-barrier rule excludes. Would be worth
   **2 Ir/byte** if anyone finds a way. Not attempted further.
9. **The withdrawal of "loosest of the set" is incomplete or wrong** — no, it is
   right and complete. Only the replacement comparison is a problem (`major 5`).
10. **The six `why` copies diverged** — no. 8526 bytes, identical, one occurrence
    each.
11. **A leaf moved that should not have** — no. Beyond the documented noise, the
    only moved leaves across `b0533f7 → 1c24c6c` are `contract_sha256`,
    `idiom.why` and the edited `source_sha256` file leaves — 3 to 7 per pattern
    plus p08's 23 noise leaves.

## What I did not do

- I did not search p16's R2, nor p17 / p02 / p01 / p08's R4 sides. The unroll
  lever is generic (`5 + 3/K` is not p16-specific) and every pattern with an
  inner byte loop is exposed to it; **`p17` and `p02` are the obvious next
  targets** and both currently publish one-sided R3 bounds.
- I did not attempt to *verify* `sv_c16` in Verus — it is an R3 cell and R3 has
  no proof, so nothing is owed. I did not check whether an unrolled **R4** would
  keep `verus.obligations = 10` (it would not: a third loop adds a query), only
  that it needs no new trusted item, unlike `r4_hdr`.
- I did not land any edit. No `git add`, no `git commit`, no history-mutating git
  command was run. Nothing under `patterns/`, `harness/`, `pilot/` or `.memory/`
  was modified; `results/gate/*.json` was restored from the pre-run copy in
  `.temp/review023/gate_committed/` and `git status` is clean.
