# TASK_087_REVIEW — report

**Role: research reviewer.** Attacked `p19-state-machine` (`3962cb3` / `fb9e9ef`)
along A1–A6. Ran `check.py p19` (PASS, reproduced), `measure.py p19
--check-stale` (2 records FRESH), disassembled all eight cells, **re-fitted p19's
two published laws from the committed sweep band**, rebuilt five controls, and
**checked the two CVE IDs online**. Evidence in `.temp/r87/`; every artefact has
a generator; `git status --porcelain` empty at start and finish.

**PROTOCOL rule 2 running count: 245 → 249.** ⚠ **Four contradictions with
measurements. Three are the engineer's, committed by the manager; the fourth is
the manager's OWN committed claim.**

---

## ✅ A1 — the headline HOLDS, and it can be stated harder than the report did

`safe_naive::kernel` fold body = **15 instr / 1 byte**:

```
1573f: cmp $0x8,%rdx
15743: jae 15786
15786: lea 0x3f4cb(%rip),%rdx ; mov $0x800,%esi ; call *0x413f8(%rip)   # panic_bounds_check(idx, LEN)
```

⚠ **The panic call's length argument is the literal `0x800` = 2048 = `tbl.len()`**,
so the branch is provably the `tbl[…]` slice check and nothing else; and **the
compare is on `%rdx` = `st` BEFORE the index is built** (`%rdi = st<<8 | b`, via
`shl`+`or`). **LLVM really did rewrite `st*256+b < 2048` into `st < 8`.** The
validation pass in the same function emits `cmpb $0x7,…; ja` ×4 — **the same
predicate.**

**What would have broken the equality** (asked for, and answered): `b` not
provably ≤ 255, or `TBL` not an exact multiple of 256. **Neither is respellable
in contract.**

R3 fold 39/4 with **exactly four `and $0x7,%edi`**; R4 fold 35/4. **39 − 35 = 4 =
the four `and`s, instruction for instruction** — §8a confirmed without needing
the unroll control.

## ✅ A5 — confirmed and strengthened, across all NINETEEN sweep lengths

Not just the two matrix inputs: `c-gcc-h − c-gcc = 10242.00` and
`c-clang-h − c-clang = 5637.00`, **exactly constant at m = 64…5001**. Crossover
root from the m ≡ 0 (mod 4) band = **2509.4**, so *"m ≈ 2510"* holds.
`verus == unsafe` marginal at all 19 lengths.

**Method cross-validated:** at m=4096 the reviewer's marginals equal the gate's
`large.bin` marginals **to the decimal for all eight cells**.

---

## major 1 — *"the only entries in this tree that forbid a spelling for being SAFE"* is FALSE

Sites: `NOTES.md:42-43`, `spec.md:212`, `README.md:35`, `TASK_087_REPORT.md` §0.
Counterexamples, each with the reason in its **own** `idiom.why`:

- **p36 `forbidden[2] op & 7` / `[3] op % 8` / `[5]` / `[6]`** — *"masking the
  opcode into range is a THIRD program — it makes every byte a legal opcode, so
  the out-of-table input stops being adversarial and the pattern's whole security
  half evaporates."* ⚠ **That is verbatim the same exclusion, in the pattern p19
  names as its NEAREST SIBLING.**
- **p03 `forbidden[1] & (STACK_CAP - 1)`** — *"MASKING IS FORBIDDEN … silently
  turns an out-of-range access into an in-range one, which is the opposite of
  what this pattern models."*

**Failure scenario:** the manager lands this as p19's novelty and the next agent
reading p36 finds the mechanism already published — **the same class of false
novelty that shipped into eight places once already.** Not inside
`contract_sha256` (all sites are prose), so the fix is **text only**.

✅ **The PRACTICE is fine and was attacked:** forbidding the safe spelling is
**not** `Rust-in-C-syntax` in reverse, because the alternative is a benchmark
whose bug is unreachable or absent — **and both p03 and p36 already do it.**
**Only the uniqueness claim is wrong.**

## major 2 — the two published laws do not describe the shipped cells, and p19's own sweep band contradicts them

`NOTES.md` §11 and `inputs/gen.py:45` publish `R2 − R4 = 6.25·m − 8` and
`R3 − R4 = 1.00·m − 2`. Re-fitted from the **committed** band with the shipped
`-O3 isolated` binaries — exact, zero scatter inside each residue class:

```
R2 - R4 = 6.25m - 6      (m=0 mod 4)   R3 - R4 = 1.00m + 4   (m=0 mod 4)
        = 6.25m - 12.25  (m=1)                 = 1.00m + 3   (m=1,2,3)
        = 6.25m - 14.5   (m=2)
        = 6.25m - 16.75  (m=3)
```

⚠ **The published intercepts are wrong at EVERY residue class, and there is an
unmodelled `m mod 4` term** — R4 unrolls 4×, and its scalar epilogue body is 11
instr/byte against 8.75, worth **2.25 per epilogue byte**.

⚠⚠ **Worse, the laws disagree with p19's OWN gate-measured cells:**

| | measured | law says |
|---|---|---|
| m=256, R2−R4 | **1594** | 1592 |
| m=256, R3−R4 | **260** | 254 |
| m=4096, R2−R4 | **25594** | 25592 |
| m=4096, R3−R4 | **4100** | 4094 |

**`NOTES.md` §4 prints `1594`, `25594`, `260`, `4100` itself, two sections above
the law that contradicts them.** This is exactly *"the only out-of-sample test
here that can fail"* and **the residue rule the band exists for.**

✅ **The headline survives** — OLS over 19 lengths gives `6.250530·m` and
`1.000035·m`, and **every m ≡ 0 (mod 4) is exact**. **Strike or re-state the
intercepts; keep the slopes.** Failure scenario: someone extrapolates `R3 − R4`
to a small odd `m` and is off by 5–6 `Ir` on a quantity of order 60.

**Fix cost:** `inputs/gen.py` is in the **measurement** record's
`source_sha256`, but a **docstring-only** edit classifies **GEN-ONLY**, not a
re-measure. `NOTES.md` is only in the **gate** record → one `check.py p19`.

## major 3 — A3: both CVEs are REAL, but one is misquoted and misattributed

Checked against the CVE Program's own API (`cveawg.mitre.org`).

- ✅ **`CVE-2026-23407` — REAL, published 2026-04-01, CVSS 7.8.** Title
  **verbatim** as p19 quotes it. Its description is **exactly p19's bug**:
  *"it reads `k = DEFAULT_TABLE[j]` and uses `k` as an array index without
  validation. A malformed DFA with `DEFAULT_TABLE[j] >= state_count`, therefore,
  causes both out-of-bounds reads and writes."* **Keep it — it is a stronger
  citation than p19 realises.**
- ⚠⚠ **`CVE-2026-23269` — REAL, published 2026-03-18, CVSS 7.1 — but its title
  is *"apparmor: validate DFA start states are in bounds in unpack_pdb"*.** p19
  quotes it, **in quotation marks**, as *"AppArmor `unpack_pdb` DFA bounds
  validation hardening"* — **a paraphrase presented as a title.** And **it is a
  different bug**: an untrusted **start state** indexing
  `dfa->tables[YYTD_ID_BASE][start]`, fixed at unpack time. **p19's kernel starts
  at `st = 0` by construction and models no start state at all.**

So `c/kernel.c:7` and `README.md:18` — *"That is CVE-2026-23269's shape"* — **name
the wrong CVE; the shape is 23407's.** Sites: `c/kernel.c:7`, `c/kernel.h:52`,
`README.md:18`, `NOTES.md:67`, `spec.md:65`. **None inside the hashed block.**
⚠ **`c/kernel.c` and `c/kernel.h` ARE in the measurement record's
`source_sha256`, so a comment-only fix there will read STALE — not GEN-ONLY.**

✅ The fetched source is genuine: `.temp/t87/apparmor_match.c`, md5
`9a9b3ee5c028e7687c67ec9bb4fd1e24`, `verify_dfa()` at 154–230 matching what
NOTES quotes.

## ⚠⚠ major 4 — A6, THE MANAGER'S OWN COMMITTED CLAIM, REFUTED THREE WAYS

The claim: *"p19 is the ONLY pattern that calls a vstd exec trusted function from
its kernel … so RECAP 'Owed' 0's sixth route is no longer hypothetical."*

**(1) The grep was not complete.** It was a **whitelist of four slice-shaped
names**, so it could only ever find slice-shaped calls. The reviewer enumerated
**all 187 exec `#[verifier::external_body]` fns in the pinned vstd** (118
distinct names) and grepped every `patterns/*/verus.rs` with comments blanked:

```
vstd/raw_ptr.rs:578-579   #[verifier::external_body] pub fn ptr_mut_write<T>
vstd/raw_ptr.rs:619-620   #[verifier::external_body] pub fn ptr_ref<T>
p27-handle-table/verus.rs:586   ptr_mut_write(base, Tracked(&mut pt), v);   in rec_open
p27-handle-table/verus.rs:620   *ptr_ref(p, Tracked(pt))                     in rec_read
p27-handle-table/verus.rs:626   fn kernel -> 708 rec_open, 776 rec_read
```

⚠ **p27's own comment says it at `verus.rs:564`**, and p27's published
`tcb_items` is **7, none of them vstd's**. ✅ **MANAGER-VERIFIED.**

**(2) The framing is wrong, and it re-opens a CLOSED decision.**
`.memory/04-verus.md` *"How the TCB column is counted (TASK_048)"* **decided this
at TASK_055_REVIEW**: one number = project-local trusted items; a second
*"vstd relied upon"* column was **refuted with a 402-site census** and *"must not
be reinstated"*; the remedy is **prose beside the number**. ⚠⚠ **And it named
this exact case IN ADVANCE** — *"A pattern built on `vstd::raw_ptr` does not …
**Decide how such a pattern is counted BEFORE building one.**"* **p27 is that
pattern, and it was built.**

**(3) It is not the sixth route.** RECAP's sixth route (B4) is about **used vstd
`assume_specification`s** making `check_miri`'s *"no trusted item ⇒ Miri not
required"* branch print a false sentence. `slice_subrange` is `external_body`,
**not** `assume_specification`, and p19 has **three local trusted items with
`miri.required: true`**, so it **never reaches that branch**. ⚠ **Meanwhile the
LITERAL sixth route has been non-hypothetical in 22 of 23 patterns since long
before p19**: `bytes.len()` and `bytes.as_slice()` inside `verus!` are vstd
`assume_specification`s (`std_specs/vec.rs:93` and `:236`).

**It changes only the prose, not the number.** Under the decided accounting
p19's `tcb_items` stays **3** — and **p19 already does the required prose**
(`verus.rs:31-35`, `NOTES.md` §7).

⚠ **RECOMMENDATION: DO NOT LAND THIS AS A FINDING.** At most: *"p19 is the
SECOND pattern, after p27, whose kernel calls a vstd `external_body` exec item —
and `.memory/04-verus.md` already covers both."*

## minors

1. `NOTES.md` §4 and §8d cite *"`.memory/01-ladder.md` finding 7"* / *"finding
   5"* for the same-LLVM-backend result. That is **RECAP finding 7**;
   `.memory/01-ladder.md` finding 7 is p08 and finding 5 is p17. ⚠ **Precisely
   the collision p36's `spec.md` documents as having *"already sent agents to the
   wrong finding"*, and `patterns/p38-alias-pun/NOTES.md:328` has the same
   mis-citation — p19 inherited it.** Adjacent; reported, not fixed.
2. `safe_tuned.rs:19` says R2 and R3 agree on *"all **nine** inputs, checked by
   the gate"*. The gate checks **eight**; the 19 sweep blobs are not in
   `inputs_checked`. (They do agree — checked.)
3. `NOTES.md` §4 says *"Miri: 7 of 7 inputs"*; the gate record has **eight**.
4. `results/gate/*.json` embeds raw ASan text **including PIDs and pc
   addresses**, so any `check.py` re-run dirties the tree even when nothing
   changed. Not p19-specific; worth normalising if it ever bites.

---

## Clean negatives, by name — these attacks did NOT land

- ✅ **"R4's spelling was chosen to match R5's" is an honest disclosure, not a
  rigged pin.** R4 rebuilt with the inline `&v[i..j]` gives a **byte-identical**
  kernel at O3 — 411 B, md5 `0ddbc5381b7d5e64bdb517c9e7d3e8c9` — and an
  identical marginal `41516.3000`. **The pin costs R4 nothing at the measured
  level.**
- ✅ **The hashed `identity.why` reproduces exactly** — both kernels **235 B,
  md5 `ac3fb207cd05963419d722adcd8b9da2`**, from the **LINKED** binaries.
- ✅ **R4 ≡ R5 independently**: 411 B / `0ddbc5381b7d…` on both, extracted by
  symbol extent, not by address.
- ✅ **R2 is NOT pessimised.** Two further in-contract R2 spellings the engineer
  did not try measure **exactly** the shipped R2's own numbers and print the same
  checksum; the `try_into` one is **byte-identical** to shipped. **Five R2
  spellings now, all degenerate.**
- ✅ **R3 is genuinely check-free in the fold** — no compare, no branch, no panic
  call in the body; **the mask replaces the check rather than moving it.** Both
  R3 and R4 still pay the same per-call slice checks, symmetrically.
- ⚠⚠ **A2's kill risk does NOT fire, and the honest reading is better than the
  claim.** *"Delete the pass and R2/R3 become two programs"* is **demonstrated**:
  without the pass R2 **panics** and R3 returns `2785253154441869312` on
  `adversarial-confuse.bin`; with it, both return `REJ`. **p19's check IS dead in
  the sense A2 means** — provably redundant on every input the benchmark
  presents, and `safe_naive.rs:13-18` says so itself. **What it prices is not a
  live check but the UNLEARNABILITY of a loop-carried data invariant: 6.25
  `Ir`/byte for a fact Z3 discharges in ghost code and LLVM cannot** — which is
  `.memory/01-ladder.md` **finding 2 with a mechanism**. ✅ **The pattern already
  publishes it.**
- ✅ **No constant folding, no leaked constants** — every kernel load is through
  a runtime pointer; three blobs one byte apart give three different R1 answers.
- ✅ **`gen.py` determinism**: two fresh regenerations byte-identical to each
  other and to all 27 committed blobs; residue coverage and both one-byte
  distances reproduce.
- ✅ **The un-gate-checked sweep blobs DO agree** — all 8 cells over all 19
  blobs, zero disagreements.
- ✅ **`model.py` is independent.** `st_fold` (flat) and `_fold_rows`
  (row-split) are two implementations cross-checked per window;
  `sanitizer_expect` comes from `_unvalidated`, which simulates `c/kernel.c` and
  tests the index against `[0, n_blob)` — and `n_blob` **is** the ASan object.
  `gen.py` re-implements the detector **without importing `model.py`**.
- ✅ **TCB recount: 3.** Both `ensures` conjuncts deleted and **load-bearing**
  (2 and 1 errors); both `requires` conjuncts probed **not a tautology** — and
  that is **full coverage**, since p19 has no other clauses anywhere.
- ✅ **`measure.py p19 --check-stale`**: 2 records, **0 STALE**, both FRESH.

## Unsure / not done

- Did **not** re-verify that all twelve named prior patterns really carry
  `index >= len` (took TASK_086 #240's corrected count).
- Did **not** re-run the rolled-vs-rolled `-unroll-count=1` control — the
  disassembly diff makes it unnecessary for §8a, **but §8b's 3.00 / 3.25 split
  still rests on it alone.**
- **No wall-clock work.** Did not sweep other patterns.
- The gate re-run rewrote `results/gate/p19-state-machine.json`; structural diff
  against a byte-snapshot showed **only** the two ASan `diagnostic` strings
  (PID + pc). **Restored from snapshot.**
