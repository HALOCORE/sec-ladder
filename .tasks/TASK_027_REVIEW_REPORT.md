# TASK_027_REVIEW — report

Reviewer's return message, recorded by the manager (the reviewer cannot commit).

⚠ **This file was cited by `.memory/01-ladder.md` and `.tasks/TASK_028.md` before
it existed** — the manager landed the corrections from the return message and
never wrote the file, and TASK_028's engineer found the dangling path. Written
retrospectively from that message; the reviewer's own scratch, including the seven
Verus logs, is `.temp/r27/` (`NOTES.md`, `gen_r5_p05.py`, `verus_p05_v{1..7}.log`,
`ctlcontract.py`, `foldcmp.log`, `gen_inputs_{1,2}.log`, `blobs-run{0,1,2}.txt`).

Scope was four questions, deliberately narrow.

## Q1 — the inferential step is VALID, and one word is missing from the sentence

The step: the gate checks the **shipped** `unsafe.rs` / `verus.rs` pair; TASK_027
inferred from it a constraint on **candidate** R4 spellings. Valid, on three
independent grounds:

1. **The pin names ROLES, not files.** `{"a": "unsafe", "b": "verus", "O3":
   "exact"}` names *cells*; `buildmod.RUST_SRC` maps a cell to a filename. A
   candidate substituted into the role inherits the pin. "Admissible R4" = "could
   occupy that role" ⇒ needs a verifying, byte-identical R5.
2. **The ladder's own rung definition already quantifies over R4** —
   `.memory/01-ladder.md:13`: *"R5 verus | R4's exec code, plus Verus specs and
   proofs discharging every unsafe precondition. **Ships the same machine code as
   R4.**"* A candidate R4 with no verifying twin leaves the pattern with four
   rungs.
3. **The project already reads a hashed pin as a class constraint, and has for
   eleven tasks** — `idiom`. Every in-contract verdict since TASK_017 applies
   `required`/`forbidden` to *unshipped* variants, and `.memory/01-ladder.md:12`
   writes R4's rung-table entry as "**Subject to the pattern's declared idiom**".
   `identity` and `idiom` are keys in the same hashed block.

**The strongest counter-argument found, and it fails on the code.**
`harness/check.py:1723` heads the section *"3c. structural identity — a RESULT,
not a gate condition"*, repeated at `:56`. The code contradicts the comment:

```
check.py:1758   if got_i < want_i:
check.py:1763       rep.fail("identity", f"{a} vs {b} at {o}: identity dropped to ...")
check.py:4826   if rep.failures:
check.py:4827       verdict = "FAIL"
```

and `check_miri` (4508-4511) makes it semantically load-bearing: *"R4 and R5
differ at O3 (identity {level!r}), so R4 does not inherit R5's discharged
obligations at all"*. → **minor: that comment is false and is the one sentence in
the tree arguing against the step.** (Fixed at TASK_028 item 5.)

**Not self-certification**, on a test that does not use the broken direction rule:
the edit changes nothing the gate does, and it moves published numbers *against*
the author's interest — it deletes TASK_024's "the unsafe rung wins by
`2 + 5·nrec`" on p16, and on p05 it raises the bottom of the pair interval and
deletes "the tax is exactly 0". It costs the project its two most-quoted
counterintuitive results.

**Two qualifications, both measured:**

- **The class must be defined by EXPRESSIBILITY, not by "Verus verifies it".**
  Same exec code, two twins: `p05_v3` (transplant + minimal ghost tidy) →
  `11 verified, 1 errors` / *postcondition not satisfied*; `p05_v5` (same exec
  code, one `lemma_zero_ncol` and one `proof` block) → **`13 verified, 0
  errors`**. A failed transplant disqualifies nothing; only `is not supported`
  does, because only that forces a new **trusted** item.
- **The sentence needs "at the pinned vstd" and does not have it.** Verus prints
  *"you may be able to add a Verus specification to this function with
  `assume_specification`"* on every rejection, and an upstream vstd shipping one
  costs the pattern zero TCB. The `r4_hdr` instance in the same `why` carries the
  qualifier; the general sentence at `spec.md:298` did not.

## Q2 — BLOCKER. p05's "R4 moves 7 flat" has no rung behind it, and both endpoints of p05's pair interval fall with it

`p05/spec.md:409` pins the same `unsafe vs verus {O0 norel, O3 exact}`. All six
patterns pin it; p01 additionally pins `safe_naive vs safe_naive_verus`.

`.memory/01-ladder.md`'s prediction — *"the same lever that moved p05's R4"* — is
**confirmed**. `patterns/p05-index-flatten/NOTES.md:1614`'s `c4_hu16_nz` is
`.temp/p22/v05/d4_nz_raw.rs:11-13`:

```rust
let p: *const u8 = unsafe { buf.as_ptr().add(off) };
let nrow: usize = unsafe { (p as *const u16).read_unaligned() } as usize;
```

Seven R5 twins built from `patterns/p05-index-flatten/verus.rs`, foreground:

```
baseline verus.rs                                    rc=0   12 verified, 0 errors
v1  published -7 spelling (read_unaligned + no zero guard)   rc=1
    error: `core::ptr::const_ptr::impl&%0::read_unaligned` is not supported
    error: `core::slice::impl&%0::as_ptr` is not supported
    error: `core::ptr::const_ptr::impl&%0::add` is not supported
v2  the -5 half alone (read_unaligned hdr)                   rc=1  same 3
v3  the -2 half alone (no zero guard), minimal ghost tidy    rc=1
    error: postcondition not satisfied  -- 11 verified, 1 errors, NO unsupported feature
v4  v2 + ONE new external_body wrapper (4th trusted item)    rc=0  12 verified, 0 errors
v5  v3 + real ghost repair (lemma + proof block)             rc=0  13 verified, 0 errors
v6  r4_dataslice (from_raw_parts)                            rc=1
    error: `core::slice::raw::from_raw_parts` is not supported
    error: `core::ptr::const_ptr::impl&%0::add` is not supported
    error: `core::slice::impl&%0::as_ptr` is not supported
v7  header via u16::from_le_bytes over two get_unchecked bytes  rc=1
    error: `core::num::impl&%7::from_le_bytes` is not supported
```

What it decides:

- **`c4_hu16_nz` is not a p05 R4.** It needs exactly one new trusted item (v4) —
  precisely the cost `r4_hdr` was disqualified for on p16, on a pattern whose
  memory-safety claim is three `external_body` items (`verus.rs:47`).
- **v7 closes the escape hatch**: the header lever is blocked as a *lever*, not as
  one spelling. Raw-pointer, `try_into`-array and `from_le_bytes` routes are all
  unsupported.
- **The `−2` half survives at zero TCB** (v5) — **but it was never compiled**. All
  26 of TASK_022's round-3 variants pair the zero-guard deletion with
  `read_unaligned`, so `−2` is an inference (`−7` minus `−5`), never a
  measurement. The p05 analogue of p16's never-built hand-unrolled 32× fold.
- **Both endpoints of p05's published pair interval fall.**
  `NOTES.md:1729-1731` builds `2·nrow − 2 … 6·nrow + 20` (36…134 / 128…410) from
  the *dearest* R4 `r4_dataslice` (v6) and the *cheapest* `c4_hu16_nz` (v1), both
  inadmissible. Substituting the cheapest/dearest admissible R4 found (0, the
  shipped cell) gives **`5·nrow + 6 … 6·nrow + 13` = 101…127 / 331…403**, width
  `nrow + 7` = 26 / 72 — *exactly* the R3-side-only span it was said to replace.
  (Arithmetic on p05's own published laws; no Ir re-measured.)
- **"An admissible pair exists whose tax is exactly 0" loses its rung** —
  `sweep-r1c30`'s 0.00 is a cheapest-R3-vs-`r4_dataslice` pairing.
- Six further round-1 R4 variants (`r4_getrange`, `r4_rowslice`, `r4_dsrow`,
  `r4_dataptr`, `r4_base`, `r4_for`) all measure 0 and were **not** Verus-tested,
  so their admissibility cannot move an endpoint either way.

**p17 — clean negative, do not re-run.** `−19.00` is **R3-side**
(`NOTES.md:1381`, R4 held at the shipped cell; `grep -c unsafe
.temp/p18/v17/r3_incontract.rs` → **0**). Q1's step does not touch it. p17's R4
side is still unsearched — nothing at risk *yet*, but it now has a documented cost
if it is searched.

## Q3 — the two committed scripts run as committed: green, two minors

```
$ python3 patterns/p16-tlv-walk/controls/gen_controls.py --build     rc=0
  24 variants written, all 24 "ok"
$ diff ctl-before.md5 ctl-after.md5   ->   24/24 BYTE-IDENTICAL regeneration
$ python3 patterns/p16-tlv-walk/controls/foldcmp.py                  rc=0
  c4 26/3 6.50000 True · c8 53/6 6.62500 True · c16 83/16 5.18750 True
  c32 163/32 5.09375 True · c64 323/64 5.04688 True
  n4 43/8 5.37500 True · n8 43/8 5.37500 True · n16 83/16 5.18750 True
  ship 23/4 5.75000 False (same multiset, different schedule)
```

Every printed number matches `NOTES.md:1522-1533`; runs correctly from an
unrelated cwd; `git grep /home/apt` finds no hardcoded path in any committed
`.py`. `inputs/gen.py --sweep` twice → identical, and the 95 pre-existing blobs
95/95 byte-identical. `spelling_matches` over all 24 controls: 24/24 True on both
`required` tokens, False on both `forbidden`. (Two apparent `OUT` verdicts were a
false positive in the reviewer's own script, which hardcoded
`buf.get_unchecked(p)` while `r4_window.rs:58` folds the tag via
`w.get_unchecked(p)`.)

- **minor 1** — `NOTES.md:1535` "Reproduce the whole table with…" overclaims:
  `foldcmp.py` produces 8 of 10 rows; the two manual-unroll rows are not
  derivable from the committed tree.
- **minor 2** — `gen_controls.py`'s docstring says both "eighteen" and "sixteen".
  (Resolved at TASK_028: **both are correct** — 18 files, 16 respellings, because
  the two `_ship` copies *are* the shipped rungs.)

## Q4 — the band-cost rule is general and correct; two caveats

Both call sites are module-level literals with no pattern-specific input
(`check.py:459-460`, `measure.py:60,261`). `inputs_of` feeds checksums,
no-collapse, marginal Ir, adversarial, proof domain, sanitizers **and Miri**, so
no sweep blob reaches any gate stage; the only other enumeration
(`check.py:4631`) validates `--skip` names. No `spec.md` key selects inputs.
Measured: `inputs_checked` = 5 names, no "sweep"; `source_sha256` 0 stale entries;
`measure.py` records no `source_sha256` at all.

Caveats now in `.memory/05-layout.md`: **the `sweep-` prefix IS the mechanism**
(a band named otherwise enters the matrix and costs a full re-measure), and **the
gate hashes `gen.py` and never the blobs**, so a sweep-derived law's
reproducibility rests on `gen.py` being deterministic — verify by regenerating
twice.

## Problems

None in the reviewer's own runs. Foreground throughout, per-file scratch paths, no
concurrent measurement. No Ir was re-measured; the p05 interval consequence is
arithmetic on p05's own published laws.

## Unsure / not done

- **The `−2` residue is unbuilt** — v5 proves it would verify at zero TCB; nobody
  has compiled it. Same open question as p16's hand-unrolled 32×, now on two
  patterns.
- **The reverse case was not settled.** p01 pins `safe_naive ≡ safe_naive_verus,
  O3 exact`, so on p01 an **R2** candidate is chained to the prover too. Nothing
  published rests on it, but the true rule is broader than "an R4 must be
  Verus-expressible": **a rung covered by an `identity` pin is chained to the
  prover.**
- Did not attack TASK_025_REVIEW's settled findings, TASK_027's own numbers,
  p16's already-measured `u_c32`/`r4_hdr`, p02/p08 (no R4-side figure published
  for either), or the deferred mechanical backstop.

## On the deferred mechanical backstop

**The call was right, and this session is evidence for it.** The backstop pins a
*rate* against a disassembly body length; every defect found here — p05's R4
lever, both interval endpoints, the missing vstd qualifier — is a
**class-membership** defect no body-length assertion would catch. The check that
would have caught all of them is cheaper and is not a gate stage: **run
`./verus_run.py` on an R5 twin before differencing any unsafe-side variant.** Six
twins, eleven minutes.

## Memory updates

None — the reviewer does not write `.memory/`. Landed by the manager: the p05
entry, the R4-by-permission paragraph's true-width statement and its two
qualifications, the pair-interval reversal, the `verus_run.py`-first trap entry,
the `check.py` comment fix (TASK_028 item 5) and the `.memory/05-layout.md`
caveats.
